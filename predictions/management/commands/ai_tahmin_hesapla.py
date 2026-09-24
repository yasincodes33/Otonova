"""
python manage.py ai_tahmin_hesapla           # yalnızca boş ilanlar
python manage.py ai_tahmin_hesapla --hepsini # tüm aktif ilanlar
"""
import datetime
import logging

from django.core.management.base import BaseCommand

from listings.models import IlanModel
from predictions.services import MLService
from predictions.utils import _firsat_skoru_hesapla

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Aktif ilanlar için AI tahmin fiyatı ve fırsat skorunu batch hesaplar'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hepsini',
            action='store_true',
            help='ai_tahmin_fiyat dolu olsa bile yeniden hesapla',
        )

    def handle(self, *args, **options):
        queryset = IlanModel.objects.filter(is_active=True, durum='aktif')
        if not options['hepsini']:
            queryset = queryset.filter(ai_tahmin_fiyat__isnull=True)

        toplam = queryset.count()
        if toplam == 0:
            self.stdout.write(self.style.WARNING(
                'Hesaplanacak ilan bulunamadı. --hepsini ile yeniden hesaplayabilirsin.'
            ))
            return

        self.stdout.write(f'Hesaplanacak ilan: {toplam}')

        bugun    = datetime.date.today()
        toplu    = []
        basarili = 0
        hatali   = 0

        for i, ilan in enumerate(queryset.iterator(chunk_size=100), 1):
            try:
                veri = {
                    'marka': ilan.marka, 'seri': ilan.seri, 'model': ilan.model,
                    'yas':   str(max(bugun.year - ilan.yil, 1)),
                    'kilometre':      str(ilan.kilometre),
                    'motor_gucu':     str(ilan.motor_gucu or 0),
                    'motor_hacmi':    str(ilan.motor_hacmi or 1000),
                    'boyali_sayisi':  str(ilan.boyali_sayisi),
                    'degisen_sayisi': str(ilan.degisen_sayisi),
                    'tramer':         str(float(ilan.tramer_tutari)),
                    'vites_tipi': ilan.vites_tipi, 'yakit_tipi': ilan.yakit_tipi,
                    'kasa_tipi':  ilan.kasa_tipi,  'renk':       ilan.renk,
                    'cekis':      ilan.cekis,       'kimden':     ilan.kimden,
                    'sehir':      ilan.sehir,        'tramer_kategori': ilan.tramer_kategori,
                }
                result = MLService.predict(veri)
                ai     = result['fiyat']
                sapma  = (float(ilan.fiyat) - ai) / ai * 100
                skor   = _firsat_skoru_hesapla(ilan, sapma, bugun)

                ilan.ai_tahmin_fiyat  = ai
                ilan.ai_sapma_yuzdesi = sapma
                ilan.firsat_skoru     = skor
                toplu.append(ilan)
                basarili += 1
            except Exception:
                logger.exception('AI tahmin hatası: ilan_pk=%s', ilan.pk)
                hatali += 1

            if len(toplu) >= 100:
                IlanModel.objects.bulk_update(
                    toplu, ['ai_tahmin_fiyat', 'ai_sapma_yuzdesi', 'firsat_skoru'])
                toplu.clear()

            if i % 50 == 0:
                self.stdout.write(f'  {i}/{toplam} işlendi...')

        if toplu:
            IlanModel.objects.bulk_update(
                toplu, ['ai_tahmin_fiyat', 'ai_sapma_yuzdesi', 'firsat_skoru'])

        self.stdout.write(self.style.SUCCESS(
            f'\n[OK] Tamamlandı\n'
            f'  Hesaplanan : {basarili}\n'
            f'  Hata       : {hatali}\n'
        ))
