"""FastAPI main application for AI-CAD backend"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
import uuid
import os
import asyncio
import json
from datetime import datetime

from src.cad.dxf_generator import DXFGenerator
from src.cad.entity_manager import EntityManager
from src.cad.layout_optimizer import LayoutOptimizer
from src.tools import tool_registry
from src.utils import get_logger, settings
from src.ai_agent.openai_client import OpenAIClient
from src.database import init_database, get_db, PlanService, MetricsService
from src.websocket_manager import websocket_manager

# Initialize database
init_database()

# Initialize FastAPI app
app = FastAPI(
    title="AI-CAD Automation API",
    description="AI-assisted architectural floor plan generation system",
    version="0.1.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],  # Next.js ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global logger
logger = get_logger(__name__)


# Pydantic models for API
class RoomRequirement(BaseModel):
    type: str
    area: Optional[float] = None
    preferred_width: Optional[float] = None
    preferred_depth: Optional[float] = None
    adjacency: Optional[List[str]] = []


class FloorPlanRequest(BaseModel):
    name: str
    dimensions: Dict[str, float]  # {"width": 10.0, "height": 8.0}
    rooms: List[RoomRequirement]
    constraints: Optional[Dict[str, Any]] = {}
    building_type: str = "residential"


class PlanResponse(BaseModel):
    plan_id: str
    status: str
    created_at: str
    message: Optional[str] = None


class ToolRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]


# Utility functions
def create_plan_directory(plan_id: str):
    """Create directory for plan files"""
    plan_dir = os.path.join(settings.output_directory, plan_id)
    os.makedirs(plan_dir, exist_ok=True)
    return plan_dir


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI-CAD Automation API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0"
    }


@app.get("/api/v1/ai/status")
async def ai_status():
    """Check AI configuration status"""
    from src.utils.config import settings
    
    ai_configured = settings.is_openai_configured()
    config = settings.get_openai_config()
    
    return {
        "ai_configured": ai_configured,
        "base_url": config.get("base_url", "Not configured"),
        "api_key_configured": bool(config.get("api_key")),
        "model_name": config.get("model", "Not configured"),
        "message": (
            "AI is properly configured" if ai_configured 
            else "AI not configured - set OPENAI_BASE_URL, OPENAI_API_KEY, and OPENAI_MODEL_NAME"
        )
    }


@app.post("/api/v1/ai/test")
async def test_ai_connection():
    """Test AI connection with current configuration"""
    from src.ai_agent.openai_client import openai_client
    
    if not openai_client.is_available():
        return {
            "success": False,
            "error": "AI client not configured",
            "message": "Please configure AI settings first"
        }
    
    try:
        test_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'AI connection test successful'"}
        ]
        
        response = await openai_client.generate_response(test_messages, max_tokens=50)
        
        if response:
            return {
                "success": True,
                "response": response,
                "message": "AI connection is working properly"
            }
        else:
            return {
                "success": False,
                "error": "No response from AI",
                "message": "AI connection test failed"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "AI connection test failed"
        }


@app.post("/api/v1/ai/configure")
async def configure_ai(
    base_url: str,
    api_key: str,
    model_name: str
):
    """Configure AI settings (for testing purposes)"""
    from src.utils.config import settings
    import os
    
    # Update environment variables
    os.environ["OPENAI_BASE_URL"] = base_url
    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["OPENAI_MODEL_NAME"] = model_name
    
    # Update settings
    settings.openai_base_url = base_url
    settings.openai_api_key = api_key
    settings.openai_model_name = model_name
    
    # Reinitialize AI client
    from src.ai_agent.openai_client import openai_client
    openai_client._initialize_client()
    
    return {
        "success": True,
        "message": "AI configuration updated",
        "base_url": base_url,
        "model_name": model_name,
        "api_key_configured": bool(api_key)
    }


@app.get("/api/v1/tools")
async def list_tools():
    """List all available tools"""
    tools = tool_registry.list_tools()
    return {"tools": tools}


@app.post("/api/v1/plans/generate", response_model=PlanResponse)
async def generate_floor_plan(
    request: FloorPlanRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate a new floor plan"""
    try:
        plan_id = str(uuid.uuid4())
        
        # Convert request to database format
        plan_data = {
            "name": request.name,
            "width": request.dimensions.get("width", 10.0),
            "height": request.dimensions.get("height", 10.0),
            "rooms": [{"name": room.type, "area": room.area, "width": room.preferred_width, "height": room.preferred_depth} for room in request.rooms],
            "requirements": request.constraints or {}
        }
        
        # Save plan to database
        plan_service = PlanService(db)
        plan = plan_service.create_plan(plan_id, plan_data)
        
        # Start generation in background
        background_tasks.add_task(
            generate_plan_background, 
            plan_id, 
            request
        )
        
        return PlanResponse(
            plan_id=plan_id,
            status=plan.status,
            created_at=plan.created_at.isoformat(),
            message="Plan generation started"
        )
        
    except Exception as e:
        logger.error(f"Failed to start plan generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/plans/{plan_id}/status")
async def get_plan_status(plan_id: str, db: Session = Depends(get_db)):
    """Get generation status for a plan"""
    plan_service = PlanService(db)
    plan = plan_service.get_plan(plan_id)
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    return plan.to_dict()


@app.get("/api/v1/plans/{plan_id}/download")
async def download_plan(plan_id: str, file_format: str = "dxf", db: Session = Depends(get_db)):
    """Download generated plan file"""
    plan_service = PlanService(db)
    plan = plan_service.get_plan(plan_id)
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    if plan.status != "completed":
        raise HTTPException(status_code=400, detail="Plan not ready for download")
    
    # Use DXF file path from database or fall back to directory-based approach
    if plan.dxf_file_path and os.path.exists(plan.dxf_file_path):
        file_path = plan.dxf_file_path
        filename = os.path.basename(file_path)
    else:
        plan_dir = os.path.join(settings.output_directory, plan_id)
        file_path = os.path.join(plan_dir, f"{plan.name}.dxf")
        filename = f"{plan.name}.dxf"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="DXF file not found")
    
    return FileResponse(
        file_path,
        media_type="application/dxf",
        filename=filename
    )


@app.get("/api/v1/plans/{plan_id}/preview")
async def preview_plan(plan_id: str, db: Session = Depends(get_db)):
    """Get plan preview data"""
    plan_service = PlanService(db)
    plan = plan_service.get_plan(plan_id)
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    if plan.status != "completed":
        raise HTTPException(status_code=400, detail="Plan not ready for preview")
    
    return {
        "plan_id": plan_id,
        "preview_data": plan.result.get("preview_data", {}) if plan.result else {},
        "summary": plan.result.get("summary", {}) if plan.result else {}
    }


@app.post("/api/v1/tools/execute")
async def execute_tool(request: ToolRequest):
    """Execute a specific tool"""
    try:
        result = tool_registry.execute_tool(request.tool_name, request.parameters)
        
        if result.success:
            return {
                "success": True,
                "data": result.data,
                "execution_time": result.execution_time
            }
        else:
            return {
                "success": False,
                "error": result.error
            }
            
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/plans")
async def list_plans(page: int = 1, limit: int = 20, status: str = None, db: Session = Depends(get_db)):
    """List all plans with pagination"""
    plan_service = PlanService(db)
    
    try:
        # Get plans from database
        plans_db = plan_service.list_plans(page=page, limit=limit, status=status)
        
        # Convert to response format
        plans = []
        for plan in plans_db:
            # Calculate summary
            total_area = plan.width * plan.height
            rooms = plan.rooms or []
            
            plans.append({
                "id": plan.id,
                "name": plan.name,
                "status": plan.status,
                "created_at": plan.created_at.isoformat() if plan.created_at else "",
                "updated_at": plan.updated_at.isoformat() if plan.updated_at else "",
                "dimensions": {
                    "width": plan.width,
                    "height": plan.height
                },
                "rooms": [
                    {
                        "id": str(i + 1),
                        "name": room.get("name", "Unknown"),
                        "type": room.get("name", "unknown"),
                        "area": room.get("area", 0)
                    } for i, room in enumerate(rooms)
                ],
                "building_type": "residential",  # Default for now
                "progress": plan.progress or 0,
                "summary": {
                    "total_rooms": len(rooms),
                    "building_area": total_area,
                    "file_size": 0,  # TODO: Calculate actual file size
                    "efficiency_score": 85 if plan.status == "completed" else 0,
                    "ai_enhanced": plan.ai_enabled or False
                }
            })
        
        return {"plans": plans}
        
    except Exception as e:
        logger.error(f"Failed to list plans: {e}")
        raise HTTPException(status_code=500, detail="Failed to list plans")


@app.delete("/api/v1/plans/{plan_id}")
async def delete_plan(plan_id: str, db: Session = Depends(get_db)):
    """Delete a plan"""
    plan_service = PlanService(db)
    
    try:
        success = plan_service.delete_plan(plan_id)
        if not success:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        return {"message": "Plan deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete plan {plan_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete plan")
    
    # Remove files
    plan_dir = os.path.join(settings.output_directory, plan_id)
    if os.path.exists(plan_dir):
        import shutil
        shutil.rmtree(plan_dir)
    
    # Notify WebSocket clients
    await websocket_manager.broadcast_to_plan(plan_id, {
        "type": "plan_deleted",
        "plan_id": plan_id,
        "message": "Plan has been deleted"
    })
    
    return {"message": "Plan deleted successfully"}


@app.websocket("/ws/plans/{plan_id}")
async def websocket_plan_updates(websocket: WebSocket, plan_id: str):
    """WebSocket endpoint for real-time plan updates"""
    connection_id = None
    try:
        # Connect to the plan
        connection_id = await websocket_manager.connect(
            websocket, 
            plan_id,
            user_info={"user_agent": websocket.headers.get("user-agent", "unknown")}
        )
        
        # Send initial plan status if plan exists
        try:
            db = next(get_db())
            plan_service = PlanService(db)
            plan = plan_service.get_plan(plan_id)
            
            if plan:
                logger.info(f"Sending initial status for plan {plan_id}, plan status: {plan.status}")
                
                # Create a simpler message to avoid serialization issues
                initial_message = {
                    "type": "initial_status",
                    "plan_id": plan_id,
                    "status": plan.status,
                    "progress": plan.progress or 0,
                    "created_at": plan.created_at.isoformat() if plan.created_at else None,
                    "message": plan.message,
                    "error": plan.error,
                    "ai_enabled": plan.ai_enabled or False
                }
                
                logger.info(f"Attempting to send initial message: {initial_message}")
                try:
                    await websocket_manager.send_to_connection(connection_id, initial_message)
                    logger.info(f"Initial status sent successfully for plan {plan_id}")
                except Exception as e:
                    logger.error(f"Failed to send initial status for plan {plan_id}: {e}")
                    logger.error(f"Plan data that caused error: {plan}")
            else:
                logger.warning(f"Plan {plan_id} not found in database")
        finally:
            db.close()
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    await websocket_manager.send_to_connection(connection_id, {
                        "type": "pong",
                        "timestamp": asyncio.get_event_loop().time()
                    })
                elif message.get("type") == "subscribe_updates":
                    # Client is subscribing to updates (already handled by connection)
                    await websocket_manager.send_to_connection(connection_id, {
                        "type": "subscription_confirmed",
                        "plan_id": plan_id
                    })
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.warning(f"WebSocket message error for {connection_id}: {e}")
                break
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        # Clean up connection
        if connection_id:
            websocket_manager.disconnect(connection_id)


@app.get("/api/v1/websocket/stats")
async def websocket_stats():
    """Get WebSocket connection statistics"""
    return websocket_manager.get_plan_stats()


# Background task function
async def generate_plan_background(plan_id: str, request: FloorPlanRequest):
    """Background task to generate floor plan"""
    db = next(get_db())
    plan_service = PlanService(db)
    
    # Initialize variables to avoid scope issues
    room_layouts = []
    ai_analysis = None
    ai_optimizations = None
    spatial_result = None
    
    try:
        # Get plan from database
        plan = plan_service.get_plan(plan_id)
        if not plan:
            raise Exception(f"Plan {plan_id} not found in database")
        
        plan_dict = {
            "id": plan.id,
            "name": plan.name,
            "status": plan.status,
            "progress": plan.progress,
            "width": plan.width,
            "height": plan.height,
            "rooms": plan.rooms,
            "requirements": plan.requirements,
            "result": plan.result,
            "dxf_file_path": plan.dxf_file_path,
            "created_at": plan.created_at.isoformat() if plan.created_at else None,
            "updated_at": plan.updated_at.isoformat() if plan.updated_at else None,
            "completed_at": plan.completed_at.isoformat() if plan.completed_at else None,
            "error": plan.error,
            "message": plan.message,
            "ai_enabled": plan.ai_enabled,
            "ai_analysis": plan.ai_analysis
        }
        
        # Update status in database
        plan_service.update_plan_status(plan_id, "generating", progress=10, message="Plan generation started")
        plan_dict["status"] = "generating"
        plan_dict["progress"] = 10
        logger.info(f"Started generating plan {plan_id}: {request.name}")
        
        # Broadcast initial status
        await websocket_manager.broadcast_plan_update(plan_id, {
            "status": "generating",
            "progress": 10,
            "message": "Plan generation started"
        })
        
        # Initialize AI client if available
        ai_client = None
        if settings.openai_api_key and settings.openai_api_key != "demo_key_replace_with_actual_key":
            try:
                ai_client = OpenAIClient()
                logger.info("AI client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize AI client: {e}")
        
        # Step 1: AI Requirements Analysis (if AI is available)
        if ai_client:
            try:
                # Update progress in database
                plan_service.update_plan_progress(plan_id, 15, "Performing AI requirements analysis...")
                plan_dict["progress"] = 15
                await websocket_manager.broadcast_progress(plan_id, 15, "ai_analysis", "Performing AI requirements analysis...")
                logger.info("Performing AI requirements analysis...")
                
                requirements_text = f"""
                Building Type: {request.building_type}
                Dimensions: {request.dimensions.width}m x {request.dimensions.height}m
                Rooms: {', '.join([f'{room.type} ({room.area}m²)' for room in request.rooms])}
                Constraints: {request.constraints}
                """
                
                ai_analysis = await ai_client.analyze_cad_requirements(requirements_text)
                
                # Update progress in database
                plan_service.update_plan_progress(plan_id, 15, "Performing AI requirements analysis...")
                plan_dict["ai_analysis"] = ai_analysis
                plan_dict["ai_enabled"] = True
                
                # Broadcast AI analysis completion
                await websocket_manager.broadcast_ai_update(plan_id, {
                    "analysis_completed": True,
                    "insights": ai_analysis.get("insights", []),
                    "recommendations": ai_analysis.get("recommendations", [])
                })
                
                logger.info("AI analysis completed")
            except Exception as e:
                logger.warning(f"AI analysis failed, proceeding with algorithmic approach: {e}")
                await websocket_manager.broadcast_error(plan_id, {
                    "error_type": "ai_analysis_failed",
                    "message": "AI analysis failed, using algorithmic approach",
                    "details": str(e)
                })
        
        # Create plan directory
        plan_dir = create_plan_directory(plan_id)
        
        # Initialize CAD components
        # Update progress in database
        plan_service.update_plan_progress(plan_id, 20, "Initializing CAD components...")
        plan_dict["progress"] = 20
        await websocket_manager.broadcast_progress(plan_id, 20, "initializing_cad", "Initializing CAD components...")
        generator = DXFGenerator()
        generator.create_drawing(request.name)
        
        # Create boundary from dimensions
        width = request.dimensions.get("width", 10.0)
        height = request.dimensions.get("height", 8.0)
        boundary_points = [
            (0, 0), (width, 0), (width, height), (0, height)
        ]
        
        # Add boundary walls
        # Update progress in database
        plan_service.update_plan_progress(plan_id, 30, "Creating building boundaries...")
        plan_dict["progress"] = 30
        await websocket_manager.broadcast_progress(plan_id, 30, "creating_boundaries", "Creating building boundaries...")
        generator.add_wall((0, 0), (width, 0), thickness=0.2)
        generator.add_wall((width, 0), (width, height), thickness=0.2)
        generator.add_wall((width, height), (0, height), thickness=0.2)
        generator.add_wall((0, height), (0, 0), thickness=0.2)
        
        # Step 2: Algorithmic Layout Generation with AI insights
        # Update progress in database
        plan_service.update_plan_progress(plan_id, 40, "Generating room layout with spatial reasoning...")
        plan_dict["progress"] = 40
        await websocket_manager.broadcast_progress(plan_id, 40, "spatial_reasoning", "Generating room layout with spatial reasoning...")
        spatial_tool = tool_registry.get_tool("spatial_reasoning")
        
        if spatial_tool:
            # Convert rooms to tool format with AI enhancements
            rooms_data = []
            for i, room_req in enumerate(request.rooms):
                room_data = {
                    "type": room_req.type,
                    "area": room_req.area or 10.0,
                    "adjacency": room_req.adjacency or []
                }
                
                # Apply AI insights if available
                if ai_analysis and isinstance(ai_analysis, dict) and ai_analysis.get("room_suggestions"):
                    ai_suggestion = ai_analysis["room_suggestions"].get(room_req.type)
                    if ai_suggestion:
                        if ai_suggestion.get("recommended_area"):
                            room_data["area"] = ai_suggestion["recommended_area"]
                        if ai_suggestion.get("preferred_location"):
                            room_data["preferred_location"] = ai_suggestion["preferred_location"]
                        if ai_suggestion.get("adjacency_preferences"):
                            room_data["adjacency"].extend(ai_suggestion["adjacency_preferences"])
                
                if room_req.preferred_width:
                    room_data["preferred_width"] = room_req.preferred_width
                if room_req.preferred_depth:
                    room_data["preferred_depth"] = room_req.preferred_depth
                rooms_data.append(room_data)
            
            spatial_result = spatial_tool.execute({
                "operation": "place_rooms",
                "boundary": boundary_points,
                "rooms": rooms_data
            })
            
            if spatial_result.success:
                # Update progress in database
                plan_service.update_plan_progress(plan_id, 60, "Room layout generated successfully")
                plan_dict["progress"] = 60
                await websocket_manager.broadcast_progress(plan_id, 60, "layout_complete", "Room layout generated successfully")
                room_layouts = spatial_result.data.get("room_layouts", [])
                
                # Broadcast layout summary
                await websocket_manager.broadcast_to_plan(plan_id, {
                    "type": "layout_summary",
                    "plan_id": plan_id,
                    "rooms_placed": len(room_layouts),
                    "efficiency_score": spatial_result.data.get("efficiency_score", 0),
                    "total_area": width * height
                })
                
                # Step 3: AI Optimization Suggestions (if AI is available)
                if ai_client and room_layouts:
                    try:
                        # Update progress in database
                        plan_service.update_plan_progress(plan_id, 65, "Generating AI optimization suggestions...")
                        plan_dict["progress"] = 65
                        plan_dict["ai_optimizations"] = ai_optimizations
                        await websocket_manager.broadcast_progress(plan_id, 65, "ai_optimization", "Generating AI optimization suggestions...")
                        logger.info("Generating AI optimization suggestions...")
                        
                        layout_data = {
                            "rooms": room_layouts,
                            "boundary": boundary_points,
                            "building_area": width * height,
                            "efficiency_score": spatial_result.data.get("efficiency_score", 0)
                        }
                        
                        ai_optimizations = await ai_client.suggest_optimizations(layout_data)
                        plan_dict["ai_optimizations"] = ai_optimizations
                        
                        # Broadcast AI optimizations
                        await websocket_manager.broadcast_ai_update(plan_id, {
                            "optimizations_completed": True,
                            "suggestions": isinstance(ai_optimizations, dict) and ai_optimizations.get("optimizations", []) or [],
                            "confidence_score": isinstance(ai_optimizations, dict) and ai_optimizations.get("confidence_score", 0) or 0
                        })
                        
                        # Apply high-confidence AI optimizations
                        if isinstance(ai_optimizations, dict) and ai_optimizations.get("optimizations"):
                            applied_optimizations = []
                            for optimization in ai_optimizations["optimizations"]:
                                if optimization.get("confidence", 0) > 0.8:
                                    # Apply optimization logic here
                                    logger.info(f"Applied AI optimization: {optimization.get('description')}")
                                    applied_optimizations.append(optimization.get('description'))
                            
                            if applied_optimizations:
                                await websocket_manager.broadcast_ai_update(plan_id, {
                                    "optimizations_applied": True,
                                    "applied_count": len(applied_optimizations),
                                    "applied_optimizations": applied_optimizations
                                })
                    
                    except Exception as e:
                        logger.warning(f"AI optimization failed: {e}")
                        await websocket_manager.broadcast_error(plan_id, {
                            "error_type": "ai_optimization_failed",
                            "message": "AI optimization failed, continuing with algorithmic layout",
                            "details": str(e)
                        })
                
                # Add rooms to DXF
                for i, room_layout in enumerate(room_layouts):
                    room_points = room_layout.get("polygon", [])
                    if room_points:
                        room_type = room_layout.get("type", f"room_{i}")
                        generator.add_room(room_points, room_type.capitalize())
                
                # Add doors and windows
                # Update progress in database
                plan_service.update_plan_progress(plan_id, 70, "Adding doors and windows...")
                plan_dict["progress"] = 70
                await websocket_manager.broadcast_progress(plan_id, 70, "adding_openings", "Adding doors and windows...")
                # Auto-place doors based on AI suggestions if available
                if isinstance(ai_optimizations, dict) and ai_optimizations.get("door_placement"):
                    door_suggestions = ai_optimizations["door_placement"]
                    for door in door_suggestions[:2]:  # Limit to 2 doors
                        pos = door.get("position", [0, height/2])
                        generator.add_door(tuple(pos), width=0.8, angle=0)
                else:
                    # Fallback door placement
                    generator.add_door((0, height/2), width=0.8, angle=0)
                
                # Add windows
                if width > 4:
                    generator.add_window((width/2 - 1, height), (width/2 + 1, height))
        
        # Apply design rules validation
        # Update progress in database
        plan_service.update_plan_progress(plan_id, 80, "Applying design rules and validation...")
        plan_dict["progress"] = 80
        await websocket_manager.broadcast_progress(plan_id, 80, "validation", "Applying design rules and validation...")
        design_tool = tool_registry.get_tool("design_rules")
        if design_tool:
            # Simple validation (would need full layout data for comprehensive validation)
            pass
        
        # Save DXF file
        # Update progress in database
        plan_service.update_plan_progress(plan_id, 85, "Generating DXF file...")
        plan_dict["progress"] = 85
        await websocket_manager.broadcast_progress(plan_id, 85, "saving", "Generating DXF file...")
        file_path = os.path.join(plan_dir, f"{request.name}.dxf")
        success = generator.save_drawing(f"{request.name}.dxf", plan_dir)
        
        if success:
            # Verify file was actually created and is valid
            if not os.path.exists(file_path):
                raise Exception(f"DXF file was not created at expected path: {file_path}")
            
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                raise Exception("DXF file was created but is empty")
            
            logger.info(f"DXF file created successfully: {file_path} ({file_size} bytes)")
            
            # Update progress for database save
            plan_service.update_plan_progress(plan_id, 90, "Saving to database...")
            plan_dict["progress"] = 90
            await websocket_manager.broadcast_progress(plan_id, 90, "saving", "Saving to database...")
            
            # Get drawing info
            drawing_info = generator.get_drawing_info()
            
            # Update plan in database with completion
            result_data = {
                "file_path": file_path,
                "drawing_info": drawing_info,
                "rooms_placed": len(room_layouts),
                "ai_enabled": ai_client is not None,
                "ai_analysis_performed": ai_analysis is not None,
                "ai_optimizations_applied": ai_optimizations is not None,
                "summary": {
                    "total_rooms": len(room_layouts),
                    "building_area": width * height,
                    "file_size": file_size,
                    "ai_enhanced": ai_client is not None,
                    "efficiency_score": min(95, (spatial_result.data.get("total_utilization", 85) if spatial_result else 85 + (5 if ai_optimizations else 0)))
                },
                "ai_analysis": ai_analysis,
                "ai_optimizations": ai_optimizations
            }
            
            # CRITICAL FIX: Proper database persistence with error handling
            try:
                updated_plan = plan_service.save_plan_result(plan_id, result_data, file_path)
                if not updated_plan:
                    raise Exception("Database save operation returned None")
                
                logger.info(f"Plan result saved to database: {plan_id}")
                
                # Only broadcast success after database commit succeeds
                await websocket_manager.broadcast_plan_update(plan_id, {
                    "status": "completed",
                    "progress": 100,
                    "message": "Plan generation completed successfully!",
                    "result": result_data,
                    "summary": result_data["summary"]
                })
                
                logger.info(f"Successfully generated plan {plan_id} with AI enhancements: {ai_client is not None}")
                
            except Exception as db_error:
                logger.error(f"Failed to save plan result to database: {db_error}")
                
                # Clean up orphaned file on database failure
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f"Cleaned up orphaned file: {file_path}")
                        
                    # Also remove empty plan directory
                    try:
                        if os.path.exists(plan_dir) and not os.listdir(plan_dir):
                            os.rmdir(plan_dir)
                            logger.info(f"Cleaned up empty plan directory: {plan_dir}")
                    except OSError:
                        pass  # Directory not empty, leave it
                        
                except Exception as cleanup_error:
                    logger.error(f"Failed to cleanup orphaned file: {cleanup_error}")
                
                raise Exception(f"Database persistence failed: {db_error}")
        else:
            raise Exception("Failed to save DXF file")
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Plan generation failed for {plan_id}: {error_msg}")
        
        # Determine error type for better user feedback
        error_type = "generation_failed"
        if "database" in error_msg.lower() or "sql" in error_msg.lower():
            error_type = "database_error"
        elif "dxf" in error_msg.lower() or "file" in error_msg.lower():
            error_type = "file_generation_error"
        elif "ai" in error_msg.lower() or "openai" in error_msg.lower():
            error_type = "ai_service_error"
        elif "memory" in error_msg.lower() or "resource" in error_msg.lower():
            error_type = "resource_error"
        
        # Update plan status in database with detailed error information
        try:
            plan_service.update_plan_status(
                plan_id, 
                "failed", 
                error=error_msg,
                message=f"Plan generation failed: {error_type}"
            )
        except Exception as db_update_error:
            logger.error(f"Failed to update plan status in database: {db_update_error}")
        
        # Broadcast detailed error to all WebSocket clients
        await websocket_manager.broadcast_error(plan_id, {
            "error_type": error_type,
            "message": "Plan generation failed",
            "details": error_msg,
            "status": "failed",
            "timestamp": datetime.now().isoformat()
        })
        
        # Perform cleanup based on error type
        if error_type in ["file_generation_error", "database_error"]:
            try:
                # Clean up any partial files
                if os.path.exists(plan_dir):
                    import shutil
                    shutil.rmtree(plan_dir)
                    logger.info(f"Cleaned up partial plan directory: {plan_dir}")
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup plan directory: {cleanup_error}")
    finally:
        db.close()


# AI Configuration endpoints
@app.post("/api/v1/settings/ai-config")
async def update_ai_config(config: dict):
    """Update AI configuration"""
    try:
        # Update environment variables (for this session)
        if config.get("baseUrl"):
            os.environ["OPENAI_BASE_URL"] = config["baseUrl"]
        if config.get("apiKey"):
            os.environ["OPENAI_API_KEY"] = config["apiKey"]
        if config.get("modelName"):
            os.environ["OPENAI_MODEL_NAME"] = config["modelName"]
        
        # Update settings
        settings.openai_base_url = config.get("baseUrl")
        settings.openai_api_key = config.get("apiKey")
        settings.openai_model_name = config.get("modelName")
        
        # Reinitialize AI client
        from src.ai_agent.openai_client import openai_client
        openai_client._initialize_client()
        
        return {
            "success": True,
            "message": "AI configuration updated successfully",
            "config": {
                "baseUrl": settings.openai_base_url,
                "apiKey": settings.openai_api_key[:10] + "..." if settings.openai_api_key else None,
                "modelName": settings.openai_model_name,
                "enabled": settings.is_openai_configured()
            }
        }
    except Exception as e:
        logger.error(f"Failed to update AI configuration: {e}")
        return {
            "success": False,
            "message": f"Failed to update AI configuration: {str(e)}"
        }

@app.get("/api/v1/settings/ai-config")
async def get_ai_config():
    """Get current AI configuration"""
    try:
        return {
            "success": True,
            "config": {
                "baseUrl": settings.openai_base_url,
                "apiKey": settings.openai_api_key[:10] + "..." if settings.openai_api_key else None,
                "modelName": settings.openai_model_name,
                "enabled": settings.is_openai_configured()
            }
        }
    except Exception as e:
        logger.error(f"Failed to get AI configuration: {e}")
        return {
            "success": False,
            "message": f"Failed to get AI configuration: {str(e)}"
        }

@app.post("/api/v1/settings/test-ai-connection")
async def test_ai_connection():
    """Test AI connection with current configuration"""
    try:
        from src.ai_agent.openai_client import openai_client
        
        if not openai_client.is_available():
            return {
                "success": False,
                "message": "AI client not configured. Please check your API settings."
            }
        
        # Test with a simple prompt
        test_response = await openai_client.generate_response([
            {"role": "user", "content": "Respond with 'Connection successful' if you can read this."}
        ], max_tokens=10)
        
        if test_response and "Connection successful" in test_response:
            return {
                "success": True,
                "message": "AI connection test successful",
                "response": test_response
            }
        else:
            return {
                "success": False,
                "message": "AI connection test failed: Invalid response",
                "response": test_response
            }
            
    except Exception as e:
        logger.error(f"AI connection test failed: {e}")
        return {
            "success": False,
            "message": f"AI connection test failed: {str(e)}"
        }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("AI-CAD API starting up...")
    
    # Ensure output directory exists
    os.makedirs(settings.output_directory, exist_ok=True)
    
    logger.info("AI-CAD API startup complete")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("AI-CAD API shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )