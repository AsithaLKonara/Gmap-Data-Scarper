# Enhanced Analytics with Real-time Data and Advanced Reporting
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Body, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
import json
import logging
from datetime import datetime, timezone, timedelta
from models import Users, Jobs, LeadScores, WhatsAppWorkflows, Leads
from database import get_db
from auth import get_current_user
from security import check_permission
from cache import cache_result

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

logger = logging.getLogger("enhanced_analytics")

class AnalyticsSummary(BaseModel):
    total_jobs: int
    total_leads: int
    success_rate: float
    average_score: float
    top_performing_queries: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]

class RealTimeMetrics(BaseModel):
    active_jobs: int
    jobs_completed_today: int
    leads_generated_today: int
    average_response_time: float
    system_health: str

class PerformanceReport(BaseModel):
    period: str
    jobs_created: int
    jobs_completed: int
    leads_generated: int
    success_rate: float
    average_lead_score: float
    revenue_potential: float

@router.get("/summary", response_model=AnalyticsSummary, summary="Get analytics summary")
@cache_result(ttl_seconds=300, key_prefix="analytics")
def get_analytics_summary(
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Get comprehensive analytics summary for the user"""
    try:
        # Check permissions
        if not check_permission(user, "analytics:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get user's jobs
        user_jobs = db.query(Jobs).filter(Jobs.user_id == user.id).all()
        total_jobs = len(user_jobs)
        
        # Calculate total leads
        total_leads = 0
        for job in user_jobs:
            if job.results:
                results = json.loads(job.results)
                total_leads += len(results)
        
        # Calculate success rate
        completed_jobs = [job for job in user_jobs if job.status == "completed"]
        success_rate = len(completed_jobs) / total_jobs if total_jobs > 0 else 0
        
        # Calculate average lead score
        lead_scores = db.query(LeadScores).filter(LeadScores.user_id == user.id).all()
        average_score = sum(score.score for score in lead_scores) / len(lead_scores) if lead_scores else 0
        
        # Get top performing queries
        query_performance = {}
        for job in user_jobs:
            if job.queries:
                queries = json.loads(job.queries)
                for query in queries:
                    if query not in query_performance:
                        query_performance[query] = {"count": 0, "success_rate": 0}
                    query_performance[query]["count"] += 1
                    if job.status == "completed":
                        query_performance[query]["success_rate"] += 1
        
        # Sort by success rate and count
        top_queries = sorted(
            [{"query": q, **stats} for q, stats in query_performance.items()],
            key=lambda x: (x["success_rate"], x["count"]),
            reverse=True
        )[:5]
        
        # Get recent activity
        recent_jobs = db.query(Jobs).filter(
            Jobs.user_id == user.id
        ).order_by(desc(Jobs.created_at)).limit(10).all()
        
        recent_activity = []
        for job in recent_jobs:
            recent_activity.append({
                "id": job.id,
                "type": "job_created",
                "status": job.status,
                "created_at": job.created_at.isoformat(),
                "queries_count": len(json.loads(job.queries)) if job.queries else 0
            })
        
        return AnalyticsSummary(
            total_jobs=total_jobs,
            total_leads=total_leads,
            success_rate=round(success_rate * 100, 2),
            average_score=round(average_score, 2),
            top_performing_queries=top_queries,
            recent_activity=recent_activity
        )
        
    except Exception as e:
        logger.exception("Error getting analytics summary")
        raise HTTPException(status_code=500, detail="Failed to get analytics summary")

@router.get("/realtime", response_model=RealTimeMetrics, summary="Get real-time metrics")
def get_realtime_metrics(
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Get real-time system metrics"""
    try:
        # Active jobs (running or pending)
        active_jobs = db.query(Jobs).filter(
            and_(
                Jobs.user_id == user.id,
                Jobs.status.in_(["running", "pending"])
            )
        ).count()
        
        # Jobs completed today
        today = datetime.now(timezone.utc).date()
        jobs_completed_today = db.query(Jobs).filter(
            and_(
                Jobs.user_id == user.id,
                Jobs.status == "completed",
                func.date(Jobs.updated_at) == today
            )
        ).count()
        
        # Leads generated today
        leads_generated_today = 0
        today_jobs = db.query(Jobs).filter(
            and_(
                Jobs.user_id == user.id,
                func.date(Jobs.updated_at) == today
            )
        ).all()
        
        for job in today_jobs:
            if job.results:
                results = json.loads(job.results)
                leads_generated_today += len(results)
        
        # Calculate average response time (simplified)
        completed_jobs = db.query(Jobs).filter(
            and_(
                Jobs.user_id == user.id,
                Jobs.status == "completed"
            )
        ).all()
        
        total_time = 0
        count = 0
        for job in completed_jobs:
            if job.created_at and job.updated_at:
                duration = (job.updated_at - job.created_at).total_seconds()
                total_time += duration
                count += 1
        
        average_response_time = total_time / count if count > 0 else 0
        
        # System health (simplified)
        system_health = "healthy"
        if active_jobs > 10:
            system_health = "busy"
        elif active_jobs == 0 and jobs_completed_today == 0:
            system_health = "idle"
        
        return RealTimeMetrics(
            active_jobs=active_jobs,
            jobs_completed_today=jobs_completed_today,
            leads_generated_today=leads_generated_today,
            average_response_time=round(average_response_time, 2),
            system_health=system_health
        )
        
    except Exception as e:
        logger.exception("Error getting real-time metrics")
        raise HTTPException(status_code=500, detail="Failed to get real-time metrics")

@router.get("/performance", response_model=List[PerformanceReport], summary="Get performance reports")
def get_performance_reports(
    period: str = Query("7d", description="Time period: 1d, 7d, 30d, 90d"),
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Get performance reports for different time periods"""
    try:
        # Parse period
        period_map = {
            "1d": 1,
            "7d": 7,
            "30d": 30,
            "90d": 90
        }
        
        days = period_map.get(period, 7)
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Get jobs in period
        period_jobs = db.query(Jobs).filter(
            and_(
                Jobs.user_id == user.id,
                Jobs.created_at >= start_date
            )
        ).all()
        
        jobs_created = len(period_jobs)
        jobs_completed = len([j for j in period_jobs if j.status == "completed"])
        
        # Calculate leads generated
        leads_generated = 0
        for job in period_jobs:
            if job.results:
                results = json.loads(job.results)
                leads_generated += len(results)
        
        # Calculate success rate
        success_rate = jobs_completed / jobs_created if jobs_created > 0 else 0
        
        # Calculate average lead score
        period_scores = db.query(LeadScores).filter(
            and_(
                LeadScores.user_id == user.id,
                LeadScores.created_at >= start_date
            )
        ).all()
        
        average_lead_score = sum(score.score for score in period_scores) / len(period_scores) if period_scores else 0
        
        # Calculate revenue potential (simplified)
        revenue_potential = leads_generated * average_lead_score * 100  # $100 per lead
        
        return [PerformanceReport(
            period=period,
            jobs_created=jobs_created,
            jobs_completed=jobs_completed,
            leads_generated=leads_generated,
            success_rate=round(success_rate * 100, 2),
            average_lead_score=round(average_lead_score, 2),
            revenue_potential=round(revenue_potential, 2)
        )]
        
    except Exception as e:
        logger.exception("Error getting performance reports")
        raise HTTPException(status_code=500, detail="Failed to get performance reports")

@router.get("/export", summary="Export analytics data")
def export_analytics_data(
    format: str = Query("csv", description="Export format: csv, json, xlsx"),
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Export analytics data in various formats"""
    try:
        # Get user's analytics data
        summary = get_analytics_summary(db, user)
        realtime = get_realtime_metrics(db, user)
        performance = get_performance_reports("30d", db, user)
        
        data = {
            "summary": summary.dict(),
            "realtime": realtime.dict(),
            "performance": [p.dict() for p in performance],
            "exported_at": datetime.now(timezone.utc).isoformat()
        }
        
        if format == "json":
            return data
        elif format == "csv":
            # Convert to CSV format (simplified)
            csv_data = "Metric,Value\n"
            csv_data += f"Total Jobs,{summary.total_jobs}\n"
            csv_data += f"Total Leads,{summary.total_leads}\n"
            csv_data += f"Success Rate,{summary.success_rate}%\n"
            csv_data += f"Average Score,{summary.average_score}\n"
            return {"csv": csv_data}
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
            
    except Exception as e:
        logger.exception("Error exporting analytics data")
        raise HTTPException(status_code=500, detail="Failed to export analytics data") 
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
    user: Users = Depends(get_current_user)
):
    """Create a new analytics goal for the current user."""
    # Calculate current progress based on goal type
    current_value = calculate_current_value(user.id, goal_data.goal_type, goal_data.period, db)
    goal = Goals(
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
    user: Users = Depends(get_current_user)
):
    """Get all analytics goals for the current user."""
    goals = db.query(Goals).filter(Goals.user_id == user.id).all()
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
    user: Users = Depends(get_current_user)
):
    """Update an existing analytics goal for the current user."""
    goal = db.query(Goals).filter(
        Goals.id == goal_id,
        Goals.user_id == user.id
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
    user: Users = Depends(get_current_user)
):
    """Delete an analytics goal for the current user."""
    goal = db.query(Goals).filter(
        Goals.id == goal_id,
        Goals.user_id == user.id
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
    user: Users = Depends(get_current_user)
):
    """Get conversion funnel analysis for the current user."""
    # Calculate funnel stages
    total_jobs = db.query(Jobs).filter(Jobs.user_id == user.id).count()
    completed_jobs = db.query(Jobs).filter(
        Jobs.user_id == user.id,
        Jobs.status == 'completed'
    ).count()
    total_leads = db.query(Leads).filter(Leads.user_id == user.id).count()
    crm_leads = db.query(Leads).filter(
        Leads.user_id == user.id,
        Leads.status.in_(['new', 'contacted', 'qualified', 'converted'])
    ).count()
    # Estimate exports (jobs with results)
    exported_jobs = db.query(Jobs).filter(
        Jobs.user_id == user.id,
        Jobs.status == 'completed'
    ).count()  # Simplified - assume completed jobs are exported
    # Estimate conversions (leads with status 'converted')
    converted_leads = db.query(Leads).filter(
        Leads.user_id == user.id,
        Leads.status == 'converted'
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
    user: Users = Depends(get_current_user)
):
    """Get personalized analytics insights"""
    
    insights = []
    
    # Get user statistics
    total_jobs = db.query(Jobs).filter(Jobs.user_id == user.id).count()
    completed_jobs = db.query(Jobs).filter(
        Jobs.user_id == user.id,
        Jobs.status == 'completed'
    ).count()
    
    total_leads = db.query(Leads).filter(Leads.user_id == user.id).count()
    converted_leads = db.query(Leads).filter(
        Leads.user_id == user.id,
        Leads.status == 'converted'
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
    recent_jobs = db.query(Jobs).filter(
        Jobs.user_id == user.id,
        Jobs.created_at >= datetime.utcnow() - timedelta(days=7)
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
    user: Users = Depends(get_current_user)
):
    """Get analytics trends over time"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get daily job counts
    daily_jobs = db.query(
        db.func.date(Jobs.created_at).label('date'),
        db.func.count(Jobs.id).label('count')
    ).filter(
        Jobs.user_id == user.id,
        Jobs.created_at >= start_date
    ).group_by(db.func.date(Jobs.created_at)).all()
    
    # Get daily lead counts
    daily_leads = db.query(
        db.func.date(Leads.created_at).label('date'),
        db.func.count(Leads.id).label('count')
    ).filter(
        Leads.user_id == user.id,
        Leads.created_at >= start_date
    ).group_by(db.func.date(Leads.created_at)).all()
    
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
        return db.query(Leads).filter(
            Leads.user_id == user_id,
            Leads.created_at >= start_date
        ).count()
    
    elif goal_type == GoalType.JOBS:
        return db.query(Jobs).filter(
            Jobs.user_id == user_id,
            Jobs.created_at >= start_date
        ).count()
    
    elif goal_type == GoalType.EXPORTS:
        # Simplified - count completed jobs as exports
        return db.query(Jobs).filter(
            Jobs.user_id == user_id,
            Jobs.status == 'completed',
            Jobs.created_at >= start_date
        ).count()
    
    elif goal_type == GoalType.REVENUE:
        # Simplified revenue calculation based on leads
        leads = db.query(Leads).filter(
            Leads.user_id == user_id,
            Leads.created_at >= start_date
        ).count()
        # Assume $50 average value per lead
        return leads * 50.0
    
    return 0.0 