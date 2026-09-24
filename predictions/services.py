import json
import logging
from pathlib import Path

import joblib
import numpy as np

from django.conf import settings

from .utils import build_input_df, MARKA_CARPAN

logger = logging.getLogger(__name__)

ARTIFACT_DIR = settings.BASE_DIR / 'predictions' / 'artifacts'
DATA_DIR     = settings.BASE_DIR / 'predictions' / 'data'


class MLService:
    _model   = None
    _encoder = None
    _finfo   = None
    _meta    = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            cls._model = joblib.load(ARTIFACT_DIR / 'ensemble_rf_gb_best.pkl')
            logger.info('ML modeli yüklendi')
        return cls._model

    @classmethod
    def get_encoder(cls):
        if cls._encoder is None:
            cls._encoder = joblib.load(ARTIFACT_DIR / 'target_encoder.pkl')
        return cls._encoder

    @classmethod
    def get_feature_info(cls):
        if cls._finfo is None:
            with open(ARTIFACT_DIR / 'feature_info.json', encoding='utf-8') as f:
                cls._finfo = json.load(f)
        return cls._finfo

    @classmethod
    def get_meta(cls):
        if cls._meta is None:
            with open(DATA_DIR / 'form_meta.json', encoding='utf-8') as f:
                cls._meta = json.load(f)
        return cls._meta

    @classmethod
    def get_metrics(cls):
        model = cls.get_model()
        return {
            'r2':   model['metadata']['R2'],
            'mae':  model['metadata']['MAE'],
            'rmse': model['metadata']['RMSE'],
            'mape': model['metadata']['MAPE'],
        }

    @classmethod
    def predict(cls, data: dict) -> dict:
        """Fiyat tahmini + P10/P90 güven aralığı döndürür."""
        model   = cls.get_model()
        encoder = cls.get_encoder()
        finfo   = cls.get_feature_info()

        df = build_input_df(
            data,
            encoder=encoder,
            ohe_map=finfo['encoding']['one_hot_encoding'],
            feature_names=finfo['feature_names'],
        )

        rf_log   = model['components']['Random Forest'].predict(df)[0]
        gb_log   = model['components']['Gradient Boosting'].predict(df)[0]
        log_pred = model['weights']['Random Forest'] * rf_log + model['weights']['Gradient Boosting'] * gb_log
        fiyat    = float(np.expm1(log_pred))

        rf_model       = model['components']['Random Forest']
        log_tree_preds = np.array([t.predict(df)[0] for t in rf_model.estimators_])
        tree_preds     = np.expm1(log_tree_preds)
        dusuk          = float(np.percentile(tree_preds, 10))
        yuksek         = float(np.percentile(tree_preds, 90))

        carpan = MARKA_CARPAN.get(data.get('marka', ''), 1.0)
        fiyat  *= carpan
        dusuk  *= carpan
        yuksek *= carpan

        return {
            'fiyat' : round(fiyat),
            'dusuk' : round(dusuk),
            'yuksek': round(yuksek),
        }

    @classmethod
    def predict_confidence_only(cls, data: dict) -> dict:
        """Sadece RF ağaçlarından P10/P90 güven aralığı döndürür."""
        model   = cls.get_model()
        encoder = cls.get_encoder()
        finfo   = cls.get_feature_info()

        df = build_input_df(
            data,
            encoder=encoder,
            ohe_map=finfo['encoding']['one_hot_encoding'],
            feature_names=finfo['feature_names'],
        )

        rf_model       = model['components']['Random Forest']
        log_tree_preds = np.array([t.predict(df)[0] for t in rf_model.estimators_])
        tree_preds     = np.expm1(log_tree_preds)

        carpan = MARKA_CARPAN.get(data.get('marka', ''), 1.0)

        return {
            'dusuk' : round(float(np.percentile(tree_preds, 10)) * carpan),
            'yuksek': round(float(np.percentile(tree_preds, 90)) * carpan),
        }
