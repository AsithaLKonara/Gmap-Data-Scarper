"""AI-powered features endpoints."""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel

router = APIRouter(prefix="/api/ai", tags=["ai"])


class GenerateSearchRequest(BaseModel):
    """Request model for AI search generation."""
    query: str = "Find me 500 Shopify stores in Canada doing paid ads"


@router.post("/generate-search", response_model=Dict[str, Any])
async def generate_search_config(request: GenerateSearchRequest):
    """
    Generate search configuration from natural language input.
    
    Example: "Find me 500 Shopify stores in Canada doing paid ads"
    Returns: Optimized queries, platforms, filters, and expected results
    """
    from backend.services.ai_query_generator import ai_query_generator
    
    try:
        result = ai_query_generator.generate_search_config(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate search config: {str(e)}")

