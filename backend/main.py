import os
import sentry_sdk
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Response, Request
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from datetime import datetime
from typing import List
from database import engine, Base
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
from config import FRONTEND_URL
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
from branding import router as branding_router
from social_media_scraper import router as social_scraper_router
from whatsapp_workflow import router as whatsapp_workflow_router
from graphql import router as graphql_router
from realtime import router as realtime_router
from payments import router as payments_router
from webhooks import router as webhooks_router
from affiliate import router as affiliate_router

# Sentry integration
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=0.1,
        environment=os.getenv("ENVIRONMENT", "development"),
    )

app = FastAPI(
    title="LeadTap API",
    description="LeadTap - Google Maps Data Scraping and Lead Generation Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "same-origin"
    return response

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
app.include_router(branding_router)
app.include_router(social_scraper_router)
app.include_router(whatsapp_workflow_router)
app.include_router(graphql_router)
app.include_router(realtime_router)
app.include_router(payments_router)
app.include_router(webhooks_router)
app.include_router(affiliate_router)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    # Initialize default plans
    from plans import initialize_default_plans
    from lead_collection import initialize_lead_sources
    from database import SessionLocal
    db = SessionLocal()
    try:
        initialize_default_plans(db)
        initialize_lead_sources(db)
    finally:
        db.close()

@app.get("/")
def root():
    return {"status": "ok"} 

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws/admin")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for testing
            await manager.send_personal_message(f"Message received: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/admin/notifications/test")
async def test_notification():
    """Test endpoint to send a notification"""
    await manager.broadcast(json.dumps({
        "type": "test",
        "message": "Test notification from admin",
        "timestamp": datetime.now().isoformat()
    }))
    return {"message": "Notification sent"} 