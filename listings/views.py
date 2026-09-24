import io
import json
import datetime
import logging

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect

from .models import IlanModel, IlanFoto, FavoriModel, IletisimModel
from .forms import IlanForm, IletisimForm
from predictions.utils import normalise_panel_raw, _firsat_skoru_hesapla, get_segment_mae
from predictions.services import MLService

logger = logging.getLogger(__name__)


def arabalar(request):
    qs = IlanModel.objects.filter(is_active=True, durum='aktif') \
        .select_related('satici') \
        .prefetch_related('fotolar')

    q         = request.GET.get('q', '').strip()
    marka     = request.GET.get('marka', '').strip()
    seri_ara  = request.GET.get('seri', '').strip()
    model_ara = request.GET.get('model', '').strip()
    sehir     = request.GET.get('sehir', '').strip()
    vites     = request.GET.get('vites', '').strip()
    yakit     = request.GET.get('yakit', '').strip()
    yil_min   = request.GET.get('yil_min', '').strip()
    yil_max   = request.GET.get('yil_max', '').strip()
    km_max    = request.GET.get('km_max', '').strip()
    fiyat_min = request.GET.get('fiyat_min', '').strip()
    fiyat_max = request.GET.get('fiyat_max', '').strip()
    sira      = request.GET.get('sira', '').strip()
    ai_durum  = request.GET.get('ai_durum', '').strip()

    if q:
        qs = qs.filter(Q(baslik__icontains=q) | Q(marka__icontains=q) | Q(model__icontains=q))
    if marka:
        qs = qs.filter(marka__icontains=marka)
    if seri_ara:
        qs = qs.filter(seri__icontains=seri_ara)
    if model_ara:
        qs = qs.filter(model__icontains=model_ara)
    if sehir:
        qs = qs.filter(sehir__icontains=sehir)
    if vites:
        qs = qs.filter(vites_tipi=vites)
    if yakit:
        qs = qs.filter(yakit_tipi=yakit)
    if yil_min.isdigit():
        qs = qs.filter(yil__gte=int(yil_min))
    if yil_max.isdigit():
        qs = qs.filter(yil__lte=int(yil_max))
    if km_max.isdigit():
        qs = qs.filter(kilometre__lte=int(km_max))
    if fiyat_min.isdigit():
        qs = qs.filter(fiyat__gte=int(fiyat_min))
    if fiyat_max.isdigit():
        qs = qs.filter(fiyat__lte=int(fiyat_max))
    if ai_durum == 'firsat':
        qs = qs.filter(firsat_skoru__gte=70)
    elif ai_durum == 'iyi':
        qs = qs.filter(ai_tahmin_fiyat__isnull=False, ai_sapma_yuzdesi__lte=-5)
    elif ai_durum == 'normal':
        qs = qs.filter(ai_tahmin_fiyat__isnull=False, ai_sapma_yuzdesi__gt=-5, ai_sapma_yuzdesi__lte=10)
    elif ai_durum == 'yuksek':
        qs = qs.filter(ai_tahmin_fiyat__isnull=False, ai_sapma_yuzdesi__gt=10)

    sira_map = {
        'fiyat_asc':  'fiyat',
        'fiyat_desc': '-fiyat',
        'yil_desc':   '-yil',
        'yil_asc':    'yil',
        'km_asc':     'kilometre',
        'firsat':     '-firsat_skoru',
        'ucuz':       'ai_sapma_yuzdesi',
    }
    qs = qs.order_by(sira_map.get(sira, '-olusturuldu'))

    toplam    = qs.count()
    paginator = Paginator(qs, 12)
    sayfa     = request.GET.get('sayfa', 1)
    ilanlar   = paginator.get_page(sayfa)

    firsat_sayisi = IlanModel.objects.filter(is_active=True, durum='aktif', firsat_skoru__gte=70).count()

    meta = MLService.get_meta()
    ctx = {
        'ilanlar'              : ilanlar,
        'toplam'               : toplam,
        'firsat_sayisi'        : firsat_sayisi,
        'markalar'             : sorted(meta['marka_seri_map'].keys()),
        'sehirler'             : meta['sehir'],
        'vites_list'           : meta['vites_tipi'],
        'yakit_list'           : meta['yakit_tipi'],
        'filtreler'            : request.GET,
        'marka_seri_model_json': json.dumps(meta.get('marka_seri_model_map', {})),
        'markalar_list'        : list(
            IlanModel.objects.filter(is_active=True, durum='aktif')
            .values_list('marka', flat=True).distinct().order_by('marka')
        ),
    }
    return render(request, 'listings/arabalar.html', ctx)


def ilan_detay(request, slug):
    try:
        ilan = IlanModel.objects.select_related('satici').prefetch_related('fotolar').get(slug=slug, is_active=True)
    except IlanModel.DoesNotExist:
        return redirect('listings:arabalar')

    favori = False
    if request.user.is_authenticated:
        favori = FavoriModel.objects.filter(kullanici=request.user, ilan=ilan).exists()

    ai_fiyat = ai_dusuk = ai_yuksek = None
    bugun = datetime.date.today()

    _tahmin_data = {
        'marka':           ilan.marka,
        'seri':            ilan.seri,
        'model':           ilan.model,
        'yas':             str(max(bugun.year - ilan.yil, 1)),
        'kilometre':       str(ilan.kilometre),
        'motor_gucu':      str(ilan.motor_gucu or 0),
        'motor_hacmi':     str(ilan.motor_hacmi or 1000),
        'boyali_sayisi':   str(ilan.boyali_sayisi),
        'degisen_sayisi':  str(ilan.degisen_sayisi),
        'tramer':          str(float(ilan.tramer_tutari)),
        'vites_tipi':      ilan.vites_tipi,
        'yakit_tipi':      ilan.yakit_tipi,
        'kasa_tipi':       ilan.kasa_tipi,
        'renk':            ilan.renk,
        'cekis':           ilan.cekis,
        'kimden':          ilan.kimden,
        'sehir':           ilan.sehir,
        'tramer_kategori': ilan.tramer_kategori,
    }

    if ilan.ai_tahmin_fiyat:
        ai_fiyat = int(ilan.ai_tahmin_fiyat)
        try:
            result = MLService.predict_confidence_only(_tahmin_data)
            ai_dusuk  = result['dusuk']
            ai_yuksek = result['yuksek']
        except Exception:
            logger.exception('AI güven aralığı hesaplanamadı: ilan_pk=%s', ilan.pk)
            metrics = MLService.get_metrics()
            _m = metrics['mape'] / 100
            ai_dusuk  = round(ai_fiyat * (1 - _m))
            ai_yuksek = round(ai_fiyat * (1 + _m))
    else:
        try:
            result   = MLService.predict(_tahmin_data)
            ai_fiyat = result['fiyat']
            ai_dusuk  = result['dusuk']
            ai_yuksek = result['yuksek']
            if ai_fiyat:
                sapma = (float(ilan.fiyat) - ai_fiyat) / ai_fiyat * 100
                skor  = _firsat_skoru_hesapla(ilan, sapma, bugun)
                IlanModel.objects.filter(pk=ilan.pk).update(
                    ai_tahmin_fiyat=ai_fiyat, ai_sapma_yuzdesi=sapma, firsat_skoru=skor
                )
        except Exception:
            logger.exception('AI tahmini hesaplanamadı: ilan_pk=%s', ilan.pk)

    fiyat_pos = 50
    if ai_dusuk and ai_yuksek and ai_yuksek > ai_dusuk:
        fiyat_pos = round(max(0, min(100,
            (int(ilan.fiyat) - ai_dusuk) / (ai_yuksek - ai_dusuk) * 100
        )))

    sapma_pct = None
    if ai_fiyat:
        sapma_pct = round(abs((float(ilan.fiyat) - ai_fiyat) / ai_fiyat * 100), 1)

    benzer_ilanlar = (
        IlanModel.objects
        .filter(is_active=True, durum='aktif', marka=ilan.marka, model=ilan.model,
                yil__gte=ilan.yil - 2, yil__lte=ilan.yil + 2)
        .exclude(pk=ilan.pk)
        .select_related('satici')
        .prefetch_related('fotolar')
        .order_by('fiyat')[:6]
    )
    if not benzer_ilanlar.exists():
        benzer_ilanlar = (
            IlanModel.objects
            .filter(is_active=True, durum='aktif', marka=ilan.marka)
            .exclude(pk=ilan.pk)
            .select_related('satici')
            .prefetch_related('fotolar')
            .order_by('fiyat')[:4]
        )

    _base = IlanModel.objects.filter(is_active=True, durum='aktif').exclude(pk=ilan.pk)
    _fiyatlar = list(
        _base.filter(marka=ilan.marka, seri=ilan.seri)
        .values_list('fiyat', flat=True).order_by('fiyat')[:60]
    )
    if len(_fiyatlar) < 4:
        _fiyatlar = list(
            _base.filter(marka=ilan.marka)
            .values_list('fiyat', flat=True).order_by('fiyat')[:60]
        )
    benzer_fiyatlar_json = json.dumps([float(f) for f in _fiyatlar])

    kapak_foto = ilan.fotolar.filter(kapak=True).first() or ilan.fotolar.first()
    metrics    = MLService.get_metrics()

    seg_mae, seg_label = get_segment_mae(ai_fiyat) if ai_fiyat else (None, None)
    seg_alt  = round(ai_fiyat - seg_mae) if ai_fiyat and seg_mae else None
    seg_ust  = round(ai_fiyat + seg_mae) if ai_fiyat and seg_mae else None
    r2_pct   = round(metrics['r2'] * 100, 1)
    guv_label = ('Çok Yüksek' if r2_pct >= 95 else 'Yüksek' if r2_pct >= 90 else 'Orta')
    guv_color = ('#22c55e' if r2_pct >= 95 else '#3b82f6' if r2_pct >= 90 else '#d97706')

    return render(request, 'listings/ilan_detay.html', {
        'ilan':                 ilan,
        'favori':               favori,
        'ai_fiyat':             ai_fiyat,
        'ai_dusuk':             ai_dusuk,
        'ai_yuksek':            ai_yuksek,
        'r2':                   round(metrics['r2'], 3),
        'r2_pct':               r2_pct,
        'mae':                  round(metrics['mae']),
        'mape':                 round(metrics['mape'], 1),
        'yas':                  max(bugun.year - ilan.yil, 1),
        'fiyat_pos':            fiyat_pos,
        'sapma_pct':            sapma_pct,
        'seg_mae':              seg_mae,
        'seg_label':            seg_label,
        'seg_alt':              seg_alt,
        'seg_ust':              seg_ust,
        'guv_label':            guv_label,
        'guv_color':            guv_color,
        'benzer_ilanlar':       benzer_ilanlar,
        'benzer_fiyatlar_json': benzer_fiyatlar_json,
        'kapak_foto':           kapak_foto,
        'panel_raw':            normalise_panel_raw(ilan.boya_degisen_detay) if ilan.boya_degisen_detay else None,
    })


@login_required
def satis(request):
    meta = MLService.get_meta()

    if request.method == 'POST':
        form = IlanForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            try:
                ilan = IlanModel(
                    satici          = request.user,
                    marka           = d['marka'],
                    seri            = d['seri'],
                    model           = d['model'],
                    kasa_tipi       = d['kasa_tipi'],
                    vites_tipi      = d['vites_tipi'],
                    yakit_tipi      = d['yakit_tipi'],
                    cekis           = d['cekis'],
                    motor_hacmi     = d.get('motor_hacmi'),
                    motor_gucu      = d.get('motor_gucu'),
                    yil             = d['yil'],
                    kilometre       = d['kilometre'],
                    renk            = d['renk'],
                    tramer_kategori = d['tramer_kategori'],
                    tramer_tutari   = d.get('tramer_tutari', 0) or 0,
                    sehir           = d['sehir'],
                    kimden          = d['kimden'],
                    fiyat           = d['fiyat'],
                    baslik          = d['baslik'],
                    aciklama        = d.get('aciklama', ''),
                    boya_degisen_detay = d.get('boya_degisen_detay', ''),
                    boyali_sayisi   = d['_boyali_sayisi'],
                    degisen_sayisi  = d['_degisen_sayisi'],
                    durum           = 'onay',
                )
                ilan.save()

                try:
                    _bugun = datetime.date.today()
                    _veri  = {
                        'marka': ilan.marka, 'seri': ilan.seri, 'model': ilan.model,
                        'yas':   str(max(_bugun.year - ilan.yil, 1)),
                        'kilometre':      str(ilan.kilometre),
                        'motor_gucu':     str(ilan.motor_gucu or 0),
                        'motor_hacmi':    str(ilan.motor_hacmi or 1000),
                        'boyali_sayisi':  str(ilan.boyali_sayisi),
                        'degisen_sayisi': str(ilan.degisen_sayisi),
                        'tramer':         str(float(ilan.tramer_tutari)),
                        'vites_tipi': ilan.vites_tipi, 'yakit_tipi': ilan.yakit_tipi,
                        'kasa_tipi':  ilan.kasa_tipi,  'renk':       ilan.renk,
                        'cekis':      ilan.cekis,       'kimden':     ilan.kimden,
                        'sehir':      ilan.sehir,        'tramer_kategori': ilan.tramer_kategori,
                    }
                    result = MLService.predict(_veri)
                    _ai    = result['fiyat']
                    _sapma = (float(ilan.fiyat) - _ai) / _ai * 100
                    _skor  = _firsat_skoru_hesapla(ilan, _sapma, _bugun)
                    IlanModel.objects.filter(pk=ilan.pk).update(
                        ai_tahmin_fiyat=_ai, ai_sapma_yuzdesi=_sapma, firsat_skoru=_skor
                    )
                except Exception:
                    logger.exception('İlan AI tahmini hesaplanamadı: ilan_pk=%s', ilan.pk)

                _IZIN_MIME = {'image/jpeg', 'image/png', 'image/webp'}
                _MAX_BOYUT = 5 * 1024 * 1024
                fotolar = request.FILES.getlist('fotolar')[:10]
                for i, foto in enumerate(fotolar):
                    if foto.content_type not in _IZIN_MIME:
                        continue
                    if foto.size > _MAX_BOYUT:
                        continue
                    try:
                        img = Image.open(foto)
                        if img.mode in ('RGBA', 'P', 'LA'):
                            img = img.convert('RGB')
                        if img.width > 1200 or img.height > 900:
                            img.thumbnail((1200, 900), Image.LANCZOS)
                        buf = io.BytesIO()
                        img.save(buf, format='JPEG', quality=88, optimize=True)
                        buf.seek(0)
                        name = foto.name.rsplit('.', 1)[0] + '.jpg'
                        resized = InMemoryUploadedFile(
                            buf, 'ImageField', name, 'image/jpeg',
                            buf.getbuffer().nbytes, None,
                        )
                        IlanFoto.objects.create(ilan=ilan, foto=resized, sira=i, kapak=(i == 0))
                    except Exception:
                        logger.exception('Foto yüklenemedi: ilan_pk=%s foto=%s', ilan.pk, i)
                        continue

                messages.success(request, 'İlanınız inceleme için gönderildi.')
                return redirect('listings:arabalar')
            except Exception:
                logger.exception('İlan kaydedilemedi: user_pk=%s', request.user.pk)
                messages.error(request, 'İlan kaydedilemedi. Lütfen tüm alanları kontrol edin.')
        else:
            for field_errors in form.errors.values():
                for error in field_errors:
                    messages.error(request, error)
    else:
        form = IlanForm()

    ctx = {
        'form'       : form,
        'form_data'  : request.POST if request.method == 'POST' else {},
        'markalar'   : sorted(meta['marka_seri_map'].keys()),
        'model_list' : sorted(meta['model']),
        'vites_list' : meta['vites_tipi'],
        'yakit_list' : meta['yakit_tipi'],
        'kasa_list'  : meta['kasa_tipi'],
        'renk_list'  : meta['renk'],
        'cekis_list' : meta['cekis'],
        'kimden_list': meta['kimden'],
        'tramer_list': meta['tramer_kategori'],
        'sehirler'   : meta['sehir'],
        'motor_list' : meta['motor_hacmi'],
        'marka_seri_json'            : json.dumps(meta['marka_seri_map']),
        'marka_seri_model_json'      : json.dumps(meta.get('marka_seri_model_map', {})),
        'marka_seri_model_kasa_json' : json.dumps(meta.get('marka_seri_model_kasa_map', {})),
        'kasa_tipleri_json'          : json.dumps(meta['kasa_tipi']),
    }
    return render(request, 'listings/satis.html', ctx)


def iletisim(request):
    if request.method == 'POST':
        form = IletisimForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.kullanici = request.user if request.user.is_authenticated else None
            obj.ip_adresi = request.META.get('REMOTE_ADDR')
            obj.save()
            messages.success(request, 'Mesajınız alındı, en kısa sürede dönüş yapılacaktır.')
            return redirect('listings:iletisim')
    else:
        form = IletisimForm()

    return render(request, 'listings/iletisim.html', {'form': form})


@login_required
def favoriler(request):
    fav_ilanlar = FavoriModel.objects.filter(kullanici=request.user) \
        .select_related('ilan').prefetch_related('ilan__fotolar').order_by('-olusturuldu')
    return render(request, 'listings/favoriler.html', {'fav_ilanlar': fav_ilanlar})


@login_required
def favori_toggle(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Sadece POST'}, status=405)
    try:
        data    = json.loads(request.body)
        ilan_id = data.get('ilan_id')
        ilan    = IlanModel.objects.get(pk=ilan_id, is_active=True)
        obj, created = FavoriModel.objects.get_or_create(kullanici=request.user, ilan=ilan)
        if not created:
            obj.delete()
        return JsonResponse({'favori': created})
    except IlanModel.DoesNotExist:
        return JsonResponse({'error': 'İlan bulunamadı'}, status=404)
