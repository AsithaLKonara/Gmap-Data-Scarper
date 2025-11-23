"""White-label and custom branding service."""
from typing import Dict, Any, Optional
from backend.models.database import get_session
from backend.models.user import User


class WhiteLabelService:
    """Service for white-label customization."""
    
    def get_branding_config(
        self,
        user_id: Optional[str] = None,
        team_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get branding configuration for user/team.
        
        Args:
            user_id: User ID
            team_id: Team ID
            
        Returns:
            Branding configuration
        """
        # Default branding
        default_config = {
            "logo_url": None,
            "primary_color": "#3B82F6",
            "secondary_color": "#8B5CF6",
            "company_name": "Lead Intelligence Platform",
            "favicon_url": None,
            "custom_css": None,
            "hide_branding": False
        }
        
        # In production, would load from database
        # For now, return default
        if team_id:
            # Load team branding
            from backend.models.team import Team
            db = get_session()
            try:
                team = db.query(Team).filter(Team.team_id == team_id).first()
                if team and team.settings:
                    branding = team.settings.get("branding", {})
                    default_config.update(branding)
            finally:
                db.close()
        
        return default_config
    
    def update_branding(
        self,
        user_id: str,
        team_id: Optional[str],
        branding_config: Dict[str, Any]
    ) -> bool:
        """
        Update branding configuration.
        
        Args:
            user_id: User ID
            team_id: Team ID
            branding_config: Branding configuration
            
        Returns:
            True if successful
        """
        if not team_id:
            return False
        
        db = get_session()
        try:
            from backend.models.team import Team
            team = db.query(Team).filter(
                Team.team_id == team_id,
                Team.owner_id == user_id  # Only owner can update
            ).first()
            
            if not team:
                return False
            
            if not team.settings:
                team.settings = {}
            
            team.settings["branding"] = branding_config
            db.commit()
            return True
        finally:
            db.close()


# Global instance
white_label_service = WhiteLabelService()

