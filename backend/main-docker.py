 
"""
LeadTap Backend API - Docker Version (No GraphQL)
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from datetime import datetime
import os

# Import routers
from auth import router as auth_router
from jobs import router as jobs_router
from leads import router as leads_router
from profiles import router as profiles_router
from payments import router as payments_router
from analytics import router as analytics_router
from lead_scoring import router as lead_scoring_router
from whatsapp_workflow import router as whatsapp_router
from cache import cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LeadTap API",
    description="LeadTap - Google Maps Data Scraper & Lead Management",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(jobs_router, prefix="/api/scrape", tags=["Scraping"])
app.include_router(leads_router, prefix="/api/leads", tags=["Leads"])
app.include_router(profiles_router, prefix="/api/profiles", tags=["Profiles"])
app.include_router(payments_router, prefix="/api/payments", tags=["Payments"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(lead_scoring_router, prefix="/api/lead-scoring", tags=["Lead Scoring"])
app.include_router(whatsapp_router, prefix="/api/whatsapp", tags=["WhatsApp"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LeadTap API is running!",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache_size": cache.size()
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main-docker:app",
        host="0.0.0.0",
        port=port,
        reload=False
    ) 
 
"""
LeadTap Backend API - Docker Version (No GraphQL)
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from datetime import datetime
import os

# Import routers
from auth import router as auth_router
from jobs import router as jobs_router
from leads import router as leads_router
from profiles import router as profiles_router
from payments import router as payments_router
from analytics import router as analytics_router
from lead_scoring import router as lead_scoring_router
from whatsapp_workflow import router as whatsapp_router
from cache import cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LeadTap API",
    description="LeadTap - Google Maps Data Scraper & Lead Management",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(jobs_router, prefix="/api/scrape", tags=["Scraping"])
app.include_router(leads_router, prefix="/api/leads", tags=["Leads"])
app.include_router(profiles_router, prefix="/api/profiles", tags=["Profiles"])
app.include_router(payments_router, prefix="/api/payments", tags=["Payments"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(lead_scoring_router, prefix="/api/lead-scoring", tags=["Lead Scoring"])
app.include_router(whatsapp_router, prefix="/api/whatsapp", tags=["WhatsApp"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LeadTap API is running!",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache_size": cache.size()
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main-docker:app",
        host="0.0.0.0",
        port=port,
        reload=False
    ) 
 
"""
LeadTap Backend API - Docker Version (No GraphQL)
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from datetime import datetime
import os

# Import routers
from auth import router as auth_router
from jobs import router as jobs_router
from leads import router as leads_router
from profiles import router as profiles_router
from payments import router as payments_router
from analytics import router as analytics_router
from lead_scoring import router as lead_scoring_router
from whatsapp_workflow import router as whatsapp_router
from cache import cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LeadTap API",
    description="LeadTap - Google Maps Data Scraper & Lead Management",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(jobs_router, prefix="/api/scrape", tags=["Scraping"])
app.include_router(leads_router, prefix="/api/leads", tags=["Leads"])
app.include_router(profiles_router, prefix="/api/profiles", tags=["Profiles"])
app.include_router(payments_router, prefix="/api/payments", tags=["Payments"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(lead_scoring_router, prefix="/api/lead-scoring", tags=["Lead Scoring"])
app.include_router(whatsapp_router, prefix="/api/whatsapp", tags=["WhatsApp"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LeadTap API is running!",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache_size": cache.size()
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main-docker:app",
        host="0.0.0.0",
        port=port,
        reload=False
    ) 
 