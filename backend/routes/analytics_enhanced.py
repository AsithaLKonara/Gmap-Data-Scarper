"""Enhanced analytics endpoints for advanced dashboards."""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, Optional
from backend.middleware.auth import get_current_user
from backend.services.analytics_service import analytics_service

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard_metrics(
    current_user: dict = Depends(get_current_user),
    team_id: Optional[str] = Query(None),
    date_range_days: int = Query(30, ge=1, le=365)
):
    """
    Get comprehensive dashboard metrics.
    
    Returns:
        Dict with:
        - total_leads: Total number of leads
        - leads_with_phone: Leads with phone numbers
        - leads_with_email: Leads with email
        - phone_coverage: Percentage with phone
        - email_coverage: Percentage with email
        - average_lead_score: Average lead score
        - platform_breakdown: Leads by platform
        - score_breakdown: Leads by score category
        - business_type_breakdown: Top business types
        - location_breakdown: Top locations
        - daily_trend: Daily lead counts
    """
    try:
        user_id = current_user["user_id"]
        metrics = analytics_service.get_dashboard_metrics(
            user_id=user_id,
            team_id=team_id,
            date_range_days=date_range_days
        )
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard metrics: {str(e)}")


@router.get("/pipeline", response_model=Dict[str, Any])
async def get_pipeline_metrics(
    current_user: dict = Depends(get_current_user),
    team_id: Optional[str] = Query(None)
):
    """
    Get lead pipeline metrics (funnel analysis).
    
    Returns:
        Dict with pipeline stages and conversion rates
    """
    try:
        user_id = current_user["user_id"]
        pipeline = analytics_service.get_pipeline_metrics(
            user_id=user_id,
            team_id=team_id
        )
        return pipeline
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pipeline metrics: {str(e)}")


@router.get("/forecast", response_model=Dict[str, Any])
async def get_revenue_forecast(
    current_user: dict = Depends(get_current_user),
    days_ahead: int = Query(30, ge=1, le=90)
):
    """
    Get revenue/lead forecast.
    
    Args:
        days_ahead: Number of days to forecast (1-90)
        
    Returns:
        Dict with forecast data and trend analysis
    """
    try:
        user_id = current_user["user_id"]
        forecast = analytics_service.get_revenue_forecast(
            user_id=user_id,
            days_ahead=days_ahead
        )
        return forecast
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get forecast: {str(e)}")

