"""FastAPI application entry point."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send
import time
from typing import Callable
from backend.config import CORS_ORIGINS, API_HOST, API_PORT, API_RELOAD, TASK_TIMEOUT_SECONDS
from backend.routes import scraper, export, filters, legal, health, consent, auth, tasks, enrichment, archival, notifications, payments, ai, templates, company, workflows, teams, predictive, reports, sso, branding
from backend.routes import analytics_enhanced as analytics
from backend.middleware.rate_limit import RateLimitMiddleware
from backend.middleware.security import SecurityHeadersMiddleware
from backend.utils.structured_logging import set_request_context, clear_request_context

app = FastAPI(
    title="Lead Intelligence Platform API",
    description="API for interactive lead scraping with phone extraction",
    version="3.1.0"
)


# Request timeout middleware
class TimeoutMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce request timeouts.
    
    This middleware:
    - Sets request context for structured logging
    - Tracks request processing time
    - Enforces timeout limits for non-streaming endpoints
    - Adds processing time header to responses
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with timeout enforcement.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware/route handler
            
        Returns:
            Response with timeout enforcement and processing time header
        """
        start_time = time.time()
        
        # Set request context for logging
        set_request_context(
            request_id=request.headers.get("X-Request-ID", ""),
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else "unknown"
        )
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Add processing time header
            response.headers["X-Process-Time"] = str(round(process_time, 3))
            
            # Enforce timeout (except for streaming endpoints)
            if process_time > TASK_TIMEOUT_SECONDS and "/live_feed" not in str(request.url):
                return Response(
                    content='{"error": "Request timeout"}',
                    status_code=504,
                    media_type="application/json"
                )
            
            return response
        finally:
            clear_request_context()


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security headers middleware (first to add headers to all responses)
app.add_middleware(SecurityHeadersMiddleware)

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Timeout middleware
app.add_middleware(TimeoutMiddleware)

# Include routers
app.include_router(scraper.router)
app.include_router(export.router)
app.include_router(filters.router)
app.include_router(legal.router)
app.include_router(health.router)
app.include_router(consent.router)
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(analytics.router)
app.include_router(enrichment.router)
app.include_router(archival.router)
app.include_router(notifications.router)
app.include_router(payments.router)
app.include_router(ai.router)
app.include_router(templates.router)
app.include_router(company.router)
app.include_router(workflows.router)
app.include_router(teams.router)
app.include_router(predictive.router)
app.include_router(reports.router)
app.include_router(sso.router)
app.include_router(branding.router)


@app.get("/")
async def root() -> dict:
    """
    Root endpoint.
    
    Returns:
        API information including message, version, and docs URL
    """
    return {
        "message": "Lead Intelligence Platform API",
        "version": "3.0.0",
        "docs": "/docs"
    }


# Health endpoint moved to health.py router


# Initialize database on startup
@app.on_event("startup")
async def startup_event() -> None:
    """
    Initialize database and ensure all tables exist.
    """
    try:
        from backend.models.database import init_db
        from backend.models.push_subscription import PushSubscription  # Ensure model is registered
        from backend.models.user import User  # Ensure model is registered
        from backend.models.user_plan import UserPlan  # Ensure model is registered
        from backend.models.lead_usage import LeadUsage  # Ensure model is registered
        from backend.models.token_blacklist import TokenBlacklist  # Ensure model is registered
        from backend.models.data_request import DataRequest  # Ensure model is registered
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")

# Graceful shutdown handler
@app.on_event("shutdown")
async def shutdown_event() -> None:
    """
    Cleanup on shutdown.
    
    Stops all Chrome instances and running tasks gracefully.
    """
    from backend.services.stream_service import stream_service
    from backend.services.orchestrator_service import task_manager
    
    # Stop all Chrome instances
    for task_id in list(stream_service.drivers.keys()):
        stream_service.stop_stream(task_id)
    
    # Stop all running tasks
    for task_id in list(task_manager.tasks.keys()):
        if task_manager.tasks[task_id]["status"] == "running":
            task_manager.stop_task(task_id)


if __name__ == "__main__":
    import uvicorn
    import signal
    import sys
    
    def signal_handler(sig: int, frame: object) -> None:
        """
        Handle shutdown signals.
        
        Args:
            sig: Signal number
            frame: Current stack frame
        """
        print("\nShutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    uvicorn.run(
        "backend.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_RELOAD
    )

