"""Database models for AI-CAD application"""

from sqlalchemy import Column, String, DateTime, Integer, Float, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

Base = declarative_base()


class Plan(Base):
    """Plan model for storing floor plan data"""
    __tablename__ = "plans"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="initializing")
    progress = Column(Integer, default=0)
    
    # Plan configuration
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    rooms = Column(JSON, nullable=True)
    requirements = Column(JSON, nullable=True)
    
    # Results
    result = Column(JSON, nullable=True)
    dxf_file_path = Column(String(500), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    # Error handling
    error = Column(Text, nullable=True)
    message = Column(Text, nullable=True)
    
    # AI features
    ai_enabled = Column(Boolean, default=False)
    ai_analysis = Column(JSON, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "progress": self.progress,
            "width": self.width,
            "height": self.height,
            "rooms": self.rooms,
            "requirements": self.requirements,
            "result": self.result,
            "dxf_file_path": self.dxf_file_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
            "message": self.message,
            "ai_enabled": self.ai_enabled,
            "ai_analysis": self.ai_analysis
        }
    
    @classmethod
    def from_request(cls, plan_id: str, request_data: Dict[str, Any]) -> "Plan":
        """Create Plan from request data"""
        return cls(
            id=plan_id,
            name=request_data.get("name", "Unnamed Plan"),
            width=request_data.get("width", 10.0),
            height=request_data.get("height", 10.0),
            rooms=request_data.get("rooms", []),
            requirements=request_data.get("requirements", {}),
            status="initializing"
        )


class PlanGenerationRequest(Base):
    """Track plan generation requests"""
    __tablename__ = "plan_generation_requests"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id = Column(String, nullable=False)
    
    # Request data
    request_data = Column(JSON, nullable=False)
    
    # Processing status
    status = Column(String(50), default="pending")
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    # Results
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    
    # Performance metrics
    processing_time = Column(Float, nullable=True)  # seconds
    memory_usage = Column(Float, nullable=True)     # MB


class SystemMetrics(Base):
    """Track system performance and usage"""
    __tablename__ = "system_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Metrics
    metric_type = Column(String(50), nullable=False)  # 'plan_generation', 'api_request', etc.
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    
    # Metadata
    timestamp = Column(DateTime, default=func.now())
    plan_id = Column(String, nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Additional data
    extra_data = Column(JSON, nullable=True)