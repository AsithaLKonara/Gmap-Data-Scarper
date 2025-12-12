"""Audit trail utility functions."""
from datetime import datetime, timezone
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
            obj.created_at = datetime.now(timezone.utc)
    
    # Always update modified fields
    if hasattr(obj, 'modified_by'):
        obj.modified_by = user_id
    if hasattr(obj, 'modified_at'):
        obj.modified_at = datetime.now(timezone.utc)


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
    table_name: str,
    record_id: str,
    action: str,
    user_id: Optional[str] = None,
    changes: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> None:
    """
    Track a change to a record.
    
    Args:
        table_name: Name of the table
        record_id: ID of the record
        action: Action performed (create, update, delete, restore)
        user_id: User who made the change
        changes: Dictionary of field changes {field: {old: value, new: value}}
        metadata: Additional metadata
        ip_address: IP address of the user
        user_agent: User agent string
    """
    try:
        from backend.models.database import get_session
        from backend.models.audit_log import AuditLog
        
        db = get_session()
        try:
            audit_log = AuditLog(
                table_name=table_name,
                record_id=str(record_id),
                action=action,
                user_id=user_id,
                changes=changes,
                metadata_json=metadata,  # Use metadata_json to avoid SQLAlchemy conflict
                ip_address=ip_address,
                user_agent=user_agent,
                created_at=datetime.now(timezone.utc)
            )
            db.add(audit_log)
            db.commit()
        except Exception as e:
            db.rollback()
            import logging
            logging.error(f"Failed to create audit log entry: {e}", exc_info=True)
        finally:
            db.close()
    except Exception as e:
        import logging
        logging.error(f"Error creating audit log: {e}", exc_info=True)

