from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from models import User, Job, ScheduledJob
from database import get_db
from auth import get_current_user
import logging
import json
import asyncio
from datetime import datetime, timedelta
from enum import Enum
import schedule
import time
import threading

logger = logging.getLogger("scheduler")

router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])

class ScheduleType(str, Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class Priority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class ScheduledJobCreate(BaseModel):
    name: str
    queries: List[str]
    schedule_type: ScheduleType
    schedule_config: Dict[str, Any]  # cron expression or specific times
    priority: Priority = Priority.NORMAL
    max_retries: int = 3
    enabled: bool = True

class ScheduledJobResponse(BaseModel):
    id: int
    name: str
    queries: List[str]
    schedule_type: ScheduleType
    schedule_config: Dict[str, Any]
    priority: Priority
    max_retries: int
    enabled: bool
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    total_runs: int
    successful_runs: int
    failed_runs: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ScheduledJobIn(BaseModel):
    name: str
    queries: List[str]
    schedule: str
    active: bool = True

class ScheduledJobOut(BaseModel):
    id: int
    name: str
    queries: List[str]
    schedule: str
    active: bool
    last_run: str = None
    next_run: str = None
    created_at: str
    class Config:
        orm_mode = True

# In-memory scheduler (in production, use Redis or database)
scheduled_jobs: Dict[int, Dict] = {}
job_queue = asyncio.Queue()

class JobScheduler:
    def __init__(self):
        self.running = False
        self.thread = None
        
    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_scheduler)
            self.thread.daemon = True
            self.thread.start()
            logger.info("Job scheduler started")
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Job scheduler stopped")
    
    def _run_scheduler(self):
        while self.running:
            try:
                # Check for jobs that need to run
                current_time = datetime.utcnow()
                for job_id, job_data in scheduled_jobs.items():
                    if not job_data['enabled']:
                        continue
                    
                    next_run = job_data.get('next_run')
                    if next_run and current_time >= next_run:
                        # Schedule job for execution
                        asyncio.run(self._execute_scheduled_job(job_id, job_data))
                        
                        # Calculate next run time
                        self._calculate_next_run(job_id, job_data)
                
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.exception("Error in scheduler loop")
                time.sleep(60)
    
    async def _execute_scheduled_job(self, job_id: int, job_data: Dict):
        try:
            logger.info(f"Executing scheduled job {job_id}: {job_data['name']}")
            
            # Create actual job
            from jobs import create_job_internal
            job_result = await create_job_internal(
                queries=job_data['queries'],
                user_id=job_data['user_id'],
                priority=job_data['priority']
            )
            
            # Update job statistics
            job_data['last_run'] = datetime.utcnow()
            job_data['total_runs'] += 1
            job_data['successful_runs'] += 1
            
            logger.info(f"Scheduled job {job_id} executed successfully")
            
        except Exception as e:
            logger.exception(f"Error executing scheduled job {job_id}")
            job_data['failed_runs'] += 1
            
            # Retry logic
            if job_data['failed_runs'] < job_data['max_retries']:
                # Schedule retry with exponential backoff
                retry_delay = 2 ** job_data['failed_runs'] * 60  # minutes
                job_data['next_run'] = datetime.utcnow() + timedelta(minutes=retry_delay)
            else:
                job_data['enabled'] = False
                logger.error(f"Scheduled job {job_id} disabled after max retries")
    
    def _calculate_next_run(self, job_id: int, job_data: Dict):
        schedule_type = job_data['schedule_type']
        config = job_data['schedule_config']
        
        if schedule_type == ScheduleType.ONCE:
            job_data['next_run'] = None
        elif schedule_type == ScheduleType.DAILY:
            hour = config.get('hour', 9)
            minute = config.get('minute', 0)
            next_run = datetime.utcnow().replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= datetime.utcnow():
                next_run += timedelta(days=1)
            job_data['next_run'] = next_run
        elif schedule_type == ScheduleType.WEEKLY:
            day_of_week = config.get('day_of_week', 0)  # Monday = 0
            hour = config.get('hour', 9)
            minute = config.get('minute', 0)
            current_weekday = datetime.utcnow().weekday()
            days_ahead = (day_of_week - current_weekday) % 7
            next_run = datetime.utcnow().replace(hour=hour, minute=minute, second=0, microsecond=0)
            next_run += timedelta(days=days_ahead)
            job_data['next_run'] = next_run
        elif schedule_type == ScheduleType.MONTHLY:
            day_of_month = config.get('day_of_month', 1)
            hour = config.get('hour', 9)
            minute = config.get('minute', 0)
            next_run = datetime.utcnow().replace(day=day_of_month, hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= datetime.utcnow():
                # Move to next month
                if next_run.month == 12:
                    next_run = next_run.replace(year=next_run.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=next_run.month + 1)
            job_data['next_run'] = next_run

# Initialize scheduler
scheduler = JobScheduler()

@router.post("/jobs", response_model=ScheduledJobResponse)
def create_scheduled_job(
    job: ScheduledJobCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    try:
        # Validate schedule configuration
        if job.schedule_type == ScheduleType.DAILY:
            if 'hour' not in job.schedule_config:
                raise HTTPException(status_code=400, detail="Daily schedule requires 'hour' configuration")
        elif job.schedule_type == ScheduleType.WEEKLY:
            if 'day_of_week' not in job.schedule_config:
                raise HTTPException(status_code=400, detail="Weekly schedule requires 'day_of_week' configuration")
        elif job.schedule_type == ScheduleType.MONTHLY:
            if 'day_of_month' not in job.schedule_config:
                raise HTTPException(status_code=400, detail="Monthly schedule requires 'day_of_month' configuration")
        
        # Create job data
        job_id = len(scheduled_jobs) + 1
        job_data = {
            'id': job_id,
            'name': job.name,
            'queries': job.queries,
            'schedule_type': job.schedule_type,
            'schedule_config': job.schedule_config,
            'priority': job.priority,
            'max_retries': job.max_retries,
            'enabled': job.enabled,
            'user_id': user.id,
            'last_run': None,
            'next_run': None,
            'total_runs': 0,
            'successful_runs': 0,
            'failed_runs': 0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }
        
        # Calculate first run time
        scheduler._calculate_next_run(job_id, job_data)
        
        # Store job
        scheduled_jobs[job_id] = job_data
        
        logger.info(f"Scheduled job created: {job_id} by user {user.id}")
        
        return job_data
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error creating scheduled job")
        raise HTTPException(status_code=500, detail="Failed to create scheduled job")

@router.get("/jobs", response_model=List[ScheduledJobResponse])
def get_scheduled_jobs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        # Filter jobs by user
        user_jobs = [
            job_data for job_data in scheduled_jobs.values()
            if job_data['user_id'] == user.id
        ]
        return user_jobs
    except Exception as e:
        logger.exception("Error getting scheduled jobs")
        raise HTTPException(status_code=500, detail="Failed to get scheduled jobs")

@router.get("/jobs/{job_id}", response_model=ScheduledJobResponse)
def get_scheduled_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        job_data = scheduled_jobs.get(job_id)
        if not job_data or job_data['user_id'] != user.id:
            raise HTTPException(status_code=404, detail="Scheduled job not found")
        return job_data
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting scheduled job")
        raise HTTPException(status_code=500, detail="Failed to get scheduled job")

@router.put("/jobs/{job_id}")
def update_scheduled_job(
    job_id: int,
    job_update: ScheduledJobCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    try:
        job_data = scheduled_jobs.get(job_id)
        if not job_data or job_data['user_id'] != user.id:
            raise HTTPException(status_code=404, detail="Scheduled job not found")
        
        # Update job data
        job_data.update({
            'name': job_update.name,
            'queries': job_update.queries,
            'schedule_type': job_update.schedule_type,
            'schedule_config': job_update.schedule_config,
            'priority': job_update.priority,
            'max_retries': job_update.max_retries,
            'enabled': job_update.enabled,
            'updated_at': datetime.utcnow(),
        })
        
        # Recalculate next run time
        scheduler._calculate_next_run(job_id, job_data)
        
        logger.info(f"Scheduled job updated: {job_id} by user {user.id}")
        return {"message": "Scheduled job updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error updating scheduled job")
        raise HTTPException(status_code=500, detail="Failed to update scheduled job")

@router.delete("/jobs/{job_id}")
def delete_scheduled_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        job_data = scheduled_jobs.get(job_id)
        if not job_data or job_data['user_id'] != user.id:
            raise HTTPException(status_code=404, detail="Scheduled job not found")
        
        del scheduled_jobs[job_id]
        
        logger.info(f"Scheduled job deleted: {job_id} by user {user.id}")
        return {"message": "Scheduled job deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error deleting scheduled job")
        raise HTTPException(status_code=500, detail="Failed to delete scheduled job")

@router.post("/jobs/{job_id}/run")
def run_scheduled_job_now(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        job_data = scheduled_jobs.get(job_id)
        if not job_data or job_data['user_id'] != user.id:
            raise HTTPException(status_code=404, detail="Scheduled job not found")
        
        # Execute job immediately
        asyncio.create_task(scheduler._execute_scheduled_job(job_id, job_data))
        
        logger.info(f"Scheduled job executed manually: {job_id} by user {user.id}")
        return {"message": "Scheduled job execution started"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error running scheduled job")
        raise HTTPException(status_code=500, detail="Failed to run scheduled job")

@router.post("/jobs/{job_id}/toggle")
def toggle_scheduled_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        job_data = scheduled_jobs.get(job_id)
        if not job_data or job_data['user_id'] != user.id:
            raise HTTPException(status_code=404, detail="Scheduled job not found")
        
        job_data['enabled'] = not job_data['enabled']
        job_data['updated_at'] = datetime.utcnow()
        
        if job_data['enabled']:
            scheduler._calculate_next_run(job_id, job_data)
        
        logger.info(f"Scheduled job toggled: {job_id} by user {user.id}")
        return {"message": f"Scheduled job {'enabled' if job_data['enabled'] else 'disabled'}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error toggling scheduled job")
        raise HTTPException(status_code=500, detail="Failed to toggle scheduled job")

@router.get("/", response_model=List[ScheduledJobOut])
def list_scheduled_jobs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(ScheduledJob).filter(ScheduledJob.user_id == user.id).order_by(ScheduledJob.created_at.desc()).all()

@router.post("/", response_model=ScheduledJobOut)
def create_scheduled_job(data: ScheduledJobIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    sj = ScheduledJob(user_id=user.id, name=data.name, queries=data.queries, schedule=data.schedule, active=data.active)
    db.add(sj)
    db.commit()
    db.refresh(sj)
    return sj

@router.put("/{job_id}", response_model=ScheduledJobOut)
def update_scheduled_job(job_id: int, data: ScheduledJobIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    sj = db.query(ScheduledJob).filter(ScheduledJob.id == job_id, ScheduledJob.user_id == user.id).first()
    if not sj:
        raise HTTPException(status_code=404, detail="Scheduled job not found")
    sj.name = data.name
    sj.queries = data.queries
    sj.schedule = data.schedule
    sj.active = data.active
    db.commit()
    db.refresh(sj)
    return sj

@router.delete("/{job_id}")
def delete_scheduled_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    sj = db.query(ScheduledJob).filter(ScheduledJob.id == job_id, ScheduledJob.user_id == user.id).first()
    if not sj:
        raise HTTPException(status_code=404, detail="Scheduled job not found")
    db.delete(sj)
    db.commit()
    return {"status": "deleted"}

@router.post("/{job_id}/activate")
def activate_scheduled_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    sj = db.query(ScheduledJob).filter(ScheduledJob.id == job_id, ScheduledJob.user_id == user.id).first()
    if not sj:
        raise HTTPException(status_code=404, detail="Scheduled job not found")
    sj.active = True
    db.commit()
    return {"status": "activated"}

@router.post("/{job_id}/deactivate")
def deactivate_scheduled_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    sj = db.query(ScheduledJob).filter(ScheduledJob.id == job_id, ScheduledJob.user_id == user.id).first()
    if not sj:
        raise HTTPException(status_code=404, detail="Scheduled job not found")
    sj.active = False
    db.commit()
    return {"status": "deactivated"}

# Start scheduler on module import
scheduler.start() 