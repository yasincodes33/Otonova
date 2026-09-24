import datetime
from django.test import TestCase

from .utils import _firsat_skoru_hesapla


class UtilsTest(TestCase):
    def test_firsat_skoru_aralik(self):
        class FakeIlan:
            tramer_kategori = 'yok'
            boyali_sayisi   = 0
            degisen_sayisi  = 0
            yil             = 2020
            kilometre       = 50000

        skor = _firsat_skoru_hesapla(FakeIlan(), -25.0, datetime.date(2026, 1, 1))
        self.assertGreaterEqual(skor, 0)
        self.assertLessEqual(skor, 100)

    def test_firsat_skoru_yuksek_sapma(self):
        class FakeIlan:
            tramer_kategori = 'yok'
            boyali_sayisi   = 0
            degisen_sayisi  = 0
            yil             = 2022
            kilometre       = 10000

        skor = _firsat_skoru_hesapla(FakeIlan(), -35.0, datetime.date(2026, 1, 1))
        self.assertGreater(skor, 50)
