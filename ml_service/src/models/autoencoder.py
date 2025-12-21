"""Autoencoder model for UNSW-NB15 feature vectors (Stage 3).

Defines a configurable dense autoencoder using TensorFlow/Keras. The
autoencoder learns to reconstruct normal (benign) network flows in the
preprocessed feature space. During inference, reconstruction error serves as
an anomaly score: flows that do not conform to the learned normal manifold
produce larger reconstruction errors.

Why train only on normal traffic?
- Unsupervised anomaly detection assumes the model captures the distribution
  of normal behavior. Including attack samples during training would cause the
  model to partially reconstruct anomalies, reducing separability between
  normal and anomalous traffic.

Why reconstruction error as anomaly score?
- The autoencoder optimizes to minimize reconstruction error on normal data.
  Samples far from the normal manifold (i.e., potential anomalies) yield
  higher reconstruction error. Thus the error can be used as a continuous
  anomaly score for thresholding.

TODO(Stage 4): Integrate this model into the realtime inference pipeline.
"""
from __future__ import annotations

from typing import Tuple

import numpy as np

try:
    import tensorflow as tf
    from tensorflow.keras import Model
    from tensorflow.keras import layers
except Exception as exc:  # pragma: no cover - import-time check
    raise ImportError(
        "TensorFlow is required to use the autoencoder module. Install tensorflow>=2.x."
    ) from exc


def _encoder_block(x: "tf.Tensor", units: int) -> "tf.Tensor":
    x = layers.Dense(units, activation="relu")(x)
    return x


def _decoder_block(x: "tf.Tensor", units: int) -> "tf.Tensor":
    x = layers.Dense(units, activation="relu")(x)
    return x


def build_autoencoder(input_dim: int) -> "Model":
    """Build a symmetric dense autoencoder.

    Parameters
    ----------
    input_dim : int
        Dimensionality of the preprocessed feature vector. Must be obtained
        from the fitted preprocessing pipeline (do not hardcode).

    Returns
    -------
    keras.Model
        Compiled autoencoder model with linear output layer.
    """
    inputs = layers.Input(shape=(input_dim,), name="input")

    # Encoder: progressively reduce dimensionality (heuristic widths)
    # Use max() to ensure widths remain >= 1 even for small input_dim values
    e1 = _encoder_block(inputs, max(input_dim // 2, 1))
    e2 = _encoder_block(e1, max(input_dim // 4, 1))
    e3 = _encoder_block(e2, max(input_dim // 8, 1))

    # Decoder: symmetric expansion back to input size
    d2 = _decoder_block(e3, max(input_dim // 4, 1))
    d1 = _decoder_block(d2, max(input_dim // 2, 1))

    outputs = layers.Dense(input_dim, activation=None, name="reconstruction")(d1)

    model = Model(inputs=inputs, outputs=outputs, name="dense_autoencoder")
    return model


def reconstruction_error(x: np.ndarray, x_hat: np.ndarray) -> np.ndarray:
    """Compute per-sample mean squared reconstruction error.

    Parameters
    ----------
    x : np.ndarray
        Original input samples (n_samples, n_features).
    x_hat : np.ndarray
        Reconstructed samples from the autoencoder (n_samples, n_features).

    Returns
    -------
    np.ndarray
        Array of shape (n_samples,) with per-sample MSE reconstruction error.
    """
    x = np.asarray(x)
    x_hat = np.asarray(x_hat)
    if x.shape != x_hat.shape:
        raise ValueError(
            f"Shape mismatch: x{x.shape} vs x_hat{x_hat.shape}. Ensure model outputs match input dimension."
        )
    err = np.mean((x - x_hat) ** 2, axis=1)
    return err
