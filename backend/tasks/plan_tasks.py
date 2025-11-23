"""Celery tasks for plan management."""
from celery import shared_task
from backend.services.plan_service import get_plan_service


@shared_task(name="reset-daily-lead-limits")
def reset_daily_lead_limits():
    """
    Reset daily lead limits for all users.
    Runs daily at midnight UTC.
    """
    from backend.models.database import get_session
    db = get_session()
    try:
        plan_service = get_plan_service(db)
        deleted_count = plan_service.reset_daily_limits()
        return {
            "status": "success",
            "deleted_records": deleted_count,
            "message": f"Reset daily limits, deleted {deleted_count} old records"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to reset daily limits"
        }
    finally:
        db.close()

