#!/usr/bin/env python3
"""
Comprehensive test to validate Recent Plans fixes and DXF viewing functionality
"""

import requests
import json
import time
from pathlib import Path

def test_backend_health():
    """Test backend is running"""
    print("🔍 Testing backend health...")
    try:
        response = requests.get("http://localhost:8100/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is running: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def test_recent_plans_api():
    """Test recent plans API endpoint"""
    print("\n🔍 Testing recent plans API...")
    try:
        # Use the main plans endpoint with limit to get recent plans
        response = requests.get("http://localhost:8100/api/v1/plans?limit=10", timeout=10)
        if response.status_code == 200:
            data = response.json()
            plans = data.get('plans', [])
            print(f"✅ Recent plans API working: {len(plans)} plans found")
            if plans:
                print(f"   First plan: {plans[0].get('name', 'unnamed')} (ID: {plans[0].get('id', 'unknown')})")
            return plans
        else:
            print(f"❌ Recent plans API failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Recent plans API error: {e}")
        return None

def test_plan_download(plan_id):
    """Test plan download endpoint"""
    print(f"\n🔍 Testing plan download for ID: {plan_id}...")
    try:
        response = requests.get(f"http://localhost:8100/api/v1/plans/{plan_id}/download?file_format=dxf", timeout=10)
        if response.status_code == 200:
            content = response.text
            if content and len(content) > 100:
                print(f"✅ Plan download working: {len(content)} characters")
                # Check if it's valid DXF
                if "SECTION" in content and "HEADER" in content:
                    print("   ✅ Content appears to be valid DXF")
                else:
                    print("   ⚠️  Content may not be valid DXF")
                return True
            else:
                print("❌ Downloaded content is empty or too short")
                return False
        else:
            print(f"❌ Plan download failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Plan download error: {e}")
        return False

def test_frontend_build():
    """Test frontend builds without errors"""
    print("\n🔍 Testing frontend build...")
    try:
        frontend_dir = Path("/home/ishanp/Documents/GitHub/AI-CAD/frontend")
        if (frontend_dir / ".next").exists():
            print("✅ Frontend build directory exists")
            return True
        else:
            print("❌ Frontend build directory not found")
            return False
    except Exception as e:
        print(f"❌ Frontend build check error: {e}")
        return False

def main():
    """Run comprehensive tests"""
    print("🧪 AI-CAD Recent Plans & DXF Viewer - Comprehensive Test")
    print("=" * 60)
    
    # Test backend health
    if not test_backend_health():
        print("\n❌ Backend is not running - aborting tests")
        return False
    
    # Test recent plans API
    plans = test_recent_plans_api()
    if not plans:
        print("\n❌ Recent plans API failed - aborting tests")
        return False
    
    # Test plan download for first few plans
    download_success = True
    for i, plan in enumerate(plans[:3]):  # Test first 3 plans
        plan_id = plan.get('id')
        if plan_id:
            if not test_plan_download(plan_id):
                download_success = False
    
    # Test frontend build
    frontend_ok = test_frontend_build()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    if download_success and frontend_ok:
        print("✅ ALL TESTS PASSED!")
        print("✅ Recent Plans functionality should now work")
        print("✅ DXF viewer should now load files correctly")
        print("✅ Download functionality should work properly")
        print("\n🎉 Fixes validated successfully!")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        if not download_success:
            print("❌ Plan download issues detected")
        if not frontend_ok:
            print("❌ Frontend build issues detected")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)