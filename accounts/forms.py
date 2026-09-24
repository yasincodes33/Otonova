import re
from django import forms
from django.contrib.auth.models import User

_TEL_RE = re.compile(r'^(\+90|0)?5\d{9}$')


def _temizle_telefon(telefon):
    t = re.sub(r'[\s\-\(\)]', '', telefon)
    if not _TEL_RE.match(t):
        raise forms.ValidationError(
            'Geçerli bir Türkiye telefon numarası girin. Örn: 05XX XXX XX XX'
        )
    return t


class KayitForm(forms.Form):
    ad       = forms.CharField(max_length=150, label='Ad')
    soyad    = forms.CharField(max_length=150, label='Soyad')
    email    = forms.EmailField(label='E-posta')
    telefon  = forms.CharField(max_length=20, required=False, label='Telefon')
    password  = forms.CharField(widget=forms.PasswordInput, min_length=8, label='Şifre')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Şifre Tekrar')
    kvkk      = forms.BooleanField(label='KVKK')

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Bu e-posta adresi zaten kayıtlı.')
        return email

    def clean_telefon(self):
        tel = self.cleaned_data.get('telefon', '').strip()
        if tel:
            return _temizle_telefon(tel)
        return tel

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Şifreler eşleşmiyor.')
        return cleaned


class GirisForm(forms.Form):
    email        = forms.EmailField(label='E-posta')
    password     = forms.CharField(widget=forms.PasswordInput, label='Şifre')
    remember_me  = forms.BooleanField(required=False, label='Beni hatırla')


class ProfilGuncelleForm(forms.Form):
    first_name  = forms.CharField(max_length=150, required=False, label='Ad')
    last_name   = forms.CharField(max_length=150, required=False, label='Soyad')
    telefon     = forms.CharField(max_length=20, required=False, label='Telefon')
    sehir       = forms.CharField(max_length=50, required=False, label='Şehir')
    biyografi   = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False, max_length=500, label='Hakkında'
    )
    avatar      = forms.ImageField(required=False, label='Profil Fotoğrafı')
    eski_sifre  = forms.CharField(widget=forms.PasswordInput, required=False, label='Mevcut Şifre')
    yeni_sifre  = forms.CharField(widget=forms.PasswordInput, min_length=8, required=False, label='Yeni Şifre')
    yeni_sifre2 = forms.CharField(widget=forms.PasswordInput, required=False, label='Yeni Şifre Tekrar')

    def clean_telefon(self):
        tel = self.cleaned_data.get('telefon', '').strip()
        if tel:
            return _temizle_telefon(tel)
        return tel

    def clean(self):
        cleaned = super().clean()
        y1 = cleaned.get('yeni_sifre')
        y2 = cleaned.get('yeni_sifre2')
        if y1 and y2 and y1 != y2:
            raise forms.ValidationError('Yeni şifreler eşleşmiyor.')
        return cleaned
