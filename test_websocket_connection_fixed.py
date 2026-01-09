#!/usr/bin/env python3
"""
Test WebSocket connection to the backend with the correct plan ID
"""
import asyncio
import websockets
import json

async def test_websocket():
    plan_id = "471bfe76-0102-4317-ad0b-8634d75cec43"
    uri = f"ws://localhost:8000/ws/plans/{plan_id}"
    
    print(f"Testing WebSocket connection to: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Send subscription message
            await websocket.send(json.dumps({
                "type": "subscribe_updates"
            }))
            print("📤 Sent subscription message")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"📥 Received: {data}")
                
                if data.get('type') == 'connection_established':
                    print("✅ Connection established successfully!")
                elif data.get('type') == 'initial_status':
                    print(f"📊 Plan status: {data.get('status')}")
                    print(f"📈 Progress: {data.get('progress', 0)}%")
                else:
                    print(f"🔍 Unknown message type: {data.get('type')}")
                    
            except asyncio.TimeoutError:
                print("⏰ Timeout waiting for response")
            
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_websocket())
    if success:
        print("\n🎉 WebSocket test completed successfully!")
    else:
        print("\n💥 WebSocket test failed!")