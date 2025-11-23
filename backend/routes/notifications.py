"""Push notification endpoints."""
from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any, Optional
from backend.services.push_service import get_push_service
from backend.middleware.auth import get_optional_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


class PushSubscriptionRequest(BaseModel):
    """Push subscription request model."""
    subscription: Dict[str, Any]
    device_info: Optional[Dict[str, Any]] = None


class PushNotificationRequest(BaseModel):
    """Push notification request model."""
    title: str
    body: str
    icon: Optional[str] = None
    badge: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    tag: Optional[str] = None
    require_interaction: bool = False


@router.post("/subscribe")
async def subscribe(
    request: PushSubscriptionRequest,
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    Subscribe to push notifications.
    
    Args:
        request: Push subscription request
        current_user: Optional authenticated user
        
    Returns:
        Subscription confirmation
    """
    try:
        push_service = get_push_service()
        user_id = current_user.get("user_id") if current_user else None
        
        subscription = push_service.subscribe(
            subscription_data=request.subscription,
            user_id=user_id,
            device_info=request.device_info
        )
        
        if subscription:
            return {
                "status": "success",
                "message": "Subscribed to push notifications",
                "subscription_id": subscription.id
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to subscribe")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/unsubscribe")
async def unsubscribe(
    endpoint: str = Body(..., embed=True),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    Unsubscribe from push notifications.
    
    Args:
        endpoint: Subscription endpoint
        current_user: Optional authenticated user
        
    Returns:
        Unsubscription confirmation
    """
    try:
        push_service = get_push_service()
        success = push_service.unsubscribe(endpoint)
        
        if success:
            return {
                "status": "success",
                "message": "Unsubscribed from push notifications"
            }
        else:
            raise HTTPException(status_code=404, detail="Subscription not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send")
async def send_notification(
    request: PushNotificationRequest,
    user_id: Optional[str] = Body(None, embed=True),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    Send a push notification.
    
    Args:
        request: Push notification request
        user_id: Optional user ID (for admin use)
        current_user: Optional authenticated user
        
    Returns:
        Notification send confirmation
    """
    try:
        push_service = get_push_service()
        
        # For admin use, allow sending to specific user
        if user_id:
            sent_count = push_service.send_to_user(
                user_id=user_id,
                title=request.title,
                body=request.body,
                icon=request.icon,
                data=request.data
            )
        else:
            # Send to all active subscriptions
            sent_count = push_service.send_to_all(
                title=request.title,
                body=request.body,
                icon=request.icon,
                data=request.data
            )
        
        return {
            "status": "success",
            "message": f"Notification sent to {sent_count} subscribers",
            "sent_count": sent_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subscriptions")
async def get_subscriptions(
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    Get all subscriptions for the current user.
    
    Args:
        current_user: Optional authenticated user
        
    Returns:
        List of subscriptions
    """
    try:
        push_service = get_push_service()
        user_id = current_user.get("user_id") if current_user else None
        
        subscriptions = push_service.get_subscriptions(user_id=user_id)
        
        return {
            "status": "success",
            "subscriptions": [sub.to_dict() for sub in subscriptions]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/preferences")
async def update_preferences(
    endpoint: str = Body(..., embed=True),
    preferences: Dict[str, Any] = Body(..., embed=True),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    Update notification preferences.
    
    Args:
        endpoint: Subscription endpoint
        preferences: Notification preferences
        current_user: Optional authenticated user
        
    Returns:
        Preferences update confirmation
    """
    try:
        push_service = get_push_service()
        success = push_service.update_preferences(endpoint, preferences)
        
        if success:
            return {
                "status": "success",
                "message": "Preferences updated"
            }
        else:
            raise HTTPException(status_code=404, detail="Subscription not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

