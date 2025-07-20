from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Body, Query, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from models import Users, WhatsAppCampaigns, WhatsAppTemplates, WhatsAppMessages, WhatsAppContacts, WhatsAppAutomations, Leads
from database import get_db
from auth import get_current_user
import logging
import secrets
import os
from fastapi import UploadFile, File
import shutil

router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])
logger = logging.getLogger("whatsapp")

# Pydantic models
class TemplateCreate(BaseModel):
    name: str
    content: str
    variables: Optional[List[str]] = None
    media_url: Optional[str] = None
    media_type: Optional[str] = None

class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    template_id: Optional[int] = None
    schedule_type: str = 'immediate'
    schedule_time: Optional[datetime] = None
    max_messages_per_hour: int = 50
    max_messages_per_day: int = 500
    contact_ids: List[int] = []

class MessageSend(BaseModel):
    recipient_phone: str
    recipient_name: Optional[str] = None
    message_content: str
    message_type: str = 'text'
    media_url: Optional[str] = None
    template_id: Optional[int] = None

class AutomationCreate(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_type: str
    trigger_conditions: Optional[Dict[str, Any]] = None
    template_id: int
    delay_minutes: int = 0

# WhatsApp Business API integration (mock for now)
class WhatsAppAPI:
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v17.0"
        self.access_token = os.getenv('WHATSAPP_ACCESS_TOKEN', 'mock_token')
        self.phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID', 'mock_phone_id')
    
    async def send_message(self, phone_number: str, message: str, message_type: str = 'text', media_url: str = None):
        """Send WhatsApp message via Business API"""
        try:
            # Mock implementation - in production, this would call WhatsApp Business API
            if message_type == 'text':
                payload = {
                    "messaging_product": "whatsapp",
                    "to": phone_number,
                    "type": "text",
                    "text": {"body": message}
                }
            elif message_type == 'image' and media_url:
                payload = {
                    "messaging_product": "whatsapp",
                    "to": phone_number,
                    "type": "image",
                    "image": {"link": media_url}
                }
            elif message_type == 'template':
                payload = {
                    "messaging_product": "whatsapp",
                    "to": phone_number,
                    "type": "template",
                    "template": {"name": message, "language": {"code": "en"}}
                }
            
            # Mock successful response
            return {
                "message_id": f"msg_{secrets.token_hex(8)}",
                "status": "sent"
            }
            
        except Exception as e:
            logger.exception(f"Error sending WhatsApp message to {phone_number}")
            raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

whatsapp_api = WhatsAppAPI()

# Template management
@router.post("/templates", response_model=Dict[str, Any])
async def create_template(
    template_data: TemplateCreate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new WhatsApp message template"""
    if current_user.plan not in ['pro', 'business']:
        raise HTTPException(status_code=403, detail="Pro or Business plan required")
    
    template = WhatsAppTemplates(
        name=template_data.name,
        content=template_data.content,
        variables=json.dumps(template_data.variables) if template_data.variables else None,
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
        "variables": json.loads(template.variables) if template.variables else [],
        "media_url": template.media_url,
        "media_type": template.media_type,
        "created_at": template.created_at
    }

@router.get("/templates", response_model=List[Dict[str, Any]])
async def get_templates(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's WhatsApp templates"""
    templates = db.query(WhatsAppTemplates).filter(
        WhatsAppTemplates.user_id == current_user.id,
        WhatsAppTemplates.is_active == True
    ).all()
    
    return [
        {
            "id": template.id,
            "name": template.name,
            "content": template.content,
            "variables": json.loads(template.variables) if template.variables else [],
            "media_url": template.media_url,
            "media_type": template.media_type,
            "created_at": template.created_at
        }
        for template in templates
    ]

# Contact management
@router.post("/contacts", response_model=Dict[str, Any])
async def create_contact(
    contact_data: Dict[str, Any],
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new WhatsApp contact"""
    if current_user.plan not in ['pro', 'business']:
        raise HTTPException(status_code=403, detail="Pro or Business plan required")
    
    contact = WhatsAppContacts(
        user_id=current_user.id,
        phone_number=contact_data['phone_number'],
        name=contact_data.get('name'),
        email=contact_data.get('email'),
        company=contact_data.get('company'),
        tags=json.dumps(contact_data.get('tags', [])),
        notes=contact_data.get('notes')
    )
    
    db.add(contact)
    db.commit()
    db.refresh(contact)
    
    return {
        "id": contact.id,
        "phone_number": contact.phone_number,
        "name": contact.name,
        "email": contact.email,
        "company": contact.company,
        "tags": json.loads(contact.tags) if contact.tags else [],
        "created_at": contact.created_at
    }

@router.get("/contacts", response_model=List[Dict[str, Any]])
async def get_contacts(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's WhatsApp contacts"""
    contacts = db.query(WhatsAppContacts).filter(
        WhatsAppContacts.user_id == current_user.id,
        WhatsAppContacts.is_active == True
    ).all()
    
    return [
        {
            "id": contact.id,
            "phone_number": contact.phone_number,
            "name": contact.name,
            "email": contact.email,
            "company": contact.company,
            "tags": json.loads(contact.tags) if contact.tags else [],
            "total_messages_sent": contact.total_messages_sent,
            "last_message_sent": contact.last_message_sent,
            "created_at": contact.created_at
        }
        for contact in contacts
    ]

# Campaign management
@router.post("/campaigns", response_model=Dict[str, Any])
async def create_campaign(
    campaign_data: CampaignCreate,
    background_tasks: BackgroundTasks,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new WhatsApp campaign"""
    if current_user.plan not in ['pro', 'business']:
        raise HTTPException(status_code=403, detail="Pro or Business plan required")
    
    campaign = WhatsAppCampaigns(
        name=campaign_data.name,
        description=campaign_data.description,
        template_id=campaign_data.template_id,
        schedule_type=campaign_data.schedule_type,
        schedule_time=campaign_data.schedule_time,
        max_messages_per_hour=campaign_data.max_messages_per_hour,
        max_messages_per_day=campaign_data.max_messages_per_day,
        user_id=current_user.id
    )
    
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    
    # If immediate campaign, start sending
    if campaign_data.schedule_type == 'immediate' and campaign_data.contact_ids:
        background_tasks.add_task(
            send_campaign_messages,
            campaign.id,
            campaign_data.contact_ids,
            current_user.id
        )
    
    return {
        "id": campaign.id,
        "name": campaign.name,
        "status": campaign.status,
        "created_at": campaign.created_at
    }

@router.get("/campaigns", response_model=List[Dict[str, Any]])
async def get_campaigns(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's WhatsApp campaigns"""
    campaigns = db.query(WhatsAppCampaigns).filter(
        WhatsAppCampaigns.user_id == current_user.id
    ).all()
    
    return [
        {
            "id": campaign.id,
            "name": campaign.name,
            "description": campaign.description,
            "status": campaign.status,
            "schedule_type": campaign.schedule_type,
            "messages_sent": campaign.messages_sent,
            "messages_failed": campaign.messages_failed,
            "created_at": campaign.created_at
        }
        for campaign in campaigns
    ]

# Message sending
@router.post("/send", response_model=Dict[str, Any])
async def send_message(
    message_data: MessageSend,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a single WhatsApp message"""
    if current_user.plan not in ['pro', 'business']:
        raise HTTPException(status_code=403, detail="Pro or Business plan required")
    
    # Create message record
    message = WhatsAppMessages(
        user_id=current_user.id,
        recipient_phone=message_data.recipient_phone,
        recipient_name=message_data.recipient_name,
        message_content=message_data.message_content,
        message_type=message_data.message_type,
        media_url=message_data.media_url,
        template_id=message_data.template_id
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Send message via WhatsApp API
    try:
        result = await whatsapp_api.send_message(
            message_data.recipient_phone,
            message_data.message_content,
            message_data.message_type,
            message_data.media_url
        )
        
        # Update message status
        message.status = 'sent'
        message.whatsapp_message_id = result['message_id']
        message.sent_at = datetime.utcnow()
        db.commit()
        
        return {
            "message_id": message.id,
            "whatsapp_message_id": result['message_id'],
            "status": "sent"
        }
        
    except Exception as e:
        message.status = 'failed'
        message.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

# Bulk message sending
@router.post("/bulk-send", response_model=Dict[str, Any])
async def bulk_send_messages(
    messages: List[MessageSend],
    background_tasks: BackgroundTasks,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send multiple WhatsApp messages"""
    if current_user.plan not in ['pro', 'business']:
        raise HTTPException(status_code=403, detail="Pro or Business plan required")
    
    # Check rate limits
    if len(messages) > 100:  # Limit bulk sends
        raise HTTPException(status_code=400, detail="Maximum 100 messages per bulk send")
    
    # Create message records
    message_records = []
    for msg_data in messages:
        message = WhatsAppMessages(
            user_id=current_user.id,
            recipient_phone=msg_data.recipient_phone,
            recipient_name=msg_data.recipient_name,
            message_content=msg_data.message_content,
            message_type=msg_data.message_type,
            media_url=msg_data.media_url,
            template_id=msg_data.template_id
        )
        message_records.append(message)
        db.add(message)
    
    db.commit()
    
    # Start background sending
    background_tasks.add_task(
        send_bulk_messages_task,
        [msg.id for msg in message_records],
        current_user.id
    )
    
    return {
        "message": f"Bulk send started for {len(messages)} messages",
        "message_ids": [msg.id for msg in message_records]
    }

# Automation
@router.post("/automations", response_model=Dict[str, Any])
async def create_automation(
    automation_data: AutomationCreate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new WhatsApp automation"""
    if current_user.plan != 'business':
        raise HTTPException(status_code=403, detail="Business plan required")
    
    automation = WhatsAppAutomations(
        name=automation_data.name,
        description=automation_data.description,
        trigger_type=automation_data.trigger_type,
        trigger_conditions=json.dumps(automation_data.trigger_conditions) if automation_data.trigger_conditions else None,
        template_id=automation_data.template_id,
        delay_minutes=automation_data.delay_minutes,
        user_id=current_user.id
    )
    
    db.add(automation)
    db.commit()
    db.refresh(automation)
    
    return {
        "id": automation.id,
        "name": automation.name,
        "trigger_type": automation.trigger_type,
        "is_active": automation.is_active,
        "created_at": automation.created_at
    }

@router.get("/automations", response_model=List[Dict[str, Any]])
async def get_automations(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's WhatsApp automations"""
    automations = db.query(WhatsAppAutomations).filter(
        WhatsAppAutomations.user_id == current_user.id
    ).all()
    
    return [
        {
            "id": automation.id,
            "name": automation.name,
            "description": automation.description,
            "trigger_type": automation.trigger_type,
            "is_active": automation.is_active,
            "created_at": automation.created_at
        }
        for automation in automations
    ]

# Background tasks
async def send_campaign_messages(campaign_id: int, contact_ids: List[int], user_id: int):
    """Background task to send campaign messages"""
    from database import SessionLocal
    db = SessionLocal()
    try:
        campaign = db.query(WhatsAppCampaigns).filter(WhatsAppCampaigns.id == campaign_id).first()
        if not campaign:
            return
        
        template = db.query(WhatsAppTemplates).filter(WhatsAppTemplates.id == campaign.template_id).first()
        if not template:
            return
        
        contacts = db.query(WhatsAppContacts).filter(
            WhatsAppContacts.id.in_(contact_ids),
            WhatsAppContacts.user_id == user_id
        ).all()
        
        for contact in contacts:
            # Replace template variables
            message_content = template.content
            if template.variables:
                variables = json.loads(template.variables)
                for var in variables:
                    if var == 'name':
                        message_content = message_content.replace('{{name}}', contact.name or 'there')
                    elif var == 'company':
                        message_content = message_content.replace('{{company}}', contact.company or '')
            
            # Create message record
            message = WhatsAppMessages(
                campaign_id=campaign_id,
                template_id=template.id,
                user_id=user_id,
                recipient_phone=contact.phone_number,
                recipient_name=contact.name,
                message_content=message_content,
                message_type='text'
            )
            db.add(message)
            
            # Send message
            try:
                result = await whatsapp_api.send_message(
                    contact.phone_number,
                    message_content
                )
                
                message.status = 'sent'
                message.whatsapp_message_id = result['message_id']
                message.sent_at = datetime.utcnow()
                
                # Update contact stats
                contact.total_messages_sent += 1
                contact.last_message_sent = datetime.utcnow()
                
                campaign.messages_sent += 1
                
            except Exception as e:
                message.status = 'failed'
                message.error_message = str(e)
                campaign.messages_failed += 1
            
            # Rate limiting
            await asyncio.sleep(1)  # 1 second delay between messages
        
        campaign.status = 'completed'
        db.commit()
        
    finally:
        db.close()

async def send_bulk_messages_task(message_ids: List[int], user_id: int):
    """Background task to send bulk messages"""
    from database import SessionLocal
    db = SessionLocal()
    try:
        messages = db.query(WhatsAppMessages).filter(
            WhatsAppMessages.id.in_(message_ids),
            WhatsAppMessages.user_id == user_id
        ).all()
        
        for message in messages:
            try:
                result = await whatsapp_api.send_message(
                    message.recipient_phone,
                    message.message_content,
                    message.message_type,
                    message.media_url
                )
                
                message.status = 'sent'
                message.whatsapp_message_id = result['message_id']
                message.sent_at = datetime.utcnow()
                
            except Exception as e:
                message.status = 'failed'
                message.error_message = str(e)
                message.retry_count += 1
            
            # Rate limiting
            await asyncio.sleep(0.5)  # 0.5 second delay between messages
        
        db.commit()
        
    finally:
        db.close()

# Trigger automation when lead is added
async def trigger_lead_automation(lead: Leads, user_id: int):
    """Trigger WhatsApp automation when a new lead is added"""
    from database import SessionLocal
    db = SessionLocal()
    try:
        automations = db.query(WhatsAppAutomations).filter(
            WhatsAppAutomations.user_id == user_id,
            WhatsAppAutomations.trigger_type == 'lead_added',
            WhatsAppAutomations.is_active == True
        ).all()
        
        for automation in automations:
            template = db.query(WhatsAppTemplates).filter(WhatsAppTemplates.id == automation.template_id).first()
            if not template:
                continue
            
            # Check if lead has phone number
            if not lead.phone:
                continue
            
            # Replace template variables
            message_content = template.content
            message_content = message_content.replace('{{name}}', lead.name)
            message_content = message_content.replace('{{company}}', lead.company or '')
            message_content = message_content.replace('{{email}}', lead.email)
            
            # Create message
            message = WhatsAppMessages(
                automation_id=automation.id,
                template_id=template.id,
                user_id=user_id,
                recipient_phone=lead.phone,
                recipient_name=lead.name,
                message_content=message_content,
                message_type='text'
            )
            db.add(message)
            
            # Send with delay if specified
            if automation.delay_minutes > 0:
                # Schedule for later
                pass
            else:
                # Send immediately
                try:
                    result = await whatsapp_api.send_message(
                        lead.phone,
                        message_content
                    )
                    
                    message.status = 'sent'
                    message.whatsapp_message_id = result['message_id']
                    message.sent_at = datetime.utcnow()
                    
                except Exception as e:
                    message.status = 'failed'
                    message.error_message = str(e)
        
        db.commit()
        
    finally:
        db.close()

# Message history
@router.get("/messages", response_model=List[Dict[str, Any]])
async def get_messages(
    status: Optional[str] = Query(None),
    campaign_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get WhatsApp message history"""
    query = db.query(WhatsAppMessages).filter(WhatsAppMessages.user_id == current_user.id)
    
    if status:
        query = query.filter(WhatsAppMessages.status == status)
    if campaign_id:
        query = query.filter(WhatsAppMessages.campaign_id == campaign_id)
    
    total = query.count()
    messages = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return [
        {
            "id": message.id,
            "recipient_phone": message.recipient_phone,
            "recipient_name": message.recipient_name,
            "message_content": message.message_content,
            "message_type": message.message_type,
            "status": message.status,
            "sent_at": message.sent_at,
            "delivered_at": message.delivered_at,
            "read_at": message.read_at,
            "error_message": message.error_message,
            "created_at": message.created_at
        }
        for message in messages
    ]

# Analytics
@router.get("/analytics", response_model=Dict[str, Any])
async def get_whatsapp_analytics(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get WhatsApp messaging analytics"""
    total_messages = db.query(WhatsAppMessages).filter(WhatsAppMessages.user_id == current_user.id).count()
    sent_messages = db.query(WhatsAppMessages).filter(
        WhatsAppMessages.user_id == current_user.id,
        WhatsAppMessages.status == 'sent'
    ).count()
    failed_messages = db.query(WhatsAppMessages).filter(
        WhatsAppMessages.user_id == current_user.id,
        WhatsAppMessages.status == 'failed'
    ).count()
    
    total_contacts = db.query(WhatsAppContacts).filter(
        WhatsAppContacts.user_id == current_user.id,
        WhatsAppContacts.is_active == True
    ).count()
    
    total_campaigns = db.query(WhatsAppCampaigns).filter(
        WhatsAppCampaigns.user_id == current_user.id
    ).count()
    
    return {
        "total_messages": total_messages,
        "sent_messages": sent_messages,
        "failed_messages": failed_messages,
        "delivery_rate": (sent_messages / total_messages * 100) if total_messages > 0 else 0,
        "total_contacts": total_contacts,
        "total_campaigns": total_campaigns
    } 