from tenant_utils import get_tenant_from_request
from tenant_utils import get_tenant_record_or_403

@router.get("/leads", ...)
def get_leads(request: Request, db: Session = Depends(get_db)):
    tenant = get_tenant_from_request(request, db)
    leads = db.query(Lead).filter_by(tenant_id=tenant.id).all()
    return leads

@router.post("/leads", ...)
def create_lead(..., request: Request, db: Session = Depends(get_db)):
    tenant = get_tenant_from_request(request, db)
    # ... create lead ...
    lead.tenant_id = tenant.id
    db.add(lead)
    db.commit()
    return lead 

@router.get("/leads/{lead_id}", ...)
def get_lead(lead_id: int, request: Request, db: Session = Depends(get_db)):
    tenant = get_tenant_from_request(request, db)
    lead = get_tenant_record_or_403(Lead, lead_id, tenant.id, db)
    return lead 