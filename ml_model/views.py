import json
import datetime

import joblib
import numpy as np
import pandas as pd

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

MODEL_PATH   = settings.BASE_DIR / 'ml_model' / 'model' / 'arac_fiyat_modeli.pkl'
ENCODER_PATH = settings.BASE_DIR / 'ml_model' / 'model' / 'target_encoder.pkl'

MODEL   = joblib.load(MODEL_PATH)
ENCODER = joblib.load(ENCODER_PATH)
print("Model tipi  :", type(MODEL))
print("Encoder tipi:", type(ENCODER))

METRICS = {
    'r2': 0.9602,
    'mae': 59782.88,
    'rmse': 92556.55,
    'mape': 10.60
}

META_PATH = settings.BASE_DIR / 'form_meta.json'
with open(META_PATH, encoding='utf-8') as f:
    META = json.load(f)


def index(request):
    return render(request, 'tahmin/anasayfa.html')


def tahmin(request):
    ctx = {
        'markalar': sorted(META['marka_seri_map'].keys()),
        'model': sorted(META['model']),
        'vites_tipleri': META['vites_tipi'],
        'yakit_tipleri': META['yakit_tipi'],
        'kasa_tipleri': META['kasa_tipi'],
        'renkler': META['renk'],
        'cekis_tipleri': META['cekis'],
        'kimden_listesi': META['kimden'],
        'tramer_kategorileri': META['tramer_kategori'],
        'sehirler': META['sehir'],
        'motor_hacimler': META['motor_hacmi'],
        'metrics': METRICS,
        'marka_seri_json': json.dumps(META['marka_seri_map']),
    }
    return render(request, 'tahmin/index.html', ctx)


def arabalar(request):
    return render(request, 'tahmin/arabalar.html')


def satis(request):
    return render(request, 'tahmin/satis.html')


def hakkimizda(request):
    return render(request, 'tahmin/hakkimizda.html')


def iletisim(request):
    return render(request, 'tahmin/iletisim.html')


def giris(request):
    return render(request, 'tahmin/giris.html')


def kayit(request):
    return render(request, 'tahmin/kayit.html')


@csrf_exempt
def tahmin_et(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Sadece POST'}, status=405)

    try:
        data = json.loads(request.body)
        df_in = build_input_df(data)

        log_tree_preds = np.array([t.predict(df_in)[0] for t in MODEL.estimators_])
        tree_preds = np.expm1(log_tree_preds)

        fiyat  = float(np.mean(tree_preds))
        dusuk  = float(np.percentile(tree_preds, 10))
        yuksek = float(np.percentile(tree_preds, 90))

        return JsonResponse({
            'fiyat' : round(fiyat),
            'dusuk' : round(dusuk),
            'yuksek': round(yuksek),
            'r2'    : round(METRICS['r2'], 4),
            'mae'   : round(METRICS['mae']),
            'mape'  : round(METRICS['mape'], 2),
        })
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({'error': f'Model Hatası: {str(e)}'}, status=200)


def build_input_df(data):
    data = dict(data)

    # 1. marka + seri → birleştir ("BMW" + "3 Serisi" → "BMW_3 Serisi")
    if 'marka' in data and 'seri' in data:
        data['marka'] = f"{data['marka']}_{data['seri']}"
        del data['seri']

    df = pd.DataFrame([data])

    # 2. Target encoding: marka / model / sehir → sayısal
    cat_cols = [c for c in ('marka', 'model', 'sehir') if c in df.columns]
    if cat_cols:
        df[cat_cols] = ENCODER.transform(df[cat_cols])

    # 3. Sayısal kolonları düzelt
    numeric_cols = ['kilometre', 'motor_hacmi', 'motor_gucu', 'yas',
                    'boyali_sayisi', 'degisen_sayisi', 'tramer',
                    'marka', 'model', 'sehir']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 4. Kalan kategorik kolonlar → One-Hot Encoding
    df = pd.get_dummies(df)

    # 5. İlan tarihi (formda yok → güncel tarih)
    now = datetime.datetime.now()
    if 'ilan_ay'  not in df.columns:
        df['ilan_ay']  = now.month
    if 'ilan_yil' not in df.columns:
        df['ilan_yil'] = now.year

    # 6. Modelin beklediği sütun yapısına hizala
    if hasattr(MODEL, 'feature_names_in_'):
        df = df.reindex(columns=MODEL.feature_names_in_, fill_value=0)

    return df
