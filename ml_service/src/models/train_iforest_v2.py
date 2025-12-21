"""Train improved Isolation Forest (v2) on numeric features only.

Isolation Forest can be negatively affected by high-dimensional sparse
one-hot encoded categorical features (noise relative to numeric signal), which
may dilute isolation paths. To improve robustness, v2 trains IF on NUMERIC
features only, preserving the most informative continuous statistics.

Hyperparameters:
- n_estimators = 500 (more trees increases stability)
- max_samples = 0.8 (subsample per tree for robustness and speed)

Execution:
    python src/models/train_iforest_v2.py

Notes:
- Trains ONLY on normal traffic (label == 0); still unsupervised in objective.
- Saves to src/models/iforest_v2.pkl
"""
from __future__ import annotations

import os
import pickle
import sys
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

# Ensure project root is on sys.path for absolute imports when running as a script
THIS_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, os.pardir, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.preprocessing.preprocessor import NUMERIC_FEATURES  # type: ignore E402

TRAIN_CSV = os.path.join("data", "UNSW_NB15_training-set.csv")
PREPROCESSOR_PKL = os.path.join("src", "preprocessing", "preprocessor.pkl")
MODEL_PATH = os.path.join("src", "models", "iforest_v2.pkl")


def _log(msg: str) -> None:
    print(f"[iforest_v2] {msg}")


def main() -> Tuple[int, int]:
    if not os.path.exists(TRAIN_CSV):
        raise FileNotFoundError(f"Training CSV not found at: {TRAIN_CSV}")
    if not os.path.exists(PREPROCESSOR_PKL):
        raise FileNotFoundError(f"Preprocessor not found at: {PREPROCESSOR_PKL}")

    df = pd.read_csv(TRAIN_CSV)
    normal_df = df.loc[df["label"] == 0]

    # Use numeric features only, but still scale them via the existing preprocessor's numeric scaler
    with open(PREPROCESSOR_PKL, "rb") as f:
        preprocessor = pickle.load(f)

    num_scaler = preprocessor.named_transformers_["num"]
    X_num = num_scaler.transform(normal_df[NUMERIC_FEATURES])
    if hasattr(X_num, "toarray"):
        X_num = X_num.toarray()
    X_num = X_num.astype(np.float32, copy=False)

    n_samples, n_features = X_num.shape
    _log(f"Training samples: {n_samples:,}")
    _log(f"Numeric feature dimension: {n_features}")

    model = IsolationForest(
        n_estimators=500,
        max_samples=0.8,
        contamination="auto",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_num)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    _log(f"Saved Isolation Forest v2 to: {MODEL_PATH}")

    return n_samples, n_features


if __name__ == "__main__":
    main()
