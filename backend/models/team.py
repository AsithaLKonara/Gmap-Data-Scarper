"""Team and workspace models for collaboration."""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, JSON, ForeignKey, Index, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, Dict, Any
from backend.models.database import Base


# Association table for team members
team_members = Table(
    'team_members',
    Base.metadata,
    Column('team_id', String, ForeignKey('teams.team_id'), primary_key=True),
    Column('user_id', String, ForeignKey('users.id'), primary_key=True),
    Column('role', String, nullable=False, default='member'),  # admin, member, viewer
    Column('joined_at', DateTime, default=datetime.utcnow),
    Column('permissions', JSON, nullable=True),  # Custom permissions override
    Index('idx_team_user', 'team_id', 'user_id'),
    extend_existing=True,  # Allow redefinition if module imported multiple times in test collection
)


class Team(Base):
    """Team/workspace model."""
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    
    # Team settings
    settings = Column(JSON, nullable=True)  # Team-specific settings
    plan = Column(String, nullable=True)  # Team plan (free, pro, enterprise)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    members = relationship("User", secondary=team_members, back_populates="teams")
    shared_lists = relationship("SharedLeadList", back_populates="team")
    activities = relationship("TeamActivity", back_populates="team")
    
    __table_args__ = (
        Index('idx_team_owner', 'owner_id', 'team_id'),
        Index('idx_team_active', 'is_active', 'created_at'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert team to dictionary."""
        return {
            "team_id": self.team_id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "settings": self.settings,
            "plan": self.plan,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "member_count": len(self.members) if self.members else 0,
        }


class SharedLeadList(Base):
    """Shared lead list model for team collaboration."""
    __tablename__ = "shared_lead_lists"
    
    id = Column(Integer, primary_key=True, index=True)
    list_id = Column(String, unique=True, index=True, nullable=False)
    team_id = Column(String, ForeignKey('teams.team_id'), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(String, ForeignKey('users.id'), nullable=False)
    
    # List configuration
    filters = Column(JSON, nullable=True)  # Saved filters for this list
    tags = Column(JSON, nullable=True)  # Tags for organization
    
    # Access control
    is_public = Column(Boolean, default=False)  # Public within team
    allowed_roles = Column(JSON, nullable=True)  # Roles that can access
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    lead_count = Column(Integer, default=0)
    
    # Relationships
    team = relationship("Team", back_populates="shared_lists")
    
    __table_args__ = (
        Index('idx_list_team', 'team_id', 'list_id'),
        Index('idx_list_created', 'created_by', 'created_at'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert list to dictionary."""
        return {
            "list_id": self.list_id,
            "team_id": self.team_id,
            "name": self.name,
            "description": self.description,
            "created_by": self.created_by,
            "filters": self.filters,
            "tags": self.tags,
            "is_public": self.is_public,
            "allowed_roles": self.allowed_roles,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "lead_count": self.lead_count,
        }


class TeamActivity(Base):
    """Team activity feed model."""
    __tablename__ = "team_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(String, unique=True, index=True, nullable=False)
    team_id = Column(String, ForeignKey('teams.team_id'), nullable=False, index=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    
    # Activity details
    activity_type = Column(String, nullable=False)  # lead_added, list_created, task_completed, etc.
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    # Avoid reserved attribute name 'metadata' in SQLAlchemy Declarative API
    activity_metadata = Column(JSON, nullable=True)  # Additional activity data
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    team = relationship("Team", back_populates="activities")
    
    __table_args__ = (
        Index('idx_activity_team', 'team_id', 'created_at'),
        Index('idx_activity_user', 'user_id', 'created_at'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert activity to dictionary."""
        return {
            "activity_id": self.activity_id,
            "team_id": self.team_id,
            "user_id": self.user_id,
            "activity_type": self.activity_type,
            "title": self.title,
            "description": self.description,
            "metadata": self.activity_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

