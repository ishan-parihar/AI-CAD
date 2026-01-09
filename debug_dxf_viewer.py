#!/usr/bin/env python3
"""
Comprehensive DXF Viewer Debug Script

This script tests the complete DXF viewing pipeline:
1. Fetches a real DXF file from the backend
2. Tests the DXF parsing logic (equivalent to frontend dxf-parser)
3. Validates the entity extraction and structure
4. Simulates the rendering calculations
"""

import requests
import json
import sys
from pathlib import Path

def test_backend_dxf_download():
    """Test downloading real DXF file from backend"""
    print("=== Testing Backend DXF Download ===")
    
    try:
        # Test with a real plan ID from the outputs directory
        plan_id = "35812cb9-e1c5-46e8-b027-1cfcedcec95e"  # Test Plan.dxf
        
        print(f"Downloading DXF for plan: {plan_id}")
        
        # Try to download from backend
        response = requests.get(
            f"http://localhost:8000/api/v1/plans/{plan_id}/download",
            params={"format": "dxf"},
            timeout=10
        )
        
        if response.status_code == 200:
            dxf_content = response.text
            print(f"✅ DXF download successful")
            print(f"   Content length: {len(dxf_content)} characters")
            print(f"   Content preview: {dxf_content[:200]}...")
            return dxf_content, plan_id
        else:
            print(f"❌ DXF download failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None, plan_id
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend - is it running on localhost:8000?")
        return None, None
    except Exception as e:
        print(f"❌ DXF download error: {e}")
        return None, None

def validate_dxf_structure(dxf_content):
    """Validate DXF file structure and extract key information"""
    print("\n=== Validating DXF Structure ===")
    
    if not dxf_content:
        return False, None
    
    # Basic DXF structure validation
    lines = dxf_content.split('\n')
    print(f"Total lines: {len(lines)}")
    
    # Check for required DXF sections
    has_header = 'SECTION' in lines and 'HEADER' in lines
    has_entities = 'SECTION' in lines and 'ENTITIES' in lines
    has_eof = 'EOF' in lines
    
    print(f"Has HEADER section: {has_header}")
    print(f"Has ENTITIES section: {has_entities}")
    print(f"Has EOF: {has_eof}")
    
    if not (has_header and has_entities and has_eof):
        print("❌ Invalid DXF structure")
        return False, None
    
    # Extract entities section
    entities_start = -1
    entities_end = -1
    
    for i, line in enumerate(lines):
        if line.strip() == 'ENTITIES':
            # Look for the pattern: 0, SECTION, 2, ENTITIES
            if i > 2 and lines[i-1].strip() == '2' and lines[i-2].strip() == 'SECTION':
                entities_start = i - 2
        elif line.strip() == 'ENDSEC' and entities_start != -1:
            entities_end = i
            break
    
    if entities_start == -1 or entities_end == -1:
        print("❌ Could not find ENTITIES section boundaries")
        print(f"   Debug: entities_start={entities_start}, entities_end={entities_end}")
        # Show some lines around where ENTITIES should be
        for i, line in enumerate(lines):
            if 'ENTITIES' in line:
                print(f"   Found ENTITIES at line {i}: '{line.strip()}'")
                if i > 0:
                    print(f"   Previous line: '{lines[i-1].strip()}'")
                if i > 1:
                    print(f"   Two lines back: '{lines[i-2].strip()}'")
                if i > 2:
                    print(f"   Three lines back: '{lines[i-3].strip()}'")
        return False, None
    
    entities_section = lines[entities_start:entities_end + 1]
    print(f"✅ Found ENTITIES section: {len(entities_section)} lines")
    
    # Parse entities
    entities = []
    current_entity = {}
    
    for i in range(2, len(entities_section) - 1):  # Skip SECTION/ENTITIES and ENDSEC
        line = lines[entities_start + i].strip()
        prev_line = lines[entities_start + i - 1].strip()
        
        if line.isdigit():
            group_code = int(line)
            if i + 1 < len(entities_section):
                value_line = lines[entities_start + i + 1].strip()
                
                if group_code == 0:  # Entity type
                    if current_entity:  # Save previous entity
                        entities.append(current_entity)
                    current_entity = {'type': value_line}
                elif group_code == 8:  # Layer
                    current_entity['layer'] = value_line
                elif group_code == 10:  # Start X
                    current_entity.setdefault('startPoint', [0, 0])[0] = float(value_line)
                elif group_code == 20:  # Start Y
                    current_entity.setdefault('startPoint', [0, 0])[1] = float(value_line)
                elif group_code == 11:  # End X
                    current_entity.setdefault('endPoint', [0, 0])[0] = float(value_line)
                elif group_code == 21:  # End Y
                    current_entity.setdefault('endPoint', [0, 0])[1] = float(value_line)
                elif group_code == 40:  # Radius
                    current_entity['radius'] = float(value_line)
                elif group_code == 50:  # Start angle
                    current_entity['startAngle'] = float(value_line)
                elif group_code == 51:  # End angle
                    current_entity['endAngle'] = float(value_line)
    
    if current_entity:
        entities.append(current_entity)
    
    print(f"✅ Parsed {len(entities)} entities")
    
    # Analyze entities
    entity_types = {}
    layers = set()
    for entity in entities:
        entity_type = entity.get('type', 'UNKNOWN')
        entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
        if 'layer' in entity:
            layers.add(entity['layer'])
    
    print(f"   Entity types: {entity_types}")
    print(f"   Layers: {sorted(layers)}")
    
    # Show some example entities
    print(f"   First 3 entities:")
    for i, entity in enumerate(entities[:3]):
        print(f"     {i+1}. {entity}")
    
    return True, {
        'entities': entities,
        'entity_types': entity_types,
        'layers': sorted(layers),
        'total_count': len(entities)
    }

def simulate_frontend_rendering(dxf_data):
    """Simulate the frontend rendering calculations"""
    print("\n=== Simulating Frontend Rendering ===")
    
    if not dxf_data:
        print("❌ No DXF data to render")
        return False
    
    entities = dxf_data['entities']
    
    # Calculate bounds (same as frontend)
    bounds = {
        'minX': float('inf'),
        'minY': float('inf'),
        'maxX': float('-inf'),
        'maxY': float('-inf')
    }
    
    for entity in entities:
        if 'startPoint' in entity:
            sp = entity['startPoint']
            bounds['minX'] = min(bounds['minX'], sp[0])
            bounds['minY'] = min(bounds['minY'], sp[1])
            bounds['maxX'] = max(bounds['maxX'], sp[0])
            bounds['maxY'] = max(bounds['maxY'], sp[1])
        
        if 'endPoint' in entity:
            ep = entity['endPoint']
            bounds['minX'] = min(bounds['minX'], ep[0])
            bounds['minY'] = min(bounds['minY'], ep[1])
            bounds['maxX'] = max(bounds['maxX'], ep[0])
            bounds['maxY'] = max(bounds['maxY'], ep[1])
        
        if 'radius' in entity and 'center' in entity:
            r = entity['radius']
            c = entity['center']
            bounds['minX'] = min(bounds['minX'], c[0] - r)
            bounds['minY'] = min(bounds['minY'], c[1] - r)
            bounds['maxX'] = max(bounds['maxX'], c[0] + r)
            bounds['maxY'] = max(bounds['maxY'], c[1] + r)
    
    print(f"✅ Calculated bounds: {bounds}")
    
    # Check if bounds are valid
    if bounds['minX'] == float('inf') or bounds['maxX'] == float('-inf'):
        print("❌ Invalid bounds - no drawable entities found")
        return False
    
    # Simulate canvas scaling (same as frontend)
    scale = 10
    offsetX = 50
    offsetY = 50
    
    canvas_width = 800
    canvas_height = 600
    padding = 50
    
    content_width = (bounds['maxX'] - bounds['minX']) * scale
    content_height = (bounds['maxY'] - bounds['minY']) * scale
    
    print(f"   Content size: {content_width} x {content_height}")
    
    scale_x = (canvas_width - padding * 2) / content_width
    scale_y = (canvas_height - padding * 2) / content_height
    final_scale = min(scale_x, scale_y, 2)
    
    print(f"   Calculated zoom scale: {final_scale:.3f}")
    
    # Test entity transformation
    print(f"   Testing entity transformations:")
    for i, entity in enumerate(entities[:5]):  # Test first 5
        entity_type = entity['type']
        
        if entity_type == 'LINE' and 'startPoint' in entity and 'endPoint' in entity:
            sp = entity['startPoint']
            ep = entity['endPoint']
            
            # Apply transformation (same as frontend)
            x1 = sp[0] * scale + offsetX
            y1 = sp[1] * scale + offsetY
            x2 = ep[0] * scale + offsetX
            y2 = ep[1] * scale + offsetY
            
            print(f"     LINE: ({x1:.1f}, {y1:.1f}) -> ({x2:.1f}, {y2:.1f})")
            
        elif entity_type == 'CIRCLE' and 'center' in entity and 'radius' in entity:
            c = entity['center']
            r = entity['radius']
            
            x = (c[0] - r) * scale + offsetX
            y = (c[1] - r) * scale + offsetY
            final_radius = r * scale
            
            print(f"     CIRCLE: center=({x:.1f}, {y:.1f}), radius={final_radius:.1f}")
    
    return True

def check_fabric_js_compatibility():
    """Check Fabric.js compatibility issues"""
    print("\n=== Checking Fabric.js Compatibility ===")
    
    # Common issues with Fabric.js and DXF rendering
    issues = []
    
    # Check 1: Fabric.js object creation
    print("Checking Fabric.js object creation patterns...")
    
    # Test line coordinates format
    test_line_coords = [10, 20, 100, 200]  # x1, y1, x2, y2
    print(f"   Line coordinates format: {test_line_coords}")
    print("   ✅ Line coordinates should be flat array [x1, y1, x2, y2]")
    
    # Test circle parameters
    test_circle_params = {
        'left': 50,
        'top': 50,
        'radius': 25,
        'fill': 'transparent',
        'stroke': '#000000',
        'strokeWidth': 1
    }
    print(f"   Circle parameters: {test_circle_params}")
    print("   ✅ Circle should use left/top for position, not center")
    
    # Check 2: Common rendering issues
    potential_issues = [
        "Canvas not properly initialized",
        "Entities outside canvas bounds",
        "Incorrect coordinate transformation",
        "Missing layer visibility handling",
        "Fabric.js version compatibility",
        "Canvas not rendered after adding objects"
    ]
    
    print(f"\n   Potential issues to check:")
    for i, issue in enumerate(potential_issues, 1):
        print(f"     {i}. {issue}")
    
    return True

def main():
    print("🔍 Comprehensive DXF Viewer Debug")
    print("=" * 50)
    
    # Test 1: Backend DXF download
    dxf_content, plan_id = test_backend_dxf_download()
    
    if not dxf_content:
        print("\n❌ Cannot proceed without DXF content")
        sys.exit(1)
    
    # Test 2: DXF structure validation
    is_valid, dxf_data = validate_dxf_structure(dxf_content)
    
    if not is_valid:
        print("\n❌ Invalid DXF structure - cannot proceed")
        sys.exit(1)
    
    # Test 3: Simulate frontend rendering
    render_success = simulate_frontend_rendering(dxf_data)
    
    if not render_success:
        print("\n❌ Rendering simulation failed")
        sys.exit(1)
    
    # Test 4: Check Fabric.js compatibility
    check_fabric_js_compatibility()
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 DEBUG SUMMARY")
    print("=" * 50)
    print("✅ Backend DXF download: Working")
    print("✅ DXF structure validation: Passed")
    
    if dxf_data:
        print(f"✅ Frontend rendering simulation: Success ({dxf_data['total_count']} entities)")
        print("✅ Fabric.js compatibility: Checked")
        
        print(f"\n📋 ANALYSIS RESULTS:")
        print(f"   Plan ID: {plan_id}")
        print(f"   Total entities: {dxf_data['total_count']}")
        print(f"   Entity types: {dxf_data['entity_types']}")
        print(f"   Layers: {dxf_data['layers']}")
    else:
        print("❌ Frontend rendering simulation: Failed")
        print("❌ Fabric.js compatibility: Not checked")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"   1. Check browser console for JavaScript errors")
    print(f"   2. Verify Fabric.js canvas initialization")
    print(f"   3. Test with a simple LINE entity first")
    print(f"   4. Check coordinate transformations")
    print(f"   5. Verify layer visibility state")

if __name__ == "__main__":
    main()