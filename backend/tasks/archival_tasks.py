"""Scheduled tasks for data archival."""
from backend.celery_app import celery_app
from backend.services.archival import get_archival_service
from backend.utils.structured_logging import logger


@celery_app.task(name="archive_old_leads", bind=True)
def archive_old_leads_task(self, dry_run: bool = False):
    """
    Scheduled task to archive old leads.
    
    This task should be scheduled to run daily via Celery Beat.
    """
    try:
        archival_service = get_archival_service()
        result = archival_service.archive_old_leads(dry_run=dry_run)
        
        logger.info(
            f"Archival task completed: {result.get('archived_count', 0)} leads archived",
            archived_count=result.get('archived_count', 0),
            total_found=result.get('total_found', 0)
        )
        
        return result
    except Exception as e:
        logger.error(f"Archival task failed: {e}", error=str(e))
        raise


@celery_app.task(name="get_archival_stats", bind=True)
def get_archival_stats_task(self):
    """Get archival statistics (for monitoring)."""
    try:
        archival_service = get_archival_service()
        stats = archival_service.get_archival_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get archival stats: {e}", error=str(e))
        raise

