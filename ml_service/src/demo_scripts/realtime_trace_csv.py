"""Realtime CSV trace runner (explainable, step-by-step).

Reads a CSV file row-by-row to simulate realtime flows and prints structured
JSON-like logs for each pipeline stage using the frozen inference pipeline.

Execution:
    python src/demo_scripts/realtime_trace_csv.py [optional_path_to_csv]

Notes:
- This runner does NOT retrain anything and does NOT modify inference logic.
- It uses the existing frozen threshold inside src/realtime_service/inference.
- CSV replay is acceptable for realtime testing because flows (not packets) are
  the modeling interface, and UNSW-NB15 already provides flow records.
"""
from __future__ import annotations

import csv
import json
import os
import sys
import time
from typing import Iterable, Mapping

import pandas as pd

# Ensure project root is on sys.path for absolute imports
THIS_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, os.pardir, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Import frozen inference API and constants
from src.realtime_service.inference import (  # type: ignore E402
    REALTIME_SCORE_THRESHOLD,
    score_flow,
)
from src.preprocessing.preprocessor import (  # type: ignore E402
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
)

# Load preprocessor only for shape introspection in logs (no refitting)
import pickle  # type: ignore E402
PREPROCESSOR_PKL = os.path.join("src", "preprocessing", "preprocessor.pkl")
with open(PREPROCESSOR_PKL, "rb") as _pf:  # type: ignore
    _PRE = pickle.load(_pf)

DEFAULT_STREAM = os.path.join("src", "demo_scripts", "sample_flow_stream.csv")
SLEEP_SECONDS = float(os.getenv("TRACE_SLEEP_SECONDS", "0.3"))


def _iter_rows(csv_path: str) -> Iterable[Mapping[str, str]]:
    with open(csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def _filter_required_columns(row: Mapping[str, str]) -> dict:
    # Keep only features expected by the preprocessor; ignore extras
    cols = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    out = {}
    for c in cols:
        if c in row:
            out[c] = row[c]
    # Convert numeric fields to floats; missing/invalid -> 0.0 for robustness
    for c in NUMERIC_FEATURES:
        if c in out:
            try:
                out[c] = float(out[c])
            except Exception:
                out[c] = 0.0
    return out


def _preprocess_shapes(one_row_df: pd.DataFrame) -> dict:
    """Report preprocessing shapes for numeric, categorical, and final vector."""
    cols_num = [c for c in NUMERIC_FEATURES if c in one_row_df.columns]
    cols_cat = [c for c in CATEGORICAL_FEATURES if c in one_row_df.columns]

    num_t = _PRE.named_transformers_["num"]
    cat_t = _PRE.named_transformers_["cat"]

    Xn = num_t.transform(one_row_df[cols_num])
    Xc = cat_t.transform(one_row_df[cols_cat])
    Xf = _PRE.transform(one_row_df[cols_num + cols_cat])

    n_shape = (int(Xn.shape[0]), int(Xn.shape[1]))
    c_shape = (int(Xc.shape[0]), int(Xc.shape[1]))
    f_shape = (int(Xf.shape[0]), int(Xf.shape[1]))

    return {
        "step": "preprocessing",
        "numeric_scaled_shape": n_shape,
        "categorical_encoded_shape": c_shape,
        "final_vector_shape": f_shape,
    }


def _print_block(obj: dict) -> None:
    print(json.dumps(obj, indent=2, sort_keys=True, default=str))


def main(csv_path: str | None = None) -> None:
    path = csv_path or DEFAULT_STREAM
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV not found: {path}")

    print(f"[trace] Starting realtime CSV trace. Source: {path}")
    print("[trace] Press Ctrl+C to stop. Threshold is frozen in inference.")

    try:
        for idx, row in enumerate(_iter_rows(path), start=1):
            features = _filter_required_columns(row)
            # Pretty small subset for raw display
            raw_keys = [
                "dur",
                "sbytes",
                "dbytes",
                "spkts",
                "dpkts",
                "proto",
                "service",
                "state",
            ]
            raw_view = {k: features.get(k) for k in raw_keys if k in features}
            _print_block({"step": "raw_flow", "index": idx, "data": raw_view})

            # Shapes from preprocessing
            row_df = pd.DataFrame([features])
            _print_block(_preprocess_shapes(row_df))

            # Score via frozen inference pipeline
            result = score_flow(features)
            ae_score = float(result["details"]["ae"]) if "details" in result else None
            if_score = float(result["details"]["iforest"]) if "details" in result else None
            final_score = float(result["score"]) if "score" in result else None
            decision = "ANOMALY" if result.get("is_anomaly", False) else "NORMAL"

            _print_block({"step": "autoencoder", "reconstruction_error": ae_score})
            _print_block({"step": "isolation_forest", "anomaly_score": if_score})
            _print_block(
                {
                    "step": "final_decision",
                    "combined_score": final_score,
                    "threshold": float(REALTIME_SCORE_THRESHOLD),
                    "label": decision,
                }
            )

            time.sleep(SLEEP_SECONDS)
    except KeyboardInterrupt:
        print("\n[trace] Stopped by user.")


if __name__ == "__main__":
    user_path = sys.argv[1] if len(sys.argv) > 1 else None
    main(user_path)
