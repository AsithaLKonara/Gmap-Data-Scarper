from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from models import Team, TeamMembership, User
from database import get_db
from auth import get_current_user
from security import check_permission
from datetime import datetime
from audit import audit_log

router = APIRouter(prefix="/api/teams", tags=["teams"])

class TeamIn(BaseModel):
    name: str

class TeamOut(BaseModel):
    id: int
    name: str
    owner_id: int
    created_at: str
    class Config:
        orm_mode = True

class MemberOut(BaseModel):
    id: int
    user_id: int
    role: str
    status: str
    invited_at: str
    class Config:
        orm_mode = True

def is_team_admin_or_manager(db, team_id, user_id):
    membership = db.query(TeamMembership).filter(TeamMembership.team_id == team_id, TeamMembership.user_id == user_id, TeamMembership.status == 'active').first()
    return membership and membership.role in ('admin', 'manager')

@router.post("/", response_model=TeamOut)
def create_team(data: TeamIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not check_permission(user, "teams", "manage", db):
        raise HTTPException(status_code=403, detail="Team features require Pro or Business plan")
    team = Team(name=data.name, owner_id=user.id)
    db.add(team)
    db.commit()
    db.refresh(team)
    # Add creator as admin member
    membership = TeamMembership(team_id=team.id, user_id=user.id, role='admin', status='active')
    db.add(membership)
    db.commit()
    return team

@router.get("/", response_model=List[TeamOut])
def list_teams(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not check_permission(user, "teams", "manage", db):
        raise HTTPException(status_code=403, detail="Team features require Pro or Business plan")
    teams = db.query(Team).join(TeamMembership).filter(TeamMembership.user_id == user.id, TeamMembership.status == 'active').all()
    return teams

@router.get("/{team_id}/members", response_model=List[MemberOut])
def list_team_members(team_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not check_permission(user, "teams", "manage", db):
        raise HTTPException(status_code=403, detail="Team features require Pro or Business plan")
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    # Only allow if user is a member
    membership = db.query(TeamMembership).filter(TeamMembership.team_id == team_id, TeamMembership.user_id == user.id, TeamMembership.status == 'active').first()
    if not membership:
        raise HTTPException(status_code=403, detail="Not a team member")
    return db.query(TeamMembership).filter(TeamMembership.team_id == team_id, TeamMembership.status == 'active').all()

class InviteIn(BaseModel):
    email: str
    role: str = 'member'

@router.post("/{team_id}/invite")
@audit_log(action="invite_team_member", target_type="team", target_id_param="team_id")
def invite_user(team_id: int, data: InviteIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not check_permission(user, "teams", "manage", db):
        raise HTTPException(status_code=403, detail="Team features require Pro or Business plan")
    if not is_team_admin_or_manager(db, team_id, user.id):
        raise HTTPException(status_code=403, detail="Only team admin or manager can invite")
    team = db.query(Team).filter(Team.id == team_id, Team.owner_id == user.id).first()
    if not team:
        raise HTTPException(status_code=403, detail="Only team owner can invite")
    invitee = db.query(User).filter(User.email == data.email).first()
    if not invitee:
        raise HTTPException(status_code=404, detail="User not found")
    # Prevent duplicate/invite
    existing = db.query(TeamMembership).filter(TeamMembership.team_id == team_id, TeamMembership.user_id == invitee.id).first()
    if existing and existing.status == 'active':
        raise HTTPException(status_code=400, detail="User already a member")
    if existing and existing.status == 'invited':
        return {"status": "already invited"}
    membership = TeamMembership(team_id=team_id, user_id=invitee.id, role=data.role, status='invited', invited_at=datetime.utcnow())
    db.add(membership)
    db.commit()
    return {"status": "invited"}

@router.post("/{team_id}/members/{member_id}/remove")
@audit_log(action="remove_team_member", target_type="team", target_id_param="team_id")
def remove_member(team_id: int, member_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not check_permission(user, "teams", "manage", db):
        raise HTTPException(status_code=403, detail="Team features require Pro or Business plan")
    if not is_team_admin_or_manager(db, team_id, user.id):
        raise HTTPException(status_code=403, detail="Only team admin or manager can remove members")
    team = db.query(Team).filter(Team.id == team_id, Team.owner_id == user.id).first()
    if not team:
        raise HTTPException(status_code=403, detail="Only team owner can remove members")
    membership = db.query(TeamMembership).filter(TeamMembership.team_id == team_id, TeamMembership.user_id == member_id, TeamMembership.status == 'active').first()
    if not membership:
        raise HTTPException(status_code=404, detail="Member not found")
    membership.status = 'removed'
    db.commit()
    return {"status": "removed"}

class RoleIn(BaseModel):
    role: str

@router.post("/{team_id}/members/{member_id}/role")
@audit_log(action="change_team_member_role", target_type="team", target_id_param="team_id")
def change_role(team_id: int, member_id: int, data: RoleIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not check_permission(user, "teams", "manage", db):
        raise HTTPException(status_code=403, detail="Team features require Pro or Business plan")
    if not is_team_admin_or_manager(db, team_id, user.id):
        raise HTTPException(status_code=403, detail="Only team admin or manager can change roles")
    team = db.query(Team).filter(Team.id == team_id, Team.owner_id == user.id).first()
    if not team:
        raise HTTPException(status_code=403, detail="Only team owner can change roles")
    membership = db.query(TeamMembership).filter(TeamMembership.team_id == team_id, TeamMembership.user_id == member_id, TeamMembership.status == 'active').first()
    if not membership:
        raise HTTPException(status_code=404, detail="Member not found")
    membership.role = data.role
    db.commit()
    return {"status": "role updated"}

@router.post("/{team_id}/transfer-ownership/{new_owner_id}")
@audit_log(action="transfer_team_ownership", target_type="team", target_id_param="team_id")
def transfer_ownership(team_id: int, new_owner_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not check_permission(user, "teams", "manage", db):
        raise HTTPException(status_code=403, detail="Team features require Pro or Business plan")
    if not is_team_admin_or_manager(db, team_id, user.id):
        raise HTTPException(status_code=403, detail="Only team admin or manager can transfer ownership")
    team = db.query(Team).filter(Team.id == team_id, Team.owner_id == user.id).first()
    if not team:
        raise HTTPException(status_code=403, detail="Only team owner can transfer ownership")
    new_owner = db.query(User).filter(User.id == new_owner_id).first()
    if not new_owner:
        raise HTTPException(status_code=404, detail="New owner not found")
    team.owner_id = new_owner_id
    db.commit()
    return {"status": "ownership transferred"}

@router.post("/memberships/{membership_id}/accept")
@audit_log(action="accept_team_invite", target_type="team")
def accept_invite(membership_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not check_permission(user, "teams", "manage", db):
        raise HTTPException(status_code=403, detail="Team features require Pro or Business plan")
    membership = db.query(TeamMembership).filter(TeamMembership.id == membership_id, TeamMembership.user_id == user.id, TeamMembership.status == 'invited').first()
    if not membership:
        raise HTTPException(status_code=404, detail="Invite not found")
    membership.status = 'active'
    db.commit()
    return {"status": "accepted"}

@router.post("/memberships/{membership_id}/decline")
@audit_log(action="decline_team_invite", target_type="team")
def decline_invite(membership_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not check_permission(user, "teams", "manage", db):
        raise HTTPException(status_code=403, detail="Team features require Pro or Business plan")
    membership = db.query(TeamMembership).filter(TeamMembership.id == membership_id, TeamMembership.user_id == user.id, TeamMembership.status == 'invited').first()
    if not membership:
        raise HTTPException(status_code=404, detail="Invite not found")
    membership.status = 'removed'
    db.commit()
    return {"status": "declined"} 