"""
Production monitoring system for LeadTap Platform
Includes Prometheus metrics, health checks, and performance monitoring
"""

import time
import psutil
import structlog
from typing import Dict, Any, Optional
from fastapi import Request, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.registry import CollectorRegistry
from config import settings
from cache import cache_manager

logger = structlog.get_logger(__name__)

# Prometheus metrics registry
registry = CollectorRegistry()

# HTTP metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=registry
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    registry=registry
)

# Business metrics
leads_created_total = Counter(
    'leads_created_total',
    'Total leads created',
    ['user_id', 'source'],
    registry=registry
)

jobs_completed_total = Counter(
    'jobs_completed_total',
    'Total jobs completed',
    ['status', 'user_id'],
    registry=registry
)

whatsapp_messages_sent_total = Counter(
    'whatsapp_messages_sent_total',
    'Total WhatsApp messages sent',
    ['campaign_id', 'status'],
    registry=registry
)

# System metrics
system_cpu_usage = Gauge(
    'system_cpu_usage_percent',
    'CPU usage percentage',
    registry=registry
)

system_memory_usage = Gauge(
    'system_memory_usage_percent',
    'Memory usage percentage',
    registry=registry
)

system_disk_usage = Gauge(
    'system_disk_usage_percent',
    'Disk usage percentage',
    registry=registry
)

# Cache metrics
cache_hits_total = Counter(
    'cache_hits_total',
    'Total cache hits',
    registry=registry
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total cache misses',
    registry=registry
)

# Database metrics
db_connections_active = Gauge(
    'db_connections_active',
    'Active database connections',
    registry=registry
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation'],
    registry=registry
)

class MonitoringMiddleware:
    """Middleware for collecting HTTP metrics"""
    
    def __init__(self):
        self.start_time = time.time()
    
    async def __call__(self, request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Extract metrics
        method = request.method
        endpoint = request.url.path
        status = response.status_code
        
        # Record metrics
        http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
        http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
        
        return response

class SystemMonitor:
    """System resource monitoring"""
    
    @staticmethod
    def get_system_metrics() -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Update Prometheus gauges
            system_cpu_usage.set(cpu_percent)
            system_memory_usage.set(memory.percent)
            system_disk_usage.set(disk.percent)
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available": memory.available,
                "memory_total": memory.total,
                "disk_percent": disk.percent,
                "disk_free": disk.free,
                "disk_total": disk.total,
                "uptime": time.time() - psutil.boot_time()
            }
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {}

class HealthChecker:
    """Comprehensive health checking"""
    
    @staticmethod
    def check_database_health() -> Dict[str, Any]:
        """Check database health"""
        try:
            from database import test_database_connection, get_database_info
            
            is_healthy = test_database_connection()
            db_info = get_database_info()
            
            return {
                "status": "healthy" if is_healthy else "unhealthy",
                "type": db_info["type"],
                "version": db_info["version"],
                "connected": is_healthy
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    @staticmethod
    def check_cache_health() -> Dict[str, Any]:
        """Check cache health"""
        try:
            return cache_manager.health_check()
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    @staticmethod
    def check_redis_health() -> Dict[str, Any]:
        """Check Redis health"""
        try:
            if not settings.ENABLE_CACHING or not settings.REDIS_URL:
                return {
                    "status": "disabled",
                    "enabled": False
                }
            
            import redis
            r = redis.from_url(settings.REDIS_URL)
            r.ping()
            
            return {
                "status": "healthy",
                "enabled": True,
                "connected": True
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "enabled": True,
                "connected": False,
                "error": str(e)
            }
    
    @staticmethod
    def comprehensive_health_check() -> Dict[str, Any]:
        """Perform comprehensive health check"""
        try:
            system_metrics = SystemMonitor.get_system_metrics()
            db_health = HealthChecker.check_database_health()
            cache_health = HealthChecker.check_cache_health()
            redis_health = HealthChecker.check_redis_health()
            
            # Determine overall health
            all_healthy = (
                db_health["status"] == "healthy" and
                cache_health["status"] in ["healthy", "disabled"] and
                redis_health["status"] in ["healthy", "disabled"]
            )
            
            return {
                "status": "healthy" if all_healthy else "unhealthy",
                "timestamp": time.time(),
                "version": "2.0.0",
                "environment": settings.ENVIRONMENT,
                "checks": {
                    "database": db_health,
                    "cache": cache_health,
                    "redis": redis_health,
                    "system": {
                        "status": "healthy" if system_metrics else "unhealthy",
                        "metrics": system_metrics
                    }
                }
            }
        except Exception as e:
            logger.error(f"Comprehensive health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }

class MetricsCollector:
    """Business metrics collection"""
    
    @staticmethod
    def record_lead_created(user_id: int, source: str):
        """Record lead creation"""
        leads_created_total.labels(user_id=user_id, source=source).inc()
        logger.info(f"Lead created - User: {user_id}, Source: {source}")
    
    @staticmethod
    def record_job_completed(job_id: int, status: str, user_id: int):
        """Record job completion"""
        jobs_completed_total.labels(status=status, user_id=user_id).inc()
        logger.info(f"Job completed - ID: {job_id}, Status: {status}, User: {user_id}")
    
    @staticmethod
    def record_whatsapp_message(campaign_id: int, status: str):
        """Record WhatsApp message"""
        whatsapp_messages_sent_total.labels(campaign_id=campaign_id, status=status).inc()
        logger.info(f"WhatsApp message sent - Campaign: {campaign_id}, Status: {status}")
    
    @staticmethod
    def record_cache_hit():
        """Record cache hit"""
        cache_hits_total.inc()
    
    @staticmethod
    def record_cache_miss():
        """Record cache miss"""
        cache_misses_total.inc()
    
    @staticmethod
    def record_db_query(operation: str, duration: float):
        """Record database query"""
        db_query_duration_seconds.labels(operation=operation).observe(duration)

# Prometheus metrics endpoint
def get_metrics():
    """Get Prometheus metrics"""
    return Response(
        content=generate_latest(registry),
        media_type=CONTENT_TYPE_LATEST
    )

# Health check endpoint
def get_health():
    """Get comprehensive health status"""
    return HealthChecker.comprehensive_health_check()

# System info endpoint
def get_system_info():
    """Get system information"""
    return SystemMonitor.get_system_metrics()

# Performance monitoring decorator
def monitor_performance(operation: str):
    """Decorator to monitor function performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record database query metrics if applicable
                if operation.startswith("db_"):
                    MetricsCollector.record_db_query(operation, duration)
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Operation {operation} failed after {duration:.2f}s: {e}")
                raise
        return wrapper
    return decorator

# Async performance monitoring decorator
def monitor_async_performance(operation: str):
    """Decorator to monitor async function performance"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record database query metrics if applicable
                if operation.startswith("db_"):
                    MetricsCollector.record_db_query(operation, duration)
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Async operation {operation} failed after {duration:.2f}s: {e}")
                raise
        return wrapper
    return decorator

# Initialize monitoring
monitoring_middleware = MonitoringMiddleware()
system_monitor = SystemMonitor()
health_checker = HealthChecker()
metrics_collector = MetricsCollector()

# Export for use in other modules
__all__ = [
    'monitoring_middleware',
    'system_monitor',
    'health_checker',
    'metrics_collector',
    'get_metrics',
    'get_health',
    'get_system_info',
    'monitor_performance',
    'monitor_async_performance'
] 