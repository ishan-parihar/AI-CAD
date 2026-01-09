#!/usr/bin/env python3
"""
Test DXF file download and content to verify frontend should receive valid data
"""
import requests
import os

def test_dxf_download():
    plan_id = "471bfe76-0102-4317-ad0b-8634d75cec43"
    url = f"http://localhost:8000/api/v1/plans/{plan_id}/download?file_format=dxf"
    
    print("🧪 Testing DXF File Download")
    print("=" * 50)
    print(f"URL: {url}")
    
    try:
        # Download the DXF file
        response = requests.get(url, timeout=10)
        
        print(f"📥 Status Code: {response.status_code}")
        print(f"📏 Content Size: {len(response.content)} bytes")
        print(f"📋 Content Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            # Save to file for inspection
            output_path = f"test_download_{plan_id[:8]}.dxf"
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"💾 Saved to: {output_path}")
            
            # Analyze content
            content = response.content.decode('utf-8', errors='ignore')
            
            print("\n📊 DXF Content Analysis:")
            print(f"   Header section: {'HEADER' in content}")
            print(f"   Entities section: {'ENTITIES' in content}")
            print(f"   EOF marker: {'EOF' in content}")
            
            # Count entities
            entity_count = content.count('\n  0')
            print(f"   Approximate entities: {entity_count}")
            
            # Look for specific entity types
            lwpolyline_count = content.count('LWPOLYLINE')
            line_count = content.count('LINE')
            circle_count = content.count('CIRCLE')
            arc_count = content.count('ARC')
            
            print(f"\n🔍 Entity Types Found:")
            print(f"   LWPOLYLINE: {lwpolyline_count}")
            print(f"   LINE: {line_count}")
            print(f"   CIRCLE: {circle_count}")
            print(f"   ARC: {arc_count}")
            
            # Show first few lines
            lines = content.split('\n')[:20]
            print(f"\n📄 First 20 lines of DXF:")
            for i, line in enumerate(lines):
                print(f"   {i+1:2d}: {line}")
            
            # Check if it looks like valid DXF
            if content.startswith('0') and 'SECTION' in content and 'ENDSEC' in content and 'EOF' in content:
                print("\n✅ DXF file appears to be valid")
                return True
            else:
                print("\n❌ DXF file may be invalid")
                return False
        else:
            print(f"❌ Download failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error downloading DXF: {e}")
        return False

if __name__ == "__main__":
    success = test_dxf_download()
    
    if success:
        print("\n🎉 DXF file is valid and should be parseable by frontend!")
        print("\n📋 If frontend still shows blank:")
        print("1. Check browser console for debugging messages")
        print("2. Verify DXF parsing is working correctly")
        print("3. Check if canvas rendering is functioning")
    else:
        print("\n💥 DXF file has issues")