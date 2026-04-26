
from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('tahmin/', views.tahmin, name='tahmin'),
    path('api/tahmin/', views.tahmin_et, name='tahmin_et'),
    path('arabalar/', views.arabalar, name='arabalar'),
    path('satis/', views.satis, name='satis'),
    path('hakkimizda/', views.hakkimizda, name='hakkimizda'),
    path('iletisim/', views.iletisim, name='iletisim'),
    path('giris/', views.giris, name='giris'),
    path('kayit/', views.kayit, name='kayit'),
]