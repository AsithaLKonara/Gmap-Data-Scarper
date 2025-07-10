from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from models import User, Testimonial
from database import get_db
from auth import get_current_user
from datetime import datetime

router = APIRouter(prefix="/api/showcase", tags=["showcase"])

class TestimonialIn(BaseModel):
    name: str
    company: Optional[str] = None
    message: str
    avatar_url: Optional[str] = None
    featured: bool = False

class TestimonialOut(BaseModel):
    id: int
    name: str
    company: Optional[str]
    message: str
    avatar_url: Optional[str]
    featured: bool
    created_at: datetime

@router.post("/testimonials", response_model=TestimonialOut)
def submit_testimonial(
    testimonial: TestimonialIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Submit a new testimonial (user-authenticated)."""
    t = Testimonial(
        user_id=user.id,
        name=testimonial.name,
        company=testimonial.company,
        message=testimonial.message,
        avatar_url=testimonial.avatar_url,
        featured=testimonial.featured,
        created_at=datetime.utcnow()
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return TestimonialOut(
        id=t.id,
        name=t.name,
        company=t.company,
        message=t.message,
        avatar_url=t.avatar_url,
        featured=t.featured,
        created_at=t.created_at
    )

@router.get("/testimonials", response_model=List[TestimonialOut])
def list_testimonials(
    featured: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List public testimonials (optionally only featured)."""
    query = db.query(Testimonial)
    if featured is not None:
        query = query.filter(Testimonial.featured == featured)
    testimonials = query.order_by(Testimonial.created_at.desc()).all()
    return [
        TestimonialOut(
            id=t.id,
            name=t.name,
            company=t.company,
            message=t.message,
            avatar_url=t.avatar_url,
            featured=t.featured,
            created_at=t.created_at
        ) for t in testimonials
    ] 