#!/usr/bin/env python3
"""Step-by-step server startup to isolate the issue"""

import os
import sys

print("Testing imports...")

try:
    print("1. FastAPI...")
    from fastapi import FastAPI
    print("   ✅ FastAPI imported")
except Exception as e:
    print(f"   ❌ FastAPI failed: {e}")
    sys.exit(1)

try:
    print("2. Utils...")
    from src.utils import get_logger, settings
    print("   ✅ Utils imported")
except Exception as e:
    print(f"   ❌ Utils failed: {e}")
    sys.exit(1)

try:
    print("3. Database...")
    from src.database import init_database, get_db, PlanService, MetricsService
    print("   ✅ Database imported")
except Exception as e:
    print(f"   ❌ Database failed: {e}")
    sys.exit(1)

try:
    print("4. Initializing database...")
    init_database()
    print("   ✅ Database initialized")
except Exception as e:
    print(f"   ❌ Database init failed: {e}")
    sys.exit(1)

try:
    print("5. Tools...")
    from src.tools import tool_registry
    print("   ✅ Tools imported")
except Exception as e:
    print(f"   ❌ Tools failed: {e}")
    sys.exit(1)

try:
    print("6. CAD modules...")
    from src.cad.dxf_generator import DXFGenerator
    from src.cad.entity_manager import EntityManager
    from src.cad.layout_optimizer import LayoutOptimizer
    print("   ✅ CAD modules imported")
except Exception as e:
    print(f"   ❌ CAD modules failed: {e}")
    sys.exit(1)

try:
    print("7. AI client...")
    from src.ai_agent.openai_client import OpenAIClient
    print("   ✅ AI client imported")
except Exception as e:
    print(f"   ❌ AI client failed: {e}")
    sys.exit(1)

try:
    print("8. WebSocket manager...")
    from src.websocket_manager import websocket_manager
    print("   ✅ WebSocket manager imported")
except Exception as e:
    print(f"   ❌ WebSocket manager failed: {e}")
    sys.exit(1)

try:
    print("9. Creating FastAPI app...")
    from fastapi import WebSocket, WebSocketDisconnect
    app = FastAPI(title="Test App")
    
    @app.get("/")
    async def root():
        return {"status": "ok", "message": "Debug server running"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "timestamp": "2025-11-06T03:17:00Z"}
    
    @app.websocket("/ws/plans/{plan_id}")
    async def websocket_endpoint(websocket: WebSocket, plan_id: str):
        await websocket.accept()
        await websocket.send_json({
            "type": "connection_established",
            "connection_id": f"debug_{plan_id}",
            "message": f"Connected to plan {plan_id}"
        })
        try:
            while True:
                data = await websocket.receive_text()
                await websocket.send_json({
                    "type": "echo",
                    "received": data,
                    "plan_id": plan_id
                })
        except WebSocketDisconnect:
            print(f"WebSocket disconnected for plan {plan_id}")
    
    print("   ✅ FastAPI app created with WebSocket endpoint")
except Exception as e:
    print(f"   ❌ FastAPI app creation failed: {e}")
    sys.exit(1)

print("\n🎉 All imports and initialization successful!")
print("Running simple server...")

import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8102, log_level="info")