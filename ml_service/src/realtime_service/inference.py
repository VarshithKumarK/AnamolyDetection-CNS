"""
Realtime inference and scoring for UNSW-NB15 flows (Stage 4).

This module loads the fitted preprocessing pipeline and trained models,
then exposes a stateless function `score_flow` that computes anomaly
scores for a single network flow.

IMPORTANT:
- Threshold is FIXED based on offline evaluation (80th percentile of NORMAL traffic).
- No threshold recomputation happens in realtime.
"""

from __future__ import annotations

import pickle
from typing import Dict, Mapping, Union

import numpy as np
import pandas as pd
import tensorflow as tf

from src.models.autoencoder import reconstruction_error
from src.models.isolation_forest import anomaly_score as iforest_anomaly_score
from src.preprocessing.preprocessor import NUMERIC_FEATURES, CATEGORICAL_FEATURES


# -------------------------------------------------------------------
# 🔒 FROZEN OFFLINE-CALIBRATED CONFIGURATION
# -------------------------------------------------------------------

AE_WEIGHT = 0.7
IFOREST_WEIGHT = 0.3

# ❗ REPLACE this with the exact value from notebook (p = 80)
REALTIME_SCORE_THRESHOLD = 0.92   # <-- example ONLY


# -------------------------------------------------------------------
# Artifact paths
# -------------------------------------------------------------------

PREPROCESSOR_PKL = "src/preprocessing/preprocessor.pkl"
AUTOENCODER_PATH = "src/models/autoencoder_v2.keras"
IFOREST_PKL = "src/models/iforest_v2.pkl"


# -------------------------------------------------------------------
# Cached artifacts (loaded once)
# -------------------------------------------------------------------

_PREPROCESSOR = None
_AUTOENCODER = None
_IFOREST = None


def _load_artifacts():
    global _PREPROCESSOR, _AUTOENCODER, _IFOREST

    if _PREPROCESSOR is None:
        with open(PREPROCESSOR_PKL, "rb") as f:
            _PREPROCESSOR = pickle.load(f)

    if _AUTOENCODER is None:
        _AUTOENCODER = tf.keras.models.load_model(
            AUTOENCODER_PATH, compile=False
        )

    if _IFOREST is None:
        with open(IFOREST_PKL, "rb") as f:
            _IFOREST = pickle.load(f)


def _to_dataframe(
    flow: Union[Mapping[str, object], pd.Series, pd.DataFrame]
) -> pd.DataFrame:
    """Convert a single flow to a one-row DataFrame."""
    if isinstance(flow, pd.DataFrame):
        if len(flow) != 1:
            raise ValueError("Expected a single-row DataFrame")
        return flow

    if isinstance(flow, pd.Series):
        return flow.to_frame().T

    if isinstance(flow, Mapping):
        return pd.DataFrame([flow])

    raise TypeError("flow must be dict, Series, or single-row DataFrame")


def _preprocess(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """
    Returns:
    - X_full    : full preprocessed vector (numeric + categorical)
    - X_numeric : numeric-only preprocessed vector
    """
    cols_num = NUMERIC_FEATURES
    cols_cat = CATEGORICAL_FEATURES

    # Numeric-only (for Isolation Forest)
    X_numeric = _PREPROCESSOR.named_transformers_["num"].transform(df[cols_num])
    X_numeric = X_numeric.astype(np.float32, copy=False)

    # Full vector (for Autoencoder)
    X_full = _PREPROCESSOR.transform(df[cols_num + cols_cat])
    if hasattr(X_full, "toarray"):
        X_full = X_full.toarray()
    X_full = X_full.astype(np.float32, copy=False)

    return X_full, X_numeric



def _compute_scores(X_full: np.ndarray, X_numeric: np.ndarray) -> Dict[str, float]:
    """
    Compute per-model anomaly scores.

    X_full    : full preprocessed feature vector (AE input)
    X_numeric : numeric-only preprocessed vector (IF input)
    """
    # Autoencoder reconstruction error (uses full vector)
    x_hat = _AUTOENCODER.predict(X_full, verbose=0)
    ae_score = float(reconstruction_error(X_full, x_hat)[0])

    # Isolation Forest anomaly score (uses numeric-only vector)
    if_score = float(iforest_anomaly_score(_IFOREST, X_numeric)[0])

    return {"ae": ae_score, "iforest": if_score}



def _combine_scores(scores: Mapping[str, float]) -> float:
    """Weighted ensemble score."""
    return (
        AE_WEIGHT * scores["ae"]
        + IFOREST_WEIGHT * scores["iforest"]
    )


def score_flow(
    flow: Union[Mapping[str, object], pd.Series, pd.DataFrame]
) -> Dict[str, object]:
    """
    Score a single network flow.

    Returns
    -------
    dict:
        {
            "score": float,
            "is_anomaly": bool,
            "details": {
                "ae": float,
                "iforest": float
            }
        }
    """
    _load_artifacts()

    df = _to_dataframe(flow)
    X_full, X_numeric = _preprocess(df)
    scores = _compute_scores(X_full, X_numeric)
    final_score = _combine_scores(scores)

    is_anomaly = final_score > REALTIME_SCORE_THRESHOLD

    return {
        "score": float(final_score),
        "is_anomaly": bool(is_anomaly),
        "details": {
            "ae": float(scores["ae"]),
            "iforest": float(scores["iforest"]),
        },
    }
