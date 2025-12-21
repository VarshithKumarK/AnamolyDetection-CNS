"""Runner script to fit the Stage 2 preprocessing pipeline on normal traffic.

This script loads the UNSW-NB15 training set, selects the finalized features,
fits the preprocessing pipeline ONLY on normal (label == 0) traffic, and saves
the fitted transformer to disk for later stages.

Execution:
    python src/preprocessing/run_preprocessing.py

Notes:
- No ML models are created here. This prepares feature transformations only.
- TODO(Stage 3): Load the saved preprocessor in model training and realtime
  inference pipelines.
"""
from __future__ import annotations

import os
import pickle
import sys
from typing import Tuple

import pandas as pd

# Ensure project root is on sys.path for absolute imports when running as a script
THIS_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, os.pardir, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.preprocessing.preprocessor import (  # type: ignore E402
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    EXCLUDED_FEATURES,
    build_preprocessor,
)

TRAIN_CSV = os.path.join("data", "UNSW_NB15_training-set.csv")
OUTPUT_PICKLE = os.path.join("src", "preprocessing", "preprocessor.pkl")


def _select_feature_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Return a view with only the finalized feature columns.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe containing UNSW-NB15 columns.

    Returns
    -------
    pd.DataFrame
        Dataframe with only numeric + categorical features retained.
    """
    wanted = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    return df[wanted]


def _log(msg: str) -> None:
    print(f"[preprocessing] {msg}")


def main() -> Tuple[int, int]:
    # Load dataset
    if not os.path.exists(TRAIN_CSV):
        raise FileNotFoundError(f"Training CSV not found at: {TRAIN_CSV}")

    df = pd.read_csv(TRAIN_CSV)

    # Validate required columns exist
    required = set(NUMERIC_FEATURES + CATEGORICAL_FEATURES + ["label"]) | set(
        EXCLUDED_FEATURES
    )
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Separate normal traffic
    normal_df = df.loc[df["label"] == 0]
    _log(f"Normal samples: {len(normal_df):,}")

    # Select features
    X_normal = _select_feature_columns(normal_df)

    # Build and fit preprocessor (ONLY on normal traffic)
    preprocessor = build_preprocessor()
    preprocessor.fit(X_normal)

    # Determine output dimension
    try:
        n_features_out = preprocessor.get_feature_names_out().shape[0]  # type: ignore[attr-defined]
    except Exception:
        # Fallback: transform a single row to infer dimensionality
        sample = X_normal.iloc[[0]] if not X_normal.empty else _select_feature_columns(df.iloc[[0]])
        n_features_out = preprocessor.transform(sample).shape[1]

    _log(f"Final feature vector dimension: {n_features_out}")

    # Persist fitted preprocessor
    with open(OUTPUT_PICKLE, "wb") as f:
        pickle.dump(preprocessor, f)
    _log(f"Saved fitted preprocessor to: {OUTPUT_PICKLE}")

    return len(normal_df), int(n_features_out)


if __name__ == "__main__":
    main()
