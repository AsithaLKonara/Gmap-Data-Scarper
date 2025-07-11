from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
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

class SupportRequest(BaseModel):
    subject: str
    message: str
    phone: Optional[str] = None

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

@router.get("/options")
def get_support_options(user: User = Depends(get_current_user)):
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

@router.post("/contact")
def submit_support_request(
    req: SupportRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Simulate logging the support request
    logger.info(f"Support request from {user.email} (plan: {user.plan}): {req.subject} - {req.message} - {req.phone}")
    print(f"[SUPPORT] {user.email} ({user.plan}): {req.subject} - {req.message} - {req.phone}")
    return {"message": "Support request submitted. Our team will contact you soon."}

@router.get("/faqs", response_model=List[FAQ], summary="Get FAQs", response_description="List of frequently asked questions")
def get_faqs():
    """Get the list of frequently asked questions for the Knowledge Base."""
    return _FAQ_LIST

@router.get("/support", response_model=List[SupportTicket], summary="Get Support Tickets", response_description="List of support tickets")
def get_support_tickets(request: Request, db: Session = Depends(get_db)):
    tenant = get_tenant_from_request(request, db)
    tickets = db.query(SupportTicket).filter_by(tenant_id=tenant.id).all()
    return tickets

@router.post("/support", response_model=SupportTicket, summary="Create Support Ticket", response_description="Created support ticket")
def create_support_ticket(
    req: BaseModel,  # Assuming req is a BaseModel for simplicity, as SupportRequest is removed
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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

@router.get("/support/{ticket_id}", response_model=SupportTicket, summary="Get Support Ticket", response_description="Retrieve a specific support ticket")
def get_support_ticket(ticket_id: int, request: Request, db: Session = Depends(get_db)):
    tenant = get_tenant_from_request(request, db)
    ticket = get_tenant_record_or_403(SupportTicket, ticket_id, tenant.id, db)
    return ticket 