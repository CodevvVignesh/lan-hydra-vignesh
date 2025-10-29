# utils/can_bus.py
"""
Compatibility helper to create a python-can Bus while handling the
deprecation of the 'bustype' argument (use 'interface' in newer python-can).
"""
from typing import Optional

def make_bus(channel: Optional[str] = None, bustype: str = "virtual"):
    """
    Create and return a python-can Bus instance.
    - In python-can >= 4.2: uses interface=<bustype>
    - Fallback: uses bustype=<bustype> for older versions
    """
    import can
    try:
        # Preferred in python-can >= 4.2
        return can.interface.Bus(interface=bustype, channel=channel)
    except TypeError:
        # Older python-can: expects bustype=
        return can.interface.Bus(bustype=bustype, channel=channel)
