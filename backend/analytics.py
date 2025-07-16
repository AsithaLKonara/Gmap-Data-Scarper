from fastapi import APIRouter, Depends, HTTPException, Request, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List
from models import CustomDashboard, User
from database import get_db
from auth import get_current_user
from config import CACHE_TIMEOUT_SECONDS
import threading
from tenant_utils import get_tenant_record_or_403
from audit import audit_log

# Thread-safe cache for per-user analytics
_analytics_cache = {}
_analytics_cache_lock = threading.Lock()

router = APIRouter(prefix="/api/analytics/custom-dashboards", tags=["custom-dashboards"])

# --- Pydantic Models for OpenAPI ---
class DashboardIn(BaseModel):
    name: str = Field(..., description="Name of the custom dashboard.")
    config: dict = Field(..., description="Dashboard configuration object.")

class DashboardOut(BaseModel):
    id: int
    name: str
    config: dict
    created_at: str
    updated_at: str = None
    class Config:
        orm_mode = True

class DeleteDashboardResponse(BaseModel):
    status: str

@router.get("/", response_model=List[DashboardOut], summary="List dashboards", description="List all custom dashboards for the current user.")
def list_dashboards(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """List all custom dashboards for the current user."""
    return db.query(CustomDashboard).filter(CustomDashboard.user_id == user.id).order_by(CustomDashboard.created_at.desc()).all()

@router.post("/", response_model=DashboardOut, summary="Create dashboard", description="Create a new custom dashboard for the current user.")
def create_dashboard(data: DashboardIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Create a new custom dashboard for the current user."""
    dash = CustomDashboard(user_id=user.id, name=data.name, config=data.config)
    db.add(dash)
    db.commit()
    db.refresh(dash)
    return dash

@router.put("/{dash_id}", response_model=DashboardOut, summary="Update dashboard", description="Update a custom dashboard by ID.")
def update_dashboard(dash_id: int = Field(..., description="ID of the dashboard."), data: DashboardIn = Body(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Update a custom dashboard by ID."""
    dash = db.query(CustomDashboard).filter(CustomDashboard.id == dash_id, CustomDashboard.user_id == user.id).first()
    if not dash:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    dash.name = data.name
    dash.config = data.config
    db.commit()
    db.refresh(dash)
    return dash

@router.delete("/{dash_id}", response_model=DeleteDashboardResponse, summary="Delete dashboard", description="Delete a custom dashboard by ID.")
@audit_log(action="delete_dashboard", target_type="dashboard", target_id_param="dash_id")
def delete_dashboard(dash_id: int = Field(..., description="ID of the dashboard."), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Delete a custom dashboard by ID."""
    dash = db.query(CustomDashboard).filter(CustomDashboard.id == dash_id, CustomDashboard.user_id == user.id).first()
    if not dash:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    db.delete(dash)
    db.commit()
    return {"status": "deleted"} 