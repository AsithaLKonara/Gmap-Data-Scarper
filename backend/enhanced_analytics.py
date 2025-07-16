from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from models import User, Goal, AnalyticsEvent, Job, Lead
from database import get_db
from auth import get_current_user
import json
from datetime import datetime, timedelta
from enum import Enum

router = APIRouter(prefix="/api/analytics", tags=["enhanced-analytics"])

class GoalType(str, Enum):
    """Type of analytics goal."""
    LEADS = "leads"
    REVENUE = "revenue"
    JOBS = "jobs"
    EXPORTS = "exports"

class GoalPeriod(str, Enum):
    """Period for analytics goal."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class GoalCreate(BaseModel):
    name: str = Field(..., description="Goal name.", example="Close 10 deals")
    target: float = Field(..., description="Target value for the goal.", example=10)
    goal_type: GoalType = Field(..., description="Type of goal.", example="leads")
    period: GoalPeriod = Field(..., description="Goal period.", example="monthly")
    deadline: datetime = Field(..., description="Deadline for the goal.", example="2024-06-30T23:59:59Z")
    description: Optional[str] = Field(None, description="Goal description.", example="Achieve 10 new leads this month.")

class GoalResponse(BaseModel):
    id: int = Field(..., description="Goal ID.", example=1)
    name: str = Field(..., description="Goal name.", example="Close 10 deals")
    target: float = Field(..., description="Target value for the goal.", example=10)
    current: float = Field(..., description="Current progress value.", example=5)
    goal_type: str = Field(..., description="Type of goal.", example="leads")
    period: str = Field(..., description="Goal period.", example="monthly")
    deadline: datetime = Field(..., description="Deadline for the goal.", example="2024-06-30T23:59:59Z")
    progress_percentage: float = Field(..., description="Progress as a percentage.", example=50.0)
    completed: bool = Field(..., description="Whether the goal is completed.", example=False)
    created_at: datetime = Field(..., description="Goal creation timestamp.", example="2024-06-01T12:00:00Z")

class FunnelStage(BaseModel):
    stage: str = Field(..., description="Funnel stage name.", example="Jobs Created")
    count: int = Field(..., description="Count at this stage.", example=100)
    conversion_rate: float = Field(..., description="Conversion rate at this stage.", example=80.0)
    drop_off_rate: float = Field(..., description="Drop-off rate at this stage.", example=20.0)

class AnalyticsInsight(BaseModel):
    type: str = Field(..., description="Insight type.", example="performance")
    title: str = Field(..., description="Insight title.", example="Excellent Job Success Rate")
    description: str = Field(..., description="Insight description.", example="Your job success rate is 90%.")
    severity: str = Field(..., description="Severity level (info, warning, success, error).", example="success")
    action_required: bool = Field(..., description="Whether user action is required.", example=False)

class DeleteGoalResponse(BaseModel):
    status: str
    goal_id: int

@router.post(
    "/goals",
    response_model=GoalResponse,
    summary="Create a new analytics goal",
    description="Create a new analytics goal for the current user.",
    response_description="The created goal."
)
def create_goal(
    goal_data: GoalCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Create a new analytics goal for the current user."""
    # Calculate current progress based on goal type
    current_value = calculate_current_value(user.id, goal_data.goal_type, goal_data.period, db)
    goal = Goal(
        user_id=user.id,
        name=goal_data.name,
        target=goal_data.target,
        current=current_value,
        goal_type=goal_data.goal_type.value,
        period=goal_data.period.value,
        deadline=goal_data.deadline,
        description=goal_data.description,
        created_at=datetime.utcnow()
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    progress_percentage = min((goal.current / goal.target) * 100, 100) if goal.target > 0 else 0
    return GoalResponse(
        id=goal.id,
        name=goal.name,
        target=goal.target,
        current=goal.current,
        goal_type=goal.goal_type,
        period=goal.period,
        deadline=goal.deadline,
        progress_percentage=progress_percentage,
        completed=progress_percentage >= 100,
        created_at=goal.created_at
    )

@router.get(
    "/goals",
    response_model=List[GoalResponse],
    summary="Get analytics goals",
    description="Get all analytics goals for the current user.",
    response_description="List of goals."
)
def get_goals(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get all analytics goals for the current user."""
    goals = db.query(Goal).filter(Goal.user_id == user.id).all()
    result = []
    for goal in goals:
        # Update current value
        goal.current = calculate_current_value(user.id, GoalType(goal.goal_type), GoalPeriod(goal.period), db)
        progress_percentage = min((goal.current / goal.target) * 100, 100) if goal.target > 0 else 0
        result.append(GoalResponse(
            id=goal.id,
            name=goal.name,
            target=goal.target,
            current=goal.current,
            goal_type=goal.goal_type,
            period=goal.period,
            deadline=goal.deadline,
            progress_percentage=progress_percentage,
            completed=progress_percentage >= 100,
            created_at=goal.created_at
        ))
    return result

@router.put(
    "/goals/{goal_id}",
    summary="Update analytics goal",
    description="Update an existing analytics goal for the current user.",
    response_model=dict,
    response_description="Status and goal ID."
)
def update_goal(
    goal_id: int,
    goal_data: GoalCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Update an existing analytics goal for the current user."""
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == user.id
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    goal.name = goal_data.name
    goal.target = goal_data.target
    goal.goal_type = goal_data.goal_type.value
    goal.period = goal_data.period.value
    goal.deadline = goal_data.deadline
    goal.description = goal_data.description
    db.commit()
    return {"status": "updated", "goal_id": goal_id}

@router.delete(
    "/goals/{goal_id}",
    summary="Delete analytics goal",
    description="Delete an analytics goal for the current user.",
    response_model=DeleteGoalResponse,
    response_description="Status and goal ID."
)
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Delete an analytics goal for the current user."""
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == user.id
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(goal)
    db.commit()
    return DeleteGoalResponse(status="deleted", goal_id=goal_id)

@router.get(
    "/funnel",
    response_model=List[FunnelStage],
    summary="Get conversion funnel analysis",
    description="Get conversion funnel analysis for the current user.",
    response_description="List of funnel stages."
)
def get_conversion_funnel(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get conversion funnel analysis for the current user."""
    # Calculate funnel stages
    total_jobs = db.query(Job).filter(Job.user_id == user.id).count()
    completed_jobs = db.query(Job).filter(
        Job.user_id == user.id,
        Job.status == 'completed'
    ).count()
    total_leads = db.query(Lead).filter(Lead.user_id == user.id).count()
    crm_leads = db.query(Lead).filter(
        Lead.user_id == user.id,
        Lead.status.in_(['new', 'contacted', 'qualified', 'converted'])
    ).count()
    # Estimate exports (jobs with results)
    exported_jobs = db.query(Job).filter(
        Job.user_id == user.id,
        Job.status == 'completed'
    ).count()  # Simplified - assume completed jobs are exported
    # Estimate conversions (leads with status 'converted')
    converted_leads = db.query(Lead).filter(
        Lead.user_id == user.id,
        Lead.status == 'converted'
    ).count()
    funnel_stages = [
        FunnelStage(
            stage="Jobs Created",
            count=total_jobs,
            conversion_rate=100.0,
            drop_off_rate=0.0
        ),
        FunnelStage(
            stage="Jobs Completed",
            count=completed_jobs,
            conversion_rate=(completed_jobs / total_jobs * 100) if total_jobs > 0 else 0,
            drop_off_rate=((total_jobs - completed_jobs) / total_jobs * 100) if total_jobs > 0 else 0
        ),
        FunnelStage(
            stage="Leads Generated",
            count=total_leads,
            conversion_rate=(total_leads / completed_jobs * 100) if completed_jobs > 0 else 0,
            drop_off_rate=((completed_jobs - total_leads) / completed_jobs * 100) if completed_jobs > 0 else 0
        ),
        FunnelStage(
            stage="CRM Added",
            count=crm_leads,
            conversion_rate=(crm_leads / total_leads * 100) if total_leads > 0 else 0,
            drop_off_rate=((total_leads - crm_leads) / total_leads * 100) if total_leads > 0 else 0
        ),
        FunnelStage(
            stage="Exported",
            count=exported_jobs,
            conversion_rate=(exported_jobs / completed_jobs * 100) if completed_jobs > 0 else 0,
            drop_off_rate=((completed_jobs - exported_jobs) / completed_jobs * 100) if completed_jobs > 0 else 0
        ),
        FunnelStage(
            stage="Converted",
            count=converted_leads,
            conversion_rate=(converted_leads / total_leads * 100) if total_leads > 0 else 0,
            drop_off_rate=((total_leads - converted_leads) / total_leads * 100) if total_leads > 0 else 0
        )
    ]
    return funnel_stages

@router.get("/insights", response_model=List[AnalyticsInsight])
def get_analytics_insights(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get personalized analytics insights"""
    
    insights = []
    
    # Get user statistics
    total_jobs = db.query(Job).filter(Job.user_id == user.id).count()
    completed_jobs = db.query(Job).filter(
        Job.user_id == user.id,
        Job.status == 'completed'
    ).count()
    
    total_leads = db.query(Lead).filter(Lead.user_id == user.id).count()
    converted_leads = db.query(Lead).filter(
        Lead.user_id == user.id,
        Lead.status == 'converted'
    ).count()
    
    # Calculate metrics
    job_success_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
    conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
    
    # Generate insights based on performance
    if job_success_rate >= 80:
        insights.append(AnalyticsInsight(
            type="performance",
            title="Excellent Job Success Rate",
            description=f"Your job success rate is {job_success_rate:.1f}%, which is above industry average.",
            severity="success",
            action_required=False
        ))
    elif job_success_rate < 60:
        insights.append(AnalyticsInsight(
            type="performance",
            title="Job Success Rate Needs Improvement",
            description=f"Your job success rate is {job_success_rate:.1f}%. Consider optimizing your queries.",
            severity="warning",
            action_required=True
        ))
    
    if conversion_rate >= 10:
        insights.append(AnalyticsInsight(
            type="conversion",
            title="Strong Conversion Rate",
            description=f"Your lead conversion rate is {conversion_rate:.1f}%, which is excellent.",
            severity="success",
            action_required=False
        ))
    elif conversion_rate < 5:
        insights.append(AnalyticsInsight(
            type="conversion",
            title="Low Conversion Rate",
            description=f"Your conversion rate is {conversion_rate:.1f}%. Focus on lead quality and follow-up.",
            severity="warning",
            action_required=True
        ))
    
    # Plan-based insights
    if user.plan == "free" and total_jobs >= 20:
        insights.append(AnalyticsInsight(
            type="upgrade",
            title="Consider Upgrading",
            description="You're using LeadTap actively. Upgrade to Pro for higher limits and advanced features.",
            severity="info",
            action_required=False
        ))
    
    # Activity insights
    recent_jobs = db.query(Job).filter(
        Job.user_id == user.id,
        Job.created_at >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    if recent_jobs == 0:
        insights.append(AnalyticsInsight(
            type="activity",
            title="No Recent Activity",
            description="You haven't created any jobs in the last 7 days. Consider running a new search.",
            severity="warning",
            action_required=True
        ))
    
    return insights

@router.get("/trends")
def get_analytics_trends(
    days: int = 30,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get analytics trends over time"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get daily job counts
    daily_jobs = db.query(
        db.func.date(Job.created_at).label('date'),
        db.func.count(Job.id).label('count')
    ).filter(
        Job.user_id == user.id,
        Job.created_at >= start_date
    ).group_by(db.func.date(Job.created_at)).all()
    
    # Get daily lead counts
    daily_leads = db.query(
        db.func.date(Lead.created_at).label('date'),
        db.func.count(Lead.id).label('count')
    ).filter(
        Lead.user_id == user.id,
        Lead.created_at >= start_date
    ).group_by(db.func.date(Lead.created_at)).all()
    
    # Format data for charts
    job_trends = [{"date": str(job.date), "count": job.count} for job in daily_jobs]
    lead_trends = [{"date": str(lead.date), "count": lead.count} for lead in daily_leads]
    
    return {
        "period_days": days,
        "job_trends": job_trends,
        "lead_trends": lead_trends
    }

def calculate_current_value(user_id: int, goal_type: GoalType, period: GoalPeriod, db: Session) -> float:
    """Calculate current value for a goal based on type and period"""
    
    now = datetime.utcnow()
    
    if period == GoalPeriod.DAILY:
        start_date = now - timedelta(days=1)
    elif period == GoalPeriod.WEEKLY:
        start_date = now - timedelta(weeks=1)
    else:  # MONTHLY
        start_date = now - timedelta(days=30)
    
    if goal_type == GoalType.LEADS:
        return db.query(Lead).filter(
            Lead.user_id == user_id,
            Lead.created_at >= start_date
        ).count()
    
    elif goal_type == GoalType.JOBS:
        return db.query(Job).filter(
            Job.user_id == user_id,
            Job.created_at >= start_date
        ).count()
    
    elif goal_type == GoalType.EXPORTS:
        # Simplified - count completed jobs as exports
        return db.query(Job).filter(
            Job.user_id == user_id,
            Job.status == 'completed',
            Job.created_at >= start_date
        ).count()
    
    elif goal_type == GoalType.REVENUE:
        # Simplified revenue calculation based on leads
        leads = db.query(Lead).filter(
            Lead.user_id == user_id,
            Lead.created_at >= start_date
        ).count()
        # Assume $50 average value per lead
        return leads * 50.0
    
    return 0.0 