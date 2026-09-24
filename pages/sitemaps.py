from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StatikSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['pages:index', 'pages:hakkimizda', 'predictions:tahmin']

    def location(self, item):
        return reverse(item)
