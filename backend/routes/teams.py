"""Team and workspace management endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.middleware.auth import get_current_user
from backend.services.team_service import team_service

router = APIRouter(prefix="/api/teams", tags=["teams"])


class TeamCreate(BaseModel):
    """Request model for creating a team."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    plan: Optional[str] = None


class AddMemberRequest(BaseModel):
    """Request model for adding a team member."""
    user_id: str
    role: str = Field(default="member", pattern="^(admin|member|viewer)$")


class UpdateRoleRequest(BaseModel):
    """Request model for updating member role."""
    user_id: str
    role: str = Field(..., pattern="^(admin|member|viewer)$")


class SharedListCreate(BaseModel):
    """Request model for creating a shared list."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None


@router.post("/", response_model=Dict[str, Any])
async def create_team(
    team: TeamCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new team/workspace."""
    try:
        user_id = current_user["user_id"]
        new_team = team_service.create_team(
            owner_id=user_id,
            name=team.name,
            description=team.description,
            plan=team.plan
        )
        return new_team.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create team: {str(e)}")


@router.get("/", response_model=List[Dict[str, Any]])
async def list_teams(current_user: dict = Depends(get_current_user)):
    """List all teams the user belongs to."""
    try:
        user_id = current_user["user_id"]
        teams = team_service.get_user_teams(user_id)
        return [t.to_dict() for t in teams]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list teams: {str(e)}")


@router.get("/{team_id}", response_model=Dict[str, Any])
async def get_team(
    team_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific team."""
    team = team_service.get_team(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check if user is a member
    user_id = current_user["user_id"]
    if not team_service.check_permission(team_id, user_id, "read"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return team.to_dict()


@router.post("/{team_id}/members", response_model=Dict[str, str])
async def add_member(
    team_id: str,
    request: AddMemberRequest,
    current_user: dict = Depends(get_current_user)
):
    """Add a member to a team."""
    user_id = current_user["user_id"]
    
    # Check if user has admin permission
    if not team_service.check_permission(team_id, user_id, "admin"):
        raise HTTPException(status_code=403, detail="Admin permission required")
    
    success = team_service.add_member(team_id, request.user_id, request.role)
    if not success:
        raise HTTPException(status_code=400, detail="User is already a member")
    
    return {"status": "success", "message": "Member added"}


@router.delete("/{team_id}/members/{member_id}", response_model=Dict[str, str])
async def remove_member(
    team_id: str,
    member_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove a member from a team."""
    user_id = current_user["user_id"]
    
    # Check if user has admin permission
    if not team_service.check_permission(team_id, user_id, "admin"):
        raise HTTPException(status_code=403, detail="Admin permission required")
    
    success = team_service.remove_member(team_id, member_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to remove member")
    
    return {"status": "success", "message": "Member removed"}


@router.put("/{team_id}/members/{member_id}/role", response_model=Dict[str, str])
async def update_member_role(
    team_id: str,
    member_id: str,
    request: UpdateRoleRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update a member's role."""
    user_id = current_user["user_id"]
    
    # Check if user has admin permission
    if not team_service.check_permission(team_id, user_id, "admin"):
        raise HTTPException(status_code=403, detail="Admin permission required")
    
    success = team_service.update_member_role(team_id, member_id, request.role)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update role")
    
    return {"status": "success", "message": "Role updated"}


@router.get("/{team_id}/members", response_model=List[Dict[str, Any]])
async def get_team_members(
    team_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all members of a team."""
    user_id = current_user["user_id"]
    
    # Check if user has read permission
    if not team_service.check_permission(team_id, user_id, "read"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    members = team_service.get_team_members(team_id)
    return members


@router.post("/{team_id}/lists", response_model=Dict[str, Any])
async def create_shared_list(
    team_id: str,
    request: SharedListCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a shared lead list."""
    user_id = current_user["user_id"]
    
    # Check if user has write permission
    if not team_service.check_permission(team_id, user_id, "write"):
        raise HTTPException(status_code=403, detail="Write permission required")
    
    shared_list = team_service.create_shared_list(
        team_id=team_id,
        created_by=user_id,
        name=request.name,
        description=request.description,
        filters=request.filters
    )
    return shared_list.to_dict()


@router.get("/{team_id}/activities", response_model=List[Dict[str, Any]])
async def get_team_activities(
    team_id: str,
    current_user: dict = Depends(get_current_user),
    limit: int = 50
):
    """Get team activity feed."""
    user_id = current_user["user_id"]
    
    # Check if user has read permission
    if not team_service.check_permission(team_id, user_id, "read"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    activities = team_service.get_team_activities(team_id, limit)
    return [a.to_dict() for a in activities]

