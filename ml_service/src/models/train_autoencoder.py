"""Train the autoencoder on normal traffic only (Stage 3).

Loads the fitted preprocessor, transforms normal samples from the UNSW-NB15
training set, builds a dense autoencoder with matching input dimension, and
trains it using MSE loss with early stopping.

Execution:
    python src/models/train_autoencoder.py

Notes:
- Labels are used only to select normal traffic (label == 0). No labels are
  used during optimization.
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
from src.models.autoencoder import build_autoencoder  # type: ignore E402

try:
    import tensorflow as tf
except Exception as exc:  # pragma: no cover - import-time check
    raise ImportError(
        "TensorFlow is required for training the autoencoder. Install tensorflow>=2.x."
    ) from exc

TRAIN_CSV = os.path.join("data", "UNSW_NB15_training-set.csv")
PREPROCESSOR_PKL = os.path.join("src", "preprocessing", "preprocessor.pkl")
MODEL_PATH = os.path.join("src", "models", "autoencoder.h5")


def _log(msg: str) -> None:
    print(f"[autoencoder] {msg}")


def main() -> Tuple[int, int, float]:
    if not os.path.exists(TRAIN_CSV):
        raise FileNotFoundError(f"Training CSV not found at: {TRAIN_CSV}")
    if not os.path.exists(PREPROCESSOR_PKL):
        raise FileNotFoundError(f"Preprocessor not found at: {PREPROCESSOR_PKL}")

    # Load data
    df = pd.read_csv(TRAIN_CSV)

    # Select normal traffic only
    normal_df = df.loc[df["label"] == 0]

    feature_cols = NUMERIC_FEATURES + CATEGORICAL_FEATURES

    # Load and apply preprocessor
    with open(PREPROCESSOR_PKL, "rb") as f:
        preprocessor = pickle.load(f)

    X_normal = preprocessor.transform(normal_df[feature_cols])
    # Ensure dense float32 for Keras
    if hasattr(X_normal, "toarray"):
        X_normal = X_normal.toarray()
    X_normal = X_normal.astype(np.float32, copy=False)

    n_samples, input_dim = X_normal.shape
    _log(f"Training samples: {n_samples:,}")
    _log(f"Input dimension: {input_dim}")

    # Build model
    model = build_autoencoder(input_dim)
    model.compile(optimizer=tf.keras.optimizers.Adam(), loss="mse")

    # Callbacks
    early_stop = tf.keras.callbacks.EarlyStopping(
        monitor="val_loss", patience=5, restore_best_weights=True
    )

    history = model.fit(
        X_normal,
        X_normal,
        epochs=100,
        batch_size=256,
        validation_split=0.1,
        callbacks=[early_stop],
        verbose=1,
        shuffle=True,
    )

    final_loss = float(history.history["loss"][ -1 ]) if history.history.get("loss") else float("nan")
    _log(f"Final training loss: {final_loss:.6f}")

    # Persist model
    model.save(MODEL_PATH)
    _log(f"Saved autoencoder model to: {MODEL_PATH}")

    return n_samples, input_dim, final_loss


if __name__ == "__main__":
    main()
