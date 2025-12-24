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
from src.preprocessing.features import add_derived_features


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

    # -------------------------------------------------------------
    # Step 0: Calculate Derived Features (Traffic/Crypto signatures)
    # -------------------------------------------------------------
    # These are added to the DF but NOT used by the current frozen model
    # (because the preprocessor drops unknowns).
    # We add them here so we can return them for the Frontend display.
    df_enhanced = add_derived_features(df)

    results: List[Dict[str, Any]] = []

    # Iterate row-by-row (backend-safe, deterministic)
    for idx, row in df_enhanced.iterrows():
        # -------------------------------------------------------------
        # Keep only expected columns (ignore extras safely)
        # -------------------------------------------------------------
        flow = {}
        # We need the original features for the model
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

        # -------------------------------------------------------------
        # Extract Network Context for Frontend Display
        # -------------------------------------------------------------
        network_context = {
            # Raw Attributes (Context)
            "proto": row.get("proto", "unknown"),
            "service": row.get("service", "unknown"),
            "state": row.get("state", "unknown"),
            # Volume / Size
            "total_bytes": float(row.get("sbytes", 0) + row.get("dbytes", 0)),
            "duration": float(row.get("dur", 0)),
            # Derived Security Metrics
            "traffic_asymmetry": float(row.get("traffic_asymmetry", 0)),
            "packet_density": float(row.get("packet_density", 0)),
            "payload_fullness": float(row.get("payload_fullness", 0)),
            "heuristic_analysis": "Encrypted"
            if float(row.get("payload_fullness", 0)) > 1000
            else "Cleartext",
        }

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
                # NEW: Network Context for UI
                "network_context": network_context,
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
                "smeansz": 1400,
                "dmeansz": 1400,
            }
        ]
    )

    print(predict_df(sample))
