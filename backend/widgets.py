from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from models import User, WidgetSubmission, Testimonial
from database import get_db
from auth import get_current_user
import secrets
from datetime import datetime

router = APIRouter(prefix="/api/widgets", tags=["widgets"])

class WidgetConfig(BaseModel):
    type: str  # 'lead_capture' or 'testimonial'
    color: Optional[str] = "#3182CE"
    title: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[List[str]] = ["name", "email", "message"]

class WidgetCodeResponse(BaseModel):
    widget_id: str
    embed_code: str
    preview_url: str

class WidgetSubmissionIn(BaseModel):
    widget_id: str
    data: Dict[str, Any]

class WidgetSubmissionOut(BaseModel):
    id: int
    widget_id: str
    data: Dict[str, Any]
    created_at: datetime

@router.post("/generate", response_model=WidgetCodeResponse)
def generate_widget_code(
    config: WidgetConfig,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Generate embeddable widget code for lead capture or testimonials."""
    widget_id = secrets.token_urlsafe(8)
    # Store widget config in DB (optional, not shown)
    embed_code = f'<iframe src="https://leadtap.com/widget/{widget_id}" width="400" height="600" style="border:none;"></iframe>'
    preview_url = f"https://leadtap.com/widget/{widget_id}/preview"
    return WidgetCodeResponse(widget_id=widget_id, embed_code=embed_code, preview_url=preview_url)

@router.post("/submit", response_model=WidgetSubmissionOut)
def submit_widget(
    submission: WidgetSubmissionIn,
    request: Request,
    db: Session = Depends(get_db)
):
    """Receive a submission from an embeddable widget (lead or testimonial)."""
    widget_submission = WidgetSubmission(
        widget_id=submission.widget_id,
        data=submission.data,
        ip_address=request.client.host,
        created_at=datetime.utcnow()
    )
    db.add(widget_submission)
    db.commit()
    db.refresh(widget_submission)
    return WidgetSubmissionOut(
        id=widget_submission.id,
        widget_id=widget_submission.widget_id,
        data=widget_submission.data,
        created_at=widget_submission.created_at
    )

@router.get("/submissions", response_model=List[WidgetSubmissionOut])
def get_widget_submissions(
    widget_id: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get all submissions for a user's widgets."""
    query = db.query(WidgetSubmission)
    if widget_id:
        query = query.filter(WidgetSubmission.widget_id == widget_id)
    # Optionally filter by user ownership
    submissions = query.order_by(WidgetSubmission.created_at.desc()).all()
    return [
        WidgetSubmissionOut(
            id=s.id,
            widget_id=s.widget_id,
            data=s.data,
            created_at=s.created_at
        ) for s in submissions
    ] 