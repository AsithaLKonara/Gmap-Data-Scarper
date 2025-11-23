"""Lead usage tracking model for daily limits."""
from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, Index, UniqueConstraint
from datetime import datetime, date
from typing import Optional, Dict, Any
from backend.models.database import Base


class LeadUsage(Base):
    """Lead usage tracking model for daily limits."""
    __tablename__ = "lead_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    usage_date = Column(Date, nullable=False, index=True)  # Date for daily tracking
    leads_count = Column(Integer, default=0, nullable=False)
    reset_at = Column(DateTime, nullable=True)  # Timestamp for next reset
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'usage_date', name='uq_user_date'),
        Index('idx_user_date', 'user_id', 'usage_date'),
        Index('idx_usage_date', 'usage_date'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert usage to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "usage_date": self.usage_date.isoformat() if self.usage_date else None,
            "leads_count": self.leads_count,
            "reset_at": self.reset_at.isoformat() if self.reset_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

