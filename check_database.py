#!/usr/bin/env python3
"""Check all plans in database"""

import sys
import os
sys.path.append('/home/ishanp/Documents/GitHub/AI-CAD/backend')

try:
    from src.database.database import get_db
    from src.database.models import Plan
    
    db = next(get_db())
    plans = db.query(Plan).all()
    
    print(f"Found {len(plans)} plans in database:")
    for plan in plans:
        print(f"  - ID: {plan.id}")
        print(f"    Name: {plan.name}")
        print(f"    Status: {plan.status}")
        print(f"    DXF Path: {plan.dxf_file_path}")
        print(f"    Created: {plan.created_at}")
        print()
    
    db.close()
    
except Exception as e:
    print(f"❌ Database query failed: {e}")
    import traceback
    traceback.print_exc()