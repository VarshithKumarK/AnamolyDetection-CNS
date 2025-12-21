"""Offline model testing on UNSW-NB15 test split (no training).

Validates trained models using the test dataset by computing anomaly scores for
normal vs. attack samples. This script does not refit preprocessing, does not
train any models, and performs only deterministic, reproducible computations.

Execution:
    python src/evaluation/test_models.py

Printed outputs:
- Mean/median autoencoder (AE) reconstruction error for normal vs. attack
- Mean/median Isolation Forest (IF) anomaly score for normal vs. attack
- Percentage of attack samples above the 95th percentile of NORMAL scores
  (reported separately for AE and IF)

Notes:
- Labels are used ONLY for evaluation in this stage.
- Preprocessor is loaded from disk and applied without refitting.
"""
from __future__ import annotations

import os
import pickle
import sys
from typing import Tuple

import numpy as np
import pandas as pd

# Ensure project root is on sys.path for absolute imports when running as a script
THIS_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, os.pardir, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.preprocessing.preprocessor import (  # type: ignore E402
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
)
from src.models.autoencoder import reconstruction_error  # type: ignore E402

TEST_CSV = os.path.join("data", "UNSW_NB15_testing-set.csv")
PREPROCESSOR_PKL = os.path.join("src", "preprocessing", "preprocessor.pkl")
AUTOENCODER_PATH = os.path.join("src", "models", "autoencoder.h5")
IFOREST_PKL = os.path.join("src", "models", "iforest.pkl")


def _log(msg: str) -> None:
    print(f"[evaluation] {msg}")


def _load_artifacts():
    # Preprocessor
    with open(PREPROCESSOR_PKL, "rb") as f:
        pre = pickle.load(f)

    # Autoencoder
    try:
        import tensorflow as tf  # local import to avoid hard dependency if unused
    except Exception as exc:  # pragma: no cover
        raise ImportError(
            "TensorFlow is required to load the autoencoder model."
        ) from exc
    ae = tf.keras.models.load_model(AUTOENCODER_PATH, compile=False)

    # Isolation Forest
    with open(IFOREST_PKL, "rb") as f:
        iforest = pickle.load(f)

    return pre, ae, iforest


def _score_models(pre, ae, iforest, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    feature_cols = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    X = pre.transform(df[feature_cols])
    if hasattr(X, "toarray"):
        X = X.toarray()
    X = X.astype(np.float32, copy=False)

    # Autoencoder reconstruction error
    X_hat = ae.predict(X, verbose=0)
    ae_scores = reconstruction_error(X, X_hat)

    # Isolation Forest anomaly score (higher => more anomalous)
    if_scores = -iforest.decision_function(X)

    return ae_scores, if_scores


def _percent_above_threshold(values: np.ndarray, threshold: float) -> float:
    if values.size == 0:
        return float("nan")
    return 100.0 * float((values > threshold).sum()) / float(values.size)


def main() -> None:
    if not os.path.exists(TEST_CSV):
        raise FileNotFoundError(f"Test CSV not found at: {TEST_CSV}")
    if not os.path.exists(PREPROCESSOR_PKL):
        raise FileNotFoundError(f"Preprocessor not found at: {PREPROCESSOR_PKL}")
    if not os.path.exists(AUTOENCODER_PATH):
        raise FileNotFoundError(f"Autoencoder not found at: {AUTOENCODER_PATH}")
    if not os.path.exists(IFOREST_PKL):
        raise FileNotFoundError(f"Isolation Forest not found at: {IFOREST_PKL}")

    df = pd.read_csv(TEST_CSV)

    # Evaluation uses labels only for separation
    normal_df = df.loc[df["label"] == 0]
    attack_df = df.loc[df["label"] == 1]

    _log(f"Normal samples: {len(normal_df):,} | Attack samples: {len(attack_df):,}")

    pre, ae, iforest = _load_artifacts()

    # Score both groups deterministically (no training)
    ae_n, if_n = _score_models(pre, ae, iforest, normal_df)
    ae_a, if_a = _score_models(pre, ae, iforest, attack_df)

    # Summaries
    def stats(name: str, normal: np.ndarray, attack: np.ndarray) -> None:
        _log(
            f"{name} | mean(normal)={np.mean(normal):.6f} median(normal)={np.median(normal):.6f} "
            f"| mean(attack)={np.mean(attack):.6f} median(attack)={np.median(attack):.6f}"
        )

    stats("AE  ", ae_n, ae_a)
    stats("IF  ", if_n, if_a)

    # 95th percentile on NORMAL scores, evaluate attack exceedance
    ae_thr = float(np.percentile(ae_n, 95)) if ae_n.size else float("nan")
    if_thr = float(np.percentile(if_n, 95)) if if_n.size else float("nan")

    ae_attack_pct = _percent_above_threshold(ae_a, ae_thr)
    if_attack_pct = _percent_above_threshold(if_a, if_thr)

    _log(f"AE  | normal_95th={ae_thr:.6f} | %attack_above_norm95={ae_attack_pct:.2f}%")
    _log(f"IF  | normal_95th={if_thr:.6f} | %attack_above_norm95={if_attack_pct:.2f}%")


if __name__ == "__main__":
    main()
