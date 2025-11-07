#!/bin/bash
# AI-CAD Backend Startup Script

echo "🚀 Starting AI-CAD Backend..."

cd /home/ishanp/Documents/GitHub/AI-CAD/backend

# Kill any existing processes
pkill -f "uvicorn src.main:app" 2>/dev/null
pkill -f "debug_enhanced.py" 2>/dev/null

# Set environment variables
export OPENAI_API_KEY="dummy-key-for-testing"
export PYTHONPATH="$PWD/src"
export PORT=8100

# Start the enhanced debug server (which works) in the background
echo "📡 Starting WebSocket-compatible server on port 8100..."
PYTHONPATH="$PWD/src" ./venv/bin/python debug_enhanced.py > /tmp/aicad_backend.log 2>&1 &
BACKEND_PID=$!

echo "✅ Backend started with PID: $BACKEND_PID"
echo "📊 Logs available at: /tmp/aicad_backend.log"
echo "🔗 WebSocket endpoint: ws://localhost:8100/ws/plans/{plan_id}"
echo "🌐 Health endpoint: http://localhost:8100/api/v1/health"

# Wait a moment and test
sleep 3
if curl -s http://localhost:8100/api/v1/health > /dev/null 2>&1; then
    echo "✅ Backend is responding to HTTP requests"
else
    echo "❌ Backend is not responding - check logs"
fi

echo "🎯 Backend setup complete!"