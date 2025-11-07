#!/usr/bin/env python3
"""Gradual server build to isolate the shutdown issue"""

import os
import sys

print("Testing main server components...")

# Set environment
os.environ["OPENAI_API_KEY"] = "dummy"

try:
    print("1. Basic imports...")
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi import WebSocket, WebSocketDisconnect
    print("   ✅ FastAPI and CORS imported")
except Exception as e:
    print(f"   ❌ FastAPI import failed: {e}")
    sys.exit(1)

try:
    print("2. AI-CAD imports...")
    from src.utils import get_logger, settings
    from src.database import init_database, get_db, PlanService, MetricsService
    from src.tools import tool_registry
    from src.cad.dxf_generator import DXFGenerator
    from src.cad.entity_manager import EntityManager
    from src.cad.layout_optimizer import LayoutOptimizer
    from src.ai_agent.openai_client import OpenAIClient
    from src.websocket_manager import websocket_manager
    print("   ✅ All AI-CAD modules imported")
except Exception as e:
    print(f"   ❌ AI-CAD imports failed: {e}")
    sys.exit(1)

try:
    print("3. Database initialization...")
    init_database()
    print("   ✅ Database initialized")
except Exception as e:
    print(f"   ❌ Database init failed: {e}")
    sys.exit(1)

try:
    print("4. Creating FastAPI app...")
    app = FastAPI(
        title="AI-CAD Automation API",
        description="AI-assisted architectural floor plan generation system",
        version="0.1.0"
    )
    print("   ✅ FastAPI app created")
except Exception as e:
    print(f"   ❌ FastAPI app creation failed: {e}")
    sys.exit(1)

try:
    print("5. Adding CORS middleware...")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    print("   ✅ CORS middleware added")
except Exception as e:
    print(f"   ❌ CORS middleware failed: {e}")
    sys.exit(1)

try:
    print("6. Adding basic endpoints...")
    logger = get_logger(__name__)
    
    @app.get("/")
    async def root():
        return {
            "message": "AI-CAD Automation API",
            "version": "0.1.0",
            "status": "running"
        }

    @app.get("/api/v1/health")
    async def health_check():
        from datetime import datetime
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "0.1.0"
        }
    
    @app.websocket("/ws/plans/{plan_id}")
    async def websocket_endpoint(websocket: WebSocket, plan_id: str):
        await websocket.accept()
        await websocket.send_json({
            "type": "connection_established",
            "connection_id": f"test_{plan_id}",
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
    
    print("   ✅ Basic endpoints added")
except Exception as e:
    print(f"   ❌ Endpoint creation failed: {e}")
    sys.exit(1)

print("\n🎉 All components loaded successfully!")
print("Running enhanced debug server...")

import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8103, log_level="info")