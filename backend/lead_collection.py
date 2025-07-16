from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Body, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from models import User, LeadSource, LeadCollection, SocialMediaLead, SystemLog
from database import get_db
from auth import get_current_user
import logging
import secrets

router = APIRouter(prefix="/api/lead-collection", tags=["lead-collection"])
logger = logging.getLogger("lead_collection")

# --- Pydantic Models for OpenAPI ---
class LeadSourceCreate(BaseModel):
    name: str = Field(..., description="Name of the lead source.")
    type: str = Field(..., description="Type of the lead source (e.g., facebook, instagram, whatsapp).")
    config: Optional[Dict[str, Any]] = Field(None, description="Configuration for the lead source.")

class LeadSourceStatus(BaseModel):
    id: int
    name: str
    type: str
    status: str
    last_sync: Optional[datetime]
    config: Optional[Dict[str, Any]]

class LeadCollectionCreate(BaseModel):
    name: str = Field(..., description="Name of the lead collection.")
    description: Optional[str] = Field(None, description="Description of the collection.")
    source_id: int = Field(..., description="ID of the lead source.")
    config: Optional[Dict[str, Any]] = Field(None, description="Configuration for the collection.")

class LeadCollectionStatus(BaseModel):
    id: int
    name: str
    description: Optional[str]
    source_id: int
    status: str
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    created_at: datetime

class SocialMediaLeadResponse(BaseModel):
    id: int
    platform: str
    platform_id: str
    username: Optional[str]
    display_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    bio: Optional[str]
    followers_count: Optional[int]
    following_count: Optional[int]
    posts_count: Optional[int]
    location: Optional[str]
    website: Optional[str]
    profile_url: Optional[str]
    avatar_url: Optional[str]
    verified: bool
    business_category: Optional[str]
    engagement_score: Optional[float]
    status: str
    tags: List[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

# --- Endpoints with OpenAPI docs ---

@router.post("/sources", response_model=Dict[str, Any], summary="Create lead source", description="Create a new lead source (Pro/Business only).")
async def create_lead_source(
    source_data: LeadSourceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new lead source. Pro/Business plan required."""
    if current_user.plan not in ['pro', 'business']:
        raise HTTPException(status_code=403, detail="Pro or Business plan required")
    
    source = LeadSource(
        name=source_data.name,
        type=source_data.type,
        config=json.dumps(source_data.config) if source_data.config else None
    )
    
    db.add(source)
    db.commit()
    db.refresh(source)
    
    return {
        "id": source.id,
        "name": source.name,
        "type": source.type,
        "config": json.loads(source.config) if source.config else None
    }

@router.get("/sources", response_model=List[LeadSourceStatus], summary="List available lead sources", description="Get all available lead sources and their connection status.")
def list_lead_sources(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get all available lead sources and their connection status."""
    sources = db.query(LeadSource).filter(LeadSource.user_id == user.id).all()
    result = []
    for source in sources:
        result.append(LeadSourceStatus(
            id=source.id,
            name=source.name,
            type=source.type,
            status=source.status if hasattr(source, 'status') else 'unknown',
            last_sync=source.last_sync if hasattr(source, 'last_sync') else None,
            config=json.loads(source.config) if source.config else None
        ))
    return result

# Lead collection management
@router.post("/collections", response_model=Dict[str, Any], summary="Create lead collection", description="Create a new lead collection (Pro/Business only).")
async def create_lead_collection(
    collection_data: LeadCollectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new lead collection. Pro/Business plan required."""
    if current_user.plan not in ['pro', 'business']:
        raise HTTPException(status_code=403, detail="Pro or Business plan required")
    
    # Verify source exists
    source = db.query(LeadSource).filter(LeadSource.id == collection_data.source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Lead source not found")
    
    collection = LeadCollection(
        name=collection_data.name,
        description=collection_data.description,
        source_id=collection_data.source_id,
        user_id=current_user.id,
        config=json.dumps(collection_data.config) if collection_data.config else None
    )
    
    db.add(collection)
    db.commit()
    db.refresh(collection)
    
    return {
        "id": collection.id,
        "name": collection.name,
        "description": collection.description,
        "source_id": collection.source_id,
        "status": collection.status,
        "created_at": collection.created_at
    }

@router.get("/collections", response_model=List[LeadCollectionStatus], summary="List lead collections", description="Get all lead collections for the authenticated user.")
async def get_lead_collections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all lead collections for the authenticated user."""
    collections = db.query(LeadCollection).filter(LeadCollection.user_id == current_user.id).all()
    return [
        {
            "id": collection.id,
            "name": collection.name,
            "description": collection.description,
            "source_id": collection.source_id,
            "status": collection.status,
            "last_run": collection.last_run,
            "next_run": collection.next_run,
            "created_at": collection.created_at
        }
        for collection in collections
    ]

# Social media lead collection
class FacebookCollectRequest(BaseModel):
    keywords: List[str] = Field(..., description="Keywords to search for.")
    location: Optional[str] = Field(None, description="Location filter.")
    max_results: int = Field(100, description="Maximum number of results.")

@router.post("/collect/facebook", summary="Collect Facebook leads", description="Collect leads from Facebook (Pro/Business only).")
async def collect_facebook_leads(
    background_tasks: BackgroundTasks,
    keywords: List[str] = Body(..., description="Keywords to search for."),
    location: Optional[str] = Body(None, description="Location filter."),
    max_results: int = Body(100, description="Maximum number of results."),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Collect leads from Facebook. Pro/Business plan required."""
    if current_user.plan not in ['pro', 'business']:
        raise HTTPException(status_code=403, detail="Pro or Business plan required")
    
    # Create collection
    collection = LeadCollection(
        name=f"Facebook Collection - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        description=f"Keywords: {', '.join(keywords)}",
        source_id=1,  # Facebook source ID
        user_id=current_user.id,
        config=json.dumps({
            "keywords": keywords,
            "location": location,
            "max_results": max_results
        })
    )
    
    db.add(collection)
    db.commit()
    db.refresh(collection)
    
    # Start background collection
    background_tasks.add_task(
        collect_facebook_leads_task,
        collection.id,
        keywords,
        location,
        max_results,
        current_user.id
    )
    
    return {
        "collection_id": collection.id,
        "status": "started",
        "message": "Facebook lead collection started"
    }

class InstagramCollectRequest(BaseModel):
    hashtags: List[str] = Field(..., description="Hashtags to search for.")
    location: Optional[str] = Field(None, description="Location filter.")
    max_results: int = Field(100, description="Maximum number of results.")

@router.post("/collect/instagram", summary="Collect Instagram leads", description="Collect leads from Instagram (Pro/Business only).")
async def collect_instagram_leads(
    background_tasks: BackgroundTasks,
    hashtags: List[str] = Body(..., description="Hashtags to search for."),
    location: Optional[str] = Body(None, description="Location filter."),
    max_results: int = Body(100, description="Maximum number of results."),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Collect leads from Instagram. Pro/Business plan required."""
    if current_user.plan not in ['pro', 'business']:
        raise HTTPException(status_code=403, detail="Pro or Business plan required")
    
    collection = LeadCollection(
        name=f"Instagram Collection - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        description=f"Hashtags: {', '.join(hashtags)}",
        source_id=2,  # Instagram source ID
        user_id=current_user.id,
        config=json.dumps({
            "hashtags": hashtags,
            "location": location,
            "max_results": max_results
        })
    )
    
    db.add(collection)
    db.commit()
    db.refresh(collection)
    
    background_tasks.add_task(
        collect_instagram_leads_task,
        collection.id,
        hashtags,
        location,
        max_results,
        current_user.id
    )
    
    return {
        "collection_id": collection.id,
        "status": "started",
        "message": "Instagram lead collection started"
    }

class WhatsAppCollectRequest(BaseModel):
    phone_numbers: List[str] = Field(..., description="Phone numbers to search for.")
    keywords: List[str] = Field(..., description="Keywords to search for.")

@router.post("/collect/whatsapp", summary="Collect WhatsApp leads", description="Collect leads from WhatsApp (Pro/Business only).")
async def collect_whatsapp_leads(
    background_tasks: BackgroundTasks,
    phone_numbers: List[str] = Body(..., description="Phone numbers to search for."),
    keywords: List[str] = Body(..., description="Keywords to search for."),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Collect leads from WhatsApp. Pro/Business plan required."""
    if current_user.plan != 'business':
        raise HTTPException(status_code=403, detail="Business plan required")
    
    collection = LeadCollection(
        name=f"WhatsApp Collection - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        description=f"Keywords: {', '.join(keywords)}",
        source_id=3,  # WhatsApp source ID
        user_id=current_user.id,
        config=json.dumps({
            "phone_numbers": phone_numbers,
            "keywords": keywords
        })
    )
    
    db.add(collection)
    db.commit()
    db.refresh(collection)
    
    background_tasks.add_task(
        collect_whatsapp_leads_task,
        collection.id,
        phone_numbers,
        keywords,
        current_user.id
    )
    
    return {
        "collection_id": collection.id,
        "status": "started",
        "message": "WhatsApp lead collection started"
    }

# Background tasks
async def collect_facebook_leads_task(
    collection_id: int,
    keywords: List[str],
    location: Optional[str],
    max_results: int,
    user_id: int
):
    """Background task to collect Facebook leads"""
    # This would integrate with Facebook Graph API
    # For now, return mock data
    mock_leads = [
        {
            "platform": "facebook",
            "platform_id": f"fb_{i}",
            "username": f"business{i}",
            "display_name": f"Business {i}",
            "email": f"contact@business{i}.com",
            "phone": f"+1-555-{i:03d}-{i:04d}",
            "bio": f"Professional business services",
            "followers_count": 1000 + i * 100,
            "location": location or "New York",
            "website": f"https://business{i}.com",
            "verified": i % 3 == 0,
            "business_category": "Professional Services"
        }
        for i in range(1, min(max_results + 1, 11))
    ]
    
    # Save to database
    from database import SessionLocal
    db = SessionLocal()
    try:
        for lead_data in mock_leads:
            lead = SocialMediaLead(
                platform=lead_data["platform"],
                platform_id=lead_data["platform_id"],
                username=lead_data["username"],
                display_name=lead_data["display_name"],
                email=lead_data["email"],
                phone=lead_data["phone"],
                bio=lead_data["bio"],
                followers_count=lead_data["followers_count"],
                location=lead_data["location"],
                website=lead_data["website"],
                verified=lead_data["verified"],
                business_category=lead_data["business_category"],
                user_id=user_id,
                collection_id=collection_id
            )
            db.add(lead)
        
        # Update collection status
        collection = db.query(LeadCollection).filter(LeadCollection.id == collection_id).first()
        if collection:
            collection.last_run = datetime.utcnow()
            collection.status = "completed"
        
        db.commit()
    finally:
        db.close()

async def collect_instagram_leads_task(
    collection_id: int,
    hashtags: List[str],
    location: Optional[str],
    max_results: int,
    user_id: int
):
    """Background task to collect Instagram leads"""
    # This would integrate with Instagram Basic Display API
    mock_leads = [
        {
            "platform": "instagram",
            "platform_id": f"ig_{i}",
            "username": f"business{i}",
            "display_name": f"Business {i}",
            "email": f"hello@business{i}.com",
            "bio": f"Professional services and solutions",
            "followers_count": 500 + i * 50,
            "posts_count": 100 + i * 10,
            "location": location or "Los Angeles",
            "website": f"https://business{i}.com",
            "verified": i % 4 == 0,
            "business_category": "Professional Services"
        }
        for i in range(1, min(max_results + 1, 11))
    ]
    
    from database import SessionLocal
    db = SessionLocal()
    try:
        for lead_data in mock_leads:
            lead = SocialMediaLead(
                platform=lead_data["platform"],
                platform_id=lead_data["platform_id"],
                username=lead_data["username"],
                display_name=lead_data["display_name"],
                email=lead_data["email"],
                bio=lead_data["bio"],
                followers_count=lead_data["followers_count"],
                posts_count=lead_data["posts_count"],
                location=lead_data["location"],
                website=lead_data["website"],
                verified=lead_data["verified"],
                business_category=lead_data["business_category"],
                user_id=user_id,
                collection_id=collection_id
            )
            db.add(lead)
        
        collection = db.query(LeadCollection).filter(LeadCollection.id == collection_id).first()
        if collection:
            collection.last_run = datetime.utcnow()
            collection.status = "completed"
        
        db.commit()
    finally:
        db.close()

async def collect_whatsapp_leads_task(
    collection_id: int,
    phone_numbers: List[str],
    keywords: List[str],
    user_id: int
):
    """Background task to collect WhatsApp Business leads"""
    # This would integrate with WhatsApp Business API
    mock_leads = [
        {
            "platform": "whatsapp",
            "platform_id": f"wa_{i}",
            "display_name": f"Business {i}",
            "phone": phone_numbers[i % len(phone_numbers)] if phone_numbers else f"+1-555-{i:03d}-{i:04d}",
            "bio": f"Professional business services",
            "location": "New York",
            "business_category": "Professional Services"
        }
        for i in range(1, 11)
    ]
    
    from database import SessionLocal
    db = SessionLocal()
    try:
        for lead_data in mock_leads:
            lead = SocialMediaLead(
                platform=lead_data["platform"],
                platform_id=lead_data["platform_id"],
                display_name=lead_data["display_name"],
                phone=lead_data["phone"],
                bio=lead_data["bio"],
                location=lead_data["location"],
                business_category=lead_data["business_category"],
                user_id=user_id,
                collection_id=collection_id
            )
            db.add(lead)
        
        collection = db.query(LeadCollection).filter(LeadCollection.id == collection_id).first()
        if collection:
            collection.last_run = datetime.utcnow()
            collection.status = "completed"
        
        db.commit()
    finally:
        db.close()

# Get collected leads
@router.get("/leads", response_model=List[SocialMediaLeadResponse], summary="List social media leads", description="Get social media leads with optional filters for platform, status, and collection.")
async def get_social_media_leads(
    platform: Optional[str] = Query(None, description="Platform filter (facebook, instagram, whatsapp)."),
    status: Optional[str] = Query(None, description="Status filter."),
    collection_id: Optional[int] = Query(None, description="Collection ID filter."),
    page: int = Query(1, ge=1, description="Page number for pagination."),
    page_size: int = Query(20, ge=1, le=100, description="Number of leads per page."),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get social media leads with optional filters for platform, status, and collection."""
    query = db.query(SocialMediaLead).filter(SocialMediaLead.user_id == current_user.id)
    
    if platform:
        query = query.filter(SocialMediaLead.platform == platform)
    if status:
        query = query.filter(SocialMediaLead.status == status)
    if collection_id:
        query = query.filter(SocialMediaLead.collection_id == collection_id)
    
    total = query.count()
    leads = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return [
        SocialMediaLeadResponse(
            id=lead.id,
            platform=lead.platform,
            platform_id=lead.platform_id,
            username=lead.username,
            display_name=lead.display_name,
            email=lead.email,
            phone=lead.phone,
            bio=lead.bio,
            followers_count=lead.followers_count,
            following_count=lead.following_count,
            posts_count=lead.posts_count,
            location=lead.location,
            website=lead.website,
            profile_url=lead.profile_url,
            avatar_url=lead.avatar_url,
            verified=lead.verified,
            business_category=lead.business_category,
            engagement_score=lead.engagement_score,
            status=lead.status,
            tags=json.loads(lead.tags) if lead.tags else [],
            notes=lead.notes,
            created_at=lead.created_at,
            updated_at=lead.updated_at
        )
        for lead in leads
    ]

# Initialize default lead sources
def initialize_lead_sources(db: Session):
    """Initialize default lead sources"""
    default_sources = [
        {
            "name": "Facebook",
            "type": "social",
            "config": {
                "api_version": "v18.0",
                "required_permissions": ["pages_read_engagement", "pages_show_list"]
            }
        },
        {
            "name": "Instagram",
            "type": "social",
            "config": {
                "api_version": "v18.0",
                "required_permissions": ["instagram_basic", "instagram_content_publish"]
            }
        },
        {
            "name": "WhatsApp Business",
            "type": "social",
            "config": {
                "api_version": "v17.0",
                "required_permissions": ["whatsapp_business_management"]
            }
        },
        {
            "name": "LinkedIn",
            "type": "social",
            "config": {
                "api_version": "v2",
                "required_permissions": ["r_liteprofile", "r_emailaddress"]
            }
        },
        {
            "name": "Twitter",
            "type": "social",
            "config": {
                "api_version": "v2",
                "required_permissions": ["tweet.read", "users.read"]
            }
        }
    ]
    
    for source_data in default_sources:
        existing = db.query(LeadSource).filter(LeadSource.name == source_data["name"]).first()
        if not existing:
            source = LeadSource(
                name=source_data["name"],
                type=source_data["type"],
                config=json.dumps(source_data["config"])
            )
            db.add(source)
    
    db.commit() 