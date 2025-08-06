import threading
from fastapi import APIRouter, Depends, HTTPException, Request, Body, Path
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List
from models import Users, CustomDashboards
from database import get_db
from auth import get_current_user
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
def list_dashboards(db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    dashboards = db.query(CustomDashboards).filter(CustomDashboards.user_id == user.id).all()
    return [DashboardOut(
        id=d.id,
        name=d.name,
        config=d.config,
        created_at=str(d.created_at),
        updated_at=str(d.updated_at) if d.updated_at else None
    ) for d in dashboards]

@router.post("/", response_model=DashboardOut, summary="Create dashboard", description="Create a new custom dashboard for the current user.")
def create_dashboard(data: DashboardIn, db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    dashboard = CustomDashboards(user_id=user.id, name=data.name, config=data.config)
    db.add(dashboard)
    db.commit()
    db.refresh(dashboard)
    return DashboardOut(
        id=dashboard.id,
        name=dashboard.name,
        config=dashboard.config,
        created_at=str(dashboard.created_at),
        updated_at=str(dashboard.updated_at) if dashboard.updated_at else None
    )

@router.put("/{dash_id}", response_model=DashboardOut, summary="Update dashboard", description="Update a custom dashboard by ID.")
def update_dashboard(dash_id: int = Path(..., description="ID of the dashboard."), data: DashboardIn = Body(...), db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    dashboard = db.query(CustomDashboards).filter(CustomDashboards.id == dash_id, CustomDashboards.user_id == user.id).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    dashboard.name = data.name
    dashboard.config = data.config
    db.commit()
    db.refresh(dashboard)
    return DashboardOut(
        id=dashboard.id,
        name=dashboard.name,
        config=dashboard.config,
        created_at=str(dashboard.created_at),
        updated_at=str(dashboard.updated_at) if dashboard.updated_at else None
    )

@router.delete("/{dash_id}", response_model=DeleteDashboardResponse, summary="Delete dashboard", description="Delete a custom dashboard by ID.")
@audit_log(action="delete_dashboard", target_type="dashboard", target_id_param="dash_id")
def delete_dashboard(dash_id: int = Path(..., description="ID of the dashboard."), db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    dashboard = db.query(CustomDashboards).filter(CustomDashboards.id == dash_id, CustomDashboards.user_id == user.id).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    db.delete(dashboard)
    db.commit()
    return DeleteDashboardResponse(status="deleted") 