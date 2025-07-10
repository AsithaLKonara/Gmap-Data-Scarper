from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from models import User, Lead, LeadScore
from database import get_db
from auth import get_current_user
import json
from datetime import datetime, timedelta
import re

router = APIRouter(prefix="/api/lead-scoring", tags=["lead-scoring"])

class LeadScoreRequest(BaseModel):
    lead_id: int
    recalculate: bool = False

class LeadScoreResponse(BaseModel):
    lead_id: int
    overall_score: float
    factors: Dict[str, float]
    recommendations: List[str]
    risk_level: str
    conversion_probability: float

class ScoringRule(BaseModel):
    name: str
    weight: float
    description: str
    enabled: bool

# Lead scoring factors and weights
SCORING_FACTORS = {
    "email_quality": {
        "weight": 0.15,
        "description": "Email address validity and format",
        "rules": {
            "valid_format": 1.0,
            "business_domain": 0.8,
            "personal_domain": 0.6,
            "disposable_email": 0.2
        }
    },
    "company_info": {
        "weight": 0.20,
        "description": "Company information completeness",
        "rules": {
            "has_company": 1.0,
            "has_website": 0.8,
            "has_phone": 0.7,
            "has_address": 0.6
        }
    },
    "source_quality": {
        "weight": 0.25,
        "description": "Lead source reliability",
        "rules": {
            "google_maps": 1.0,
            "facebook": 0.8,
            "linkedin": 0.9,
            "manual": 0.7,
            "import": 0.6
        }
    },
    "engagement_potential": {
        "weight": 0.20,
        "description": "Potential for engagement",
        "rules": {
            "has_phone": 1.0,
            "has_website": 0.8,
            "has_social_media": 0.7,
            "recent_activity": 0.9
        }
    },
    "demographics": {
        "weight": 0.10,
        "description": "Demographic factors",
        "rules": {
            "location_match": 1.0,
            "industry_match": 0.8,
            "size_match": 0.7
        }
    },
    "behavioral": {
        "weight": 0.10,
        "description": "Behavioral indicators",
        "rules": {
            "recent_contact": 1.0,
            "response_history": 0.8,
            "interaction_frequency": 0.7
        }
    }
}

def validate_email(email: str) -> Dict[str, float]:
    """Validate email and return quality score"""
    if not email:
        return {"score": 0.0, "reason": "no_email"}
    
    # Basic email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return {"score": 0.0, "reason": "invalid_format"}
    
    # Check for business domains
    business_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
    domain = email.split('@')[1].lower()
    
    if domain in business_domains:
        return {"score": 0.6, "reason": "personal_domain"}
    else:
        return {"score": 0.8, "reason": "business_domain"}

def calculate_company_score(lead: Lead) -> float:
    """Calculate company information score"""
    score = 0.0
    factors = 0
    
    if lead.company:
        score += 1.0
        factors += 1
    
    if lead.website:
        score += 0.8
        factors += 1
    
    if lead.phone:
        score += 0.7
        factors += 1
    
    if lead.address:
        score += 0.6
        factors += 1
    
    return score / factors if factors > 0 else 0.0

def calculate_source_score(source: str) -> float:
    """Calculate lead source quality score"""
    source_scores = {
        "google_maps": 1.0,
        "facebook": 0.8,
        "linkedin": 0.9,
        "manual": 0.7,
        "import": 0.6,
        "gmaps": 1.0,  # Alternative name
        "social": 0.8,
        "web": 0.7
    }
    
    return source_scores.get(source.lower(), 0.5)

def calculate_engagement_score(lead: Lead) -> float:
    """Calculate engagement potential score"""
    score = 0.0
    factors = 0
    
    if lead.phone:
        score += 1.0
        factors += 1
    
    if lead.website:
        score += 0.8
        factors += 1
    
    # Check for social media indicators in notes
    if lead.notes:
        social_indicators = ['facebook', 'linkedin', 'twitter', 'instagram']
        if any(indicator in lead.notes.lower() for indicator in social_indicators):
            score += 0.7
            factors += 1
    
    return score / factors if factors > 0 else 0.0

@router.post("/score", response_model=LeadScoreResponse)
def score_lead(
    score_request: LeadScoreRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Calculate or recalculate lead score"""
    
    # Get the lead
    lead = db.query(Lead).filter(
        Lead.id == score_request.lead_id,
        Lead.user_id == user.id
    ).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Check if score already exists and recalculate is not requested
    existing_score = db.query(LeadScore).filter(
        LeadScore.lead_id == score_request.lead_id
    ).first()
    
    if existing_score and not score_request.recalculate:
        return LeadScoreResponse(
            lead_id=lead.id,
            overall_score=existing_score.overall_score,
            factors=json.loads(existing_score.factors),
            recommendations=json.loads(existing_score.recommendations),
            risk_level=existing_score.risk_level,
            conversion_probability=existing_score.conversion_probability
        )
    
    # Calculate individual factor scores
    factors = {}
    
    # Email quality
    email_result = validate_email(lead.email)
    factors["email_quality"] = email_result["score"]
    
    # Company information
    factors["company_info"] = calculate_company_score(lead)
    
    # Source quality
    factors["source_quality"] = calculate_source_score(lead.source)
    
    # Engagement potential
    factors["engagement_potential"] = calculate_engagement_score(lead)
    
    # Demographics (simplified - could be enhanced with location/industry matching)
    factors["demographics"] = 0.7  # Default score
    
    # Behavioral (simplified - could be enhanced with interaction history)
    factors["behavioral"] = 0.6  # Default score
    
    # Calculate weighted overall score
    overall_score = 0.0
    total_weight = 0.0
    
    for factor, weight in SCORING_FACTORS.items():
        if factor in factors:
            overall_score += factors[factor] * weight["weight"]
            total_weight += weight["weight"]
    
    overall_score = overall_score / total_weight if total_weight > 0 else 0.0
    
    # Determine risk level and conversion probability
    if overall_score >= 0.8:
        risk_level = "low"
        conversion_probability = 0.85
    elif overall_score >= 0.6:
        risk_level = "medium"
        conversion_probability = 0.65
    elif overall_score >= 0.4:
        risk_level = "high"
        conversion_probability = 0.45
    else:
        risk_level = "very_high"
        conversion_probability = 0.25
    
    # Generate recommendations
    recommendations = []
    
    if factors["email_quality"] < 0.5:
        recommendations.append("Verify email address validity")
    
    if factors["company_info"] < 0.5:
        recommendations.append("Add more company information")
    
    if factors["source_quality"] < 0.7:
        recommendations.append("Consider higher quality lead sources")
    
    if factors["engagement_potential"] < 0.5:
        recommendations.append("Add contact information for better engagement")
    
    if overall_score < 0.6:
        recommendations.append("Lead may need additional qualification")
    
    # Save or update score
    if existing_score:
        existing_score.overall_score = overall_score
        existing_score.factors = json.dumps(factors)
        existing_score.recommendations = json.dumps(recommendations)
        existing_score.risk_level = risk_level
        existing_score.conversion_probability = conversion_probability
        existing_score.updated_at = datetime.utcnow()
    else:
        new_score = LeadScore(
            lead_id=lead.id,
            overall_score=overall_score,
            factors=json.dumps(factors),
            recommendations=json.dumps(recommendations),
            risk_level=risk_level,
            conversion_probability=conversion_probability,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(new_score)
    
    db.commit()
    
    return LeadScoreResponse(
        lead_id=lead.id,
        overall_score=overall_score,
        factors=factors,
        recommendations=recommendations,
        risk_level=risk_level,
        conversion_probability=conversion_probability
    )

@router.get("/leads/{lead_id}/score")
def get_lead_score(
    lead_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get lead score if it exists"""
    
    # Verify lead belongs to user
    lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.user_id == user.id
    ).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Get score
    score = db.query(LeadScore).filter(LeadScore.lead_id == lead_id).first()
    
    if not score:
        raise HTTPException(status_code=404, detail="Lead score not found")
    
    return {
        "lead_id": lead_id,
        "overall_score": score.overall_score,
        "factors": json.loads(score.factors),
        "recommendations": json.loads(score.recommendations),
        "risk_level": score.risk_level,
        "conversion_probability": score.conversion_probability,
        "created_at": score.created_at,
        "updated_at": score.updated_at
    }

@router.get("/stats")
def get_scoring_stats(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get lead scoring statistics"""
    
    # Get all scored leads for user
    scored_leads = db.query(LeadScore).join(Lead).filter(Lead.user_id == user.id).all()
    
    if not scored_leads:
        return {
            "total_scored": 0,
            "average_score": 0,
            "score_distribution": {},
            "risk_distribution": {},
            "recommendations_summary": []
        }
    
    total_scored = len(scored_leads)
    average_score = sum(score.overall_score for score in scored_leads) / total_scored
    
    # Score distribution
    score_distribution = {
        "high": len([s for s in scored_leads if s.overall_score >= 0.8]),
        "medium": len([s for s in scored_leads if 0.6 <= s.overall_score < 0.8]),
        "low": len([s for s in scored_leads if s.overall_score < 0.6])
    }
    
    # Risk distribution
    risk_distribution = {}
    for score in scored_leads:
        risk_distribution[score.risk_level] = risk_distribution.get(score.risk_level, 0) + 1
    
    # Common recommendations
    all_recommendations = []
    for score in scored_leads:
        recommendations = json.loads(score.recommendations)
        all_recommendations.extend(recommendations)
    
    from collections import Counter
    recommendation_counts = Counter(all_recommendations)
    top_recommendations = [{"recommendation": rec, "count": count} 
                          for rec, count in recommendation_counts.most_common(5)]
    
    return {
        "total_scored": total_scored,
        "average_score": round(average_score, 3),
        "score_distribution": score_distribution,
        "risk_distribution": risk_distribution,
        "recommendations_summary": top_recommendations
    }

@router.post("/bulk-score")
def bulk_score_leads(
    lead_ids: List[int],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Score multiple leads at once"""
    
    results = []
    
    for lead_id in lead_ids:
        try:
            score_request = LeadScoreRequest(lead_id=lead_id, recalculate=True)
            result = score_lead(score_request, db, user)
            results.append({
                "lead_id": lead_id,
                "status": "success",
                "score": result.overall_score
            })
        except Exception as e:
            results.append({
                "lead_id": lead_id,
                "status": "error",
                "error": str(e)
            })
    
    return {"results": results} 