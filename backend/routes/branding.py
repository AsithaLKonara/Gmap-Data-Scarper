"""White-label and branding endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from pydantic import BaseModel
from backend.middleware.auth import get_current_user
from backend.services.white_label_service import white_label_service

router = APIRouter(prefix="/api/branding", tags=["branding"])


class BrandingConfig(BaseModel):
    """Request model for branding configuration."""
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    company_name: Optional[str] = None
    favicon_url: Optional[str] = None
    custom_css: Optional[str] = None
    hide_branding: Optional[bool] = None


@router.get("/", response_model=Dict[str, Any])
async def get_branding(
    current_user: dict = Depends(get_current_user),
    team_id: Optional[str] = None
):
    """Get branding configuration."""
    try:
        user_id = current_user["user_id"]
        config = white_label_service.get_branding_config(
            user_id=user_id,
            team_id=team_id
        )
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get branding: {str(e)}")


@router.put("/", response_model=Dict[str, str])
async def update_branding(
    branding: BrandingConfig,
    current_user: dict = Depends(get_current_user),
    team_id: Optional[str] = None
):
    """Update branding configuration."""
    try:
        user_id = current_user["user_id"]
        branding_dict = branding.dict(exclude_none=True)
        
        success = white_label_service.update_branding(
            user_id=user_id,
            team_id=team_id,
            branding_config=branding_dict
        )
        
        if not success:
            raise HTTPException(status_code=403, detail="Permission denied or team not found")
        
        return {"status": "success", "message": "Branding updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update branding: {str(e)}")

