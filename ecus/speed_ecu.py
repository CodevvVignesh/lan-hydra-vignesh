# ecus/speed_ecu.py
import time
import os
import can
from utils.can_bus import make_bus

DEFAULT_ID = 0x100
DEFAULT_SPEED = 50  # published value every second

def run(bustype: str = "virtual", channel: str | None = None, interval: float = 1.0):
    """
    Publish a periodic 'speed' CAN frame to the bus.
    """
    os.makedirs("data", exist_ok=True)
    print(f"# ECU (speed) starting — bustype={bustype}, channel={channel}")
    bus = make_bus(channel=channel, bustype=bustype)
    try:
        while True:
            speed = DEFAULT_SPEED
            payload = bytes([int(speed) & 0xFF])
            msg = can.Message(arbitration_id=DEFAULT_ID, data=payload, is_extended_id=False)
            try:
                bus.send(msg)
                print(f"ECU: sent speed={speed}")
            except Exception as e:
                print("ECU: send failed:", e)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("ECU: stopped by user")

if __name__ == "__main__":
    run()
