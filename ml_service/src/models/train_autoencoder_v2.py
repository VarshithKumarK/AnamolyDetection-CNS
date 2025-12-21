"""Train improved Autoencoder v2 on normal traffic only.

Uses a deeper architecture with BatchNorm+Dropout and MAE loss. Trains ONLY on
normal samples (label == 0) and saves the model for later evaluation.

Execution:
    python src/models/train_autoencoder_v2.py

Notes:
- EarlyStopping + ReduceLROnPlateau are used for robust convergence.
- Logs basic reconstruction statistics on the training data at the end.
- Labels are used only to select normal traffic; they are not used in loss.
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
from src.models.autoencoder_v2 import build_autoencoder_v2, reconstruction_error_mae  # type: ignore E402

try:
    import tensorflow as tf
except Exception as exc:  # pragma: no cover
    raise ImportError(
        "TensorFlow is required to train autoencoder_v2. Install tensorflow>=2.x."
    ) from exc

TRAIN_CSV = os.path.join("data", "UNSW_NB15_training-set.csv")
PREPROCESSOR_PKL = os.path.join("src", "preprocessing", "preprocessor.pkl")
MODEL_PATH = os.path.join("src", "models", "autoencoder_v2.keras")


def _log(msg: str) -> None:
    print(f"[ae_v2] {msg}")


def main() -> Tuple[int, int, float]:
    if not os.path.exists(TRAIN_CSV):
        raise FileNotFoundError(f"Training CSV not found at: {TRAIN_CSV}")
    if not os.path.exists(PREPROCESSOR_PKL):
        raise FileNotFoundError(f"Preprocessor not found at: {PREPROCESSOR_PKL}")

    df = pd.read_csv(TRAIN_CSV)
    normal_df = df.loc[df["label"] == 0]

    feature_cols = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    with open(PREPROCESSOR_PKL, "rb") as f:
        preprocessor = pickle.load(f)

    X = preprocessor.transform(normal_df[feature_cols])
    if hasattr(X, "toarray"):
        X = X.toarray()
    X = X.astype(np.float32, copy=False)

    n_samples, input_dim = X.shape
    _log(f"Training samples: {n_samples:,}")
    _log(f"Input dimension: {input_dim}")

    model = build_autoencoder_v2(input_dim)
    model.compile(optimizer=tf.keras.optimizers.Adam(), loss="mae")

    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=8, restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=4, min_lr=1e-6),
    ]

    history = model.fit(
        X,
        X,
        epochs=150,
        batch_size=256,
        validation_split=0.1,
        callbacks=callbacks,
        verbose=1,
        shuffle=True,
    )

    # Reconstruction statistics on training data (MAE)
    X_hat = model.predict(X, verbose=0)
    errs = reconstruction_error_mae(X, X_hat)
    _log(f"Reconstruction MAE | mean={errs.mean():.6f} median={np.median(errs):.6f} 95p={np.percentile(errs,95):.6f}")

    model.save(MODEL_PATH)
    _log(f"Saved Autoencoder v2 model to: {MODEL_PATH}")

    final_loss = float(history.history["loss"][ -1 ]) if history.history.get("loss") else float("nan")
    return n_samples, input_dim, final_loss


if __name__ == "__main__":
    main()
