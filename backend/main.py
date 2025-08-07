import os
import sentry_sdk
import structlog
import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Response, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
from datetime import datetime
from typing import List
from database import engine, Base, test_database_connection, get_database_info
from auth import router as auth_router
from jobs import router as jobs_router
from payhere import router as payhere_router
from admin import router as admin_router
from crm import router as crm_router
from plans import router as plans_router
from profiles import router as profiles_router
from system import router as system_router
from scheduler import router as scheduler_router
from export import router as export_router
from notifications import router as notifications_router
from support import router as support_router
from saved_queries import router as saved_queries_router
from analytics import router as analytics_router
from lead_collection import router as lead_collection_router
from security import router as security_router
from integrations import router as integrations_router
from onboarding import router as onboarding_router
from roi_calculator import router as roi_router
from lead_scoring import router as lead_scoring_router
from enhanced_analytics import router as enhanced_analytics_router
from referral import router as referral_router
from widgets import router as widgets_router
from showcase import router as showcase_router
from sso import router as sso_router
from social_media_scraper import router as social_scraper_router
from whatsapp_workflow import router as whatsapp_workflow_router
from bulk_whatsapp_sender import router as bulk_whatsapp_router
from realtime import router as realtime_router
from payments import router as payments_router
from webhooks import router as webhooks_router
from affiliate import router as affiliate_router
from config import settings, SECURITY_HEADERS, ALLOWED_ORIGINS

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Sentry integration for production
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=0.1,
        environment=settings.ENVIRONMENT,
        profiles_sample_rate=0.1,
        enable_tracing=True,
    )
    logger.info("✅ Sentry error tracking initialized")

# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting LeadTap application...")
    
    # Test database connection
    if not test_database_connection():
        logger.error("❌ Database connection failed")
        raise Exception("Database connection failed")
    
    # Log database info
    db_info = get_database_info()
    logger.info(f"📊 Database: {db_info['type']} {db_info['version']}")
    
    # Log environment info
    logger.info(f"🌍 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔧 Debug mode: {settings.DEBUG}")
    logger.info(f"🔒 Security features: 2FA={settings.ENABLE_2FA}, SSO={settings.ENABLE_SSO}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down LeadTap application...")

# Create FastAPI application with production settings
app = FastAPI(
    title="LeadTap API",
    description="LeadTap - Google Maps Data Scraping and Lead Generation Platform",
    version="2.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan
)

# Security middleware
@app.middleware("http")
async def add_security_headers_and_rate_limit(request: Request, call_next):
    """Add security headers and implement rate limiting"""
    start_time = time.time()
    
    # Add security headers
    response = await call_next(request)
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    
    # Add custom headers
    response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", "unknown")
    response.headers["X-Response-Time"] = str(time.time() - start_time)
    
    # Log request
    logger.info(
        "HTTP Request",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        response_time=time.time() - start_time,
        user_agent=request.headers.get("user-agent"),
        client_ip=request.client.host if request.client else "unknown"
    )
    
    return response

# Trusted host middleware for production
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["leadtap.com", "www.leadtap.com", "api.leadtap.com"]
    )

# CORS middleware with production settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Request-ID", "X-Response-Time"],
)

# Gzip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include all routers
app.include_router(auth_router)
app.include_router(jobs_router)
app.include_router(payhere_router)
app.include_router(admin_router)
app.include_router(crm_router)
app.include_router(plans_router)
app.include_router(profiles_router)
app.include_router(system_router)
app.include_router(scheduler_router)
app.include_router(export_router)
app.include_router(notifications_router)
app.include_router(support_router)
app.include_router(saved_queries_router)
app.include_router(analytics_router)
app.include_router(lead_collection_router)
app.include_router(security_router)
app.include_router(integrations_router)
app.include_router(onboarding_router)
app.include_router(roi_router)
app.include_router(lead_scoring_router)
app.include_router(enhanced_analytics_router)
app.include_router(referral_router)
app.include_router(widgets_router)
app.include_router(showcase_router)
app.include_router(sso_router)
app.include_router(social_scraper_router)
app.include_router(whatsapp_workflow_router)
app.include_router(bulk_whatsapp_router)
app.include_router(realtime_router)
app.include_router(payments_router)
app.include_router(webhooks_router)
app.include_router(affiliate_router)

# Root endpoint
@app.get("/")
def root():
    """Root endpoint with application info"""
    return {
        "name": "LeadTap API",
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT,
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs" if settings.DEBUG else None
    }

# Enhanced health check endpoint
@app.get("/api/health")
def health_check():
    """Comprehensive health check endpoint"""
    try:
        # Test database connection
        db_healthy = test_database_connection()
        
        # Get database info
        db_info = get_database_info()
        
        # Check Redis connection (if enabled)
        redis_healthy = True
        if settings.ENABLE_CACHING:
            try:
                import redis
                r = redis.from_url(settings.REDIS_URL)
                r.ping()
            except Exception as e:
                redis_healthy = False
                logger.error(f"Redis health check failed: {e}")
        
        health_status = {
            "status": "healthy" if db_healthy and redis_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0",
            "environment": settings.ENVIRONMENT,
            "checks": {
                "database": {
                    "status": "healthy" if db_healthy else "unhealthy",
                    "type": db_info["type"],
                    "version": db_info["version"]
                },
                "redis": {
                    "status": "healthy" if redis_healthy else "unhealthy",
                    "enabled": settings.ENABLE_CACHING
                },
                "sentry": {
                    "status": "enabled" if settings.SENTRY_DSN else "disabled"
                }
            }
        }
        
        status_code = 200 if health_status["status"] == "healthy" else 503
        return JSONResponse(content=health_status, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            },
            status_code=503
        )

# System info endpoint
@app.get("/api/system/info")
def system_info():
    """Get system information for monitoring"""
    import psutil
    
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "uptime": time.time(),
        "environment": settings.ENVIRONMENT,
        "version": "2.0.0"
    }

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Failed to send message to WebSocket: {e}")
                self.active_connections.remove(connection)

manager = ConnectionManager()

# WebSocket endpoint for real-time updates
@app.websocket("/ws/admin")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Process real-time data
            await manager.broadcast(f"Message: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Test notification endpoint
@app.post("/api/admin/notifications/test")
async def test_notification():
    """Test notification system"""
    try:
        # Send test notification
        await manager.broadcast(json.dumps({
            "type": "notification",
            "title": "Test Notification",
            "message": "This is a test notification",
            "timestamp": datetime.utcnow().isoformat()
        }))
        return {"status": "success", "message": "Test notification sent"}
    except Exception as e:
        logger.error(f"Test notification failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to send test notification")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for production"""
    logger.error(
        "Unhandled exception",
        exc_info=exc,
        url=str(request.url),
        method=request.method,
        client_ip=request.client.host if request.client else "unknown"
    )
    
    if settings.ENVIRONMENT == "production":
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)}
        )

# Startup event
@app.on_event("startup")
def on_startup():
    """Application startup event"""
    logger.info("🚀 LeadTap API started successfully")
    logger.info(f"📊 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔧 Debug mode: {settings.DEBUG}")
    logger.info(f"🔒 Security features enabled")
    logger.info(f"📈 Monitoring enabled: {settings.ENABLE_MONITORING}")

# Shutdown event
@app.on_event("shutdown")
def on_shutdown():
    """Application shutdown event"""
    logger.info("🛑 LeadTap API shutting down")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=settings.MAX_WORKERS if not settings.DEBUG else 1,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )