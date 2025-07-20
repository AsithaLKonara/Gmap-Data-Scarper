from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from models import Users, Testimonials
from database import get_db
from auth import get_current_user
from datetime import datetime

router = APIRouter(prefix="/api/showcase", tags=["showcase"])

class TestimonialIn(BaseModel):
    name: str = Field(..., description="Name of the person giving the testimonial.", example="Alice Smith")
    company: Optional[str] = Field(None, description="Company or organization.", example="Acme Inc.")
    message: str = Field(..., description="Testimonial message.", example="LeadTap helped us grow our business!")
    avatar_url: Optional[str] = Field(None, description="URL to the avatar image.", example="https://example.com/avatar.jpg")
    featured: bool = Field(False, description="Whether this testimonial is featured.")

class TestimonialOut(BaseModel):
    id: int = Field(..., description="Unique identifier for the testimonial.")
    name: str = Field(..., description="Name of the person giving the testimonial.")
    company: Optional[str] = Field(None, description="Company or organization.")
    message: str = Field(..., description="Testimonial message.")
    avatar_url: Optional[str] = Field(None, description="URL to the avatar image.")
    featured: bool = Field(..., description="Whether this testimonial is featured.")
    created_at: datetime = Field(..., description="Timestamp when the testimonial was created.")

@router.post(
    "/testimonials",
    response_model=TestimonialOut,
    summary="Submit a testimonial",
    description="Submit a new testimonial. User authentication required."
)
def submit_testimonial(
    testimonial: TestimonialIn,
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Submit a new testimonial (user-authenticated)."""
    t = Testimonials(
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

@router.get(
    "/testimonials",
    response_model=List[TestimonialOut],
    summary="List testimonials",
    description="List public testimonials. Optionally filter by featured status."
)
def list_testimonials(
    featured: Optional[bool] = Field(None, description="If true, only return featured testimonials."),
    db: Session = Depends(get_db)
):
    """List public testimonials (optionally only featured)."""
    query = db.query(Testimonials)
    if featured is not None:
        query = query.filter(Testimonials.featured == featured)
    testimonials = query.order_by(Testimonials.created_at.desc()).all()
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