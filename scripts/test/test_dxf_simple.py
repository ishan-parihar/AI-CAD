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
        
        # Focus on LINE entities
        line_entities = [e for e in entities if e.dxftype() == 'LINE']
        print(f"🎯 Found {len(line_entities)} LINE entities")
        
        for i, entity in enumerate(line_entities):
            print(f"\n--- LINE Entity {i+1} ---")
            print(f"DXF Type: {entity.dxftype()}")
            print(f"Layer: {entity.dxf.layer}")
            print(f"Start point: ({entity.dxf.start.x}, {entity.dxf.start.y})")
            print(f"End point: ({entity.dxf.end.x}, {entity.dxf.end.y})")
            
            # Check all available attributes
            print(f"Available attributes: {[attr for attr in dir(entity.dxf) if not attr.startswith('_')]}")
            
            # Show coordinate formats for dxf-parser compatibility
            start_point = [float(entity.dxf.start.x), float(entity.dxf.start.y)]
            end_point = [float(entity.dxf.end.x), float(entity.dxf.end.y)]
            coordinates = start_point + end_point
            
            print(f"Expected coordinates array: {coordinates}")
            print(f"Expected startPoint: {start_point}")
            print(f"Expected endPoint: {end_point}")
        
        # Also test with dxf-parser to see what it produces
        print(f"\n" + "="*60)
        print(f"📄 Testing with dxf-parser library...")
        
        try:
            import DxfParser
            with open(dxf_file, 'r') as f:
                content = f.read()
            
            parser = DxfParser.DxfParser()
            dxf = parser.parse(content)
            
            if dxf and dxf.entities:
                print(f"🔍 dxf-parser found {len(dxf.entities)} entities")
                
                for i, entity in enumerate(dxf.entities):
                    if entity.type == 'LINE':
                        print(f"\n--- dxf-parser LINE Entity {i+1} ---")
                        print(f"Type: {entity.type}")
                        print(f"Layer: {entity.layer}")
                        print(f"Raw entity data: {entity}")
                        print(f"Available keys: {list(entity.__dict__.keys())}")
                        
                        # Check coordinate properties
                        for coord_prop in ['coordinates', 'startPoint', 'endPoint', 'vertices', 'points', 'x', 'y', 'x1', 'y1', 'x2', 'y2']:
                            if hasattr(entity, coord_prop):
                                value = getattr(entity, coord_prop)
                                print(f"  {coord_prop}: {value}")
                        
        except ImportError:
            print("❌ dxf-parser not available for comparison")
        except Exception as e:
            print(f"❌ Error with dxf-parser: {e}")
        
    except Exception as e:
        print(f"❌ Error parsing DXF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dxf_structure()