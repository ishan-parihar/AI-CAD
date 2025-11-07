#!/usr/bin/env python3
"""
Minimal test to isolate and fix the plan generation issue
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, './src')

async def test_plan_generation():
    """Test the plan generation with minimal requirements"""
    from main import FloorPlanRequest, RoomRequirement, generate_plan_background
    from main import active_plans
    
    # Create simple test request
    request = FloorPlanRequest(
        name='Minimal Test',
        building_type='residential',
        dimensions={'width': 8, 'height': 6},
        rooms=[
            RoomRequirement(type='living_room', area=12),
            RoomRequirement(type='bedroom', area=10)
        ],
        constraints={}
    )
    
    # Create plan entry manually
    import uuid
    from datetime import datetime
    plan_id = str(uuid.uuid4())
    
    active_plans[plan_id] = {
        "id": plan_id,
        "name": request.name,
        "status": "initializing",
        "created_at": datetime.now().isoformat(),
        "request": request.model_dump(),
        "progress": 0
    }
    
    print(f"Testing plan generation for: {plan_id}")
    
    try:
        # Run the background generation
        await generate_plan_background(plan_id, request)
        
        # Check result
        plan = active_plans.get(plan_id, {})
        print(f"Final status: {plan.get('status')}")
        print(f"Error: {plan.get('error')}")
        
        return plan.get('status') == 'completed'
        
    except Exception as e:
        print(f"Exception during generation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_plan_generation())
    if success:
        print("✅ Plan generation successful!")
    else:
        print("❌ Plan generation failed!")
    
    exit(0 if success else 1)