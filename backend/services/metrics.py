"""Prometheus metrics service for monitoring."""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
from typing import Optional, Dict, Any
import time
from backend.models.database import get_engine


# Metrics
scraping_requests_total = Counter(
    'scraping_requests_total',
    'Total number of scraping requests',
    ['platform', 'status']
)

scraping_duration_seconds = Histogram(
    'scraping_duration_seconds',
    'Time spent scraping',
    ['platform'],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0]
)

leads_collected_total = Counter(
    'leads_collected_total',
    'Total number of leads collected',
    ['platform', 'has_phone']
)

leads_quality_score = Histogram(
    'leads_quality_score',
    'Lead quality score distribution',
    buckets=[0, 25, 50, 75, 90, 95, 100]
)

active_tasks = Gauge(
    'active_tasks',
    'Number of active scraping tasks'
)

tasks_completed_total = Counter(
    'tasks_completed_total',
    'Total number of completed tasks',
    ['status']
)

api_requests_total = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status_code']
)

api_request_duration_seconds = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
)

database_operations_total = Counter(
    'database_operations_total',
    'Total number of database operations',
    ['operation', 'status']
)

database_operation_duration_seconds = Histogram(
    'database_operation_duration_seconds',
    'Database operation duration',
    ['operation'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0]
)


class MetricsService:
    """Service for recording metrics."""
    
    @staticmethod
    def record_scraping_request(platform: str, status: str = "success"):
        """Record a scraping request."""
        scraping_requests_total.labels(platform=platform, status=status).inc()
    
    @staticmethod
    def record_scraping_duration(platform: str, duration: float):
        """Record scraping duration."""
        scraping_duration_seconds.labels(platform=platform).observe(duration)
    
    @staticmethod
    def record_lead_collected(platform: str, has_phone: bool):
        """Record a collected lead."""
        leads_collected_total.labels(
            platform=platform,
            has_phone="yes" if has_phone else "no"
        ).inc()
    
    @staticmethod
    def record_lead_quality(score: int):
        """Record lead quality score."""
        leads_quality_score.observe(score)
    
    @staticmethod
    def set_active_tasks(count: int):
        """Set number of active tasks."""
        active_tasks.set(count)
    
    @staticmethod
    def record_task_completed(status: str):
        """Record a completed task."""
        tasks_completed_total.labels(status=status).inc()
    
    @staticmethod
    def record_api_request(method: str, endpoint: str, status_code: int, duration: float):
        """Record an API request."""
        api_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        api_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    @staticmethod
    def record_database_operation(operation: str, status: str, duration: float):
        """Record a database operation."""
        database_operations_total.labels(
            operation=operation,
            status=status
        ).inc()
        database_operation_duration_seconds.labels(operation=operation).observe(duration)
    
    @staticmethod
    def get_metrics() -> bytes:
        """Get Prometheus metrics in text format."""
        return generate_latest(REGISTRY)
    
    @staticmethod
    def get_database_pool_stats() -> Dict[str, Any]:
        """Get database connection pool statistics."""
        try:
            engine = get_engine()
            if hasattr(engine.pool, 'size'):
                return {
                    "pool_size": engine.pool.size(),
                    "checked_in": engine.pool.checkedin(),
                    "checked_out": engine.pool.checkedout(),
                    "overflow": engine.pool.overflow(),
                }
            return {"pool_size": "N/A (SQLite)"}
        except Exception as e:
            return {"error": str(e)}


# Global instance
_metrics_service: Optional[MetricsService] = None


def get_metrics_service() -> MetricsService:
    """Get or create global metrics service instance."""
    global _metrics_service
    if _metrics_service is None:
        _metrics_service = MetricsService()
    return _metrics_service

