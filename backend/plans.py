from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
from datetime import datetime, timedelta
from database import get_db
from models import User, Plan, SystemLog
from auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/plans", tags=["plans"])

class PlanResponse(BaseModel):
    id: int
    name: str
    display_name: str
    description: Optional[str]
    price_monthly: Optional[float]
    price_yearly: Optional[float]
    max_queries_per_day: int
    max_results_per_query: int
    features: List[str]
    limits: dict
    is_active: bool

class PlanLimitsResponse(BaseModel):
    max_queries_per_day: int
    max_results_per_query: int
    queries_used_today: int
    queries_remaining_today: int
    plan_name: str
    subscription_status: str
    subscription_end: Optional[datetime]

PLAN_LIMITS = {
    'free': {'max_queries_per_day': 10, 'max_results_per_query': 5, 'plan_name': 'free', 'price': 0, 'features': ['Basic scraping', 'CSV export', 'Email support']},
    'pro': {'max_queries_per_day': 100, 'max_results_per_query': 50, 'plan_name': 'pro', 'price': 29, 'features': ['Advanced scraping', 'Multiple exports', 'API access', 'Priority support']},
    'business': {'max_queries_per_day': 1000, 'max_results_per_query': 200, 'plan_name': 'business', 'price': 99, 'features': ['Enterprise features', 'All exports', 'White-label', 'Phone support']}
}

class PlanLimits(BaseModel):
    max_queries_per_day: int
    max_results_per_query: int
    queries_used_today: int
    queries_remaining_today: int
    plan_name: str
    subscription_status: str
    subscription_end: str = None

class PlanComparison(BaseModel):
    plan_name: str
    price: float
    features: List[str]
    max_queries_per_day: int
    max_results_per_query: int

@router.get("/", response_model=List[PlanResponse])
async def get_plans(db: Session = Depends(get_db)):
    """Get all available plans"""
    plans = db.query(Plan).filter(Plan.is_active == True).all()
    
    result = []
    for plan in plans:
        features = json.loads(plan.features) if plan.features else []
        limits = json.loads(plan.limits) if plan.limits else {}
        
        result.append(PlanResponse(
            id=plan.id,
            name=plan.name,
            display_name=plan.display_name,
            description=plan.description,
            price_monthly=plan.price_monthly,
            price_yearly=plan.price_yearly,
            max_queries_per_day=plan.max_queries_per_day,
            max_results_per_query=plan.max_results_per_query,
            features=features,
            limits=limits,
            is_active=plan.is_active
        ))
    
    return result

@router.get("/current", response_model=PlanLimitsResponse)
async def get_current_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's plan and usage limits"""
    # Get user's plan
    plan = db.query(Plan).filter(Plan.name == current_user.plan).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Calculate usage
    today = datetime.utcnow().date()
    if current_user.last_query_date and current_user.last_query_date.date() == today:
        queries_used_today = current_user.queries_today
    else:
        queries_used_today = 0
    
    queries_remaining_today = max(0, plan.max_queries_per_day - queries_used_today)
    
    return PlanLimitsResponse(
        max_queries_per_day=plan.max_queries_per_day,
        max_results_per_query=plan.max_results_per_query,
        queries_used_today=queries_used_today,
        queries_remaining_today=queries_remaining_today,
        plan_name=current_user.plan,
        subscription_status=current_user.subscription_status,
        subscription_end=current_user.subscription_end
    )

@router.post("/upgrade")
async def upgrade_plan(
    plan_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upgrade user's plan (simplified - in real app would integrate with Stripe)"""
    # Check if plan exists
    plan = db.query(Plan).filter(Plan.name == plan_name, Plan.is_active == True).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Update user's plan
    current_user.plan = plan_name
    current_user.subscription_status = "active"
    current_user.subscription_start = datetime.utcnow()
    current_user.subscription_end = datetime.utcnow() + timedelta(days=30)  # 30-day trial
    
    db.commit()
    
    # Log the upgrade
    log = SystemLog(
        level="INFO",
        module="plans",
        message=f"User {current_user.email} upgraded to {plan_name} plan",
        details=json.dumps({"old_plan": current_user.plan, "new_plan": plan_name}),
        user_id=current_user.id
    )
    db.add(log)
    db.commit()
    
    return {"message": f"Successfully upgraded to {plan_name} plan"}

@router.get("/limits", response_model=PlanLimits)
def get_plan_limits(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    plan = user.plan or 'free'
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS['free'])
    now = datetime.utcnow()
    # Reset daily usage if new day
    if not user.last_query_date or user.last_query_date.date() != now.date():
        user.queries_today = 0
        user.last_query_date = now
        db.commit()
    queries_used_today = user.queries_today or 0
    queries_remaining_today = max(0, limits['max_queries_per_day'] - queries_used_today)
    return PlanLimits(
        max_queries_per_day=limits['max_queries_per_day'],
        max_results_per_query=limits['max_results_per_query'],
        queries_used_today=queries_used_today,
        queries_remaining_today=queries_remaining_today,
        plan_name=limits['plan_name'],
        subscription_status=user.subscription_status or 'active',
        subscription_end=str(user.subscription_end) if user.subscription_end else None
    )

@router.get("/compare", response_model=List[PlanComparison])
def compare_plans():
    """Get plan comparison for pricing page and upgrade modal."""
    return [
        PlanComparison(
            plan_name=limits['plan_name'],
            price=limits['price'],
            features=limits['features'],
            max_queries_per_day=limits['max_queries_per_day'],
            max_results_per_query=limits['max_results_per_query']
        )
        for limits in PLAN_LIMITS.values()
    ]

@router.post("/check-limit")
async def check_job_limit(
    queries: List[str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if user can create a job with given queries"""
    plan = db.query(Plan).filter(Plan.name == current_user.plan).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Check daily limit
    today = datetime.utcnow().date()
    if current_user.last_query_date and current_user.last_query_date.date() == today:
        queries_used_today = current_user.queries_today
    else:
        queries_used_today = 0
    
    total_queries = len(queries)
    if queries_used_today + total_queries > plan.max_queries_per_day:
        raise HTTPException(
            status_code=400, 
            detail=f"Daily limit exceeded. You can only create {plan.max_queries_per_day - queries_used_today} more queries today."
        )
    
    # Check results per query limit
    for query in queries:
        if len(query) > 1000:  # Example limit
            raise HTTPException(
                status_code=400,
                detail="Query too long. Maximum 1000 characters per query."
            )
    
    return {
        "can_create": True,
        "queries_used_today": queries_used_today,
        "queries_remaining_today": plan.max_queries_per_day - queries_used_today,
        "total_queries_requested": total_queries
    }

def initialize_default_plans(db: Session):
    """Initialize default plans if they don't exist"""
    default_plans = [
        {
            "name": "free",
            "display_name": "Free",
            "description": "Basic Google Maps scraping, CSV export, Email support, Basic search filters",
            "price_monthly": 0,
            "price_yearly": 0,
            "max_queries_per_day": 10,
            "max_results_per_query": 10,
            "features": json.dumps([
                "Basic Google Maps scraping",
                "CSV export format",
                "Email support",
                "Basic search filters"
            ]),
            "limits": json.dumps({
                "max_queries_per_day": 10,
                "max_results_per_query": 10,
                "export_formats": ["csv"],
                "crm_leads": 20
            }),
            "is_active": True
        },
        {
            "name": "pro",
            "display_name": "Pro",
            "description": "Advanced scraping, CSV/JSON/Excel export, Priority email support, Advanced filters, API access, Data validation",
            "price_monthly": 9,
            "price_yearly": 90,
            "max_queries_per_day": 100,
            "max_results_per_query": 100,
            "features": json.dumps([
                "Advanced scraping capabilities",
                "CSV, JSON, Excel export",
                "Priority email support",
                "Advanced search filters",
                "API access",
                "Data validation"
            ]),
            "limits": json.dumps({
                "max_queries_per_day": 100,
                "max_results_per_query": 100,
                "export_formats": ["csv", "json", "xlsx"],
                "crm_leads": 1000,
                "api_access": True
            }),
            "is_active": True
        },
        {
            "name": "business",
            "display_name": "Business",
            "description": "Enterprise scraping, All export formats, 24/7 phone support, Custom integrations, White-label, Dedicated manager",
            "price_monthly": 49,
            "price_yearly": 490,
            "max_queries_per_day": 1000000,  # Effectively unlimited
            "max_results_per_query": 10000,
            "features": json.dumps([
                "Enterprise-level scraping",
                "All export formats",
                "24/7 phone support",
                "Custom integrations",
                "White-label options",
                "Dedicated account manager"
            ]),
            "limits": json.dumps({
                "max_queries_per_day": 1000000,
                "max_results_per_query": 10000,
                "export_formats": ["csv", "json", "xlsx", "pdf"],
                "crm_leads": 100000,
                "api_access": True,
                "phone_support": True,
                "custom_integrations": True,
                "white_label": True,
                "dedicated_manager": True
            }),
            "is_active": True
        }
    ]
    for plan_data in default_plans:
        existing_plan = db.query(Plan).filter(Plan.name == plan_data["name"]).first()
        if not existing_plan:
            plan = Plan(**plan_data)
            db.add(plan)
    db.commit() 