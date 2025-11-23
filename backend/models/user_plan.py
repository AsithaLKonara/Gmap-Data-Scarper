"""User plan model for subscription management."""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Index
from datetime import datetime
from typing import Optional, Dict, Any
from backend.models.database import Base


class UserPlan(Base):
    """User plan model for managing subscriptions."""
    __tablename__ = "user_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    plan_type = Column(String, nullable=False, index=True)  # 'free', 'paid_monthly', 'paid_usage'
    daily_lead_limit = Column(Integer, nullable=True)  # 10 for free, null for paid
    monthly_price = Column(Float, nullable=True)  # For fixed monthly plans
    price_per_lead = Column(Float, nullable=True)  # For usage-based plans
    stripe_subscription_id = Column(String, nullable=True, index=True)
    stripe_customer_id = Column(String, nullable=True, index=True)
    status = Column(String, default='active', nullable=False)  # 'active', 'cancelled', 'expired', 'trial'
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cancelled_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_user_plan_status', 'user_id', 'status'),
        Index('idx_plan_type_status', 'plan_type', 'status'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert plan to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "plan_type": self.plan_type,
            "daily_lead_limit": self.daily_lead_limit,
            "monthly_price": self.monthly_price,
            "price_per_lead": self.price_per_lead,
            "stripe_subscription_id": self.stripe_subscription_id,
            "stripe_customer_id": self.stripe_customer_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
        }

