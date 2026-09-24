import uuid

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator

from core.models import ZamanDamgasi


VITES_CHOICES = [
    ('Düz',           'Düz'),
    ('Otomatik',      'Otomatik'),
    ('Yarı Otomatik', 'Yarı Otomatik'),
]

YAKIT_CHOICES = [
    ('Benzin',       'Benzin'),
    ('Dizel',        'Dizel'),
    ('Elektrik',     'Elektrik'),
    ('Hibrit',       'Hibrit'),
    ('LPG & Benzin', 'LPG & Benzin'),
]

KASA_CHOICES = [
    ('-',             'Belirtilmemiş'),
    ('Cabrio',        'Cabrio'),
    ('Coupe',         'Coupe'),
    ('Hatchback/3',   'Hatchback 3 Kapı'),
    ('Hatchback/5',   'Hatchback 5 Kapı'),
    ('MPV',           'MPV'),
    ('Pick-up',       'Pick-up'),
    ('Roadster',      'Roadster'),
    ('SUV',           'SUV'),
    ('Sedan',         'Sedan'),
    ('Station wagon', 'Station Wagon'),
]

RENK_CHOICES = [
    ('Bej',        'Bej'),
    ('Beyaz',      'Beyaz'),
    ('Bordo',      'Bordo'),
    ('Diger',      'Diğer'),
    ('Füme',       'Füme'),
    ('Gri',        'Gri'),
    ('Kahverengi', 'Kahverengi'),
    ('Kırmızı',    'Kırmızı'),
    ('Lacivert',   'Lacivert'),
    ('Mavi',       'Mavi'),
    ('Siyah',      'Siyah'),
    ('Yeşil',      'Yeşil'),
    ('Şampanya',   'Şampanya'),
]

CEKIS_CHOICES = [
    ('4WD (Sürekli)',    '4WD (Sürekli)'),
    ('AWD (Elektronik)', 'AWD (Elektronik)'),
    ('Arkadan İtiş',     'Arkadan İtiş'),
    ('Önden Çekiş',      'Önden Çekiş'),
]

KIMDEN_CHOICES = [
    ('Galeriden',       'Galeriden'),
    ('Sahibinden',      'Sahibinden'),
    ('Yetkili Bayiden', 'Yetkili Bayiden'),
]

TRAMER_CHOICES = [
    ('yok',        'Yok'),
    ('dusuk',      'Düşük'),
    ('orta',       'Orta'),
    ('yuksek',     'Yüksek'),
    ('bilinmiyor', 'Bilinmiyor'),
]

ILAN_DURUM_CHOICES = [
    ('aktif',   'Aktif'),
    ('pasif',   'Pasif'),
    ('satildi', 'Satıldı'),
    ('onay',    'Onay Bekliyor'),
]

MOTOR_HACMI_CHOICES = [
    (cc, f'{cc} cc') for cc in [
        900, 1000, 1100, 1200, 1250, 1300, 1400, 1500, 1600,
        1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500,
        2600, 2700, 2800, 2900, 3000,
    ]
]


class IlanModel(ZamanDamgasi):
    uuid  = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    slug  = models.SlugField(max_length=200, unique=True, blank=True, verbose_name='URL Slug')

    satici = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='ilanlar',
        verbose_name='Satıcı',
        db_index=True,
    )

    marka = models.CharField(max_length=60,  verbose_name='Marka',  db_index=True)
    seri  = models.CharField(max_length=80,  blank=True,            verbose_name='Seri')
    model = models.CharField(max_length=120, verbose_name='Model',  db_index=True)

    kasa_tipi   = models.CharField(max_length=20, choices=KASA_CHOICES,  default='-',       verbose_name='Kasa Tipi',   db_index=True)
    vites_tipi  = models.CharField(max_length=20, choices=VITES_CHOICES,                    verbose_name='Vites Tipi',  db_index=True)
    yakit_tipi  = models.CharField(max_length=20, choices=YAKIT_CHOICES,                    verbose_name='Yakıt Tipi',  db_index=True)
    cekis       = models.CharField(max_length=25, choices=CEKIS_CHOICES, blank=True,        verbose_name='Çekiş')
    motor_hacmi = models.PositiveIntegerField(choices=MOTOR_HACMI_CHOICES, null=True, blank=True, verbose_name='Motor Hacmi (cc)')
    motor_gucu  = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(30), MaxValueValidator(2000)],
        verbose_name='Motor Gücü (HP)',
    )

    yil       = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1950), MaxValueValidator(2030)],
        verbose_name='Model Yılı', db_index=True,
    )
    kilometre = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(1_500_000)],
        verbose_name='Kilometre', db_index=True,
    )
    renk = models.CharField(max_length=20, choices=RENK_CHOICES, blank=True, verbose_name='Renk')

    tramer_kategori = models.CharField(max_length=15, choices=TRAMER_CHOICES, default='bilinmiyor', verbose_name='Tramer Kategori')
    tramer_tutari   = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Tramer Tutarı (TL)')
    boyali_sayisi   = models.PositiveSmallIntegerField(default=0, verbose_name='Boyalı Parça Sayısı')
    degisen_sayisi  = models.PositiveSmallIntegerField(default=0, verbose_name='Değişen Parça Sayısı')

    sehir  = models.CharField(max_length=50, verbose_name='Şehir', db_index=True)
    kimden = models.CharField(max_length=20, choices=KIMDEN_CHOICES, default='Sahibinden', verbose_name='Kimden', db_index=True)

    fiyat            = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Fiyat (TL)', db_index=True)
    ai_tahmin_fiyat  = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, verbose_name='AI Tahmin Fiyatı')
    ai_sapma_yuzdesi = models.FloatField(null=True, blank=True, verbose_name='AI Sapma %')
    firsat_skoru     = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Fırsat Skoru (0-100)', db_index=True)

    satici_adi     = models.CharField(max_length=150, blank=True, verbose_name='Satıcı Adı')
    yetkili_kisi   = models.CharField(max_length=100, blank=True, verbose_name='Yetkili Kişi')
    satici_tipi    = models.CharField(max_length=60,  blank=True, verbose_name='Satıcı Tipi')
    yetki_belge_no = models.CharField(max_length=30,  blank=True, verbose_name='Yetki Belge No')

    boya_degisen_detay = models.TextField(blank=True, verbose_name='Boya/Değişen Detay')

    baslik   = models.CharField(max_length=200, verbose_name='Başlık')
    aciklama = models.TextField(blank=True, verbose_name='Açıklama')

    durum     = models.CharField(max_length=10, choices=ILAN_DURUM_CHOICES, default='onay', verbose_name='Durum', db_index=True)
    is_active = models.BooleanField(default=True, verbose_name='Aktif', db_index=True)
    one_cikan = models.BooleanField(default=False, verbose_name='Öne Çıkan', db_index=True)

    ilan_tarihi  = models.DateField(auto_now_add=True, verbose_name='İlan Tarihi', db_index=True)
    bitis_tarihi = models.DateField(null=True, blank=True, verbose_name='Bitiş Tarihi')

    class Meta:
        db_table            = 'ml_model_ilanmodel'
        verbose_name        = 'İlan'
        verbose_name_plural = 'İlanlar'
        ordering            = ['-olusturuldu']
        indexes = [
            models.Index(fields=['marka', 'model']),
            models.Index(fields=['yil', 'kilometre']),
            models.Index(fields=['sehir', 'durum']),
            models.Index(fields=['fiyat']),
            models.Index(fields=['is_active', 'durum']),
            models.Index(fields=['one_cikan', 'is_active']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f'{self.marka}-{self.model}-{self.yil}')
            self.slug = f'{base}-{str(self.uuid)[:8]}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.marka} {self.model} {self.yil} – {self.fiyat:,.0f} TL'


class IlanFoto(ZamanDamgasi):
    ilan  = models.ForeignKey(IlanModel, on_delete=models.CASCADE, related_name='fotolar', verbose_name='İlan', db_index=True)
    foto  = models.ImageField(upload_to='ilan_fotolar/%Y/%m/', verbose_name='Fotoğraf')
    sira  = models.PositiveSmallIntegerField(default=0, verbose_name='Sıra')
    kapak = models.BooleanField(default=False, verbose_name='Kapak Fotoğrafı')

    class Meta:
        db_table            = 'ml_model_ilanfoto'
        verbose_name        = 'İlan Fotoğrafı'
        verbose_name_plural = 'İlan Fotoğrafları'
        ordering            = ['sira']
        indexes = [
            models.Index(fields=['ilan', 'kapak']),
        ]

    def __str__(self):
        return f'Foto #{self.sira} – {self.ilan}'


class FavoriModel(ZamanDamgasi):
    kullanici = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favoriler',
        verbose_name='Kullanıcı',
        db_index=True,
    )
    ilan = models.ForeignKey(
        IlanModel,
        on_delete=models.CASCADE,
        related_name='favoriler',
        verbose_name='İlan',
        db_index=True,
    )

    class Meta:
        db_table            = 'ml_model_favorimodel'
        verbose_name        = 'Favori'
        verbose_name_plural = 'Favoriler'
        unique_together     = [('kullanici', 'ilan')]
        indexes = [
            models.Index(fields=['kullanici', 'ilan']),
        ]

    def __str__(self):
        return f'{self.kullanici.username} ♥ {self.ilan}'


class IletisimModel(ZamanDamgasi):
    KONU_CHOICES = [
        ('genel',  'Genel Soru'),
        ('teknik', 'Teknik Destek'),
        ('ilan',   'İlan Sorunu'),
        ('odeme',  'Ödeme Sorunu'),
        ('diger',  'Diğer'),
    ]

    kullanici = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='iletisimler',
        verbose_name='Kullanıcı',
    )
    ad_soyad  = models.CharField(max_length=100, verbose_name='Ad Soyad')
    email     = models.EmailField(verbose_name='E-posta')
    telefon   = models.CharField(max_length=20, blank=True, verbose_name='Telefon')
    konu      = models.CharField(max_length=10, choices=KONU_CHOICES, default='genel', verbose_name='Konu', db_index=True)
    mesaj     = models.TextField(verbose_name='Mesaj')
    okundu    = models.BooleanField(default=False, verbose_name='Okundu', db_index=True)
    ip_adresi = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table            = 'ml_model_iletisimmodel'
        verbose_name        = 'İletişim'
        verbose_name_plural = 'İletişim Mesajları'
        ordering            = ['-olusturuldu']
        indexes = [
            models.Index(fields=['okundu', 'olusturuldu']),
            models.Index(fields=['konu']),
        ]

    def __str__(self):
        return f'{self.ad_soyad} — {self.get_konu_display()} ({self.olusturuldu:%d.%m.%Y})'
