from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('giris/',             views.giris,           name='giris'),
    path('kayit/',             views.kayit,           name='kayit'),
    path('cikis/',             views.cikis,           name='cikis'),
    path('profil/',            views.profil,          name='profil'),
    path('profil/guncelle/',   views.profil_guncelle, name='profil_guncelle'),
]
