# predict.py
"""
Prediction utilities:
 - loads scaler, autoencoder (.keras), encoder (.keras), IF models (raw and latent) and AE threshold
 - exposes predict_df(df) which returns per-row iso_label/ae_label and scores
"""

import os
import joblib
import json
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model

SCALER_PATH = "models/scaler.pkl"
ISO_RAW_PATH = "models/iso_model_raw.pkl"
ISO_LATENT_PATH = "models/iso_model_latent.pkl"
AE_PATH = "models/autoencoder_model.keras"
ENC_PATH = "models/encoder.keras"
THRESH_PATH = "models/ae_threshold.json"
FEATURES_PATH = "models/feature_columns.json"  # produced by preprocess.py

# load artifacts
if not os.path.exists(SCALER_PATH):
    raise FileNotFoundError(f"Missing scaler at {SCALER_PATH}. Run train.py first.")

scaler = joblib.load(SCALER_PATH)
iso_raw = joblib.load(ISO_RAW_PATH)
iso_latent = joblib.load(ISO_LATENT_PATH)
# load Keras models with compile=False to avoid deserialization issues
ae_model = load_model(AE_PATH, compile=False)
encoder = load_model(ENC_PATH, compile=False)
with open(THRESH_PATH, "r") as f:
    threshold = json.load(f)["threshold"]
with open(FEATURES_PATH, "r") as f:
    feature_columns = json.load(f)

def _prepare_input_df(df: pd.DataFrame):
    # Keep numeric columns
    df_num = df.select_dtypes(include=[np.number]).copy()
    # Ensure all feature_columns exist (add missing as 0.0) and reorder
    df_num = df_num.reindex(columns=feature_columns, fill_value=0.0)
    df_num = df_num.fillna(df_num.mean())
    return df_num

def predict_df(df: pd.DataFrame):
    """
    Input: pandas DataFrame (raw columns)
    Output: dict with results list {index, iso_raw_label, iso_raw_score, iso_latent_label, iso_latent_score, ae_label, ae_score}
    Labels: 1 -> anomaly, 0 -> normal
    """
    df_num = _prepare_input_df(df)
    X = scaler.transform(df_num.values.astype(float))

    # IsolationForest on raw features
    iso_raw_scores = iso_raw.decision_function(X).tolist()
    iso_raw_labels = (iso_raw.predict(X) == -1).astype(int).tolist()

    # AE recon errors
    recon = ae_model.predict(X)
    ae_errors = np.mean(np.abs(recon - X), axis=1)
    ae_labels = (ae_errors > threshold).astype(int).tolist()

    # IF on latent
    Z = encoder.predict(X)
    iso_lat_scores = iso_latent.decision_function(Z).tolist()
    iso_lat_labels = (iso_latent.predict(Z) == -1).astype(int).tolist()

    results = []
    for i in range(len(df_num)):
        results.append({
            "index": int(i),
            "iso_raw_label": int(iso_raw_labels[i]),
            "iso_raw_score": float(iso_raw_scores[i]),
            "iso_latent_label": int(iso_lat_labels[i]),
            "iso_latent_score": float(iso_lat_scores[i]),
            "ae_label": int(ae_labels[i]),
            "ae_score": float(ae_errors[i])
        })
    return {"results": results}
