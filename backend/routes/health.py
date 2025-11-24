"""Health and metrics endpoints."""
import psutil
import time
from fastapi import APIRouter
from fastapi.responses import Response
from typing import Dict, Any
from backend.services.orchestrator_service import task_manager
from backend.services.stream_service import stream_service
from backend.services.metrics import get_metrics_service

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    # Check database connection
    db_status = "healthy"
    db_error = None
    try:
        from backend.models.database import get_engine
        from sqlalchemy import text
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = "unhealthy"
        db_error = str(e)
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": time.time(),
        "service": "Lead Intelligence Platform API",
        "database": {
            "status": db_status,
            "error": db_error
        }
    }


@router.get("/health/database")
async def database_health_check() -> Dict[str, Any]:
    """Database connection health check endpoint."""
    from backend.models.database import get_engine
    from sqlalchemy import text, inspect
    import time as time_module
    
    start_time = time_module.time()
    status = "healthy"
    error = None
    pool_info = {}
    
    try:
        engine = get_engine()
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        # Get pool information (if available)
        if hasattr(engine.pool, 'size'):
            pool_info = {
                "pool_size": engine.pool.size(),
                "checked_in": engine.pool.checkedin(),
                "checked_out": engine.pool.checkedout(),
                "overflow": engine.pool.overflow(),
            }
        
        response_time = (time_module.time() - start_time) * 1000  # Convert to ms
        
        return {
            "status": status,
            "response_time_ms": round(response_time, 2),
            "pool": pool_info,
            "timestamp": time.time()
        }
    except Exception as e:
        status = "unhealthy"
        error = str(e)
        response_time = (time_module.time() - start_time) * 1000
        
        return {
            "status": status,
            "error": error,
            "response_time_ms": round(response_time, 2),
            "timestamp": time.time()
        }


@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    Prometheus-compatible metrics endpoint.
    Returns real-time statistics about the system.
    """
    # Get active tasks count
    active_tasks = sum(
        1 for task in task_manager.tasks.values()
        if task["status"] == "running"
    )
    
    # Get Chrome instances count
    chrome_instances = len(stream_service.drivers)
    
    # Get memory usage
    process = psutil.Process()
    memory_info = process.memory_info()
    memory_mb = memory_info.rss / (1024 * 1024)
    
    # Get system memory
    system_memory = psutil.virtual_memory()
    
    # Calculate error rates (from tasks)
    total_tasks = len(task_manager.tasks)
    error_tasks = sum(
        1 for task in task_manager.tasks.values()
        if task["status"] == "error"
    )
    error_rate = (error_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Calculate scraping throughput (results per minute)
    # Get results from last minute
    current_time = time.time()
    results_last_minute = 0
    for task in task_manager.tasks.values():
        if task.get("started_at"):
            # Estimate based on total_results and elapsed time
            if task["status"] == "running" and task.get("total_results", 0) > 0:
                elapsed_seconds = (time.time() - task["started_at"].timestamp()) if hasattr(task["started_at"], "timestamp") else 0
                if elapsed_seconds > 0:
                    rate_per_second = task["total_results"] / elapsed_seconds
                    results_last_minute += rate_per_second * 60
    
    # Get CPU usage
    cpu_percent = process.cpu_percent(interval=0.1)
    
    # Get task status breakdown
    task_statuses = {}
    for task in task_manager.tasks.values():
        status = task["status"]
        task_statuses[status] = task_statuses.get(status, 0) + 1
    
    return {
        "active_tasks": active_tasks,
        "chrome_instances": chrome_instances,
        "memory": {
            "process_mb": round(memory_mb, 2),
            "system_total_gb": round(system_memory.total / (1024 ** 3), 2),
            "system_available_gb": round(system_memory.available / (1024 ** 3), 2),
            "system_percent": round(system_memory.percent, 2)
        },
        "cpu": {
            "percent": round(cpu_percent, 2)
        },
        "error_rate_percent": round(error_rate, 2),
        "scraping_throughput": {
            "results_per_minute": round(results_last_minute, 2)
        },
        "tasks": {
            "total": total_tasks,
            "by_status": task_statuses
        },
        "timestamp": time.time()
    }


@router.get("/metrics/prometheus")
async def get_prometheus_metrics() -> Response:
    """
    Prometheus-compatible metrics endpoint.
    Returns metrics in Prometheus text format.
    """
    metrics_service = get_metrics_service()
    metrics_data = metrics_service.get_metrics()
    return Response(content=metrics_data, media_type="text/plain; version=0.0.4")


# Compatibility alias expected by some tests/tools:
@router.get("/health/metrics/prometheus")
async def get_prometheus_metrics_alias() -> Response:
    """Alias to expose Prometheus metrics under /health/metrics/prometheus as well."""
    return await get_prometheus_metrics()