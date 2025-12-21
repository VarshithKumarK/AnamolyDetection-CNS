# Pipeline Trace Explanation (Academic Demonstration)

This document explains each stage of the realtime anomaly detection pipeline used in the project
"Realtime Network Anomaly Detection using Unsupervised Learning" and what to expect when tracing flows.

Important: No labels are used during realtime inference.

## 1) Raw Flow
- What happens:
  - A single network flow record (row) is provided with numeric and categorical fields (e.g., duration, packet counts, proto, service, state).
- Why it exists:
  - The system operates at the flow level (similar to NetFlow/IPFIX), which is a compact summary suitable for realtime detection.
- What an anomaly looks like:
  - Raw values may be extreme (very large bytes/packets) or rare combinations (unusual protocol/service/state), but raw values alone are not standardized.

## 2) Preprocessing
- What happens:
  - Numeric features are standardized (zero-mean, unit-variance) using statistics fit on normal traffic only.
  - Categorical features are one-hot encoded, ignoring unknown categories at inference time.
- Why it exists:
  - Standardization enables distance- or reconstruction-based models to behave well.
  - One-hot encoding converts categorical fields into a machine-readable vector.
- What an anomaly looks like:
  - Values far from the normal distribution scale to larger z-scores.
  - Previously unseen categories appear as all-zero columns (due to handle_unknown="ignore"), which can still be informative when combined with other features.

## 3) Autoencoder (Unsupervised)
- What happens:
  - The dense autoencoder reconstructs the input vector and we compute the mean squared reconstruction error.
- Why it exists:
  - Trained only on normal data, it captures common patterns of benign traffic.
- What an anomaly looks like:
  - Anomalous flows reconstruct poorly, leading to higher reconstruction error used as an anomaly score.

## 4) Isolation Forest (Unsupervised)
- What happens:
  - Isolation Forest assigns an anomaly score based on how easily a sample is isolated via random splits.
- Why it exists:
  - It complements the autoencoder with a tree-based, distribution-free perspective well-suited for tabular data.
- What an anomaly looks like:
  - Points that are isolated with fewer splits have higher anomaly scores.

## 5) Final Decision
- What happens:
  - Scores from the autoencoder and Isolation Forest are combined (weighted sum) and compared to a threshold.
- Why it exists:
  - Combining complementary models often yields more robust detection.
- What an anomaly looks like:
  - Combined score exceeds the threshold, and the label is ANOMALY.

Notes:
- Thresholds should be calibrated using normal traffic statistics (see Stage 3 threshold analysis).
- The tracing utilities print each stage as structured JSON for clarity and reproducibility.
- No labels are used during realtime inference.
