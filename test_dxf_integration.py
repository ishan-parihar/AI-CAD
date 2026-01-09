#!/usr/bin/env python3

"""
Test script to verify DXF download and basic parsing functionality
"""

import requests
import os
import tempfile
from typing import Dict, Any

def test_backend_api():
    """Test backend API endpoints"""
    print("🔧 Testing Backend API...")
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:8000/api/v1/health")
        if response.status_code == 200:
            print("✅ Backend health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False
    
    # Test plans endpoint
    try:
        response = requests.get("http://localhost:8000/api/v1/plans")
        if response.status_code == 200:
            plans = response.json().get("plans", [])
            print(f"✅ Found {len(plans)} plans")
            
            # Find a completed plan
            completed_plan = None
            for plan in plans:
                if plan.get("status") == "completed":
                    completed_plan = plan
                    break
            
            if completed_plan:
                print(f"✅ Found completed plan: {completed_plan['name']} (ID: {completed_plan['id']})")
                return completed_plan
            else:
                print("❌ No completed plans found")
                return False
        else:
            print(f"❌ Plans endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Plans request failed: {e}")
        return False

def test_dxf_download(plan_id: str, plan_name: str):
    """Test DXF file download"""
    print(f"\n📥 Testing DXF Download for plan {plan_id}...")
    
    try:
        url = f"http://localhost:8000/api/v1/plans/{plan_id}/download?file_format=dxf"
        response = requests.get(url)
        
        if response.status_code == 200:
            print(f"✅ DXF download successful")
            print(f"   Content type: {response.headers.get('content-type')}")
            print(f"   Content length: {len(response.content)} bytes")
            
            # Check if it looks like DXF content
            content_preview = response.content[:200].decode('utf-8', errors='ignore')
            print(f"   Content preview: {content_preview[:100]}...")
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.dxf', delete=False) as f:
                f.write(response.content)
                temp_path = f.name
            
            print(f"✅ DXF saved to temporary file: {temp_path}")
            return temp_path
        else:
            print(f"❌ DXF download failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ DXF download error: {e}")
        return None

def test_dxf_parsing(file_path: str):
    """Test basic DXF file parsing"""
    print(f"\n🔍 Testing DXF Parsing for {file_path}...")
    
    try:
        # Read the DXF file
        with open(file_path, 'r') as f:
            content = f.read()
        
        print(f"✅ DXF file read successfully")
        print(f"   File size: {len(content)} characters")
        
        # Basic DXF structure validation
        sections = []
        entities = []
        lines = content.split('\n')
        
        print(f"   First 10 lines: {lines[:10]}")
        
        # Parse DXF structure properly
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line == '0' and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line == 'SECTION':
                    sections.append('SECTION')
                    # Find section type
                    if i + 3 < len(lines) and lines[i + 2].strip() == '2':
                        section_type = lines[i + 3].strip()
                        sections.append(f'SECTION_TYPE:{section_type}')
                elif next_line == 'ENDSEC':
                    sections.append('ENDSEC')
                elif next_line in ['LWPOLYLINE', 'LINE', 'ARC', 'TEXT', 'CIRCLE', 'INSERT']:
                    entities.append(next_line)
                    sections.append(f'ENTITY:{next_line}')
                elif next_line in ['ENTITIES', 'HEADER', 'TABLES', 'BLOCKS']:
                    sections.append(f'SECTION_START:{next_line}')
            i += 1
        
        print(f"✅ DXF structure analysis:")
        print(f"   Total lines: {len(lines)}")
        print(f"   Sections found: {len(sections)}")
        print(f"   Entities found: {len(entities)}")
        
        # Show section breakdown
        section_types = [s for s in sections if s.startswith('SECTION_TYPE:')]
        if section_types:
            print(f"   Section types: {', '.join([s.split(':')[1] for s in section_types])}")
        
        if entities:
            entity_types = list(set(entities))
            print(f"   Entity types: {', '.join(entity_types)}")
            
            # Count each entity type
            from collections import Counter
            entity_counts = Counter(entities)
            for entity_type, count in entity_counts.items():
                print(f"   {entity_type}: {count}")
        
        # Check if this looks like a valid DXF
        has_header = any('HEADER' in s for s in sections)
        has_entities = any('ENTITIES' in s for s in sections)
        has_entity_data = len(entities) > 0
        
        print(f"   Has HEADER section: {has_header}")
        print(f"   Has ENTITIES section: {has_entities}")
        print(f"   Has entity data: {has_entity_data}")
        
        return has_entity_data
        
    except Exception as e:
        print(f"❌ DXF parsing error: {e}")
        return False

def test_frontend_connection():
    """Test frontend accessibility"""
    print(f"\n🌐 Testing Frontend Connection...")
    
    try:
        response = requests.get("http://localhost:3000/")
        if response.status_code == 200:
            print("✅ Frontend accessible on port 3000")
            return True
        else:
            print(f"❌ Frontend returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend connection failed: {e}")
        return False

def cleanup_temp_file(file_path: str):
    """Clean up temporary file"""
    try:
        os.unlink(file_path)
        print(f"🧹 Cleaned up temporary file: {file_path}")
    except:
        pass

def main():
    """Main test function"""
    print("🚀 AI-CAD DXF Integration Test")
    print("=" * 50)
    
    # Test 1: Backend API
    plan = test_backend_api()
    if not plan:
        print("\n❌ Backend API test failed. Exiting.")
        return False
    
    # Test 2: Frontend Connection
    frontend_ok = test_frontend_connection()
    
    # Test 3: DXF Download
    dxf_file = test_dxf_download(plan['id'], plan['name'])
    if not dxf_file:
        print("\n❌ DXF download test failed. Exiting.")
        return False
    
    # Test 4: DXF Parsing
    parsing_ok = test_dxf_parsing(dxf_file)
    
    # Cleanup
    cleanup_temp_file(dxf_file)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Backend API:    ✅")
    print(f"Frontend:       {'✅' if frontend_ok else '❌'}")
    print(f"DXF Download:   ✅")
    print(f"DXF Parsing:    {'✅' if parsing_ok else '❌'}")
    
    if parsing_ok:
        print("\n🎉 All critical tests passed! The DXF integration is working.")
        print("📝 Next steps:")
        print("   1. Open http://localhost:3000 in your browser")
        print("   2. Navigate to the plans page")
        print("   3. Click on a plan to view the DXF viewer")
        print("   4. Check browser console for debugging messages")
    else:
        print("\n⚠️  Some tests failed. Check the logs above for details.")
    
    return parsing_ok

if __name__ == "__main__":
    main()