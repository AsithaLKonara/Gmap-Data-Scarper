from fastapi import APIRouter, Response, Request, HTTPException, Depends
from fastapi.responses import FileResponse, JSONResponse
import os
from sqlalchemy.orm import Session
from models import Tenant
from database import get_db

router = APIRouter(prefix="/api/integrations", tags=["integrations"])

INTEGRATIONS = [
    {
        "name": "Zapier",
        "description": "Connect LeadTap with 5000+ apps",
        "status": "available",
        "category": "Automation",
        "logo": "🔗",
        "setup_url": "https://zapier.com/apps/leadtap"
    },
    {
        "name": "Make (Integromat)",
        "description": "Advanced automation workflows",
        "status": "available",
        "category": "Automation",
        "logo": "⚙️",
        "setup_url": "https://make.com/integrations/leadtap"
    },
    {
        "name": "HubSpot",
        "description": "CRM integration for lead management",
        "status": "available",
        "category": "CRM",
        "logo": "📊"
    },
    {
        "name": "Salesforce",
        "description": "Enterprise CRM integration",
        "status": "coming_soon",
        "category": "CRM",
        "logo": "☁️"
    },
    {
        "name": "Slack",
        "description": "Get notifications in Slack",
        "status": "available",
        "category": "Communication",
        "logo": "💬"
    },
    {
        "name": "Discord",
        "description": "Discord bot integration",
        "status": "beta",
        "category": "Communication",
        "logo": "🎮"
    }
]

@router.get("/", summary="List available integrations", response_description="List of integrations")
def list_integrations():
    """Get all available integrations and setup URLs."""
    return {"integrations": INTEGRATIONS}

@router.get("/postman", summary="Download Postman collection", response_description="Postman collection JSON")
def download_postman_collection():
    """Download the LeadTap Postman collection for API testing."""
    postman_path = os.path.join(os.path.dirname(__file__), "postman_collection.json")
    if not os.path.exists(postman_path):
        return JSONResponse(status_code=404, content={"detail": "Postman collection not found"})
    return FileResponse(postman_path, media_type="application/json", filename="LeadTap.postman_collection.json")

# CRM Integration
@router.post("/crm/connect", response_model=dict)
async def connect_crm(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    tenant_id = data.get('tenant_id')
    provider = data.get('provider')
    config = data.get('config', {})
    tenant = db.query(Tenant).get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    if not tenant.branding:
        tenant.branding = {}
    tenant.branding['crm'] = {'provider': provider, 'config': config}
    db.commit()
    return {"ok": True}

@router.get("/crm/status", response_model=dict)
def get_crm_status(tenant_id: int, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    crm = (tenant.branding or {}).get('crm', {})
    return {"provider": crm.get('provider'), "config": crm.get('config')}

# Webhook Integration
@router.post("/webhook", response_model=dict)
async def set_webhook(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    tenant_id = data.get('tenant_id')
    url = data.get('url')
    tenant = db.query(Tenant).get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    if not tenant.branding:
        tenant.branding = {}
    tenant.branding['webhook_url'] = url
    db.commit()
    return {"ok": True}

@router.get("/webhook", response_model=dict)
def get_webhook(tenant_id: int, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    url = (tenant.branding or {}).get('webhook_url')
    return {"webhook_url": url} 