"""Scheduled report models."""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, JSON, ForeignKey, Index
from datetime import datetime
from typing import Dict, Any
from backend.models.database import Base


class ScheduledReport(Base):
    """Scheduled report model."""
    __tablename__ = "scheduled_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    team_id = Column(String, ForeignKey('teams.team_id'), nullable=True, index=True)
    
    # Report configuration
    name = Column(String, nullable=False)
    report_config = Column(JSON, nullable=False)  # Report builder config
    schedule = Column(JSON, nullable=False)  # {"frequency": "daily|weekly|monthly", "day": 1, "time": "09:00"}
    
    # Delivery settings
    delivery_method = Column(String, nullable=False, default="email")  # email, webhook, s3
    delivery_config = Column(JSON, nullable=True)  # Email addresses, webhook URL, etc.
    format = Column(String, nullable=False, default="json")  # json, csv, pdf
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True, index=True)
    run_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_report_user', 'user_id', 'is_active'),
        Index('idx_report_next_run', 'next_run_at', 'is_active'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "report_id": self.report_id,
            "user_id": self.user_id,
            "team_id": self.team_id,
            "name": self.name,
            "report_config": self.report_config,
            "schedule": self.schedule,
            "delivery_method": self.delivery_method,
            "delivery_config": self.delivery_config,
            "format": self.format,
            "is_active": self.is_active,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "next_run_at": self.next_run_at.isoformat() if self.next_run_at else None,
            "run_count": self.run_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

