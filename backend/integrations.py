from fastapi import APIRouter, Response
from fastapi.responses import FileResponse, JSONResponse
import os

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