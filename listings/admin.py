from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Count

from .models import IlanModel, IlanFoto, FavoriModel, IletisimModel

admin.site.site_title = "OtoNova"
admin.site.site_header = "OtoNova Yönetim Paneli"
admin.site.index_title = "Kontrol Merkezi"


class IlanFotoInline(admin.TabularInline):
    model           = IlanFoto
    extra           = 3
    fields          = ('foto_onizleme', 'foto', 'sira', 'kapak')
    readonly_fields = ('foto_onizleme',)

    def foto_onizleme(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" style="height:60px;width:90px;object-fit:cover;border-radius:6px;border:1px solid #e2e8f0">',
                obj.foto.url
            )
        return '—'
    foto_onizleme.short_description = 'Önizleme'


@admin.register(IlanModel)
class IlanAdmin(admin.ModelAdmin):
    inlines      = [IlanFotoInline]
    list_display = (
        'kapak_foto', 'baslik', 'marka_seri_model', 'yil_km',
        'fiyat_formatted', 'sehir', 'durum_badge', 'durum',
        'is_active', 'one_cikan', 'favori_sayisi', 'olusturuldu',
    )
    list_filter      = ('durum', 'is_active', 'one_cikan', 'yakit_tipi', 'vites_tipi', 'kasa_tipi', 'sehir', 'marka')
    search_fields    = ('baslik', 'marka', 'model', 'seri', 'satici_adi', 'aciklama')
    readonly_fields  = ('uuid', 'slug', 'olusturuldu', 'guncellendi', 'ilan_tarihi', 'kapak_foto_buyuk')
    list_editable    = ('durum', 'is_active', 'one_cikan')
    ordering         = ('-olusturuldu',)
    date_hierarchy   = 'ilan_tarihi'
    list_per_page    = 25
    save_on_top      = True

    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('baslik', 'slug', 'uuid', 'durum', 'is_active', 'one_cikan')
        }),
        ('Araç Kimliği', {
            'fields': (('marka', 'seri', 'model'), ('kasa_tipi', 'renk', 'cekis'))
        }),
        ('Teknik Özellikler', {
            'fields': (('yil', 'kilometre'), ('vites_tipi', 'yakit_tipi'), ('motor_hacmi', 'motor_gucu'))
        }),
        ('Hasar & Tramer', {
            'fields': (('tramer_kategori', 'tramer_tutari'), ('boyali_sayisi', 'degisen_sayisi'), 'boya_degisen_detay')
        }),
        ('Fiyat & İlan', {
            'fields': (('fiyat', 'ai_tahmin_fiyat'), 'sehir', 'kimden', 'aciklama')
        }),
        ('Satıcı Bilgileri', {
            'fields': ('satici', ('satici_adi', 'yetkili_kisi'), ('satici_tipi', 'yetki_belge_no')),
            'classes': ('collapse',)
        }),
        ('Sistem', {
            'fields': ('olusturuldu', 'guncellendi', 'ilan_tarihi'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_fav_count=Count('favoriler'))

    def kapak_foto(self, obj):
        foto = obj.fotolar.filter(kapak=True).first() or obj.fotolar.first()
        if foto and foto.foto:
            return format_html(
                '<img src="{}" style="height:48px;width:72px;object-fit:cover;border-radius:6px;border:1px solid #e2e8f0">',
                foto.foto.url
            )
        return mark_safe('<span style="color:#94a3b8;font-size:.75rem">Foto yok</span>')
    kapak_foto.short_description = ''

    def kapak_foto_buyuk(self, obj):
        foto = obj.fotolar.filter(kapak=True).first() or obj.fotolar.first()
        if foto and foto.foto:
            return format_html('<img src="{}" style="max-height:200px;border-radius:8px">', foto.foto.url)
        return '—'
    kapak_foto_buyuk.short_description = 'Kapak Fotoğraf'

    def marka_seri_model(self, obj):
        return format_html('<b>{}</b> {} <span style="color:#94a3b8">{}</span>', obj.marka, obj.seri, obj.model)
    marka_seri_model.short_description = 'Araç'
    marka_seri_model.admin_order_field = 'marka'

    def yil_km(self, obj):
        km = f'{obj.kilometre:,}'.replace(',', '.')
        return format_html('{} · <span style="color:#64748b">{} km</span>', obj.yil, km)
    yil_km.short_description = 'Yıl / KM'
    yil_km.admin_order_field = 'yil'

    def fiyat_formatted(self, obj):
        formatted = f'{int(obj.fiyat):,}'.replace(',', '.')
        return format_html('<b style="color:#2563eb">{} ₺</b>', formatted)
    fiyat_formatted.short_description = 'Fiyat'
    fiyat_formatted.admin_order_field = 'fiyat'

    def durum_badge(self, obj):
        renkler = {'aktif': '#059669', 'pasif': '#94a3b8', 'satildi': '#7c3aed', 'onay': '#d97706'}
        r = renkler.get(obj.durum, '#64748b')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:20px;font-size:.72rem;font-weight:700">{}</span>',
            r, obj.get_durum_display()
        )
    durum_badge.short_description = 'Durum'

    def favori_sayisi(self, obj):
        return format_html('<span style="color:#ef4444">♥ {}</span>', obj._fav_count)
    favori_sayisi.short_description = 'Favori'
    favori_sayisi.admin_order_field = '_fav_count'


@admin.register(FavoriModel)
class FavoriAdmin(admin.ModelAdmin):
    list_display    = ('kullanici', 'ilan_linki', 'olusturuldu')
    list_filter     = ('olusturuldu',)
    search_fields   = ('kullanici__username', 'ilan__baslik', 'ilan__marka')
    readonly_fields = ('olusturuldu',)

    def ilan_linki(self, obj):
        return format_html(
            '<a href="/ilan/{}/" target="_blank">{}</a>',
            obj.ilan.slug, obj.ilan.baslik[:50]
        )
    ilan_linki.short_description = 'İlan'


@admin.register(IletisimModel)
class IletisimAdmin(admin.ModelAdmin):
    list_display    = ('ad_soyad', 'email', 'telefon', 'konu_badge', 'mesaj_onizleme', 'okundu', 'okundu_badge', 'olusturuldu')
    list_filter     = ('konu', 'okundu')
    search_fields   = ('ad_soyad', 'email', 'mesaj')
    list_editable   = ('okundu',)
    readonly_fields = ('ip_adresi', 'olusturuldu', 'guncellendi')
    ordering        = ('-olusturuldu',)
    list_per_page   = 20

    fieldsets = (
        ('Gönderen', {'fields': ('kullanici', ('ad_soyad', 'email', 'telefon'))}),
        ('Mesaj',    {'fields': ('konu', 'mesaj')}),
        ('Durum',    {'fields': ('okundu', 'ip_adresi', 'olusturuldu')}),
    )

    def konu_badge(self, obj):
        renkler = {'genel': '#2563eb', 'teknik': '#7c3aed', 'ilan': '#059669', 'odeme': '#d97706', 'diger': '#64748b'}
        r = renkler.get(obj.konu, '#64748b')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:12px;font-size:.7rem;font-weight:700">{}</span>',
            r, obj.get_konu_display()
        )
    konu_badge.short_description = 'Konu'

    def mesaj_onizleme(self, obj):
        return format_html(
            '<span style="color:#475569">{}</span>',
            obj.mesaj[:60] + '…' if len(obj.mesaj) > 60 else obj.mesaj
        )
    mesaj_onizleme.short_description = 'Mesaj'

    def okundu_badge(self, obj):
        if obj.okundu:
            return mark_safe('<span style="color:#059669;font-weight:700">&#10003; Okundu</span>')
        return mark_safe('<span style="color:#ef4444;font-weight:700">&#9679; Yeni</span>')
    okundu_badge.short_description = 'Durum'
    okundu_badge.admin_order_field = 'okundu'
