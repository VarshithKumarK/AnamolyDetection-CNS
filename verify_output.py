import sys
import os
import pandas as pd
import json

# Ensure we can import from ml_service
sys.path.append(os.path.join(os.getcwd(), "ml_service"))

from ml_service.predict import predict_df


def test_prediction():
    print("Running prediction test...")

    # Create a sample row that simulates a high-entropy, encrypted-like flow
    sample_data = {
        "proto": "tcp",
        "service": "ssl",
        "state": "FIN",
        "sbytes": 50000,
        "dbytes": 45000,
        "spkts": 50,
        "dpkts": 45,
        "dur": 1.5,
        "sttl": 62,
        "dttl": 252,
        "tcprtt": 0.05,
        "synack": 0.02,
        "ackdat": 0.03,
        "smeansz": 1000,
        "dmeansz": 1000,
        "ackdat": 0.05,
    }

    df = pd.DataFrame([sample_data])

    try:
        response = predict_df(df)

        # Check if results exist
        if "results" not in response:
            print("FAIL: No 'results' key in response")
            return

        result = response["results"][0]

        # Check for network_context
        if "network_context" not in result:
            print("FAIL: No 'network_context' in result")
            return

        ctx = result["network_context"]
        print("\nSUCCESS: Network Context Retrieved:")
        print(json.dumps(ctx, indent=2))

        # Verify specific derived field logic
        if ctx["traffic_asymmetry"] != 0:  # Should be calculated
            print(f"traffic_asymmetry: {ctx['traffic_asymmetry']:.4f} (OK)")
        else:
            print(
                "WARNING: traffic_asymmetry is 0 (might be correct if bytes are equal, but check logic)"
            )

    except Exception as e:
        print(f"ERROR during prediction: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_prediction()
