#!/usr/bin/env python3
"""Quick test to verify API endpoints are working"""

import requests
import json

def test_api():
    base_url = "http://localhost:8100"
    
    print("🧪 Testing AI-CAD API endpoints...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test plans endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/plans", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Plans endpoint working - Found {len(data.get('plans', []))} plans")
            if data.get('plans'):
                print(f"   Sample plan: {data['plans'][0].get('name', 'Unknown')}")
        else:
            print(f"❌ Plans endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Plans endpoint error: {e}")
    
    # Test tools endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/tools", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Tools endpoint working - Found {len(data.get('tools', []))} tools")
        else:
            print(f"❌ Tools endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Tools endpoint error: {e}")

if __name__ == "__main__":
    test_api()