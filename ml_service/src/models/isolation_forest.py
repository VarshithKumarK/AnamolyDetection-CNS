"""Isolation Forest wrapper for UNSW-NB15 feature vectors (Stage 3).

Isolation Forest (IF) is well-suited for tabular flow data because it detects
anomalies by randomly partitioning feature space; points that are easier to
isolate (requiring fewer splits) are considered more anomalous. This approach
is model-free with respect to underlying distributions and scales to high-
-dimensional sparse representations resulting from one-hot encoding.

Unsupervised nature:
- IF does not require labels during training. It learns isolation paths from
  the data itself, making it appropriate when only normal traffic is used for
  fitting and when labels are unreliable or unavailable.

TODO(Stage 4): Use the trained IF model to score realtime flows after
preprocessing.
"""
from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.ensemble import IsolationForest


def train_iforest(X: np.ndarray) -> IsolationForest:
    """Train Isolation Forest on preprocessed feature vectors.

    Parameters
    ----------
    X : np.ndarray
        Preprocessed feature matrix of shape (n_samples, n_features). Should be
        dense; convert from sparse if necessary before calling.

    Returns
    -------
    IsolationForest
        Fitted IsolationForest instance.
    """
    model = IsolationForest(
        n_estimators=200,
        contamination="auto",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X)
    return model


def anomaly_score(model: IsolationForest, X: np.ndarray) -> np.ndarray:
    """Compute anomaly scores using a fitted Isolation Forest.

    Higher scores indicate greater anomalousness.

    Parameters
    ----------
    model : IsolationForest
        Fitted model.
    X : np.ndarray
        Feature matrix to score.

    Returns
    -------
    np.ndarray
        Anomaly scores where larger values imply more anomalous samples. This
        is implemented as the negative of the decision_function, since
        sklearn's decision_function yields higher values for more normal points.
    """
    scores = -model.decision_function(X)
    return scores
