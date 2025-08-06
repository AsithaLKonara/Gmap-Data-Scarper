# Enhanced Lead Scoring with Advanced Algorithms
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
import logging
import re
from datetime import datetime, timezone
from models import Users, Jobs, LeadScores, Leads
from database import get_db
from auth import get_current_user
from security import check_permission

router = APIRouter(prefix="/api/lead-scoring", tags=["lead-scoring"])

logger = logging.getLogger("lead_scoring")

class LeadScoreRequest(BaseModel):
    job_id: int = Field(..., description="ID of the job to score leads for")
    scoring_criteria: Dict[str, float] = Field(..., description="Scoring criteria and weights")

class LeadScoreResponse(BaseModel):
    lead_id: int
    company_name: str
    score: float
    factors: Dict[str, float]
    recommendations: List[str]

class ScoringCriteria(BaseModel):
    name: str
    weight: float = Field(..., ge=0, le=1, description="Weight between 0 and 1")
    description: str

class BulkScoreRequest(BaseModel):
    lead_ids: List[int] = Field(..., description="List of lead IDs to score")
    scoring_criteria: Optional[Dict[str, float]] = Field(None, description="Optional custom scoring criteria")

@router.post("/score/{job_id}", response_model=List[LeadScoreResponse], summary="Score leads for a job")
def score_leads(
    job_id: int,
    request: LeadScoreRequest,
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Score leads for a specific job using advanced algorithms"""
    try:
        # Check permissions
        if not check_permission(user, "leads:score"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get job and verify ownership
        job = db.query(Jobs).filter(Jobs.id == job_id, Jobs.user_id == user.id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Get job results
        if not job.results:
            raise HTTPException(status_code=400, detail="No results available for scoring")
        
        results = json.loads(job.results)
        scored_leads = []
        
        for i, lead in enumerate(results):
            score, factors, recommendations = calculate_lead_score(lead, request.scoring_criteria)
            
            # Save score to database
            lead_score = LeadScores(
                job_id=job_id,
                lead_data=json.dumps(lead),
                score=score,
                factors=json.dumps(factors),
                recommendations=json.dumps(recommendations),
                user_id=user.id
            )
            db.add(lead_score)
            
            scored_leads.append(LeadScoreResponse(
                lead_id=i,
                company_name=lead.get('name', 'Unknown'),
                score=score,
                factors=factors,
                recommendations=recommendations
            ))
        
        db.commit()
        
        logger.info(f"Scored {len(scored_leads)} leads for job {job_id}")
        
        return scored_leads
        
    except Exception as e:
        logger.exception("Error scoring leads")
        raise HTTPException(status_code=500, detail="Failed to score leads")

def calculate_lead_score(lead: Dict[str, Any], criteria: Dict[str, float]) -> tuple:
    """Calculate lead score using advanced algorithms"""
    score = 0.0
    factors = {}
    recommendations = []
    
    # Company size scoring
    if 'employee_count' in lead:
        employee_count = lead['employee_count']
        if employee_count:
            if employee_count > 1000:
                factors['company_size'] = 0.9
                recommendations.append("Large company - high potential value")
            elif employee_count > 100:
                factors['company_size'] = 0.7
                recommendations.append("Medium company - good potential")
            else:
                factors['company_size'] = 0.4
                recommendations.append("Small company - lower potential")
        else:
            factors['company_size'] = 0.5
    
    # Rating scoring
    if 'rating' in lead and lead['rating']:
        rating = float(lead['rating'])
        factors['rating'] = rating / 5.0
        if rating >= 4.5:
            recommendations.append("High rating - strong reputation")
        elif rating >= 4.0:
            recommendations.append("Good rating - reliable business")
    
    # Review count scoring
    if 'review_count' in lead and lead['review_count']:
        review_count = int(lead['review_count'])
        if review_count > 100:
            factors['engagement'] = 0.9
            recommendations.append("High engagement - many reviews")
        elif review_count > 50:
            factors['engagement'] = 0.7
            recommendations.append("Good engagement - moderate reviews")
        else:
            factors['engagement'] = 0.4
            recommendations.append("Low engagement - few reviews")
    
    # Location scoring
    if 'location' in lead:
        location = lead['location'].lower()
        if any(city in location for city in ['new york', 'los angeles', 'chicago', 'san francisco']):
            factors['location'] = 0.9
            recommendations.append("Major market location")
        elif any(city in location for city in ['boston', 'seattle', 'austin', 'denver']):
            factors['location'] = 0.8
            recommendations.append("Growing market location")
        else:
            factors['location'] = 0.6
            recommendations.append("Standard market location")
    
    # Website presence
    if 'website' in lead and lead['website']:
        factors['online_presence'] = 0.8
        recommendations.append("Has website - professional presence")
    else:
        factors['online_presence'] = 0.3
        recommendations.append("No website - limited online presence")
    
    # Phone number presence
    if 'phone' in lead and lead['phone']:
        factors['contact_availability'] = 0.8
        recommendations.append("Phone available - easy to contact")
    else:
        factors['contact_availability'] = 0.4
        recommendations.append("No phone - harder to contact")
    
    # Calculate weighted score
    total_weight = 0
    weighted_score = 0
    
    for factor, value in factors.items():
        weight = criteria.get(factor, 0.1)  # Default weight
        weighted_score += value * weight
        total_weight += weight
    
    if total_weight > 0:
        final_score = weighted_score / total_weight
    else:
        final_score = 0.5  # Default score
    
    return final_score, factors, recommendations

@router.get("/scores/{job_id}", response_model=List[LeadScoreResponse], summary="Get lead scores for a job")
def get_lead_scores(
    job_id: int,
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Get previously calculated lead scores for a job"""
    try:
        # Verify job ownership
        job = db.query(Jobs).filter(Jobs.id == job_id, Jobs.user_id == user.id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Get saved scores
        scores = db.query(LeadScores).filter(LeadScores.job_id == job_id).all()
        
        return [
            LeadScoreResponse(
                lead_id=score.id,
                company_name=json.loads(score.lead_data).get('name', 'Unknown'),
                score=score.score,
        factors=json.loads(score.factors),
                recommendations=json.loads(score.recommendations)
            )
            for score in scores
        ]
        
    except Exception as e:
        logger.exception("Error getting lead scores")
        raise HTTPException(status_code=500, detail="Failed to get lead scores")

@router.get("/criteria", response_model=List[ScoringCriteria], summary="Get available scoring criteria")
def get_scoring_criteria():
    """Get available scoring criteria and their descriptions"""
    return [
        ScoringCriteria(
            name="company_size",
            weight=0.2,
            description="Company size based on employee count"
        ),
        ScoringCriteria(
            name="rating",
            weight=0.15,
            description="Google Maps rating (1-5 stars)"
        ),
        ScoringCriteria(
            name="engagement",
            weight=0.1,
            description="Customer engagement based on review count"
        ),
        ScoringCriteria(
            name="location",
            weight=0.15,
            description="Market location and potential"
        ),
        ScoringCriteria(
            name="online_presence",
            weight=0.1,
            description="Online presence and professionalism"
        ),
        ScoringCriteria(
            name="contact_availability",
            weight=0.1,
            description="Ease of contact and accessibility"
        )
    ] 
class BulkScoreResponseItem(BaseModel):
    lead_id: int
    overall_score: float
    risk_level: str
    conversion_probability: float

class BulkScoreResponse(BaseModel):
    results: List[BulkScoreResponseItem]

class ScoringStatsResponse(BaseModel):
    total_scored: int
    average_score: float
    high_risk_count: int
    low_risk_count: int
    conversion_rate: float

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

def calculate_company_score(lead: Leads) -> float:
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

def calculate_engagement_score(lead: Leads) -> float:
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

@router.post("/score", response_model=LeadScoreResponse, summary="Score a lead", description="Calculate or recalculate the score for a single lead.")
def score_lead(
    score_request: LeadScoreRequest,
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Calculate or recalculate the score for a single lead."""
    
    # Get the lead
    lead = db.query(Leads).filter(
        Leads.id == score_request.lead_id,
        Leads.user_id == user.id
    ).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Check if score already exists and recalculate is not requested
    existing_score = db.query(LeadScores).filter(
        LeadScores.lead_id == score_request.lead_id
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
        new_score = LeadScores(
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

@router.get("/leads/{lead_id}/score", response_model=LeadScoreResponse, summary="Get lead score", description="Get the score for a specific lead by ID.")
def get_lead_score(
    lead_id: int = Path(..., description="ID of the lead to retrieve score for."),
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Get the score for a specific lead by ID."""
    
    # Verify lead belongs to user
    lead = db.query(Leads).filter(
        Leads.id == lead_id,
        Leads.user_id == user.id
    ).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Get score
    score = db.query(LeadScores).filter(LeadScores.lead_id == lead_id).first()
    
    if not score:
        raise HTTPException(status_code=404, detail="Lead score not found")
    
    return LeadScoreResponse(
        lead_id=lead_id,
        overall_score=score.overall_score,
        factors=json.loads(score.factors),
        recommendations=json.loads(score.recommendations),
        risk_level=score.risk_level,
        conversion_probability=score.conversion_probability
    )

@router.get("/stats", response_model=ScoringStatsResponse, summary="Get scoring statistics", description="Get statistics about lead scoring for the current user.")
def get_scoring_stats(
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Get statistics about lead scoring for the current user."""
    
    # Get all scored leads for user
    scored_leads = db.query(LeadScores).join(Leads).filter(Leads.user_id == user.id).all()
    
    if not scored_leads:
        return ScoringStatsResponse(
            total_scored=0,
            average_score=0.0,
            high_risk_count=0,
            low_risk_count=0,
            conversion_rate=0.0
        )
    
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
    
    return ScoringStatsResponse(
        total_scored=total_scored,
        average_score=round(average_score, 3),
        high_risk_count=risk_distribution.get("high", 0) + risk_distribution.get("very_high", 0),
        low_risk_count=risk_distribution.get("low", 0),
        conversion_rate=round(sum(s.conversion_probability for s in scored_leads) / total_scored, 3)
    )

@router.post("/bulk-score", response_model=BulkScoreResponse, summary="Bulk score leads", description="Bulk score multiple leads by their IDs.")
def bulk_score_leads(
    bulk_request: BulkScoreRequest,
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Bulk score multiple leads by their IDs."""
    
    results = []
    
    for lead_id in bulk_request.lead_ids:
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
        new_score = LeadScores(
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

@router.get("/leads/{lead_id}/score", response_model=LeadScoreResponse, summary="Get lead score", description="Get the score for a specific lead by ID.")
def get_lead_score(
    lead_id: int = Path(..., description="ID of the lead to retrieve score for."),
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Get the score for a specific lead by ID."""
    
    # Verify lead belongs to user
    lead = db.query(Leads).filter(
        Leads.id == lead_id,
        Leads.user_id == user.id
    ).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Get score
    score = db.query(LeadScores).filter(LeadScores.lead_id == lead_id).first()
    
    if not score:
        raise HTTPException(status_code=404, detail="Lead score not found")
    
    return LeadScoreResponse(
        lead_id=lead_id,
        overall_score=score.overall_score,
        factors=json.loads(score.factors),
        recommendations=json.loads(score.recommendations),
        risk_level=score.risk_level,
        conversion_probability=score.conversion_probability
    )

@router.get("/stats", response_model=ScoringStatsResponse, summary="Get scoring statistics", description="Get statistics about lead scoring for the current user.")
def get_scoring_stats(
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Get statistics about lead scoring for the current user."""
    
    # Get all scored leads for user
    scored_leads = db.query(LeadScores).join(Leads).filter(Leads.user_id == user.id).all()
    
    if not scored_leads:
        return ScoringStatsResponse(
            total_scored=0,
            average_score=0.0,
            high_risk_count=0,
            low_risk_count=0,
            conversion_rate=0.0
        )
    
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
    
    return ScoringStatsResponse(
        total_scored=total_scored,
        average_score=round(average_score, 3),
        high_risk_count=risk_distribution.get("high", 0) + risk_distribution.get("very_high", 0),
        low_risk_count=risk_distribution.get("low", 0),
        conversion_rate=round(sum(s.conversion_probability for s in scored_leads) / total_scored, 3)
    )

@router.post("/bulk-score", response_model=BulkScoreResponse, summary="Bulk score leads", description="Bulk score multiple leads by their IDs.")
def bulk_score_leads(
    bulk_request: BulkScoreRequest,
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Bulk score multiple leads by their IDs."""
    
    results = []
    
    for lead_id in bulk_request.lead_ids:
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