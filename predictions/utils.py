MARKA_CARPAN = {
    "Audi":            1.2049,
    "BMW":             1.1532,
    "Chevrolet":       1.0353,
    "Citroen":         1.0605,
    "Dacia":           1.1468,
    "Fiat":            1.0857,
    "Ford":            1.1549,
    "Honda":           1.1933,
    "Hyundai":         1.1263,
    "Kia":             1.0699,
    "Mercedes - Benz": 1.2618,
    "Nissan":          1.1933,
    "Opel":            1.1481,
    "Peugeot":         1.0661,
    "Renault":         1.1095,
    "Seat":            1.1442,
    "Skoda":           1.1211,
    "Tofaş":           1.0949,
    "Toyota":          1.1665,
    "Volkswagen":      1.1644,
}

SEGMENT_MAE = [
    (300_000,      34_289, '0–300K'),
    (600_000,      44_427, '300K–600K'),
    (900_000,      57_479, '600K–900K'),
    (1_200_000,    75_693, '900K–1.2M'),
    (1_500_000,    87_306, '1.2M–1.5M'),
    (1_800_000,   113_692, '1.5M–1.8M'),
    (2_100_000,   139_870, '1.8M–2.1M'),
    (2_400_000,   208_115, '2.1M–2.4M'),
    (float('inf'), 279_303, '2.4M+'),
]


def get_segment_mae(fiyat):
    for limit, mae, label in SEGMENT_MAE:
        if fiyat < limit:
            return mae, label
    return SEGMENT_MAE[-1][1], SEGMENT_MAE[-1][2]


CAR_PANELS = [
    'Ön Tampon', 'Sol Ön Çamurluk', 'Motor Kaputu', 'Sağ Ön Çamurluk',
    'Sol Ön Kapı', 'Tavan', 'Sağ Ön Kapı',
    'Sol Arka Kapı', 'Sağ Arka Kapı',
    'Sol Arka Çamurluk', 'Bagaj Kapağı', 'Sağ Arka Çamurluk', 'Arka Tampon',
]


def normalise_panel_raw(raw):
    """Ham panel verisini standart 'Panel:Durum|...' formatına dönüştürür."""
    if not raw:
        return '|'.join(p + ':Orjinal' for p in CAR_PANELS)
    if ':' in raw and '|' in raw:
        return raw
    return raw.replace(' | ', '|')


def _firsat_skoru_hesapla(ilan, sapma_yuzdesi: float, bugun) -> int:
    """0-100 arası fırsat skoru: yüksek = iyi fırsat."""
    fiyat_puani = max(0.0, min(60.0, (-sapma_yuzdesi / 30.0) * 60.0))

    tramer_puani_map = {'yok': 20, 'dusuk': 12, 'orta': 4, 'bilinmiyor': 6, 'yuksek': 0}
    tramer_puani = tramer_puani_map.get(getattr(ilan, 'tramer_kategori', 'bilinmiyor'), 6)

    boyali  = getattr(ilan, 'boyali_sayisi', 0) or 0
    degisen = getattr(ilan, 'degisen_sayisi', 0) or 0
    boya_puani = max(0.0, 10.0 - boyali * 1.5 - degisen * 3.0)

    yil = getattr(ilan, 'yil', bugun.year)
    km  = getattr(ilan, 'kilometre', 0) or 0
    yas = max(bugun.year - yil, 1)
    km_per_yil = km / yas
    if   km_per_yil < 10000: km_puani = 10
    elif km_per_yil < 20000: km_puani = 7
    elif km_per_yil < 30000: km_puani = 4
    else:                    km_puani = 1

    return min(100, max(0, round(fiyat_puani + tramer_puani + boya_puani + km_puani)))


def build_input_df(data, *, encoder, ohe_map, feature_names):
    """Tahmin için pandas DataFrame oluşturur."""
    import datetime
    import numpy as np
    import pandas as pd

    data = dict(data)

    if 'marka' in data and 'seri' in data:
        data['marka'] = f"{data['marka']}_{data['seri']}"
        del data['seri']

    yas         = float(data.get('yas', 1)) or 1
    km          = float(data.get('kilometre', 0))
    motor_gucu  = float(data.get('motor_gucu', 0))
    motor_hacmi = float(data.get('motor_hacmi', 1)) or 1
    boyali      = float(data.get('boyali_sayisi', 0))
    degisen     = float(data.get('degisen_sayisi', 0))
    tramer_val  = float(data.get('tramer', 0))

    data['km_per_year']       = km / yas
    data['motor_verimlilik']  = motor_gucu / motor_hacmi
    data['hasar_skoru']       = boyali + degisen * 2
    data['log_km']            = float(np.log1p(km))
    data['motor_gucu_sq']     = motor_gucu ** 2
    data['tramer_bilinmiyor'] = 1 if tramer_val == 0 else 0

    df = pd.DataFrame([data])

    cat_cols = [c for c in ('marka', 'model', 'sehir') if c in df.columns]
    if cat_cols:
        df[cat_cols] = encoder.transform(df[cat_cols])

    numeric_cols = [
        'kilometre', 'motor_hacmi', 'motor_gucu', 'yas',
        'boyali_sayisi', 'degisen_sayisi', 'tramer',
        'marka', 'model', 'sehir',
        'km_per_year', 'motor_verimlilik', 'hasar_skoru',
        'log_km', 'motor_gucu_sq', 'tramer_bilinmiyor',
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    for orig_col, ohe_cols in ohe_map.items():
        col_val = data.get(orig_col, '')
        for ohe_col in ohe_cols:
            category    = ohe_col[len(orig_col) + 1:]
            df[ohe_col] = 1 if col_val == category else 0

    now = datetime.datetime.now()
    df['ilan_ay']  = now.month
    df['ilan_yil'] = now.year

    df = df.reindex(columns=feature_names, fill_value=0)
    return df
