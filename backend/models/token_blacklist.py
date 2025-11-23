"""Token blacklist model for logout functionality."""
from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.sql import func
from backend.models.database import Base
from datetime import datetime


class TokenBlacklist(Base):
    """Token blacklist model to track revoked tokens."""
    __tablename__ = "token_blacklist"
    
    id = Column(String, primary_key=True)  # JWT token ID (jti) or full token hash
    token_hash = Column(String, unique=True, index=True, nullable=False)  # SHA256 hash of token
    user_id = Column(String, index=True, nullable=False)
    token_type = Column(String, nullable=False)  # "access" or "refresh"
    expires_at = Column(DateTime, nullable=False, index=True)
    blacklisted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_user_token', 'user_id', 'token_type'),
        Index('idx_expires_at', 'expires_at'),  # For cleanup queries
    )

