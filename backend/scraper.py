import json
import asyncio
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Jobs
from webhook_utils import send_webhook_event

def run_scraper(job_id: int):
    db: Session = SessionLocal()
    job = db.query(Jobs).filter(Jobs.id == job_id).first()
    if not job:
        db.close()
        return
    try:
        job.status = "running"
        db.commit()
        # Simulate scraping logic (replace with real scraping as needed)
        import time
        time.sleep(2)  # Simulate work
        dummy_results = [
            {"business_name": "Test Business", "address": "123 Main St", "phone": "123-456-7890", "website": "https://example.com"}
        ]
        job.result = json.dumps(dummy_results)
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