from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field
from models import Webhook, User
from database import get_db
from auth import get_current_user
from tenant_utils import get_tenant_from_request
from datetime import datetime

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

class WebhookCreate(BaseModel):
    url: HttpUrl = Field(..., description="The URL to which webhook events will be sent.", example="https://example.com/webhook")
    event: str = Field(..., description="The event type to subscribe to.", example="lead.created")
    secret: Optional[str] = Field(None, description="Optional secret for verifying webhook payloads.", example="mysecret123")

class WebhookOut(BaseModel):
    id: int = Field(..., description="Unique identifier for the webhook.")
    url: HttpUrl = Field(..., description="The URL to which webhook events are sent.")
    event: str = Field(..., description="The event type this webhook is subscribed to.")
    is_active: bool = Field(..., description="Whether the webhook is currently active.")
    secret: Optional[str] = Field(None, description="Secret for verifying webhook payloads.")
    last_delivery_status: Optional[str] = Field(None, description="Status of the last delivery attempt.")
    last_delivery_at: Optional[datetime] = Field(None, description="Timestamp of the last delivery attempt.")
    created_at: datetime = Field(..., description="Timestamp when the webhook was created.")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when the webhook was last updated.")

    class Config:
        orm_mode = True

class DeleteResponse(BaseModel):
    status: str = Field(..., description="Status message.", example="deleted")

class WebhookUpdate(BaseModel):
    url: Optional[HttpUrl] = None
    event: Optional[str] = None
    secret: Optional[str] = None
    is_active: Optional[bool] = None

class WebhookDeliveryLog(BaseModel):
    status: str
    timestamp: datetime
    response_code: Optional[int] = None
    error: Optional[str] = None

@router.get("/", response_model=List[WebhookOut], summary="List webhooks", description="List all webhooks for the authenticated user.")
def list_webhooks(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List all webhooks for the authenticated user."""
    return db.query(Webhook).filter_by(user_id=user.id).all()

@router.post("/", response_model=WebhookOut, summary="Create webhook", description="Create a new webhook for the authenticated user.")
def create_webhook(
    data: WebhookCreate = Body(..., description="Webhook creation payload."),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register a new webhook for the authenticated user."""
    webhook = Webhook(
        user_id=user.id,
        url=str(data.url),
        event=data.event,
        secret=data.secret,
        is_active=True
    )
    db.add(webhook)
    db.commit()
    db.refresh(webhook)
    return webhook

@router.get("/{webhook_id}", response_model=WebhookOut, summary="Get webhook", description="Get a webhook by ID for the authenticated user.")
def get_webhook(
    webhook_id: int = Field(..., description="ID of the webhook to retrieve."),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve a webhook by its ID for the authenticated user."""
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id, Webhook.user_id == user.id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return webhook

@router.put("/{webhook_id}", response_model=WebhookOut, summary="Update webhook", description="Update a webhook by ID for the authenticated user.")
def update_webhook(webhook_id: int, data: WebhookUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update a webhook by ID for the authenticated user."""
    webhook = db.query(Webhook).filter_by(id=webhook_id, user_id=user.id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    if data.url is not None:
    webhook.url = str(data.url)
    if data.event is not None:
    webhook.event = data.event
    if data.secret is not None:
    webhook.secret = data.secret
    if data.is_active is not None:
        webhook.is_active = data.is_active
    db.commit()
    db.refresh(webhook)
    return webhook

@router.delete("/{webhook_id}", response_model=DeleteResponse, summary="Delete webhook", description="Delete a webhook by ID for the authenticated user.")
def delete_webhook(webhook_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a webhook by ID for the authenticated user."""
    webhook = db.query(Webhook).filter_by(id=webhook_id, user_id=user.id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    db.delete(webhook)
    db.commit()
    return DeleteResponse(status="deleted")

# Optional: Delivery log/history endpoint (basic, returns last status/time)
@router.get("/{webhook_id}/delivery-log", response_model=List[WebhookDeliveryLog], summary="Get webhook delivery log", description="Get delivery log for a webhook (last status/time only, for now).")
def get_webhook_delivery_log(webhook_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    webhook = db.query(Webhook).filter_by(id=webhook_id, user_id=user.id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    # For now, just return the last delivery status/time
    if webhook.last_delivery_status and webhook.last_delivery_at:
        return [WebhookDeliveryLog(status=webhook.last_delivery_status, timestamp=webhook.last_delivery_at)]
    return [] 