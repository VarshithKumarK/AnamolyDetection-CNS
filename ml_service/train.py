# train.py
"""
Improved training script:
 - trains Autoencoder and saves in native Keras format (.keras)
 - selects AE threshold by maximizing F1 on a validation set (or test set if no val)
 - builds and saves encoder
 - trains IsolationForest on raw features and on AE latent space
 - performs grid-search over contamination for IF (if labels available)
 - saves models and metadata to models/
"""

import os
import json
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, precision_recall_curve, f1_score
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras import regularizers
from tensorflow.keras.models import load_model

from preprocess import prepare_train_test

os.makedirs("models", exist_ok=True)


def build_autoencoder(input_dim):
    # Deeper and wider autoencoder with Dropout
    inp = Input(shape=(input_dim,), name="ae_input")

    # Encoder
    x = Dense(256, activation="relu", name="enc_1")(inp)
    x = Dropout(0.2)(x)
    x = Dense(128, activation="relu", name="enc_2")(x)
    x = Dropout(0.2)(x)
    x = Dense(64, activation="relu", name="enc_3")(x)

    latent = Dense(32, activation="relu", name="latent")(x)

    # Decoder
    x = Dense(64, activation="relu", name="dec_1")(latent)
    x = Dropout(0.2)(x)
    x = Dense(128, activation="relu", name="dec_2")(x)
    x = Dropout(0.2)(x)
    x = Dense(256, activation="relu", name="dec_3")(x)

    out = Dense(input_dim, activation="linear", name="reconstruction")(x)

    autoencoder = Model(inputs=inp, outputs=out, name="autoencoder")
    autoencoder.compile(optimizer="adam", loss="mse")
    return autoencoder


def select_threshold_by_f1(errors, y_true):
    """
    Given reconstruction errors and binary ground-truth (0 normal, 1 anomaly),
    pick threshold that maximizes F1 on provided set.
    Returns best_threshold, best_f1.
    """
    precision, recall, thresholds = precision_recall_curve(y_true, errors)
    # thresholds length = len(precision)-1, align carefully
    f1_scores = (
        2 * (precision[:-1] * recall[:-1]) / (precision[:-1] + recall[:-1] + 1e-12)
    )
    if len(f1_scores) == 0:
        # fallback if PR curve failed
        return float(np.percentile(errors, 95)), 0.0
    best_idx = np.nanargmax(f1_scores)
    best_thr = thresholds[best_idx]
    best_f1 = float(f1_scores[best_idx])
    return float(best_thr), best_f1


def grid_search_if(
    X_train,
    X_val,
    y_val,
    contamination_list=[0.01, 0.03, 0.05, 0.1],
    n_estimators_list=[100, 200],
):
    """
    Simple grid search for IsolationForest contamination parameter using F1 on validation set.
    Returns best_model, best_params
    """
    best = (None, -1.0, None)  # (model, f1, params)
    for cont in contamination_list:
        for n_est in n_estimators_list:
            model = IsolationForest(
                n_estimators=n_est, contamination=cont, random_state=42, n_jobs=-1
            )
            model.fit(X_train)
            preds = (model.predict(X_val) == -1).astype(int)
            f1 = f1_score(y_val, preds)
            print(f"IF params cont={cont}, n_estimators={n_est} => f1={f1:.4f}")
            if f1 > best[1]:
                best = (model, f1, {"contamination": cont, "n_estimators": n_est})
    print("Best IF params:", best[2], "best f1:", best[1])
    return best


def train_and_save():
    print("Preparing data (preprocess.py)...")
    X_train, y_train, X_test, y_test, scaler, feature_cols = prepare_train_test()
    print(
        "Prepared. Shapes:",
        X_train.shape,
        "y_train:",
        None if y_train is None else y_train.shape,
    )
    # create a validation set if we have labels; otherwise create a small val split without labels for threshold heuristics
    if y_train is not None:
        # stratify on y_train if possible
        X_ae_train_full = X_train  # use for IF and for AE data splitting
        X_train_main, X_val, y_train_main, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
        )
        # For AE we need normal samples only (for training AE). Identify normals in X_train_main if labels exist
        if y_train is not None:
            normal_idx = np.where(y_train_main == 0)[0]
            if len(normal_idx) > 0:
                X_ae_train = X_train_main[normal_idx]
            else:
                X_ae_train = X_train_main
    else:
        # no labels: simple train/val random split
        X_train_main, X_val = train_test_split(X_train, test_size=0.2, random_state=42)
        y_val = None
        X_ae_train = X_train_main

    print("AE training data shape:", X_ae_train.shape)

    # ===== IsolationForest on raw features =====
    print("\nTraining IsolationForest on raw features (quick default)")
    iso_raw = IsolationForest(
        n_estimators=200, contamination=0.05, random_state=42, n_jobs=-1
    )
    iso_raw.fit(X_train)
    joblib.dump(iso_raw, "models/iso_model_raw.pkl")
    print("Saved models/iso_model_raw.pkl")

    # ===== Autoencoder =====
    # ===== Autoencoder =====
    print("\nBuilding autoencoder...")
    ae = build_autoencoder(X_train.shape[1])

    # Early stopping
    es = EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True)

    ae.fit(
        X_ae_train,
        X_ae_train,
        epochs=100,
        batch_size=256,
        validation_split=0.1,
        verbose=1,
        callbacks=[es],
    )

    # Save autoencoder in native Keras format (recommended)
    ae_path = "models/autoencoder_model.keras"
    ae.save(ae_path)
    print(f"Saved autoencoder to {ae_path}")

    # Build and save encoder model explicitly (use the 'latent' layer by name)
    encoder = Model(
        inputs=ae.input, outputs=ae.get_layer("latent").output, name="encoder"
    )
    encoder.save("models/encoder.keras")
    print("Saved encoder to models/encoder.keras")

    # ===== Compute reconstruction errors on a validation set with labels to select threshold =====
    # Prefer y_val (if labels available), else try y_test, else use percentile on training normal samples
    if y_val is not None:
        # compute errors on X_val
        recon_val = ae.predict(X_val)
        errors_val = np.mean(np.abs(recon_val - X_val), axis=1)
        thr, best_f1 = select_threshold_by_f1(errors_val, y_val)
        print("Selected AE threshold from validation set by F1:", thr, "F1:", best_f1)
    elif y_test is not None:
        recon_test = ae.predict(X_test)
        errors_test = np.mean(np.abs(recon_test - X_test), axis=1)
        thr, best_f1 = select_threshold_by_f1(errors_test, y_test)
        print("Selected AE threshold from TEST set by F1:", thr, "F1:", best_f1)
    else:
        # no labels available: fallback to 95th percentile of AE reconstruction on training normals
        recon_train_ae = ae.predict(X_ae_train)
        errors_train = np.mean(np.abs(recon_train_ae - X_ae_train), axis=1)
        thr = float(np.percentile(errors_train, 95))
        best_f1 = None
        print("No labels found; using 95th percentile threshold:", thr)

    with open("models/ae_threshold.json", "w") as f:
        json.dump({"threshold": float(thr)}, f)
    print("Saved AE threshold to models/ae_threshold.json")

    # ===== Train IsolationForest on AE latent space =====
    print("\nComputing latent representation for IF (encoder)...")
    Z_train = encoder.predict(X_train)
    print("Z_train shape:", Z_train.shape)

    # If we have validation labels, use grid search on Z to find best contamination/n_estimators
    if y_val is not None:
        # need latent for validation too
        Z_val = encoder.predict(X_val)
        best_model, best_f1, best_params = grid_search_if(
            Z_train,
            Z_val,
            y_val,
            contamination_list=[0.01, 0.03, 0.05, 0.1, 0.15],
            n_estimators_list=[100, 200, 300],
        )
        # save best_model
        joblib.dump(best_model, "models/iso_model_latent.pkl")
        print(
            "Saved best latent IF to models/iso_model_latent.pkl with params:",
            best_params,
        )
    else:
        # no labels to grid-search; train default IF on latent
        iso_latent = IsolationForest(
            n_estimators=200, contamination=0.05, random_state=42, n_jobs=-1
        )
        iso_latent.fit(Z_train)
        joblib.dump(iso_latent, "models/iso_model_latent.pkl")
        print("Saved iso_model_latent.pkl (default params)")

    # Also save scaler and feature_columns metadata (preprocess should have saved scaler; save feature_cols file if returned)
    # If preprocess saved scaler and feature_columns, they should already be present; otherwise, save them
    # (The prepare_train_test from preprocess.py should have saved scaler & feature_columns.)
    print("\nTraining complete. Models saved in models/ directory.")

    # Optional: evaluate both IF models and AE on test set (if y_test available)
    if y_test is not None:
        print("\n--- Final evaluation on TEST set ---")
        # AE eval
        recon_test = ae.predict(X_test)
        errors_test = np.mean(np.abs(recon_test - X_test), axis=1)
        ae_preds = (errors_test > thr).astype(int)
        print("Autoencoder classification report:")
        print(classification_report(y_test, ae_preds, digits=4))

        # IF raw
        iso_raw = joblib.load("models/iso_model_raw.pkl")
        iso_raw_preds = (iso_raw.predict(X_test) == -1).astype(int)
        print("IsolationForest (raw features) classification report:")
        print(classification_report(y_test, iso_raw_preds, digits=4))

        # IF latent
        encoder_loaded = load_model("models/encoder.keras", compile=False)
        Z_test = encoder_loaded.predict(X_test)
        iso_lat = joblib.load("models/iso_model_latent.pkl")
        iso_lat_preds = (iso_lat.predict(Z_test) == -1).astype(int)
        print("IsolationForest (latent) classification report:")
        print(classification_report(y_test, iso_lat_preds, digits=4))


if __name__ == "__main__":
    train_and_save()
