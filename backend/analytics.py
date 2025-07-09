from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from models import CustomDashboard, User
from database import get_db
from auth import get_current_user
from config import CACHE_TIMEOUT_SECONDS
import threading

# Thread-safe cache for per-user analytics
_analytics_cache = {}
_analytics_cache_lock = threading.Lock()

router = APIRouter(prefix="/api/analytics/custom-dashboards", tags=["custom-dashboards"])

class DashboardIn(BaseModel):
    name: str
    config: dict

class DashboardOut(BaseModel):
    id: int
    name: str
    config: dict
    created_at: str
    updated_at: str = None
    class Config:
        orm_mode = True

@router.get("/", response_model=List[DashboardOut])
def list_dashboards(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(CustomDashboard).filter(CustomDashboard.user_id == user.id).order_by(CustomDashboard.created_at.desc()).all()

@router.post("/", response_model=DashboardOut)
def create_dashboard(data: DashboardIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    dash = CustomDashboard(user_id=user.id, name=data.name, config=data.config)
    db.add(dash)
    db.commit()
    db.refresh(dash)
    return dash

@router.put("/{dash_id}", response_model=DashboardOut)
def update_dashboard(dash_id: int, data: DashboardIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    dash = db.query(CustomDashboard).filter(CustomDashboard.id == dash_id, CustomDashboard.user_id == user.id).first()
    if not dash:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    dash.name = data.name
    dash.config = data.config
    db.commit()
    db.refresh(dash)
    return dash

@router.delete("/{dash_id}")
def delete_dashboard(dash_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    dash = db.query(CustomDashboard).filter(CustomDashboard.id == dash_id, CustomDashboard.user_id == user.id).first()
    if not dash:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    db.delete(dash)
    db.commit()
    return {"status": "deleted"} 