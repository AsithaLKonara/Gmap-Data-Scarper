import json
import asyncio
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Job
from webhook_utils import send_webhook_event

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
        # Trigger webhook for job completion
        send_webhook_event(
            event="job.completed",
            payload={
                "job_id": job.id,
                "status": job.status,
                "user_id": job.user_id,
                "queries": job.queries,
                "completed_at": str(job.updated_at)
            },
            user_id=job.user_id,
            db=db
        )
    except Exception as e:
        job.status = "failed"
        db.commit()
    finally:
        db.close() 