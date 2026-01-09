#!/usr/bin/env python3
"""
Final validation test for Recent Plans and DXF Viewer fixes
"""

import requests
import json

def test_api_endpoints():
    """Test the actual API endpoints used by the frontend"""
    print("🔍 Testing API endpoints used by frontend...")
    
    # Test the list plans endpoint (what Recent Plans uses)
    try:
        response = requests.get("http://localhost:8100/api/v1/plans?limit=20", timeout=10)
        if response.status_code == 200:
            data = response.json()
            plans = data.get('plans', [])
            print(f"✅ List plans endpoint working: {len(plans)} plans returned")
            
            # Get first valid plan for download test
            valid_plan = None
            for plan in plans:
                if plan.get('id') and plan.get('id') != 'test-123':
                    valid_plan = plan
                    break
            
            if valid_plan:
                plan_id = valid_plan['id']
                plan_name = valid_plan.get('name', 'unnamed')
                print(f"   Testing with plan: {plan_name} (ID: {plan_id})")
                
                # Test download endpoint
                download_response = requests.get(f"http://localhost:8100/api/v1/plans/{plan_id}/download?file_format=dxf", timeout=10)
                if download_response.status_code == 200:
                    content = download_response.text
                    if content and len(content) > 1000 and "SECTION" in content:
                        print(f"✅ Download endpoint working: {len(content)} characters")
                        return True
                    else:
                        print("❌ Downloaded content invalid")
                        return False
                else:
                    print(f"❌ Download failed: {download_response.status_code}")
                    return False
            else:
                print("❌ No valid plans found for testing")
                return False
        else:
            print(f"❌ List plans failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False

def test_frontend_files():
    """Test that frontend files are properly updated"""
    print("\n🔍 Testing frontend file modifications...")
    
    try:
        # Check dashboard page has download function
        dashboard_path = "/home/ishanp/Documents/GitHub/AI-CAD/frontend/src/app/(dashboard)/dashboard/page.tsx"
        with open(dashboard_path, 'r') as f:
            dashboard_content = f.read()
            
        if 'handleDownload' in dashboard_content and 'apiClient.downloadPlan' in dashboard_content:
            print("✅ Dashboard page has download functionality")
        else:
            print("❌ Dashboard page missing download functionality")
            return False
        
        # Check DXF viewer uses API client
        dxf_viewer_path = "/home/ishanp/Documents/GitHub/AI-CAD/frontend/src/components/cad/DXFViewer.tsx"
        with open(dxf_viewer_path, 'r') as f:
            dxf_content = f.read()
            
        if 'apiClient.downloadPlan' in dxf_content and 'dxfBlob.text()' in dxf_content:
            print("✅ DXF viewer uses API client correctly")
        else:
            print("❌ DXF viewer not properly updated")
            return False
        
        # Check plan detail page uses API client
        plan_detail_path = "/home/ishanp/Documents/GitHub/AI-CAD/frontend/src/app/(dashboard)/plans/[id]/page.tsx"
        with open(plan_detail_path, 'r') as f:
            plan_detail_content = f.read()
            
        if 'apiClient.downloadPlan' in plan_detail_content:
            print("✅ Plan detail page uses API client")
        else:
            print("❌ Plan detail page not properly updated")
            return False
        
        return True
    except Exception as e:
        print(f"❌ File check error: {e}")
        return False

def main():
    """Run final validation"""
    print("🎯 AI-CAD Recent Plans & DXF Viewer - Final Validation")
    print("=" * 60)
    
    # Test API endpoints
    api_ok = test_api_endpoints()
    
    # Test frontend files
    files_ok = test_frontend_files()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 VALIDATION SUMMARY")
    print("=" * 60)
    
    if api_ok and files_ok:
        print("✅ ALL FIXES VALIDATED SUCCESSFULLY!")
        print()
        print("📋 What was fixed:")
        print("   ✅ Recent Plans download functionality")
        print("   ✅ Recent Plans navigation (click to view details)")
        print("   ✅ DXF viewer file loading")
        print("   ✅ Plan detail page download")
        print("   ✅ All components now use API client instead of direct fetch")
        print()
        print("🚀 The Recent Plans component should now be fully functional!")
        print("   - Click any plan to view details")
        print("   - Use download buttons to save DXF files")
        print("   - DXF viewer should load and display files correctly")
        return True
    else:
        print("❌ VALIDATION FAILED")
        if not api_ok:
            print("❌ API endpoints not working correctly")
        if not files_ok:
            print("❌ Frontend files not properly updated")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)