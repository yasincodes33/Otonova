from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import IlanModel


class IlanSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.8

    def items(self):
        return IlanModel.objects.filter(is_active=True, durum='aktif')

    def location(self, obj):
        return reverse('listings:ilan_detay', kwargs={'slug': obj.slug})

    def lastmod(self, obj):
        return obj.guncellendi
