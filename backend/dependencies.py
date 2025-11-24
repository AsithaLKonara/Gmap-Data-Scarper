"""FastAPI dependencies for database and other shared resources."""
from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Generator
from backend.models.database import get_session


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency.
    
    Provides a database session that is automatically closed after the request.
    Use this as a dependency in route handlers:
    
    @router.get("/items")
    async def get_items(db: Session = Depends(get_db)):
        return db.query(Item).all()
    """
    db = get_session()
    try:
        yield db
    finally:
        db.close()

