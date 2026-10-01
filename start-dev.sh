#!/usr/bin/env bash
# One command to start the whole app correctly: backend first, confirmed
# actually up (not just "command ran"), then the frontend. Run this from
# the repo root: ./start-dev.sh
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

echo "==> Installing backend dependencies..."
pip install -r requirements.txt --quiet --break-system-packages 2>/dev/null || pip install -r requirements.txt --quiet

echo "==> Starting backend..."
python -m app.main > /tmp/gpip-backend.log 2>&1 &
BACKEND_PID=$!

cleanup() {
  echo ""
  echo "==> Stopping backend..."
  kill "$BACKEND_PID" 2>/dev/null || true
}
trap cleanup EXIT

echo "==> Waiting for the backend to actually respond (not just start)..."
BACKEND_UP=false
for _ in $(seq 1 20); do
  if curl -s -o /dev/null http://127.0.0.1:8000/; then
    BACKEND_UP=true
    break
  fi
  sleep 1
done

if [ "$BACKEND_UP" != "true" ]; then
  echo ""
  echo "!! The backend did not come up after 20 seconds. Here's its log:"
  echo "----------------------------------------------------------------"
  cat /tmp/gpip-backend.log
  echo "----------------------------------------------------------------"
  echo "Fix whatever's shown above, then run ./start-dev.sh again."
  exit 1
fi

echo "==> Backend confirmed running at http://0.0.0.0:8000"
echo "==> Installing frontend dependencies (first run only - this can take a minute)..."
cd frontend
npm install --silent

echo "==> Starting frontend. A popup should appear offering to open port 5173 -"
echo "    use that, or the Ports tab, rather than any previously saved link."
echo ""
npm run dev
