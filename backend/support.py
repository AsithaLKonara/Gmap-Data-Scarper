from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from models import User
from auth import get_current_user
from database import get_db
import logging
from models import SupportTicket
from tenant_utils import get_tenant_from_request
from tenant_utils import get_tenant_record_or_403

router = APIRouter(prefix="/api/support", tags=["support"])
logger = logging.getLogger("support")

# --- Pydantic Models for OpenAPI ---
class SupportRequest(BaseModel):
    subject: str = Field(..., description="Subject of the support request.")
    message: str = Field(..., description="Message body of the support request.")
    phone: Optional[str] = Field(None, description="Phone number for support contact.")

class SupportResponse(BaseModel):
    message: str

class FAQ(BaseModel):
    question: str
    answer: str

_FAQ_LIST = [
    FAQ(question="How do I create my first scraping job?", answer="Go to the Dashboard, enter your search queries, and click 'Create Job'."),
    FAQ(question="How do I upgrade my plan?", answer="Click the 'Upgrade Plan' button in your dashboard or settings."),
    FAQ(question="How do I export my leads?", answer="After a job is completed, use the Export buttons to download your leads in CSV, JSON, or Excel format (depending on your plan)."),
    FAQ(question="How do I connect my CRM?", answer="Go to the CRM section and follow the instructions to connect HubSpot, Salesforce, or export to CSV for manual import."),
    FAQ(question="How do I contact support?", answer="Use the 'Contact Support' button in your dashboard or email us at support@leadtap.com."),
]

@router.get("/options", summary="Get support options", description="Get available support options for the authenticated user's plan.")
def get_support_options(user: User = Depends(get_current_user)):
    """Get available support options for the authenticated user's plan."""
    if user.plan == "free":
        return {"support": ["email"], "priority": False}
    elif user.plan == "pro":
        return {"support": ["email"], "priority": True}
    elif user.plan == "business":
        return {
            "support": ["email", "phone", "custom_integrations", "white_label", "dedicated_manager"],
            "priority": True
        }
    else:
        return {"support": ["email"], "priority": False}

@router.post("/contact", response_model=SupportResponse, summary="Submit support request", description="Submit a support request to the support team.")
def submit_support_request(
    req: SupportRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a support request to the support team."""
    # Simulate logging the support request
    logger.info(f"Support request from {user.email} (plan: {user.plan}): {req.subject} - {req.message} - {req.phone}")
    print(f"[SUPPORT] {user.email} ({user.plan}): {req.subject} - {req.message} - {req.phone}")
    return {"message": "Support request submitted. Our team will contact you soon."}

@router.get("/faqs", response_model=List[FAQ], summary="Get FAQs", description="Get the list of frequently asked questions for the Knowledge Base.", response_description="List of frequently asked questions")
def get_faqs():
    """Get the list of frequently asked questions for the Knowledge Base."""
    return _FAQ_LIST

@router.get("/support", response_model=List[SupportTicket], summary="Get Support Tickets", description="Get all support tickets for the current tenant.", response_description="List of support tickets")
def get_support_tickets(request: Request, db: Session = Depends(get_db)):
    """Get all support tickets for the current tenant."""
    tenant = get_tenant_from_request(request, db)
    tickets = db.query(SupportTicket).filter_by(tenant_id=tenant.id).all()
    return tickets

@router.post("/support", response_model=SupportTicket, summary="Create Support Ticket", description="Create a new support ticket for the current tenant.", response_description="Created support ticket")
def create_support_ticket(
    req: SupportRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new support ticket for the current tenant."""
    tenant = get_tenant_from_request(request, db)
    ticket = SupportTicket(
        subject=req.subject,
        message=req.message,
        phone=req.phone,
        user_id=user.id,
        tenant_id=tenant.id
    )
    db.add(ticket)
    db.commit()
    return ticket

@router.get("/support/{ticket_id}", response_model=SupportTicket, summary="Get Support Ticket", description="Retrieve a specific support ticket by ID for the current tenant.", response_description="Retrieve a specific support ticket")
def get_support_ticket(ticket_id: int = Field(..., description="ID of the support ticket."), request: Request = None, db: Session = Depends(get_db)):
    """Retrieve a specific support ticket by ID for the current tenant."""
    tenant = get_tenant_from_request(request, db)
    ticket = get_tenant_record_or_403(SupportTicket, ticket_id, tenant.id, db)
    return ticket 