"""Push subscription model for Web Push notifications."""
from sqlalchemy import Column, String, Text, DateTime, Integer, JSON
from datetime import datetime
from typing import Optional, Dict, Any
from backend.models.database import Base


class PushSubscription(Base):
    """Push subscription model for storing user notification preferences."""
    __tablename__ = "push_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=True)  # Optional: for multi-user support
    endpoint = Column(Text, nullable=False, unique=True, index=True)
    p256dh = Column(Text, nullable=False)  # Public key
    auth = Column(Text, nullable=False)  # Auth secret
    device_info = Column(JSON, nullable=True)  # Device information (browser, OS, etc.)
    subscribed_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_notified_at = Column(DateTime, nullable=True)
    notification_preferences = Column(JSON, nullable=True)  # User preferences
    is_active = Column(String, default="true", nullable=False)  # "true" or "false"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert subscription to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "endpoint": self.endpoint,
            "p256dh": self.p256dh,
            "auth": self.auth,
            "device_info": self.device_info,
            "subscribed_at": self.subscribed_at.isoformat() if self.subscribed_at else None,
            "last_notified_at": self.last_notified_at.isoformat() if self.last_notified_at else None,
            "notification_preferences": self.notification_preferences,
            "is_active": self.is_active == "true"
        }

