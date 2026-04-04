#!/bin/bash

cd /home/ishanp/Documents/GitHub/AI-CAD/backend

echo "Starting AI-CAD Backend Server..."
export PORT=8101
export PYTHONPATH="$PWD/src"

# Start server in background
./venv/bin/python -m src.main &
SERVER_PID=$!

echo "Server PID: $SERVER_PID"
echo "Waiting for server to start..."

sleep 5

# Test if server is responding
echo "Testing server..."
wget -qO- http://localhost:8101/api/v1/health || echo "Server not responding"

# Keep server running
wait $SERVER_PID