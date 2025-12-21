"""
predict.py
-----------
Drop-in replacement ML interface for the backend.

This file preserves the original predict_df(df) API expected by the backend,
but internally uses the enhanced ML pipeline:
- Preprocessing (frozen)
- Autoencoder v2
- Isolation Forest v2
- Frozen threshold ensemble scoring

No backend or frontend changes required.
"""

from __future__ import annotations

import os
import sys
from typing import Dict, Any, List

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------
# Ensure project root is on path (important when backend runs this file)
# ---------------------------------------------------------------------
THIS_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# ---------------------------------------------------------------------
# Import YOUR ML inference logic (already tested)
# ---------------------------------------------------------------------
from src.realtime_service.inference import score_flow
from src.preprocessing.preprocessor import (
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
)

# ---------------------------------------------------------------------
# Public API — DO NOT CHANGE (backend depends on this)
# ---------------------------------------------------------------------
def predict_df(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Predict anomalies for a batch of network flows.

    Parameters
    ----------
    df : pd.DataFrame
        Raw flow-level features sent by backend.

    Returns
    -------
    dict
        JSON-serializable prediction results.
    """

    results: List[Dict[str, Any]] = []

    # Iterate row-by-row (backend-safe, deterministic)
    for idx, row in df.iterrows():
        # -------------------------------------------------------------
        # Keep only expected columns (ignore extras safely)
        # -------------------------------------------------------------
        flow = {}
        for c in NUMERIC_FEATURES + CATEGORICAL_FEATURES:
            if c in row:
                flow[c] = row[c]

        # Ensure numeric columns are floats
        for c in NUMERIC_FEATURES:
            try:
                flow[c] = float(flow.get(c, 0.0))
            except Exception:
                flow[c] = 0.0

        # -------------------------------------------------------------
        # Call YOUR realtime inference pipeline
        # -------------------------------------------------------------
        out = score_flow(flow)

        # out structure (from your pipeline):
        # {
        #   "score": float,
        #   "is_anomaly": bool,
        #   "details": {
        #       "ae": float,
        #       "iforest": float
        #   }
        # }

        # -------------------------------------------------------------
        # Adapter mapping — preserve old backend schema
        # -------------------------------------------------------------
        ae_score = float(out["details"]["ae"])
        if_score = float(out["details"]["iforest"])
        label = 1 if out["is_anomaly"] else 0

        results.append(
            {
                "index": int(idx),
                # Autoencoder output
                "ae_score": ae_score,
                "ae_label": label,

                # Isolation Forest (raw & latent mapped safely)
                "iso_raw_score": if_score,
                "iso_raw_label": label,
                "iso_latent_score": if_score,
                "iso_latent_label": label,
            }
        )

    return {"results": results}


# ---------------------------------------------------------------------
# Optional: quick local test
# ---------------------------------------------------------------------
if __name__ == "__main__":
    # Minimal sanity test
    sample = pd.DataFrame(
        [
            {
                "dur": 0.01,
                "spkts": 2000,
                "dpkts": 1800,
                "sbytes": 5_000_000,
                "dbytes": 4_500_000,
                "proto": "tcp",
                "service": "ssh",
                "state": "S0",
            }
        ]
    )

    print(predict_df(sample))
