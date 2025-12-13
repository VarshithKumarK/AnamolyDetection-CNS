#!/usr/bin/env python3
"""
client_test.py

Simple client to test the ML Flask API /predict endpoint.

Features:
- Reads first N rows from the UNSW training CSV (default N=5)
- Sends them to the API as:
    1) multipart/form-data CSV upload
    2) JSON payload with records
- Pretty-prints the API response (summary + per-row final_label and explanation)

Usage:
  python client_test.py                # uses defaults
  python client_test.py --rows 10      # send 10 rows
  python client_test.py --mode intersection   # send with ensemble mode intersection
  python client_test.py --json-only    # only run JSON test
  python client_test.py --csv-only     # only run CSV upload test
"""

import argparse
import requests
import pandas as pd
import io
import json
import sys
from typing import Any, Dict

# Default config
API_URL = "http://localhost:5000/predict"
TRAIN_CSV = "data/UNSW_NB15_training-set.csv"

def pretty_print_response(resp_json: Dict[str, Any]) -> None:
    if resp_json is None:
        print("No response JSON to print.")
        return

    summary = resp_json.get("summary")
    if summary:
        print("\n=== SUMMARY ===")
        print(f"Total rows: {summary.get('total_rows')}")
        print(f"Anomalies:   {summary.get('anomalies')}")
        print(f"Mode:        {summary.get('mode')}")
    else:
        print("\n(no summary in response)")

    results = resp_json.get("results", [])
    if not results:
        print("\n(no results in response)")
        return

    print("\n=== ROW RESULTS ===")
    for r in results:
        idx = r.get("index")
        final = r.get("final_label", "UNKNOWN")
        # explanation.triggered_by might be empty list
        triggered = r.get("explanation", {}).get("triggered_by", [])
        ae_score = r.get("ae_score")
        iso_lat_score = r.get("iso_latent_score")
        iso_raw_score = r.get("iso_raw_score")
        print(f"\nRow {idx}: FINAL = {final}")
        print(f"  Triggered by: {triggered}")
        print(f"  AE score:      {ae_score}")
        print(f"  IF_latent score:{iso_lat_score}")
        print(f"  IF_raw score:  {iso_raw_score}")
    print("")

def run_csv_test(df: pd.DataFrame, mode: str = "union") -> Dict:
    """
    Send DataFrame as CSV file upload to /predict?mode=<mode>
    """
    print(f"\n[*] Running CSV upload test with mode={mode} and {len(df)} rows...")
    # convert df to CSV bytes
    csv_buf = io.StringIO()
    df.to_csv(csv_buf, index=False)
    csv_bytes = csv_buf.getvalue().encode("utf-8")

    files = {'file': ('sample.csv', csv_bytes, 'text/csv')}
    params = {'mode': mode}
    try:
        r = requests.post(API_URL, files=files, params=params, timeout=60)
        r.raise_for_status()
        resp_json = r.json()
        print("[+] CSV upload response received.")
        return resp_json
    except Exception as e:
        print(f"[!] CSV request failed: {e}")
        try:
            print("Status code:", r.status_code, "Response text:", r.text[:1000])
        except Exception:
            pass
        return None

def run_json_test(df: pd.DataFrame, mode: str = "union") -> Dict:
    """
    Send DataFrame as JSON records to /predict?mode=<mode>
    """
    print(f"\n[*] Running JSON records test with mode={mode} and {len(df)} rows...")
    records = df.to_dict(orient="records")
    headers = {'Content-Type': 'application/json'}
    params = {'mode': mode}
    payload = {"records": records}
    try:
        r = requests.post(API_URL, json=payload, headers=headers, params=params, timeout=60)
        r.raise_for_status()
        resp_json = r.json()
        print("[+] JSON request response received.")
        return resp_json
    except Exception as e:
        print(f"[!] JSON request failed: {e}")
        try:
            print("Status code:", r.status_code, "Response text:", r.text[:1000])
        except Exception:
            pass
        return None

def main():
    parser = argparse.ArgumentParser(description="Client tester for ML Flask API /predict")
    parser.add_argument("--csv-path", default=TRAIN_CSV, help="Path to training CSV (default data/UNSW_NB15_training-set.csv)")
    parser.add_argument("--rows", type=int, default=5, help="Number of rows to send (default 5)")
    parser.add_argument("--mode", choices=["union","intersection"], default="union", help="Ensemble mode for API")
    parser.add_argument("--json-only", action="store_true", help="Only run JSON test")
    parser.add_argument("--csv-only", action="store_true", help="Only run CSV upload test")
    args = parser.parse_args()

    # load CSV slice
    try:
        df_full = pd.read_csv(args.csv_path)
    except Exception as e:
        print(f"[!] Failed to read CSV at {args.csv_path}: {e}")
        sys.exit(1)

    if args.rows <= 0:
        print("[!] --rows must be > 0")
        sys.exit(1)

    df = df_full.head(args.rows).copy()
    print(f"Loaded {len(df)} rows from {args.csv_path}")

    csv_result = None
    json_result = None

    if not args.json_only:
        csv_result = run_csv_test(df, mode=args.mode)
        if csv_result:
            pretty_print_response(csv_result)

    if not args.csv_only:
        json_result = run_json_test(df, mode=args.mode)
        if json_result:
            pretty_print_response(json_result)

if __name__ == "__main__":
    main()
