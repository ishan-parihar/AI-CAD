#!/usr/bin/env python3
"""Simple test script for CAD components"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from cad.dxf_generator import DXFGenerator
from cad.entity_manager import EntityManager, Room, Wall, Door, Window
from cad.layout_optimizer import LayoutOptimizer
from shapely.geometry import Polygon


def test_dxf_generator():
    """Test DXF generator functionality"""
    print("Testing DXF Generator...")
    
    # Create DXF generator
    generator = DXFGenerator()
    
    # Create drawing
    success = generator.create_drawing("Test Floor Plan")
    print(f"Drawing created: {success}")
    
    if success:
        # Add walls
        generator.add_wall((0, 0), (10, 0), thickness=0.2)
        generator.add_wall((10, 0), (10, 8), thickness=0.2)
        generator.add_wall((10, 8), (0, 8), thickness=0.2)
        generator.add_wall((0, 8), (0, 0), thickness=0.2)
        
        # Add a door
        generator.add_door((0, 4), width=0.8, angle=0)
        
        # Add a window
        generator.add_window((5, 8), (7, 8), width=1.2)
        
        # Add a room
        room_points = [(0.2, 0.2), (9.8, 0.2), (9.8, 7.8), (0.2, 7.8)]
        generator.add_room(room_points, "Living Room")
        
        # Save drawing
        success = generator.save_drawing("test_floor_plan")
        print(f"Drawing saved: {success}")
        
        # Get drawing info
        info = generator.get_drawing_info()
        print(f"Drawing info: {info}")


def test_entity_manager():
    """Test entity manager functionality"""
    print("\nTesting Entity Manager...")
    
    # Create manager and generator
    generator = DXFGenerator()
    generator.create_drawing("Entity Test")
    manager = EntityManager(generator)
    
    # Create boundary
    boundary = Polygon([(0, 0), (10, 0), (10, 8), (0, 8)])
    
    # Add rooms
    room1 = Room([(0, 0), (5, 0), (5, 4), (0, 4)], "living_room", "Living Room")
    room2 = Room([(5, 0), (10, 0), (10, 4), (5, 4)], "kitchen", "Kitchen")
    room3 = Room([(0, 4), (10, 4), (10, 8), (0, 8)], "bedroom", "Master Bedroom")
    
    manager.add_entity(room1)
    manager.add_entity(room2)
    manager.add_entity(room3)
    
    # Add walls
    wall1 = Wall((0, 0), (10, 0), thickness=0.2)
    wall2 = Wall((10, 0), (10, 8), thickness=0.2)
    wall3 = Wall((10, 8), (0, 8), thickness=0.2)
    wall4 = Wall((0, 8), (0, 0), thickness=0.2)
    wall5 = Wall((5, 0), (5, 4), thickness=0.15)  # Interior wall
    
    manager.add_entity(wall1)
    manager.add_entity(wall2)
    manager.add_entity(wall3)
    manager.add_entity(wall4)
    manager.add_entity(wall5)
    
    # Add doors
    door1 = Door((0, 2), width=0.8, angle=0)
    door2 = Door((5, 2), width=0.8, angle=0)
    
    manager.add_entity(door1)
    manager.add_entity(door2)
    
    # Add windows
    window1 = Window((2, 8), (4, 8), width=1.2)
    window2 = Window((6, 8), (8, 8), width=1.2)
    
    manager.add_entity(window1)
    manager.add_entity(window2)
    
    # Get summary
    summary = manager.get_layout_summary()
    print(f"Layout summary: {summary}")
    
    # Validate layout
    validation = manager.validate_layout()
    print(f"Layout validation: {validation}")
    
    # Export to DXF
    success = manager.export_to_dxf()
    print(f"Exported to DXF: {success}")
    
    if success:
        generator.save_drawing("entity_test_plan")
        print("Entity test plan saved")


def test_layout_optimizer():
    """Test layout optimizer functionality"""
    print("\nTesting Layout Optimizer...")
    
    # Create manager and generator
    generator = DXFGenerator()
    generator.create_drawing("Optimizer Test")
    manager = EntityManager(generator)
    optimizer = LayoutOptimizer(manager)
    
    # Create boundary
    boundary = Polygon([(0, 0), (12, 0), (12, 10), (0, 10)])
    
    # Add rooms with suboptimal layout
    room1 = Room([(0, 0), (3, 0), (3, 3), (0, 3)], "bedroom1", "Bedroom 1")
    room2 = Room([(9, 7), (12, 7), (12, 10), (9, 10)], "bedroom2", "Bedroom 2")  # Far corner
    room3 = Room([(4, 4), (8, 4), (8, 6), (4, 6)], "kitchen", "Kitchen")
    
    manager.add_entity(room1)
    manager.add_entity(room2)
    manager.add_entity(room3)
    
    # Define adjacency requirements
    adjacency_requirements = {
        "bedroom1": ["kitchen"],
        "bedroom2": ["kitchen"],
        "kitchen": ["bedroom1", "bedroom2"]
    }
    
    # Run optimization
    result = optimizer.optimize_layout(boundary, adjacency_requirements, max_iterations=20)
    print(f"Optimization result: {result}")
    
    # Test circulation optimization
    circulation_result = optimizer.optimize_circulation_paths()
    print(f"Circulation optimization: {circulation_result}")
    
    # Test auto placement
    auto_result = optimizer.auto_place_doors_windows(boundary)
    print(f"Auto placement result: {auto_result}")


if __name__ == "__main__":
    print("Running CAD Component Tests\n")
    
    try:
        test_dxf_generator()
        test_entity_manager()
        test_layout_optimizer()
        print("\n✅ All tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()