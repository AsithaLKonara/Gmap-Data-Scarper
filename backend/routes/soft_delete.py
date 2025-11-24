"""Soft delete and restore endpoints."""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from backend.middleware.auth import get_current_user
from backend.dependencies import get_db
from backend.utils.soft_delete import (
    soft_delete_lead,
    restore_lead,
    soft_delete_task,
    restore_task,
    hard_delete_lead,
    hard_delete_task
)
from backend.utils.error_handler import not_found_error, handle_exception
from sqlalchemy.orm import Session
import os


def check_admin_access(db: Session, user_id: str) -> bool:
    """
    Check if user has admin access.
    
    For now, checks against ADMIN_USER_IDS environment variable (comma-separated).
    Can be extended to check User.is_admin field if added in future.
    
    Args:
        db: Database session
        user_id: User ID to check
        
    Returns:
        True if user is admin, False otherwise
    """
    # Check environment variable for admin user IDs
    admin_user_ids = os.getenv("ADMIN_USER_IDS", "").split(",")
    admin_user_ids = [uid.strip() for uid in admin_user_ids if uid.strip()]
    
    if user_id in admin_user_ids:
        return True
    
    # Future: Check User.is_admin field if it exists
    # from backend.models.user import User
    # user = db.query(User).filter(User.id == user_id).first()
    # if user and getattr(user, 'is_admin', False):
    #     return True
    
    return False

router = APIRouter(prefix="/api/soft-delete", tags=["soft-delete"])


@router.post("/leads/{lead_id}/delete")
async def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Soft delete a lead.
    
    Args:
        lead_id: ID of the lead to delete
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Success message
    """
    try:
        user_id = current_user.get("user_id")
        success = soft_delete_lead(db, lead_id, deleted_by=user_id)
        
        if not success:
            raise not_found_error(f"Lead {lead_id}")
        
        return {
            "status": "success",
            "message": f"Lead {lead_id} soft deleted successfully",
            "lead_id": lead_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise handle_exception(e, context="soft_delete_lead")


@router.post("/leads/{lead_id}/restore")
async def restore_lead_endpoint(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Restore a soft-deleted lead.
    
    Args:
        lead_id: ID of the lead to restore
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Success message
    """
    try:
        user_id = current_user.get("user_id")
        success = restore_lead(db, lead_id, restored_by=user_id)
        
        if not success:
            raise not_found_error(f"Lead {lead_id}")
        
        return {
            "status": "success",
            "message": f"Lead {lead_id} restored successfully",
            "lead_id": lead_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise handle_exception(e, context="restore_lead")


@router.post("/tasks/{task_id}/delete")
async def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Soft delete a task.
    
    Args:
        task_id: ID of the task to delete
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Success message
    """
    try:
        user_id = current_user.get("user_id")
        success = soft_delete_task(db, task_id, deleted_by=user_id)
        
        if not success:
            raise not_found_error(f"Task {task_id}")
        
        return {
            "status": "success",
            "message": f"Task {task_id} soft deleted successfully",
            "task_id": task_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise handle_exception(e, context="soft_delete_task")


@router.post("/tasks/{task_id}/restore")
async def restore_task_endpoint(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Restore a soft-deleted task.
    
    Args:
        task_id: ID of the task to restore
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Success message
    """
    try:
        user_id = current_user.get("user_id")
        success = restore_task(db, task_id, restored_by=user_id)
        
        if not success:
            raise not_found_error(f"Task {task_id}")
        
        return {
            "status": "success",
            "message": f"Task {task_id} restored successfully",
            "task_id": task_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise handle_exception(e, context="restore_task")


@router.post("/leads/{lead_id}/hard-delete")
async def hard_delete_lead_endpoint(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Permanently delete a lead (hard delete).
    Use with caution - this cannot be undone.
    
    Args:
        lead_id: ID of the lead to permanently delete
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Success message
    """
    try:
        # Check if user is admin
        user_id = current_user.get("user_id")
        if not check_admin_access(db, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required for hard delete operations"
            )
        
        success = hard_delete_lead(db, lead_id)
        
        if not success:
            raise not_found_error(f"Lead {lead_id}")
        
        return {
            "status": "success",
            "message": f"Lead {lead_id} permanently deleted",
            "lead_id": lead_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise handle_exception(e, context="hard_delete_lead")


@router.post("/tasks/{task_id}/hard-delete")
async def hard_delete_task_endpoint(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Permanently delete a task (hard delete).
    Use with caution - this cannot be undone.
    
    Args:
        task_id: ID of the task to permanently delete
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Success message
    """
    try:
        # Check if user is admin
        user_id = current_user.get("user_id")
        if not check_admin_access(db, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required for hard delete operations"
            )
        
        success = hard_delete_task(db, task_id)
        
        if not success:
            raise not_found_error(f"Task {task_id}")
        
        return {
            "status": "success",
            "message": f"Task {task_id} permanently deleted",
            "task_id": task_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise handle_exception(e, context="hard_delete_task")

