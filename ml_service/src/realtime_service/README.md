Below is a **short, instructor-friendly Confluence page draft** you can paste directly.
It’s written for **clarity, reproducibility, and evaluation**, not marketing.

---

# Realtime Network Anomaly Detection – Demo Guide

## Overview

This project demonstrates **realtime anomaly detection in network traffic** using **unsupervised learning**.
The system is trained **only on normal traffic** and flags deviations as anomalies during live execution.

The demo focuses on:

* Realtime flow processing
* Explainable step-by-step inference
* Detection of *previously unseen attacks*

---

## What the Demo Shows

For each network flow, the system prints:

1. **Raw flow data** (flow-level features)
2. **Preprocessing details**

   * Numeric scaling
   * Categorical encoding
3. **Autoencoder reconstruction error**
4. **Isolation Forest anomaly score**
5. **Final ensemble decision**

   * Combined score
   * Fixed detection threshold
   * NORMAL / ANOMALY label

This provides full transparency into how decisions are made.

---

## How to Run the Realtime Demo

### Prerequisites

* Python environment activated
* Project dependencies installed
* Models and preprocessing already trained

### Command to Run

```bash
python src/demo_scripts/realtime_trace_csv.py
```

The demo streams flows from:

```
src/demo_scripts/sample_flow_stream.csv
```

and processes them **one by one**, simulating realtime traffic.

---

## How Anomalies Are Simulated

* The system operates on **network flows**, not raw packets.
* Anomalies are simulated by inserting **abnormal flow records** into the CSV.
* Examples include:

  * Extremely high packet counts in very short duration
  * Large byte transfers with suspicious protocol/state combinations
  * Unusual jitter or load values

This approach is:

* Safe
* Reproducible
* Standard in IDS research

---

## How to Interpret the Output

### Normal Traffic

* Low reconstruction error
* Isolation Forest score within normal range
* Combined score **below threshold**
* Labeled as `NORMAL`

### Anomalous Traffic

* High reconstruction error (poor reconstruction)
* Isolation Forest isolates the flow
* Combined score **exceeds threshold**
* Labeled as `ANOMALY`

The detection threshold is:

* **Calibrated offline** on normal traffic
* **Fixed (frozen)** during realtime execution
* Chosen to prioritize attack detection while controlling false positives

---

## Key Design Principles

* **Unsupervised learning** (no labels used during training)
* **Realtime compatible** inference
* **Explainable pipeline**
* **No retraining or tuning during demo**

This ensures the demo reflects a realistic deployment scenario.

---

## Educational Takeaway

The demo illustrates how:

* Normal network behavior can be learned automatically
* Unknown attacks can be detected without signatures
* Realtime decisions can be explained step-by-step

This aligns with modern intrusion detection system (IDS) design.

---

## Stopping the Demo

Press:

```
Ctrl + C
```

to stop the realtime stream.

---

If you want, I can also:

* Condense this into a **1-page viva handout**
* Rewrite it in a **more academic/report style**
* Add a **“common questions”** section for instructors
