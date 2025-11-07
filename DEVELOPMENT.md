# 🚀 AI-CAD Development Launcher

## Quick Start

The AI-CAD development environment is now fully integrated and ready to use!

### Method 1: Simple Launcher (Recommended)
```bash
# Start both servers interactively
./run.sh

# Press Ctrl+C to stop both servers
```

### Method 2: Advanced Launcher
```bash
# Start servers in background
./start.sh start

# Check status
./start.sh status

# View logs
./start.sh logs

# Stop servers
./start.sh stop
```

## 🌐 Access URLs

Once running, you can access:

- **🏠 Frontend App**: http://localhost:3001
- **🔧 Backend API**: http://localhost:8100  
- **📚 API Documentation**: http://localhost:8100/docs
- **🧪 API Test Page**: http://localhost:3001/api-test

## ✅ Features

### ✅ Completed Integration
- **Next.js 16** frontend with latest packages
- **FastAPI** backend with CORS configured
- **Real-time API connection** between frontend and backend
- **Auto-dependency installation** for both environments
- **Process management** with graceful startup/shutdown
- **Port conflict resolution** (3001 for frontend, 8100 for backend)
- **Environment configuration** automatically created

### 🔧 Available Features
1. **Plan Generation**: Create floor plans with AI assistance
2. **Real-time Status**: Track plan generation progress
3. **DXF Export**: Download generated CAD files
4. **API Testing**: Built-in connection test page
5. **Interactive Documentation**: Auto-generated API docs

## 🛠️ Development Workflow

### Daily Usage
```bash
# Start development servers
./run.sh

# Work on your app...
# - Frontend: http://localhost:3001
# - Backend: http://localhost:8100/docs

# Stop when done (Ctrl+C)
```

### First Time Setup
```bash
# The scripts handle all setup automatically:
# - Python virtual environment
# - Node.js dependencies  
# - Environment configuration
# - Output directories

# Just run and start developing!
./run.sh
```

## 📁 Project Structure

```
AI-CAD/
├── run.sh              # Simple launcher (recommended)
├── start.sh            # Advanced launcher with background mode
├── test-servers.sh     # Server connectivity test
├── frontend/           # Next.js 16 frontend
│   ├── src/
│   │   ├── app/        # App Router pages
│   │   ├── components/ # React components
│   │   ├── lib/        # API client & utilities
│   │   └── types/      # TypeScript definitions
│   └── .env.local      # Frontend environment (auto-created)
└── backend/            # FastAPI backend
    ├── src/
    │   ├── main.py     # FastAPI application
    │   ├── cad/        # DXF generation engine
    │   ├── ai_agent/   # AI integration
    │   └── tools/      # Spatial reasoning tools
    ├── .env            # Backend environment (auto-created)
    └── outputs/        # Generated DXF files
```

## 🎯 Next Development Steps

Now that the integration is complete, you can:

1. **Build Features**: Create plan generation UI, CAD viewers, dashboards
2. **Add Authentication**: Implement user management
3. **Enhance AI**: Add more sophisticated design rules
4. **Deploy**: Prepare for production deployment

## 🐛 Troubleshooting

### Port Conflicts
The scripts automatically handle port conflicts. If issues persist:
```bash
# Kill all related processes
pkill -f "python.*src.main"
pkill -f "next.*dev"

# Restart
./run.sh
```

### Dependencies
If you encounter dependency issues:
```bash
# Clean install
rm -rf frontend/node_modules backend/venv
./run.sh  # Will reinstall everything
```

### Logs
Check the logs for detailed error information:
```bash
# With advanced launcher
./start.sh logs

# Or check log files directly
tail -f backend.log frontend.log
```

## 🎉 Ready to Build!

Your AI-CAD development environment is now fully operational. The frontend and backend are seamlessly integrated and ready for building the next generation of AI-powered architectural design tools!

**Start building**: `./run.sh` then visit http://localhost:3001