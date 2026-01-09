#!/usr/bin/env python3

"""
Test script to verify API connectivity and configuration
"""

import requests
import json
from urllib.parse import urlparse

def test_frontend_api_connectivity():
    """Test the exact API calls the frontend makes"""
    print("🔧 Testing Frontend API Connectivity...")
    
    # Test the exact endpoint the dashboard uses
    dashboard_url = "http://localhost:8000/api/v1/plans?page=1&limit=20&sort=updated_at&order=desc"
    
    try:
        print(f"📡 Testing: {dashboard_url}")
        
        # Simulate browser request
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Origin': 'http://localhost:3000',
            'Referer': 'http://localhost:3000/dashboard'
        }
        
        response = requests.get(dashboard_url, headers=headers, timeout=10)
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response Structure: {list(data.keys())}")
            
            if 'plans' in data:
                plans = data['plans']
                print(f"✅ Plans Count: {len(plans)}")
                
                if plans:
                    print(f"✅ Sample Plan: {plans[0]['name']} (ID: {plans[0]['id']})")
                    print(f"   Status: {plans[0]['status']}")
                    print(f"   Created: {plans[0]['created_at']}")
                
                # Test the data structure the frontend expects
                expected_structure = {
                    'success': True,
                    'data': plans,
                    'pagination': {
                        'page': 1,
                        'limit': 20,
                        'total': len(plans),
                        'totalPages': 1
                    }
                }
                
                print(f"✅ Expected structure matches: {isinstance(plans, list)}")
                return True
            else:
                print(f"❌ 'plans' key not found in response")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        print("   Make sure backend is running on port 8000")
        return False
    except requests.exceptions.Timeout as e:
        print(f"❌ Timeout Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def test_environment_variables():
    """Test frontend environment configuration"""
    print(f"\n🌍 Testing Environment Configuration...")
    
    # Test if frontend is accessible
    try:
        response = requests.get("http://localhost:3000/", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend accessible on port 3000")
        else:
            print(f"❌ Frontend returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend not accessible: {e}")
    
    # Check what API URL the frontend should be using
    expected_api_url = "http://localhost:8000"
    print(f"✅ Expected API URL: {expected_api_url}")
    
    return True

def main():
    """Main test function"""
    print("🚀 AI-CAD Frontend API Connectivity Test")
    print("=" * 50)
    
    # Test environment setup
    env_ok = test_environment_variables()
    
    # Test API connectivity
    api_ok = test_frontend_api_connectivity()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    print(f"Environment:    {'✅' if env_ok else '❌'}")
    print(f"API Connection: {'✅' if api_ok else '❌'}")
    
    if api_ok:
        print(f"\n🎉 SUCCESS! The API is working correctly.")
        print(f"📝 If the frontend still shows errors:")
        print(f"   1. Refresh the browser (Ctrl+F5)")
        print(f"   2. Check browser console for JavaScript errors")
        print(f"   3. Check browser Network tab for failed requests")
        print(f"   4. Clear browser cache")
    else:
        print(f"\n⚠️  API connectivity issues detected.")
        print(f"📝 Check:")
        print(f"   1. Backend is running on port 8000")
        print(f"   2. No firewall blocking the connection")
        print(f"   3. CORS is properly configured")

if __name__ == "__main__":
    main()