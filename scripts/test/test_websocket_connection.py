#!/usr/bin/env python3

import asyncio
import websockets
import json
import sys

async def test_websocket_connection():
    """Test WebSocket connection to the backend"""
    plan_id = "471bfe76-0102-4317-ad0b-8634d75cec43"  # Real plan ID from logs
    uri = f"ws://localhost:8100/ws/plans/{plan_id}"
    
    try:
        print(f"Connecting to WebSocket: {uri}")
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Send subscription message
            subscribe_msg = {
                "type": "subscribe_updates"
            }
            await websocket.send(json.dumps(subscribe_msg))
            print(f"📤 Sent: {subscribe_msg}")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 Received: {response}")
                
                try:
                    data = json.loads(response)
                    print(f"✅ Parsed JSON: {data}")
                except json.JSONDecodeError as e:
                    print(f"⚠️  JSON parse error: {e}")
                    
            except asyncio.TimeoutError:
                print("⚠️  Timeout waiting for response")
            
            # Send ping
            ping_msg = {"type": "ping"}
            await websocket.send(json.dumps(ping_msg))
            print(f"📤 Sent ping: {ping_msg}")
            
            print("✅ WebSocket test completed successfully!")
            return True
            
    except websockets.exceptions.ConnectionRefusedError:
        print("❌ Connection refused - server may not be running")
        return False
    except websockets.exceptions.ConnectionClosed:
        print("❌ Connection closed")
        return False
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        return False

async def test_http_endpoints():
    """Test HTTP endpoints first"""
    import aiohttp
    
    base_url = "http://localhost:8100"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test health endpoint
            async with session.get(f"{base_url}/api/v1/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check: {data}")
                else:
                    print(f"❌ Health check failed: {response.status}")
                    return False
            
            # Test AI config endpoint
            async with session.get(f"{base_url}/api/v1/settings/ai-config") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ AI Config: {data}")
                else:
                    print(f"❌ AI Config failed: {response.status}")
                    return False
            
            return True
            
    except Exception as e:
        print(f"❌ HTTP test error: {e}")
        return False

async def main():
    """Main test function"""
    print("🧪 Testing AI-CAD Backend WebSocket Connection")
    print("=" * 50)
    
    # Test HTTP endpoints first
    print("1. Testing HTTP endpoints...")
    http_ok = await test_http_endpoints()
    
    if not http_ok:
        print("❌ HTTP endpoints failed - server may not be running")
        sys.exit(1)
    
    print("\n2. Testing WebSocket connection...")
    ws_ok = await test_websocket_connection()
    
    if ws_ok:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ WebSocket test failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())