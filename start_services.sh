#!/bin/bash

# AI-CAD Service Manager
# Keeps both frontend and backend running

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo -e "${BLUE}🚀 Starting AI-CAD Services${NC}"

# Stop existing processes
echo "Stopping existing processes..."
pkill -f "python.*src.main" 2>/dev/null || true
pkill -f "next.*dev" 2>/dev/null || true
sleep 2

# Start Backend
echo "Starting backend..."
cd "$BACKEND_DIR"
source venv/bin/activate
PYTHONPATH="$BACKEND_DIR/src" nohup python -m src.main > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 5

# Start Frontend
echo "Starting frontend..."
cd "$FRONTEND_DIR"
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Wait for frontend to start
sleep 5

# Check status
echo ""
echo -e "${BLUE}🔍 Service Status:${NC}"

if ps -p $BACKEND_PID > /dev/null; then
    echo -e "${GREEN}✅ Backend is running (PID: $BACKEND_PID)${NC}"
else
    echo -e "${RED}❌ Backend not running${NC}"
fi

if ps -p $FRONTEND_PID > /dev/null; then
    echo -e "${GREEN}✅ Frontend is running (PID: $FRONTEND_PID)${NC}"
else
    echo -e "${RED}❌ Frontend not running${NC}"
fi

echo ""
echo -e "${GREEN}🎉 AI-CAD Services Started!${NC}"
echo "🌐 Frontend: http://localhost:3001"
echo "🔧 Backend API: http://localhost:8100"
echo "📚 API Documentation: http://localhost:8100/docs"
echo ""
echo "Check logs with:"
echo "  tail -f $BACKEND_DIR/backend.log"
echo "  tail -f $FRONTEND_DIR/frontend.log"