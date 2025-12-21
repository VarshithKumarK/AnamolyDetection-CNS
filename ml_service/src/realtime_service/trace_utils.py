"""Tracing utilities that wrap realtime inference for educational demos (Stage 6).

Provides a backend-agnostic function `trace_flow` that explains each step in the
pipeline for a single flow: raw input -> preprocessing -> model scores -> final
decision. This module does not modify models or retrain anything; it reuses the
existing artifacts and inference logic.

No labels are used during realtime inference.
"""
from __future__ import annotations

import os
import pickle
from typing import Dict, List, Mapping, Union

import numpy as np
import pandas as pd

from src.preprocessing.preprocessor import CATEGORICAL_FEATURES, NUMERIC_FEATURES
from src.realtime_service.inference import (
    AE_WEIGHT,
    IFOREST_WEIGHT,
    REALTIME_SCORE_THRESHOLD,
    score_flow,
)

# Paths must mirror inference module to ensure consistent artifacts
PREPROCESSOR_PKL = os.path.join("src", "preprocessing", "preprocessor.pkl")

# Module-local cache for the preprocessor so we can inspect sub-transformers
_PREPROCESSOR = None


def _load_preprocessor():
    global _PREPROCESSOR
    if _PREPROCESSOR is None:
        with open(PREPROCESSOR_PKL, "rb") as f:
            _PREPROCESSOR = pickle.load(f)


def _to_dataframe(flow: Union[Mapping[str, object], pd.Series, pd.DataFrame]) -> pd.DataFrame:
    if isinstance(flow, pd.DataFrame):
        if len(flow) != 1:
            raise ValueError("trace_flow expects a single-row DataFrame")
        return flow
    if isinstance(flow, pd.Series):
        return flow.to_frame().T
    if isinstance(flow, Mapping):
        return pd.DataFrame([flow])
    raise TypeError("flow must be dict, Series, or single-row DataFrame")


def _sanitize_types(df: pd.DataFrame) -> pd.DataFrame:
    # Ensure numeric columns are floats; keep categorical as is
    for c in NUMERIC_FEATURES:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def _preprocess_shapes(row_df: pd.DataFrame) -> Dict[str, tuple]:
    """Compute shapes of numeric-scaled, categorical-encoded, and final vector."""
    cols_num = [c for c in NUMERIC_FEATURES if c in row_df.columns]
    cols_cat = [c for c in CATEGORICAL_FEATURES if c in row_df.columns]

    num_t = _PREPROCESSOR.named_transformers_["num"]
    cat_t = _PREPROCESSOR.named_transformers_["cat"]

    # Transform subsets separately to inspect shapes
    Xn = num_t.transform(row_df[cols_num])
    Xc = cat_t.transform(row_df[cols_cat])

    n_shape = getattr(Xn, "shape", (1, len(cols_num)))
    c_shape = getattr(Xc, "shape", (1, 0))

    # Final vector via full preprocessor
    X = _PREPROCESSOR.transform(row_df[cols_num + cols_cat])
    f_shape = X.shape

    return {
        "numeric_scaled_shape": (int(n_shape[0]), int(n_shape[1])),
        "categorical_encoded_shape": (int(c_shape[0]), int(c_shape[1])),
        "final_vector_shape": (int(f_shape[0]), int(f_shape[1])),
    }


def trace_flow(flow_df: Union[Mapping[str, object], pd.Series, pd.DataFrame]) -> List[Dict[str, object]]:
    """Trace a single flow through the pipeline and return structured steps.

    Steps returned (in order):
    - raw_flow: original feature values used by the pipeline
    - preprocessing: shapes of transformed numeric/categorical blocks and final vector
    - autoencoder: reconstruction error
    - isolation_forest: anomaly score (higher means more anomalous)
    - final_decision: combined score, threshold, and label (NORMAL/ANOMALY)

    No labels are used during realtime inference.
    """
    _load_preprocessor()

    df = _to_dataframe(flow_df)
    df = _sanitize_types(df)

    # Keep only relevant columns for display and processing
    show_cols = [c for c in (NUMERIC_FEATURES + CATEGORICAL_FEATURES) if c in df.columns]
    raw_dict = {c: (None if pd.isna(df.iloc[0][c]) else df.iloc[0][c]) for c in show_cols}

    # Preprocessing shapes
    shapes = _preprocess_shapes(df[show_cols])

    # Reuse production scoring to ensure identical logic for scores and decision
    scored = score_flow(df[show_cols])

    ae = float(scored["details"]["ae"])  # reconstruction error
    ifs = float(scored["details"]["iforest"])  # isolation forest score
    combined = float(scored["score"])  # weighted sum via inference module

    label = "ANOMALY" if scored["is_anomaly"] else "NORMAL"

    trace = [
        {"step": "raw_flow", "data": raw_dict},
        {"step": "preprocessing", **shapes},
        {"step": "autoencoder", "reconstruction_error": ae},
        {"step": "isolation_forest", "anomaly_score": ifs},
        {
            "step": "final_decision",
            "combined_score": combined,
            "threshold": float(REALTIME_SCORE_THRESHOLD),
            "label": label,
            "weights": {"autoencoder": float(AE_WEIGHT), "isolation_forest": float(IFOREST_WEIGHT)},
        },
    ]
    return trace
