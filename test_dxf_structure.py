#!/usr/bin/env python3

import sys
import os
import json

try:
    import ezdxf
    from ezdxf import recover
except ImportError:
    print("❌ ezdxf not installed. Install with: pip install ezdxf")
    sys.exit(1)

def test_dxf_structure():
    """Test the raw structure of the DXF file to understand coordinate storage"""
    
    plan_id = "471bfe76-0102-4317-ad0b-8634d75cec43"
    output_dir = "/home/ishanp/Documents/GitHub/AI-CAD/backend/outputs"
    
    print(f"🔍 Testing DXF structure for plan: {plan_id}")
    
    # Find the DXF file
    plan_path = os.path.join(output_dir, plan_id)
    if not os.path.exists(plan_path):
        print(f"❌ Plan directory not found: {plan_path}")
        return
    
    dxf_files = [f for f in os.listdir(plan_path) if f.endswith('.dxf')]
    if not dxf_files:
        print(f"❌ No DXF files found in: {plan_path}")
        return
    
    dxf_file = os.path.join(plan_path, dxf_files[0])
    print(f"📁 Found DXF file: {dxf_file}")
    
    try:
        # Read and parse DXF with ezdxf
        print(f"📄 Loading DXF with ezdxf...")
        doc, auditor = recover.readfile(dxf_file)
        
        if auditor.has_errors:
            print(f"⚠️  DXF has errors: {len(auditor.errors)}")
        
        modelspace = doc.modelspace()
        entities = list(modelspace)
        
        print(f"🔍 Found {len(entities)} entities in modelspace")
        
        for i, entity in enumerate(entities):
            print(f"\n--- Entity {i+1} ---")
            print(f"DXF Type: {entity.dxftype()}")
            print(f"Layer: {entity.dxf.layer}")
            print(f"Entity: {entity}")
            
            # Show coordinate-related data based on entity type
            if entity.dxftype() == 'LINE':
                print(f"  🎯 LINE entity coordinates:")
                print(f"    Start: ({entity.dxf.start.x}, {entity.dxf.start.y})")
                print(f"    End: ({entity.dxf.end.x}, {entity.dxf.end.y})")
                print(f"    All DXF data: {dict(entity.dxf)}")
                
            elif entity.dxftype() == 'LWPOLYLINE':
                print(f"  🎯 LWPOLYLINE entity coordinates:")
                if hasattr(entity, 'vertices') and callable(entity.vertices):
                    try:
                        vertices = list(entity.vertices())
                        print(f"    Vertices: {vertices}")
                    except:
                        print(f"    Vertices: (method call failed)")
                if hasattr(entity, 'points') and entity.points is not None:
                    print(f"    Points: {entity.points}")
                # Show key DXF attributes
                dxf_attrs = {}
                for attr in ['layer', 'color', 'linetype', 'flags', 'const_width']:
                    if hasattr(entity.dxf, attr):
                        dxf_attrs[attr] = getattr(entity.dxf, attr)
                print(f"    Key DXF data: {dxf_attrs}")
                
            elif entity.dxftype() == 'TEXT':
                print(f"  🎯 TEXT entity data:")
                print(f"    Text: {entity.dxf.text}")
                print(f"    Insert point: ({entity.dxf.insert.x}, {entity.dxf.insert.y})")
                print(f"    All DXF data: {dict(entity.dxf)}")
                
            else:
                print(f"  🎯 {entity.dxftype()} entity data:")
                print(f"    All DXF data: {dict(entity.dxf)}")
        
        # Also examine raw text content for comparison
        print(f"\n" + "="*60)
        print(f"📄 Raw DXF content analysis:")
        with open(dxf_file, 'r') as f:
            lines = f.readlines()
        
        # Find LINE entities in raw text
        line_entities = []
        for i, line in enumerate(lines):
            if line.strip() == 'LINE':
                # Extract the next 20 lines to see the structure
                context = lines[i:i+20]
                line_entities.append((i, context))
        
        print(f"🔍 Found {len(line_entities)} LINE entities in raw text")
        for idx, (line_num, context) in enumerate(line_entities[:2]):  # Show first 2
            print(f"\n--- Raw LINE Entity {idx+1} at line {line_num} ---")
            for j, ctx_line in enumerate(context):
                print(f"  {line_num + j}: {ctx_line.rstrip()}")
        
    except Exception as e:
        print(f"❌ Error parsing DXF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dxf_structure()