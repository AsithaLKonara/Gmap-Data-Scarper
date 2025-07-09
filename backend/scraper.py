import json
import asyncio
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Job

def run_scraper(job_id: int):
    db: Session = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        db.close()
        return
    try:
        job.status = "running"
        db.commit()
        # TODO: Implement real scraping logic here using job.queries
        # Placeholder: Set job.result to an empty list until real logic is implemented
        job.result = json.dumps([])
        job.status = "completed"
        db.commit()
    except Exception as e:
        job.status = "failed"
        db.commit()
    finally:
        db.close() 