from django.db import models


class ZamanDamgasi(models.Model):
    """Tüm modellerin türediği soyut taban: oluşturma/güncelleme zaman damgaları."""
    olusturuldu = models.DateTimeField(auto_now_add=True)
    guncellendi = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
