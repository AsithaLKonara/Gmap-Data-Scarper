"""Template management endpoints."""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/templates", tags=["templates"])


class ApplyTemplateRequest(BaseModel):
    """Request model for applying a template."""
    template_name: str
    variables: Dict[str, str] = {}


@router.get("/", response_model=List[Dict[str, str]])
async def list_templates():
    """List all available search templates."""
    from backend.services.template_service import template_service
    return template_service.list_templates()


@router.get("/{template_name}", response_model=Dict[str, Any])
async def get_template(template_name: str):
    """Get a specific template by name."""
    from backend.services.template_service import template_service
    template = template_service.get_template(template_name)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")
    return template


@router.post("/apply", response_model=Dict[str, Any])
async def apply_template(request: ApplyTemplateRequest):
    """
    Apply a template with variable substitution.
    
    Example:
    {
      "template_name": "Restaurants in any city",
      "variables": {"location": "Toronto"}
    }
    """
    from backend.services.template_service import template_service
    applied = template_service.apply_template(request.template_name, request.variables)
    if not applied:
        raise HTTPException(
            status_code=404,
            detail=f"Template '{request.template_name}' not found or failed to apply"
        )
    return applied

