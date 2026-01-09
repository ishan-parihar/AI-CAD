#!/usr/bin/env python3

"""
Quick test to verify the dashboard data loading is working
"""

import requests
import json

def test_dashboard_endpoints():
    """Test the specific endpoints the dashboard uses"""
    print("🔧 Testing Dashboard API Endpoints...")
    
    base_url = "http://localhost:8000"
    
    # Test endpoints
    endpoints = [
        "/api/v1/health",
        "/api/v1/plans",
        "/api/v1/plans?page=1&limit=20&sort=updated_at&order=desc"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint}")
                print(f"   Status: {response.status_code}")
                print(f"   Data keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                
                if "plans" in data:
                    print(f"   Plans count: {len(data['plans'])}")
                print()
            else:
                print(f"❌ {endpoint}")
                print(f"   Status: {response.status_code}")
                print(f"   Error: {response.text}")
                print()
                
        except Exception as e:
            print(f"❌ {endpoint}")
            print(f"   Error: {e}")
            print()
    
    # Test frontend accessibility
    try:
        response = requests.get("http://localhost:3000/", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend accessible")
        else:
            print(f"❌ Frontend error: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend error: {e}")

if __name__ == "__main__":
    test_dashboard_endpoints()