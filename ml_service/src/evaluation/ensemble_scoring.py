"""Ensemble scoring utilities for improved anomaly detection accuracy.

Combines Autoencoder v2 and Isolation Forest v2 scores after normalizing each
by z-scoring on NORMAL traffic only. This preserves the unsupervised nature of
training while enabling calibrated combination of heterogeneous scores.

final_score = 0.7 * AE_z + 0.3 * IF_z

Justification:
- The autoencoder directly optimizes reconstruction on normal data and often
  exhibits stronger separation; thus it receives higher weight (0.7).
- Isolation Forest adds a complementary perspective with tree-based isolation;
  it contributes at 0.3 to avoid overpowering AE in most regimes.

Labels are used only for evaluation (to identify normal vs. attack groups when
computing z-scores and metrics). No labels are used during training.
"""
from __future__ import annotations

import os
import pickle
from typing import Dict, Tuple

import numpy as np
import pandas as pd

from src.preprocessing.preprocessor import NUMERIC_FEATURES, CATEGORICAL_FEATURES
from src.models.autoencoder_v2 import reconstruction_error_mae

try:
    import tensorflow as tf
except Exception as exc:  # pragma: no cover
    raise ImportError("TensorFlow is required for AE v2 inference.") from exc

AE_V2_PATH = os.path.join("src", "models", "autoencoder_v2.keras")
IF_V2_PKL = os.path.join("src", "models", "iforest_v2.pkl")
PREPROCESSOR_PKL = os.path.join("src", "preprocessing", "preprocessor.pkl")


def _load_artifacts():
    with open(PREPROCESSOR_PKL, "rb") as f:
        pre = pickle.load(f)
    ae = tf.keras.models.load_model(AE_V2_PATH)
    with open(IF_V2_PKL, "rb") as f:
        iforest = pickle.load(f)
    return pre, ae, iforest


def _preprocess_full(pre, df: pd.DataFrame) -> np.ndarray:
    X = pre.transform(df[NUMERIC_FEATURES + CATEGORICAL_FEATURES])
    if hasattr(X, "toarray"):
        X = X.toarray()
    return X.astype(np.float32, copy=False)


def _preprocess_numeric(pre, df: pd.DataFrame) -> np.ndarray:
    num_scaler = pre.named_transformers_["num"]
    Xn = num_scaler.transform(df[NUMERIC_FEATURES])
    if hasattr(Xn, "toarray"):
        Xn = Xn.toarray()
    return Xn.astype(np.float32, copy=False)


def score_components(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    """Return AE_v2 MAE errors and IF_v2 anomaly scores for given samples."""
    pre, ae, iforest = _load_artifacts()
    X_full = _preprocess_full(pre, df)
    X_num = _preprocess_numeric(pre, df)

    X_hat = ae.predict(X_full, verbose=0)
    ae_scores = reconstruction_error_mae(X_full, X_hat)

    if_scores = -iforest.decision_function(X_num)
    return ae_scores, if_scores


def zscore_on_normal(ae_scores_n: np.ndarray, if_scores_n: np.ndarray) -> Tuple[Dict[str, float], Dict[str, float]]:
    """Compute z-score parameters (mean, std) on normal traffic for AE and IF."""
    eps = 1e-12
    ae_mu, ae_sigma = float(np.mean(ae_scores_n)), float(np.std(ae_scores_n) + eps)
    if_mu, if_sigma = float(np.mean(if_scores_n)), float(np.std(if_scores_n) + eps)
    return {"mu": ae_mu, "sigma": ae_sigma}, {"mu": if_mu, "sigma": if_sigma}


def combine_scores(ae_scores: np.ndarray, if_scores: np.ndarray, ae_params: Dict[str, float], if_params: Dict[str, float]) -> np.ndarray:
    """Combine z-scored AE and IF scores with fixed weights.

    final = 0.7 * z(AE) + 0.3 * z(IF)
    """
    ae_z = (ae_scores - ae_params["mu"]) / max(ae_params["sigma"], 1e-12)
    if_z = (if_scores - if_params["mu"]) / max(if_params["sigma"], 1e-12)
    return 0.7 * ae_z + 0.3 * if_z
