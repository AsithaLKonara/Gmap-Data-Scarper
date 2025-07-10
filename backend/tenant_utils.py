from fastapi import Request, HTTPException, Depends, FastAPI
from sqlalchemy.orm import Session
from database import get_db
from models import Tenant

def get_tenant_from_request(request: Request, db: Session = Depends(get_db)) -> Tenant:
    # Example: extract tenant from X-Tenant header
    tenant_slug = request.headers.get('X-Tenant')
    if not tenant_slug:
        raise HTTPException(status_code=400, detail='Missing X-Tenant header')
    tenant = db.query(Tenant).filter_by(slug=tenant_slug).first()
    if not tenant:
        raise HTTPException(status_code=404, detail='Tenant not found')
    return tenant

def tenant_from_domain_middleware(app: FastAPI):
    @app.middleware('http')
    async def extract_tenant_from_domain(request: Request, call_next):
        host = request.headers.get('host', '').split(':')[0]
        db = next(get_db())
        tenant = db.query(Tenant).filter_by(custom_domain=host).first()
        if tenant:
            request.state.tenant_slug = tenant.slug
        response = await call_next(request)
        return response 