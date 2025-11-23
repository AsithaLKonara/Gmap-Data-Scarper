"""Task management endpoints."""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from backend.models.schemas import TaskStatus
from backend.services.orchestrator_service import task_manager
from backend.middleware.auth import get_optional_user
from datetime import datetime
from typing import List as ListType

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=List[dict])
async def list_tasks(
    status: Optional[str] = Query(None, description="Filter by status (running, paused, completed, error, stopped)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of tasks to return"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip"),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    List all tasks for the current user.
    
    Returns tasks with metadata including status, progress, and timestamps.
    """
    user_id = current_user.get("user_id") if current_user else None
    
    # Get user's tasks
    if user_id:
        tasks = task_manager.get_user_tasks(user_id)
    else:
        # For unauthenticated users, return empty list or all tasks (depending on requirements)
        tasks = []
    
    # Filter by status if provided
    if status:
        tasks = [t for t in tasks if t.get("status") == status]
    
    # Sort by started_at (most recent first)
    tasks.sort(key=lambda x: x.get("started_at", datetime.min), reverse=True)
    
    # Apply pagination
    paginated_tasks = tasks[offset:offset + limit]
    
    # Format response
    return [
        {
            "task_id": task["task_id"],
            "status": task["status"],
            "progress": task.get("progress", {}),
            "total_results": task.get("total_results", 0),
            "started_at": task.get("started_at").isoformat() if task.get("started_at") else None,
            "completed_at": task.get("completed_at").isoformat() if task.get("completed_at") else None,
            "duration_seconds": (
                (task.get("completed_at") or datetime.now()) - task.get("started_at", datetime.now())
            ).total_seconds() if task.get("started_at") else None,
        }
        for task in paginated_tasks
    ]


@router.get("/{task_id}", response_model=TaskStatus)
async def get_task(
    task_id: str,
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Get detailed status of a specific task."""
    user_id = current_user.get("user_id") if current_user else None
    status = task_manager.get_task_status(task_id, user_id=user_id)
    
    if status is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return status


@router.get("/queue/status", response_model=dict)
async def get_queue_status(
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    Get queue statistics for the current user.
    
    Returns pending tasks count, estimated wait time, etc.
    """
    user_id = current_user.get("user_id") if current_user else None
    
    if user_id:
        all_tasks = task_manager.get_user_tasks(user_id)
    else:
        all_tasks = []
    
    running_tasks = [t for t in all_tasks if t.get("status") == "running"]
    paused_tasks = [t for t in all_tasks if t.get("status") == "paused"]
    pending_tasks = [t for t in all_tasks if t.get("status") == "pending"]
    completed_tasks = [t for t in all_tasks if t.get("status") == "completed"]
    
    return {
        "total_tasks": len(all_tasks),
        "running": len(running_tasks),
        "paused": len(paused_tasks),
        "pending": len(pending_tasks),
        "completed": len(completed_tasks),
        "estimated_wait_time_seconds": len(pending_tasks) * 60,  # Rough estimate: 1 minute per task
    }


@router.post("/bulk/stop")
async def bulk_stop_tasks(
    task_ids: ListType[str],
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    Stop multiple tasks at once.
    
    Returns count of successfully stopped tasks.
    """
    user_id = current_user.get("user_id") if current_user else None
    stopped_count = 0
    errors = []
    
    for task_id in task_ids:
        try:
            # Verify task belongs to user
            task_status = task_manager.get_task_status(task_id, user_id=user_id)
            if task_status:
                task_manager.stop_task(task_id)
                stopped_count += 1
            else:
                errors.append(f"Task {task_id} not found or access denied")
        except Exception as e:
            errors.append(f"Failed to stop {task_id}: {str(e)}")
    
    return {
        "stopped_count": stopped_count,
        "total_requested": len(task_ids),
        "errors": errors
    }


@router.post("/bulk/pause")
async def bulk_pause_tasks(
    task_ids: ListType[str],
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    Pause multiple tasks at once.
    
    Returns count of successfully paused tasks.
    """
    user_id = current_user.get("user_id") if current_user else None
    paused_count = 0
    errors = []
    
    for task_id in task_ids:
        try:
            # Verify task belongs to user
            task_status = task_manager.get_task_status(task_id, user_id=user_id)
            if task_status and task_status.status == "running":
                task_manager.pause_task(task_id)
                paused_count += 1
            else:
                errors.append(f"Task {task_id} not found, not running, or access denied")
        except Exception as e:
            errors.append(f"Failed to pause {task_id}: {str(e)}")
    
    return {
        "paused_count": paused_count,
        "total_requested": len(task_ids),
        "errors": errors
    }


@router.post("/bulk/resume")
async def bulk_resume_tasks(
    task_ids: ListType[str],
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    Resume multiple paused tasks at once.
    
    Returns count of successfully resumed tasks.
    """
    user_id = current_user.get("user_id") if current_user else None
    resumed_count = 0
    errors = []
    
    for task_id in task_ids:
        try:
            # Verify task belongs to user
            task_status = task_manager.get_task_status(task_id, user_id=user_id)
            if task_status and task_status.status == "paused":
                task_manager.resume_task(task_id)
                resumed_count += 1
            else:
                errors.append(f"Task {task_id} not found, not paused, or access denied")
        except Exception as e:
            errors.append(f"Failed to resume {task_id}: {str(e)}")
    
    return {
        "resumed_count": resumed_count,
        "total_requested": len(task_ids),
        "errors": errors
    }
