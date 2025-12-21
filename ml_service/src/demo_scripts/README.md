# Realtime CSV Trace Demo (Explainable)

Run a step-by-step realtime trace over flow records using the frozen inference pipeline.

## How to run

- Default sample:
```
python src/demo_scripts/realtime_trace_csv.py
```
- Custom CSV path:
```
python src/demo_scripts/realtime_trace_csv.py path/to/your_flow_stream.csv
```
- Optional pacing:
```
TRACE_SLEEP_SECONDS=0.3 python src/demo_scripts/realtime_trace_csv.py
```

## What each printed stage means

- `raw_flow`:
  - Selected raw feature values for the current flow (e.g., dur, sbytes, dbytes, spkts, dpkts, proto, service, state).
- `preprocessing`:
  - Shapes of the numeric-scaled block, categorical one-hot block, and final vector after the fitted preprocessor.
- `autoencoder`:
  - Reconstruction error for the flow (higher implies more anomalous under the reconstruction model).
- `isolation_forest`:
  - Isolation-based anomaly score (higher implies more anomalous under the tree model).
- `final_decision`:
  - Combined score (from frozen inference pipeline), the frozen threshold, and NORMAL/ANOMALY label.

## Why CSV replay is valid for realtime testing

- The system operates on flow features (not raw packets). UNSW-NB15 already provides flows, so replaying CSV rows faithfully simulates a telemetry stream.
- It is deterministic, reproducible, and works fully offline without network access.

## Extending conceptually to PCAP replay

- PCAP packets can be replayed in a lab using `tcpreplay` into a test interface.
- A flow extractor (e.g., NetFlow/IPFIX collector or custom tool) aggregates packets into flow records with the required fields.
- These flow records are then passed to the same `score_flow()` function; the tracing output remains unchanged. See `realtime_trace_pcap.py` for a placeholder.
