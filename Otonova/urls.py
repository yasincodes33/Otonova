from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path, re_path
from django.conf import settings
from django.views.generic import TemplateView
from django.views.static import serve

from listings.sitemaps import IlanSitemap
from pages.sitemaps import StatikSitemap

_sitemaps = {'ilanlar': IlanSitemap, 'statik': StatikSitemap}

urlpatterns = [
    path('admin/', admin.site.urls),

    # ── Statik/meta ──
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('sitemap.xml', sitemap, {'sitemaps': _sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # ── Şifre sıfırlama (Django built-in) ──
    path('sifremi-unuttum/', auth_views.PasswordResetView.as_view(
        template_name='accounts/sifre/sifre_sifirla.html',
        email_template_name='accounts/email/sifre_sifirla_email.txt',
        subject_template_name='accounts/email/sifre_sifirla_konu.txt',
        success_url='/sifremi-unuttum/gonderildi/'), name='password_reset'),
    path('sifremi-unuttum/gonderildi/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/sifre/sifre_sifirla_gonderildi.html'), name='password_reset_done'),
    path('sifremi-sifirla/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/sifre/sifre_sifirla_onayla.html',
        success_url='/sifremi-sifirla/tamamlandi/'), name='password_reset_confirm'),
    path('sifremi-sifirla/tamamlandi/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/sifre/sifre_sifirla_tamamlandi.html'), name='password_reset_complete'),

    # ── Yeni app URL'leri (namespace'li) ──
    path('', include('pages.urls')),
    path('', include('accounts.urls')),
    path('', include('listings.urls')),
    path('', include('predictions.urls')),

    # ── Media ──
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
