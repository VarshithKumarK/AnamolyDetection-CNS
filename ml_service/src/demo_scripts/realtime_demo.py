"""Realtime flow ingestion demo (Stage 5).

Continuously reads network flow records from a CSV file to simulate realtime
streaming, scores each flow using the trained anomaly detection pipeline,
and prints results to stdout.

Usage:
    python src/demo_scripts/realtime_demo.py [path/to/flow_csv]

Defaults:
    If no CSV path is provided, uses: src/demo_scripts/sample_flow_stream.csv

Notes:
- This is an offline demo that does not capture live packets. It replays CSV
  rows with a small delay to mimic realtime ingestion.
- Do not use this script to perform any network attacks. It is demo-only.
- TODO: In a production setup, replace the CSV reader with a streaming source
  (e.g., message queue, socket listener), and connect a PCAP-to-flow pipeline
  upstream.
"""
from __future__ import annotations

import csv
import os
import sys
import time
from typing import Iterable, Mapping

import pandas as pd

# Ensure project root is on sys.path for absolute imports when running as a script
THIS_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, os.pardir, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.realtime_service.inference import score_flow  # type: ignore E402
from src.preprocessing.preprocessor import (  # type: ignore E402
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
)

DEFAULT_STREAM = os.path.join("src", "demo_scripts", "sample_flow_stream.csv")
SLEEP_SECONDS = float(os.getenv("FLOW_SLEEP_SECONDS", "0.25"))


def _iter_rows(csv_path: str) -> Iterable[Mapping[str, str]]:
    with open(csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def _filter_required_columns(row: Mapping[str, str]) -> dict:
    # Keep only the columns expected by the preprocessor; ignore extras if any
    cols = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    out = {}
    for c in cols:
        if c in row:
            out[c] = row[c]
    # Convert numeric fields from strings to floats
    for c in NUMERIC_FEATURES:
        if c in out:
            try:
                out[c] = float(out[c])
            except Exception:
                out[c] = 0.0
    return out


def main(csv_path: str | None = None) -> None:
    path = csv_path or DEFAULT_STREAM
    if not os.path.exists(path):
        raise FileNotFoundError(f"Flow CSV not found: {path}")

    print(f"[demo] Starting realtime scoring demo. Source: {path}")
    print("[demo] Press Ctrl+C to stop.")

    try:
        for idx, row in enumerate(_iter_rows(path), start=1):
            features = _filter_required_columns(row)
            result = score_flow(features)
            status = "ANOMALY" if result["is_anomaly"] else "NORMAL"
            print(
                f"[demo] #{idx:06d} | score={result['score']:.6f} | "
                f"AE={result['details']['ae']:.6f} IF={result['details']['iforest']:.6f} | {status}"
            )
            time.sleep(SLEEP_SECONDS)
    except KeyboardInterrupt:
        print("\n[demo] Stopped by user.")


if __name__ == "__main__":
    user_path = sys.argv[1] if len(sys.argv) > 1 else None
    main(user_path)
