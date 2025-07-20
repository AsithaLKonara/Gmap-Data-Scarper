from fastapi import APIRouter, Depends, HTTPException, Body, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from models import AuditLogs, Users
from database import get_db
from auth import get_current_user
from functools import wraps

router = APIRouter(prefix="/api/audit", tags=["audit"])

class AuditLogIn(BaseModel):
    action: str = Field(..., description="Action performed by the user.", example="delete_lead")
    target_type: Optional[str] = Field(None, description="Type of the target entity.", example="lead")
    target_id: Optional[int] = Field(None, description="ID of the target entity.", example=123)
    details: Optional[str] = Field(None, description="Additional details about the action.", example="Lead deleted by admin.")

class AuditLogOut(BaseModel):
    id: int = Field(..., description="Audit log entry ID.", example=1)
    action: str = Field(..., description="Action performed by the user.", example="delete_lead")
    target_type: Optional[str] = Field(None, description="Type of the target entity.", example="lead")
    target_id: Optional[int] = Field(None, description="ID of the target entity.", example=123)
    details: Optional[str] = Field(None, description="Additional details about the action.", example="Lead deleted by admin.")
    timestamp: str = Field(..., description="Timestamp of the action (ISO format).", example="2024-05-01T12:00:00Z")
    class Config:
        orm_mode = True

# Unified audit logging decorator
# Usage: @audit_log(action="delete_lead", target_type="lead")
def audit_log(action: str, target_type: str = None, target_id_param: str = None, details_param: str = None):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get('request')
            db = kwargs.get('db')
            user = kwargs.get('user') or kwargs.get('current_user')
            # Extract target_id and details from params if specified
            target_id = kwargs.get(target_id_param) if target_id_param else None
            details = kwargs.get(details_param) if details_param else None
            # Call the endpoint
            result = await func(*args, **kwargs) if callable(getattr(func, '__await__', None)) else func(*args, **kwargs)
            # Log the action
            if db and user:
                log = AuditLogs(
                    user_id=user.id,
                    action=action,
                    target_type=target_type,
                    target_id=target_id,
                    details=str(details) if details else None
                )
                db.add(log)
                db.commit()
            return result
        return wrapper
    return decorator

# Example usage on a sensitive endpoint
# @router.delete("/example/{item_id}")
# @audit_log(action="delete_example", target_type="example", target_id_param="item_id")
# def delete_example(item_id: int, db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
#     ...

@router.post(
    "/log",
    summary="Log an audit action",
    description="Log a user action for auditing purposes.",
    response_model=dict,
    response_description="Status of the log action."
)
def log_action(
    data: AuditLogIn,
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Log a user action for auditing purposes."""
    log = AuditLogs(user_id=user.id, action=data.action, target_type=data.target_type, target_id=data.target_id, details=data.details)
    db.add(log)
    db.commit()
    return {"status": "logged"}

@router.get(
    "/my",
    response_model=List[AuditLogOut],
    summary="Get my audit logs",
    description="Retrieve the audit log entries for the current user.",
    response_description="List of audit log entries."
)
def get_my_logs(
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Retrieve the audit log entries for the current user."""
    return db.query(AuditLogs).filter(AuditLogs.user_id == user.id).order_by(AuditLogs.timestamp.desc()).all() 