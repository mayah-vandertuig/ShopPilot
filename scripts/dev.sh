#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -x "$ROOT/backend/.venv/bin/python" ]]; then
  echo "Backend venv not found. Run: make install-backend"
  exit 1
fi

if [[ ! -d "$ROOT/frontend/node_modules" ]]; then
  echo "Frontend deps not found. Run: make install-frontend"
  exit 1
fi

cleanup() {
  echo ""
  echo "Stopping ShopPilot..."
  [[ -n "${BACKEND_PID:-}" ]] && kill "$BACKEND_PID" 2>/dev/null || true
  [[ -n "${FRONTEND_PID:-}" ]] && kill "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "Starting ShopPilot..."
echo "  Backend:  http://127.0.0.1:8000"
echo "  Frontend: http://127.0.0.1:3000"
echo "Press Ctrl+C to stop both servers."
echo ""

(cd "$ROOT/backend" && .venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000) &
BACKEND_PID=$!

sleep 2

(cd "$ROOT/frontend" && npm run dev -- --hostname 127.0.0.1 --port 3000) &
FRONTEND_PID=$!

wait
