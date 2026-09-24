from django.db import models
from django.contrib.auth.models import User
from core.models import ZamanDamgasi


class ProfilModel(ZamanDamgasi):
    kullanici = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profil',
        verbose_name='Kullanıcı',
    )
    telefon   = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefon')
    sehir     = models.CharField(max_length=50, blank=True, verbose_name='Şehir')
    avatar    = models.ImageField(
        upload_to='avatarlar/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Profil Fotoğrafı',
    )
    biyografi = models.TextField(blank=True, verbose_name='Hakkında')
    is_active = models.BooleanField(default=True, verbose_name='Aktif', db_index=True)

    class Meta:
        db_table            = 'ml_model_profilmodel'
        verbose_name        = 'Profil'
        verbose_name_plural = 'Profiller'
        indexes = [
            models.Index(fields=['kullanici']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.kullanici.get_full_name() or self.kullanici.username
