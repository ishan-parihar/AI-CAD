#!/bin/bash

# AI-CAD Development Server Launcher
# This script starts both frontend and backend services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# PID files for background processes
BACKEND_PID_FILE="$PROJECT_ROOT/.backend.pid"
FRONTEND_PID_FILE="$PROJECT_ROOT/.frontend.pid"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[AI-CAD]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if port is in use
check_port() {
    local port=$1
    if ss -tlnp 2>/dev/null | grep -q ":$port "; then
        return 0  # Port is in use
    else
        return 1  # Port is available
    fi
}

# Function to stop existing servers
stop_servers() {
    print_status "Stopping existing servers..."
    
    # Stop backend if running
    if [ -f "$BACKEND_PID_FILE" ]; then
        local backend_pid=$(cat "$BACKEND_PID_FILE")
        if ps -p $backend_pid > /dev/null 2>&1; then
            print_status "Stopping backend server (PID: $backend_pid)"
            kill $backend_pid 2>/dev/null || true
            sleep 2
        fi
        rm -f "$BACKEND_PID_FILE"
    fi
    
    # Stop frontend if running
    if [ -f "$FRONTEND_PID_FILE" ]; then
        local frontend_pid=$(cat "$FRONTEND_PID_FILE")
        if ps -p $frontend_pid > /dev/null 2>&1; then
            print_status "Stopping frontend server (PID: $frontend_pid)"
            kill $frontend_pid 2>/dev/null || true
            sleep 2
        fi
        rm -f "$FRONTEND_PID_FILE"
    fi
    
    # Kill any remaining processes on ports 8100 and 3001
    if check_port 8100; then
        print_warning "Port 8100 is still in use, killing process..."
        lsof -ti:8100 | xargs kill -9 2>/dev/null || true
    fi
    
    if check_port 3001; then
        print_warning "Port 3001 is still in use, killing process..."
        lsof -ti:3001 | xargs kill -9 2>/dev/null || true
    fi
    
    if check_port 3000; then
        print_warning "Port 3000 is still in use, killing process..."
        lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    fi
    
    # Clean Next.js lock files
    rm -f "$FRONTEND_DIR/.next/dev/lock" 2>/dev/null || true
    rm -f "$FRONTEND_DIR/.next/build/lock" 2>/dev/null || true
}

# Function to setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd "$BACKEND_DIR"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    print_status "Installing backend dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt >/dev/null 2>&1 || {
        print_error "Failed to install backend dependencies"
        exit 1
    }
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating backend .env file..."
        cat > .env << EOF
# AI-CAD Backend Environment
DEBUG=true
LOG_LEVEL=INFO
PORT=8100
OUTPUT_DIRECTORY=./outputs
MAX_FILE_SIZE=104857600
DXF_VERSION=R2010
UNITS=Meters

# AI Configuration (add your API keys here)
# BASE_URL=https://api.openai.com/v1
# API_KEY=your_openai_api_key_here
# MODEL_NAME=gpt-4

# Database (optional)
# DATABASE_URL=sqlite:///./aicad.db

# Redis (optional)
# REDIS_URL=redis://localhost:6379
EOF
    fi
    
    # Ensure output directory exists
    mkdir -p outputs
    
    print_success "Backend setup complete"
}

# Function to setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd "$FRONTEND_DIR"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install --legacy-peer-deps >/dev/null 2>&1 || {
            print_error "Failed to install frontend dependencies"
            exit 1
        }
    fi
    
    # Create .env.local file if it doesn't exist
    if [ ! -f ".env.local" ]; then
        print_status "Creating frontend .env.local file..."
        cat > .env.local << EOF
# AI-CAD Frontend Environment
NEXT_PUBLIC_APP_URL=http://localhost:3001
NEXT_PUBLIC_API_URL=http://localhost:8100
NODE_ENV=development
NEXT_PUBLIC_DEV_MODE=true
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_3D_VIEWER=true
NEXT_PUBLIC_ENABLE_COLLABORATION=false
NEXT_PUBLIC_API_TIMEOUT=30000
NEXT_PUBLIC_WS_URL=ws://localhost:8100/ws
EOF
    fi
    
    print_success "Frontend setup complete"
}

# Function to start backend
start_backend() {
    print_status "Starting backend server..."
    
    cd "$BACKEND_DIR"
    
    # Check if port 8100 is available
    if check_port 8100; then
        print_warning "Port 8100 is already in use"
        return 1
    fi
    
    # Start backend in background
    cd "$BACKEND_DIR"
    source venv/bin/activate && PYTHONPATH="$BACKEND_DIR/src" python -m src.main > "$PROJECT_ROOT/backend.log" 2>&1 &
    local backend_pid=$!
    echo $backend_pid > "$BACKEND_PID_FILE"
    
    # Wait for backend to start
    sleep 3
    
    # Check if backend is running
    if ps -p $backend_pid > /dev/null 2>&1; then
        print_success "Backend server started (PID: $backend_pid)"
        print_status "Backend URL: http://localhost:8100"
        print_status "Backend API docs: http://localhost:8100/docs"
        return 0
    else
        print_error "Failed to start backend server"
        print_status "Check backend logs: $PROJECT_ROOT/backend.log"
        return 1
    fi
}

# Function to start frontend
start_frontend() {
    print_status "Starting frontend server..."
    
    cd "$FRONTEND_DIR"
    
    # Check if port 3001 is available
    if check_port 3001; then
        print_warning "Port 3001 is already in use"
        return 1
    fi
    
    # Start frontend in background
    npm run dev > "$PROJECT_ROOT/frontend.log" 2>&1 &
    local frontend_pid=$!
    echo $frontend_pid > "$FRONTEND_PID_FILE"
    
    # Wait for frontend to start
    sleep 5
    
    # Check if frontend is running
    if ps -p $frontend_pid > /dev/null 2>&1; then
        print_success "Frontend server started (PID: $frontend_pid)"
        print_status "Frontend URL: http://localhost:3001"
        return 0
    else
        print_error "Failed to start frontend server"
        print_status "Check frontend logs: $PROJECT_ROOT/frontend.log"
        return 1
    fi
}

# Function to show logs
show_logs() {
    print_status "Showing logs (Ctrl+C to exit)..."
    
    if [ -f "$PROJECT_ROOT/backend.log" ]; then
        echo -e "\n${BLUE}=== BACKEND LOGS ===${NC}"
        tail -f "$PROJECT_ROOT/backend.log" &
        local log_pid=$!
    fi
    
    if [ -f "$PROJECT_ROOT/frontend.log" ]; then
        echo -e "\n${BLUE}=== FRONTEND LOGS ===${NC}"
        tail -f "$PROJECT_ROOT/frontend.log" &
        local log_pid2=$!
    fi
    
    # Wait for user to interrupt
    trap "kill $log_pid $log_pid2 2>/dev/null; exit 0" INT
    wait
}

# Function to check server status
check_status() {
    print_status "Checking server status..."
    
    echo -e "\n${BLUE}=== SERVER STATUS ===${NC}"
    
    # Check backend
    local backend_running=false
    if check_port 8100; then
        backend_running=true
        echo -e "Backend: ${GREEN}RUNNING${NC}"
        echo -e "Backend API: ${GREEN}http://localhost:8100${NC}"
        echo -e "API Docs: ${GREEN}http://localhost:8100/docs${NC}"
    else
        echo -e "Backend: ${RED}STOPPED${NC}"
    fi
    
    # Check frontend (both possible ports)
    local frontend_running=false
    local frontend_port=""
    
    if check_port 3001; then
        frontend_running=true
        frontend_port="3001"
    elif check_port 3000; then
        frontend_running=true
        frontend_port="3000"
    fi
    
    if $frontend_running; then
        echo -e "Frontend: ${GREEN}RUNNING${NC}"
        echo -e "Frontend App: ${GREEN}http://localhost:$frontend_port${NC}"
    else
        echo -e "Frontend: ${RED}STOPPED${NC}"
    fi
    
    # Show quick access URLs
    if $backend_running && $frontend_running; then
        echo ""
        echo -e "${BLUE}=== QUICK ACCESS ===${NC}"
        echo -e "🌐 Frontend: ${GREEN}http://localhost:$frontend_port${NC}"
        echo -e "🔧 Backend API: ${GREEN}http://localhost:8100${NC}"
        echo -e "📚 API Docs: ${GREEN}http://localhost:8100/docs${NC}"
        if [ "$frontend_port" = "3001" ]; then
            echo -e "🧪 API Test: ${GREEN}http://localhost:$frontend_port/api-test${NC}"
        fi
    fi
    
    echo ""
}

# Function to show help
show_help() {
    echo -e "${BLUE}AI-CAD Development Server${NC}"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start both frontend and backend servers"
    echo "  stop      Stop all running servers"
    echo "  restart   Restart all servers"
    echo "  status    Check server status"
    echo "  logs      Show server logs"
    echo "  setup     Setup dependencies and configuration"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start      # Start both servers"
    echo "  $0 status     # Check if servers are running"
    echo "  $0 logs       # View logs"
    echo "  $0 stop       # Stop all servers"
    echo ""
}

# Main script logic
case "${1:-start}" in
    "start")
        print_status "Starting AI-CAD development servers..."
        stop_servers
        
        if ! setup_backend; then
            print_error "Backend setup failed"
            exit 1
        fi
        
        if ! setup_frontend; then
            print_error "Frontend setup failed"
            exit 1
        fi
        
        if ! start_backend; then
            print_error "Failed to start backend"
            exit 1
        fi
        
        if ! start_frontend; then
            print_error "Failed to start frontend"
            exit 1
        fi
        
        echo ""
        print_success "🎉 AI-CAD is now running!"
        echo ""
        echo -e "${GREEN}Frontend:${NC} http://localhost:3001"
        echo -e "${GREEN}Backend API:${NC} http://localhost:8100"
        echo -e "${GREEN}API Documentation:${NC} http://localhost:8100/docs"
        echo -e "${GREEN}API Test:${NC} http://localhost:3001/api-test"
        echo ""
        echo -e "${BLUE}Useful commands:${NC}"
        echo "  $0 status    # Check server status"
        echo "  $0 logs      # View logs"
        echo "  $0 stop      # Stop servers"
        echo ""
        ;;
    
    "stop")
        stop_servers
        print_success "All servers stopped"
        ;;
    
    "restart")
        stop_servers
        sleep 2
        exec "$0" start
        ;;
    
    "status")
        check_status
        ;;
    
    "logs")
        show_logs
        ;;
    
    "setup")
        print_status "Setting up AI-CAD development environment..."
        setup_backend
        setup_frontend
        print_success "Setup complete! Run '$0 start' to start the servers."
        ;;
    
    "help"|"-h"|"--help")
        show_help
        ;;
    
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac