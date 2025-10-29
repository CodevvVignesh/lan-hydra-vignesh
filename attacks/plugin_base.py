# attacks/plugin_base.py
import threading
import time
from typing import Dict, Any

class AttackPlugin:
    """
    Minimal plugin base class for LAN-Hydra.
    Subclasses must implement _run() and can optionally override configure().
    """

    def __init__(self, config: Dict[str, Any] = None, dry_run: bool = True):
        self.config = config or {}
        self.dry_run = dry_run
        self._stop_event = threading.Event()
        self._thread = None

    def configure(self, config: Dict[str, Any]):
        """Apply configuration from caller/CLI"""
        self.config.update(config or {})

    def start(self):
        """Start plugin in background thread."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_wrapper, daemon=True)
        self._thread.start()

    def stop(self):
        """Signal thread to stop and wait."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def _run_wrapper(self):
        try:
            self._run()
        except Exception as e:
            # keep plugin from crashing whole program
            print(f"[{self.__class__.__name__}] Exception: {e}")

    def _run(self):
        """Main plugin logic. Subclasses MUST implement this."""
        raise NotImplementedError
