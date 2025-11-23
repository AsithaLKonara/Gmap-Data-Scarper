"""Celery tasks for scraping operations."""
from celery import Task
from typing import Dict, List, Optional
import sys
import os
import uuid

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.celery_app import celery_app
from orchestrator_core import run_orchestrator, StopFlag
from backend.models.schemas import ScrapeRequest
from backend.services.postgresql_storage import get_postgresql_storage


class ScrapingTask(Task):
    """Custom task class with retry logic."""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        print(f"[CELERY] Task {task_id} failed: {exc}")
        # Could emit WebSocket event here
    
    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success."""
        print(f"[CELERY] Task {task_id} completed successfully")


@celery_app.task(
    bind=True,
    base=ScrapingTask,
    name="backend.tasks.scraping_tasks.run_scraping_task",
    max_retries=3,
    default_retry_delay=60,  # Retry after 60 seconds
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,  # Max 10 minutes between retries
    retry_jitter=True,
)
def run_scraping_task(
    self,
    task_id: str,
    request_data: Dict,
    config_path: str,
    output_dir: str
) -> Dict:
    """
    Run a scraping task asynchronously.
    
    Args:
        task_id: Unique task identifier
        request_data: ScrapeRequest data as dictionary
        config_path: Path to YAML config file
        output_dir: Output directory for results
        
    Returns:
        Task result dictionary
    """
    try:
        # Create stop flag
        stop_flag = StopFlag()
        
        # Track progress
        progress_counts: Dict[str, int] = {}
        total_results = 0
        
        def on_log(message: str):
            """Log callback."""
            print(f"[TASK {task_id}] {message}")
            # Could emit WebSocket event here
        
        def on_progress(progress: Dict[str, int]):
            """Progress callback."""
            nonlocal progress_counts
            progress_counts = progress
            # Update task state
            self.update_state(
                state="PROGRESS",
                meta={
                    "progress": progress,
                    "total_results": sum(progress.values())
                }
            )
        
        def on_result(result: Dict):
            """Result callback."""
            nonlocal total_results
            total_results += 1
            
            # Save to PostgreSQL
            try:
                storage = get_postgresql_storage()
                storage.save_lead(task_id, result)
            except Exception as e:
                print(f"[TASK {task_id}] Error saving to DB: {e}")
        
        def on_finish():
            """Finish callback."""
            print(f"[TASK {task_id}] Scraping completed")
        
        # Convert request data to ScrapeRequest
        request = ScrapeRequest(**request_data)
        
        # Run orchestrator
        run_orchestrator(
            config_path=config_path,
            queries_list=request.queries,
            enabled_platforms=request.platforms,
            skip_gmaps="google_maps" not in request.platforms,
            max_results_override=request.max_results,
            on_log=on_log,
            on_progress=on_progress,
            on_result=on_result,
            on_finish=on_finish,
            stop_flag=stop_flag,
            phone_only=request.phone_only or False,
        )
        
        return {
            "task_id": task_id,
            "status": "completed",
            "total_results": total_results,
            "progress": progress_counts
        }
    
    except Exception as exc:
        # Retry on failure
        print(f"[TASK {task_id}] Error: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(
    name="backend.tasks.scraping_tasks.stop_scraping_task",
    ignore_result=True
)
def stop_scraping_task(task_id: str):
    """
    Stop a running scraping task.
    
    Args:
        task_id: Task identifier to stop
    """
    # This would need to communicate with the running task
    # For now, we'll use a shared state (Redis) to signal stop
    from redis import Redis
    redis_client = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    redis_client.set(f"stop_task:{task_id}", "1", ex=3600)  # Expire after 1 hour
    print(f"[CELERY] Stop signal sent for task {task_id}")


@celery_app.task(
    name="backend.tasks.scraping_tasks.get_task_status",
    ignore_result=False
)
def get_task_status(task_id: str) -> Dict:
    """
    Get status of a Celery task.
    
    Args:
        task_id: Celery task ID
        
    Returns:
        Task status dictionary
    """
    task = celery_app.AsyncResult(task_id)
    
    if task.state == "PENDING":
        return {"status": "pending", "message": "Task is waiting to be processed"}
    elif task.state == "PROGRESS":
        return {
            "status": "running",
            "progress": task.info.get("progress", {}),
            "total_results": task.info.get("total_results", 0)
        }
    elif task.state == "SUCCESS":
        return {
            "status": "completed",
            "result": task.result
        }
    elif task.state == "FAILURE":
        return {
            "status": "error",
            "error": str(task.info)
        }
    else:
        return {"status": task.state.lower(), "info": task.info}

