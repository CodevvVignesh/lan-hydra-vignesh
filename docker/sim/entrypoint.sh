#!/usr/bin/env bash
set -euo pipefail

# create the vcan interface (ignore errors if exists)
modprobe vcan || true
ip link add dev vcan0 type vcan 2>/dev/null || true
ip link set up vcan0

# Ensure a config exists for upstream sim
mkdir -p /work/canbus/config
cat > /work/canbus/config/config.json <<'JSON'
{
  "channel": "vcan0",
  "nbNodes": 3,
  "totalNodes": 3,
  "delay": 1,
  "verbose": true,
  "sign": false,
  "startId": 100
}
JSON

cd /work/canbus
# run upstream simulator (stdout to console)
python3 src/main.py
