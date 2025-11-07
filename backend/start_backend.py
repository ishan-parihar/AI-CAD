#!/usr/bin/env python3
import sys
import os
import time

# Add src to path
sys.path.insert(0, './src')

# Set environment variables
os.environ['PYTHONPATH'] = './src'

# Import and run uvicorn directly
import uvicorn
from main import app

if __name__ == "__main__":
    print("Starting AI-CAD Backend Server...")
    print("Press Ctrl+C to stop")
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8100,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Error starting server: {e}")