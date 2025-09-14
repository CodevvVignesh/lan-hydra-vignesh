#!/usr/bin/env bash
set -e
# demo runner: start ECU, monitor, inject, replay (virtual bus)
source venv/bin/activate

# start monitor in background
python monitor/monitor_bus.py > data/monitor.log 2>&1 &
MON_PID=$!

# start ECU simulator in background
python ecus/speed_ecu.py > data/ecu.log 2>&1 &
ECU_PID=$!

sleep 1

# run injection
python attacks/injection.py --duration 6 --value 220

# optional: run replay (uncomment to enable)
# python attacks/replay.py --file data/sample_candump.log

# cleanup
kill $ECU_PID || true
kill $MON_PID || true

echo "Demo finished. Logs: data/monitor.log data/ecu.log"
