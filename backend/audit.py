from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from models import AuditLog, User
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/api/audit", tags=["audit"])

class AuditLogIn(BaseModel):
    action: str
    target_type: Optional[str] = None
    target_id: Optional[int] = None
    details: Optional[str] = None

class AuditLogOut(BaseModel):
    id: int
    action: str
    target_type: Optional[str]
    target_id: Optional[int]
    details: Optional[str]
    timestamp: str
    class Config:
        orm_mode = True

@router.post("/log")
def log_action(data: AuditLogIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    log = AuditLog(user_id=user.id, action=data.action, target_type=data.target_type, target_id=data.target_id, details=data.details)
    db.add(log)
    db.commit()
    return {"status": "logged"}

@router.get("/my", response_model=List[AuditLogOut])
def get_my_logs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(AuditLog).filter(AuditLog.user_id == user.id).order_by(AuditLog.timestamp.desc()).all() 