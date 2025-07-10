from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from models import User, Referral, ReferralReward
from database import get_db
from auth import get_current_user
import secrets
from datetime import datetime

router = APIRouter(prefix="/api/referral", tags=["referral"])

class ReferralInfo(BaseModel):
    code: str
    url: str
    total_referred: int
    total_rewards: float
    rewards: List[Dict[str, Any]]

class ReferralRewardOut(BaseModel):
    id: int
    referred_email: str
    reward_amount: float
    status: str
    created_at: datetime

@router.get("/me", response_model=ReferralInfo)
def get_my_referral_info(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get the current user's referral code, stats, and rewards."""
    # Generate referral code if not present
    if not user.referral_code:
        user.referral_code = secrets.token_urlsafe(8)
        db.commit()
    code = user.referral_code
    url = f"https://leadtap.com/register?ref={code}"
    total_referred = db.query(Referral).filter(Referral.referrer_id == user.id).count()
    rewards = db.query(ReferralReward).filter(ReferralReward.user_id == user.id).all()
    total_rewards = sum(r.reward_amount for r in rewards)
    rewards_out = [
        {
            "id": r.id,
            "referred_email": r.referred_email,
            "reward_amount": r.reward_amount,
            "status": r.status,
            "created_at": r.created_at
        }
        for r in rewards
    ]
    return ReferralInfo(
        code=code,
        url=url,
        total_referred=total_referred,
        total_rewards=total_rewards,
        rewards=rewards_out
    )

@router.post("/track")
def track_referral(ref_code: str, referred_email: str, db: Session = Depends(get_db)):
    """Track a new referral sign-up."""
    referrer = db.query(User).filter(User.referral_code == ref_code).first()
    if not referrer:
        raise HTTPException(status_code=404, detail="Referral code not found")
    referral = Referral(referrer_id=referrer.id, referred_email=referred_email, created_at=datetime.utcnow())
    db.add(referral)
    db.commit()
    return {"status": "tracked"}

@router.get("/rewards", response_model=List[ReferralRewardOut])
def get_referral_rewards(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get all referral rewards for the current user."""
    rewards = db.query(ReferralReward).filter(ReferralReward.user_id == user.id).all()
    return [
        ReferralRewardOut(
            id=r.id,
            referred_email=r.referred_email,
            reward_amount=r.reward_amount,
            status=r.status,
            created_at=r.created_at
        ) for r in rewards
    ] 