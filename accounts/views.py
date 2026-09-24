import io
import logging

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from .models import ProfilModel
from .forms import KayitForm, GirisForm, ProfilGuncelleForm

logger = logging.getLogger(__name__)


def kayit(request):
    if request.user.is_authenticated:
        return redirect('pages:index')

    if request.method == 'POST':
        form = KayitForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            user = User.objects.create_user(
                username   = d['email'],
                email      = d['email'],
                first_name = d['ad'],
                last_name  = d['soyad'],
                password   = d['password'],
            )
            if d.get('telefon'):
                try:
                    user.profil.telefon = d['telefon']
                    user.profil.save()
                except Exception:
                    logger.exception('Profil telefon güncellenemedi: user_pk=%s', user.pk)
            login(request, user)
            messages.success(request, f"Hoş geldiniz, {d['ad']}!")
            return redirect('pages:index')
        for field_errors in form.errors.values():
            for error in field_errors:
                messages.error(request, error)
    else:
        form = KayitForm()

    return render(request, 'accounts/kayit.html', {'form': form})


def giris(request):
    if request.user.is_authenticated:
        return redirect('pages:index')

    if request.method == 'POST':
        form = GirisForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            email        = d['email'].strip().lower()
            sifre        = d['password']
            beni_hatirla = d.get('remember_me', False)

            try:
                kullanici_adi = User.objects.get(email=email).username
            except User.DoesNotExist:
                kullanici_adi = email

            user = authenticate(request, username=kullanici_adi, password=sifre)
            if user is not None:
                login(request, user)
                if not beni_hatirla:
                    request.session.set_expiry(0)
                next_url = request.POST.get('next') or request.GET.get('next') or ''
                if next_url and next_url.startswith('/'):
                    return redirect(next_url)
                return redirect('pages:index')
            else:
                messages.error(request, 'E-posta veya şifre hatalı.')
        else:
            messages.error(request, 'E-posta veya şifre hatalı.')
    else:
        form = GirisForm()

    return render(request, 'accounts/giris.html', {'form': form})


def cikis(request):
    logout(request)
    return redirect('pages:index')


@login_required
def profil(request):
    from predictions.models import TahminGecmisi
    from listings.models import IlanModel

    tahminler = TahminGecmisi.objects.filter(kullanici=request.user).order_by('-olusturuldu')[:10]
    ilanlarim = IlanModel.objects.filter(satici=request.user).prefetch_related('fotolar').order_by('-olusturuldu')
    return render(request, 'accounts/profil.html', {
        'tahminler': tahminler,
        'ilanlarim': ilanlarim,
    })


def _sehir_listesi():
    from predictions.services import MLService
    return MLService.get_meta().get('sehir', [])


@login_required
def profil_guncelle(request):
    user = request.user
    try:
        profil_obj = user.profil
    except ProfilModel.DoesNotExist:
        profil_obj = ProfilModel.objects.create(kullanici=user)

    if request.method == 'POST':
        form = ProfilGuncelleForm(request.POST, request.FILES)
        if form.is_valid():
            d = form.cleaned_data
            user.first_name = d.get('first_name', '').strip()
            user.last_name  = d.get('last_name', '').strip()
            user.save()

            profil_obj.telefon   = d.get('telefon', '').strip() or None
            profil_obj.sehir     = d.get('sehir', '').strip()
            profil_obj.biyografi = d.get('biyografi', '').strip()

            avatar = d.get('avatar')
            if avatar:
                try:
                    img = Image.open(avatar)
                    if img.mode in ('RGBA', 'P', 'LA'):
                        img = img.convert('RGB')
                    img.thumbnail((400, 400), Image.LANCZOS)
                    buf = io.BytesIO()
                    img.save(buf, format='JPEG', quality=90, optimize=True)
                    buf.seek(0)
                    name = avatar.name.rsplit('.', 1)[0] + '.jpg'
                    profil_obj.avatar = InMemoryUploadedFile(
                        buf, 'ImageField', name, 'image/jpeg', buf.getbuffer().nbytes, None,
                    )
                except Exception:
                    logger.exception('Avatar yüklenemedi: user_pk=%s', user.pk)

            profil_obj.save()

            eski_sifre = d.get('eski_sifre', '')
            yeni_sifre = d.get('yeni_sifre', '')
            if eski_sifre and yeni_sifre:
                if user.check_password(eski_sifre):
                    user.set_password(yeni_sifre)
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, 'Şifreniz güncellendi.')
                else:
                    messages.error(request, 'Mevcut şifre hatalı.')
                    return render(request, 'accounts/profil_guncelle.html', {
                        'form': form, 'sehirler': _sehir_listesi(),
                    })
        else:
            for field_errors in form.errors.values():
                for error in field_errors:
                    messages.error(request, error)
            return render(request, 'accounts/profil_guncelle.html', {
                'form': form, 'sehirler': _sehir_listesi(),
            })

        messages.success(request, 'Profil bilgileriniz güncellendi.')
        return redirect('accounts:profil')

    else:
        initial = {
            'first_name': user.first_name,
            'last_name':  user.last_name,
            'telefon':    getattr(profil_obj, 'telefon', ''),
            'sehir':      getattr(profil_obj, 'sehir', ''),
            'biyografi':  getattr(profil_obj, 'biyografi', ''),
        }
        form = ProfilGuncelleForm(initial=initial)

    return render(request, 'accounts/profil_guncelle.html', {
        'form': form, 'sehirler': _sehir_listesi(),
    })
