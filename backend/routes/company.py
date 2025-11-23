"""Company intelligence endpoints."""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/company", tags=["company"])


class CompanyIntelligenceRequest(BaseModel):
    """Request model for company intelligence."""
    company_name: str
    website: Optional[str] = None
    location: Optional[str] = None


@router.post("/intelligence", response_model=Dict[str, Any])
async def get_company_intelligence(request: CompanyIntelligenceRequest):
    """
    Get comprehensive company intelligence.
    
    Returns:
        Dict with:
        - employee_count: Estimated employee count
        - revenue_estimate: Revenue estimate range
        - funding_rounds: List of funding rounds
        - total_funding: Total funding amount
        - competitors: List of competitor names
        - tags: List of company tags
        - founded_year: Year company was founded
        - headquarters: Company headquarters location
    """
    from backend.services.company_intelligence import company_intelligence_service
    
    try:
        intelligence = company_intelligence_service.get_company_intelligence(
            company_name=request.company_name,
            website=request.website,
            location=request.location
        )
        return intelligence
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get company intelligence: {str(e)}")

