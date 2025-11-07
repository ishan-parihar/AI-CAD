#!/usr/bin/env python3
"""
Test WebSocket connection from frontend perspective
"""

import asyncio
import websockets
import json

async def test_frontend_websocket():
    """Test WebSocket connection as if coming from frontend"""
    
    # Test multiple plan IDs to see if any work
    test_plan_ids = [
        "test-plan-123",
        "frontend-test-456", 
        "new-plan-789"
    ]
    
    for plan_id in test_plan_ids:
        print(f"\n🔍 Testing plan ID: {plan_id}")
        
        # WebSocket URL (same as frontend would construct)
        ws_url = f"ws://localhost:8100/ws/plans/{plan_id}"
        
        try:
            print(f"   Connecting to {ws_url}...")
            async with websockets.connect(ws_url) as websocket:
                print("   ✅ Connection established!")
                
                # Send subscription message (like frontend)
                subscribe_msg = {"type": "subscribe_updates"}
                await websocket.send(json.dumps(subscribe_msg))
                print(f"   📤 Sent subscription: {subscribe_msg}")
                
                # Wait for initial response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(response)
                    print(f"   📥 Received: {data}")
                    
                    if data.get("type") == "connection_established":
                        print("   ✅ Connection properly established!")
                        
                        # Test with a new plan generation
                        print("   🚀 Testing plan generation...")
                        test_msg = {"type": "generate_plan", "data": {
                            "name": f"Frontend Test Plan {plan_id}",
                            "building_type": "residential",
                            "dimensions": {"width": 10, "height": 8},
                            "rooms": [{"type": "bedroom", "area": 15}],
                            "constraints": {}
                        }}
                        await websocket.send(json.dumps(test_msg))
                        
                        # Listen for a few responses
                        for i in range(5):
                            try:
                                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                                data = json.loads(response)
                                print(f"   📥 Response {i+1}: {data.get('type', 'unknown')} - {data.get('message', '')}")
                            except asyncio.TimeoutError:
                                print("   ⏰ Timeout waiting for response")
                                break
                    
                except asyncio.TimeoutError:
                    print("   ⏰ No response received within 2 seconds")
                
        except websockets.ConnectionClosed as e:
            print(f"   ❌ Connection closed: {e}")
        except ConnectionRefusedError:
            print("   ❌ Connection refused - backend not running")
        except Exception as e:
            print(f"   ❌ Error: {e}")

async def test_plan_generation_api():
    """Test the plan generation API endpoint"""
    
    import aiohttp
    
    url = "http://localhost:8100/api/v1/plans/generate"
    data = {
        "name": "Frontend WebSocket Test Plan",
        "building_type": "residential",
        "dimensions": {"width": 10, "height": 8},
        "rooms": [{"type": "bedroom", "area": 15}],
        "constraints": {}
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"\n✅ Plan generation started!")
                    print(f"   Plan ID: {result.get('plan_id')}")
                    print(f"   Status: {result.get('status')}")
                    return result.get('plan_id')
                else:
                    print(f"\n❌ Plan generation failed: {response.status}")
                    return None
                    
    except Exception as e:
        print(f"\n❌ API request failed: {e}")
        return None

async def main():
    """Main test function"""
    
    print("🧪 Frontend WebSocket Connection Test")
    print("=" * 50)
    
    # First test plan generation to get a real plan ID
    plan_id = await test_plan_generation_api()
    
    if plan_id:
        print(f"\n🔍 Now testing WebSocket with real plan ID: {plan_id}")
        ws_url = f"ws://localhost:8100/ws/plans/{plan_id}"
        
        try:
            async with websockets.connect(ws_url) as websocket:
                print("✅ WebSocket connected to real plan!")
                
                # Subscribe to updates
                await websocket.send(json.dumps({"type": "subscribe_updates"}))
                
                # Listen for updates
                print("📡 Listening for plan updates...")
                for i in range(10):
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                        data = json.loads(response)
                        print(f"📥 Update {i+1}: {data.get('type', 'unknown')} - Status: {data.get('status', 'N/A')} - Progress: {data.get('progress', 0)}%")
                        
                        if data.get('status') == 'completed':
                            print("🎉 Plan generation completed!")
                            break
                        elif data.get('status') == 'error':
                            print(f"❌ Plan generation failed: {data.get('message', 'Unknown error')}")
                            break
                            
                    except asyncio.TimeoutError:
                        print("⏰ Timeout - checking if plan is complete...")
                        break
                        
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
    
    # Test with some common plan IDs
    print("\n🔍 Testing with common plan IDs...")
    await test_frontend_websocket()

if __name__ == "__main__":
    asyncio.run(main())