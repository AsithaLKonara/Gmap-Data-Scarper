from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from models import Lead
from database import get_db
from tenant_utils import get_tenant_from_request, get_tenant_record_or_403

router = APIRouter(prefix="/api", tags=["leads"])

@router.get("/leads")
def get_leads(request: Request, db: Session = Depends(get_db)):
    tenant = get_tenant_from_request(request, db)
    leads = db.query(Lead).filter_by(tenant_id=tenant.id).all()
    return leads

@router.post("/leads")
def create_lead(lead_data: dict, request: Request, db: Session = Depends(get_db)):
    tenant = get_tenant_from_request(request, db)
    lead = Lead(**lead_data, tenant_id=tenant.id)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead

@router.get("/leads/{lead_id}")
def get_lead(lead_id: int, request: Request, db: Session = Depends(get_db)):
    tenant = get_tenant_from_request(request, db)
    lead = get_tenant_record_or_403(Lead, lead_id, tenant.id, db)
    return lead 