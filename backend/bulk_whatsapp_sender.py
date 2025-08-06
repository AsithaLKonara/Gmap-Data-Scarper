from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Body, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
import json
import asyncio
import csv
import io
import pandas as pd
from datetime import datetime, timedelta
import logging
from models import Users, BulkWhatsAppCampaigns, BulkWhatsAppMessages, WhatsAppContacts, WhatsAppTemplates
from database import get_db
from auth import get_current_user
from security import check_permission
from whatsapp_automation import whatsapp_api
import secrets
import os

router = APIRouter(prefix="/api/bulk-whatsapp", tags=["bulk-whatsapp"])
logger = logging.getLogger("bulk_whatsapp_sender")

# Pydantic models
class ContactData(BaseModel):
    phone_number: str = Field(..., description="Phone number with country code")
    name: Optional[str] = Field(None, description="Contact name")
    email: Optional[str] = Field(None, description="Contact email")
    company: Optional[str] = Field(None, description="Company name")
    custom_fields: Optional[Dict[str, str]] = Field(None, description="Custom fields")

class MessageTemplate(BaseModel):
    name: str = Field(..., description="Template name")
    content: str = Field(..., description="Message content with variables")
    variables: List[str] = Field(..., description="List of variables used in template")
    media_url: Optional[str] = Field(None, description="Media URL if any")
    media_type: Optional[str] = Field(None, description="Media type (image, video, document)")

class BulkCampaignCreate(BaseModel):
    name: str = Field(..., description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    template_id: Optional[int] = Field(None, description="Template ID")
    message_content: str = Field(..., description="Message content")
    contacts: List[ContactData] = Field(..., description="List of contacts")
    schedule_type: str = Field("immediate", description="Schedule type: immediate, scheduled, recurring")
    schedule_time: Optional[datetime] = Field(None, description="Scheduled time")
    delay_between_messages: int = Field(30, description="Delay between messages in seconds")
    max_messages_per_hour: int = Field(50, description="Maximum messages per hour")
    max_messages_per_day: int = Field(500, description="Maximum messages per day")
    retry_failed: bool = Field(True, description="Retry failed messages")
    max_retries: int = Field(3, description="Maximum retry attempts")

class CampaignStatus(BaseModel):
    campaign_id: int
    status: str
    total_messages: int
    sent_messages: int
    failed_messages: int
    pending_messages: int
    success_rate: float
    start_time: Optional[datetime]
    end_time: Optional[datetime]

class BulkWhatsAppSender:
    def __init__(self):
        self.active_campaigns = {}
        self.rate_limit_tracker = {}
    
    async def create_campaign(self, campaign_data: BulkCampaignCreate, user_id: int, db: Session):
        """Create a new bulk WhatsApp campaign"""
        try:
            # Validate phone numbers
            validated_contacts = []
            for contact in campaign_data.contacts:
                phone = self.normalize_phone_number(contact.phone_number)
                if phone:
                    contact.phone_number = phone
                    validated_contacts.append(contact)
                else:
                    logger.warning(f"Invalid phone number: {contact.phone_number}")
            
            if not validated_contacts:
                raise HTTPException(status_code=400, detail="No valid phone numbers found")
            
            # Create campaign record
            campaign = BulkWhatsAppCampaigns(
                name=campaign_data.name,
                description=campaign_data.description,
                message_content=campaign_data.message_content,
                template_id=campaign_data.template_id,
                schedule_type=campaign_data.schedule_type,
                schedule_time=campaign_data.schedule_time,
                delay_between_messages=campaign_data.delay_between_messages,
                max_messages_per_hour=campaign_data.max_messages_per_hour,
                max_messages_per_day=campaign_data.max_messages_per_day,
                retry_failed=campaign_data.retry_failed,
                max_retries=campaign_data.max_retries,
                user_id=user_id,
                status="pending",
                total_contacts=len(validated_contacts)
            )
            
            db.add(campaign)
            db.commit()
            db.refresh(campaign)
            
            # Create message records
            for contact in validated_contacts:
                message = BulkWhatsAppMessages(
                    campaign_id=campaign.id,
                    phone_number=contact.phone_number,
                    contact_name=contact.name,
                    message_content=self.personalize_message(
                        campaign_data.message_content, contact
                    ),
                    status="pending",
                    retry_count=0
                )
                db.add(message)
            
            db.commit()
            
            return {
                "campaign_id": campaign.id,
                "total_contacts": len(validated_contacts),
                "status": "created"
            }
            
        except Exception as e:
            logger.exception("Error creating bulk campaign")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def start_campaign(self, campaign_id: int, db: Session):
        """Start a bulk WhatsApp campaign"""
        try:
            campaign = db.query(BulkWhatsAppCampaigns).filter(
                BulkWhatsAppCampaigns.id == campaign_id
            ).first()
            
            if not campaign:
                raise HTTPException(status_code=404, detail="Campaign not found")
            
            if campaign.status != "pending":
                raise HTTPException(status_code=400, detail="Campaign already started or completed")
            
            # Update campaign status
            campaign.status = "running"
            campaign.start_time = datetime.utcnow()
            db.commit()
            
            # Start background task
            asyncio.create_task(self.execute_campaign(campaign_id, db))
            
            return {"status": "started", "campaign_id": campaign_id}
            
        except Exception as e:
            logger.exception("Error starting campaign")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def execute_campaign(self, campaign_id: int, db: Session):
        """Execute the bulk campaign with rate limiting"""
        try:
            campaign = db.query(BulkWhatsAppCampaigns).filter(
                BulkWhatsAppCampaigns.id == campaign_id
            ).first()
            
            messages = db.query(BulkWhatsAppMessages).filter(
                BulkWhatsAppMessages.campaign_id == campaign_id,
                BulkWhatsAppMessages.status == "pending"
            ).all()
            
            messages_sent = 0
            messages_per_hour = 0
            messages_per_day = 0
            hour_start = datetime.utcnow()
            day_start = datetime.utcnow()
            
            for message in messages:
                # Check rate limits
                current_time = datetime.utcnow()
                
                # Reset hourly counter
                if (current_time - hour_start).seconds >= 3600:
                    messages_per_hour = 0
                    hour_start = current_time
                
                # Reset daily counter
                if (current_time - day_start).days >= 1:
                    messages_per_day = 0
                    day_start = current_time
                
                # Check limits
                if messages_per_hour >= campaign.max_messages_per_hour:
                    await asyncio.sleep(3600 - (current_time - hour_start).seconds)
                    messages_per_hour = 0
                    hour_start = datetime.utcnow()
                
                if messages_per_day >= campaign.max_messages_per_day:
                    await asyncio.sleep(86400 - (current_time - day_start).seconds)
                    messages_per_day = 0
                    day_start = datetime.utcnow()
                
                # Send message
                try:
                    result = await whatsapp_api.send_message(
                        phone_number=message.phone_number,
                        message=message.message_content,
                        message_type="text"
                    )
                    
                    message.status = "sent"
                    message.sent_at = datetime.utcnow()
                    message.message_id = result.get("message_id")
                    messages_sent += 1
                    messages_per_hour += 1
                    messages_per_day += 1
                    
                except Exception as e:
                    logger.error(f"Failed to send message to {message.phone_number}: {str(e)}")
                    message.status = "failed"
                    message.error_message = str(e)
                    message.retry_count += 1
                    
                    # Retry logic
                    if campaign.retry_failed and message.retry_count < campaign.max_retries:
                        message.status = "pending"
                
                db.commit()
                
                # Delay between messages
                if campaign.delay_between_messages > 0:
                    await asyncio.sleep(campaign.delay_between_messages)
            
            # Update campaign status
            campaign.status = "completed"
            campaign.end_time = datetime.utcnow()
            campaign.sent_messages = messages_sent
            db.commit()
            
        except Exception as e:
            logger.exception(f"Error executing campaign {campaign_id}")
            campaign.status = "failed"
            campaign.error_message = str(e)
            db.commit()
    
    def normalize_phone_number(self, phone: str) -> Optional[str]:
        """Normalize and validate phone number"""
        try:
            # Remove all non-digit characters
            digits = ''.join(filter(str.isdigit, phone))
            
            # Add country code if missing
            if len(digits) == 10:
                digits = "1" + digits  # Default to US
            elif len(digits) == 11 and digits.startswith("1"):
                pass  # Already has US country code
            elif len(digits) >= 10:
                pass  # Assume it's valid
            else:
                return None
            
            return f"+{digits}"
            
        except Exception:
            return None
    
    def personalize_message(self, template: str, contact: ContactData) -> str:
        """Replace variables in message template with contact data"""
        try:
            personalized = template
            
            # Replace standard variables
            replacements = {
                "{{name}}": contact.name or "there",
                "{{phone}}": contact.phone_number,
                "{{email}}": contact.email or "",
                "{{company}}": contact.company or "",
            }
            
            for var, value in replacements.items():
                personalized = personalized.replace(var, str(value))
            
            # Replace custom fields
            if contact.custom_fields:
                for key, value in contact.custom_fields.items():
                    personalized = personalized.replace(f"{{{{{key}}}}}", str(value))
            
            return personalized
            
        except Exception as e:
            logger.error(f"Error personalizing message: {str(e)}")
            return template

bulk_sender = BulkWhatsAppSender()

# API Endpoints
@router.post("/campaigns", response_model=Dict[str, Any])
async def create_bulk_campaign(
    campaign_data: BulkCampaignCreate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new bulk WhatsApp campaign"""
    if not check_permission(current_user, "whatsapp:bulk_send"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return await bulk_sender.create_campaign(campaign_data, current_user.id, db)

@router.post("/campaigns/{campaign_id}/start")
async def start_bulk_campaign(
    campaign_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a bulk WhatsApp campaign"""
    if not check_permission(current_user, "whatsapp:bulk_send"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return await bulk_sender.start_campaign(campaign_id, db)

@router.get("/campaigns", response_model=List[Dict[str, Any]])
async def list_bulk_campaigns(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List bulk WhatsApp campaigns"""
    query = db.query(BulkWhatsAppCampaigns).filter(
        BulkWhatsAppCampaigns.user_id == current_user.id
    )
    
    if status:
        query = query.filter(BulkWhatsAppCampaigns.status == status)
    
    campaigns = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "status": c.status,
            "total_contacts": c.total_contacts,
            "sent_messages": c.sent_messages,
            "created_at": c.created_at,
            "start_time": c.start_time,
            "end_time": c.end_time
        }
        for c in campaigns
    ]

@router.get("/campaigns/{campaign_id}/status", response_model=CampaignStatus)
async def get_campaign_status(
    campaign_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get campaign status and statistics"""
    campaign = db.query(BulkWhatsAppCampaigns).filter(
        BulkWhatsAppCampaigns.id == campaign_id,
        BulkWhatsAppCampaigns.user_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Get message statistics
    total_messages = db.query(BulkWhatsAppMessages).filter(
        BulkWhatsAppMessages.campaign_id == campaign_id
    ).count()
    
    sent_messages = db.query(BulkWhatsAppMessages).filter(
        BulkWhatsAppMessages.campaign_id == campaign_id,
        BulkWhatsAppMessages.status == "sent"
    ).count()
    
    failed_messages = db.query(BulkWhatsAppMessages).filter(
        BulkWhatsAppMessages.campaign_id == campaign_id,
        BulkWhatsAppMessages.status == "failed"
    ).count()
    
    pending_messages = db.query(BulkWhatsAppMessages).filter(
        BulkWhatsAppMessages.campaign_id == campaign_id,
        BulkWhatsAppMessages.status == "pending"
    ).count()
    
    success_rate = (sent_messages / total_messages * 100) if total_messages > 0 else 0
    
    return CampaignStatus(
        campaign_id=campaign.id,
        status=campaign.status,
        total_messages=total_messages,
        sent_messages=sent_messages,
        failed_messages=failed_messages,
        pending_messages=pending_messages,
        success_rate=success_rate,
        start_time=campaign.start_time,
        end_time=campaign.end_time
    )

@router.post("/import-contacts")
async def import_contacts(
    file: UploadFile = File(...),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Import contacts from CSV/Excel file"""
    if not check_permission(current_user, "whatsapp:bulk_send"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        # Read file content
        content = await file.read()
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        contacts = []
        for _, row in df.iterrows():
            contact = ContactData(
                phone_number=str(row.get('phone_number', '')),
                name=str(row.get('name', '')) if pd.notna(row.get('name')) else None,
                email=str(row.get('email', '')) if pd.notna(row.get('email')) else None,
                company=str(row.get('company', '')) if pd.notna(row.get('company')) else None
            )
            contacts.append(contact)
        
        return {
            "total_contacts": len(contacts),
            "contacts": [c.dict() for c in contacts[:10]]  # Return first 10 for preview
        }
        
    except Exception as e:
        logger.exception("Error importing contacts")
        raise HTTPException(status_code=500, detail=f"Error importing contacts: {str(e)}")

@router.get("/templates", response_model=List[Dict[str, Any]])
async def get_message_templates(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get message templates for bulk campaigns"""
    templates = db.query(WhatsAppTemplates).filter(
        WhatsAppTemplates.user_id == current_user.id
    ).all()
    
    return [
        {
            "id": t.id,
            "name": t.name,
            "content": t.content,
            "variables": json.loads(t.variables) if t.variables else [],
            "media_url": t.media_url,
            "media_type": t.media_type
        }
        for t in templates
    ]

@router.post("/templates", response_model=Dict[str, Any])
async def create_message_template(
    template_data: MessageTemplate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new message template"""
    if not check_permission(current_user, "whatsapp:bulk_send"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    template = WhatsAppTemplates(
        name=template_data.name,
        content=template_data.content,
        variables=json.dumps(template_data.variables),
        media_url=template_data.media_url,
        media_type=template_data.media_type,
        user_id=current_user.id
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return {
        "id": template.id,
        "name": template.name,
        "content": template.content,
        "variables": template_data.variables
    }

@router.get("/analytics", response_model=Dict[str, Any])
async def get_bulk_analytics(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get bulk messaging analytics"""
    # Total campaigns
    total_campaigns = db.query(BulkWhatsAppCampaigns).filter(
        BulkWhatsAppCampaigns.user_id == current_user.id
    ).count()
    
    # Total messages
    total_messages = db.query(BulkWhatsAppMessages).join(
        BulkWhatsAppCampaigns
    ).filter(
        BulkWhatsAppCampaigns.user_id == current_user.id
    ).count()
    
    # Success rate
    sent_messages = db.query(BulkWhatsAppMessages).join(
        BulkWhatsAppCampaigns
    ).filter(
        BulkWhatsAppCampaigns.user_id == current_user.id,
        BulkWhatsAppMessages.status == "sent"
    ).count()
    
    success_rate = (sent_messages / total_messages * 100) if total_messages > 0 else 0
    
    # Recent activity
    recent_campaigns = db.query(BulkWhatsAppCampaigns).filter(
        BulkWhatsAppCampaigns.user_id == current_user.id
    ).order_by(BulkWhatsAppCampaigns.created_at.desc()).limit(5).all()
    
    return {
        "total_campaigns": total_campaigns,
        "total_messages": total_messages,
        "sent_messages": sent_messages,
        "success_rate": success_rate,
        "recent_campaigns": [
            {
                "id": c.id,
                "name": c.name,
                "status": c.status,
                "sent_messages": c.sent_messages,
                "created_at": c.created_at
            }
            for c in recent_campaigns
        ]
    } 