# Offline Evaluation

Purpose:
- Validate trained models on the UNSW-NB15 test dataset without any retraining or realtime logic.
- Provide quantitative and visual evidence that anomaly scores separate normal and attack traffic.

Difference vs. Realtime Inference:
- Evaluation uses labels only to separate normal vs. attack for analysis; labels are NEVER used during realtime inference.
- Realtime inference operates on individual flows and emits a decision immediately; evaluation processes a static dataset offline.

Process:
- Load the fitted preprocessor and trained models from disk (no refitting, no training).
- Compute autoencoder (AE) reconstruction errors and Isolation Forest (IF) anomaly scores.
- Summarize distributions and calculate how many attack samples exceed a normal-based percentile threshold.

Mandatory Step:
- This step is mandatory before realtime deployment to ensure the pipeline behaves as expected on held-out data.

Reproducibility:
- Scripts avoid random retraining and reuse persisted artifacts.
- No hyperparameter tuning is performed during evaluation.
