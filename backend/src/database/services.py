"""Database service layer for plan operations"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, and_, or_
import os

from .models import Plan, PlanGenerationRequest, SystemMetrics
from ..utils import get_logger

logger = get_logger(__name__)


class PlanService:
    """Service class for plan database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_plan(self, plan_id: str, request_data: Dict[str, Any]) -> Plan:
        """Create a new plan"""
        try:
            plan = Plan.from_request(plan_id, request_data)
            self.db.add(plan)
            
            # Also create generation request record
            generation_request = PlanGenerationRequest(
                plan_id=plan_id,
                request_data=request_data,
                status="pending"
            )
            self.db.add(generation_request)
            
            self.db.commit()
            self.db.refresh(plan)
            
            logger.info(f"Created plan {plan_id}: {plan.name}")
            return plan
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create plan {plan_id}: {e}")
            raise
    
    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Get plan by ID"""
        try:
            plan = self.db.query(Plan).filter(Plan.id == plan_id).first()
            if plan:
                logger.debug(f"Retrieved plan {plan_id}")
            else:
                logger.warning(f"Plan {plan_id} not found")
            return plan
        except Exception as e:
            logger.error(f"Failed to get plan {plan_id}: {e}")
            raise
    
    def update_plan_status(self, plan_id: str, status: str, **kwargs) -> Optional[Plan]:
        """Update plan status and additional fields"""
        try:
            plan = self.get_plan(plan_id)
            if not plan:
                return None
            
            plan.status = status
            plan.updated_at = datetime.now()
            
            # Update additional fields
            for key, value in kwargs.items():
                if hasattr(plan, key):
                    setattr(plan, key, value)
            
            # Set completion time if completed
            if status in ["completed", "failed"]:
                plan.completed_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(plan)
            
            logger.info(f"Updated plan {plan_id} status to {status}")
            return plan
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update plan {plan_id}: {e}")
            raise
    
    def update_plan_progress(self, plan_id: str, progress: int, message: str = None) -> Optional[Plan]:
        """Update plan progress"""
        try:
            plan = self.get_plan(plan_id)
            if not plan:
                return None
            
            plan.progress = progress
            plan.updated_at = datetime.now()
            if message:
                plan.message = message
            
            self.db.commit()
            self.db.refresh(plan)
            
            logger.debug(f"Updated plan {plan_id} progress to {progress}%")
            return plan
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update plan {plan_id} progress: {e}")
            raise
    
    def save_plan_result(self, plan_id: str, result: Dict[str, Any], dxf_file_path: str = None) -> Optional[Plan]:
        """Save plan generation result with enhanced error handling"""
        try:
            # Validate inputs
            if not plan_id:
                raise ValueError("Plan ID is required")
            if not result:
                raise ValueError("Result data is required")
            
            # Check if plan exists first
            plan = self.get_plan(plan_id)
            if not plan:
                logger.error(f"Cannot save result for non-existent plan: {plan_id}")
                return None
            
            # Validate DXF file path if provided
            if dxf_file_path and not os.path.exists(dxf_file_path):
                logger.warning(f"DXF file path does not exist: {dxf_file_path}")
                # Don't fail the save, but log the issue
            
            # Update plan with completion data
            updated_plan = self.update_plan_status(
                plan_id, 
                "completed",
                result=result,
                dxf_file_path=dxf_file_path,
                ai_enabled=result.get("ai_enabled", False),
                ai_analysis=result.get("ai_analysis")
            )
            
            if updated_plan:
                logger.info(f"Successfully saved plan result: {plan_id}")
                
                # Verify the save was successful
                verification_plan = self.get_plan(plan_id)
                if verification_plan and verification_plan.status == "completed":
                    logger.info(f"Verified plan completion: {plan_id}")
                    return verification_plan
                else:
                    logger.error(f"Plan save verification failed: {plan_id}")
                    return None
            else:
                logger.error(f"Plan save operation returned None: {plan_id}")
                return None
                
        except ValueError as ve:
            logger.error(f"Validation error saving plan result {plan_id}: {ve}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error saving plan result {plan_id}: {e}")
            # Re-raise with more context
            raise Exception(f"Failed to save plan result: {str(e)}")
    
    def set_plan_error(self, plan_id: str, error: str, status: str = "failed") -> Optional[Plan]:
        """Set plan error status"""
        return self.update_plan_status(plan_id, status, error=error)
    
    def list_plans(self, page: int = 1, limit: int = 20, status: str = None) -> List[Plan]:
        """List plans with pagination"""
        try:
            query = self.db.query(Plan)
            
            # Filter by status if provided
            if status:
                query = query.filter(Plan.status == status)
            
            # Apply pagination
            offset = (page - 1) * limit
            plans = query.order_by(desc(Plan.created_at)).offset(offset).limit(limit).all()
            
            logger.debug(f"Listed {len(plans)} plans (page {page}, limit {limit})")
            return plans
            
        except Exception as e:
            logger.error(f"Failed to list plans: {e}")
            raise
    
    def delete_plan(self, plan_id: str) -> bool:
        """Delete a plan"""
        try:
            plan = self.get_plan(plan_id)
            if not plan:
                return False
            
            self.db.delete(plan)
            self.db.commit()
            
            logger.info(f"Deleted plan {plan_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete plan {plan_id}: {e}")
            raise
    
    def get_plan_statistics(self) -> Dict[str, Any]:
        """Get plan statistics"""
        try:
            total_plans = self.db.query(Plan).count()
            completed_plans = self.db.query(Plan).filter(Plan.status == "completed").count()
            failed_plans = self.db.query(Plan).filter(Plan.status == "failed").count()
            active_plans = self.db.query(Plan).filter(Plan.status.in_(["initializing", "generating"])).count()
            
            return {
                "total": total_plans,
                "completed": completed_plans,
                "failed": failed_plans,
                "active": active_plans,
                "success_rate": (completed_plans / total_plans * 100) if total_plans > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get plan statistics: {e}")
            raise


class MetricsService:
    """Service class for system metrics"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def record_metric(self, metric_type: str, metric_name: str, metric_value: float, 
                     plan_id: str = None, metadata: Dict[str, Any] = None) -> SystemMetrics:
        """Record a system metric"""
        try:
            metric = SystemMetrics(
                metric_type=metric_type,
                metric_name=metric_name,
                metric_value=metric_value,
                plan_id=plan_id,
                metadata=metadata
            )
            self.db.add(metric)
            self.db.commit()
            
            logger.debug(f"Recorded metric: {metric_type}.{metric_name} = {metric_value}")
            return metric
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to record metric: {e}")
            raise
    
    def get_metrics(self, metric_type: str = None, limit: int = 100) -> List[SystemMetrics]:
        """Get system metrics"""
        try:
            query = self.db.query(SystemMetrics)
            
            if metric_type:
                query = query.filter(SystemMetrics.metric_type == metric_type)
            
            metrics = query.order_by(desc(SystemMetrics.timestamp)).limit(limit).all()
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            raise