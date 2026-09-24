from django.db import models
from django.contrib.auth.models import User
from core.models import ZamanDamgasi

VITES_CHOICES = [
    ('Düz',           'Düz'),
    ('Otomatik',      'Otomatik'),
    ('Yarı Otomatik', 'Yarı Otomatik'),
]
YAKIT_CHOICES = [
    ('Benzin', 'Benzin'), ('Dizel', 'Dizel'), ('Elektrik', 'Elektrik'),
    ('Hibrit', 'Hibrit'), ('LPG & Benzin', 'LPG & Benzin'),
]
KASA_CHOICES = [
    ('-', 'Belirtilmemiş'), ('Sedan', 'Sedan'), ('SUV', 'SUV'),
    ('Hatchback/5', 'Hatchback 5 Kapı'), ('Hatchback/3', 'Hatchback 3 Kapı'),
    ('MPV', 'MPV'), ('Coupe', 'Coupe'), ('Cabrio', 'Cabrio'),
    ('Station wagon', 'Station Wagon'), ('Pick-up', 'Pick-up'), ('Roadster', 'Roadster'),
]
KIMDEN_CHOICES = [
    ('Galeriden', 'Galeriden'), ('Sahibinden', 'Sahibinden'), ('Yetkili Bayiden', 'Yetkili Bayiden'),
]
TRAMER_CHOICES = [
    ('yok', 'Yok'), ('dusuk', 'Düşük'), ('orta', 'Orta'), ('yuksek', 'Yüksek'), ('bilinmiyor', 'Bilinmiyor'),
]


class TahminGecmisi(ZamanDamgasi):
    kullanici = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='tahminler',
        verbose_name='Kullanıcı',
        db_index=True,
    )

    marka           = models.CharField(max_length=60,  verbose_name='Marka')
    seri            = models.CharField(max_length=80,  blank=True)
    model           = models.CharField(max_length=120, verbose_name='Model')
    yil             = models.PositiveSmallIntegerField(verbose_name='Yıl')
    kilometre       = models.PositiveIntegerField(verbose_name='Kilometre')
    vites_tipi      = models.CharField(max_length=20, choices=VITES_CHOICES)
    yakit_tipi      = models.CharField(max_length=20, choices=YAKIT_CHOICES)
    kasa_tipi       = models.CharField(max_length=20, choices=KASA_CHOICES, default='-')
    motor_hacmi     = models.PositiveIntegerField(null=True, blank=True)
    motor_gucu      = models.PositiveSmallIntegerField(null=True, blank=True)
    sehir           = models.CharField(max_length=50)
    kimden          = models.CharField(max_length=20, choices=KIMDEN_CHOICES, default='Sahibinden')
    tramer_kategori = models.CharField(max_length=15, choices=TRAMER_CHOICES, default='bilinmiyor')
    tramer_tutari   = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    boyali_sayisi   = models.PositiveSmallIntegerField(default=0)
    degisen_sayisi  = models.PositiveSmallIntegerField(default=0)

    tahmin_fiyat = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Tahmin Fiyat')
    dusuk_sinir  = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Alt Sınır (P10)')
    yuksek_sinir = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Üst Sınır (P90)')
    r2_skoru     = models.FloatField(verbose_name='R² Skoru')
    mape_skoru   = models.FloatField(verbose_name='MAPE Skoru')

    ip_adresi = models.GenericIPAddressField(null=True, blank=True)
    tarayici  = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table            = 'ml_model_tahmingecmisi'
        verbose_name        = 'Tahmin Geçmişi'
        verbose_name_plural = 'Tahmin Geçmişleri'
        ordering            = ['-olusturuldu']
        indexes = [
            models.Index(fields=['kullanici', 'olusturuldu']),
            models.Index(fields=['marka', 'model']),
        ]

    def __str__(self):
        return f'{self.marka} {self.model} {self.yil} → {self.tahmin_fiyat:,.0f} TL'
