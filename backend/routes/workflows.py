"""Workflow management endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.middleware.auth import get_current_user

router = APIRouter(prefix="/api/workflows", tags=["workflows"])


class WorkflowCreate(BaseModel):
    """Request model for creating a workflow."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    trigger: Dict[str, Any] = Field(..., description="Workflow trigger configuration")
    actions: List[Dict[str, Any]] = Field(..., min_items=1, description="List of actions to execute")


class WorkflowUpdate(BaseModel):
    """Request model for updating a workflow."""
    name: Optional[str] = None
    description: Optional[str] = None
    trigger: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, Any]]] = None
    is_enabled: Optional[bool] = None


@router.post("/", response_model=Dict[str, Any])
async def create_workflow(
    workflow: WorkflowCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new workflow."""
    from backend.models.database import get_session
    from backend.models.workflow import Workflow
    from backend.dependencies import get_db
    from fastapi import Depends
    from sqlalchemy.orm import Session
    import uuid
    
    # Note: This endpoint doesn't use dependency injection yet due to complex logic
    # Will be updated in a future refactor
    db = get_session()
    try:
        workflow_id = str(uuid.uuid4())
        user_id = current_user["user_id"]
        
        new_workflow = Workflow(
            workflow_id=workflow_id,
            user_id=user_id,
            name=workflow.name,
            description=workflow.description,
            trigger=workflow.trigger,
            actions=workflow.actions,
            is_active=True,
            is_enabled=True
        )
        
        db.add(new_workflow)
        db.commit()
        db.refresh(new_workflow)
        
        return new_workflow.to_dict()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create workflow: {str(e)}")
    finally:
        db.close()


@router.get("/", response_model=List[Dict[str, Any]])
async def list_workflows(current_user: dict = Depends(get_current_user)):
    """List all workflows for the current user."""
    from backend.models.database import get_session
    from backend.models.workflow import Workflow
    
    db = get_session()
    try:
        user_id = current_user["user_id"]
        workflows = db.query(Workflow).filter(Workflow.user_id == user_id).all()
        return [w.to_dict() for w in workflows]
    finally:
        db.close()


@router.get("/{workflow_id}", response_model=Dict[str, Any])
async def get_workflow(
    workflow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific workflow."""
    from backend.models.database import get_session
    from backend.models.workflow import Workflow
    
    db = get_session()
    try:
        user_id = current_user["user_id"]
        workflow = db.query(Workflow).filter(
            Workflow.workflow_id == workflow_id,
            Workflow.user_id == user_id
        ).first()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return workflow.to_dict()
    finally:
        db.close()


@router.put("/{workflow_id}", response_model=Dict[str, Any])
async def update_workflow(
    workflow_id: str,
    update: WorkflowUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a workflow."""
    from backend.models.database import get_session
    from backend.models.workflow import Workflow
    from datetime import datetime
    
    db = get_session()
    try:
        user_id = current_user["user_id"]
        workflow = db.query(Workflow).filter(
            Workflow.workflow_id == workflow_id,
            Workflow.user_id == user_id
        ).first()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        if update.name is not None:
            workflow.name = update.name
        if update.description is not None:
            workflow.description = update.description
        if update.trigger is not None:
            workflow.trigger = update.trigger
        if update.actions is not None:
            workflow.actions = update.actions
        if update.is_enabled is not None:
            workflow.is_enabled = update.is_enabled
        
        workflow.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(workflow)
        
        return workflow.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update workflow: {str(e)}")
    finally:
        db.close()


@router.delete("/{workflow_id}", response_model=Dict[str, str])
async def delete_workflow(
    workflow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a workflow."""
    from backend.models.database import get_session
    from backend.models.workflow import Workflow
    
    db = get_session()
    try:
        user_id = current_user["user_id"]
        workflow = db.query(Workflow).filter(
            Workflow.workflow_id == workflow_id,
            Workflow.user_id == user_id
        ).first()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        workflow.is_active = False
        db.commit()
        
        return {"status": "deleted", "workflow_id": workflow_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete workflow: {str(e)}")
    finally:
        db.close()


@router.get("/{workflow_id}/executions", response_model=List[Dict[str, Any]])
async def get_workflow_executions(
    workflow_id: str,
    current_user: dict = Depends(get_current_user),
    limit: int = 50
):
    """Get execution history for a workflow."""
    from backend.models.database import get_session
    from backend.models.workflow import WorkflowExecution
    
    db = get_session()
    try:
        user_id = current_user["user_id"]
        executions = db.query(WorkflowExecution).filter(
            WorkflowExecution.workflow_id == workflow_id,
            WorkflowExecution.user_id == user_id
        ).order_by(WorkflowExecution.started_at.desc()).limit(limit).all()
        
        return [e.to_dict() for e in executions]
    finally:
        db.close()

