from tenant_utils import get_tenant_from_request

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