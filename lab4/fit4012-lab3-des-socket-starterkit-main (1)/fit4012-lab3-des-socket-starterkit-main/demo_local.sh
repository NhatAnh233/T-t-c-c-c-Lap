#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-6001}"
MESSAGE="${2:-Xin chao FIT4012}"

PYTHONUNBUFFERED=1 RECEIVER_HOST=127.0.0.1 RECEIVER_PORT="$PORT" SOCKET_TIMEOUT=10 python receiver.py &
receiver_pid=$!
sleep 1
SERVER_IP=127.0.0.1 SERVER_PORT="$PORT" MESSAGE="$MESSAGE" python sender.py
wait "$receiver_pid"
