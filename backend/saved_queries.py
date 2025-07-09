from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from models import SavedQuery, User
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/api/saved-queries", tags=["saved-queries"])

class SavedQueryIn(BaseModel):
    name: str
    queries: List[str]

class SavedQueryOut(BaseModel):
    id: int
    name: str
    queries: List[str]
    created_at: str
    updated_at: str = None

    class Config:
        orm_mode = True

@router.get("/", response_model=List[SavedQueryOut])
def list_saved_queries(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(SavedQuery).filter(SavedQuery.user_id == user.id).order_by(SavedQuery.created_at.desc()).all()

@router.post("/", response_model=SavedQueryOut)
def create_saved_query(data: SavedQueryIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    sq = SavedQuery(user_id=user.id, name=data.name, queries=data.queries)
    db.add(sq)
    db.commit()
    db.refresh(sq)
    return sq

@router.put("/{query_id}", response_model=SavedQueryOut)
def update_saved_query(query_id: int, data: SavedQueryIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    sq = db.query(SavedQuery).filter(SavedQuery.id == query_id, SavedQuery.user_id == user.id).first()
    if not sq:
        raise HTTPException(status_code=404, detail="Saved query not found")
    sq.name = data.name
    sq.queries = data.queries
    db.commit()
    db.refresh(sq)
    return sq

@router.delete("/{query_id}")
def delete_saved_query(query_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    sq = db.query(SavedQuery).filter(SavedQuery.id == query_id, SavedQuery.user_id == user.id).first()
    if not sq:
        raise HTTPException(status_code=404, detail="Saved query not found")
    db.delete(sq)
    db.commit()
    return {"status": "deleted"} 