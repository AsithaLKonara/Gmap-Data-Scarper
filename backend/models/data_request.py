"""Data request tracking model for GDPR compliance."""
from sqlalchemy import Column, String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from backend.models.database import Base
from datetime import datetime
import enum


class RequestType(enum.Enum):
    """Type of data request."""
    ACCESS = "access"
    DELETION = "deletion"


class RequestStatus(enum.Enum):
    """Status of data request."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DataRequest(Base):
    """Data request tracking model for GDPR compliance."""
    __tablename__ = "data_requests"
    
    id = Column(String, primary_key=True)  # Request ID (e.g., dar_1234567890)
    request_type = Column(SQLEnum(RequestType), nullable=False, index=True)
    status = Column(SQLEnum(RequestStatus), default=RequestStatus.PENDING, nullable=False, index=True)
    email = Column(String, nullable=True, index=True)
    profile_url = Column(String, nullable=True)
    user_id = Column(String, nullable=True, index=True)  # If user is authenticated
    request_data = Column(Text, nullable=True)  # JSON string of request details
    response_data = Column(Text, nullable=True)  # JSON string of response/export
    estimated_completion = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)  # Internal notes about processing

