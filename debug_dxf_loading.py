#!/usr/bin/env python3
"""
Debug script to test DXF loading and parsing
"""

import requests
import tempfile
import os

def test_dxf_download():
    """Test downloading a DXF file from the backend"""
    plan_id = "471bfe76-0102-4317-ad0b-8634d75cec43"
    url = f"http://localhost:8100/api/v1/plans/{plan_id}/download?file_format=dxf"
    
    print(f"🔍 Testing DXF download for plan: {plan_id}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            print(f"✅ Download successful: {len(content)} characters")
            
            # Check if it looks like valid DXF
            if "SECTION" in content and "HEADER" in content and "ENTITIES" in content:
                print("✅ Content appears to be valid DXF")
                
                # Count entities
                entity_count = content.count("  0\n")
                print(f"📊 Found ~{entity_count} entities/sections")
                
                # Show first few lines
                lines = content.split('\n')[:20]
                print("\n📄 First 20 lines:")
                for i, line in enumerate(lines, 1):
                    print(f"  {i:2d}: {line}")
                
                # Save to temporary file for inspection
                with tempfile.NamedTemporaryFile(mode='w', suffix='.dxf', delete=False) as f:
                    f.write(content)
                    temp_path = f.name
                
                print(f"\n💾 Saved to: {temp_path}")
                return True, temp_path
            else:
                print("❌ Content doesn't appear to be valid DXF")
                print(f"Content preview: {content[:200]}...")
                return False, None
        else:
            print(f"❌ Download failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Download error: {e}")
        return False, None

def main():
    """Run DXF debug test"""
    print("🧪 DXF Loading Debug Test")
    print("=" * 40)
    
    success, temp_path = test_dxf_download()
    
    if success:
        print(f"\n✅ DXF download test PASSED")
        print(f"The DXF file should be loadable in the frontend")
        if temp_path:
            print(f"File saved for inspection: {temp_path}")
    else:
        print(f"\n❌ DXF download test FAILED")
        print("The frontend DXF viewer will fail because the file can't be downloaded")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)