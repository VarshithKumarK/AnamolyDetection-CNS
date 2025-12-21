"""Improved (v2) Autoencoder for UNSW-NB15 feature vectors.

This version increases robustness and anomaly sensitivity by using a deeper
architecture with BatchNormalization and Dropout (encoder only) and a smaller
latent bottleneck compared to the v1 model. The model is trained with MAE
loss to emphasize absolute reconstruction deviations.

Rationale:
- Stronger compression increases anomaly sensitivity: by constraining the
  latent space more aggressively, the autoencoder must prioritize the most
  common patterns in normal traffic, making it harder to reconstruct
  out-of-distribution attack flows.
- BatchNormalization stabilizes training across varying feature scales.
- Dropout in the encoder regularizes the representation to improve generalization.

TODO(Stage realtime): Use this model for inference as a drop-in replacement
once validated offline (keeps realtime compatibility: same input/output dims).
"""
from __future__ import annotations

from typing import Optional

import numpy as np

try:
    import tensorflow as tf
    from tensorflow.keras import Model
    from tensorflow.keras import layers
except Exception as exc:  # pragma: no cover
    raise ImportError(
        "TensorFlow is required to use autoencoder_v2. Install tensorflow>=2.x."
    ) from exc


def _block(x: "tf.Tensor", units: int, dropout: Optional[float] = None) -> "tf.Tensor":
    x = layers.Dense(units, use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    if dropout and dropout > 0:
        x = layers.Dropout(dropout)(x)
    return x


def build_autoencoder_v2(input_dim: int, encoder_dropout: float = 0.2) -> "Model":
    """Build a deeper symmetric autoencoder with BN and Dropout (encoder only).

    Parameters
    ----------
    input_dim : int
        Dimensionality of the preprocessed feature vector.
    encoder_dropout : float, optional
        Dropout rate to apply on encoder hidden layers (default 0.2).

    Returns
    -------
    keras.Model
        Autoencoder model with linear output layer.
    """
    inputs = layers.Input(shape=(input_dim,), name="input")

    # Encoder (deeper than v1) with stronger bottleneck
    e1 = _block(inputs, max(input_dim // 2, 1), dropout=encoder_dropout)
    e2 = _block(e1, max(input_dim // 4, 1), dropout=encoder_dropout)
    e3 = _block(e2, max(input_dim // 8, 1), dropout=encoder_dropout)
    # Smaller bottleneck than v1 (which used ~input_dim//8); use //16
    bottleneck = _block(e3, max(input_dim // 16, 1), dropout=encoder_dropout)

    # Decoder (symmetric, no dropout)
    d3 = _block(bottleneck, max(input_dim // 8, 1), dropout=0.0)
    d2 = _block(d3, max(input_dim // 4, 1), dropout=0.0)
    d1 = _block(d2, max(input_dim // 2, 1), dropout=0.0)

    outputs = layers.Dense(input_dim, activation=None, name="reconstruction")(d1)

    model = Model(inputs=inputs, outputs=outputs, name="dense_autoencoder_v2")
    return model


def reconstruction_error_mae(x: np.ndarray, x_hat: np.ndarray) -> np.ndarray:
    """Compute per-sample mean absolute reconstruction error (MAE)."""
    x = np.asarray(x)
    x_hat = np.asarray(x_hat)
    if x.shape != x_hat.shape:
        raise ValueError(
            f"Shape mismatch: x{x.shape} vs x_hat{x_hat.shape}. Ensure model outputs match input dimension."
        )
    return np.mean(np.abs(x - x_hat), axis=1)
