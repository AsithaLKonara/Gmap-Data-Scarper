from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from models import User, OnboardingStep, DemoProject
from database import get_db
from auth import get_current_user
import json
from datetime import datetime

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])

class OnboardingStepUpdate(BaseModel):
    step_id: str
    completed: bool
    data: Optional[Dict[str, Any]] = None

class DemoProjectCreate(BaseModel):
    name: str
    description: str
    queries: List[str]
    tags: Optional[List[str]] = None

class OnboardingProgress(BaseModel):
    user_id: int
    current_step: str
    completed_steps: List[str]
    total_steps: int
    progress_percentage: float
    estimated_time_remaining: int  # minutes

@router.get("/progress", response_model=OnboardingProgress)
def get_onboarding_progress(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get user's onboarding progress"""
    steps = db.query(OnboardingStep).filter(OnboardingStep.user_id == user.id).all()
    
    if not steps:
        # Initialize onboarding steps for new user
        default_steps = [
            {"step_id": "welcome", "name": "Welcome", "description": "Get started with LeadTap"},
            {"step_id": "profile", "name": "Complete Profile", "description": "Set up your profile"},
            {"step_id": "first_job", "name": "Create First Job", "description": "Create your first scraping job"},
            {"step_id": "demo_project", "name": "Demo Project", "description": "Try our demo project"},
            {"step_id": "crm_setup", "name": "CRM Setup", "description": "Connect your CRM"},
            {"step_id": "analytics", "name": "Analytics Tour", "description": "Explore analytics features"},
            {"step_id": "complete", "name": "Onboarding Complete", "description": "You're all set!"}
        ]
        
        for step_data in default_steps:
            step = OnboardingStep(
                user_id=user.id,
                step_id=step_data["step_id"],
                name=step_data["name"],
                description=step_data["description"],
                completed=False,
                data=None
            )
            db.add(step)
        
        db.commit()
        steps = db.query(OnboardingStep).filter(OnboardingStep.user_id == user.id).all()
    
    completed_steps = [step.step_id for step in steps if step.completed]
    total_steps = len(steps)
    progress_percentage = (len(completed_steps) / total_steps) * 100 if total_steps > 0 else 0
    
    # Determine current step (first incomplete step)
    current_step = "complete"
    for step in steps:
        if not step.completed:
            current_step = step.step_id
            break
    
    # Estimate time remaining (2-5 minutes per remaining step)
    remaining_steps = total_steps - len(completed_steps)
    estimated_time_remaining = remaining_steps * 3  # 3 minutes per step average
    
    return OnboardingProgress(
        user_id=user.id,
        current_step=current_step,
        completed_steps=completed_steps,
        total_steps=total_steps,
        progress_percentage=progress_percentage,
        estimated_time_remaining=estimated_time_remaining
    )

@router.post("/step")
def update_onboarding_step(
    step_update: OnboardingStepUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Update onboarding step completion status"""
    step = db.query(OnboardingStep).filter(
        OnboardingStep.user_id == user.id,
        OnboardingStep.step_id == step_update.step_id
    ).first()
    
    if not step:
        raise HTTPException(status_code=404, detail="Onboarding step not found")
    
    step.completed = step_update.completed
    if step_update.data:
        step.data = json.dumps(step_update.data)
    step.completed_at = datetime.utcnow() if step_update.completed else None
    
    db.commit()
    
    return {"status": "updated", "step_id": step_update.step_id}

@router.post("/demo-project", response_model=Dict[str, Any])
def create_demo_project(
    project_data: DemoProjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Create a demo project for onboarding"""
    demo_project = DemoProject(
        user_id=user.id,
        name=project_data.name,
        description=project_data.description,
        queries=json.dumps(project_data.queries),
        tags=json.dumps(project_data.tags) if project_data.tags else None,
        is_demo=True
    )
    
    db.add(demo_project)
    db.commit()
    db.refresh(demo_project)
    
    # Mark demo project step as completed
    step = db.query(OnboardingStep).filter(
        OnboardingStep.user_id == user.id,
        OnboardingStep.step_id == "demo_project"
    ).first()
    
    if step:
        step.completed = True
        step.completed_at = datetime.utcnow()
        db.commit()
    
    return {
        "id": demo_project.id,
        "name": demo_project.name,
        "description": demo_project.description,
        "queries": json.loads(demo_project.queries),
        "tags": json.loads(demo_project.tags) if demo_project.tags else [],
        "is_demo": demo_project.is_demo,
        "created_at": demo_project.created_at
    }

@router.get("/demo-projects", response_model=List[Dict[str, Any]])
def get_demo_projects(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get user's demo projects"""
    projects = db.query(DemoProject).filter(
        DemoProject.user_id == user.id,
        DemoProject.is_demo == True
    ).all()
    
    return [
        {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "queries": json.loads(project.queries),
            "tags": json.loads(project.tags) if project.tags else [],
            "created_at": project.created_at
        }
        for project in projects
    ]

@router.get("/suggestions")
def get_onboarding_suggestions(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get personalized onboarding suggestions based on user progress"""
    progress = get_onboarding_progress(db, user)
    
    suggestions = []
    
    if progress.current_step == "welcome":
        suggestions.append({
            "type": "tip",
            "title": "Welcome to LeadTap!",
            "message": "Let's get you started with lead generation in just a few steps.",
            "action": "next_step"
        })
    
    elif progress.current_step == "first_job":
        suggestions.append({
            "type": "example",
            "title": "Try this example query",
            "message": "restaurants in New York",
            "action": "use_example"
        })
        suggestions.append({
            "type": "tip",
            "title": "Pro tip",
            "message": "Be specific with your queries for better results. Include location and business type.",
            "action": "info"
        })
    
    elif progress.current_step == "crm_setup":
        suggestions.append({
            "type": "integration",
            "title": "Connect your CRM",
            "message": "Integrate with HubSpot, Salesforce, or export to CSV.",
            "action": "setup_crm"
        })
    
    elif progress.current_step == "analytics":
        suggestions.append({
            "type": "feature",
            "title": "Explore Analytics",
            "message": "Track your lead generation performance and ROI.",
            "action": "explore_analytics"
        })
    
    return {"suggestions": suggestions}

@router.post("/complete")
def complete_onboarding(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Mark onboarding as complete"""
    # Mark all steps as completed
    steps = db.query(OnboardingStep).filter(OnboardingStep.user_id == user.id).all()
    
    for step in steps:
        step.completed = True
        step.completed_at = datetime.utcnow()
    
    db.commit()
    
    return {"status": "completed", "message": "Onboarding completed successfully!"} 