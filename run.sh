#!/bin/bash

# AI-CAD Simple Launcher
# Starts both frontend and backend servers

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Project paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo -e "${BLUE}🚀 Starting AI-CAD Development Servers${NC}"

# Function to check if port is in use
port_in_use() {
    ss -tln 2>/dev/null | grep -q ":$1 "
}

# Stop any existing processes
echo "Stopping existing processes..."
pkill -f "python.*src.main" 2>/dev/null || true
pkill -f "next.*dev" 2>/dev/null || true
sleep 2

# Start Backend
echo "Starting backend..."
cd "$BACKEND_DIR"
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

# Create .env if missing
if [ ! -f ".env" ]; then
    cat > .env << EOF
DEBUG=true
LOG_LEVEL=INFO
PORT=8100
OUTPUT_DIRECTORY=./outputs
DXF_VERSION=R2010
UNITS=Meters
EOF
fi

mkdir -p outputs

# Start backend in background
PYTHONPATH="$BACKEND_DIR/src" python -m src.main &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3
if ! ps -p $BACKEND_PID > /dev/null; then
    echo -e "${RED}❌ Backend failed to start${NC}"
    exit 1
fi

# Start Frontend
echo "Starting frontend..."
cd "$FRONTEND_DIR"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install --legacy-peer-deps > /dev/null 2>&1
fi

# Create .env.local if missing
if [ ! -f ".env.local" ]; then
    cat > .env.local << EOF
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8100
NODE_ENV=development
NEXT_PUBLIC_DEV_MODE=true
EOF
fi

# Start frontend in background
npm run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Wait for frontend to start
sleep 5

# Check if both are running
echo ""
echo -e "${BLUE}🔍 Checking server status...${NC}"

# Check backend
if port_in_use 8100; then
    echo -e "${GREEN}✅ Backend running on http://localhost:8100${NC}"
else
    echo -e "${RED}❌ Backend not running${NC}"
fi

# Check frontend (try both ports)
if port_in_use 3000; then
    echo -e "${GREEN}✅ Frontend running on http://localhost:3000${NC}"
    FRONTEND_URL="http://localhost:3000"
elif port_in_use 3001; then
    echo -e "${GREEN}✅ Frontend running on http://localhost:3001${NC}"
    FRONTEND_URL="http://localhost:3001"
else
    echo -e "${RED}❌ Frontend not running${NC}"
fi

# Show access URLs
echo ""
echo -e "${GREEN}🎉 AI-CAD is ready!${NC}"
echo -e "🌐 Frontend: ${FRONTEND_URL:-'Not running'}"
echo -e "🔧 Backend API: http://localhost:8100"
echo -e "📚 API Documentation: http://localhost:8100/docs"
if [ -n "$FRONTEND_URL" ]; then
    echo -e "🧪 API Test: $FRONTEND_URL/api-test"
fi

echo ""
echo "Press Ctrl+C to stop all servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${BLUE}🛑 Stopping servers...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM

# Keep script running
wait