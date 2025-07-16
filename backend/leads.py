from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Lead
from database import get_db
from tenant_utils import get_tenant_from_request, get_tenant_record_or_403
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter(prefix="/api", tags=["leads"])

class LeadBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    tag: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = "new"
    source: Optional[str] = None

class LeadCreate(LeadBase):
    pass

class LeadOut(LeadBase):
    id: int
    user_id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    tenant_id: Optional[int]

    class Config:
        orm_mode = True

@router.get("/leads", response_model=List[LeadOut], summary="List all leads", description="Get all leads for the current tenant.")
def get_leads(request: Request, db: Session = Depends(get_db)):
    """Get all leads for the current tenant."""
    tenant = get_tenant_from_request(request, db)
    leads = db.query(Lead).filter_by(tenant_id=tenant.id).all()
    return leads

@router.post("/leads", response_model=LeadOut, summary="Create a new lead", description="Create a new lead for the current tenant.")
def create_lead(lead_data: LeadCreate, request: Request, db: Session = Depends(get_db)):
    """Create a new lead for the current tenant."""
    tenant = get_tenant_from_request(request, db)
    lead = Lead(**lead_data.dict(), tenant_id=tenant.id)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead

@router.get("/leads/{lead_id}", response_model=LeadOut, summary="Get a lead by ID", description="Get a single lead by its ID for the current tenant.")
def get_lead(lead_id: int, request: Request, db: Session = Depends(get_db)):
    """Get a single lead by its ID for the current tenant."""
    tenant = get_tenant_from_request(request, db)
    lead = get_tenant_record_or_403(Lead, lead_id, tenant.id, db)
    return lead 