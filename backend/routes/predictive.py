"""Predictive analytics endpoints."""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from backend.middleware.auth import get_current_user
from backend.services.predictive_analytics import predictive_analytics_service
from backend.services.ai_recommendations import ai_recommendation_service
from backend.services.sentiment_analyzer import sentiment_analyzer

router = APIRouter(prefix="/api/predictive", tags=["predictive"])


class LeadDataRequest(BaseModel):
    """Request model for lead conversion prediction."""
    lead_data: Dict[str, Any]


class QualificationRules(BaseModel):
    """Request model for lead qualification."""
    min_score: Optional[int] = 70
    require_phone: Optional[bool] = True
    require_email: Optional[bool] = False
    min_followers: Optional[int] = 0


@router.post("/conversion", response_model=Dict[str, Any])
async def predict_conversion(
    request: LeadDataRequest,
    current_user: dict = Depends(get_current_user)
):
    """Predict lead conversion probability."""
    try:
        prediction = predictive_analytics_service.predict_lead_conversion(request.lead_data)
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to predict conversion: {str(e)}")


@router.get("/churn", response_model=Dict[str, Any])
async def predict_churn(
    current_user: dict = Depends(get_current_user),
    days_lookback: int = Query(30, ge=7, le=90)
):
    """Predict user churn risk."""
    try:
        user_id = current_user["user_id"]
        prediction = predictive_analytics_service.predict_churn(user_id, days_lookback)
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to predict churn: {str(e)}")


@router.get("/trends", response_model=Dict[str, Any])
async def get_market_trends(
    current_user: dict = Depends(get_current_user),
    days: int = Query(90, ge=7, le=365)
):
    """Get market trend analysis."""
    try:
        trends = predictive_analytics_service.analyze_market_trends(days)
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trends: {str(e)}")


@router.post("/recommendations", response_model=List[Dict[str, Any]])
async def get_lead_recommendations(
    criteria: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=50)
):
    """Get AI-powered lead recommendations."""
    try:
        user_id = current_user["user_id"]
        recommendations = ai_recommendation_service.recommend_leads(
            user_id=user_id,
            criteria=criteria,
            limit=limit
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.post("/qualify", response_model=Dict[str, Any])
async def auto_qualify_lead(
    lead_data: Dict[str, Any],
    rules: Optional[QualificationRules] = None,
    current_user: dict = Depends(get_current_user)
):
    """Automatically qualify a lead."""
    try:
        rules_dict = rules.dict() if rules else None
        qualification = ai_recommendation_service.auto_qualify_lead(
            lead_data=lead_data,
            qualification_rules=rules_dict
        )
        return qualification
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to qualify lead: {str(e)}")


class SentimentRequest(BaseModel):
    """Request model for sentiment analysis."""
    text: str


@router.post("/sentiment", response_model=Dict[str, Any])
async def analyze_sentiment(
    request: SentimentRequest,
    current_user: dict = Depends(get_current_user)
):
    """Analyze sentiment of text."""
    try:
        analysis = sentiment_analyzer.analyze_sentiment(request.text)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze sentiment: {str(e)}")


class IntentRequest(BaseModel):
    """Request model for intent detection."""
    text: str


@router.post("/intent", response_model=Dict[str, Any])
async def detect_intent(
    request: IntentRequest,
    current_user: dict = Depends(get_current_user)
):
    """Detect intent from text."""
    try:
        intent = sentiment_analyzer.detect_intent(request.text)
        return intent
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to detect intent: {str(e)}")

