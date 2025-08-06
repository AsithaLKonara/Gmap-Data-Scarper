from fastapi import APIRouter, Response, Request, HTTPException, Depends, Query
from fastapi.responses import FileResponse, JSONResponse
import os
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from database import get_db
from models import Tenant

router = APIRouter(prefix="/api/integrations", tags=["integrations"])

class IntegrationInfo(BaseModel):
    name: str = Field(..., description="Integration name", example="Zapier")
    description: str = Field(..., description="Integration description", example="Connect LeadTap with 5000+ apps")
    status: str = Field(..., description="Integration status", example="available")
    category: str = Field(..., description="Integration category", example="Automation")
    logo: str = Field(..., description="Integration logo emoji", example="🔗")
    setup_url: Optional[str] = Field(None, description="Setup URL for the integration", example="https://zapier.com/apps/leadtap")

class IntegrationsListOut(BaseModel):
    integrations: List[IntegrationInfo] = Field(..., description="List of available integrations")

class CRMConnectIn(BaseModel):
    tenant_id: int = Field(..., description="Tenant ID to connect CRM for", example=1)
    provider: str = Field(..., description="CRM provider name", example="hubspot")
    config: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific configuration", example={"api_key": "abc123"})

class CRMConnectOut(BaseModel):
    ok: bool = Field(..., description="Whether the CRM connection was successful", example=True)

class CRMStatusOut(BaseModel):
    provider: Optional[str] = Field(None, description="CRM provider name", example="hubspot")
    config: Optional[Dict[str, Any]] = Field(None, description="Provider-specific configuration", example={"api_key": "abc123"})

class WebhookSetIn(BaseModel):
    tenant_id: int = Field(..., description="Tenant ID to set webhook for", example=1)
    url: str = Field(..., description="Webhook URL to receive events", example="https://example.com/webhook")

class WebhookSetOut(BaseModel):
    ok: bool = Field(..., description="Whether the webhook was set successfully", example=True)

class WebhookGetOut(BaseModel):
    webhook_url: Optional[str] = Field(None, description="Current webhook URL for the tenant", example="https://example.com/webhook")

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

@router.get("/", response_model=IntegrationsListOut, summary="List available integrations", description="Get all available integrations and setup URLs.")
def list_integrations():
    """Get all available integrations and setup URLs."""
    return {"integrations": INTEGRATIONS}

@router.get("/postman", summary="Download Postman collection", description="Download the LeadTap Postman collection for API testing.")
def download_postman_collection():
    """Download the LeadTap Postman collection for API testing."""
    postman_path = os.path.join(os.path.dirname(__file__), "postman_collection.json")
    if not os.path.exists(postman_path):
        return JSONResponse(status_code=404, content={"detail": "Postman collection not found"})
    return FileResponse(postman_path, media_type="application/json", filename="LeadTap.postman_collection.json")

@router.post("/crm/connect", response_model=CRMConnectOut, summary="Connect CRM integration", description="Connect a CRM provider for a tenant.")
async def connect_crm(
    data: CRMConnectIn,
    db: Session = Depends(get_db)
):
    """Connect a CRM provider for a tenant."""
    tenant = db.query(Tenant).get(data.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    if not tenant.branding:
        tenant.branding = {}
    tenant.branding['crm'] = {'provider': data.provider, 'config': data.config}
    db.commit()
    return {"ok": True}

@router.get("/crm/status", response_model=CRMStatusOut, summary="Get CRM integration status", description="Get the current CRM provider and configuration for a tenant.")
def get_crm_status(
    tenant_id: int = Query(..., description="Tenant ID to get CRM status for", example=1),
    db: Session = Depends(get_db)
):
    """Get the current CRM provider and configuration for a tenant."""
    tenant = db.query(Tenant).get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    crm = (tenant.branding or {}).get('crm', {})
    return {"provider": crm.get('provider'), "config": crm.get('config')}

@router.post("/webhook", response_model=WebhookSetOut, summary="Set webhook URL", description="Set a webhook URL for a tenant to receive events.")
async def set_webhook(
    data: WebhookSetIn,
    db: Session = Depends(get_db)
):
    """Set a webhook URL for a tenant to receive events."""
    tenant = db.query(Tenant).get(data.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    if not tenant.branding:
        tenant.branding = {}
    tenant.branding['webhook_url'] = data.url
    db.commit()
    return {"ok": True}

@router.get("/webhook", response_model=WebhookGetOut, summary="Get webhook URL", description="Get the current webhook URL for a tenant.")
def get_webhook(
    tenant_id: int = Query(..., description="Tenant ID to get webhook URL for", example=1),
    db: Session = Depends(get_db)
):
    """Get the current webhook URL for a tenant."""
    tenant = db.query(Tenant).get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    url = (tenant.branding or {}).get('webhook_url')
    return {"webhook_url": url} 