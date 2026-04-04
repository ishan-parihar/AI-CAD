#!/usr/bin/env python3
"""Quick test to verify backend is working"""

import subprocess
import time
import sys

def test_backend():
    print("🧪 Testing AI-CAD Backend...")
    
    # Check if backend is running by testing health endpoint
    try:
        import urllib.request
        import json
        
        response = urllib.request.urlopen("http://localhost:8100/api/v1/health", timeout=5)
        if response.getcode() == 200:
            print("✅ Backend health endpoint working")
            
            # Test plans endpoint
            response = urllib.request.urlopen("http://localhost:8100/api/v1/plans", timeout=5)
            if response.getcode() == 200:
                data = json.loads(response.read().decode())
                plans = data.get('plans', [])
                print(f"✅ Plans endpoint working - Found {len(plans)} plans")
                for plan in plans:
                    print(f"   - {plan.get('name', 'Unknown')} ({plan.get('status', 'unknown status')})")
            else:
                print("❌ Plans endpoint failed")
        else:
            print("❌ Backend health endpoint failed")
    except Exception as e:
        print(f"❌ Backend connection error: {e}")
        print("Make sure the backend is running on http://localhost:8100")

if __name__ == "__main__":
    test_backend()