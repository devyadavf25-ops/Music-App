#!/bin/sh
set -e

PORT="${PORT:-8001}"
echo "=================================================="
echo "Starting Aura Music Platform API"
echo "Listening on 0.0.0.0:${PORT}"
echo "=================================================="

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT}" --workers 1
