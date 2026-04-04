#!/bin/bash

# AI-CAD System Startup Script
# This script starts both backend and frontend services

echo "🚀 Starting AI-CAD System..."

# Function to check if port is in use
check_port() {
    local port=$1
    if python -c "
import socket
try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('127.0.0.1', $port))
    print('Port $port is in use')
    exit(1)
except:
    print('Port $port is available')
    exit(0)
" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Check if ports are available
if ! check_port 8100; then
    echo "❌ Port 8100 is already in use. Please stop the existing service."
    exit 1
fi

if ! check_port 3000; then
    echo "❌ Port 3000 is already in use. Please stop the existing service."
    exit 1
fi

# Start Backend
echo "🔧 Starting Backend API..."
cd backend
PYTHONPATH=./src python -c "
import uvicorn
from main import app
print('✅ Backend API starting on http://127.0.0.1:8100')
uvicorn.run(app, host='127.0.0.1', port=8100, log_level='info')
" &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Test backend health
python -c "
import requests
import time
for i in range(10):
    try:
        response = requests.get('http://127.0.0.1:8100/health', timeout=2)
        print('✅ Backend is healthy!')
        break
    except:
        if i < 9:
            time.sleep(1)
        else:
            print('❌ Backend failed to start')
            exit(1)
"

# Start Frontend
echo "🎨 Starting Frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 10

# Test frontend health
python -c "
import requests
import time
for i in range(10):
    try:
        response = requests.get('http://127.0.0.1:3000', timeout=2)
        print('✅ Frontend is healthy!')
        break
    except:
        if i < 9:
            time.sleep(1)
        else:
            print('❌ Frontend failed to start')
            exit(1)
"

echo ""
echo "🎉 AI-CAD System is now running!"
echo "📍 Frontend: http://127.0.0.1:3000"
echo "📍 Backend API: http://127.0.0.1:8100"
echo "📍 API Docs: http://127.0.0.1:8100/docs"
echo ""
echo "Process IDs:"
echo "  Backend PID: $BACKEND_PID"
echo "  Frontend PID: $FRONTEND_PID"
echo ""
echo "To stop the system, run: kill $BACKEND_PID $FRONTEND_PID"
echo "Or use: ./stop_services.sh"

# Save PIDs for later use
echo "$BACKEND_PID" > ../.backend.pid
echo "$FRONTEND_PID" > ../.frontend.pid

echo ""
echo "💡 System Features Ready:"
echo "  ✅ DXF Viewer with interactive controls"
echo "  ✅ AI-powered plan generation"
echo "  ✅ Real-time WebSocket updates"
echo "  ✅ Comprehensive error handling"
echo "  ✅ Export capabilities"
echo ""