# monitor/monitor_bus.py
import can
import json
import time
import os
from utils.can_bus import make_bus

def run(bustype="virtual", channel=None):
    log_path = os.path.join("data", "monitor.log")
    os.makedirs("data", exist_ok=True)

    print(f"# Monitor will append JSON lines to {log_path}")
    with open(log_path, "a") as logfile:
        bus = make_bus(channel=channel, bustype=bustype)
        print("Monitoring CAN bus... Press Ctrl+C to exit")
        try:
            while True:
                msg = bus.recv(timeout=1)
                if msg is None:
                    continue
                # Save message in JSON format
                log_entry = {
                    "timestamp": time.time(),
                    "arbitration_id": msg.arbitration_id,
                    "data": msg.data.hex()
                }
                logfile.write(json.dumps(log_entry) + "\n")
                logfile.flush()
                print(log_entry)
        except KeyboardInterrupt:
            print("Stopped monitoring")
