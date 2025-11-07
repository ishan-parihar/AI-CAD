# AI-CAD Development Server Launcher

A comprehensive bash script to manage the AI-CAD frontend and backend development servers.

## Quick Start

```bash
# Make executable (one time)
chmod +x start.sh

# Start both servers
./start.sh start

# Check status
./start.sh status

# View logs
./start.sh logs

# Stop servers
./start.sh stop
```

## Commands

| Command | Description |
|---------|-------------|
| `start` | Start both frontend and backend servers |
| `stop` | Stop all running servers |
| `restart` | Restart all servers |
| `status` | Check server status and URLs |
| `logs` | Show live logs from both servers |
| `setup` | Install dependencies and create config files |
| `help` | Show help message |

## Features

- ✅ **Automatic Setup**: Installs dependencies and creates environment files
- ✅ **Port Management**: Handles port conflicts and cleanup
- ✅ **Process Management**: Tracks PIDs and graceful shutdown
- ✅ **Log Management**: Centralized logging with timestamps
- ✅ **Status Monitoring**: Real-time server status checks
- ✅ **Error Handling**: Comprehensive error detection and reporting

## URLs After Starting

- **Frontend App**: http://localhost:3001
- **Backend API**: http://localhost:8100
- **API Documentation**: http://localhost:8100/docs
- **API Test Page**: http://localhost:3001/api-test

## Environment Files

The script automatically creates:

### Backend (.env)
```bash
DEBUG=true
LOG_LEVEL=INFO
PORT=8100
OUTPUT_DIRECTORY=./outputs
# Add your OpenAI API key here
# API_KEY=your_openai_api_key_here
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_APP_URL=http://localhost:3001
NEXT_PUBLIC_API_URL=http://localhost:8100
NODE_ENV=development
```

## Usage Examples

```bash
# First time setup
./start.sh setup
./start.sh start

# Daily development workflow
./start.sh start
# ... work on the app ...
./start.sh stop

# Check if servers are running
./start.sh status

# Monitor logs
./start.sh logs
```

## Troubleshooting

### Port Conflicts
The script automatically detects and resolves port conflicts on 8100 and 3001.

### Dependencies
If you encounter dependency issues:
```bash
./start.sh stop
./start.sh setup
./start.sh start
```

### Logs
Check the logs for detailed error information:
```bash
./start.sh logs
```

## Process Management

The script tracks processes using PID files:
- `.backend.pid` - Backend server process ID
- `.frontend.pid` - Frontend server process ID
- `backend.log` - Backend server logs
- `frontend.log` - Frontend server logs