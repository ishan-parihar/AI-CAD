#!/usr/bin/env python3
"""
WebSocket test script for AI-CAD backend
"""

import asyncio
import websockets
import json
import sys

async def test_websocket_connection():
    """Test WebSocket connection to the backend"""
    
    # WebSocket URL
    ws_url = "ws://localhost:8100/ws/plans/test-plan-123"
    
    try:
        print(f"Connecting to {ws_url}...")
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Send subscription message
            subscribe_msg = {"type": "subscribe_updates"}
            await websocket.send(json.dumps(subscribe_msg))
            print(f"📤 Sent: {subscribe_msg}")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 Received: {response}")
            except asyncio.TimeoutError:
                print("⏰ No response received within 5 seconds")
            
            # Send ping
            ping_msg = {"type": "ping"}
            await websocket.send(json.dumps(ping_msg))
            print(f"📤 Sent ping: {ping_msg}")
            
    except websockets.ConnectionClosed as e:
        print(f"❌ WebSocket connection closed: {e}")
        return False
    except ConnectionRefusedError:
        print("❌ Connection refused - backend may not be running")
        return False
    except Exception as e:
        print(f"❌ WebSocket connection error: {e}")
        return False
    
    return True

async def test_http_endpoints():
    """Test HTTP endpoints to verify backend is running"""
    
    import aiohttp
    
    base_url = "http://localhost:8100"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test health endpoint
            async with session.get(f"{base_url}/api/v1/health") as response:
                if response.status == 200:
                    print("✅ HTTP health endpoint working")
                    data = await response.json()
                    print(f"📊 Health response: {data}")
                else:
                    print(f"❌ Health endpoint failed: {response.status}")
                    return False
            
            # Test plans endpoint
            async with session.get(f"{base_url}/api/v1/plans") as response:
                if response.status == 200:
                    print("✅ HTTP plans endpoint working")
                    data = await response.json()
                    print(f"📊 Plans count: {len(data.get('plans', []))}")
                else:
                    print(f"❌ Plans endpoint failed: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ HTTP endpoint error: {e}")
        return False
    
    return True

async def main():
    """Main test function"""
    
    print("🚀 Testing AI-CAD Backend Connectivity")
    print("=" * 50)
    
    # Test HTTP endpoints first
    print("\n1️⃣ Testing HTTP endpoints...")
    http_ok = await test_http_endpoints()
    
    if not http_ok:
        print("❌ HTTP endpoints not working - backend may not be running")
        sys.exit(1)
    
    # Test WebSocket connection
    print("\n2️⃣ Testing WebSocket connection...")
    ws_ok = await test_websocket_connection()
    
    if ws_ok:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ WebSocket test failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())