from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, Request
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime, timedelta
from database import get_db
from models import User, Lead, SystemLog
from auth import get_current_user
from pydantic import BaseModel
import secrets
from config import lru_cache, CACHE_TIMEOUT_SECONDS
import threading
from tenant_utils import get_tenant_from_request, get_tenant_record_or_403

router = APIRouter(prefix="/api/crm", tags=["crm"])

class LeadCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    source: str = "manual"
    notes: Optional[str] = None
    tags: Optional[List[str]] = None

class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None

class LeadResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    company: Optional[str]
    website: Optional[str]
    address: Optional[str]
    source: str
    status: str
    notes: Optional[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime

# Thread-safe cache for per-user stats
_stats_cache = {}
_stats_cache_lock = threading.Lock()

@router.post("/leads", response_model=LeadResponse)
async def create_lead(
    lead_data: LeadCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new lead"""
    lead = Lead(
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
    log = SystemLog(
        level="INFO",
        module="crm",
        message=f"Lead created: {lead_data.name} ({lead_data.email})",
        details=json.dumps({"lead_id": lead.id, "source": lead_data.source}),
        user_id=current_user.id
    )
    db.add(log)
    db.commit()
    
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

@router.get("/leads", response_model=List[LeadResponse])
async def get_leads(
    status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's leads with filtering and pagination"""
    query = db.query(Lead).filter(Lead.user_id == current_user.id)
    
    if status:
        query = query.filter(Lead.status == status)
    if source:
        query = query.filter(Lead.source == source)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Lead.name.ilike(search_filter)) |
            (Lead.email.ilike(search_filter)) |
            (Lead.company.ilike(search_filter))
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

@router.get("/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific lead"""
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.user_id == current_user.id).first()
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

@router.put("/leads/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: int,
    lead_data: LeadUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a lead"""
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.user_id == current_user.id).first()
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

@router.delete("/leads/{lead_id}")
async def delete_lead(
    lead_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a lead"""
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.user_id == current_user.id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    db.delete(lead)
    db.commit()
    
    return {"message": "Lead deleted successfully"}

@router.get("/stats")
async def get_crm_stats(
    current_user: User = Depends(get_current_user),
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
    total_leads = db.query(Lead).filter(Lead.user_id == user_id).count()
    status_counts = db.query(Lead.status, db.func.count(Lead.id)).filter(
        Lead.user_id == user_id
    ).group_by(Lead.status).all()
    source_counts = db.query(Lead.source, db.func.count(Lead.id)).filter(
        Lead.user_id == user_id
    ).group_by(Lead.source).all()
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_leads = db.query(Lead).filter(
        Lead.user_id == user_id,
        Lead.created_at >= thirty_days_ago
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

@router.post("/leads/import")
async def import_leads(
    leads_data: List[LeadCreate],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Import multiple leads"""
    created_leads = []
    
    for lead_data in leads_data:
        lead = Lead(
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
    
    return {
        "message": f"Successfully imported {len(created_leads)} leads",
        "imported_count": len(created_leads)
    }

@router.post("/leads/bulk-delete")
def bulk_delete_leads(lead_ids: list = Body(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    leads = db.query(Lead).filter(Lead.id.in_(lead_ids), Lead.user_id == user.id).all()
    count = len(leads)
    for lead in leads:
        db.delete(lead)
    db.commit()
    return {"deleted": count}

@router.post("/leads/bulk-add")
def bulk_add_leads(leads: list = Body(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    added = 0
    for lead_data in leads:
        lead = Lead(user_id=user.id, **lead_data)
        db.add(lead)
        added += 1
    db.commit()
    return {"added": added}

@router.post("/leads/{lead_id}/enrich")
def enrich_lead(lead_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.user_id == user.id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    # TODO: Implement real enrichment logic here (e.g., call external API)
    # For now, do nothing and return the lead as-is
    db.commit()
    db.refresh(lead)
    return lead

@router.post("/connect")
def connect_crm(provider: str = Body(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # For now, just store provider; real implementation would redirect to OAuth
    if provider not in ["hubspot", "salesforce", "mailchimp"]:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    user.crm_provider = provider
    db.commit()
    # In real implementation, redirect to provider's OAuth URL
    return {"status": "oauth_required", "provider": provider, "oauth_url": f"/api/crm/oauth/{provider}"}

@router.get("/status")
def crm_status(user: User = Depends(get_current_user)):
    return {
        "crm_provider": user.crm_provider,
        "crm_connected": bool(user.crm_access_token),
        "email_provider": user.email_provider,
        "email_connected": bool(user.email_access_token)
    }

@router.post("/disconnect")
def disconnect_crm(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
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
def oauth_callback(provider: str, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Stub: In real implementation, handle OAuth callback, exchange code for tokens, store in user
    # Example: user.crm_access_token = ...
    # db.commit()
    return {"status": "oauth_callback_stub", "provider": provider}

@router.post("/leads/{lead_id}/push")
def push_lead_to_crm(lead_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.user_id == user.id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    # For demo, just mark as pushed (real: API call to CRM)
    lead.notes = (lead.notes or "") + "\n[Pushed to CRM]"
    db.commit()
    return {"status": "pushed", "lead_id": lead_id}

@router.post("/leads/{lead_id}/share")
def share_lead(lead_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.user_id == current_user.id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    if lead.share_token:
        return {"share_token": lead.share_token, "url": f"/api/crm/leads/shared/{lead.share_token}"}
    token = secrets.token_urlsafe(32)
    lead.share_token = token
    db.commit()
    return {"share_token": token, "url": f"/api/crm/leads/shared/{token}"}

@router.post("/leads/{lead_id}/unshare")
def unshare_lead(lead_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.user_id == current_user.id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead.share_token = None
    db.commit()
    return {"status": "unshared"}

@router.get("/leads/shared/{share_token}")
def get_shared_lead(share_token: str, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.share_token == share_token).first()
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