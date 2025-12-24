"""
Feature engineering module for derived Network & Cryptography parameters.
"""

import pandas as pd
import numpy as np


def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Augment the dataframe with derived network security features.

    New Features:
    1. traffic_asymmetry: (sbytes - dbytes) / (sbytes + dbytes)
       - Range: [-1, 1]. Close to 1 (upload), -1 (download), 0 (symmetric).

    2. packet_density: (spkts + dpkts) / dur
       - Packets per second. High values indicate flooding/DoS.

    3. connection_setup_ratio: tcprtt / dur
       - High ratio indicates short connections dominated by handshake (scanning).

    4. ack_efficiency: ackdat / (tcprtt + epsilon)
       - Efficiency of acknowledgement relative to RTT.

    5. payload_fullness: (smeansz + dmeansz) / 2
       - Proxy for payload density. High values (near MTU) often imply encrypted/compressed bulk data.

    6. header_ratio: (spkts * 54) / (sbytes + epsilon)
       - Approximation of header overhead. High ratio means control traffic.
    """
    # Working on a copy to avoid side-effects
    df_out = df.copy()

    # Safely handle division by zero with epsilon
    epsilon = 1e-6

    # 1. Traffic Asymmetry
    # Using numpy for vectorized operations which handle NaNs/division better
    sbytes = df_out.get("sbytes", 0)
    dbytes = df_out.get("dbytes", 0)
    total_bytes = sbytes + dbytes + epsilon
    df_out["traffic_asymmetry"] = (sbytes - dbytes) / total_bytes

    # 2. Packet Density
    dur = df_out.get("dur", epsilon)
    # Avoid zero duration
    dur = dur.replace(0, epsilon)
    spkts = df_out.get("spkts", 0)
    dpkts = df_out.get("dpkts", 0)
    df_out["packet_density"] = (spkts + dpkts) / dur

    # 3. Connection Setup Ratio
    tcprtt = df_out.get("tcprtt", 0)
    df_out["connection_setup_ratio"] = tcprtt / dur

    # 4. Ack Efficiency
    ackdat = df_out.get("ackdat", 0)
    df_out["ack_efficiency"] = ackdat / (tcprtt + epsilon)

    # 5. Payload Fullness (Proxy for Encryption signatures)
    smeansz = df_out.get("smeansz", 0)
    dmeansz = df_out.get("dmeansz", 0)
    df_out["payload_fullness"] = (smeansz + dmeansz) / 2.0

    # 6. Header Ratio (Control vs Data)
    # Assuming min 54 bytes for basic TCP/IP headers roughly
    df_out["header_ratio"] = (spkts * 54) / (sbytes + epsilon)

    # Fill any NaNs created by weird data with 0
    cols = [
        "traffic_asymmetry",
        "packet_density",
        "connection_setup_ratio",
        "ack_efficiency",
        "payload_fullness",
        "header_ratio",
    ]

    for c in cols:
        if c in df_out.columns:
            df_out[c] = df_out[c].fillna(0.0)

    return df_out
