from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session, joinedload
from models import Users, Jobs, AuditLogs, Leads
from database import get_db
from auth import get_current_user, get_password_hash
from security import check_permission
import os
from fastapi.responses import StreamingResponse
import csv
import io
import json
from datetime import datetime, timedelta, date
import time
import logging
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from system import get_system_health as system_health_api, get_performance_metrics as system_performance_api

router = APIRouter(prefix="/api/admin", tags=["admin"])

# Setup logging for exceptions
logger = logging.getLogger("admin")

# --- Pydantic Models for OpenAPI ---
class UserOut(BaseModel):
    id: int
    email: str
    plan: str
    created_at: Optional[datetime]
    queries_today: Optional[int]
    last_query_date: Optional[datetime]

class UserListResponse(BaseModel):
    results: List[UserOut]
    total: int

class JobOut(BaseModel):
    id: int
    queries: List[str]
    status: str
    result: Optional[Any]
    csv_path: Optional[str]
    user_id: int
    user_email: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class JobListResponse(BaseModel):
    results: List[JobOut]
    total: int

class SiteStatsResponse(BaseModel):
    user_count: int
    job_count: int
    active_users_today: int

class LogResponse(BaseModel):
    logs: List[str]

class AuditLogOut(BaseModel):
    id: int
    admin_email: str
    action: str
    target_type: Optional[str]
    target_id: Optional[int]
    target_email: Optional[str]
    details: Optional[Dict[str, Any]]
    created_at: Optional[str]

class AuditLogListResponse(BaseModel):
    results: List[AuditLogOut]
    total: int

class BanUserRequest(BaseModel):
    user_id: int = Field(..., description="ID of the user to ban.")

class UnbanUserRequest(BaseModel):
    user_id: int = Field(..., description="ID of the user to unban.")

class ResetPasswordRequest(BaseModel):
    user_id: int = Field(..., description="ID of the user to reset password for.")
    new_password: str = Field(..., description="New password for the user.")

class SimpleStatusResponse(BaseModel):
    status: str
    user_id: int

class ExportFormat(str):
    csv = "csv"
    json = "json"

class UserGrowthData(BaseModel):
    date: str
    new_users: int
    total_users: int

class UserGrowthResponse(BaseModel):
    period_days: int
    data: List[UserGrowthData]

class JobTrendsData(BaseModel):
    date: str
    pending: int
    completed: int
    failed: int
    total: int

class JobTrendsResponse(BaseModel):
    period_days: int
    data: List[JobTrendsData]

class PlanDistributionItem(BaseModel):
    plan: str
    count: int

class PlanDistributionResponse(BaseModel):
    plans: List[PlanDistributionItem]

class ActiveUsersData(BaseModel):
    date: str
    active_users: int

class ActiveUsersResponse(BaseModel):
    period_days: int
    data: List[ActiveUsersData]

class SystemHealthResponse(BaseModel):
    timestamp: str
    system: Dict[str, Any]
    database: Dict[str, Any]
    api: Dict[str, Any]
    error: Optional[str] = None
    status: Optional[str] = None

class SystemPerformanceResponse(BaseModel):
    period_hours: int
    data: List[Any]
    message: str

class RecentSystemLogItem(BaseModel):
    timestamp: str
    level: str
    message: str
    details: Dict[str, Any]

class RecentSystemLogsResponse(BaseModel):
    logs: List[RecentSystemLogItem]

class CRMAnalyticsResponse(BaseModel):
    crm_leads: Optional[Any]
    crm_conversion_rate: Optional[Any]
    message: Optional[str]

# --- Endpoints with OpenAPI docs ---

@router.get("/users", response_model=UserListResponse, summary="List users", description="List all users with optional filters for email and plan.")
def list_users(
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number for pagination."),
    page_size: int = Query(20, ge=1, le=100, description="Number of users per page."),
    email: Optional[str] = Query(None, description="Filter users by email (partial match)."),
    plan: Optional[str] = Query(None, description="Filter users by plan name.")
):
    """Get a paginated list of users. Admin access required."""
    if not check_permission(user, "admin", "read", db):
        raise HTTPException(status_code=403, detail="Admin access required")
    try:
        print(f"📋 [ADMIN] Listing users - Page: {page}, Page Size: {page_size}, Email Filter: {email}, Plan Filter: {plan}")
        
        query = db.query(Users)
        if email:
            query = query.filter(Users.email.ilike(f"%{email}%"))
            print(f"🔍 [ADMIN] Applied email filter: {email}")
        if plan:
            query = query.filter(Users.plan == plan)
            print(f"🔍 [ADMIN] Applied plan filter: {plan}")
        
        total = query.count()
        print(f"📊 [ADMIN] Total users found: {total}")
        
        users = query.order_by(Users.id.desc()).offset((page-1)*page_size).limit(page_size).all()
        print(f"📋 [ADMIN] Retrieved {len(users)} users for page {page}")
        
        return {
            "results": [
                {
                    "id": u.id,
                    "email": u.email,
                    "plan": u.plan,
                    "created_at": u.created_at,
                    "queries_today": u.queries_today,
                    "last_query_date": u.last_query_date
                }
                for u in users
            ],
            "total": total
        }
    except Exception as e:
        logger.exception("Error listing users")
        raise HTTPException(status_code=500, detail="Failed to list users. Please try again later.")

@router.get("/jobs", response_model=JobListResponse, summary="List jobs", description="List all jobs with optional filters for user email and status.")
def list_jobs(
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number for pagination."),
    page_size: int = Query(20, ge=1, le=100, description="Number of jobs per page."),
    user_email: Optional[str] = Query(None, description="Filter jobs by user email (partial match)."),
    status: Optional[str] = Query(None, description="Filter jobs by status.")
):
    """Get a paginated list of jobs. Admin access required."""
    if not check_permission(user, "admin", "read", db):
        raise HTTPException(status_code=403, detail="Admin access required")
    print(f"📋 [ADMIN] Listing jobs - Page: {page}, Page Size: {page_size}, User Email Filter: {user_email}, Status Filter: {status}")
    
    query = db.query(Jobs).options(joinedload(Jobs.user))
    if user_email:
        user_obj = db.query(Users).filter(Users.email.ilike(f"%{user_email}%")).first()
        if user_obj:
            query = query.filter(Jobs.user_id == user_obj.id)
            print(f"🔍 [ADMIN] Applied user filter: {user_email} (ID: {user_obj.id})")
        else:
            print(f"⚠️ [ADMIN] User not found for filter: {user_email}")
            return {"results": [], "total": 0}
    if status:
        query = query.filter(Jobs.status == status)
        print(f"🔍 [ADMIN] Applied status filter: {status}")
    
    total = query.count()
    print(f"📊 [ADMIN] Total jobs found: {total}")
    
    jobs = query.order_by(Jobs.id.desc()).offset((page-1)*page_size).limit(page_size).all()
    print(f"📋 [ADMIN] Retrieved {len(jobs)} jobs for page {page}")
    
    return {
        "results": [
            {
                "id": j.id,
                "queries": j.queries,
                "status": j.status,
                "result": j.result,
                "csv_path": j.csv_path,
                "user_id": j.user_id,
                "user_email": j.user.email if j.user else None,
                "created_at": j.created_at,
                "updated_at": j.updated_at
            }
            for j in jobs
        ],
        "total": total
    }

@router.get("/stats", response_model=SiteStatsResponse, summary="Get site statistics", description="Get overall statistics for users, jobs, and active users today.")
def site_stats(db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    """Get site-wide statistics. Admin access required."""
    if not check_permission(user, "admin", "read", db):
        raise HTTPException(status_code=403, detail="Admin access required")
    print(f"📊 [ADMIN] Getting site statistics")
    
    user_count = db.query(Users).count()
    job_count = db.query(Jobs).count()
    from datetime import date
    today = date.today()
    active_users_today = db.query(Users).filter(Users.last_query_date >= today).count()
    
    print(f"📈 [ADMIN] Site stats - Users: {user_count}, Jobs: {job_count}, Active Today: {active_users_today}")
    
    return {
        "user_count": user_count,
        "job_count": job_count,
        "active_users_today": active_users_today
    }

@router.get("/logs", response_model=LogResponse, summary="Get system logs", description="Get the last 100 lines of the system error log file.")
def get_logs(user: Users = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get the last 100 lines of the system error log file. Admin access required."""
    if not check_permission(user, "admin", "read", db):
        raise HTTPException(status_code=403, detail="Admin access required")
    print(f"📋 [ADMIN] Getting system logs")
    log_path = "/app/gmap_script_errors.log"
    if not os.path.exists(log_path):
        print(f"⚠️ [ADMIN] Log file not found: {log_path}")
        return {"logs": []}
    
    with open(log_path, "r") as f:
        lines = f.readlines()[-100:]
    print(f"📋 [ADMIN] Retrieved {len(lines)} log lines")
    return {"logs": lines}

def log_admin_action(db: Session, admin_user: Users, action: str, target_type: str, target_id: int = None, target_email: str = None, details: dict = None):
    """Log an admin action for audit purposes"""
    print(f"📝 [AUDIT] Admin action logged - Admin: {admin_user.email}, Action: {action}, Target: {target_type}")
    audit_log = AuditLogs(
        admin_id=admin_user.id,
        admin_email=admin_user.email,
        action=action,
        target_type=target_type,
        target_id=target_id,
        target_email=target_email,
        details=json.dumps(details) if details else None
    )
    db.add(audit_log)
    db.commit()
    print(f"✅ [AUDIT] Audit log saved successfully")

@router.get("/audit-logs", response_model=AuditLogListResponse, summary="Get audit logs", description="Get a paginated list of admin audit logs with optional filters.")
def get_audit_logs(
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number for pagination."),
    page_size: int = Query(20, ge=1, le=100, description="Number of logs per page."),
    action: Optional[str] = Query(None, description="Filter logs by action type."),
    admin_email: Optional[str] = Query(None, description="Filter logs by admin email (partial match)."),
    target_type: Optional[str] = Query(None, description="Filter logs by target type.")
):
    """Get a paginated list of admin audit logs. Admin access required."""
    if not check_permission(user, "admin", "read", db):
        raise HTTPException(status_code=403, detail="Admin access required")
    print(f"📋 [ADMIN] Getting audit logs - Page: {page}, Page Size: {page_size}")
    
    query = db.query(AuditLogs)
    if action:
        query = query.filter(AuditLogs.action == action)
        print(f"🔍 [ADMIN] Applied action filter: {action}")
    if admin_email:
        query = query.filter(AuditLogs.admin_email.ilike(f"%{admin_email}%"))
        print(f"🔍 [ADMIN] Applied admin email filter: {admin_email}")
    if target_type:
        query = query.filter(AuditLogs.target_type == target_type)
        print(f"🔍 [ADMIN] Applied target type filter: {target_type}")
    
    total = query.count()
    print(f"📊 [ADMIN] Total audit logs found: {total}")
    
    logs = query.order_by(AuditLogs.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()
    print(f"📋 [ADMIN] Retrieved {len(logs)} audit logs for page {page}")
    
    return {
        "results": [
            {
                "id": log.id,
                "admin_email": log.admin_email,
                "action": log.action,
                "target_type": log.target_type,
                "target_id": log.target_id,
                "target_email": log.target_email,
                "details": json.loads(log.details) if log.details else None,
                "created_at": log.created_at.isoformat() if log.created_at else None
            }
            for log in logs
        ],
        "total": total
    }

@router.post("/ban_user", response_model=SimpleStatusResponse, summary="Ban a user", description="Ban a user by user ID. Admin access required.")
def ban_user(
    user_id: int = Body(..., embed=True, description="ID of the user to ban."),
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    # RBAC: Only allow if user has admin:write permission
    if not check_permission(user, "admin", "write", db):
        raise HTTPException(status_code=403, detail="Admin access required")
    print(f"🚫 [ADMIN] Banning user - User ID: {user_id}, Admin: {user.email}")
    
    target = db.query(Users).filter(Users.id == user_id).first()
    if not target:
        print(f"❌ [ADMIN] Ban failed - User not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    print(f"✅ [ADMIN] User found - ID: {target.id}, Email: {target.email}, Current Plan: {target.plan}")
    target.plan = "banned"
    db.commit()
    print(f"🚫 [ADMIN] User banned successfully - ID: {target.id}, Email: {target.email}")
    
    # Log the action
    log_admin_action(
        db=db,
        admin_user=user,
        action="ban_user",
        target_type="user",
        target_id=target.id,
        target_email=target.email,
        details={"previous_plan": target.plan, "new_plan": "banned"}
    )
    
    return {"status": "banned", "user_id": user_id}

@router.post("/unban_user", response_model=SimpleStatusResponse, summary="Unban a user", description="Unban a user by user ID. Admin access required.")
def unban_user(
    user_id: int = Body(..., embed=True, description="ID of the user to unban."),
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Unban a user by user ID. Admin access required."""
    if not check_permission(user, "admin", "write", db):
        raise HTTPException(status_code=403, detail="Admin access required")
    print(f"✅ [ADMIN] Unbanning user - User ID: {user_id}, Admin: {user.email}")
    
    target = db.query(Users).filter(Users.id == user_id).first()
    if not target:
        print(f"❌ [ADMIN] Unban failed - User not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    print(f"✅ [ADMIN] User found - ID: {target.id}, Email: {target.email}, Current Plan: {target.plan}")
    previous_plan = target.plan
    target.plan = "free"
    db.commit()
    print(f"✅ [ADMIN] User unbanned successfully - ID: {target.id}, Email: {target.email}")
    
    # Log the action
    log_admin_action(
        db=db,
        admin_user=user,
        action="unban_user",
        target_type="user",
        target_id=target.id,
        target_email=target.email,
        details={"previous_plan": previous_plan, "new_plan": "free"}
    )
    
    return {"status": "unbanned", "user_id": user_id}

@router.post("/reset_password", response_model=SimpleStatusResponse, summary="Reset user password", description="Reset a user's password by user ID. Admin access required.")
def reset_password(
    user_id: int = Body(..., embed=True, description="ID of the user to reset password for."),
    new_password: str = Body(..., embed=True, description="New password for the user."),
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Reset a user's password by user ID. Admin access required."""
    if not check_permission(user, "admin", "write", db):
        raise HTTPException(status_code=403, detail="Admin access required")
    print(f"🔑 [ADMIN] Resetting password - User ID: {user_id}, Admin: {user.email}")
    
    target = db.query(Users).filter(Users.id == user_id).first()
    if not target:
        print(f"❌ [ADMIN] Password reset failed - User not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    print(f"✅ [ADMIN] User found - ID: {target.id}, Email: {target.email}")
    target.hashed_password = get_password_hash(new_password)
    db.commit()
    print(f"🔑 [ADMIN] Password reset successfully - ID: {target.id}, Email: {target.email}")
    
    # Log the action
    log_admin_action(
        db=db,
        admin_user=user,
        action="reset_password",
        target_type="user",
        target_id=target.id,
        target_email=target.email,
        details={"password_changed": True}
    )
    
    return {"status": "password_reset", "user_id": user_id}

@router.get("/export/users", summary="Export users", description="Export users as CSV or JSON. Admin access required.")
def export_users(
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user),
    format: str = Query("csv", regex="^(csv|json)$", description="Export format: csv or json."),
    email: Optional[str] = Query(None, description="Filter users by email (partial match)."),
    plan: Optional[str] = Query(None, description="Filter users by plan name.")
):
    """Export users as CSV or JSON. Admin access required."""
    if not check_permission(user, "admin", "read", db):
        raise HTTPException(status_code=403, detail="Admin access required")
    query = db.query(Users)
    if email:
        query = query.filter(Users.email.ilike(f"%{email}%"))
    if plan:
        query = query.filter(Users.plan == plan)
    users = query.order_by(Users.id.desc()).all()
    
    if format == "json":
        return [
            {
                "id": u.id,
                "email": u.email,
                "plan": u.plan,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "queries_today": u.queries_today,
                "last_query_date": u.last_query_date.isoformat() if u.last_query_date else None
            }
            for u in users
        ]
    else:  # csv
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Email", "Plan", "Created At", "Queries Today", "Last Query Date"])
        for u in users:
            writer.writerow([
                u.id,
                u.email,
                u.plan,
                u.created_at.isoformat() if u.created_at else "",
                u.queries_today,
                u.last_query_date.isoformat() if u.last_query_date else ""
            ])
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=users_export.csv"}
        )

@router.get("/export/jobs", summary="Export jobs", description="Export jobs as CSV or JSON. Admin access required.")
def export_jobs(
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user),
    format: str = Query("csv", regex="^(csv|json)$", description="Export format: csv or json."),
    user_email: Optional[str] = Query(None, description="Filter jobs by user email (partial match)."),
    status: Optional[str] = Query(None, description="Filter jobs by status.")
):
    """Export jobs as CSV or JSON. Admin access required."""
    if not check_permission(user, "admin", "read", db):
        raise HTTPException(status_code=403, detail="Admin access required")
    query = db.query(Jobs)
    if user_email:
        user_obj = db.query(Users).filter(Users.email.ilike(f"%{user_email}%")).first()
        if user_obj:
            query = query.filter(Jobs.user_id == user_obj.id)
        else:
            return [] if format == "json" else StreamingResponse(
                io.BytesIO(b""),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=jobs_export.csv"}
            )
    if status:
        query = query.filter(Jobs.status == status)
    jobs = query.order_by(Jobs.id.desc()).all()
    
    if format == "json":
        return [
            {
                "id": j.id,
                "queries": j.queries,
                "status": j.status,
                "user_id": j.user_id,
                "user_email": db.query(Users).filter(Users.id == j.user_id).first().email if j.user_id else None,
                "created_at": j.created_at.isoformat() if j.created_at else None,
                "updated_at": j.updated_at.isoformat() if j.updated_at else None
            }
            for j in jobs
        ]
    else:  # csv
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Queries", "Status", "User ID", "User Email", "Created At", "Updated At"])
        for j in jobs:
            writer.writerow([
                j.id,
                j.queries,
                j.status,
                j.user_id,
                db.query(Users).filter(Users.id == j.user_id).first().email if j.user_id else "",
                j.created_at.isoformat() if j.created_at else "",
                j.updated_at.isoformat() if j.updated_at else ""
            ])
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=jobs_export.csv"}
        )

@router.get("/analytics/user-growth", response_model=UserGrowthResponse, summary="User growth analytics", description="Get user growth data for the last N days.")
def user_growth_analytics(
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user),
    days: int = Query(30, ge=1, le=365, description="Number of days to include in the analytics.")
):
    """Get user growth analytics for the last N days. Admin access required."""
    if not check_permission(user, "admin", "read", db):
        raise HTTPException(status_code=403, detail="Admin access required")
    """Get user growth data for the last N days"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # Get daily user counts
    daily_counts = []
    current_date = start_date
    while current_date <= end_date:
        count = db.query(Users).filter(
            Users.created_at >= current_date,
            Users.created_at < current_date + timedelta(days=1)
        ).count()
        daily_counts.append({
            "date": current_date.isoformat(),
            "new_users": count,
            "total_users": db.query(Users).filter(Users.created_at <= current_date).count()
        })
        current_date += timedelta(days=1)
    
    return {
        "period_days": days,
        "data": daily_counts
    }

@router.get("/analytics/job-trends", response_model=JobTrendsResponse, summary="Job trends analytics", description="Get job trends data for the last N days.")
def job_trends_analytics(
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user),
    days: int = Query(30, ge=1, le=365, description="Number of days to include in the analytics.")
):
    """Get job trends analytics for the last N days. Admin access required."""
    if not check_permission(user, "admin", "read", db):
        raise HTTPException(status_code=403, detail="Admin access required")
    """Get job trends data for the last N days"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # Get daily job counts by status
    daily_counts = []
    current_date = start_date
    while current_date <= end_date:
        next_date = current_date + timedelta(days=1)
        pending = db.query(Jobs).filter(
            Jobs.created_at >= current_date,
            Jobs.created_at < next_date,
            Jobs.status == 'pending'
        ).count()
        completed = db.query(Jobs).filter(
            Jobs.created_at >= current_date,
            Jobs.created_at < next_date,
            Jobs.status == 'completed'
        ).count()
        failed = db.query(Jobs).filter(
            Jobs.created_at >= current_date,
            Jobs.created_at < next_date,
            Jobs.status == 'failed'
        ).count()
        
        daily_counts.append({
            "date": current_date.isoformat(),
            "pending": pending,
            "completed": completed,
            "failed": failed,
            "total": pending + completed + failed
        })
        current_date += timedelta(days=1)
    
    return {
        "period_days": days,
        "data": daily_counts
    }

@router.get("/analytics/plan-distribution", response_model=PlanDistributionResponse, summary="Plan distribution analytics", description="Get user plan distribution analytics.")
def plan_distribution_analytics(
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Get user plan distribution analytics. Admin access required."""
    if not check_permission(user, "admin", "read", db):
        raise HTTPException(status_code=403, detail="Admin access required")
    """Get user plan distribution"""
    plans = db.query(Users.plan, db.func.count(Users.id)).group_by(Users.plan).all()
    return {
        "plans": [{"plan": plan, "count": count} for plan, count in plans]
    }

@router.get("/analytics/active-users", response_model=ActiveUsersResponse, summary="Active users analytics", description="Get active users data for the last N days.")
def active_users_analytics(
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user),
    days: int = Query(7, ge=1, le=30, description="Number of days to include in the analytics.")
):
    """Get active users analytics for the last N days. Admin access required."""
    if not check_permission(user, "admin", "read", db):
        raise HTTPException(status_code=403, detail="Admin access required")
    """Get active users data for the last N days"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # Get daily active users (users who made queries)
    daily_active = []
    current_date = start_date
    while current_date <= end_date:
        active_count = db.query(Users).filter(
            Users.last_query_date >= current_date,
            Users.last_query_date < current_date + timedelta(days=1)
        ).count()
        daily_active.append({
            "date": current_date.isoformat(),
            "active_users": active_count
        })
        current_date += timedelta(days=1)
    
    return {
        "period_days": days,
        "data": daily_active
    }

@router.get("/system/health", response_model=SystemHealthResponse, summary="System health", description="Get system health metrics.")
def system_health(
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    return system_health_api(db, user)

@router.get("/system/performance", response_model=SystemPerformanceResponse, summary="System performance", description="Get system performance metrics over time.")
def system_performance(
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user),
    hours: int = Query(24, ge=1, le=168, description="Number of hours to include in the performance analytics.")
):
    perf = system_performance_api(db, user)
    return {"period_hours": hours, "data": [perf], "message": "OK"}

@router.get("/system/logs/recent", response_model=RecentSystemLogsResponse, summary="Recent system logs", description="Get recent system logs (sample of recent audit logs).")
def recent_system_logs(
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user),
    limit: int = Query(100, ge=1, le=1000, description="Number of recent logs to return.")
):
    """Get recent system logs (sample of recent audit logs). Admin access required."""
    if not check_permission(user, "admin", "read", db):
        raise HTTPException(status_code=403, detail="Admin access required")
    """Get recent system logs"""
    # In production, you'd query actual log files or a log database
    # For now, we'll return a sample of recent audit logs
    logs = db.query(AuditLogs).order_by(AuditLogs.timestamp.desc()).limit(limit).all()
    
    return {
        "logs": [
            {
                "timestamp": log.timestamp.isoformat(),
                "level": "INFO",
                "message": f"{log.action} by {log.admin_email}",
                "details": {
                    "action": log.action,
                    "admin_email": log.admin_email,
                    "target_type": log.target_type,
                    "target_id": log.target_id
                }
            }
            for log in logs
        ]
    }

@router.get("/crm/analytics", response_model=CRMAnalyticsResponse, summary="CRM analytics", description="Get CRM analytics data.")
def crm_analytics(db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    if not check_permission(user, "admin", "read", db):
        raise HTTPException(status_code=403, detail="Admin access required")
    try:
        # Example CRM analytics: count of leads with CRM data, conversion rate
        crm_leads = db.query(Leads).filter(Leads.enriched_data != None).count()
        total_leads = db.query(Leads).count()
        crm_conversion_rate = (crm_leads / total_leads) if total_leads > 0 else 0.0
        return {"crm_leads": crm_leads, "crm_conversion_rate": crm_conversion_rate, "message": "OK"}
    except Exception as e:
        logger.exception("Error in CRM analytics")
        raise 