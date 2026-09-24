import datetime
import json
import logging

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import TahminGecmisi
from .services import MLService

logger = logging.getLogger(__name__)


def tahmin(request):
    meta    = MLService.get_meta()
    metrics = MLService.get_metrics()
    ctx = {
        'markalar'             : sorted(meta['marka_seri_map'].keys()),
        'model'                : sorted(meta['model']),
        'vites_tipleri'        : meta['vites_tipi'],
        'yakit_tipleri'        : meta['yakit_tipi'],
        'kasa_tipleri'         : meta['kasa_tipi'],
        'renkler'              : meta['renk'],
        'cekis_tipleri'        : meta['cekis'],
        'kimden_listesi'       : meta['kimden'],
        'tramer_kategorileri'  : meta['tramer_kategori'],
        'sehirler'             : meta['sehir'],
        'motor_hacimler'       : meta['motor_hacmi'],
        'metrics'              : metrics,
        'marka_seri_json'            : json.dumps(meta['marka_seri_map']),
        'marka_seri_model_json'      : json.dumps(meta.get('marka_seri_model_map', {})),
        'marka_seri_model_kasa_json' : json.dumps(meta.get('marka_seri_model_kasa_map', {})),
        'kasa_tipleri_json'          : json.dumps(meta['kasa_tipi']),
    }
    return render(request, 'predictions/index.html', ctx)


@csrf_exempt
def tahmin_et(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Sadece POST'}, status=405)

    try:
        data    = json.loads(request.body)
        result  = MLService.predict(data)
        metrics = MLService.get_metrics()

        TahminGecmisi.objects.create(
            kullanici       = request.user if request.user.is_authenticated else None,
            marka           = data.get('marka', ''),
            seri            = data.get('seri', ''),
            model           = data.get('model', ''),
            yil             = int(datetime.datetime.now().year - float(data.get('yas', 1))),
            kilometre       = int(float(data.get('kilometre', 0))),
            vites_tipi      = data.get('vites_tipi', ''),
            yakit_tipi      = data.get('yakit_tipi', ''),
            kasa_tipi       = data.get('kasa_tipi', '-'),
            motor_hacmi     = int(float(data.get('motor_hacmi', 0))) or None,
            motor_gucu      = int(float(data.get('motor_gucu', 0))) or None,
            sehir           = data.get('sehir', ''),
            kimden          = data.get('kimden', 'Sahibinden'),
            tramer_kategori = data.get('tramer_kategori', 'bilinmiyor'),
            tramer_tutari   = float(data.get('tramer', 0)),
            boyali_sayisi   = int(float(data.get('boyali_sayisi', 0))),
            degisen_sayisi  = int(float(data.get('degisen_sayisi', 0))),
            tahmin_fiyat    = result['fiyat'],
            dusuk_sinir     = result['dusuk'],
            yuksek_sinir    = result['yuksek'],
            r2_skoru        = metrics['r2'],
            mape_skoru      = metrics['mape'],
            ip_adresi       = request.META.get('REMOTE_ADDR'),
            tarayici        = request.META.get('HTTP_USER_AGENT', '')[:200],
        )

        return JsonResponse({
            'fiyat' : result['fiyat'],
            'dusuk' : result['dusuk'],
            'yuksek': result['yuksek'],
            'r2'    : round(metrics['r2'], 4),
            'mae'   : round(metrics['mae']),
            'mape'  : round(metrics['mape'], 2),
        })
    except Exception as e:
        logger.exception('Tahmin API hatası')
        return JsonResponse({'error': f'Model Hatası: {str(e)}'}, status=200)
