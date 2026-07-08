#!/usr/bin/env bash
set -euo pipefail

PORTS=(8000 3000)

echo "Stopping ShopPilot processes on ports ${PORTS[*]}..."

for port in "${PORTS[@]}"; do
  pids="$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
  if [[ -z "$pids" ]]; then
    echo "  Port $port: free"
    continue
  fi

  echo "  Port $port: stopping PID(s) $pids"
  kill $pids 2>/dev/null || true
  sleep 1

  remaining="$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
  if [[ -n "$remaining" ]]; then
    echo "  Port $port: force-stopping PID(s) $remaining"
    kill -9 $remaining 2>/dev/null || true
  fi
done

echo "Done."
