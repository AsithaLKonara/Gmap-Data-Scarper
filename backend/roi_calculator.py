from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from models import Users, Plans
from database import get_db
from auth import get_current_user
import json
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/roi", tags=["roi-calculator"])

class ROICalculation(BaseModel):
    current_leads_per_month: int
    conversion_rate: float  # percentage
    average_deal_value: float
    cost_per_lead: float
    monthly_budget: float
    plan_type: str

class PlanComparison(BaseModel):
    plan_name: str
    monthly_cost: float
    features: List[str]
    lead_limit: int
    export_formats: List[str]
    support_level: str

class ROIResult(BaseModel):
    current_roi: float
    projected_roi: float
    payback_period_months: float
    monthly_revenue: float
    monthly_profit: float
    breakeven_point: int  # number of leads needed
    recommendations: List[str]

PLAN_FEATURES = {
    "free": {
        "monthly_cost": 0,
        "lead_limit": 30,
        "export_formats": ["csv"],
        "support_level": "email",
        "features": ["Basic scraping", "CSV export", "Email support"]
    },
    "pro": {
        "monthly_cost": 29,
        "lead_limit": 1000,
        "export_formats": ["csv", "json", "xlsx"],
        "support_level": "priority_email",
        "features": ["Advanced scraping", "Multiple exports", "API access", "Priority support"]
    },
    "business": {
        "monthly_cost": 99,
        "lead_limit": 10000,
        "export_formats": ["csv", "json", "xlsx", "pdf"],
        "support_level": "phone",
        "features": ["Enterprise features", "All exports", "White-label", "Phone support"]
    }
}

@router.post("/calculate", response_model=ROIResult)
def calculate_roi(
    calculation: ROICalculation,
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Calculate ROI for lead generation"""
    
    # Validate inputs
    if calculation.conversion_rate < 0 or calculation.conversion_rate > 100:
        raise HTTPException(status_code=400, detail="Conversion rate must be between 0 and 100")
    
    if calculation.average_deal_value <= 0:
        raise HTTPException(status_code=400, detail="Average deal value must be positive")
    
    # Calculate current metrics
    monthly_revenue = calculation.current_leads_per_month * (calculation.conversion_rate / 100) * calculation.average_deal_value
    monthly_cost = calculation.current_leads_per_month * calculation.cost_per_lead
    current_roi = ((monthly_revenue - monthly_cost) / monthly_cost * 100) if monthly_cost > 0 else 0
    
    # Get plan features
    plan_features = PLAN_FEATURES.get(calculation.plan_type, PLAN_FEATURES["free"])
    
    # Calculate projected metrics with LeadTap
    # Assume LeadTap reduces cost per lead by 60% and increases conversion rate by 20%
    improved_cost_per_lead = calculation.cost_per_lead * 0.4  # 60% reduction
    improved_conversion_rate = calculation.conversion_rate * 1.2  # 20% improvement
    
    # Calculate potential leads with LeadTap (based on plan limits)
    potential_leads = min(plan_features["lead_limit"], calculation.current_leads_per_month * 2)
    
    projected_revenue = potential_leads * (improved_conversion_rate / 100) * calculation.average_deal_value
    projected_cost = potential_leads * improved_cost_per_lead + plan_features["monthly_cost"]
    projected_roi = ((projected_revenue - projected_cost) / projected_cost * 100) if projected_cost > 0 else 0
    
    # Calculate payback period
    monthly_profit = projected_revenue - projected_cost
    payback_period = plan_features["monthly_cost"] / monthly_profit if monthly_profit > 0 else float('inf')
    
    # Calculate breakeven point
    breakeven_leads = plan_features["monthly_cost"] / (improved_cost_per_lead - calculation.cost_per_lead) if improved_cost_per_lead < calculation.cost_per_lead else 0
    
    # Generate recommendations
    recommendations = []
    
    if projected_roi > current_roi:
        recommendations.append(f"Upgrade to {calculation.plan_type.title()} plan for {projected_roi:.1f}% ROI")
    
    if payback_period < 3:
        recommendations.append("Quick payback period - consider upgrading for faster ROI")
    
    if breakeven_leads < potential_leads:
        recommendations.append(f"Breakeven at {breakeven_leads:.0f} leads - easily achievable")
    
    if calculation.plan_type == "free":
        recommendations.append("Consider Pro plan for advanced features and higher limits")
    
    return ROIResult(
        current_roi=current_roi,
        projected_roi=projected_roi,
        payback_period_months=payback_period,
        monthly_revenue=projected_revenue,
        monthly_profit=monthly_profit,
        breakeven_point=int(breakeven_leads),
        recommendations=recommendations
    )

@router.get("/plans", response_model=List[PlanComparison])
def get_plan_comparisons():
    """Get detailed plan comparisons for ROI analysis"""
    comparisons = []
    
    for plan_name, features in PLAN_FEATURES.items():
        comparisons.append(PlanComparison(
            plan_name=plan_name.title(),
            monthly_cost=features["monthly_cost"],
            features=features["features"],
            lead_limit=features["lead_limit"],
            export_formats=features["export_formats"],
            support_level=features["support_level"]
        ))
    
    return comparisons

@router.get("/user-stats")
def get_user_roi_stats(
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Get user's current ROI statistics"""
    
    # Get user's job and lead statistics
    total_jobs = db.query(user.jobs).count()
    completed_jobs = db.query(user.jobs).filter(user.jobs.any(status='completed')).count()
    total_leads = db.query(user.leads).count()
    
    # Calculate basic metrics
    success_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
    
    # Estimate ROI based on user's plan and usage
    plan_features = PLAN_FEATURES.get(user.plan, PLAN_FEATURES["free"])
    
    # Simple ROI calculation based on plan value
    if user.plan == "free":
        estimated_roi = 0  # Free plan has no cost
    else:
        # Assume user gets value worth 3x the plan cost
        plan_value = plan_features["monthly_cost"] * 3
        estimated_roi = ((plan_value - plan_features["monthly_cost"]) / plan_features["monthly_cost"] * 100) if plan_features["monthly_cost"] > 0 else 0
    
    return {
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs,
        "success_rate": round(success_rate, 2),
        "total_leads": total_leads,
        "current_plan": user.plan,
        "plan_cost": plan_features["monthly_cost"],
        "estimated_roi": round(estimated_roi, 2),
        "plan_features": plan_features["features"]
    }

@router.post("/upgrade-recommendation")
def get_upgrade_recommendation(
    current_usage: Dict[str, Any],
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Get personalized upgrade recommendation based on usage"""
    
    recommendations = []
    
    # Check if user is approaching limits
    if user.plan == "free":
        if current_usage.get("jobs_this_month", 0) >= 25:
            recommendations.append({
                "type": "limit_reached",
                "plan": "pro",
                "reason": "You're approaching the free plan job limit",
                "benefit": "Unlimited jobs and advanced features"
            })
        
        if current_usage.get("leads_this_month", 0) >= 25:
            recommendations.append({
                "type": "limit_reached",
                "plan": "pro",
                "reason": "You're approaching the free plan lead limit",
                "benefit": "Higher lead limits and export options"
            })
    
    elif user.plan == "pro":
        if current_usage.get("jobs_this_month", 0) >= 400:
            recommendations.append({
                "type": "limit_reached",
                "plan": "business",
                "reason": "You're approaching the pro plan job limit",
                "benefit": "Enterprise features and team management"
            })
    
    # Check for feature usage that suggests upgrade
    if current_usage.get("api_calls", 0) > 100 and user.plan == "free":
        recommendations.append({
            "type": "feature_usage",
            "plan": "pro",
            "reason": "High API usage detected",
            "benefit": "API access and advanced integrations"
        })
    
    # Check for team features
    if current_usage.get("team_members", 0) > 0 and user.plan != "business":
        recommendations.append({
            "type": "team_management",
            "plan": "business",
            "reason": "Team management features needed",
            "benefit": "Advanced team management and collaboration"
        })
    
    return {
        "current_plan": user.plan,
        "recommendations": recommendations,
        "upgrade_benefits": PLAN_FEATURES.get(user.plan, {}).get("features", [])
    } 