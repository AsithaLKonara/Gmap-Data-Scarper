from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, Request, Path
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime, timedelta
from database import get_db
from models import Users, Leads
from auth import get_current_user
from pydantic import BaseModel, Field
import secrets
from config import lru_cache, CACHE_TIMEOUT_SECONDS
import threading
from tenant_utils import get_tenant_from_request, get_tenant_record_or_403
from webhook_utils import send_webhook_event
from audit import audit_log
from security import check_permission

router = APIRouter(prefix="/api/crm", tags=["crm"])

class LeadCreate(BaseModel):
    name: str = Field(..., description="Lead's full name", example="Alice Smith")
    email: str = Field(..., description="Lead's email address", example="alice@example.com")
    phone: Optional[str] = Field(None, description="Lead's phone number", example="+1234567890")
    company: Optional[str] = Field(None, description="Lead's company name", example="Acme Inc.")
    website: Optional[str] = Field(None, description="Lead's website", example="https://acme.com")
    address: Optional[str] = Field(None, description="Lead's address", example="123 Main St, City")
    source: str = Field("manual", description="Source of the lead (manual, gmap_scrape, etc.)", example="manual")
    notes: Optional[str] = Field(None, description="Additional notes about the lead")
    tags: Optional[List[str]] = Field(None, description="Tags for the lead", example=["vip", "newsletter"])

class LeadUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Lead's full name")
    email: Optional[str] = Field(None, description="Lead's email address")
    phone: Optional[str] = Field(None, description="Lead's phone number")
    company: Optional[str] = Field(None, description="Lead's company name")
    website: Optional[str] = Field(None, description="Lead's website")
    address: Optional[str] = Field(None, description="Lead's address")
    status: Optional[str] = Field(None, description="Lead status (new, contacted, converted, etc.)")
    notes: Optional[str] = Field(None, description="Additional notes about the lead")
    tags: Optional[List[str]] = Field(None, description="Tags for the lead")

class LeadResponse(BaseModel):
    id: int = Field(..., description="Lead ID")
    name: str = Field(..., description="Lead's full name")
    email: str = Field(..., description="Lead's email address")
    phone: Optional[str] = Field(None, description="Lead's phone number")
    company: Optional[str] = Field(None, description="Lead's company name")
    website: Optional[str] = Field(None, description="Lead's website")
    address: Optional[str] = Field(None, description="Lead's address")
    source: str = Field(..., description="Source of the lead")
    status: str = Field(..., description="Lead status")
    notes: Optional[str] = Field(None, description="Additional notes")
    tags: List[str] = Field([], description="Tags for the lead")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

class BulkDeleteLeadsRequest(BaseModel):
    lead_ids: List[int] = Field(..., description="List of lead IDs to delete.", example=[1,2,3])
class BulkAddLeadsRequest(BaseModel):
    leads: List[LeadCreate] = Field(..., description="List of leads to add.")
class BulkDeleteLeadsResponse(BaseModel):
    deleted: int = Field(..., description="Number of leads deleted.")
class BulkAddLeadsResponse(BaseModel):
    added: int = Field(..., description="Number of leads added.")

class DeleteLeadResponse(BaseModel):
    message: str

# Thread-safe cache for per-user stats
_stats_cache = {}
_stats_cache_lock = threading.Lock()

@router.post("/leads", response_model=LeadResponse, summary="Create a new CRM lead", description="Create a new lead in the CRM for the authenticated user.")
async def create_lead(
    lead_data: LeadCreate = Body(..., description="Lead data to create."),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new lead in the CRM for the authenticated user.

- **lead_data**: LeadCreate object.
- **Returns**: LeadResponse.
- **Errors**: 400/500 on failure."""
    lead = Leads(
        user_id=current_user.id,
        name=lead_data.name,
        email=lead_data.email,
        phone=lead_data.phone,
        company=lead_data.company,
        website=lead_data.website,
        address=lead_data.address,
        source=lead_data.source,
        notes=lead_data.notes,
        tags=json.dumps(lead_data.tags) if lead_data.tags else None
    )
    
    db.add(lead)
    db.commit()
    db.refresh(lead)
    
    # Log the action
    log = SystemLogs(
        level="INFO",
        module="crm",
        message=f"Lead created: {lead_data.name} ({lead_data.email})",
        details=json.dumps({"lead_id": lead.id, "source": lead_data.source}),
        user_id=current_user.id
    )
    db.add(log)
    db.commit()
    
    # Trigger webhook for lead creation
    send_webhook_event(
        event="lead.created",
        payload={
            "lead_id": lead.id,
            "name": lead.name,
            "email": lead.email,
            "phone": lead.phone,
            "company": lead.company,
            "website": lead.website,
            "address": lead.address,
            "source": lead.source,
            "status": lead.status,
            "user_id": lead.user_id,
            "created_at": str(lead.created_at)
        },
        user_id=lead.user_id,
        db=db
    )
    
    return LeadResponse(
        id=lead.id,
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        company=lead.company,
        website=lead.website,
        address=lead.address,
        source=lead.source,
        status=lead.status,
        notes=lead.notes,
        tags=json.loads(lead.tags) if lead.tags else [],
        created_at=lead.created_at,
        updated_at=lead.updated_at
    )

@router.get("/leads", response_model=List[LeadResponse], summary="List CRM leads", description="Get all leads for the authenticated user, with filtering and pagination.")
async def get_leads(
    status: Optional[str] = Query(None, description="Filter by lead status (new, contacted, etc.)"),
    source: Optional[str] = Query(None, description="Filter by lead source (manual, gmap_scrape, etc.)"),
    search: Optional[str] = Query(None, description="Search by name, email, or company"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    page_size: int = Query(20, ge=1, le=100, description="Number of leads per page"),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all leads for the authenticated user, with filtering and pagination.

- **status/source/search**: Optional filters.
- **page/page_size**: Pagination.
- **Returns**: List of LeadResponse."""
    query = db.query(Leads).filter(Leads.user_id == current_user.id)
    
    if status:
        query = query.filter(Leads.status == status)
    if source:
        query = query.filter(Leads.source == source)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Leads.name.ilike(search_filter)) |
            (Leads.email.ilike(search_filter)) |
            (Leads.company.ilike(search_filter))
        )
    
    # Pagination
    total = query.count()
    leads = query.offset((page - 1) * page_size).limit(page_size).all()
    
    result = []
    for lead in leads:
        result.append(LeadResponse(
            id=lead.id,
            name=lead.name,
            email=lead.email,
            phone=lead.phone,
            company=lead.company,
            website=lead.website,
            address=lead.address,
            source=lead.source,
            status=lead.status,
            notes=lead.notes,
            tags=json.loads(lead.tags) if lead.tags else [],
            created_at=lead.created_at,
            updated_at=lead.updated_at
        ))
    
    return result

@router.get("/leads/{lead_id}", response_model=LeadResponse, summary="Get a CRM lead by ID", description="Get a specific lead by its ID for the authenticated user.")
async def get_lead(
    lead_id: int = Path(..., description="ID of the lead to retrieve."),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific lead by its ID for the authenticated user.

- **lead_id**: Lead ID.
- **Returns**: LeadResponse.
- **Errors**: 404 if not found."""
    lead = db.query(Leads).filter(Leads.id == lead_id, Leads.user_id == current_user.id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return LeadResponse(
        id=lead.id,
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        company=lead.company,
        website=lead.website,
        address=lead.address,
        source=lead.source,
        status=lead.status,
        notes=lead.notes,
        tags=json.loads(lead.tags) if lead.tags else [],
        created_at=lead.created_at,
        updated_at=lead.updated_at
    )

@router.put("/leads/{lead_id}", response_model=LeadResponse, summary="Update a CRM lead", description="Update a lead in the CRM by its ID for the authenticated user.")
async def update_lead(
    lead_id: int = Path(..., description="ID of the lead to update."),
    lead_data: LeadUpdate = Body(..., description="Fields to update for the lead."),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a lead in the CRM by its ID for the authenticated user.

- **lead_id**: Lead ID.
- **lead_data**: Fields to update.
- **Returns**: LeadResponse.
- **Errors**: 404 if not found."""
    lead = db.query(Leads).filter(Leads.id == lead_id, Leads.user_id == current_user.id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Update fields
    if lead_data.name is not None:
        lead.name = lead_data.name
    if lead_data.email is not None:
        lead.email = lead_data.email
    if lead_data.phone is not None:
        lead.phone = lead_data.phone
    if lead_data.company is not None:
        lead.company = lead_data.company
    if lead_data.website is not None:
        lead.website = lead_data.website
    if lead_data.address is not None:
        lead.address = lead_data.address
    if lead_data.status is not None:
        lead.status = lead_data.status
    if lead_data.notes is not None:
        lead.notes = lead_data.notes
    if lead_data.tags is not None:
        lead.tags = json.dumps(lead_data.tags)
    
    lead.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(lead)
    
    return LeadResponse(
        id=lead.id,
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        company=lead.company,
        website=lead.website,
        address=lead.address,
        source=lead.source,
        status=lead.status,
        notes=lead.notes,
        tags=json.loads(lead.tags) if lead.tags else [],
        created_at=lead.created_at,
        updated_at=lead.updated_at
    )

@router.delete("/leads/{lead_id}", response_model=DeleteLeadResponse, summary="Delete a CRM lead", description="Delete a lead in the CRM by its ID for the authenticated user.")
@audit_log(action="delete_lead", target_type="lead", target_id_param="lead_id")
async def delete_lead(
    lead_id: int = Path(..., description="ID of the lead to delete."),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # RBAC: Only allow if user has leads:delete permission
    if not check_permission(current_user, "leads", "delete", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions to delete leads")
    lead = db.query(Leads).filter(Leads.id == lead_id, Leads.user_id == current_user.id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    db.delete(lead)
    db.commit()
    
    return DeleteLeadResponse(message="Lead deleted successfully")

@router.get("/stats")
async def get_crm_stats(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get CRM statistics for the user, cached for 60 seconds"""
    user_id = current_user.id
    now = datetime.utcnow()
    cache_key = f"stats_{user_id}"
    with _stats_cache_lock:
        entry = _stats_cache.get(cache_key)
        if entry and (now - entry["timestamp"]).total_seconds() < CACHE_TIMEOUT_SECONDS:
            return entry["data"]
    # Compute stats as before
    total_leads = db.query(Leads).filter(Leads.user_id == user_id).count()
    status_counts = db.query(Leads.status, db.func.count(Leads.id)).filter(
        Leads.user_id == user_id
    ).group_by(Leads.status).all()
    source_counts = db.query(Leads.source, db.func.count(Leads.id)).filter(
        Leads.user_id == user_id
    ).group_by(Leads.source).all()
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_leads = db.query(Leads).filter(
        Leads.user_id == user_id,
        Leads.created_at >= thirty_days_ago
    ).count()
    data = {
        "total_leads": total_leads,
        "recent_leads": recent_leads,
        "status_breakdown": dict(status_counts),
        "source_breakdown": dict(source_counts)
    }
    with _stats_cache_lock:
        _stats_cache[cache_key] = {"timestamp": now, "data": data}
    return data

@router.post("/leads/import", summary="Import leads", description="Import multiple leads in bulk.", response_model=List[LeadResponse])
async def import_leads(
    leads_data: List[LeadCreate] = Body(..., description="List of leads to import."),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Import multiple leads in bulk.

- **leads_data**: List of LeadCreate.
- **Returns**: List of LeadResponse."""
    created_leads = []
    
    for lead_data in leads_data:
        lead = Leads(
            user_id=current_user.id,
            name=lead_data.name,
            email=lead_data.email,
            phone=lead_data.phone,
            company=lead_data.company,
            website=lead_data.website,
            address=lead_data.address,
            source="import",
            notes=lead_data.notes,
            tags=json.dumps(lead_data.tags) if lead_data.tags else None
        )
        db.add(lead)
        created_leads.append(lead)
    
    db.commit()
    
    return [
        LeadResponse(
            id=lead.id,
            name=lead.name,
            email=lead.email,
            phone=lead.phone,
            company=lead.company,
            website=lead.website,
            address=lead.address,
            source=lead.source,
            status=lead.status,
            notes=lead.notes,
            tags=json.loads(lead.tags) if lead.tags else [],
            created_at=lead.created_at,
            updated_at=lead.updated_at
        ) for lead in created_leads
    ]

@router.post("/leads/bulk-delete", summary="Bulk delete leads", description="Delete multiple leads by their IDs.", response_model=BulkDeleteLeadsResponse)
def bulk_delete_leads(req: BulkDeleteLeadsRequest, db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    """Delete multiple leads by their IDs.

- **lead_ids**: List of lead IDs.
- **Returns**: Number of leads deleted."""
    leads = db.query(Leads).filter(Leads.id.in_(req.lead_ids), Leads.user_id == user.id).all()
    count = len(leads)
    for lead in leads:
        db.delete(lead)
    db.commit()
    return {"deleted": count}

@router.post("/leads/bulk-add", summary="Bulk add leads", description="Add multiple leads in bulk.", response_model=BulkAddLeadsResponse)
def bulk_add_leads(req: BulkAddLeadsRequest, db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    """Add multiple leads in bulk.

- **leads**: List of LeadCreate.
- **Returns**: Number of leads added."""
    count = 0
    for lead_data in req.leads:
        lead = Leads(
            user_id=user.id,
            name=lead_data.name,
            email=lead_data.email,
            phone=lead_data.phone,
            company=lead_data.company,
            website=lead_data.website,
            address=lead_data.address,
            source=lead_data.source,
            notes=lead_data.notes,
            tags=json.dumps(lead_data.tags) if lead_data.tags else None
        )
        db.add(lead)
        count += 1
    db.commit()
    return {"added": count}

@router.post("/leads/{lead_id}/enrich", summary="Enrich a lead", description="Enrich a lead with additional data from external sources.")
def enrich_lead(lead_id: int = Path(..., description="ID of the lead to enrich."), db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    """Enrich a lead with additional data from external sources.

- **lead_id**: Lead ID.
- **Returns**: Enriched lead data."""
    lead = db.query(Leads).filter(Leads.id == lead_id, Leads.user_id == user.id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    # TODO: Implement real enrichment logic here (e.g., call external API)
    # For now, do nothing and return the lead as-is
    db.commit()
    db.refresh(lead)
    return lead

@router.post("/connect", summary="Connect CRM provider", description="Connect to an external CRM provider.")
def connect_crm(provider: str = Body(..., description="CRM provider name (e.g., hubspot, salesforce)"), db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    """Connect to an external CRM provider.

- **provider**: CRM provider name.
- **Returns**: Status message."""
    # For now, just store provider; real implementation would redirect to OAuth
    if provider not in ["hubspot", "salesforce", "mailchimp"]:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    user.crm_provider = provider
    db.commit()
    # In real implementation, redirect to provider's OAuth URL
    return {"status": "oauth_required", "provider": provider, "oauth_url": f"/api/crm/oauth/{provider}"}

@router.get("/status", summary="Get CRM connection status", description="Get the current CRM connection status for the user.")
def crm_status(user: Users = Depends(get_current_user)):
    """Get the current CRM connection status for the user.

- **Returns**: Status and provider info."""
    return {
        "crm_provider": user.crm_provider,
        "crm_connected": bool(user.crm_access_token),
        "email_provider": user.email_provider,
        "email_connected": bool(user.email_access_token)
    }

@router.post("/disconnect", summary="Disconnect CRM provider", description="Disconnect from the external CRM provider.")
def disconnect_crm(db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    """Disconnect from the external CRM provider.

- **Returns**: Status message."""
    user.crm_provider = None
    user.crm_access_token = None
    user.crm_refresh_token = None
    user.crm_token_expiry = None
    user.email_provider = None
    user.email_access_token = None
    user.email_refresh_token = None
    user.email_token_expiry = None
    db.commit()
    return {"status": "disconnected"}

@router.get("/oauth/{provider}")
def oauth_callback(provider: str, request: Request, db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    # Stub: In real implementation, handle OAuth callback, exchange code for tokens, store in user
    # Example: user.crm_access_token = ...
    # db.commit()
    return {"status": "oauth_callback_stub", "provider": provider}

@router.post("/leads/{lead_id}/push", summary="Push lead to CRM", description="Push a lead to the connected external CRM provider.")
def push_lead_to_crm(lead_id: int = Path(..., description="ID of the lead to push."), db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    """Push a lead to the connected external CRM provider.

- **lead_id**: Lead ID.
- **Returns**: Status message."""
    lead = db.query(Leads).filter(Leads.id == lead_id, Leads.user_id == user.id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    # For demo, just mark as pushed (real: API call to CRM)
    lead.notes = (lead.notes or "") + "\n[Pushed to CRM]"
    db.commit()
    return {"status": "pushed", "lead_id": lead_id}

@router.post("/leads/{lead_id}/share", summary="Share a lead", description="Generate a shareable link for a lead.")
def share_lead(lead_id: int = Path(..., description="ID of the lead to share."), db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    """Generate a shareable link for a lead.

- **lead_id**: Lead ID.
- **Returns**: Shareable URL."""
    lead = db.query(Leads).filter(Leads.id == lead_id, Leads.user_id == current_user.id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    if lead.share_token:
        return {"share_token": lead.share_token, "url": f"/api/crm/leads/shared/{lead.share_token}"}
    token = secrets.token_urlsafe(32)
    lead.share_token = token
    db.commit()
    return {"share_token": token, "url": f"/api/crm/leads/shared/{token}"}

@router.post("/leads/{lead_id}/unshare", summary="Unshare a lead", description="Disable the shareable link for a lead.")
def unshare_lead(lead_id: int = Path(..., description="ID of the lead to unshare."), db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    """Disable the shareable link for a lead.

- **lead_id**: Lead ID.
- **Returns**: Status message."""
    lead = db.query(Leads).filter(Leads.id == lead_id, Leads.user_id == current_user.id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead.share_token = None
    db.commit()
    return {"status": "unshared"}

@router.get("/leads/shared/{share_token}", summary="Get shared lead", description="Get a shared lead by its share token.")
def get_shared_lead(share_token: str = Path(..., description="Share token for the lead."), db: Session = Depends(get_db)):
    """Get a shared lead by its share token.

- **share_token**: Token from the shareable link.
- **Returns**: Lead details if valid."""
    lead = db.query(Leads).filter(Leads.share_token == share_token).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Shared lead not found")
    return {
        "id": lead.id,
        "name": lead.name,
        "email": lead.email,
        "phone": lead.phone,
        "company": lead.company,
        "status": lead.status,
        "source": lead.source,
        "notes": lead.notes,
        "created_at": lead.created_at,
        "updated_at": lead.updated_at
    } 