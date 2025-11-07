"""Database initialization and connection management"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import logging

from ..utils.config import settings
from .models import Base

logger = logging.getLogger(__name__)

# Global database objects
engine = None
SessionLocal = None


def init_database() -> None:
    """Initialize database connection and create tables"""
    global engine, SessionLocal
    
    try:
        # Create database engine
        database_url = settings.database_url
        
        # Special handling for SQLite
        if database_url.startswith("sqlite"):
            # Ensure directory exists for SQLite file
            db_path = database_url.replace("sqlite:///", "")
            if db_path and not db_path.startswith(":memory:"):
                os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
            
            # SQLite specific configuration
            engine = create_engine(
                database_url,
                poolclass=StaticPool,
                connect_args={
                    "check_same_thread": False,
                    "timeout": 20
                },
                echo=settings.debug  # Log SQL queries in debug mode
            )
        else:
            # PostgreSQL/MySQL configuration
            engine = create_engine(
                database_url,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=settings.debug
            )
        
        # Create session factory
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info(f"Database initialized successfully: {database_url}")
        
        # Test database connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("Database connection test: OK")
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseManager:
    """High-level database operations manager"""
    
    def __init__(self):
        if engine is None:
            init_database()
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return SessionLocal()
    
    def health_check(self) -> bool:
        """Check database health"""
        try:
            with self.get_session() as db:
                db.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def get_database_info(self) -> dict:
        """Get database information"""
        try:
            with self.get_session() as db:
                # Get table counts
                plan_count = db.execute(text("SELECT COUNT(*) FROM plans")).scalar()
                request_count = db.execute(text("SELECT COUNT(*) FROM plan_generation_requests")).scalar()
                
                return {
                    "database_type": "sqlite" if settings.database_url.startswith("sqlite") else "other",
                    "database_url": settings.database_url.split("//")[0] + "//[hidden]",  # Hide password
                    "tables": {
                        "plans": plan_count,
                        "plan_generation_requests": request_count,
                        "system_metrics": db.execute(text("SELECT COUNT(*) FROM system_metrics")).scalar()
                    },
                    "status": "healthy"
                }
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


# Global database manager instance
db_manager = DatabaseManager()