from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Body, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
import asyncio
from datetime import datetime, timedelta
from models import User, WhatsAppWorkflow, WhatsAppWorkflowStep, WhatsAppWorkflowTrigger, SocialMediaLead, Lead
from database import get_db
from auth import get_current_user
import logging
import secrets
import os

router = APIRouter(prefix="/api/whatsapp-workflow", tags=["whatsapp-workflow"])
logger = logging.getLogger("whatsapp-workflow")

# Pydantic models
class WorkflowStepCreate(BaseModel):
    name: str = Field(..., description="Step name.", example="Send Welcome Message")
    step_type: str = Field(..., description="Type of step (message, delay, condition, action)", example="message")
    content: Optional[str] = Field(None, description="Message content or step details.", example="Hi {{name}}, welcome!")
    delay_minutes: Optional[int] = Field(0, description="Delay in minutes for delay steps.", example=60)
    conditions: Optional[Dict[str, Any]] = Field(None, description="Conditions for conditional steps.")
    actions: Optional[List[str]] = Field(None, description="Actions to perform in this step.")
    order: int = Field(..., description="Order of the step in the workflow.", example=1)

class WorkflowCreate(BaseModel):
    name: str = Field(..., description="Workflow name.", example="Welcome Sequence")
    description: Optional[str] = Field(None, description="Workflow description.", example="Welcome new leads with a 3-step sequence.")
    trigger_type: str = Field(..., description="Trigger type (lead_created, lead_qualified, manual, scheduled)", example="lead_created")
    trigger_conditions: Optional[Dict[str, Any]] = Field(None, description="Conditions for triggering the workflow.")
    steps: List[WorkflowStepCreate] = Field(..., description="List of workflow steps.")
    is_active: bool = Field(True, description="Whether the workflow is active.")

class WorkflowTrigger(BaseModel):
    workflow_id: int = Field(..., description="ID of the workflow to trigger.")
    lead_id: Optional[int] = Field(None, description="CRM lead ID to use as input.")
    social_lead_id: Optional[int] = Field(None, description="Social media lead ID to use as input.")
    trigger_data: Optional[Dict[str, Any]] = Field(None, description="Additional data for the trigger.")

class WorkflowExecution(BaseModel):
    workflow_id: int = Field(..., description="ID of the workflow to execute.")
    lead_id: Optional[int] = Field(None, description="CRM lead ID to use as input.")
    social_lead_id: Optional[int] = Field(None, description="Social media lead ID to use as input.")
    execution_data: Optional[Dict[str, Any]] = Field(None, description="Additional data for the execution.")

# WhatsApp Workflow Engine
class WhatsAppWorkflowEngine:
    def __init__(self):
        self.active_workflows = {}
    
    async def execute_workflow(self, workflow_id: int, lead_data: Dict, db: Session):
        """Execute a WhatsApp workflow"""
        workflow = db.query(WhatsAppWorkflow).filter(WhatsAppWorkflow.id == workflow_id).first()
        if not workflow or not workflow.is_active:
            return
        
        steps = db.query(WhatsAppWorkflowStep).filter(
            WhatsAppWorkflowStep.workflow_id == workflow_id
        ).order_by(WhatsAppWorkflowStep.order).all()
        
        execution_data = {
            "workflow_id": workflow_id,
            "lead_data": lead_data,
            "current_step": 0,
            "variables": {},
            "started_at": datetime.utcnow()
        }
        
        for step in steps:
            try:
                await self.execute_step(step, execution_data, db)
                execution_data["current_step"] += 1
            except Exception as e:
                logger.error(f"Error executing workflow step {step.id}: {e}")
                break
    
    async def execute_step(self, step: WhatsAppWorkflowStep, execution_data: Dict, db: Session):
        """Execute a single workflow step"""
        if step.step_type == "message":
            await self.send_message_step(step, execution_data, db)
        elif step.step_type == "delay":
            await self.delay_step(step, execution_data)
        elif step.step_type == "condition":
            await self.condition_step(step, execution_data, db)
        elif step.step_type == "action":
            await self.action_step(step, execution_data, db)
    
    async def send_message_step(self, step: WhatsAppWorkflowStep, execution_data: Dict, db: Session):
        """Send a WhatsApp message step"""
        from whatsapp_automation import whatsapp_api
        
        # Replace variables in message content
        message_content = self.replace_variables(step.content, execution_data)
        
        # Get recipient phone number
        lead_data = execution_data["lead_data"]
        phone_number = lead_data.get("phone")
        
        if not phone_number:
            logger.warning(f"No phone number found for lead in workflow step {step.id}")
            return
        
        try:
            # Send message via WhatsApp API
            result = await whatsapp_api.send_message(
                phone_number=phone_number,
                message=message_content,
                message_type="text"
            )
            
            # Log the message
            from models import WhatsAppMessage
            message = WhatsAppMessage(
                user_id=execution_data["lead_data"]["user_id"],
                recipient_phone=phone_number,
                message_content=message_content,
                message_type="text",
                status="sent",
                workflow_id=execution_data["workflow_id"],
                step_id=step.id
            )
            db.add(message)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
    
    async def delay_step(self, step: WhatsAppWorkflowStep, execution_data: Dict):
        """Execute a delay step"""
        delay_minutes = step.delay_minutes or 0
        if delay_minutes > 0:
            await asyncio.sleep(delay_minutes * 60)
    
    async def condition_step(self, step: WhatsAppWorkflowStep, execution_data: Dict, db: Session):
        """Execute a conditional step"""
        conditions = step.conditions or {}
        lead_data = execution_data["lead_data"]
        
        # Evaluate conditions
        condition_met = self.evaluate_conditions(conditions, lead_data)
        
        if condition_met:
            # Execute positive actions
            if step.actions:
                for action in step.actions:
                    await self.execute_action(action, execution_data, db)
        else:
            # Execute negative actions (if any)
            negative_actions = step.conditions.get("negative_actions", [])
            for action in negative_actions:
                await self.execute_action(action, execution_data, db)
    
    async def action_step(self, step: WhatsAppWorkflowStep, execution_data: Dict, db: Session):
        """Execute an action step"""
        actions = step.actions or []
        for action in actions:
            await self.execute_action(action, execution_data, db)
    
    def replace_variables(self, content: str, execution_data: Dict) -> str:
        """Replace variables in content with actual values"""
        lead_data = execution_data["lead_data"]
        
        # Common variable replacements
        replacements = {
            "{{name}}": lead_data.get("display_name", ""),
            "{{company}}": lead_data.get("business_category", ""),
            "{{location}}": lead_data.get("location", ""),
            "{{platform}}": lead_data.get("platform", ""),
            "{{followers}}": str(lead_data.get("followers_count", 0)),
            "{{engagement_score}}": str(lead_data.get("engagement_score", 0)),
            "{{website}}": lead_data.get("website", ""),
            "{{email}}": lead_data.get("email", ""),
            "{{phone}}": lead_data.get("phone", "")
        }
        
        for variable, value in replacements.items():
            content = content.replace(variable, value)
        
        return content
    
    def evaluate_conditions(self, conditions: Dict, lead_data: Dict) -> bool:
        """Evaluate workflow conditions"""
        for condition_type, condition_value in conditions.items():
            if condition_type == "engagement_score_min":
                if lead_data.get("engagement_score", 0) < condition_value:
                    return False
            elif condition_type == "followers_min":
                if lead_data.get("followers_count", 0) < condition_value:
                    return False
            elif condition_type == "platform":
                if lead_data.get("platform") not in condition_value:
                    return False
            elif condition_type == "has_contact":
                required_contacts = condition_value
                has_email = bool(lead_data.get("email"))
                has_phone = bool(lead_data.get("phone"))
                has_website = bool(lead_data.get("website"))
                
                if "email" in required_contacts and not has_email:
                    return False
                if "phone" in required_contacts and not has_phone:
                    return False
                if "website" in required_contacts and not has_website:
                    return False
        
        return True
    
    async def execute_action(self, action: str, execution_data: Dict, db: Session):
        """Execute a workflow action"""
        if action == "add_to_crm":
            await self.add_lead_to_crm(execution_data["lead_data"], db)
        elif action == "send_follow_up":
            await self.send_follow_up_message(execution_data["lead_data"], db)
        elif action == "update_status":
            await self.update_lead_status(execution_data["lead_data"], "contacted", db)
        elif action == "create_task":
            await self.create_follow_up_task(execution_data["lead_data"], db)
    
    async def add_lead_to_crm(self, lead_data: Dict, db: Session):
        """Add lead to CRM"""
        from models import Lead
        
        # Check if lead already exists
        existing_lead = db.query(Lead).filter(
            Lead.email == lead_data.get("email"),
            Lead.user_id == lead_data["user_id"]
        ).first()
        
        if not existing_lead:
            lead = Lead(
                user_id=lead_data["user_id"],
                name=lead_data.get("display_name", ""),
                email=lead_data.get("email"),
                phone=lead_data.get("phone"),
                company=lead_data.get("business_category", ""),
                website=lead_data.get("website"),
                source="social_media",
                status="new",
                notes=f"Imported from {lead_data.get('platform', 'social media')} workflow"
            )
            db.add(lead)
            db.commit()
    
    async def send_follow_up_message(self, lead_data: Dict, db: Session):
        """Send follow-up message"""
        from whatsapp_automation import whatsapp_api
        
        phone_number = lead_data.get("phone")
        if not phone_number:
            return
        
        follow_up_message = f"Hi {lead_data.get('display_name', 'there')}! We noticed your profile and would love to connect. Are you interested in learning more about our services?"
        
        try:
            await whatsapp_api.send_message(
                phone_number=phone_number,
                message=follow_up_message,
                message_type="text"
            )
        except Exception as e:
            logger.error(f"Error sending follow-up message: {e}")
    
    async def update_lead_status(self, lead_data: Dict, status: str, db: Session):
        """Update lead status"""
        if lead_data.get("social_lead_id"):
            social_lead = db.query(SocialMediaLead).filter(
                SocialMediaLead.id == lead_data["social_lead_id"]
            ).first()
            if social_lead:
                social_lead.status = status
                db.commit()
    
    async def create_follow_up_task(self, lead_data: Dict, db: Session):
        """Create follow-up task"""
        # This would integrate with a task management system
        # For now, we'll just log it
        logger.info(f"Created follow-up task for lead: {lead_data.get('display_name')}")

# Initialize workflow engine
workflow_engine = WhatsAppWorkflowEngine()

# API endpoints
@router.post(
    "/workflows",
    response_model=Dict[str, Any],
    summary="Create WhatsApp workflow",
    description="Create a new WhatsApp workflow. Requires Pro or Business plan."
)
async def create_workflow(
    workflow_data: WorkflowCreate = Body(..., description="Workflow creation payload."),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new WhatsApp workflow."""
    if current_user.plan not in ['pro', 'business']:
        raise HTTPException(status_code=403, detail="Pro or Business plan required")
    
    # Create workflow
    workflow = WhatsAppWorkflow(
        name=workflow_data.name,
        description=workflow_data.description,
        trigger_type=workflow_data.trigger_type,
        trigger_conditions=json.dumps(workflow_data.trigger_conditions) if workflow_data.trigger_conditions else None,
        is_active=workflow_data.is_active,
        user_id=current_user.id
    )
    
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    
    # Create workflow steps
    for step_data in workflow_data.steps:
        step = WhatsAppWorkflowStep(
            workflow_id=workflow.id,
            name=step_data.name,
            step_type=step_data.step_type,
            content=step_data.content,
            delay_minutes=step_data.delay_minutes,
            conditions=json.dumps(step_data.conditions) if step_data.conditions else None,
            actions=json.dumps(step_data.actions) if step_data.actions else None,
            order=step_data.order
        )
        db.add(step)
    
    db.commit()
    
    return {
        "id": workflow.id,
        "name": workflow.name,
        "description": workflow.description,
        "trigger_type": workflow.trigger_type,
        "is_active": workflow.is_active,
        "created_at": workflow.created_at
    }

@router.get(
    "/workflows",
    response_model=List[Dict[str, Any]],
    summary="List WhatsApp workflows",
    description="Get all WhatsApp workflows for the authenticated user."
)
async def get_workflows(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's WhatsApp workflows."""
    workflows = db.query(WhatsAppWorkflow).filter(
        WhatsAppWorkflow.user_id == current_user.id
    ).all()
    
    result = []
    for workflow in workflows:
        steps = db.query(WhatsAppWorkflowStep).filter(
            WhatsAppWorkflowStep.workflow_id == workflow.id
        ).order_by(WhatsAppWorkflowStep.order).all()
        
        result.append({
            "id": workflow.id,
            "name": workflow.name,
            "description": workflow.description,
            "trigger_type": workflow.trigger_type,
            "trigger_conditions": json.loads(workflow.trigger_conditions) if workflow.trigger_conditions else None,
            "is_active": workflow.is_active,
            "steps": [
                {
                    "id": step.id,
                    "name": step.name,
                    "step_type": step.step_type,
                    "content": step.content,
                    "delay_minutes": step.delay_minutes,
                    "conditions": json.loads(step.conditions) if step.conditions else None,
                    "actions": json.loads(step.actions) if step.actions else None,
                    "order": step.order
                }
                for step in steps
            ],
            "created_at": workflow.created_at,
            "updated_at": workflow.updated_at
        })
    
    return result

@router.post(
    "/trigger",
    response_model=Dict[str, Any],
    summary="Trigger WhatsApp workflow",
    description="Trigger a WhatsApp workflow for a lead. Starts execution in the background."
)
async def trigger_workflow(
    trigger_data: WorkflowTrigger = Body(..., description="Workflow trigger payload."),
    background_tasks: BackgroundTasks = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger a WhatsApp workflow for a lead (background execution)."""
    workflow = db.query(WhatsAppWorkflow).filter(
        WhatsAppWorkflow.id == trigger_data.workflow_id,
        WhatsAppWorkflow.user_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    if not workflow.is_active:
        raise HTTPException(status_code=400, detail="Workflow is not active")
    
    # Get lead data
    lead_data = {}
    if trigger_data.lead_id:
        lead = db.query(Lead).filter(Lead.id == trigger_data.lead_id).first()
        if lead:
            lead_data = {
                "id": lead.id,
                "display_name": lead.name,
                "email": lead.email,
                "phone": lead.phone,
                "company": lead.company,
                "website": lead.website,
                "user_id": current_user.id,
                "source": "crm"
            }
    
    if trigger_data.social_lead_id:
        social_lead = db.query(SocialMediaLead).filter(
            SocialMediaLead.id == trigger_data.social_lead_id
        ).first()
        if social_lead:
            lead_data = {
                "id": social_lead.id,
                "display_name": social_lead.display_name,
                "email": social_lead.email,
                "phone": social_lead.phone,
                "business_category": social_lead.business_category,
                "website": social_lead.website,
                "platform": social_lead.platform,
                "followers_count": social_lead.followers_count,
                "engagement_score": social_lead.engagement_score,
                "user_id": current_user.id,
                "source": "social_media",
                "social_lead_id": social_lead.id
            }
    
    if not lead_data:
        raise HTTPException(status_code=400, detail="No valid lead data found")
    
    # Add trigger data
    if trigger_data.trigger_data:
        lead_data.update(trigger_data.trigger_data)
    
    # Start workflow execution in background
    background_tasks.add_task(
        workflow_engine.execute_workflow,
        workflow.id,
        lead_data,
        db
    )
    
    return {
        "workflow_id": workflow.id,
        "status": "triggered",
        "message": "Workflow execution started"
    }

@router.post(
    "/execute",
    response_model=Dict[str, Any],
    summary="Execute WhatsApp workflow manually",
    description="Manually execute a WhatsApp workflow for a lead. Starts execution in the background."
)
async def execute_workflow(
    execution_data: WorkflowExecution = Body(..., description="Workflow execution payload."),
    background_tasks: BackgroundTasks = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually execute a WhatsApp workflow for a lead (background execution)."""
    workflow = db.query(WhatsAppWorkflow).filter(
        WhatsAppWorkflow.id == execution_data.workflow_id,
        WhatsAppWorkflow.user_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Get lead data
    lead_data = {}
    if execution_data.lead_id:
        lead = db.query(Lead).filter(Lead.id == execution_data.lead_id).first()
        if lead:
            lead_data = {
                "id": lead.id,
                "display_name": lead.name,
                "email": lead.email,
                "phone": lead.phone,
                "company": lead.company,
                "website": lead.website,
                "user_id": current_user.id,
                "source": "crm"
            }
    
    if execution_data.social_lead_id:
        social_lead = db.query(SocialMediaLead).filter(
            SocialMediaLead.id == execution_data.social_lead_id
        ).first()
        if social_lead:
            lead_data = {
                "id": social_lead.id,
                "display_name": social_lead.display_name,
                "email": social_lead.email,
                "phone": social_lead.phone,
                "business_category": social_lead.business_category,
                "website": social_lead.website,
                "platform": social_lead.platform,
                "followers_count": social_lead.followers_count,
                "engagement_score": social_lead.engagement_score,
                "user_id": current_user.id,
                "source": "social_media",
                "social_lead_id": social_lead.id
            }
    
    if not lead_data:
        raise HTTPException(status_code=400, detail="No valid lead data found")
    
    # Add execution data
    if execution_data.execution_data:
        lead_data.update(execution_data.execution_data)
    
    # Start workflow execution in background
    background_tasks.add_task(
        workflow_engine.execute_workflow,
        workflow.id,
        lead_data,
        db
    )
    
    return {
        "workflow_id": workflow.id,
        "status": "executing",
        "message": "Workflow execution started"
    }

@router.get(
    "/templates",
    response_model=List[Dict[str, Any]],
    summary="Get workflow templates",
    description="Get predefined WhatsApp workflow templates."
)
async def get_workflow_templates(
    current_user: User = Depends(get_current_user)
):
    """Get predefined workflow templates."""
    templates = [
        {
            "id": "welcome_sequence",
            "name": "Welcome Sequence",
            "description": "Welcome new leads with a 3-step sequence",
            "trigger_type": "lead_created",
            "steps": [
                {
                    "name": "Welcome Message",
                    "step_type": "message",
                    "content": "Hi {{name}}! Welcome to our community. We're excited to connect with you!",
                    "order": 1
                },
                {
                    "name": "Delay",
                    "step_type": "delay",
                    "delay_minutes": 60,
                    "order": 2
                },
                {
                    "name": "Value Proposition",
                    "step_type": "message",
                    "content": "We help businesses like yours grow through our innovative solutions. Would you like to learn more?",
                    "order": 3
                }
            ]
        },
        {
            "id": "engagement_sequence",
            "name": "Engagement Sequence",
            "description": "Engage high-value leads with personalized messages",
            "trigger_type": "lead_qualified",
            "steps": [
                {
                    "name": "Personalized Greeting",
                    "step_type": "message",
                    "content": "Hi {{name}}! I noticed your impressive {{followers}} followers on {{platform}}. Your content is amazing!",
                    "order": 1
                },
                {
                    "name": "Delay",
                    "step_type": "delay",
                    "delay_minutes": 30,
                    "order": 2
                },
                {
                    "name": "Collaboration Offer",
                    "step_type": "message",
                    "content": "We'd love to explore collaboration opportunities. Are you interested in discussing potential partnerships?",
                    "order": 3
                }
            ]
        },
        {
            "id": "follow_up_sequence",
            "name": "Follow-up Sequence",
            "description": "Follow up with leads who haven't responded",
            "trigger_type": "manual",
            "steps": [
                {
                    "name": "Friendly Reminder",
                    "step_type": "message",
                    "content": "Hi {{name}}! Just wanted to follow up on our previous message. Are you still interested?",
                    "order": 1
                },
                {
                    "name": "Delay",
                    "step_type": "delay",
                    "delay_minutes": 120,
                    "order": 2
                },
                {
                    "name": "Final Offer",
                    "step_type": "message",
                    "content": "Last chance! We have a special offer for you. Would you like to take advantage of it?",
                    "order": 3
                }
            ]
        }
    ]
    
    return templates

@router.get(
    "/analytics",
    response_model=Dict[str, Any],
    summary="Get workflow analytics",
    description="Get analytics and statistics for WhatsApp workflows and messages."
)
async def get_workflow_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get WhatsApp workflow analytics and statistics."""
    # Get workflow statistics
    total_workflows = db.query(WhatsAppWorkflow).filter(
        WhatsAppWorkflow.user_id == current_user.id
    ).count()
    
    active_workflows = db.query(WhatsAppWorkflow).filter(
        WhatsAppWorkflow.user_id == current_user.id,
        WhatsAppWorkflow.is_active == True
    ).count()
    
    # Get message statistics
    from models import WhatsAppMessage
    total_messages = db.query(WhatsAppMessage).filter(
        WhatsAppMessage.user_id == current_user.id,
        WhatsAppMessage.workflow_id.isnot(None)
    ).count()
    
    successful_messages = db.query(WhatsAppMessage).filter(
        WhatsAppMessage.user_id == current_user.id,
        WhatsAppMessage.workflow_id.isnot(None),
        WhatsAppMessage.status == "sent"
    ).count()
    
    return {
        "total_workflows": total_workflows,
        "active_workflows": active_workflows,
        "total_messages": total_messages,
        "successful_messages": successful_messages,
        "success_rate": (successful_messages / total_messages * 100) if total_messages > 0 else 0
    } 