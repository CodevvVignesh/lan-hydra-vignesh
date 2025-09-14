import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# demo/combined_demo.py
import threading
import time
from utils.can_bus import make_bus

BUS_BUSTYPE = "virtual"
CHANNEL = None

def ecu_loop(bus, stop_event):
    msg_id = 0x100
    while not stop_event.is_set():
        import can
        msg = can.Message(arbitration_id=msg_id, data=[0x32], is_extended_id=False)
        bus.send(msg)
        print("ECU: sent speed=50")
        time.sleep(1)

def injector_loop(bus, value=220, interval=0.2, duration=6):
    msg_id = 0x100
    end = time.time() + duration
    import can
    while time.time() < end:
        msg = can.Message(arbitration_id=msg_id, data=[value], is_extended_id=False)
        bus.send(msg)
        print("Injected", value)
        time.sleep(interval)

def monitor_loop(bus, stop_event):
    print("Monitor started (prints all frames)")
    while not stop_event.is_set():
        msg = bus.recv(timeout=1.0)
        if msg is not None:
            print(f"[MON] ID=0x{msg.arbitration_id:X} LEN={msg.dlc} DATA={msg.data.hex()}")

def main():
    bus = make_bus(channel=CHANNEL, bustype=BUS_BUSTYPE)
    stop_event = threading.Event()

    t_ecu = threading.Thread(target=ecu_loop, args=(bus, stop_event), daemon=True)
    t_monitor = threading.Thread(target=monitor_loop, args=(bus, stop_event), daemon=True)

    t_ecu.start()
    t_monitor.start()

    # give ECU/monitor a moment
    time.sleep(1)
    # run injector in same process (not a thread) so we can wait for completion
    injector_loop(bus, value=220, interval=0.2, duration=6)

    # stop everything
    stop_event.set()
    time.sleep(0.5)
    print("Combined demo finished")

if __name__ == "__main__":
    main()
