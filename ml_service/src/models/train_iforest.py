"""Train Isolation Forest on normal traffic (Stage 3).

Loads the fitted preprocessor, transforms normal samples from the UNSW-NB15
training set, fits an IsolationForest, and saves the trained model.

Execution:
    python src/models/train_iforest.py

Notes:
- Labels are used only to filter normal traffic (label == 0). No labels are
  used by the IsolationForest during fitting.
- TODO(Stage 4): Load the saved model for realtime inference and scoring.
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
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
)
from src.models.isolation_forest import train_iforest  # type: ignore E402

TRAIN_CSV = os.path.join("data", "UNSW_NB15_training-set.csv")
PREPROCESSOR_PKL = os.path.join("src", "preprocessing", "preprocessor.pkl")
MODEL_PATH = os.path.join("src", "models", "iforest.pkl")


def _log(msg: str) -> None:
    print(f"[iforest] {msg}")


def main() -> Tuple[int, int]:
    if not os.path.exists(TRAIN_CSV):
        raise FileNotFoundError(f"Training CSV not found at: {TRAIN_CSV}")
    if not os.path.exists(PREPROCESSOR_PKL):
        raise FileNotFoundError(f"Preprocessor not found at: {PREPROCESSOR_PKL}")

    # Load data
    df = pd.read_csv(TRAIN_CSV)

    # Filter normal traffic only
    normal_df = df.loc[df["label"] == 0]

    feature_cols = NUMERIC_FEATURES + CATEGORICAL_FEATURES

    # Load and apply preprocessor
    with open(PREPROCESSOR_PKL, "rb") as f:
        preprocessor = pickle.load(f)

    X_normal = preprocessor.transform(normal_df[feature_cols])

    # Ensure dense array for sklearn IsolationForest
    if hasattr(X_normal, "toarray"):
        X_normal = X_normal.toarray()
    X_normal = X_normal.astype(np.float32, copy=False)

    n_samples, n_features = X_normal.shape
    _log(f"Number of samples: {n_samples:,}")
    _log(f"Feature dimension: {n_features}")

    model = train_iforest(X_normal)

    # Persist model
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    _log(f"Saved Isolation Forest model to: {MODEL_PATH}")

    return n_samples, n_features


if __name__ == "__main__":
    main()
