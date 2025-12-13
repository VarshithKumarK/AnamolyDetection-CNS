# preprocess.py
"""
Preprocessing utilities for UNSW-NB15 dataset.
Saves feature_columns list and scaler to models/.
"""

import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib
import json

TRAIN_PATH = "data/UNSW_NB15_training-set.csv"
TEST_PATH = "data/UNSW_NB15_testing-set.csv"
SCALER_PATH = "models/scaler.pkl"
FEATURES_PATH = "models/feature_columns.json"


def _detect_label_col(df: pd.DataFrame):
    for col in ["label", " Label", "attack_cat", "attack", "class"]:
        if col in df.columns:
            return col
    return None


def load_raw_dfs(train_path: str = TRAIN_PATH, test_path: str = TEST_PATH):
    print(f"Loading training data from: {train_path}")
    df_train = pd.read_csv(train_path)
    print(f"Loading testing data from: {test_path}")
    df_test = pd.read_csv(test_path)
    return df_train, df_test


def select_features(df: pd.DataFrame):
    df = df.copy()
    label_col = _detect_label_col(df)
    if label_col is not None:
        df_no_label = df.drop(columns=[label_col])
    else:
        df_no_label = df

    # Select numeric columns
    numeric_df = df_no_label.select_dtypes(include=[np.number]).copy()

    # Select specific categorical columns to include
    cat_cols = ["proto", "service", "state"]
    cat_df = pd.DataFrame()
    for c in cat_cols:
        if c in df_no_label.columns:
            # One-hot encode
            dummies = pd.get_dummies(df_no_label[c], prefix=c)
            cat_df = pd.concat([cat_df, dummies], axis=1)

    # Combine
    combined = pd.concat([numeric_df, cat_df], axis=1)

    # Drop columns with very few non-null values if needed,
    # but for OHE usually we keep them or filter rare categories.
    # Here we stick to numeric filtering logic for numeric fields?
    # Actually, let's just do a fillna for numeric and return combined.
    # The previous logic dropped columns with < 30% valid data.
    # Let's simple apply fillna(0) for safety on combined.
    combined = combined.fillna(0)

    return combined


def preprocess_split(
    df: pd.DataFrame,
    feature_columns=None,
    scaler: StandardScaler = None,
    fit_scaler: bool = False,
):
    df_proc = select_features(df)
    # if feature_columns provided, reindex to that order, filling missing cols with zeros
    if feature_columns is not None:
        for c in feature_columns:
            if c not in df_proc.columns:
                df_proc[c] = 0.0
        df_proc = df_proc.reindex(columns=feature_columns)

    X = df_proc.values.astype(float)
    # detect y label (if exists)
    label_col = _detect_label_col(df)
    y = None
    if label_col is not None:
        raw = df[label_col]
        if raw.dtype == object:
            y = (raw.str.lower() != "normal").astype(int).values
        else:
            try:
                y = (raw != 0).astype(int).values
            except Exception:
                y = raw.values

    if fit_scaler:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        os.makedirs("models", exist_ok=True)
        joblib.dump(scaler, SCALER_PATH)
        # save feature columns order
        feature_cols = list(df_proc.columns)
        with open(FEATURES_PATH, "w") as f:
            json.dump(feature_cols, f)
        return X_scaled, y, scaler, feature_cols
    else:
        if scaler is None:
            raise ValueError("scaler must be provided if fit_scaler=False")
        X_scaled = scaler.transform(X)
        return X_scaled, y


def prepare_train_test(train_path: str = TRAIN_PATH, test_path: str = TEST_PATH):
    df_train, df_test = load_raw_dfs(train_path, test_path)
    X_train, y_train, scaler, feature_cols = preprocess_split(df_train, fit_scaler=True)
    X_test, y_test = preprocess_split(
        df_test, feature_columns=feature_cols, scaler=scaler, fit_scaler=False
    )
    return X_train, y_train, X_test, y_test, scaler, feature_cols


if __name__ == "__main__":
    X_train, y_train, X_test, y_test, scaler, feature_cols = prepare_train_test()
    print("Shapes:")
    print("X_train:", X_train.shape)
    print("y_train:", None if y_train is None else y_train.shape)
    print("X_test :", X_test.shape)
    print("y_test :", None if y_test is None else y_test.shape)
    print("Scaler saved to:", SCALER_PATH)
    print("Feature columns saved to: models/feature_columns.json")
