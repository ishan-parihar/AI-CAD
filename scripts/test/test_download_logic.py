#!/usr/bin/env python3
"""Test the download endpoint functionality"""

import sys
import os
sys.path.append('/home/ishanp/Documents/GitHub/AI-CAD/backend')

# Test database connection and plan retrieval
try:
    from src.database.database import get_db
    from src.database.models import Plan
    from src.utils.config import settings
    
    print("Testing database connection...")
    db = next(get_db())
    
    plan_id = "471bfe76-0102-4317-ad0b-8634d75cec43"
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    
    if plan:
        print(f"✅ Plan found:")
        print(f"   ID: {plan.id}")
        print(f"   Name: {plan.name}")
        print(f"   Status: {plan.status}")
        print(f"   DXF File Path: {plan.dxf_file_path}")
        
        # Check if file exists at stored path
        if plan.dxf_file_path:
            exists_stored = os.path.exists(plan.dxf_file_path)
            print(f"   File exists at stored path: {exists_stored}")
        
        # Check expected path
        expected_path = os.path.join(settings.output_directory, plan_id, f"{plan.name}.dxf")
        exists_expected = os.path.exists(expected_path)
        print(f"   Expected path: {expected_path}")
        print(f"   File exists at expected path: {exists_expected}")
        
        # List directory contents
        plan_dir = os.path.join(settings.output_directory, plan_id)
        if os.path.exists(plan_dir):
            print(f"   Directory contents:")
            for file in os.listdir(plan_dir):
                file_path = os.path.join(plan_dir, file)
                size = os.path.getsize(file_path)
                print(f"     - {file} ({size} bytes)")
        
        # Test file reading
        if exists_expected:
            try:
                import ezdxf
                doc = ezdxf.readfile(expected_path)
                entities = list(doc.modelspace())
                print(f"   ✅ DXF file can be read: {len(entities)} entities")
                
                # Show some entity info
                layer_counts = {}
                for entity in entities:
                    layer = entity.dxf.layer
                    layer_counts[layer] = layer_counts.get(layer, 0) + 1
                
                print(f"   Entities by layer: {layer_counts}")
                
            except Exception as e:
                print(f"   ❌ DXF file read error: {e}")
        
    else:
        print(f"❌ Plan {plan_id} not found in database")
    
    db.close()
    
except Exception as e:
    print(f"❌ Database test failed: {e}")
    import traceback
    traceback.print_exc()

# Test download logic simulation
print("\n" + "="*50)
print("Testing download logic simulation...")

try:
    from src.database.services import PlanService
    
    db = next(get_db())
    plan_service = PlanService(db)
    plan = plan_service.get_plan(plan_id)
    
    if plan:
        # Simulate download_plan logic
        if plan.status != "completed":
            print(f"❌ Plan status is '{plan.status}', not 'completed'")
        else:
            print(f"✅ Plan status is 'completed'")
            
            # Check file path logic
            if plan.dxf_file_path and os.path.exists(plan.dxf_file_path):
                file_path = plan.dxf_file_path
                filename = os.path.basename(file_path)
                print(f"✅ Using stored DXF path: {file_path}")
            else:
                plan_dir = os.path.join(settings.output_directory, plan_id)
                file_path = os.path.join(plan_dir, f"{plan.name}.dxf")
                filename = f"{plan.name}.dxf"
                
                if not os.path.exists(file_path):
                    print(f"❌ DXF file not found at: {file_path}")
                else:
                    print(f"✅ Found DXF file at fallback path: {file_path}")
                    
                    # This would be the FileResponse
                    print(f"   Filename: {filename}")
                    print(f"   Media type: application/dxf")
                    print(f"   File size: {os.path.getsize(file_path)} bytes")
    
    db.close()
    
except Exception as e:
    print(f"❌ Download logic test failed: {e}")
    import traceback
    traceback.print_exc()