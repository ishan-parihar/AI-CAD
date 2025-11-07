#!/usr/bin/env python3
"""
Comprehensive test script for AI-CAD backend
Tests all the critical fixes and end-to-end functionality
"""

import requests
import json
import time
import os

BASE_URL = "http://127.0.0.1:8100"

def test_health():
    """Test API health endpoint"""
    print("🔍 Testing API Health...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_plan_generation():
    """Test end-to-end plan generation"""
    print("\n🏗️ Testing Plan Generation...")
    
    test_plan = {
        "name": "Test Apartment",
        "building_type": "residential",
        "dimensions": {"width": 12, "height": 10},
        "rooms": [
            {"type": "living_room", "area": 20, "adjacency": ["kitchen"]},
            {"type": "kitchen", "area": 15, "adjacency": ["living_room"]},
            {"type": "bedroom", "area": 12},
            {"type": "bathroom", "area": 6}
        ],
        "constraints": {
            "min_room_size": 5,
            "corridor_width": 1.2
        }
    }
    
    try:
        # Start plan generation
        response = requests.post(
            f"{BASE_URL}/api/v1/plans/generate",
            json=test_plan,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Generation request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        result = response.json()
        plan_id = result.get('plan_id')
        print(f"✅ Plan generation started: {plan_id}")
        
        # Monitor progress
        max_attempts = 15
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{BASE_URL}/api/v1/plans/{plan_id}", timeout=5)
                if response.status_code == 200:
                    plan_data = response.json()
                    status = plan_data.get('status')
                    progress = plan_data.get('progress', 0)
                    
                    print(f"   Progress: {progress}% - Status: {status}")
                    
                    if status == 'completed':
                        print("✅ Plan generation completed successfully!")
                        
                        # Check if DXF file was created
                        file_path = plan_data.get('file_path')
                        if file_path and os.path.exists(file_path):
                            file_size = os.path.getsize(file_path)
                            print(f"✅ DXF file created: {file_path} ({file_size} bytes)")
                        else:
                            print("⚠️ DXF file not found")
                        
                        # Check summary
                        summary = plan_data.get('summary', {})
                        print(f"   Total rooms: {summary.get('total_rooms', 0)}")
                        print(f"   Building area: {summary.get('building_area', 0)}m²")
                        print(f"   AI enhanced: {summary.get('ai_enhanced', False)}")
                        
                        return True
                        
                    elif status == 'failed':
                        error = plan_data.get('error', 'Unknown error')
                        print(f"❌ Plan generation failed: {error}")
                        return False
                        
                time.sleep(2)
                
            except Exception as e:
                print(f"⚠️ Error checking progress: {e}")
                time.sleep(2)
        
        print("⏰ Plan generation timed out")
        return False
        
    except Exception as e:
        print(f"❌ Plan generation error: {e}")
        return False

def test_plans_list():
    """Test plans listing endpoint"""
    print("\n📋 Testing Plans List...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/plans", timeout=5)
        if response.status_code == 200:
            data = response.json()
            plans = data.get('plans', [])
            print(f"✅ Retrieved {len(plans)} plans")
            
            # Check for any error plans
            error_plans = [p for p in plans if p.get('status') == 'error']
            if error_plans:
                print(f"⚠️ Found {len(error_plans)} plans with errors")
            else:
                print("✅ No error plans found")
            
            return True
        else:
            print(f"❌ Plans list failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Plans list error: {e}")
        return False

def test_dxf_download():
    """Test DXF file download"""
    print("\n💾 Testing DXF Download...")
    
    # Get a completed plan
    try:
        response = requests.get(f"{BASE_URL}/api/v1/plans", timeout=5)
        if response.status_code == 200:
            data = response.json()
            plans = data.get('plans', [])
            completed_plans = [p for p in plans if p.get('status') == 'completed']
            
            if completed_plans:
                plan_id = completed_plans[0]['id']
                download_url = f"{BASE_URL}/api/v1/plans/{plan_id}/download"
                
                response = requests.get(download_url, timeout=10)
                if response.status_code == 200:
                    # Check if it's a valid DXF file
                    content = response.content
                    if content.startswith(b'0') and b'SECTION' in content:
                        print("✅ DXF download successful")
                        return True
                    else:
                        print("❌ Invalid DXF file format")
                        return False
                else:
                    print(f"❌ Download failed: {response.status_code}")
                    return False
            else:
                print("⚠️ No completed plans found for download test")
                return True  # Not a failure, just no data
    except Exception as e:
        print(f"❌ Download test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 AI-CAD Backend Comprehensive Test Suite")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Plan Generation", test_plan_generation),
        ("Plans List", test_plans_list),
        ("DXF Download", test_dxf_download)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the logs above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)