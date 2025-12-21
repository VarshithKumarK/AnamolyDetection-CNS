"""PCAP realtime trace placeholder (no packet capture).

This stub shows how PCAP replay and flow extraction would conceptually connect
into the existing inference pipeline without changing score_flow().

Important:
- No packet capture or replay is implemented here.
- Do NOT run real attacks on production networks.
- This file is for documentation and explanation only.
"""
from __future__ import annotations

# Conceptual outline only (commented pseudo-code):

# 1) Traffic injection (lab-only)
#    Use tcpreplay to inject packets from a PCAP into a test interface.
#    Example (theory):
#        tcpreplay --intf1=eth1 sample.pcap
#    This is performed outside Python.

# 2) Flow extraction
#    A separate collector aggregates packets into flow records comparable to
#    UNSW-NB15 fields (dur, spkts, dpkts, sbytes, dbytes, rate, proto, service, state, ...).
#    The extractor outputs rows (e.g., JSON lines or CSV) to a local pipe/queue.

# 3) Reuse score_flow() unchanged
#    from src.realtime_service.inference import score_flow
#
#    def on_new_flow(flow_record: dict):
#        result = score_flow(flow_record)
#        print({
#            "raw": {k: flow_record.get(k) for k in ("dur","sbytes","dbytes","proto","service","state")},
#            "score": result.get("score"),
#            "is_anomaly": result.get("is_anomaly"),
#            "details": result.get("details"),
#        })
#
#    # Wire on_new_flow to the extractor's output stream.

if __name__ == "__main__":
    print(
        "This is a placeholder. No PCAP handling is implemented.\n"
        "See comments for where tcpreplay and a flow extractor would connect to score_flow()."
    )
