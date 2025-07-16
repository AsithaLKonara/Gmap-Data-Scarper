from fastapi import APIRouter, Depends, HTTPException, Request, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List
from models import SavedQuery, User
from database import get_db
from auth import get_current_user
from tenant_utils import get_tenant_record_or_403, get_tenant_from_request
from audit import audit_log

router = APIRouter(prefix="/api/saved-queries", tags=["saved-queries"])

# --- Pydantic Models for OpenAPI ---
class SavedQueryIn(BaseModel):
    name: str = Field(..., description="Name of the saved query.")
    queries: List[str] = Field(..., description="List of queries in the saved query.")

class SavedQueryOut(BaseModel):
    id: int
    name: str
    queries: List[str]
    created_at: str
    updated_at: str = None
    class Config:
        orm_mode = True

class DeleteSavedQueryResponse(BaseModel):
    status: str

@router.get("/", response_model=List[SavedQueryOut], summary="List saved queries", description="List all saved queries for the current user.")
def list_saved_queries(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """List all saved queries for the current user."""
    return db.query(SavedQuery).filter(SavedQuery.user_id == user.id).order_by(SavedQuery.created_at.desc()).all()

@router.post("/", response_model=SavedQueryOut, summary="Create saved query", description="Create a new saved query for the current user.")
def create_saved_query(data: SavedQueryIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Create a new saved query for the current user."""
    sq = SavedQuery(user_id=user.id, name=data.name, queries=data.queries)
    db.add(sq)
    db.commit()
    db.refresh(sq)
    return sq

@router.put("/{query_id}", response_model=SavedQueryOut, summary="Update saved query", description="Update a saved query by ID.")
def update_saved_query(query_id: int = Field(..., description="ID of the saved query."), data: SavedQueryIn = Body(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Update a saved query by ID."""
    sq = db.query(SavedQuery).filter(SavedQuery.id == query_id, SavedQuery.user_id == user.id).first()
    if not sq:
        raise HTTPException(status_code=404, detail="Saved query not found")
    sq.name = data.name
    sq.queries = data.queries
    db.commit()
    db.refresh(sq)
    return sq

@router.delete("/{query_id}", response_model=DeleteSavedQueryResponse, summary="Delete saved query", description="Delete a saved query by ID.")
@audit_log(action="delete_saved_query", target_type="saved_query", target_id_param="query_id")
def delete_saved_query(query_id: int = Field(..., description="ID of the saved query."), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Delete a saved query by ID."""
    sq = db.query(SavedQuery).filter(SavedQuery.id == query_id, SavedQuery.user_id == user.id).first()
    if not sq:
        raise HTTPException(status_code=404, detail="Saved query not found")
    db.delete(sq)
    db.commit()
    return DeleteSavedQueryResponse(status="deleted")

@router.get("/saved_queries/{query_id}", response_model=SavedQueryOut, summary="Get saved query", description="Get a saved query by ID.")
def get_saved_query(query_id: int = Field(..., description="ID of the saved query."), request: Request = None, db: Session = Depends(get_db)):
    """Get a saved query by ID."""
    tenant = get_tenant_from_request(request, db)
    query = get_tenant_record_or_403(SavedQuery, query_id, tenant.id, db)
    return query 