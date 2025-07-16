from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from models import User, SystemLog, Job, User as UserModel
from database import get_db
from auth import get_current_user
from security import check_permission
import logging
import json
import psutil
import os
from datetime import datetime, timedelta
import platform

logger = logging.getLogger("system")

router = APIRouter(prefix="/api/system", tags=["system"])

# --- Pydantic Models for OpenAPI ---
class SystemHealthResponse(BaseModel):
    status: str = Field(..., description="System health status.")
    timestamp: datetime = Field(..., description="Timestamp of the health check.")
    uptime: float = Field(..., description="System uptime in seconds.")
    cpu_usage: float = Field(..., description="CPU usage percentage.")
    memory_usage: float = Field(..., description="Memory usage percentage.")
    disk_usage: float = Field(..., description="Disk usage percentage.")
    active_connections: int = Field(..., description="Number of active network connections.")
    database_status: str = Field(..., description="Database connection status.")

class SystemLogResponse(BaseModel):
    id: int
    level: str
    module: str
    message: str
    details: Optional[str] = None
    user_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PerformanceMetrics(BaseModel):
    cpu_usage: Optional[float]
    memory_usage: Optional[float]
    disk_usage: Optional[float]
    active_jobs: Optional[int]
    total_users: Optional[int]
    total_jobs: Optional[int]
    average_response_time: Optional[float]
    message: Optional[str] = None

@router.get("/health", response_model=SystemHealthResponse, summary="Get system health", description="Get system health metrics and status.")
def get_system_health(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        if not check_permission(user, "system", "read", db):
            raise HTTPException(status_code=403, detail="Access denied. Admin privileges required.")
        
        # Get system metrics
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get uptime
        uptime = (datetime.utcnow() - datetime.fromtimestamp(psutil.boot_time())).total_seconds()
        
        # Check database connection
        try:
            db.execute("SELECT 1")
            db_status = "healthy"
        except Exception:
            db_status = "unhealthy"
        
        # Get active connections (approximate)
        active_connections = len(psutil.net_connections())
        
        return {
            "status": "healthy" if db_status == "healthy" else "degraded",
            "timestamp": datetime.utcnow(),
            "uptime": uptime,
            "cpu_usage": cpu_usage,
            "memory_usage": memory.percent,
            "disk_usage": disk.percent,
            "active_connections": active_connections,
            "database_status": db_status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting system health")
        raise HTTPException(status_code=500, detail="Failed to get system health. Please try again later.")

@router.get("/performance", response_model=PerformanceMetrics, summary="Get system performance", description="Get system performance metrics.")
def get_performance_metrics(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        if not check_permission(user, "system", "read", db):
            raise HTTPException(status_code=403, detail="Access denied. Admin privileges required.")
        # TODO: Implement real system performance metrics
        return {
            "cpu_usage": None,
            "memory_usage": None,
            "disk_usage": None,
            "active_jobs": None,
            "total_users": None,
            "total_jobs": None,
            "average_response_time": None,
            "message": "Not implemented"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting performance metrics")
        raise HTTPException(status_code=500, detail="Failed to get performance metrics. Please try again later.")

@router.get("/logs", response_model=List[SystemLogResponse], summary="Get system logs", description="Get recent system logs with optional filters.")
def get_system_logs(
    level: Optional[str] = None,
    module: Optional[str] = None,
    hours: int = 24,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    try:
        if not check_permission(user, "system", "read", db):
            raise HTTPException(status_code=403, detail="Access denied. Admin privileges required.")
        
        # Calculate time range
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # Build query
        query = db.query(SystemLog).filter(SystemLog.created_at >= since)
        
        if level:
            query = query.filter(SystemLog.level == level)
        if module:
            query = query.filter(SystemLog.module == module)
        
        logs = query.order_by(SystemLog.created_at.desc()).limit(limit).all()
        return logs
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting system logs")
        raise HTTPException(status_code=500, detail="Failed to get system logs. Please try again later.")

@router.get("/info", summary="Get system info", description="Get system and environment information.")
def get_system_info(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        if not check_permission(user, "system", "read", db):
            raise HTTPException(status_code=403, detail="Access denied. Admin privileges required.")
        
        return {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "processor": platform.processor(),
            "machine": platform.machine(),
            "node": platform.node(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "environment": os.getenv('ENVIRONMENT', 'development'),
            "database_url": os.getenv('DATABASE_URL', 'sqlite:///app.db').split('@')[0] + '@***' if '@' in os.getenv('DATABASE_URL', '') else 'sqlite:///app.db'
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting system info")
        raise HTTPException(status_code=500, detail="Failed to get system info. Please try again later.")

def log_system_event(level: str, module: str, message: str, details: Optional[Dict] = None, user_id: Optional[int] = None, request: Optional[Any] = None):
    """Helper function to log system events"""
    try:
        db = next(get_db())
        log_entry = SystemLog(
            level=level,
            module=module,
            message=message,
            details=json.dumps(details) if details else None,
            user_id=user_id,
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get('user-agent') if request else None
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        logger.exception("Error logging system event") 