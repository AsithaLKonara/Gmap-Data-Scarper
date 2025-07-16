from fastapi import APIRouter, Depends, HTTPException, Body
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

@router.get("/", response_model=List[WebhookOut], summary="List webhooks", description="List all webhooks for the authenticated user.")
def list_webhooks(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get a list of all webhooks registered by the authenticated user."""
    return db.query(Webhook).filter(Webhook.user_id == user.id).all()

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
def update_webhook(
    webhook_id: int = Field(..., description="ID of the webhook to update."),
    data: WebhookCreate = Body(..., description="Webhook update payload."),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing webhook by its ID for the authenticated user."""
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id, Webhook.user_id == user.id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    webhook.url = str(data.url)
    webhook.event = data.event
    webhook.secret = data.secret
    db.commit()
    db.refresh(webhook)
    return webhook

@router.delete("/{webhook_id}", response_model=DeleteResponse, summary="Delete webhook", description="Delete a webhook by ID for the authenticated user.")
def delete_webhook(
    webhook_id: int = Field(..., description="ID of the webhook to delete."),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a webhook by its ID for the authenticated user."""
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id, Webhook.user_id == user.id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    db.delete(webhook)
    db.commit()
    return {"status": "deleted"} 