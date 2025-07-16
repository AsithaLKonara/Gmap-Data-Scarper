from fastapi import APIRouter, Depends, HTTPException, Body, Request
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from models import Widget, User
from database import get_db
from auth import get_current_user
from datetime import datetime
import json
from audit import audit_log
from security import check_permission

router = APIRouter(prefix="/api/widgets", tags=["widgets"])

# --- Pydantic Models for OpenAPI ---
class WidgetCreate(BaseModel):
    type: str = Field(..., description="Type of widget (lead_capture, testimonial, metrics).")
    config: Optional[Dict[str, Any]] = Field(None, description="Widget configuration.")

class WidgetOut(BaseModel):
    id: int
    type: str
    config: Optional[Dict[str, Any]]
    embed_code: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

class DeleteWidgetResponse(BaseModel):
    success: bool

class SubmitLeadResponse(BaseModel):
    success: bool
    message: str

# --- Endpoints with OpenAPI docs ---

@router.post("/", response_model=WidgetOut, summary="Create widget", description="Create a new embeddable widget.")
def create_widget(widget: WidgetCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Create a new embeddable widget for the current user."""
    embed_code = f'<script src="https://your-leadtap-domain.com/widget.js?id={{WIDGET_ID}}"></script>'
    w = Widget(user_id=user.id, type=widget.type, config=widget.config, embed_code=embed_code)
    db.add(w)
    db.commit()
    db.refresh(w)
    w.embed_code = w.embed_code.replace('{WIDGET_ID}', str(w.id))
    db.commit()
    return w

@router.get("/", response_model=List[WidgetOut], summary="List widgets", description="List all widgets for the current user.")
def list_widgets(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """List all widgets for the current user."""
    widgets = db.query(Widget).filter_by(user_id=user.id).all()
    return widgets

@router.get("/{widget_id}", response_model=WidgetOut, summary="Get widget", description="Get a widget by ID.")
def get_widget(widget_id: int = Field(..., description="ID of the widget."), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get a widget by ID."""
    w = db.query(Widget).filter_by(id=widget_id, user_id=user.id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Widget not found")
    return w

@router.put("/{widget_id}", response_model=WidgetOut, summary="Update widget", description="Update a widget's config.")
def update_widget(widget_id: int = Field(..., description="ID of the widget."), widget: WidgetCreate = Body(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Update a widget's config."""
    w = db.query(Widget).filter_by(id=widget_id, user_id=user.id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Widget not found")
    w.type = widget.type
    w.config = widget.config
    w.updated_at = datetime.utcnow()
    db.commit()
    return w

@router.delete("/{widget_id}", response_model=DeleteWidgetResponse, summary="Delete widget", description="Delete a widget by ID for the authenticated user.")
@audit_log(action="delete_widget", target_type="widget", target_id_param="widget_id")
def delete_widget(widget_id: int = Field(..., description="ID of the widget."), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # RBAC: Only allow if user has widgets:delete permission
    if not check_permission(user, "widgets", "delete", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions to delete widgets")
    w = db.query(Widget).filter_by(id=widget_id, user_id=user.id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Widget not found")
    db.delete(w)
    db.commit()
    return DeleteWidgetResponse(success=True)

# Public endpoint for lead capture widget submissions
@router.post("/public/lead_capture/{widget_id}", response_model=SubmitLeadResponse, summary="Submit lead via widget", description="Public endpoint for lead capture widget submissions.")
async def submit_lead(widget_id: int = Field(..., description="ID of the widget."), request: Request = Body(...), db: Session = Depends(get_db)):
    """Public endpoint for lead capture widget submissions."""
    w = db.query(Widget).filter_by(id=widget_id, type='lead_capture', is_active=True).first()
    if not w:
        raise HTTPException(status_code=404, detail="Widget not found")
    data = await request.json()
    # TODO: Validate and save lead to CRM (integrate with CRM logic)
    # Example: db.add(Lead(...)); db.commit()
    return {"success": True, "message": "Lead submitted!"} 