from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Query, Body, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
import os
from datetime import datetime, timezone
from models import Job, User
from database import get_db
from auth import get_current_user
from scraper import run_scraper
from fastapi.responses import StreamingResponse
import logging
import secrets
from tenant_utils import get_tenant_from_request
from security import check_permission

router = APIRouter(prefix="/api/scrape", tags=["scrape"])

# Setup logging for exceptions
logger = logging.getLogger("jobs")

PLAN_LIMITS = {
    'free': {'max_queries_per_day': 3, 'max_results_per_query': 5},
    'pro': {'max_queries_per_day': 50, 'max_results_per_query': 50},
    'business': {'max_queries_per_day': 500, 'max_results_per_query': 200},
}

class ScrapeRequest(BaseModel):
    queries: List[str] = Field(..., description="List of Google Maps search queries to run.", example=["coffee shops in New York", "bookstores in San Francisco"])

class JobStatus(BaseModel):
    job_id: int = Field(..., description="ID of the scraping job.")
    status: str = Field(..., description="Current status of the job (pending, running, completed, failed, etc.)")

class JobResult(BaseModel):
    job_id: int = Field(..., description="ID of the scraping job.")
    status: str = Field(..., description="Current status of the job.")
    result: List[Dict[str, Any]] = Field(..., description="List of result objects for the job.")

class BulkDeleteRequest(BaseModel):
    job_ids: List[int] = Field(..., description="List of job IDs to delete.", example=[1,2,3])

class BulkDeleteResponse(BaseModel):
    deleted: int = Field(..., description="Number of jobs deleted.")

@router.post("/", response_model=JobStatus, summary="Create a new scraping job", description="Create a new Google Maps scraping job for the authenticated user.")
def create_scrape_job(req: ScrapeRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Create a new Google Maps scraping job for the authenticated user.\n\n- **queries**: List of search queries (one per line or array).\n- **Returns**: Job ID and status.\n- **Errors**: 403 if plan limits exceeded."""
    try:
        print(f"📝 [JOB] Creating new scraping job - User: {user.email}, Queries: {len(req.queries)}")
        
        plan = user.plan or 'free'
        limits = PLAN_LIMITS.get(plan, PLAN_LIMITS['free'])
        now = datetime.now(timezone.utc)
        # Reset daily usage if new day
        if not user.last_query_date or user.last_query_date.date() != now.date():
            user.queries_today = 0
            user.last_query_date = now
        if user.queries_today >= limits['max_queries_per_day']:
            print(f"❌ [JOB] Job creation failed - User {user.email} has reached daily limit ({limits['max_queries_per_day']})")
            raise HTTPException(status_code=403, detail=f"Daily query limit reached for your plan ({limits['max_queries_per_day']})")
        if len(req.queries) > limits['max_results_per_query']:
            raise HTTPException(status_code=403, detail=f"Max results per query exceeded for your plan ({limits['max_results_per_query']})")
        user.queries_today += 1
        user.last_query_date = now
        db.commit()
        job = Job(queries=json.dumps(req.queries), status="pending", user_id=user.id)
        db.add(job)
        db.commit()
        db.refresh(job)
        background_tasks.add_task(run_scraper, job.id)
        print(f"🎉 [JOB] Job created successfully - ID: {job.id}, User: {user.email}, Status: {job.status}")
        print(f"📊 [JOB] Updated user query count - {user.email}: {user.queries_today} queries today")
        return {"job_id": job.id, "status": job.status}
    except Exception as e:
        logger.exception("Error creating scrape job")
        raise HTTPException(status_code=500, detail="Failed to create job. Please try again later.")

@router.post("/upgrade_plan", summary="Upgrade user plan", description="Upgrade the authenticated user's plan (free, pro, business).", response_model=Dict[str, str])
def upgrade_plan(new_plan: str = Body(..., description="New plan to upgrade to (free, pro, business)", example="pro"), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Upgrade the authenticated user's plan.\n\n- **new_plan**: Target plan (free, pro, business).\n- **Returns**: Status and new plan."""
    try:
        if new_plan not in PLAN_LIMITS:
            raise HTTPException(status_code=400, detail="Invalid plan")
        user.plan = new_plan
        db.commit()
        return {"status": "success", "new_plan": new_plan}
    except Exception as e:
        logger.exception("Error upgrading plan")
        raise

@router.get("/{job_id}/status", response_model=JobStatus, summary="Get job status", description="Get the status of a specific scraping job by job ID.")
def get_job_status(job_id: int = Field(..., description="ID of the job to check."), db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Get the status of a specific scraping job by job ID.\n\n- **job_id**: ID of the job.\n- **Returns**: Job ID and status.\n- **Errors**: 404 if job not found."""
    try:
        print(f"🔍 [JOB] Checking job status - Job ID: {job_id}, User: {user.email}")
        
        job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
        if not job:
            print(f"❌ [JOB] Job not found - ID: {job_id}")
            raise HTTPException(status_code=404, detail="Job not found")
        
        print(f"✅ [JOB] Job found - ID: {job.id}, Status: {job.status}, User: {user.email}")
        
        return {"job_id": job.id, "status": job.status}
    except Exception as e:
        print(f"❌ [JOB] Job status check failed - Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get job status")

@router.get("/{job_id}/results", response_model=JobResult, summary="Get job results", description="Get the results of a completed scraping job by job ID. Supports filtering by status, company, and date range.")
def get_job_results(
    job_id: int = Field(..., description="ID of the job to get results for."),
    status: Optional[str] = Query(None, description="Filter results by status (completed, failed, etc.)"),
    company: Optional[str] = Query(None, description="Filter results by company name"),
    date_from: Optional[str] = Query(None, description="Filter results from this date (ISO format)"),
    date_to: Optional[str] = Query(None, description="Filter results up to this date (ISO format)"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Get the results of a completed scraping job by job ID.\n\n- **job_id**: ID of the job.\n- **status/company/date_from/date_to**: Optional filters.\n- **Returns**: Job ID, status, and result list.\n- **Errors**: 404 if job/results not found."""
    try:
        print(f"📋 [JOB] Getting job results - Job ID: {job_id}, User: {user.email}")
        job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
        if not job or not job.result:
            print(f"❌ [JOB] Job not found - ID: {job_id}")
            raise HTTPException(status_code=404, detail="Results not found")
        print(f"✅ [JOB] Job found - ID: {job.id}, Status: {job.status}, User: {user.email}")
        if job.status != "completed":
            print(f"⚠️ [JOB] Job not completed yet - Status: {job.status}")
            return {"status": job.status, "message": "Job not completed yet"}
        results = json.loads(job.result)
        # Apply filters if provided
        if status:
            results = [r for r in results if r.get("status", "").lower() == status.lower()]
        if company:
            results = [r for r in results if company.lower() in r.get("company", "").lower()]
        if date_from:
            try:
                date_from_dt = datetime.fromisoformat(date_from)
                results = [r for r in results if r.get("created_at") and datetime.fromisoformat(r["created_at"]) >= date_from_dt]
            except Exception:
                pass
        if date_to:
            try:
                date_to_dt = datetime.fromisoformat(date_to)
                results = [r for r in results if r.get("created_at") and datetime.fromisoformat(r["created_at"]) <= date_to_dt]
            except Exception:
                pass
        print(f"📊 [JOB] Returning filtered job results - ID: {job.id}, Count: {len(results)}")
        return {"job_id": job.id, "status": job.status, "result": results}
    except Exception as e:
        print(f"❌ [JOB] Job results retrieval failed - Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get job results")

@router.get("/{job_id}/csv", summary="Download job results as CSV", description="Download the results of a completed scraping job as a CSV file.")
def download_csv(job_id: int = Field(..., description="ID of the job to download CSV for."), db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Download the results of a completed scraping job as a CSV file.\n\n- **job_id**: ID of the job.\n- **Returns**: CSV file.\n- **Errors**: 404 if CSV not found."""
    try:
        print(f"📄 [JOB] Getting job CSV - Job ID: {job_id}, User: {user.email}")
        
        job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
        if not job or not job.csv_path or not os.path.exists(job.csv_path):
            print(f"❌ [JOB] CSV not found - ID: {job_id}")
            raise HTTPException(status_code=404, detail="CSV not found")
        
        print(f"✅ [JOB] Job found - ID: {job.id}, Status: {job.status}, User: {user.email}")
        
        def generate():
            with open(job.csv_path, 'r') as f:
                yield from f
        
        return StreamingResponse(generate(), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=gmap_leads_{job_id}.csv"})
    except Exception as e:
        print(f"❌ [JOB] CSV download failed - Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to download CSV")

@router.get("/jobs", summary="List user jobs", description="List all scraping jobs for the authenticated user.", response_model=Dict[str, Any])
def list_user_jobs(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """List all scraping jobs for the authenticated user.\n\n- **Returns**: List of jobs with ID, queries, status, created/updated timestamps."""
    tenant = get_tenant_from_request(request, db)
    try:
        jobs = db.query(Job).filter(Job.user_id == user.id).order_by(Job.id.desc()).all()
        return {
            "jobs": [
                {
                    "id": job.id,
                    "queries": json.loads(job.queries),
                    "status": job.status,
                    "created_at": job.created_at,
                    "updated_at": job.updated_at
                }
                for job in jobs
            ]
        }
    except Exception as e:
        print(f"❌ [JOB] Job listing failed - Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to list jobs")

@router.post("/bulk-delete", summary="Bulk delete jobs", description="Delete multiple scraping jobs by their IDs.", response_model=BulkDeleteResponse)
def bulk_delete_jobs(req: BulkDeleteRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # RBAC: Only allow if user has jobs:delete permission
    if not check_permission(user, "jobs", "delete", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions to bulk delete jobs")
    jobs = db.query(Job).filter(Job.id.in_(req.job_ids), Job.user_id == user.id).all()
    count = len(jobs)
    for job in jobs:
        db.delete(job)
    db.commit()
    return BulkDeleteResponse(deleted=count)

@router.post("/{job_id}/share", summary="Share a job", description="Generate a shareable link for a scraping job.", response_model=Dict[str, str])
def share_job(job_id: int = Field(..., description="ID of the job to share."), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Generate a shareable link for a scraping job.\n\n- **job_id**: ID of the job.\n- **Returns**: Shareable URL."""
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.share_token:
        return {"share_token": job.share_token, "url": f"/api/scrape/shared/{job.share_token}"}
    token = secrets.token_urlsafe(32)
    job.share_token = token
    db.commit()
    return {"share_token": token, "url": f"/api/scrape/shared/{token}"}

@router.post("/{job_id}/unshare", summary="Unshare a job", description="Disable the shareable link for a scraping job.", response_model=Dict[str, str])
def unshare_job(job_id: int = Field(..., description="ID of the job to unshare."), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Disable the shareable link for a scraping job.\n\n- **job_id**: ID of the job.\n- **Returns**: Status message."""
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.share_token = None
    db.commit()
    return {"status": "unshared"}

@router.get("/shared/{share_token}", summary="Get shared job", description="Get a shared scraping job by its share token.", response_model=Dict[str, Any])
def get_shared_job(share_token: str = Field(..., description="Share token for the job."), db: Session = Depends(get_db)):
    """Get a shared scraping job by its share token.\n\n- **share_token**: Token from the shareable link.\n- **Returns**: Job details if valid."""
    job = db.query(Job).filter(Job.share_token == share_token).first()
    if not job:
        raise HTTPException(status_code=404, detail="Shared job not found")
    return {"id": job.id, "queries": job.queries, "status": job.status, "result": job.result, "created_at": job.created_at, "updated_at": job.updated_at} 