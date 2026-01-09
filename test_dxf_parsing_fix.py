#!/usr/bin/env python3
"""
Test script to verify DXF parsing fix
"""
import asyncio
import websockets
import json

async def test_dxf_parsing_fix():
    print("🧪 Testing DXF Parsing Fix")
    print("=" * 40)
    print("Instructions:")
    print("1. Open browser to: http://localhost:3001/plans/471bfe76-0102-4317-ad0b-8634d75cec43")
    print("2. Open browser console (F12)")
    print("3. Look for these debugging messages:")
    print("   - 🔍 LWPOLYLINE coordinates extracted:")
    print("   - 🔍 LINE points extracted - start:")
    print("   - ✓ Created Fabric.js object for entity")
    print("4. Check if floor plan is visible in the viewer")
    print()
    print("Expected results:")
    print("- LWPOLYLINE entities should now have coordinates")
    print("- LINE entities should have start/end points")
    print("- More entities should render successfully")
    print("- Floor plan should be visible in the viewer")
    print()
    print("If still seeing blank viewer:")
    print("- Check console for any remaining errors")
    print("- Verify coordinates are being extracted correctly")
    print("- Check if fabric objects are being created")

if __name__ == "__main__":
    asyncio.run(test_dxf_parsing_fix())