# api.py
"""
Flask ML API that returns model predictions plus a final_label and explanation.
Endpoint:
  POST /predict?mode=union|intersection
Accepts:
  - multipart/form-data file upload (CSV, form field 'file')
  - JSON body with {"records": [ {col:val, ...}, ... ] } or raw list of dicts
Returns:
  JSON with per-row results including iso_raw_label, iso_latent_label, ae_label, scores,
  final_label ("ANOMALY"|"NORMAL"), and explanation (which models flagged anomaly).
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import io
import json
from predict import predict_df  # uses saved models; predict_df returns {'results': [...]}

app = Flask(__name__)
CORS(app)  # restrict in production

# Default ensemble mode
DEFAULT_MODE = "union"  # options: 'union' or 'intersection'

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

def compute_final_label_and_explanation(row_dict, mode="union"):
    """
    Input: row_dict contains keys:
      iso_raw_label, iso_latent_label, ae_label, iso_raw_score, iso_latent_score, ae_score
    mode: 'union' or 'intersection'
    Returns: final_label ("ANOMALY"|"NORMAL") and explanation string/list
    """
    # Convert to ints (labels expected 0/1)
    iso_raw = int(row_dict.get("iso_raw_label", 0))
    iso_lat = int(row_dict.get("iso_latent_label", 0))
    ae = int(row_dict.get("ae_label", 0))

    triggered = []
    if iso_raw == 1:
        triggered.append("iso_raw")
    if iso_lat == 1:
        triggered.append("iso_latent")
    if ae == 1:
        triggered.append("autoencoder")

    if mode == "intersection":
        is_anomaly = (iso_raw == 1) and (iso_lat == 1) and (ae == 1)
    else:  # union or any unknown mode defaults to union
        is_anomaly = len(triggered) > 0

    final_label = "ANOMALY" if is_anomaly else "NORMAL"

    # Explanation: list triggered and short text on scores
    explanation = {
        "triggered_by": triggered,
        "scores": {
            "ae_score": row_dict.get("ae_score"),
            "iso_latent_score": row_dict.get("iso_latent_score"),
            "iso_raw_score": row_dict.get("iso_raw_score")
        }
    }
    return final_label, explanation

@app.route("/predict", methods=["POST"])
def predict_route():
    # ensemble mode query param
    mode = request.args.get("mode", DEFAULT_MODE).lower()
    if mode not in ("union", "intersection"):
        return jsonify({"error": "Invalid mode. Use mode=union or mode=intersection"}), 400

    # Parse input: CSV file upload or JSON
    df = None
    if 'file' in request.files:
        file = request.files['file']
        try:
            content = file.read().decode('utf-8')
            df = pd.read_csv(io.StringIO(content))
        except Exception as e:
            return jsonify({"error": f"Failed to parse uploaded CSV: {e}"}), 400
    else:
        # JSON body
        try:
            body = request.get_json(force=True)
        except Exception as e:
            return jsonify({"error": f"Failed to read JSON body: {e}"}), 400
        if body is None:
            return jsonify({"error": "No file uploaded and no JSON body present"}), 400

        # Accept different JSON shapes: {"records":[...]} or list-of-dicts
        if isinstance(body, dict) and "records" in body:
            records = body["records"]
        elif isinstance(body, list):
            records = body
        else:
            # maybe the body itself is a dict representing a single record
            if isinstance(body, dict):
                # If dict contains numeric columns, treat as single record
                records = [body]
            else:
                return jsonify({"error": "JSON body must be a list of records or contain 'records' key"}), 400
        try:
            df = pd.DataFrame.from_records(records)
        except Exception as e:
            return jsonify({"error": f"Failed to construct DataFrame from JSON records: {e}"}), 400

    # At this point we have df
    if df is None or df.shape[0] == 0:
        return jsonify({"error": "No data found in input"}), 400

    try:
        prediction_payload = predict_df(df)  # {'results': [ {index,...}, ... ]}
    except Exception as e:
        return jsonify({"error": f"Prediction error: {e}"}), 500

    results = prediction_payload.get("results", [])
    # compute final_label and explanation per row
    enhanced = []
    for r in results:
        final_label, explanation = compute_final_label_and_explanation(r, mode=mode)
        r_enh = r.copy()
        r_enh["final_label"] = final_label
        r_enh["explanation"] = explanation
        enhanced.append(r_enh)

    # summary counts
    total = len(enhanced)
    anomalies = sum(1 for r in enhanced if r["final_label"] == "ANOMALY")
    summary = {"total_rows": total, "anomalies": anomalies, "mode": mode}

    return jsonify({"summary": summary, "results": enhanced})

if __name__ == "__main__":
    # For development; in production use gunicorn/uwsgi
    app.run(host="0.0.0.0", port=5000, debug=True)
