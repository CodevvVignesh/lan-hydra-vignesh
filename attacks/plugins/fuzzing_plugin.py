# attacks/plugins/fuzzing_plugin.py
import time
from typing import Dict, Any
from attacks.plugin_base import AttackPlugin
from utils.can_bus import make_bus
import can, random

class FuzzingPlugin(AttackPlugin):
    """
    Payload fuzzing: send randomized payloads to chosen IDs (or random IDs).
    config:
      bustype, channel, ids (list), duration, interval
    """
    def _run(self):
        cfg = self.config
        bustype = cfg.get("bustype", "virtual")
        channel = cfg.get("channel", None)
        ids = cfg.get("ids", [0x100])
        interval = float(cfg.get("interval", 0.1))
        duration = cfg.get("duration", None)

        if isinstance(ids, (int, str)):
            ids = [int(ids)]

        if self.dry_run:
            print(f"[FuzzingPlugin] DRY RUN: fuzzing ids={ids}")
            start = time.time()
            while not self._stop_event.is_set():
                print("Fuzz")
                time.sleep(interval)
                if duration and (time.time() - start) >= duration:
                    break
            return

        bus = make_bus(channel=channel, bustype=bustype)
        start = time.time()
        print(f"[FuzzingPlugin] starting fuzzing ids={ids}")
        while not self._stop_event.is_set():
            cid = random.choice(ids)
            length = random.randint(1,8)
            payload = bytes(random.getrandbits(8) for _ in range(length))
            msg = can.Message(arbitration_id=cid, data=payload, is_extended_id=False)
            try:
                bus.send(msg)
            except Exception as e:
                print(f"[FuzzingPlugin] send error: {e}")
            print(f"Fuzzed id=0x{cid:x} len={length}")
            time.sleep(interval)
            if duration and (time.time() - start) >= duration:
                break
        print("[FuzzingPlugin] finished")
