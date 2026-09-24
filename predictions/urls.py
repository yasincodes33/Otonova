from django.urls import path
from . import views

app_name = 'predictions'

urlpatterns = [
    path('tahmin/',     views.tahmin,    name='tahmin'),
    path('api/tahmin/', views.tahmin_et, name='tahmin_et'),
]
