import pandas as pd
import random
import time
import os

OUTPUT_DIR = "test_csvs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================
# FULL UNSW-NB15 SCHEMA
# =========================

CATEGORICAL_COLUMNS = ["proto", "service", "state"]

NUMERIC_COLUMNS = [
    "dur","sbytes","dbytes","sttl","dttl","sloss","dloss",
    "sload","dload","spkts","dpkts","swin","dwin","stcpb","dtcpb",
    "smss","dmss","sjit","djit","stime","ltime",
    "swin_max","dwin_max","tcprtt","synack","ackdat",
    "smeansz","dmeansz","trans_depth","res_bdy_len",
    "srv_count","same_srv_rate",
    "dst_host_count","dst_host_srv_count",
    "dst_host_same_srv_rate","dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate","dst_host_srv_diff_host_rate",
    "dst_host_serror_rate","dst_host_srv_serror_rate"
]

ALL_COLUMNS = CATEGORICAL_COLUMNS + NUMERIC_COLUMNS


# =========================
# GENERATORS
# =========================

def generate_normal_row():
    now = int(time.time())
    return {
        "proto": "tcp",
        "service": "http",
        "state": "FIN",

        "dur": round(random.uniform(1, 20), 2),
        "sbytes": random.randint(500, 2000),
        "dbytes": random.randint(500, 3000),
        "sttl": 64,
        "dttl": 64,
        "sloss": 0,
        "dloss": 0,
        "sload": random.randint(5000, 15000),
        "dload": random.randint(5000, 20000),
        "spkts": random.randint(5, 20),
        "dpkts": random.randint(5, 25),
        "swin": 8192,
        "dwin": 8192,
        "stcpb": random.randint(10000, 50000),
        "dtcpb": random.randint(10000, 50000),
        "smss": 1460,
        "dmss": 1460,
        "sjit": round(random.uniform(0.01, 0.5), 3),
        "djit": round(random.uniform(0.01, 0.5), 3),
        "stime": now,
        "ltime": now + random.randint(1, 10),
        "swin_max": 8192,
        "dwin_max": 8192,
        "tcprtt": round(random.uniform(0.01, 0.2), 3),
        "synack": round(random.uniform(0.01, 0.1), 3),
        "ackdat": round(random.uniform(0.01, 0.1), 3),
        "smeansz": random.randint(80, 150),
        "dmeansz": random.randint(80, 200),
        "trans_depth": 1,
        "res_bdy_len": 0,
        "srv_count": random.randint(5, 20),
        "same_srv_rate": round(random.uniform(0.6, 0.9), 2),
        "dst_host_count": 255,
        "dst_host_srv_count": random.randint(100, 200),
        "dst_host_same_srv_rate": round(random.uniform(0.6, 0.9), 2),
        "dst_host_diff_srv_rate": round(random.uniform(0.01, 0.05), 2),
        "dst_host_same_src_port_rate": round(random.uniform(0.5, 0.8), 2),
        "dst_host_srv_diff_host_rate": round(random.uniform(0.01, 0.05), 2),
        "dst_host_serror_rate": 0.0,
        "dst_host_srv_serror_rate": 0.0,
    }


def generate_anomaly_row():
    now = int(time.time())
    return {
        "proto": "udp",
        "service": "dns",
        "state": "INT",

        "dur": round(random.uniform(200, 800), 2),
        "sbytes": random.randint(500000, 1500000),
        "dbytes": random.randint(0, 200),
        "sttl": random.randint(1, 5),
        "dttl": random.randint(1, 5),
        "sloss": random.randint(10, 100),
        "dloss": 0,
        "sload": random.randint(500000, 2000000),
        "dload": random.randint(100, 2000),
        "spkts": random.randint(1000, 10000),
        "dpkts": random.randint(1, 5),
        "swin": 0,
        "dwin": 0,
        "stcpb": 0,
        "dtcpb": 0,
        "smss": 512,
        "dmss": 512,
        "sjit": round(random.uniform(10, 100), 2),
        "djit": round(random.uniform(10, 100), 2),
        "stime": now,
        "ltime": now + random.randint(200, 600),
        "swin_max": 0,
        "dwin_max": 0,
        "tcprtt": round(random.uniform(0.5, 2.0), 2),
        "synack": round(random.uniform(0.5, 2.0), 2),
        "ackdat": round(random.uniform(0.5, 2.0), 2),
        "smeansz": random.randint(500, 2000),
        "dmeansz": random.randint(10, 60),
        "trans_depth": random.randint(5, 20),
        "res_bdy_len": random.randint(100, 1000),
        "srv_count": random.randint(50, 200),
        "same_srv_rate": round(random.uniform(0.01, 0.1), 2),
        "dst_host_count": 255,
        "dst_host_srv_count": random.randint(1, 20),
        "dst_host_same_srv_rate": round(random.uniform(0.01, 0.1), 2),
        "dst_host_diff_srv_rate": round(random.uniform(0.8, 1.0), 2),
        "dst_host_same_src_port_rate": round(random.uniform(0.01, 0.1), 2),
        "dst_host_srv_diff_host_rate": round(random.uniform(0.7, 1.0), 2),
        "dst_host_serror_rate": round(random.uniform(0.7, 1.0), 2),
        "dst_host_srv_serror_rate": round(random.uniform(0.7, 1.0), 2),
    }


# =========================
# CSV GENERATION
# =========================

def save_csv(filename, rows):
    df = pd.DataFrame(rows, columns=ALL_COLUMNS)
    path = os.path.join(OUTPUT_DIR, filename)
    df.to_csv(path, index=False)
    print(f"✅ Generated {path}")


if __name__ == "__main__":
    # One NORMAL row
    save_csv("test_normal.csv", [generate_normal_row()])

    # One ANOMALY row
    save_csv("test_anomaly.csv", [generate_anomaly_row()])

    # Mixed (3 rows)
    save_csv(
        "test_mixed.csv",
        [
            generate_normal_row(),
            generate_anomaly_row(),
            generate_normal_row(),
        ]
    )
