"""Batch inference runner for UNSW-NB15 (Stage 4 testing).

Loads the fitted preprocessor and trained models, runs realtime scoring on a
small batch from the testing set, and prints the number of anomalies detected.

Execution:
    python src/realtime_service/run_inference.py

Notes:
- No training, capture, or dashboards here. Backend-friendly batch check only.
"""
from __future__ import annotations

import os
import sys
from typing import Tuple

import pandas as pd

# Ensure project root is on sys.path for absolute imports when running as a script
THIS_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, os.pardir, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.realtime_service.inference import score_flow  # type: ignore E402
from src.preprocessing.preprocessor import NUMERIC_FEATURES, CATEGORICAL_FEATURES  # type: ignore E402

TEST_CSV = os.path.join("data", "UNSW_NB15_testing-set.csv")


def _log(msg: str) -> None:
    print(f"[realtime] {msg}")


def main(batch_size: int = 256) -> Tuple[int, int]:
    if not os.path.exists(TEST_CSV):
        raise FileNotFoundError(f"Testing CSV not found at: {TEST_CSV}")

    df = pd.read_csv(TEST_CSV)

    # Select only the necessary columns plus label (label not used in scoring, only for optional analysis)
    cols = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    batch_df = df.head(batch_size)

    anomalies = 0
    for _, row in batch_df.iterrows():
        result = score_flow(row)
        if result.get("is_anomaly", False):
            anomalies += 1

    _log(f"Batch size: {len(batch_df)} | Anomalies detected: {anomalies}")
    return len(batch_df), anomalies


if __name__ == "__main__":
    main()
