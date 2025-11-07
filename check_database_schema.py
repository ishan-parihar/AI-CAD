#!/usr/bin/env python3
"""Check database schema and status"""

import sys
import os
sys.path.append('/home/ishanp/Documents/GitHub/AI-CAD/backend')

try:
    from src.database.database import engine, Base
    import sqlite3
    
    # Check SQLite database directly
    db_path = "/home/ishanp/Documents/GitHub/AI-CAD/backend/aicad.db"
    print(f"Database path: {db_path}")
    print(f"Database exists: {os.path.exists(db_path)}")
    
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"Database size: {size} bytes")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # List tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables found: {[table[0] for table in tables]}")
        
        # Check plans table structure
        if ('plans',) in tables:
            cursor.execute("PRAGMA table_info(plans);")
            columns = cursor.fetchall()
            print("Plans table structure:")
            for col in columns:
                print(f"  - {col[1]}: {col[2]} (nullable: {col[3] == 0})")
            
            # Count records
            cursor.execute("SELECT COUNT(*) FROM plans;")
            count = cursor.fetchone()[0]
            print(f"Plans table record count: {count}")
            
            # Show sample records if any
            if count > 0:
                cursor.execute("SELECT id, name, status, created_at FROM plans LIMIT 5;")
                records = cursor.fetchall()
                print("Sample records:")
                for record in records:
                    print(f"  - {record}")
        
        conn.close()
    
    # Check SQLAlchemy models
    print("\n" + "="*50)
    print("SQLAlchemy Model Check:")
    
    from src.database.models import Plan
    
    # Show model columns
    print("Plan model columns:")
    for column in Plan.__table__.columns:
        print(f"  - {column.name}: {column.type} (nullable: {column.nullable})")
    
    # Test database creation
    print("\n" + "="*50)
    print("Testing database creation...")
    
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified")
    
except Exception as e:
    print(f"❌ Database check failed: {e}")
    import traceback
    traceback.print_exc()