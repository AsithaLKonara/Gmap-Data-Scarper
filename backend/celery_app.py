"""Celery application configuration for async task processing."""
from celery import Celery
import os

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "lead_intelligence",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "backend.tasks.scraping_tasks",
        "backend.tasks.archival_tasks",
        "backend.tasks.plan_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600 * 24,  # 24 hours max
    task_soft_time_limit=3600 * 23,  # 23 hours soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_routes={
        "backend.tasks.scraping_tasks.*": {"queue": "scraping"},
        "backend.tasks.enrichment_tasks.*": {"queue": "enrichment"},
        "backend.tasks.archival_tasks.*": {"queue": "archival"},
    },
    # Scheduled tasks (Celery Beat)
    beat_schedule={
        'archive-old-leads-daily': {
            'task': 'archive_old_leads',
            'schedule': 86400.0,  # Run daily (24 hours)
            'args': (False,)  # Not a dry run
        },
        'get-archival-stats-hourly': {
            'task': 'get_archival_stats',
            'schedule': 3600.0,  # Run hourly
        },
        'reset-daily-lead-limits': {
            'task': 'reset-daily-lead-limits',
            'schedule': 86400.0,  # Run daily at midnight UTC
        },
    },
    task_default_queue="default",
    task_default_exchange="tasks",
    task_default_exchange_type="direct",
    task_default_routing_key="default",
    result_expires=3600,  # Results expire after 1 hour
)

# Task priority settings
celery_app.conf.task_queue_max_priority = 10
celery_app.conf.task_default_priority = 5

if __name__ == "__main__":
    celery_app.start()

