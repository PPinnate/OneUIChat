#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "[QwenWorkbench] Preparing Python virtual environment..."
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e backend[dev]

echo "[QwenWorkbench] Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "[QwenWorkbench] Starting backend and frontend..."
( source .venv/bin/activate && cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 ) &
BACKEND_PID=$!

cleanup() {
  echo "[QwenWorkbench] Stopping services..."
  kill "$BACKEND_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT

sleep 2
open "http://127.0.0.1:5173"
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
