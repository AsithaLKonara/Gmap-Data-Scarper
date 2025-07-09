from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session, joinedload
from models import User, Job, AuditLog
from database import get_db
from auth import get_current_user, get_password_hash
import os
from fastapi.responses import StreamingResponse
import csv
import io
import json
from datetime import datetime, timedelta, date
import time
import logging

router = APIRouter(prefix="/api/admin", tags=["admin"])

# Setup logging for exceptions
logger = logging.getLogger("admin")

def admin_required(user=Depends(get_current_user)):
    print(f"🔒 [ADMIN] Checking admin access for user: {user.email}, Plan: {user.plan}")
    if user.plan != "business":
        print(f"❌ [ADMIN] Access denied - User {user.email} does not have admin privileges")
        raise HTTPException(status_code=403, detail="Admin access required")
    print(f"✅ [ADMIN] Admin access granted for user: {user.email}")
    return user

@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    user=Depends(admin_required),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    email: str = Query(None),
    plan: str = Query(None)
):
    try:
        print(f"📋 [ADMIN] Listing users - Page: {page}, Page Size: {page_size}, Email Filter: {email}, Plan Filter: {plan}")
        
        query = db.query(User)
        if email:
            query = query.filter(User.email.ilike(f"%{email}%"))
            print(f"🔍 [ADMIN] Applied email filter: {email}")
        if plan:
            query = query.filter(User.plan == plan)
            print(f"🔍 [ADMIN] Applied plan filter: {plan}")
        
        total = query.count()
        print(f"📊 [ADMIN] Total users found: {total}")
        
        users = query.order_by(User.id.desc()).offset((page-1)*page_size).limit(page_size).all()
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

@router.get("/jobs")
def list_jobs(
    db: Session = Depends(get_db),
    user=Depends(admin_required),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_email: str = Query(None),
    status: str = Query(None)
):
    print(f"📋 [ADMIN] Listing jobs - Page: {page}, Page Size: {page_size}, User Email Filter: {user_email}, Status Filter: {status}")
    
    query = db.query(Job).options(joinedload(Job.user))
    if user_email:
        user_obj = db.query(User).filter(User.email.ilike(f"%{user_email}%")).first()
        if user_obj:
            query = query.filter(Job.user_id == user_obj.id)
            print(f"🔍 [ADMIN] Applied user filter: {user_email} (ID: {user_obj.id})")
        else:
            print(f"⚠️ [ADMIN] User not found for filter: {user_email}")
            return {"results": [], "total": 0}
    if status:
        query = query.filter(Job.status == status)
        print(f"🔍 [ADMIN] Applied status filter: {status}")
    
    total = query.count()
    print(f"📊 [ADMIN] Total jobs found: {total}")
    
    jobs = query.order_by(Job.id.desc()).offset((page-1)*page_size).limit(page_size).all()
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

@router.get("/stats")
def site_stats(db: Session = Depends(get_db), user=Depends(admin_required)):
    print(f"📊 [ADMIN] Getting site statistics")
    
    user_count = db.query(User).count()
    job_count = db.query(Job).count()
    from datetime import date
    today = date.today()
    active_users_today = db.query(User).filter(User.last_query_date >= today).count()
    
    print(f"📈 [ADMIN] Site stats - Users: {user_count}, Jobs: {job_count}, Active Today: {active_users_today}")
    
    return {
        "user_count": user_count,
        "job_count": job_count,
        "active_users_today": active_users_today
    }

@router.get("/logs")
def get_logs(user=Depends(admin_required)):
    print(f"📋 [ADMIN] Getting system logs")
    log_path = "/app/gmap_script_errors.log"
    if not os.path.exists(log_path):
        print(f"⚠️ [ADMIN] Log file not found: {log_path}")
        return {"logs": []}
    
    with open(log_path, "r") as f:
        lines = f.readlines()[-100:]
    print(f"📋 [ADMIN] Retrieved {len(lines)} log lines")
    return {"logs": lines}

def log_admin_action(db: Session, admin_user: User, action: str, target_type: str, target_id: int = None, target_email: str = None, details: dict = None):
    """Log an admin action for audit purposes"""
    print(f"📝 [AUDIT] Admin action logged - Admin: {admin_user.email}, Action: {action}, Target: {target_type}")
    audit_log = AuditLog(
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

@router.get("/audit-logs")
def get_audit_logs(
    db: Session = Depends(get_db),
    user=Depends(admin_required),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    action: str = Query(None),
    admin_email: str = Query(None),
    target_type: str = Query(None)
):
    print(f"📋 [ADMIN] Getting audit logs - Page: {page}, Page Size: {page_size}")
    
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
        print(f"🔍 [ADMIN] Applied action filter: {action}")
    if admin_email:
        query = query.filter(AuditLog.admin_email.ilike(f"%{admin_email}%"))
        print(f"🔍 [ADMIN] Applied admin email filter: {admin_email}")
    if target_type:
        query = query.filter(AuditLog.target_type == target_type)
        print(f"🔍 [ADMIN] Applied target type filter: {target_type}")
    
    total = query.count()
    print(f"📊 [ADMIN] Total audit logs found: {total}")
    
    logs = query.order_by(AuditLog.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()
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

@router.post("/ban_user")
def ban_user(user_id: int = Body(...), db: Session = Depends(get_db), user=Depends(admin_required)):
    print(f"🚫 [ADMIN] Banning user - User ID: {user_id}, Admin: {user.email}")
    
    target = db.query(User).filter(User.id == user_id).first()
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

@router.post("/unban_user")
def unban_user(user_id: int = Body(...), db: Session = Depends(get_db), user=Depends(admin_required)):
    print(f"✅ [ADMIN] Unbanning user - User ID: {user_id}, Admin: {user.email}")
    
    target = db.query(User).filter(User.id == user_id).first()
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

@router.post("/reset_password")
def reset_password(user_id: int = Body(...), new_password: str = Body(...), db: Session = Depends(get_db), user=Depends(admin_required)):
    print(f"🔑 [ADMIN] Resetting password - User ID: {user_id}, Admin: {user.email}")
    
    target = db.query(User).filter(User.id == user_id).first()
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

@router.get("/export/users")
def export_users(
    db: Session = Depends(get_db),
    user=Depends(admin_required),
    format: str = Query("csv", regex="^(csv|json)$"),
    email: str = Query(None),
    plan: str = Query(None)
):
    query = db.query(User)
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    if plan:
        query = query.filter(User.plan == plan)
    users = query.order_by(User.id.desc()).all()
    
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

@router.get("/export/jobs")
def export_jobs(
    db: Session = Depends(get_db),
    user=Depends(admin_required),
    format: str = Query("csv", regex="^(csv|json)$"),
    user_email: str = Query(None),
    status: str = Query(None)
):
    query = db.query(Job)
    if user_email:
        user_obj = db.query(User).filter(User.email.ilike(f"%{user_email}%")).first()
        if user_obj:
            query = query.filter(Job.user_id == user_obj.id)
        else:
            return [] if format == "json" else StreamingResponse(
                io.BytesIO(b""),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=jobs_export.csv"}
            )
    if status:
        query = query.filter(Job.status == status)
    jobs = query.order_by(Job.id.desc()).all()
    
    if format == "json":
        return [
            {
                "id": j.id,
                "queries": j.queries,
                "status": j.status,
                "user_id": j.user_id,
                "user_email": db.query(User).filter(User.id == j.user_id).first().email if j.user_id else None,
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
                db.query(User).filter(User.id == j.user_id).first().email if j.user_id else "",
                j.created_at.isoformat() if j.created_at else "",
                j.updated_at.isoformat() if j.updated_at else ""
            ])
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=jobs_export.csv"}
        )

@router.get("/analytics/user-growth")
def user_growth_analytics(
    db: Session = Depends(get_db),
    user=Depends(admin_required),
    days: int = Query(30, ge=1, le=365)
):
    """Get user growth data for the last N days"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # Get daily user counts
    daily_counts = []
    current_date = start_date
    while current_date <= end_date:
        count = db.query(User).filter(
            User.created_at >= current_date,
            User.created_at < current_date + timedelta(days=1)
        ).count()
        daily_counts.append({
            "date": current_date.isoformat(),
            "new_users": count,
            "total_users": db.query(User).filter(User.created_at <= current_date).count()
        })
        current_date += timedelta(days=1)
    
    return {
        "period_days": days,
        "data": daily_counts
    }

@router.get("/analytics/job-trends")
def job_trends_analytics(
    db: Session = Depends(get_db),
    user=Depends(admin_required),
    days: int = Query(30, ge=1, le=365)
):
    """Get job trends data for the last N days"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # Get daily job counts by status
    daily_counts = []
    current_date = start_date
    while current_date <= end_date:
        next_date = current_date + timedelta(days=1)
        pending = db.query(Job).filter(
            Job.created_at >= current_date,
            Job.created_at < next_date,
            Job.status == 'pending'
        ).count()
        completed = db.query(Job).filter(
            Job.created_at >= current_date,
            Job.created_at < next_date,
            Job.status == 'completed'
        ).count()
        failed = db.query(Job).filter(
            Job.created_at >= current_date,
            Job.created_at < next_date,
            Job.status == 'failed'
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

@router.get("/analytics/plan-distribution")
def plan_distribution_analytics(
    db: Session = Depends(get_db),
    user=Depends(admin_required)
):
    """Get user plan distribution"""
    plans = db.query(User.plan, db.func.count(User.id)).group_by(User.plan).all()
    return {
        "plans": [{"plan": plan, "count": count} for plan, count in plans]
    }

@router.get("/analytics/active-users")
def active_users_analytics(
    db: Session = Depends(get_db),
    user=Depends(admin_required),
    days: int = Query(7, ge=1, le=30)
):
    """Get active users data for the last N days"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # Get daily active users (users who made queries)
    daily_active = []
    current_date = start_date
    while current_date <= end_date:
        active_count = db.query(User).filter(
            User.last_query_date >= current_date,
            User.last_query_date < current_date + timedelta(days=1)
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

@router.get("/system/health")
def system_health(
    db: Session = Depends(get_db),
    user=Depends(admin_required)
):
    """Get system health metrics"""
    try:
        # TODO: Implement real system health metrics
        return {
            "timestamp": datetime.now().isoformat(),
            "system": {"status": "not_implemented"},
            "database": {"status": "not_implemented"},
            "api": {"status": "not_implemented"}
        }
    except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "status": "error"
        }

@router.get("/system/performance")
def system_performance(
    db: Session = Depends(get_db),
    user=Depends(admin_required),
    hours: int = Query(24, ge=1, le=168)
):
    """Get performance metrics over time"""
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)
    # TODO: Implement real performance data collection
    return {
        "period_hours": hours,
        "data": [],
        "message": "Not implemented"
    }

@router.get("/system/logs/recent")
def recent_system_logs(
    db: Session = Depends(get_db),
    user=Depends(admin_required),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get recent system logs"""
    # In production, you'd query actual log files or a log database
    # For now, we'll return a sample of recent audit logs
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    
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

@router.get("/crm/analytics")
def crm_analytics(db: Session = Depends(get_db), user=Depends(admin_required)):
    try:
        # TODO: Implement real CRM analytics logic
        return {"crm_leads": None, "crm_conversion_rate": None, "message": "Not implemented"}
    except Exception as e:
        logger.exception("Error in CRM analytics")
        raise 