from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from models import Users, OnboardingSteps, DemoProjects
from database import get_db
from auth import get_current_user
import json
from datetime import datetime

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])

# --- Pydantic Models for OpenAPI ---
class OnboardingStepUpdate(BaseModel):
    step_id: str = Field(..., description="ID of the onboarding step.")
    completed: bool = Field(..., description="Whether the step is completed.")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data for the step.")

class DemoProjectCreate(BaseModel):
    name: str = Field(..., description="Name of the demo project.")
    description: str = Field(..., description="Description of the demo project.")
    queries: List[str] = Field(..., description="List of queries for the demo project.")
    tags: Optional[List[str]] = Field(None, description="Tags for the demo project.")

class OnboardingProgress(BaseModel):
    user_id: int
    current_step: str
    completed_steps: List[str]
    total_steps: int
    progress_percentage: float
    estimated_time_remaining: int  # minutes

class DemoProjectOut(BaseModel):
    id: int
    name: str
    description: str
    queries: List[str]
    tags: List[str]
    is_demo: bool
    created_at: datetime

class OnboardingStepStatusResponse(BaseModel):
    status: str
    step_id: str

@router.get("/progress", response_model=OnboardingProgress, summary="Get onboarding progress", description="Get the current user's onboarding progress.")
def get_onboarding_progress(
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    default_steps = [
        {"step_id": "welcome", "name": "Welcome", "description": "Get started with LeadTap"},
        {"step_id": "profile", "name": "Complete Profile", "description": "Set up your profile"},
        {"step_id": "first_job", "name": "Create First Job", "description": "Create your first scraping job"},
        {"step_id": "demo_project", "name": "Demo Project", "description": "Try our demo project"},
        {"step_id": "crm_setup", "name": "CRM Setup", "description": "Connect your CRM"},
        {"step_id": "analytics", "name": "Analytics Tour", "description": "Explore analytics features"},
        {"step_id": "complete", "name": "Onboarding Complete", "description": "You're all set!"}
    ]
    # Ensure steps exist for user
    steps = db.query(OnboardingSteps).filter(OnboardingSteps.user_id == user.id).all()
    if not steps:
        for step in default_steps:
            db.add(OnboardingSteps(user_id=user.id, step_id=step["step_id"], completed=False))
        db.commit()
        steps = db.query(OnboardingSteps).filter(OnboardingSteps.user_id == user.id).all()
    completed_steps = [step.step_id for step in steps if step.completed]
    total_steps = len(default_steps)
    progress_percentage = (len(completed_steps) / total_steps) * 100 if total_steps > 0 else 0
    # Determine current step
    current_step = "complete"
    for step in default_steps:
        s = next((x for x in steps if x.step_id == step["step_id"]), None)
        if s and not s.completed:
            current_step = step["step_id"]
            break
    remaining_steps = total_steps - len(completed_steps)
    estimated_time_remaining = remaining_steps * 3
    return OnboardingProgress(
        user_id=user.id,
        current_step=current_step,
        completed_steps=completed_steps,
        total_steps=total_steps,
        progress_percentage=progress_percentage,
        estimated_time_remaining=estimated_time_remaining
    )

@router.post("/step", response_model=OnboardingStepStatusResponse, summary="Update onboarding step", description="Update onboarding step completion status.")
def update_onboarding_step(
    step_update: OnboardingStepUpdate,
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    step = db.query(OnboardingSteps).filter(
        OnboardingSteps.user_id == user.id,
        OnboardingSteps.step_id == step_update.step_id
    ).first()
    if not step:
        raise HTTPException(status_code=404, detail="Onboarding step not found")
    step.completed = step_update.completed
    if step_update.data:
        step.data = step_update.data
    step.completed_at = datetime.utcnow() if step_update.completed else None
    db.commit()
    return {"status": "updated", "step_id": step_update.step_id}

@router.post("/demo-project", response_model=DemoProjectOut, summary="Create demo project", description="Create a demo project for onboarding.")
def create_demo_project(
    project_data: DemoProjectCreate,
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    demo_project = DemoProjects(
        user_id=user.id,
        name=project_data.name,
        description=project_data.description,
        queries=project_data.queries,
        tags=project_data.tags,
        is_demo=True
    )
    db.add(demo_project)
    db.commit()
    db.refresh(demo_project)
    # Mark demo_project step as completed
    step = db.query(OnboardingSteps).filter(
        OnboardingSteps.user_id == user.id,
        OnboardingSteps.step_id == "demo_project"
    ).first()
    if step:
        step.completed = True
        step.completed_at = datetime.utcnow()
        db.commit()
    return DemoProjectOut(
        id=demo_project.id,
        name=demo_project.name,
        description=demo_project.description,
        queries=demo_project.queries,
        tags=demo_project.tags or [],
        is_demo=demo_project.is_demo,
        created_at=demo_project.created_at
    )

@router.get("/demo-projects", response_model=List[DemoProjectOut], summary="List demo projects", description="Get all demo projects for the current user.")
def get_demo_projects(
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    projects = db.query(DemoProjects).filter(
        DemoProjects.user_id == user.id,
        DemoProjects.is_demo == True
    ).all()
    return [DemoProjectOut(
        id=p.id,
        name=p.name,
        description=p.description,
        queries=p.queries,
        tags=p.tags or [],
        is_demo=p.is_demo,
        created_at=p.created_at
    ) for p in projects]

@router.get("/suggestions", summary="Get onboarding suggestions", description="Get personalized onboarding suggestions based on user progress.")
def get_onboarding_suggestions(
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Get personalized onboarding suggestions based on user progress."""
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

@router.post("/complete", summary="Complete onboarding", description="Mark onboarding as complete for the current user.")
def complete_onboarding(
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    steps = db.query(OnboardingSteps).filter(OnboardingSteps.user_id == user.id).all()
    for step in steps:
        step.completed = True
        step.completed_at = datetime.utcnow()
    db.commit()
    return {"status": "completed", "message": "Onboarding completed successfully!"} 