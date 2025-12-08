#!/bin/bash
cd "$(dirname "$0")"
echo "Stopping any existing server..."
pkill -f "uvicorn app.main:app" || true
sleep 1
echo "Starting server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
