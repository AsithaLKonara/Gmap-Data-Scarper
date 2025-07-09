from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from models import User
from auth import get_current_user
from database import get_db
import logging

router = APIRouter(prefix="/api/support", tags=["support"])
logger = logging.getLogger("support")

class SupportRequest(BaseModel):
    subject: str
    message: str
    phone: Optional[str] = None

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