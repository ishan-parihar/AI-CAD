#!/usr/bin/env python3
"""Test DXF generation directly"""

import sys
import os
sys.path.append('/home/ishanp/Documents/GitHub/AI-CAD/backend')

# Test basic imports
try:
    import ezdxf
    print(f"✅ ezdxf imported successfully: {ezdxf.__version__}")
except ImportError as e:
    print(f"❌ Failed to import ezdxf: {e}")
    sys.exit(1)

# Test DXF generator
try:
    from src.cad.dxf_generator import DXFGenerator
    print("✅ DXFGenerator imported successfully")
except ImportError as e:
    print(f"❌ Failed to import DXFGenerator: {e}")
    sys.exit(1)

# Test creating a drawing
try:
    generator = DXFGenerator()
    success = generator.create_drawing("Test Drawing")
    if success:
        print("✅ Drawing created successfully")
        
        # Add a simple wall
        wall = generator.add_wall((0, 0), (10, 0), 0.2)
        if wall:
            print("✅ Wall added successfully")
            
            # Save the drawing
            output_dir = "/tmp/dxf_test"
            os.makedirs(output_dir, exist_ok=True)
            saved = generator.save_drawing("test.dxf", output_dir)
            
            if saved:
                file_path = os.path.join(output_dir, "test.dxf")
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    print(f"✅ DXF file saved successfully: {file_path} ({file_size} bytes)")
                    
                    # Verify file can be opened
                    try:
                        doc = ezdxf.readfile(file_path)
                        entities = list(doc.modelspace())
                        print(f"✅ DXF file verification successful: {len(entities)} entities found")
                    except Exception as e:
                        print(f"❌ DXF file verification failed: {e}")
                else:
                    print("❌ DXF file was not created")
            else:
                print("❌ Failed to save DXF file")
        else:
            print("❌ Failed to add wall")
    else:
        print("❌ Failed to create drawing")
except Exception as e:
    print(f"❌ DXF generation test failed: {e}")
    import traceback
    traceback.print_exc()