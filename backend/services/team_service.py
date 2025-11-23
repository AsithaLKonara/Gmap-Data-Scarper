"""Team and workspace management service."""
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from backend.models.database import get_session
from backend.models.team import Team, SharedLeadList, TeamActivity, team_members
from backend.models.user import User


class TeamService:
    """Service for managing teams and workspaces."""
    
    def create_team(
        self,
        owner_id: str,
        name: str,
        description: Optional[str] = None,
        plan: Optional[str] = None
    ) -> Team:
        """
        Create a new team/workspace.
        
        Args:
            owner_id: User ID of the team owner
            name: Team name
            description: Team description
            plan: Team plan (free, pro, enterprise)
            
        Returns:
            Created Team instance
        """
        db = get_session()
        try:
            team_id = str(uuid.uuid4())
            
            team = Team(
                team_id=team_id,
                name=name,
                description=description,
                owner_id=owner_id,
                plan=plan or "free",
                settings={},
                is_active=True
            )
            
            db.add(team)
            
            # Add owner as admin member
            owner = db.query(User).filter(User.id == owner_id).first()
            if owner:
                # Insert into team_members association table
                from sqlalchemy import insert
                stmt = insert(team_members).values(
                    team_id=team_id,
                    user_id=owner_id,
                    role='admin',
                    joined_at=datetime.utcnow()
                )
                db.execute(stmt)
            
            db.commit()
            db.refresh(team)
            return team
        finally:
            db.close()
    
    def get_team(self, team_id: str) -> Optional[Team]:
        """Get a team by ID."""
        db = get_session()
        try:
            return db.query(Team).filter(Team.team_id == team_id).first()
        finally:
            db.close()
    
    def get_user_teams(self, user_id: str) -> List[Team]:
        """Get all teams a user belongs to."""
        db = get_session()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                return user.teams
            return []
        finally:
            db.close()
    
    def add_member(
        self,
        team_id: str,
        user_id: str,
        role: str = "member"
    ) -> bool:
        """
        Add a member to a team.
        
        Args:
            team_id: Team ID
            user_id: User ID to add
            role: Member role (admin, member, viewer)
            
        Returns:
            True if successful
        """
        db = get_session()
        try:
            # Check if already a member
            from sqlalchemy import select
            stmt = select(team_members).where(
                team_members.c.team_id == team_id,
                team_members.c.user_id == user_id
            )
            existing = db.execute(stmt).first()
            
            if existing:
                return False  # Already a member
            
            # Add member
            from sqlalchemy import insert
            stmt = insert(team_members).values(
                team_id=team_id,
                user_id=user_id,
                role=role,
                joined_at=datetime.utcnow()
            )
            db.execute(stmt)
            
            # Log activity
            self._log_activity(
                db, team_id, user_id, "member_added",
                f"New member added to team",
                {"added_user_id": user_id, "role": role}
            )
            
            db.commit()
            return True
        finally:
            db.close()
    
    def remove_member(self, team_id: str, user_id: str) -> bool:
        """Remove a member from a team."""
        db = get_session()
        try:
            from sqlalchemy import delete
            stmt = delete(team_members).where(
                team_members.c.team_id == team_id,
                team_members.c.user_id == user_id
            )
            db.execute(stmt)
            
            # Log activity
            self._log_activity(
                db, team_id, user_id, "member_removed",
                f"Member removed from team",
                {"removed_user_id": user_id}
            )
            
            db.commit()
            return True
        finally:
            db.close()
    
    def update_member_role(
        self,
        team_id: str,
        user_id: str,
        new_role: str
    ) -> bool:
        """Update a member's role."""
        db = get_session()
        try:
            from sqlalchemy import update
            stmt = update(team_members).where(
                team_members.c.team_id == team_id,
                team_members.c.user_id == user_id
            ).values(role=new_role)
            db.execute(stmt)
            
            # Log activity
            self._log_activity(
                db, team_id, user_id, "role_updated",
                f"Member role updated",
                {"user_id": user_id, "new_role": new_role}
            )
            
            db.commit()
            return True
        finally:
            db.close()
    
    def get_team_members(self, team_id: str) -> List[Dict[str, Any]]:
        """Get all members of a team."""
        db = get_session()
        try:
            from sqlalchemy import select
            stmt = select(team_members, User).join(
                User, team_members.c.user_id == User.id
            ).where(team_members.c.team_id == team_id)
            
            results = db.execute(stmt).all()
            members = []
            for row in results:
                members.append({
                    "user_id": row.user_id,
                    "email": row.email,
                    "name": row.name,
                    "role": row.role,
                    "joined_at": row.joined_at.isoformat() if row.joined_at else None,
                })
            return members
        finally:
            db.close()
    
    def check_permission(
        self,
        team_id: str,
        user_id: str,
        required_permission: str
    ) -> bool:
        """
        Check if user has required permission in team.
        
        Args:
            team_id: Team ID
            user_id: User ID
            required_permission: Permission to check (read, write, admin)
            
        Returns:
            True if user has permission
        """
        db = get_session()
        try:
            from sqlalchemy import select
            stmt = select(team_members).where(
                team_members.c.team_id == team_id,
                team_members.c.user_id == user_id
            )
            member = db.execute(stmt).first()
            
            if not member:
                return False
            
            role = member.role
            
            # Permission mapping
            if role == "admin":
                return True  # Admins have all permissions
            elif role == "member":
                return required_permission in ["read", "write"]
            elif role == "viewer":
                return required_permission == "read"
            
            return False
        finally:
            db.close()
    
    def create_shared_list(
        self,
        team_id: str,
        created_by: str,
        name: str,
        description: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> SharedLeadList:
        """Create a shared lead list."""
        db = get_session()
        try:
            list_id = str(uuid.uuid4())
            
            shared_list = SharedLeadList(
                list_id=list_id,
                team_id=team_id,
                name=name,
                description=description,
                created_by=created_by,
                filters=filters or {},
                tags=[],
                is_public=False,
                allowed_roles=["admin", "member"],
                lead_count=0
            )
            
            db.add(shared_list)
            
            # Log activity
            self._log_activity(
                db, team_id, created_by, "list_created",
                f"Created shared list: {name}",
                {"list_id": list_id, "list_name": name}
            )
            
            db.commit()
            db.refresh(shared_list)
            return shared_list
        finally:
            db.close()
    
    def get_team_activities(
        self,
        team_id: str,
        limit: int = 50
    ) -> List[TeamActivity]:
        """Get recent team activities."""
        db = get_session()
        try:
            return db.query(TeamActivity).filter(
                TeamActivity.team_id == team_id
            ).order_by(TeamActivity.created_at.desc()).limit(limit).all()
        finally:
            db.close()
    
    def _log_activity(
        self,
        db,
        team_id: str,
        user_id: str,
        activity_type: str,
        title: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log a team activity."""
        activity_id = str(uuid.uuid4())
        activity = TeamActivity(
            activity_id=activity_id,
            team_id=team_id,
            user_id=user_id,
            activity_type=activity_type,
            title=title,
            description=None,
            metadata=metadata or {}
        )
        db.add(activity)


# Global instance
team_service = TeamService()

