from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from models import Users, Jobs, Leads
from database import get_db
from auth import get_current_user
import logging
import json
from datetime import datetime
import os
import shutil
from fastapi.responses import JSONResponse
import secrets
from audit import audit_log

logger = logging.getLogger("profiles")

router = APIRouter(prefix="/api/profiles", tags=["profiles"])

# --- Pydantic Models for OpenAPI ---
class ProfileUpdateRequest(BaseModel):
    first_name: Optional[str] = Field(None, description="First name of the user.")
    last_name: Optional[str] = Field(None, description="Last name of the user.")
    phone: Optional[str] = Field(None, description="Phone number of the user.")
    company: Optional[str] = Field(None, description="Company name.")
    website: Optional[str] = Field(None, description="Website URL.")
    bio: Optional[str] = Field(None, description="User bio.")
    timezone: Optional[str] = Field(None, description="Timezone.")

class ProfileResponse(BaseModel):
    id: int
    user_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    website: Optional[str] = None
    bio: Optional[str] = None
    timezone: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserInfoResponse(BaseModel):
    id: int
    email: str
    plan: str
    created_at: datetime
    profile: Optional[ProfileResponse] = None

    class Config:
        from_attributes = True

class AvatarUploadResponse(BaseModel):
    message: str
    avatar_url: str

class AvatarDeleteResponse(BaseModel):
    message: str

class UserStatsResponse(BaseModel):
    total_jobs: int
    completed_jobs: int
    success_rate: float
    total_leads: int
    account_age_days: int

class ExportDataResponse(BaseModel):
    jobs: list
    leads: list

class DeleteAccountResponse(BaseModel):
    status: str

class ReferralInfoResponse(BaseModel):
    code: str
    stats: dict

class ReferralUseResponse(BaseModel):
    message: str

class ReferralStatsResponse(BaseModel):
    referred_users: int
    total_credits: int

class UsageResponse(BaseModel):
    jobs_count: int
    exports_count: int

class CreditsPurchaseResponse(BaseModel):
    message: str
    credits_added: int

@router.get("/me", response_model=UserInfoResponse, summary="Get user info", description="Get the authenticated user's profile and plan information.")
def get_user_info(db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    """Get the authenticated user's profile and plan information."""
    try:
        # Get or create profile
        profile = db.query(UserProfiles).filter(UserProfiles.user_id == user.id).first()
        if not profile:
            profile = UserProfiles(user_id=user.id)
            db.add(profile)
            db.commit()
            db.refresh(profile)
        
        return {
            "id": user.id,
            "email": user.email,
            "plan": user.plan,
            "created_at": user.created_at,
            "profile": profile
        }
    except Exception as e:
        logger.exception("Error getting user info")
        raise HTTPException(status_code=500, detail="Failed to get user information. Please try again later.")

@router.put("/me", response_model=ProfileResponse, summary="Update user profile", description="Update the authenticated user's profile information.")
def update_profile(profile_update: ProfileUpdateRequest, db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    """Update the authenticated user's profile information."""
    try:
        # Get or create profile
        profile = db.query(UserProfiles).filter(UserProfiles.user_id == user.id).first()
        if not profile:
            profile = UserProfiles(user_id=user.id)
            db.add(profile)
        
        # Update only provided fields
        update_data = profile_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
        
        profile.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(profile)
        
        logger.info(f"Profile updated for user {user.id}")
        return profile
    except Exception as e:
        logger.exception("Error updating profile")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update profile. Please try again later.")

@router.post("/me/avatar", response_model=AvatarUploadResponse, summary="Upload avatar", description="Upload a new avatar image for the authenticated user.")
def upload_avatar(file: UploadFile = File(..., description="Avatar image file"), db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    """Upload a new avatar image for the authenticated user."""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads/avatars"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        filename = f"avatar_{user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}{file_extension}"
        file_path = os.path.join(upload_dir, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Update profile
        profile = db.query(UserProfiles).filter(UserProfiles.user_id == user.id).first()
        if not profile:
            profile = UserProfiles(user_id=user.id)
            db.add(profile)
        
        profile.avatar = f"/uploads/avatars/{filename}"
        profile.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Avatar uploaded for user {user.id}")
        return {"message": "Avatar uploaded successfully", "avatar_url": profile.avatar}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error uploading avatar")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to upload avatar. Please try again later.")

@router.delete("/me/avatar", response_model=AvatarDeleteResponse, summary="Delete avatar", description="Delete the authenticated user's avatar image.")
def delete_avatar(db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    """Delete the authenticated user's avatar image."""
    try:
        profile = db.query(UserProfiles).filter(UserProfiles.user_id == user.id).first()
        if profile and profile.avatar:
            # Delete file if it exists
            avatar_path = profile.avatar.lstrip('/')
            if os.path.exists(avatar_path):
                os.remove(avatar_path)
            
            profile.avatar = None
            profile.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Avatar deleted for user {user.id}")
            return {"message": "Avatar deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="No avatar found")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error deleting avatar")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete avatar. Please try again later.")

@router.get("/me/stats", response_model=UserStatsResponse, summary="Get user stats", description="Get statistics for the authenticated user's account (jobs, leads, etc.).")
def get_user_stats(db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    """Get statistics for the authenticated user's account (jobs, leads, etc.)."""
    try:
        # Get user statistics
        total_jobs = db.query(Jobs).filter(Jobs.user_id == user.id).count()
        completed_jobs = db.query(Jobs).filter(Jobs.user_id == user.id, Jobs.status == 'completed').count()
        total_leads = db.query(Leads).filter(Leads.user_id == user.id).count()
        
        # Calculate success rate
        success_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
        
        return {
            "total_jobs": total_jobs,
            "completed_jobs": completed_jobs,
            "success_rate": round(success_rate, 2),
            "total_leads": total_leads,
            "account_age_days": (datetime.utcnow() - user.created_at).days
        }
    except Exception as e:
        logger.exception("Error getting user stats")
        raise HTTPException(status_code=500, detail="Failed to get user statistics. Please try again later.")

@router.post("/export-data", response_model=ExportDataResponse, summary="Export user data", description="Export all data related to the authenticated user's account.")
def export_data(db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    """Export all data related to the authenticated user's account."""
    # Gather user data (profile, jobs, leads, etc.)
    jobs = db.query(Jobs).filter(Jobs.user_id == user.id).all()
    leads = db.query(Leads).filter(Leads.user_id == user.id).all()
    crm_notes = getattr(user, 'notes', None)
    data = {
        "user": {"id": user.id, "email": user.email, "plan": user.plan, "created_at": str(user.created_at)},
        "jobs": [dict(id=j.id, status=j.status, queries=j.queries, created_at=str(j.created_at)) for j in jobs],
        "leads": [dict(id=l.id, name=l.name, email=l.email, company=l.company, created_at=str(l.created_at)) for l in leads],
        "notes": crm_notes,
    }
    return JSONResponse(content=data)

@router.post("/delete-account", response_model=DeleteAccountResponse, summary="Delete user account", description="Delete the authenticated user's account.")
@audit_log(action="delete_account", target_type="user")
def delete_account(db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    """Delete the authenticated user's account."""
    # For demo, delete immediately (real: mark for deletion, delay, admin review)
    db.delete(user)
    db.commit()
    return DeleteAccountResponse(status="deleted") 

@router.get("/referral", response_model=ReferralInfoResponse, summary="Get referral info", description="Get the authenticated user's referral code and stats.")
def get_referral_info(db: Session = Depends(get_db), user: Users = Depends(get_current_user), request: Request = None):
    """Get the authenticated user's referral code and stats."""
    if not user.referral_code:
        # Generate a referral code if not present
        code = secrets.token_urlsafe(8)
        user.referral_code = code
        db.commit()
    base_url = request.base_url._url.rstrip('/') if request else 'http://localhost:8000'
    link = f"{base_url}/register?ref={user.referral_code}"
    referred_count = db.query(Users).filter(Users.referred_by == user.id).count()
    return {
        "referral_code": user.referral_code,
        "referral_link": link,
        "referred_count": referred_count,
        "referral_credits": user.referral_credits
    }

@router.post("/referral/use", response_model=ReferralUseResponse, summary="Use referral code", description="Apply a referral code to the authenticated user's account.")
def use_referral_code(code: str = Body(..., description="Referral code to apply"), db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    """Apply a referral code to the authenticated user's account."""
    if user.referred_by:
        raise HTTPException(status_code=400, detail="Referral already used")
    referrer = db.query(Users).filter(Users.referral_code == code).first()
    if not referrer or referrer.id == user.id:
        raise HTTPException(status_code=400, detail="Invalid referral code")
    user.referred_by = referrer.id
    user.referral_credits += 10  # Bonus for being referred
    referrer.referral_credits += 20  # Bonus for referrer
    db.commit()
    return {"status": "referral applied", "referrer": referrer.email, "credits": user.referral_credits}

@router.get("/referral/stats", response_model=ReferralStatsResponse, summary="Get referral stats", description="Get stats for users referred by the authenticated user.")
def get_referral_stats(db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    """Get stats for users referred by the authenticated user."""
    referred_users = db.query(Users).filter(Users.referred_by == user.id).all()
    return {
        "referred": [
            {"email": u.email, "created_at": u.created_at, "credits": u.referral_credits}
            for u in referred_users
        ],
        "total_credits": user.referral_credits
    } 

@router.get("/usage", response_model=UsageResponse, summary="Get usage", description="Get usage statistics for the authenticated user.")
def get_usage(db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    # Count jobs and exports (stub: jobs only)
    today = datetime.utcnow().date()
    jobs_today = db.query(Jobs).filter(Jobs.user_id == user.id, Jobs.created_at >= today).count()
    plan = user.plan
    plan_limits = {
        'free': {'max_queries_per_day': 10, 'max_results_per_query': 10},
        'pro': {'max_queries_per_day': 100, 'max_results_per_query': 100},
        'business': {'max_queries_per_day': 1000000, 'max_results_per_query': 10000},
    }.get(plan, {'max_queries_per_day': 10, 'max_results_per_query': 10})
    return {
        'plan': plan,
        'jobs_today': jobs_today,
        'max_queries_per_day': plan_limits['max_queries_per_day'],
        'usage_credits': user.usage_credits,
        'referral_credits': user.referral_credits
    }

@router.post("/credits/purchase", response_model=CreditsPurchaseResponse, summary="Purchase credits", description="Purchase additional credits for the authenticated user.")
def purchase_credits(amount: int = Body(..., description="Amount of credits to purchase"), db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    # Simulate payment and add credits
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    user.usage_credits += amount
    db.commit()
    return {"status": "credits added", "usage_credits": user.usage_credits} 