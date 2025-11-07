#!/bin/bash

# AI-CAD System Stop Script
# This script stops both backend and frontend services

echo "🛑 Stopping AI-CAD System..."

# Read PIDs from files if they exist
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    echo "🔧 Stopping backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null || echo "Backend process not found"
    rm .backend.pid
fi

if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    echo "🎨 Stopping frontend (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null || echo "Frontend process not found"
    rm .frontend.pid
fi

# Also kill any remaining processes on the ports
echo "🧹 Cleaning up any remaining processes..."

# Kill processes on port 8100 (backend)
pkill -f "port.*8100" 2>/dev/null || true

# Kill processes on port 3000 (frontend)
pkill -f "next.*dev" 2>/dev/null || true

echo "✅ AI-CAD System stopped successfully!"