#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

# ── Configure your virtual environment path here ──────────
# Leave blank to auto-detect (looks for venv, .venv, env in project root)
VENV_PATH=""

# ──────────────────────────────────────────────────────────

# Auto-detect venv if not set manually
if [ -z "$VENV_PATH" ]; then
    for name in venv .venv env; do
        if [ -f "$ROOT/$name/bin/activate" ]; then
            VENV_PATH="$ROOT/$name"
            break
        fi
    done
fi

if [ -z "$VENV_PATH" ]; then
    echo "[ERROR] No virtual environment found."
    echo "Set VENV_PATH at the top of this script, e.g.:"
    echo "  VENV_PATH=\"\$HOME/.virtualenvs/personal_ai\""
    exit 1
fi

echo ""
echo " Virtual env : $VENV_PATH"
echo " Backend     → http://localhost:7860"
echo " Frontend    → http://localhost:3000"
echo ""

# Activate venv and start backend
source "$VENV_PATH/bin/activate"
python "$ROOT/app.py" &
BACKEND_PID=$!
echo " ✓ Backend started (PID $BACKEND_PID)"

# Start frontend (no venv needed)
cd "$ROOT/frontend" && npm run dev &
FRONTEND_PID=$!
echo " ✓ Frontend started (PID $FRONTEND_PID)"

echo ""
echo " Press Ctrl+C to stop both services."
echo ""

trap "echo ''; echo ' Stopping...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" SIGINT SIGTERM

wait $BACKEND_PID $FRONTEND_PID
