"""Audit log model for tracking changes to records."""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from datetime import datetime
from backend.models.database import Base


class AuditLog(Base):
    """Audit log entry for tracking changes to records."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String, nullable=False, index=True)
    record_id = Column(String, nullable=False, index=True)
    action = Column(String, nullable=False)  # "create", "update", "delete", "restore"
    user_id = Column(String, nullable=True, index=True)
    changes = Column(JSON, nullable=True)  # JSON object with field: {old: value, new: value}
    metadata_json = Column(JSON, nullable=True)  # Additional metadata (renamed from 'metadata' to avoid SQLAlchemy conflict)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, table={self.table_name}, record_id={self.record_id}, action={self.action})>"

