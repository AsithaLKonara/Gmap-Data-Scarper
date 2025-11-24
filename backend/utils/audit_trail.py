"""Audit trail utility functions."""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base

# Base for audit log model (if we create a separate audit log table)
Base = declarative_base()


def set_audit_fields(
    obj: Any,
    user_id: Optional[str] = None,
    is_creation: bool = False
) -> None:
    """
    Set audit fields (created_by, modified_by, modified_at) on a model instance.
    
    Args:
        obj: SQLAlchemy model instance
        user_id: User ID performing the action
        is_creation: True if this is a new record, False if update
    """
    if is_creation:
        if hasattr(obj, 'created_by') and not obj.created_by:
            obj.created_by = user_id
        if hasattr(obj, 'created_at') and not obj.created_at:
            obj.created_at = datetime.utcnow()
    
    # Always update modified fields
    if hasattr(obj, 'modified_by'):
        obj.modified_by = user_id
    if hasattr(obj, 'modified_at'):
        obj.modified_at = datetime.utcnow()


def get_audit_info(obj: Any) -> Dict[str, Any]:
    """
    Get audit information from a model instance.
    
    Args:
        obj: SQLAlchemy model instance
        
    Returns:
        Dictionary with audit information
    """
    audit_info = {}
    
    if hasattr(obj, 'created_by'):
        audit_info['created_by'] = obj.created_by
    if hasattr(obj, 'created_at'):
        audit_info['created_at'] = obj.created_at.isoformat() if obj.created_at else None
    if hasattr(obj, 'modified_by'):
        audit_info['modified_by'] = obj.modified_by
    if hasattr(obj, 'modified_at'):
        audit_info['modified_at'] = obj.modified_at.isoformat() if obj.modified_at else None
    
    return audit_info


def track_change(
    db: Session,
    model_class: Any,
    record_id: Any,
    user_id: Optional[str],
    action: str,
    changes: Optional[Dict[str, Any]] = None
) -> None:
    """
    Track a change to a record (for future audit log table implementation).
    
    Args:
        db: Database session
        model_class: Model class
        record_id: ID of the record being changed
        user_id: User ID performing the action
        action: Action type (create, update, delete, restore)
        changes: Dictionary of field changes (optional)
    """
    # TODO: Implement audit log table and store changes
    # For now, this is a placeholder for future implementation
    import logging
    logging.info(
        f"Audit: {action} on {model_class.__name__} (id={record_id}) "
        f"by user={user_id}, changes={changes}"
    )

