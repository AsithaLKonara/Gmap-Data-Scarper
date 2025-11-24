"""Soft delete utility functions."""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from backend.models.database import Lead, Task


def soft_delete_lead(
    db: Session,
    lead_id: int,
    deleted_by: Optional[str] = None
) -> bool:
    """
    Soft delete a lead by setting deleted_at timestamp.
    
    Args:
        db: Database session
        lead_id: ID of the lead to delete
        deleted_by: User ID who performed the deletion
        
    Returns:
        True if lead was found and soft deleted, False otherwise
    """
    lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.deleted_at.is_(None)  # Only delete if not already deleted
    ).first()
    
    if not lead:
        return False
    
    lead.deleted_at = datetime.utcnow()
    lead.modified_at = datetime.utcnow()
    if deleted_by:
        lead.modified_by = deleted_by
    
    db.commit()
    return True


def restore_lead(
    db: Session,
    lead_id: int,
    restored_by: Optional[str] = None
) -> bool:
    """
    Restore a soft-deleted lead by clearing deleted_at.
    
    Args:
        db: Database session
        lead_id: ID of the lead to restore
        restored_by: User ID who performed the restoration
        
    Returns:
        True if lead was found and restored, False otherwise
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    
    if not lead:
        return False
    
    if lead.deleted_at is None:
        return False  # Already restored
    
    lead.deleted_at = None
    lead.modified_at = datetime.utcnow()
    if restored_by:
        lead.modified_by = restored_by
    
    db.commit()
    return True


def soft_delete_task(
    db: Session,
    task_id: str,
    deleted_by: Optional[str] = None
) -> bool:
    """
    Soft delete a task by setting deleted_at timestamp.
    
    Args:
        db: Database session
        task_id: ID of the task to delete
        deleted_by: User ID who performed the deletion
        
    Returns:
        True if task was found and soft deleted, False otherwise
    """
    task = db.query(Task).filter(
        Task.task_id == task_id,
        Task.deleted_at.is_(None)  # Only delete if not already deleted
    ).first()
    
    if not task:
        return False
    
    task.deleted_at = datetime.utcnow()
    task.modified_at = datetime.utcnow()
    if deleted_by:
        task.modified_by = deleted_by
    
    db.commit()
    return True


def restore_task(
    db: Session,
    task_id: str,
    restored_by: Optional[str] = None
) -> bool:
    """
    Restore a soft-deleted task by clearing deleted_at.
    
    Args:
        db: Database session
        task_id: ID of the task to restore
        restored_by: User ID who performed the restoration
        
    Returns:
        True if task was found and restored, False otherwise
    """
    task = db.query(Task).filter(Task.task_id == task_id).first()
    
    if not task:
        return False
    
    if task.deleted_at is None:
        return False  # Already restored
    
    task.deleted_at = None
    task.modified_at = datetime.utcnow()
    if restored_by:
        task.modified_by = restored_by
    
    db.commit()
    return True


def hard_delete_lead(
    db: Session,
    lead_id: int
) -> bool:
    """
    Permanently delete a lead (hard delete).
    Use with caution - this cannot be undone.
    
    Args:
        db: Database session
        lead_id: ID of the lead to permanently delete
        
    Returns:
        True if lead was found and deleted, False otherwise
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    
    if not lead:
        return False
    
    db.delete(lead)
    db.commit()
    return True


def hard_delete_task(
    db: Session,
    task_id: str
) -> bool:
    """
    Permanently delete a task (hard delete).
    Use with caution - this cannot be undone.
    
    Args:
        db: Database session
        task_id: ID of the task to permanently delete
        
    Returns:
        True if task was found and deleted, False otherwise
    """
    task = db.query(Task).filter(Task.task_id == task_id).first()
    
    if not task:
        return False
    
    db.delete(task)
    db.commit()
    return True

