"""WebSocket manager for real-time plan updates"""

import json
import asyncio
from typing import Dict, Set, Any
from fastapi import WebSocket, WebSocketDisconnect
from .utils import get_logger

logger = get_logger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Store active connections: {plan_id: {connection_id: websocket}}
        self.plan_connections: Dict[str, Dict[str, WebSocket]] = {}
        # Store connection metadata: {connection_id: {plan_id, user_info, etc.}}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        self.connection_counter = 0
    
    async def connect(self, websocket: WebSocket, plan_id: str, user_info: Dict[str, Any] = None) -> str:
        """Connect a WebSocket to a specific plan"""
        await websocket.accept()
        
        # Generate unique connection ID
        self.connection_counter += 1
        connection_id = f"conn_{self.connection_counter}"
        
        # Add to plan connections
        if plan_id not in self.plan_connections:
            self.plan_connections[plan_id] = {}
        
        self.plan_connections[plan_id][connection_id] = websocket
        
        # Store metadata
        self.connection_metadata[connection_id] = {
            "plan_id": plan_id,
            "user_info": user_info or {},
            "connected_at": asyncio.get_event_loop().time()
        }
        
        logger.info(f"WebSocket connected: {connection_id} for plan {plan_id}")
        
        # Send initial connection confirmation
        await self.send_to_connection(connection_id, {
            "type": "connection_established",
            "connection_id": connection_id,
            "plan_id": plan_id
        })
        
        return connection_id
    
    def disconnect(self, connection_id: str):
        """Disconnect a WebSocket connection"""
        if connection_id in self.connection_metadata:
            plan_id = self.connection_metadata[connection_id]["plan_id"]
            
            # Remove from plan connections
            if plan_id in self.plan_connections and connection_id in self.plan_connections[plan_id]:
                del self.plan_connections[plan_id][connection_id]
                
                # Clean up empty plan entries
                if not self.plan_connections[plan_id]:
                    del self.plan_connections[plan_id]
            
            # Remove metadata
            del self.connection_metadata[connection_id]
            
            logger.info(f"WebSocket disconnected: {connection_id} from plan {plan_id}")
    
    async def send_to_connection(self, connection_id: str, message: Dict[str, Any]):
        """Send a message to a specific connection"""
        if connection_id in self.connection_metadata:
            plan_id = self.connection_metadata[connection_id]["plan_id"]
            
            if (plan_id in self.plan_connections and 
                connection_id in self.plan_connections[plan_id]):
                
                websocket = self.plan_connections[plan_id][connection_id]
                try:
                    # Validate message can be serialized
                    json_str = json.dumps(message)
                    await websocket.send_text(json_str)
                except Exception as e:
                    logger.error(f"Failed to send message to {connection_id}: {e}")
                    logger.error(f"Message that failed: {message}")
                    # Only disconnect if it's a connection error, not serialization error
                    if "connection" in str(e).lower() or "disconnect" in str(e).lower():
                        logger.info(f"Connection {connection_id} appears dead, cleaning up")
                        self.disconnect(connection_id)
                    else:
                        logger.warning(f"Serialization error for {connection_id}, keeping connection alive")
    
    async def broadcast_to_plan(self, plan_id: str, message: Dict[str, Any]):
        """Broadcast a message to all connections watching a plan"""
        if plan_id in self.plan_connections:
            disconnected_connections = []
            
            for connection_id, websocket in self.plan_connections[plan_id].items():
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.warning(f"Failed to broadcast to {connection_id}: {e}")
                    disconnected_connections.append(connection_id)
            
            # Clean up dead connections
            for connection_id in disconnected_connections:
                self.disconnect(connection_id)
    
    async def broadcast_plan_update(self, plan_id: str, status_data: Dict[str, Any]):
        """Send plan status update to all watchers"""
        message = {
            "type": "plan_update",
            "plan_id": plan_id,
            "timestamp": asyncio.get_event_loop().time(),
            **status_data
        }
        await self.broadcast_to_plan(plan_id, message)
    
    async def broadcast_ai_update(self, plan_id: str, ai_data: Dict[str, Any]):
        """Send AI analysis/optimization updates"""
        message = {
            "type": "ai_update",
            "plan_id": plan_id,
            "timestamp": asyncio.get_event_loop().time(),
            **ai_data
        }
        await self.broadcast_to_plan(plan_id, message)
    
    async def broadcast_error(self, plan_id: str, error_data: Dict[str, Any]):
        """Send error notification"""
        message = {
            "type": "error",
            "plan_id": plan_id,
            "timestamp": asyncio.get_event_loop().time(),
            **error_data
        }
        await self.broadcast_to_plan(plan_id, message)
    
    async def broadcast_progress(self, plan_id: str, progress: int, current_step: str, message: str = None):
        """Send progress update"""
        update_data = {
            "progress": progress,
            "current_step": current_step,
            "message": message or f"Step {current_step} in progress"
        }
        await self.broadcast_plan_update(plan_id, update_data)
    
    def get_connection_count(self, plan_id: str = None) -> int:
        """Get number of active connections, optionally filtered by plan"""
        if plan_id:
            return len(self.plan_connections.get(plan_id, {}))
        
        total = 0
        for plan_connections in self.plan_connections.values():
            total += len(plan_connections)
        return total
    
    def get_plan_stats(self) -> Dict[str, Any]:
        """Get statistics about active connections"""
        stats = {
            "total_connections": self.get_connection_count(),
            "plans_with_connections": len(self.plan_connections),
            "plan_details": {}
        }
        
        for plan_id, connections in self.plan_connections.items():
            stats["plan_details"][plan_id] = {
                "connection_count": len(connections),
                "connections": list(connections.keys())
            }
        
        return stats


# Global WebSocket manager instance
websocket_manager = WebSocketManager()