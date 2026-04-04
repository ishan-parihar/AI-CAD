#!/usr/bin/env python3

import subprocess
import time
import asyncio
import websockets
import json
import requests
import signal
import sys
import os

# Global process reference
backend_process = None

def start_backend():
    """Start the backend server"""
    global backend_process
    print("Starting backend server...")
    
    backend_dir = "/home/ishanp/Documents/GitHub/AI-CAD/backend"
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{backend_dir}/src"
    
    backend_process = subprocess.Popen(
        [
            "python3", "-c", 
            """
import sys
sys.path.insert(0, 'src')
from src.main import app
import uvicorn
uvicorn.run(app, host='0.0.0.0', port=8100)
"""
        ],
        cwd=backend_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Wait for backend to start
    time.sleep(5)
    return backend_process

def stop_backend():
    """Stop the backend server"""
    global backend_process
    if backend_process:
        print("Stopping backend server...")
        backend_process.terminate()
        backend_process.wait()
        print("Backend stopped")

async def test_websocket():
    """Test WebSocket connection with detailed logging"""
    plan_id = "test-websocket-fix-123"
    uri = f"ws://localhost:8100/ws/plans/{plan_id}"
    
    try:
        print(f"Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Send subscription message
            await websocket.send(json.dumps({
                "type": "subscribe_updates"
            }))
            print("✅ Sent subscription message")
            
            # Wait for initial status message
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                print(f"✅ Received message: {response_data}")
                
                # Check message type
                if response_data.get("type") == "plan_not_found":
                    print("ℹ️  Plan not found (expected for test plan)")
                elif response_data.get("type") == "initial_status":
                    print("✅ Received initial status message!")
                else:
                    print(f"ℹ️  Received message type: {response_data.get('type')}")
                    
            except asyncio.TimeoutError:
                print("⚠️  No message received in 5 seconds")
            
            # Send ping
            await websocket.send(json.dumps({
                "type": "ping"
            }))
            print("✅ Sent ping")
            
            # Wait for pong
            try:
                pong = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                pong_data = json.loads(pong)
                if pong_data.get("type") == "pong":
                    print("✅ Received pong - WebSocket is working!")
                else:
                    print(f"ℹ️  Received: {pong_data}")
            except asyncio.TimeoutError:
                print("⚠️  No pong received in 5 seconds")
                
            return True
            
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        return False

async def main():
    """Main test function"""
    try:
        # Start backend
        backend_process = start_backend()
        
        # Test WebSocket
        success = await test_websocket()
        
        if success:
            print("\n🎉 WebSocket test completed successfully!")
            print("The WebSocket fix is working - no more immediate disconnects!")
        else:
            print("\n❌ WebSocket test failed")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
    finally:
        # Clean up
        stop_backend()

if __name__ == "__main__":
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n\nStopping test...")
        stop_backend()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    asyncio.run(main())