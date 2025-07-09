from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from models import User, SystemLog, Job, User as UserModel
from database import get_db
from auth import get_current_user
import logging
import json
import psutil
import os
from datetime import datetime, timedelta
import platform

logger = logging.getLogger("system")

router = APIRouter(prefix="/api/system", tags=["system"])

class SystemHealthResponse(BaseModel):
    status: str
    timestamp: datetime
    uptime: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_connections: int
    database_status: str

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
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_jobs: int
    total_users: int
    total_jobs: int
    average_response_time: float

@router.get("/health", response_model=SystemHealthResponse)
def get_system_health(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        # Check if user is admin
        if user.plan != 'business' and not user.is_admin:
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

@router.get("/performance", response_model=PerformanceMetrics)
def get_performance_metrics(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        # Check if user is admin
        if user.plan != 'business' and not getattr(user, 'is_admin', False):
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

@router.get("/logs", response_model=List[SystemLogResponse])
def get_system_logs(
    level: Optional[str] = None,
    module: Optional[str] = None,
    hours: int = 24,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    try:
        # Check if user is admin
        if user.plan != 'business' and not user.is_admin:
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

@router.get("/info")
def get_system_info(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        # Check if user is admin
        if user.plan != 'business' and not user.is_admin:
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