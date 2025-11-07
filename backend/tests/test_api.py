#!/usr/bin/env python3
"""Simple test script for FastAPI endpoints"""

import asyncio
import aiohttp
import json


async def test_api_endpoints():
    """Test API endpoints"""
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        print("Testing AI-CAD API Endpoints\n")
        
        # Test health check
        print("1. Testing health check...")
        async with session.get(f"{base_url}/api/v1/health") as response:
            if response.status == 200:
                data = await response.json()
                print(f"   ✅ Health check: {data}")
            else:
                print(f"   ❌ Health check failed: {response.status}")
                return
        
        # Test tools listing
        print("\n2. Testing tools listing...")
        async with session.get(f"{base_url}/api/v1/tools") as response:
            if response.status == 200:
                data = await response.json()
                tools = data.get("tools", [])
                print(f"   ✅ Found {len(tools)} tools:")
                for tool in tools[:3]:  # Show first 3 tools
                    print(f"      - {tool['name']}: {tool['description']}")
                if len(tools) > 3:
                    print(f"      ... and {len(tools) - 3} more")
            else:
                print(f"   ❌ Tools listing failed: {response.status}")
        
        # Test plan generation
        print("\n3. Testing plan generation...")
        plan_request = {
            "name": "Test Apartment",
            "dimensions": {"width": 10.0, "height": 8.0},
            "rooms": [
                {"type": "living_room", "area": 20.0, "adjacency": ["kitchen"]},
                {"type": "kitchen", "area": 12.0, "adjacency": ["living_room", "bedroom"]},
                {"type": "bedroom", "area": 15.0, "adjacency": ["kitchen"]},
                {"type": "bathroom", "area": 6.0}
            ],
            "building_type": "residential"
        }
        
        async with session.post(
            f"{base_url}/api/v1/plans/generate",
            json=plan_request
        ) as response:
            if response.status == 200:
                data = await response.json()
                plan_id = data.get("plan_id")
                print(f"   ✅ Plan generation started: {plan_id}")
                
                # Poll for completion
                print("\n4. Polling for plan completion...")
                for i in range(30):  # Poll for 30 seconds
                    await asyncio.sleep(1)
                    
                    async with session.get(
                        f"{base_url}/api/v1/plans/{plan_id}/status"
                    ) as status_response:
                        if status_response.status == 200:
                            status_data = await status_response.json()
                            status = status_data.get("status")
                            progress = status_data.get("progress", 0)
                            
                            print(f"   Progress: {progress}% - Status: {status}")
                            
                            if status == "completed":
                                print(f"   ✅ Plan completed successfully!")
                                
                                # Get plan details
                                async with session.get(
                                    f"{base_url}/api/v1/plans/{plan_id}/preview"
                                ) as preview_response:
                                    if preview_response.status == 200:
                                        preview_data = await preview_response.json()
                                        summary = preview_data.get("summary", {})
                                        print(f"   Summary: {summary}")
                                
                                break
                            elif status == "failed":
                                error = status_data.get("error", "Unknown error")
                                print(f"   ❌ Plan generation failed: {error}")
                                break
                        else:
                            print(f"   ❌ Status check failed: {status_response.status}")
                            break
                else:
                    print("   ⏰ Plan generation timed out")
                    
            else:
                error_data = await response.json()
                print(f"   ❌ Plan generation failed: {error_data}")
        
        # Test plans listing
        print("\n5. Testing plans listing...")
        async with session.get(f"{base_url}/api/v1/plans") as response:
            if response.status == 200:
                data = await response.json()
                plans = data.get("plans", [])
                print(f"   ✅ Found {len(plans)} plans:")
                for plan in plans:
                    print(f"      - {plan['name']} ({plan['status']})")
            else:
                print(f"   ❌ Plans listing failed: {response.status}")
        
        print("\n✅ All API tests completed!")


if __name__ == "__main__":
    print("Starting API tests...")
    print("Make sure the API server is running: python -m uvicorn src.main:app --reload")
    
    try:
        asyncio.run(test_api_endpoints())
    except KeyboardInterrupt:
        print("\nTests interrupted")
    except Exception as e:
        print(f"\nTests failed: {e}")