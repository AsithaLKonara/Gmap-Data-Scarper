from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, Field
from models import Affiliate, Commission, User
from database import get_db
from auth import get_current_user
from datetime import datetime
import random, string

router = APIRouter(prefix="/api/affiliate", tags=["affiliate"])

class AffiliateOut(BaseModel):
    code: str = Field(..., description="Unique affiliate code assigned to the user.", example="ABCD1234")
    total_earnings: float = Field(..., description="Total earnings accumulated by the affiliate.", example=123.45)
    is_active: bool = Field(..., description="Whether the affiliate account is active.")
    created_at: datetime = Field(..., description="Timestamp when the affiliate account was created.")

class CommissionOut(BaseModel):
    id: int = Field(..., description="Unique identifier for the commission.")
    amount: float = Field(..., description="Commission amount earned.", example=10.0)
    status: str = Field(..., description="Status of the commission (pending, paid, etc.)", example="pending")
    created_at: datetime = Field(..., description="Timestamp when the commission was created.")
    paid_at: Optional[datetime] = Field(None, description="Timestamp when the commission was paid, if applicable.")
    notes: Optional[str] = Field(None, description="Optional notes about the commission.")
    referred_user_id: int = Field(..., description="ID of the user who was referred.")

class PayoutRequest(BaseModel):
    amount: float = Field(..., description="Amount to request for payout.", example=50.0)
    notes: Optional[str] = Field(None, description="Optional notes for the payout request.")

class PayoutResponse(BaseModel):
    success: bool = Field(..., description="Whether the payout request was successful.", example=True)
    message: str = Field(..., description="Status message.", example="Payout request submitted for review.")

@router.post("/generate", response_model=AffiliateOut, summary="Generate affiliate code", description="Generate a unique affiliate code for the current user.")
def generate_affiliate_code(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Generate a unique affiliate code for the current user."""
    existing = db.query(Affiliate).filter_by(user_id=user.id).first()
    if existing:
        return existing
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    affiliate = Affiliate(user_id=user.id, code=code)
    db.add(affiliate)
    db.commit()
    db.refresh(affiliate)
    return affiliate

@router.get("/stats", response_model=AffiliateOut, summary="Get affiliate stats", description="Get the current user's affiliate stats.")
def get_affiliate_stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get the current user's affiliate stats."""
    affiliate = db.query(Affiliate).filter_by(user_id=user.id).first()
    if not affiliate:
        raise HTTPException(status_code=404, detail="No affiliate account found")
    return affiliate

@router.get("/commissions", response_model=List[CommissionOut], summary="List commissions", description="List all commissions for the current affiliate.")
def list_commissions(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """List all commissions for the current affiliate."""
    affiliate = db.query(Affiliate).filter_by(user_id=user.id).first()
    if not affiliate:
        raise HTTPException(status_code=404, detail="No affiliate account found")
    commissions = db.query(Commission).filter_by(affiliate_id=affiliate.id).all()
    return commissions

@router.post(
    "/payout",
    response_model=PayoutResponse,
    summary="Request payout",
    description="Request a payout for available commissions. This will submit a payout request for admin review.")
def request_payout(
    req: PayoutRequest = Body(..., description="Payout request payload."),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Request a payout for available commissions (admin review required)."""
    affiliate = db.query(Affiliate).filter_by(user_id=user.id).first()
    if not affiliate:
        raise HTTPException(status_code=404, detail="No affiliate account found")
    # TODO: Implement payout request logic (e.g., mark commissions as requested, notify admin)
    return PayoutResponse(success=True, message="Payout request submitted for review.") 