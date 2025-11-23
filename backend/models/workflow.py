"""Workflow models for automation."""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, JSON, ForeignKey, Index
from datetime import datetime
from typing import Optional, Dict, Any
from backend.models.database import Base


class Workflow(Base):
    """Workflow definition model."""
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Workflow definition (JSON)
    trigger = Column(JSON, nullable=False)  # {"type": "new_lead", "conditions": {...}}
    actions = Column(JSON, nullable=False)  # [{"type": "add_to_sheet", "config": {...}}, ...]
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_executed_at = Column(DateTime, nullable=True)
    execution_count = Column(Integer, default=0)
    
    __table_args__ = (
        Index('idx_user_workflow', 'user_id', 'workflow_id'),
        Index('idx_workflow_active', 'is_active', 'is_enabled'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "trigger": self.trigger,
            "actions": self.actions,
            "is_active": self.is_active,
            "is_enabled": self.is_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_executed_at": self.last_executed_at.isoformat() if self.last_executed_at else None,
            "execution_count": self.execution_count,
        }


class WorkflowExecution(Base):
    """Workflow execution history model."""
    __tablename__ = "workflow_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String, unique=True, index=True, nullable=False)
    workflow_id = Column(String, ForeignKey('workflows.workflow_id'), index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    
    # Execution details
    trigger_data = Column(JSON, nullable=True)  # Data that triggered the workflow
    action_results = Column(JSON, nullable=True)  # Results from each action
    
    # Status
    status = Column(String, nullable=False, default="running")  # running, completed, failed
    error = Column(Text, nullable=True)
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    __table_args__ = (
        Index('idx_workflow_execution', 'workflow_id', 'started_at'),
        Index('idx_user_execution', 'user_id', 'started_at'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert execution to dictionary."""
        return {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "user_id": self.user_id,
            "trigger_data": self.trigger_data,
            "action_results": self.action_results,
            "status": self.status,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
        }

