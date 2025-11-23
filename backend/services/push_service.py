"""Web Push notification service using pywebpush."""
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import json
import base64
from sqlalchemy.orm import Session
from backend.models.database import get_session
from backend.models.push_subscription import PushSubscription

try:
    from pywebpush import webpush, WebPushException
    PYWEBPUSH_AVAILABLE = True
except ImportError:
    PYWEBPUSH_AVAILABLE = False
    print("Warning: pywebpush not available. Install with: pip install pywebpush")


class PushService:
    """Service for sending Web Push notifications."""
    
    def __init__(self):
        """Initialize push service."""
        if not PYWEBPUSH_AVAILABLE:
            raise ImportError("pywebpush is required for push notifications. Install with: pip install pywebpush")
        
        # VAPID keys (should be in environment variables)
        self.vapid_private_key = os.getenv("VAPID_PRIVATE_KEY", "")
        self.vapid_public_key = os.getenv("VAPID_PUBLIC_KEY", "")
        self.vapid_email = os.getenv("VAPID_EMAIL", "admin@leadintelligence.com")
        
        if not self.vapid_private_key or not self.vapid_public_key:
            print("Warning: VAPID keys not configured. Push notifications will not work.")
    
    def subscribe(
        self,
        subscription_data: Dict[str, Any],
        user_id: Optional[str] = None,
        device_info: Optional[Dict[str, Any]] = None,
        db_session: Optional[Session] = None
    ) -> PushSubscription:
        """
        Subscribe a user to push notifications.
        
        Args:
            subscription_data: Web Push subscription data (endpoint, keys)
            user_id: Optional user ID
            device_info: Optional device information
            db_session: Optional database session (for testing)
            
        Returns:
            PushSubscription object
        """
        db = db_session if db_session else get_session()
        should_close = db_session is None
        try:
            # Check if subscription already exists
            existing = db.query(PushSubscription).filter(
                PushSubscription.endpoint == subscription_data["endpoint"]
            ).first()
            
            if existing:
                # Update existing subscription
                existing.p256dh = subscription_data["keys"]["p256dh"]
                existing.auth = subscription_data["keys"]["auth"]
                existing.user_id = user_id
                existing.device_info = device_info
                existing.is_active = "true"
                db.commit()
                return existing
            
            # Create new subscription
            subscription = PushSubscription(
                user_id=user_id,
                endpoint=subscription_data["endpoint"],
                p256dh=subscription_data["keys"]["p256dh"],
                auth=subscription_data["keys"]["auth"],
                device_info=device_info,
                notification_preferences={
                    "task_completion": True,
                    "task_errors": True,
                    "task_paused": False,
                    "task_resumed": False
                }
            )
            db.add(subscription)
            db.commit()
            db.refresh(subscription)
            return subscription
        finally:
            if should_close:
                db.close()
    
    def unsubscribe(self, endpoint: str) -> bool:
        """
        Unsubscribe a user from push notifications.
        
        Args:
            endpoint: Subscription endpoint
            
        Returns:
            True if unsubscribed successfully
        """
        db = get_session()
        try:
            subscription = db.query(PushSubscription).filter(
                PushSubscription.endpoint == endpoint
            ).first()
            
            if subscription:
                subscription.is_active = "false"
                db.commit()
                return True
            return False
        finally:
            db.close()
    
    def send_notification(
        self,
        subscription: PushSubscription,
        title: str,
        body: str,
        icon: Optional[str] = None,
        badge: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        tag: Optional[str] = None,
        require_interaction: bool = False
    ) -> bool:
        """
        Send a push notification to a subscription.
        
        Args:
            subscription: PushSubscription object
            title: Notification title
            body: Notification body
            icon: Optional icon URL
            badge: Optional badge URL
            data: Optional data payload
            tag: Optional notification tag
            require_interaction: Whether notification requires user interaction
            
        Returns:
            True if notification sent successfully
        """
        if not PYWEBPUSH_AVAILABLE:
            return False
        
        if subscription.is_active != "true":
            return False
        
        try:
            # Prepare subscription info
            subscription_info = {
                "endpoint": subscription.endpoint,
                "keys": {
                    "p256dh": subscription.p256dh,
                    "auth": subscription.auth
                }
            }
            
            # Prepare notification payload
            payload = {
                "title": title,
                "body": body,
                "icon": icon or "/icon-192.png",
                "badge": badge or "/icon-192.png",
                "tag": tag,
                "requireInteraction": require_interaction,
                "data": data or {}
            }
            
            # Send notification
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=self.vapid_private_key,
                vapid_claims={
                    "sub": f"mailto:{self.vapid_email}"
                }
            )
            
            # Update last notified timestamp
            db = get_session()
            try:
                subscription.last_notified_at = datetime.utcnow()
                db.commit()
            finally:
                db.close()
            
            return True
        except WebPushException as e:
            print(f"WebPush error: {e}")
            # If subscription is invalid, mark as inactive
            if e.response and e.response.status_code == 410:
                db = get_session()
                try:
                    subscription.is_active = "false"
                    db.commit()
                finally:
                    db.close()
            return False
        except Exception as e:
            print(f"Error sending push notification: {e}")
            return False
    
    def send_to_user(
        self,
        user_id: str,
        title: str,
        body: str,
        icon: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Send notification to all active subscriptions for a user.
        
        Args:
            user_id: User ID
            title: Notification title
            body: Notification body
            icon: Optional icon URL
            data: Optional data payload
            
        Returns:
            Number of notifications sent
        """
        db = get_session()
        try:
            subscriptions = db.query(PushSubscription).filter(
                PushSubscription.user_id == user_id,
                PushSubscription.is_active == "true"
            ).all()
            
            sent_count = 0
            for subscription in subscriptions:
                if self.send_notification(subscription, title, body, icon=icon, data=data):
                    sent_count += 1
            
            return sent_count
        finally:
            db.close()
    
    def send_to_all(
        self,
        title: str,
        body: str,
        icon: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Send notification to all active subscriptions.
        
        Args:
            title: Notification title
            body: Notification body
            icon: Optional icon URL
            data: Optional data payload
            
        Returns:
            Number of notifications sent
        """
        db = get_session()
        try:
            subscriptions = db.query(PushSubscription).filter(
                PushSubscription.is_active == "true"
            ).all()
            
            sent_count = 0
            for subscription in subscriptions:
                if self.send_notification(subscription, title, body, icon=icon, data=data):
                    sent_count += 1
            
            return sent_count
        finally:
            db.close()
    
    def update_preferences(
        self,
        endpoint: str,
        preferences: Dict[str, Any]
    ) -> bool:
        """
        Update notification preferences for a subscription.
        
        Args:
            endpoint: Subscription endpoint
            preferences: Notification preferences dictionary
            
        Returns:
            True if updated successfully
        """
        db = get_session()
        try:
            subscription = db.query(PushSubscription).filter(
                PushSubscription.endpoint == endpoint
            ).first()
            
            if subscription:
                subscription.notification_preferences = preferences
                db.commit()
                return True
            return False
        finally:
            db.close()
    
    def get_subscriptions(
        self,
        user_id: Optional[str] = None
    ) -> List[PushSubscription]:
        """
        Get all subscriptions for a user or all subscriptions.
        
        Args:
            user_id: Optional user ID
            
        Returns:
            List of PushSubscription objects
        """
        db = get_session()
        try:
            query = db.query(PushSubscription)
            if user_id:
                query = query.filter(PushSubscription.user_id == user_id)
            return query.all()
        finally:
            db.close()


# Global instance
_push_service: Optional[PushService] = None


def get_push_service() -> PushService:
    """Get or create global push service instance."""
    global _push_service
    if _push_service is None:
        try:
            _push_service = PushService()
        except ImportError:
            # Return a mock service if pywebpush is not available
            class MockPushService:
                def subscribe(self, *args, **kwargs):
                    return None
                def unsubscribe(self, *args, **kwargs):
                    return False
                def send_notification(self, *args, **kwargs):
                    return False
                def send_to_user(self, *args, **kwargs):
                    return 0
                def send_to_all(self, *args, **kwargs):
                    return 0
                def update_preferences(self, *args, **kwargs):
                    return False
                def get_subscriptions(self, *args, **kwargs):
                    return []
            _push_service = MockPushService()
    return _push_service

