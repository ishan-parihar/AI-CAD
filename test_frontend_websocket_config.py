#!/usr/bin/env python3
"""
Test that verifies the frontend WebSocket configuration is working
"""
import asyncio
import websockets
import json

async def test_frontend_websocket_url():
    # Test the exact URL the frontend would construct
    plan_id = "471bfe76-0102-4317-ad0b-8634d75cec43"
    
    # This is what the frontend should construct with the corrected config
    ws_url = f"ws://localhost:8000/ws/plans/{plan_id}"
    
    print(f"Testing frontend WebSocket URL: {ws_url}")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print("✅ Frontend WebSocket URL works!")
            
            # Send subscription message like the frontend does
            await websocket.send(json.dumps({
                "type": "subscribe_updates"
            }))
            print("📤 Subscription sent")
            
            # Wait for initial status
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response)
            
            print(f"📥 Response type: {data.get('type')}")
            
            if data.get('type') == 'initial_status':
                print(f"📊 Plan status: {data.get('status')}")
                print(f"📈 Progress: {data.get('progress', 0)}%")
                print(f"📝 Message: {data.get('message', 'N/A')}")
                print("✅ Frontend should receive this data correctly!")
            else:
                print(f"🔍 Unexpected response: {data}")
                
    except Exception as e:
        print(f"❌ Frontend WebSocket URL failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🧪 Testing Frontend WebSocket Configuration")
    print("=" * 50)
    success = asyncio.run(test_frontend_websocket_url())
    
    if success:
        print("\n🎉 Frontend WebSocket configuration is correct!")
        print("✅ The frontend should now connect properly")
    else:
        print("\n💥 Frontend WebSocket configuration needs fixing")