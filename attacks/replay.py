# attacks/replay.py
"""
Small replay: reads a candump-style log and replays messages onto bus created by make_bus()
"""
import re
import time
import argparse
from utils.can_bus import make_bus

LINE_RE = re.compile(r"\((?P<ts>[^)]+)\)\s+(?P<if>[^ ]+)\s+\[(?P<len>\d+)\]\s+(?P<id>[0-9A-Fa-fx]+)#(?P<data>[0-9A-Fa-f]+)")

BUS_BUSTYPE = "virtual"
CHANNEL = None

def parse_line(line: str):
    m = LINE_RE.search(line)
    if not m:
        return None
    arb = int(m.group("id"), 16)
    data_hex = m.group("data")
    data = bytes.fromhex(data_hex)
    return arb, data

def run_replay(filename: str, channel=CHANNEL, bustype=BUS_BUSTYPE):
    bus = make_bus(channel=channel, bustype=bustype)
    with open(filename, "r") as f:
        for line in f:
            p = parse_line(line)
            if not p:
                continue
            arb, data = p
            import can
            msg = can.Message(arbitration_id=arb, data=list(data), is_extended_id=False)
            bus.send(msg)
            print("Replayed", hex(arb), data.hex())
            time.sleep(0.05)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    args = parser.parse_args()
    run_replay(args.file)
