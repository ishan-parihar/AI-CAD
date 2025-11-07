#!/usr/bin/env python3
"""
AI-CAD Backend Functionality Verification
Tests core functionality without requiring a running server
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test all core imports work"""
    print("🔍 Testing imports...")
    
    try:
        from src.cad.dxf_generator import DXFGenerator
        from src.tools import tool_registry
        from src.utils import get_logger, settings
        from src.main import app
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_dxf_generation():
    """Test DXF generation functionality"""
    print("\n🏗️ Testing DXF generation...")
    
    try:
        from src.cad.dxf_generator import DXFGenerator
        
        # Create generator
        gen = DXFGenerator()
        
        # Create drawing
        result = gen.create_drawing("test_plan")
        if not result:
            print("❌ Failed to create DXF drawing")
            return False
        
        # Add walls
        gen.add_wall((0, 0), (10, 0))
        gen.add_wall((10, 0), (10, 8))
        gen.add_wall((10, 8), (0, 8))
        gen.add_wall((0, 8), (0, 0))
        
        # Add rooms
        room_points = [(1, 1), (5, 1), (5, 5), (1, 5)]
        gen.add_room(room_points, "Test Room")
        
        # Save to temp file
        with tempfile.TemporaryDirectory() as temp_dir:
            save_result = gen.save_drawing("test_output", temp_dir)
            if not save_result:
                print("❌ Failed to save DXF file")
                return False
            
            # Check file exists
            file_path = os.path.join(temp_dir, "test_output.dxf")
            if not os.path.exists(file_path):
                print("❌ DXF file not created")
                return False
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size < 1000:  # Very small file indicates error
                print(f"❌ DXF file too small: {file_size} bytes")
                return False
            
            print(f"✅ DXF generated successfully ({file_size} bytes)")
            return True
            
    except Exception as e:
        print(f"❌ DXF generation error: {e}")
        return False

def test_spatial_reasoning():
    """Test spatial reasoning tool"""
    print("\n🧠 Testing spatial reasoning...")
    
    try:
        from src.tools import tool_registry
        
        # Get spatial reasoning tool
        spatial_tool = tool_registry.get_tool('spatial_reasoning')
        if not spatial_tool:
            print("❌ Spatial reasoning tool not found")
            return False
        
        # Test room placement
        test_params = {
            'operation': 'place_rooms',
            'boundary': [(0, 0), (10, 0), (10, 8), (0, 8)],
            'rooms': [
                {'type': 'living_room', 'area': 20.0},
                {'type': 'bedroom', 'area': 15.0},
                {'type': 'kitchen', 'area': 12.0}
            ]
        }
        
        result = spatial_tool.execute(test_params)
        if not result.success:
            print(f"❌ Spatial reasoning failed: {result.error}")
            return False
        
        room_layouts = result.data.get('room_layouts', [])
        if len(room_layouts) == 0:
            print("❌ No room layouts generated")
            return False
        
        total_utilization = result.data.get('total_utilization', 0)
        if total_utilization <= 0:
            print("❌ Invalid space utilization")
            return False
        
        print(f"✅ Spatial reasoning works ({len(room_layouts)} rooms, {total_utilization:.1f}% utilization)")
        return True
        
    except Exception as e:
        print(f"❌ Spatial reasoning error: {e}")
        return False

def test_api_models():
    """Test API models"""
    print("\n📋 Testing API models...")
    
    try:
        from src.main import FloorPlanRequest, RoomRequirement, PlanResponse
        
        # Test room requirement
        room = RoomRequirement(type="living_room", area=20.0)
        if room.type != "living_room" or room.area != 20.0:
            print("❌ RoomRequirement model failed")
            return False
        
        # Test floor plan request
        request = FloorPlanRequest(
            name="test_plan",
            building_type="residential",
            dimensions={"width": 10.0, "height": 8.0},
            rooms=[room],
            constraints={"style": "open_plan"}
        )
        
        # Test model dump (modern Pydantic)
        request_dict = request.model_dump()
        if not request_dict or 'name' not in request_dict:
            print("❌ FloorPlanRequest model dump failed")
            return False
        
        print("✅ API models work correctly")
        return True
        
    except Exception as e:
        print(f"❌ API models error: {e}")
        return False

def test_plan_generation_flow():
    """Test complete plan generation flow"""
    print("\n🔄 Testing plan generation flow...")
    
    try:
        import asyncio
        from src.main import generate_plan_background, FloorPlanRequest, RoomRequirement, active_plans
        
        # Create test request
        request = FloorPlanRequest(
            name="flow_test_plan",
            building_type="residential", 
            dimensions={"width": 10.0, "height": 8.0},
            rooms=[
                RoomRequirement(type="living_room", area=20.0),
                RoomRequirement(type="bedroom", area=15.0)
            ],
            constraints={"style": "open_plan"}
        )
        
        # Generate plan ID and add to active_plans
        import uuid
        from datetime import datetime
        plan_id = str(uuid.uuid4())
        
        # Initialize plan in active_plans (as the API would do)
        active_plans[plan_id] = {
            "id": plan_id,
            "name": request.name,
            "status": "initializing",
            "progress": 0,
            "created_at": datetime.now().isoformat(),
            "request": request.model_dump(),
            "result": None,
            "error": None
        }
        
        # Run background task
        asyncio.run(generate_plan_background(plan_id, request))
        
        # Check result
        if plan_id not in active_plans:
            print("❌ Plan not found in active_plans")
            return False
        
        plan = active_plans[plan_id]
        if plan.get("status") != "completed":
            print(f"❌ Plan generation failed: {plan.get('error')}")
            return False
        
        if not plan.get("result"):
            print("❌ No result in generated plan")
            return False
        
        result = plan["result"]
        if not result.get("file_path") or not os.path.exists(result["file_path"]):
            print("❌ DXF file not created or missing")
            return False
        
        print(f"✅ Plan generation flow works ({result.get('rooms_placed', 0)} rooms placed)")
        return True
        
    except Exception as e:
        print(f"❌ Plan generation flow error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 AI-CAD Backend Functionality Verification")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_dxf_generation,
        test_spatial_reasoning,
        test_api_models,
        test_plan_generation_flow
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print("📊 VERIFICATION RESULTS")
    print("=" * 50)
    
    status = "✅ PASSED" if passed == total else "⚠️  PARTIAL"
    print(f"Overall Status: {status}")
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All core functionality is working correctly!")
        print("The AI-CAD system is ready for production use.")
    else:
        print("\n⚠️  Some issues were found. Please check the logs above.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())