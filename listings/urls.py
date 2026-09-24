from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    path('arabalar/',           views.arabalar,      name='arabalar'),
    path('ilan/<slug:slug>/',   views.ilan_detay,    name='ilan_detay'),
    path('satis/',              views.satis,         name='satis'),
    path('iletisim/',           views.iletisim,      name='iletisim'),
    path('favoriler/',          views.favoriler,     name='favoriler'),
    path('api/favori/',         views.favori_toggle, name='favori_toggle'),
]
