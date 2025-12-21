"""Preprocessing utilities for UNSW-NB15 feature extraction (Stage 2).

This module defines the finalized feature schema and exposes a factory
function to build a scikit-learn ColumnTransformer that standardizes
numeric features and one-hot encodes categorical features.

Important operational notes:
- Preprocessing is fit only on normal (benign) traffic because subsequent
  unsupervised anomaly detection models are trained to learn the distribution
  of normal behavior. Fitting scalers/encoders on attack data can leak
  information about anomalies into the preprocessing statistics and distort
  model assumptions, leading to degraded detection performance.
- OneHotEncoder is configured with handle_unknown="ignore" to support
  realtime inference. In live networks, previously unseen protocol/service/
  state categories can appear. Without handle_unknown, inference would raise
  errors when encountering new categories. With it, such categories map to
  all-zero vectors, allowing the pipeline to continue processing safely.

TODO(Stage 3): Connect this preprocessor to the anomaly detection training
pipeline and realtime service.
"""

from typing import List

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Finalized feature lists for UNSW-NB15
NUMERIC_FEATURES: List[str] = [
    "dur",
    "spkts",
    "dpkts",
    "sbytes",
    "dbytes",
    "rate",
    "sttl",
    "dttl",
    "sload",
    "dload",
    "sinpkt",
    "dinpkt",
    "sjit",
    "djit",
]

CATEGORICAL_FEATURES: List[str] = [
    "proto",
    "service",
    "state",
]

# Explicit exclusions: id, label, attack_cat
EXCLUDED_FEATURES: List[str] = ["id", "label", "attack_cat"]


def build_preprocessor() -> ColumnTransformer:
    """Build the preprocessing ColumnTransformer.

    Returns
    -------
    ColumnTransformer
        A ColumnTransformer that standard-scales numeric features and one-hot
        encodes categorical features. Unknown categories are ignored during
        transform to ensure robust realtime inference.

    Notes
    -----
    - This transformer must be fit ONLY on normal (label == 0) traffic prior
      to model training. See module docstring for rationale.
    - The returned transformer performs no imputation. Upstream data loading
      should ensure the required columns exist and contain valid values.
    """

    numeric_transformer = StandardScaler(with_mean=True, with_std=True)

    # Handle scikit-learn API differences across versions:
    # - sklearn >= 1.2 uses `sparse_output`
    # - older versions use `sparse`
    try:
        categorical_transformer = OneHotEncoder(
            handle_unknown="ignore",
            sparse_output=True,  # sparse for efficiency; downstream models should support sparse
        )
    except TypeError:
        categorical_transformer = OneHotEncoder(
            handle_unknown="ignore",
            sparse=True,
        )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
        sparse_threshold=1.0,  # keep sparse when possible
        n_jobs=None,
    )

    return preprocessor
