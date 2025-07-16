from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Request, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from models import User, Notification
from database import get_db
from auth import get_current_user
import logging
import json
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import aiohttp
from tenant_utils import get_tenant_record_or_403
from fastapi import Request
from tenant_utils import get_tenant_from_request
from realtime import broadcast_notification
import os

logger = logging.getLogger("notifications")

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

class NotificationType(str, Enum):
    JOB_COMPLETED = "job_completed"
    JOB_FAILED = "job_failed"
    LEAD_ADDED = "lead_added"
    PLAN_UPGRADE = "plan_upgrade"
    SYSTEM_ALERT = "system_alert"
    DAILY_REPORT = "daily_report"

class NotificationChannel(str, Enum):
    EMAIL = "email"
    WEBHOOK = "webhook"
    WEBSOCKET = "websocket"
    SMS = "sms"

class NotificationTemplate(BaseModel):
    id: str
    name: str
    type: NotificationType
    subject: str
    body: str
    variables: List[str]
    enabled: bool = True

class NotificationRequest(BaseModel):
    type: NotificationType
    user_id: int
    data: Dict[str, Any]
    channels: List[NotificationChannel] = [NotificationChannel.EMAIL]
    priority: str = "normal"

class NotificationResponse(BaseModel):
    id: str
    type: NotificationType
    user_id: int
    data: Dict[str, Any]
    channels: List[NotificationChannel]
    status: str  # pending, sent, failed
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# In-memory notification storage (in production, use database)
notifications: Dict[str, NotificationResponse] = {}
notification_templates: Dict[str, NotificationTemplate] = {}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected for user {user_id}")

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected for user {user_id}")

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except:
                    await self.disconnect(connection, user_id)

    async def broadcast_to_user(self, user_id: int, notification: NotificationResponse):
        message = json.dumps({
            "type": "notification",
            "data": notification.dict()
        })
        await self.send_personal_message(message, user_id)

manager = ConnectionManager()

class NotificationService:
    def __init__(self):
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': os.getenv('EMAIL_USERNAME', ''),
            'password': os.getenv('EMAIL_PASSWORD', ''),
            'from_email': os.getenv('FROM_EMAIL', 'noreply@leadtap.com')
        }
        self.webhook_config = {}
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize default notification templates"""
        templates = [
            NotificationTemplate(
                id="job_completed",
                name="Job Completed",
                type=NotificationType.JOB_COMPLETED,
                subject="Your job has been completed successfully",
                body="Hello {user_name},\n\nYour job #{job_id} has been completed successfully. You can download the results from your dashboard.\n\nBest regards,\nLeadTap Team",
                variables=["user_name", "job_id"]
            ),
            NotificationTemplate(
                id="job_failed",
                name="Job Failed",
                type=NotificationType.JOB_FAILED,
                subject="Your job has failed",
                body="Hello {user_name},\n\nYour job #{job_id} has failed. Please check the job details for more information.\n\nBest regards,\nLeadTap Team",
                variables=["user_name", "job_id"]
            ),
            NotificationTemplate(
                id="lead_added",
                name="New Lead Added",
                type=NotificationType.LEAD_ADDED,
                subject="New lead added to your CRM",
                body="Hello {user_name},\n\nA new lead '{lead_name}' has been added to your CRM.\n\nBest regards,\nLeadTap Team",
                variables=["user_name", "lead_name"]
            ),
            NotificationTemplate(
                id="plan_upgrade",
                name="Plan Upgraded",
                type=NotificationType.PLAN_UPGRADE,
                subject="Your plan has been upgraded",
                body="Hello {user_name},\n\nYour plan has been successfully upgraded to {new_plan}.\n\nBest regards,\nLeadTap Team",
                variables=["user_name", "new_plan"]
            ),
            NotificationTemplate(
                id="daily_report",
                name="Daily Report",
                type=NotificationType.DAILY_REPORT,
                subject="Your daily report",
                body="Hello {user_name},\n\nHere's your daily report:\n- Jobs completed: {jobs_completed}\n- New leads: {new_leads}\n- Conversion rate: {conversion_rate}%\n\nBest regards,\nLeadTap Team",
                variables=["user_name", "jobs_completed", "new_leads", "conversion_rate"]
            )
        ]
        
        for template in templates:
            notification_templates[template.id] = template
    
    async def send_notification(self, notification: NotificationRequest) -> NotificationResponse:
        """Send notification through all specified channels"""
        notification_id = f"notif_{notification.user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        notification_response = NotificationResponse(
            id=notification_id,
            type=notification.type,
            user_id=notification.user_id,
            data=notification.data,
            channels=notification.channels,
            status="pending",
            sent_at=None,
            error_message=None,
            created_at=datetime.utcnow()
        )
        
        notifications[notification_id] = notification_response
        
        try:
            # Get user information
            db = next(get_db())
            user = db.query(User).filter(User.id == notification.user_id).first()
            if not user:
                raise ValueError("User not found")
            
            # Get template
            template = notification_templates.get(notification.type.value)
            if not template:
                raise ValueError(f"No template found for notification type: {notification.type}")
            
            # Send through each channel
            for channel in notification.channels:
                try:
                    if channel == NotificationChannel.EMAIL:
                        await self._send_email(user, template, notification.data)
                    elif channel == NotificationChannel.WEBHOOK:
                        await self._send_webhook(user, template, notification.data)
                    elif channel == NotificationChannel.WEBSOCKET:
                        await manager.broadcast_to_user(notification.user_id, notification_response)
                    elif channel == NotificationChannel.SMS:
                        await self._send_sms(user, template, notification.data)
                    
                    notification_response.status = "sent"
                    notification_response.sent_at = datetime.utcnow()
                    
                except Exception as e:
                    logger.exception(f"Error sending notification via {channel}")
                    notification_response.status = "failed"
                    notification_response.error_message = str(e)
            
            logger.info(f"Notification sent: {notification_id}")
            return notification_response
            
        except Exception as e:
            logger.exception(f"Error sending notification {notification_id}")
            notification_response.status = "failed"
            notification_response.error_message = str(e)
            return notification_response
    
    async def _send_email(self, user: User, template: NotificationTemplate, data: Dict[str, Any]):
        """Send email notification"""
        try:
            # Prepare email content
            subject = self._replace_variables(template.subject, data)
            body = self._replace_variables(template.body, data)
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = user.email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['username'], self.email_config['password'])
                server.send_message(msg)
            
            logger.info(f"Email sent to {user.email}")
            
        except Exception as e:
            logger.exception("Error sending email")
            raise
    
    async def _send_webhook(self, user: User, template: NotificationTemplate, data: Dict[str, Any]):
        """Send webhook notification"""
        try:
            webhook_url = self.webhook_config.get(str(user.id))
            if not webhook_url:
                logger.warning(f"No webhook URL configured for user {user.id}")
                return
            
            payload = {
                "user_id": user.id,
                "user_email": user.email,
                "notification_type": template.type.value,
                "subject": self._replace_variables(template.subject, data),
                "body": self._replace_variables(template.body, data),
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status != 200:
                        raise Exception(f"Webhook failed with status {response.status}")
            
            logger.info(f"Webhook sent to {webhook_url}")
            
        except Exception as e:
            logger.exception("Error sending webhook")
            raise
    
    async def _send_sms(self, user: User, template: NotificationTemplate, data: Dict[str, Any]):
        """Send SMS notification (placeholder)"""
        try:
            # SMS implementation would go here
            # For now, just log the attempt
            logger.info(f"SMS notification would be sent to user {user.id}")
            
        except Exception as e:
            logger.exception("Error sending SMS")
            raise
    
    def _replace_variables(self, text: str, data: Dict[str, Any]) -> str:
        """Replace variables in template text"""
        for key, value in data.items():
            placeholder = f"{{{key}}}"
            if placeholder in text:
                text = text.replace(placeholder, str(value))
        return text

# Initialize notification service
notification_service = NotificationService()

# --- Pydantic Models for OpenAPI ---
class NotificationTemplate(BaseModel):
    id: str
    name: str
    type: NotificationType
    subject: str
    body: str
    variables: List[str]
    enabled: bool = True

class NotificationRequest(BaseModel):
    type: NotificationType
    user_id: int
    data: Dict[str, Any]
    channels: List[NotificationChannel] = [NotificationChannel.EMAIL]
    priority: str = "normal"

class NotificationResponse(BaseModel):
    id: str
    type: NotificationType
    user_id: int
    data: Dict[str, Any]
    channels: List[NotificationChannel]
    status: str  # pending, sent, failed
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True

class NotificationOut(BaseModel):
    id: int
    type: str
    message: str
    read: bool
    created_at: str
    class Config:
        orm_mode = True

class NotificationIn(BaseModel):
    type: str
    message: str

class MarkReadResponse(BaseModel):
    message: str
    notif_id: int

class WebhookUrlResponse(BaseModel):
    url: str

class WebhookTestResponse(BaseModel):
    message: str
    status: str

# --- Endpoints with OpenAPI docs ---

@router.post("/send", response_model=NotificationResponse, summary="Send notification", description="Send a notification to a user through specified channels.")
async def send_notification(
    notification: NotificationRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Send a notification to a user through specified channels."""
    try:
        # Validate that user can send notification to themselves or is admin
        if notification.user_id != user.id and not user.is_admin:
            raise HTTPException(status_code=403, detail="Not authorized to send notifications to other users")
        
        result = await notification_service.send_notification(notification)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error sending notification")
        raise HTTPException(status_code=500, detail="Failed to send notification")

@router.get("/templates", response_model=List[NotificationTemplate], summary="List notification templates", description="Get all available notification templates.")
def get_notification_templates(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get all available notification templates."""
    try:
        return list(notification_templates.values())
    except Exception as e:
        logger.exception("Error getting notification templates")
        raise HTTPException(status_code=500, detail="Failed to get notification templates")

@router.get("/history", response_model=List[NotificationResponse], summary="Get notification history", description="Get notification history for the current user.")
def get_notification_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get notification history for the current user."""
    try:
        # Get user's notification history
        user_notifications = [
            notif for notif in notifications.values()
            if notif.user_id == user.id
        ]
        
        # Sort by creation date and limit
        sorted_notifications = sorted(
            user_notifications,
            key=lambda x: x.created_at,
            reverse=True
        )[:limit]
        
        return sorted_notifications
        
    except Exception as e:
        logger.exception("Error getting notification history")
        raise HTTPException(status_code=500, detail="Failed to get notification history")

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back for testing
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

# Utility function to send notifications from other parts of the application
async def send_job_completed_notification(user_id: int, job_id: int, job_data: Dict[str, Any]):
    """Send job completed notification"""
    notification = NotificationRequest(
        type=NotificationType.JOB_COMPLETED,
        user_id=user_id,
        data={
            "user_name": "User",  # Would get from user object
            "job_id": job_id,
            **job_data
        },
        channels=[NotificationChannel.EMAIL, NotificationChannel.WEBSOCKET]
    )
    await notification_service.send_notification(notification)

async def send_job_failed_notification(user_id: int, job_id: int, error_message: str):
    """Send job failed notification"""
    notification = NotificationRequest(
        type=NotificationType.JOB_FAILED,
        user_id=user_id,
        data={
            "user_name": "User",  # Would get from user object
            "job_id": job_id,
            "error_message": error_message
        },
        channels=[NotificationChannel.EMAIL, NotificationChannel.WEBSOCKET]
    )
    await notification_service.send_notification(notification)

async def send_daily_report_notification(user_id: int, report_data: Dict[str, Any]):
    """Send daily report notification"""
    notification = NotificationRequest(
        type=NotificationType.DAILY_REPORT,
        user_id=user_id,
        data={
            "user_name": "User",  # Would get from user object
            **report_data
        },
        channels=[NotificationChannel.EMAIL]
    )
    await notification_service.send_notification(notification)

@router.get("/", response_model=List[NotificationOut], summary="List notifications", description="List all notifications for the current user.")
def list_notifications(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """List all notifications for the current user."""
    return db.query(Notification).filter(Notification.user_id == user.id).order_by(Notification.created_at.desc()).all()

@router.get("/notifications/{notif_id}", response_model=NotificationOut, summary="Get notification", description="Get a specific notification by ID.")
def get_notification(notif_id: int = Field(..., description="ID of the notification."), request: Request = None, db: Session = Depends(get_db)):
    """Get a specific notification by ID."""
    tenant = get_tenant_from_request(request, db)
    notif = get_tenant_record_or_403(Notification, notif_id, tenant.id, db)
    return notif

@router.post("/{notif_id}/read", response_model=MarkReadResponse, summary="Mark notification as read", description="Mark a notification as read by ID.")
def mark_notification_read(notif_id: int = Field(..., description="ID of the notification."), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Mark a notification as read by ID."""
    notif = db.query(Notification).filter(Notification.id == notif_id, Notification.user_id == user.id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.read = True
    db.commit()
    return {"message": "Notification marked as read", "notif_id": notif_id}

@router.post("/", response_model=NotificationOut, summary="Create notification", description="Create a new notification for the current user.")
def create_notification(data: NotificationIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Create a new notification for the current user."""
    notif = Notification(user_id=user.id, type=data.type, message=data.message)
    db.add(notif)
    db.commit()
    db.refresh(notif)
    # Broadcast in real time
    import asyncio
    asyncio.create_task(broadcast_notification(user.id, {
        "id": notif.id,
        "type": notif.type,
        "message": notif.message,
        "read": notif.read,
        "created_at": notif.created_at.isoformat()
    }))
    return notif

@router.get("/webhook", response_model=WebhookUrlResponse, summary="Get webhook URL", description="Get the webhook URL for the current user.")
def get_webhook_url(user: User = Depends(get_current_user)):
    """Get the webhook URL for the current user."""
    return {"url": user.webhook_url}

@router.post("/webhook", response_model=WebhookUrlResponse, summary="Set webhook URL", description="Set the webhook URL for the current user.")
def set_webhook_url(data: dict = Body(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Set the webhook URL for the current user."""
    url = data.get("webhook_url")
    if not url or not url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid webhook URL")
    user.webhook_url = url
    db.commit()
    return {"url": url}

@router.delete("/webhook", response_model=WebhookUrlResponse, summary="Delete webhook URL", description="Delete the webhook URL for the current user.")
def delete_webhook_url(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Delete the webhook URL for the current user."""
    user.webhook_url = None
    db.commit()
    return {"url": None}

@router.post("/webhook/test", response_model=WebhookTestResponse, summary="Test webhook", description="Send a test notification to the user's webhook URL.")
def test_webhook(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Send a test notification to the user's webhook URL."""
    if not user.webhook_url:
        raise HTTPException(status_code=400, detail="No webhook URL set")
    payload = {
        "test": True,
        "message": "This is a test webhook from LeadTap.",
        "timestamp": datetime.utcnow().isoformat()
    }
    try:
        resp = requests.post(user.webhook_url, json=payload, timeout=5)
        return {"message": "Webhook test sent", "status": "sent", "response_code": resp.status_code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook test failed: {e}") 