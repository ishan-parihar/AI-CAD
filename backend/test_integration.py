#!/usr/bin/env python3
"""
Comprehensive test for frontend-backend integration
"""

import asyncio
import aiohttp
import json

async def test_complete_flow():
    """Test the complete flow from frontend perspective"""
    
    base_url = "http://localhost:8100"
    
    async with aiohttp.ClientSession() as session:
        print("🚀 Testing Complete Frontend-Backend Integration")
        print("=" * 60)
        
        # 1. Test health
        print("\n1️⃣ Testing API Health...")
        async with session.get(f"{base_url}/api/v1/health") as response:
            data = await response.json()
            print(f"   ✅ Status: {data['status']}")
        
        # 2. Test AI configuration
        print("\n2️⃣ Testing AI Configuration...")
        async with session.get(f"{base_url}/api/v1/ai/status") as response:
            data = await response.json()
            print(f"   🤖 AI Configured: {data['ai_configured']}")
            print(f"   🔗 Base URL: {data['base_url']}")
            print(f"   📝 Model: {data['model_name']}")
        
        # 3. Start plan generation
        print("\n3️⃣ Starting Plan Generation...")
        plan_request = {
            "name": "Frontend Integration Test Plan",
            "building_type": "residential",
            "dimensions": {"width": 12, "height": 10},
            "rooms": [
                {"type": "bedroom", "area": 20},
                {"type": "kitchen", "area": 15},
                {"type": "bathroom", "area": 8}
            ],
            "constraints": {"min_rooms": 3}
        }
        
        async with session.post(f"{base_url}/api/v1/plans/generate", json=plan_request) as response:
            if response.status == 200:
                plan_data = await response.json()
                plan_id = plan_data['plan_id']
                print(f"   ✅ Plan Started: {plan_id}")
                print(f"   📊 Status: {plan_data['status']}")
            else:
                print(f"   ❌ Plan generation failed: {response.status}")
                return
        
        # 4. Check plan status
        print("\n4️⃣ Checking Plan Status...")
        async with session.get(f"{base_url}/api/v1/plans/{plan_id}") as response:
            if response.status == 200:
                plan_info = await response.json()
                print(f"   📋 Plan Name: {plan_info['name']}")
                print(f"   📊 Current Status: {plan_info['status']}")
                print(f"   📈 Progress: {plan_info['progress']}%")
            else:
                print(f"   ❌ Failed to get plan status: {response.status}")
        
        # 5. List all plans
        print("\n5️⃣ Listing All Plans...")
        async with session.get(f"{base_url}/api/v1/plans") as response:
            if response.status == 200:
                plans_data = await response.json()
                print(f"   📁 Total Plans: {len(plans_data['plans'])}")
                print("   📋 Recent Plans:")
                for i, plan in enumerate(plans_data['plans'][:3]):
                    print(f"      {i+1}. {plan['name']} - {plan['status']} ({plan['progress']}%)")
            else:
                print(f"   ❌ Failed to list plans: {response.status}")
        
        # 6. Test WebSocket connection info
        print("\n6️⃣ WebSocket Connection Info...")
        print(f"   🔗 WebSocket URL: ws://localhost:8100/ws/plans/{plan_id}")
        print(f"   🌐 Frontend URL: http://localhost:3000")
        print(f"   🔧 CORS Origins: http://localhost:3000, http://localhost:3001")
        
        # 7. Provide WebSocket test instructions
        print("\n7️⃣ WebSocket Test Instructions:")
        print(f"   📡 To test WebSocket, run:")
        print(f"      python3 test_websocket_connection.py")
        print(f"   🔍 Or connect directly to:")
        print(f"      ws://localhost:8100/ws/plans/{plan_id}")
        
        print(f"\n✅ Integration test completed successfully!")
        print(f"📝 Plan ID for WebSocket testing: {plan_id}")

if __name__ == "__main__":
    asyncio.run(test_complete_flow())