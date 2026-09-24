import re
from django import forms
from .models import IlanModel, IletisimModel, VITES_CHOICES, YAKIT_CHOICES, KASA_CHOICES, RENK_CHOICES, CEKIS_CHOICES, KIMDEN_CHOICES, TRAMER_CHOICES, MOTOR_HACMI_CHOICES

_TEL_RE = re.compile(r'^(\+90|0)?5\d{9}$')


class IlanForm(forms.ModelForm):
    class Meta:
        model = IlanModel
        fields = [
            'marka', 'seri', 'model', 'kasa_tipi', 'vites_tipi', 'yakit_tipi',
            'cekis', 'motor_hacmi', 'motor_gucu', 'yil', 'kilometre', 'renk',
            'tramer_kategori', 'tramer_tutari', 'sehir', 'kimden',
            'fiyat', 'baslik', 'aciklama', 'boya_degisen_detay',
        ]

    def clean(self):
        cleaned = super().clean()
        panel_raw = cleaned.get('boya_degisen_detay', '')
        boyali = degisen = 0
        for part in panel_raw.split('|'):
            sep = part.rfind(':')
            if sep >= 0:
                st = part[sep + 1:].strip()
                if st == 'Boyalı':
                    boyali += 1
                elif st == 'Değişen':
                    degisen += 1
        cleaned['_boyali_sayisi'] = boyali
        cleaned['_degisen_sayisi'] = degisen
        return cleaned


class IletisimForm(forms.ModelForm):
    class Meta:
        model = IletisimModel
        fields = ['ad_soyad', 'email', 'telefon', 'konu', 'mesaj']

    def clean_ad_soyad(self):
        val = self.cleaned_data.get('ad_soyad', '').strip()
        if len(val) < 3:
            raise forms.ValidationError('Ad soyad en az 3 karakter olmalıdır.')
        if not re.match(r'^[A-Za-zÇçĞğİıÖöŞşÜü\s]+$', val):
            raise forms.ValidationError('Ad soyad yalnızca harf içerebilir.')
        return val

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
            raise forms.ValidationError('Geçerli bir e-posta adresi girin.')
        return email

    def clean_telefon(self):
        tel = self.cleaned_data.get('telefon', '').strip()
        if tel:
            t = re.sub(r'[\s\-\(\)]', '', tel)
            if not _TEL_RE.match(t):
                raise forms.ValidationError(
                    'Geçerli bir Türkiye telefon numarası girin. Örn: 05XX XXX XX XX'
                )
            return t
        return tel

    def clean_mesaj(self):
        mesaj = self.cleaned_data.get('mesaj', '').strip()
        if len(mesaj) < 10:
            raise forms.ValidationError('Mesaj en az 10 karakter olmalıdır.')
        if len(mesaj) > 2000:
            raise forms.ValidationError('Mesaj en fazla 2000 karakter olabilir.')
        return mesaj
