#!/usr/bin/env bash

set -euo pipefail

TARGET_IP=${1:-127.0.0.1}
SEQUENCE=${2:-"1234,5678,9012"}
PROTECTED_PORT=${3:-2222}

# Start the knock server in the background
echo "[0/4] Starting knock server..."
python3 knock_server.py --sequence "$SEQUENCE" --protected-port "$PROTECTED_PORT" &
KNOCK_PID=$!

# Give the server a second to bind ports
sleep 1

echo "[1/4] Attempting protected port before knocking"
nc -z -v "$TARGET_IP" "$PROTECTED_PORT" || echo "Port $PROTECTED_PORT is closed (expected)"

echo "[2/4] Sending knock sequence: $SEQUENCE"
python3 knock_client.py --target "$TARGET_IP" --sequence "$SEQUENCE" --check

echo "[3/4] Attempting protected port after knocking"
nc -z -v "$TARGET_IP" "$PROTECTED_PORT" && echo "Port $PROTECTED_PORT is now open!"

# Optional: stop the knock server
kill $KNOCK_PID
echo "[4/4] Demo finished"
