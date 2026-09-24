from django.contrib import admin
from django.utils.html import format_html

from .models import TahminGecmisi


@admin.register(TahminGecmisi)
class TahminGecmisiAdmin(admin.ModelAdmin):
    list_display    = ('marka_model_yil', 'tahmin_fiyat_formatted', 'r2_badge', 'kullanici', 'sehir', 'ip_adresi', 'olusturuldu')
    list_filter     = ('marka', 'yakit_tipi', 'vites_tipi', 'kasa_tipi')
    search_fields   = ('marka', 'model', 'kullanici__username')
    readonly_fields = ('olusturuldu', 'guncellendi', 'ip_adresi', 'tarayici')
    ordering        = ('-olusturuldu',)
    list_per_page   = 30

    fieldsets = (
        ('Araç',        {'fields': (('marka', 'seri', 'model'), ('yil', 'kilometre'), ('vites_tipi', 'yakit_tipi', 'kasa_tipi'))}),
        ('Tahmin',      {'fields': (('tahmin_fiyat', 'dusuk_sinir', 'yuksek_sinir'), ('r2_skoru', 'mape_skoru'))}),
        ('İstek Bilgisi', {'fields': ('kullanici', 'ip_adresi', 'tarayici', 'olusturuldu'), 'classes': ('collapse',)}),
    )

    def marka_model_yil(self, obj):
        return format_html('<b>{}</b> {} <span style="color:#64748b">({})</span>', obj.marka, obj.model, obj.yil)
    marka_model_yil.short_description = 'Araç'

    def tahmin_fiyat_formatted(self, obj):
        if obj.tahmin_fiyat:
            formatted = f'{int(obj.tahmin_fiyat):,}'.replace(',', '.')
            return format_html('<b style="color:#2563eb">{} ₺</b>', formatted)
        return '—'
    tahmin_fiyat_formatted.short_description = 'Tahmin Fiyatı'

    def r2_badge(self, obj):
        if obj.r2_skoru:
            r = round(float(obj.r2_skoru), 3)
            color = '#059669' if r >= 0.9 else '#d97706'
            return format_html('<span style="color:{};font-weight:700">{}</span>', color, r)
        return '—'
    r2_badge.short_description = 'R²'
