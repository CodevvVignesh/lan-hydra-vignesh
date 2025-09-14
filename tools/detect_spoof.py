# tools/detect_spoof.py
import json, sys
from collections import deque

LOG = "data/monitor.log"

def hex_to_int(h): return int(h, 16)

def detect(threshold_delta=50, target_id="0x100"):
    with open(LOG) as f:
        last = None
        for line in f:
            rec = json.loads(line)
            if rec["id"] != target_id:
                continue
            value = int(rec["data"], 16) if len(rec["data"])<=2 else None
            if value is None:
                continue
            if last is not None and abs(value - last) >= threshold_delta:
                print(f"[ALERT] sudden change {last} -> {value} at {rec['time']}")
            last = value

if __name__ == "__main__":
    detect()
