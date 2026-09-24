from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import ProfilModel


@receiver(post_save, sender=User)
def olustur_kullanici_profili(sender, instance, created, **kwargs):
    if created:
        ProfilModel.objects.get_or_create(kullanici=instance)
