"""Pydantic models for API requests and responses."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from backend.middleware.security import validate_query, validate_platform, sanitize_input


class ScrapeRequest(BaseModel):
    """Request model for starting a scrape job."""
    queries: List[str] = Field(..., min_length=1, max_length=50, description="List of search queries")
    platforms: List[str] = Field(
        default=["google_maps"],
        min_length=1,
        max_length=10,
        description="List of platforms to scrape"
    )
    max_results: Optional[int] = Field(
        default=None,
        ge=0,
        le=9999999,
        description="Maximum results per query (None = unlimited)"
    )
    headless: bool = Field(default=False, description="Run browser in headless mode")
    user_id: Optional[str] = Field(default=None, description="User ID for task ownership")
    lead_objective: Optional[str] = Field(
        default=None,
        description="Lead objective type: students, businesses, job_seekers, influencers, service_providers, real_estate, ecommerce, restaurants, medical_clinics, software_companies, freelancers"
    )
    
    @field_validator('queries')
    @classmethod
    def validate_queries(cls, v):
        """Validate and sanitize queries."""
        if not v:
            raise ValueError("At least one query is required")
        
        validated_queries = []
        for query in v:
            # Sanitize input
            sanitized = sanitize_input(query, max_length=500)
            
            # Validate query
            is_valid, error = validate_query(sanitized)
            if not is_valid:
                raise ValueError(f"Invalid query: {error}")
            
            validated_queries.append(sanitized)
        
        return validated_queries
    
    @field_validator('platforms')
    @classmethod
    def validate_platforms(cls, v):
        """Validate platforms against whitelist."""
        if not v:
            raise ValueError("At least one platform is required")
        
        validated_platforms = []
        for platform in v:
            is_valid, error = validate_platform(platform)
            if not is_valid:
                raise ValueError(error)
            validated_platforms.append(platform)
        
        return validated_platforms
    
    @field_validator('field_of_study')
    @classmethod
    def validate_field_of_study(cls, v):
        """Sanitize field of study."""
        if v:
            return sanitize_input(v, max_length=100)
        return v
    
    @field_validator('location')
    @classmethod
    def validate_location(cls, v):
        """Sanitize location."""
        if v:
            return sanitize_input(v, max_length=200)
        return v
    
    @field_validator('institution')
    @classmethod
    def validate_institution(cls, v):
        """Sanitize institution."""
        if v:
            return sanitize_input(v, max_length=200)
        return v
    
    # Filter options
    business_type: Optional[List[str]] = None
    job_level: Optional[List[str]] = None
    location: Optional[str] = None
    radius_km: Optional[float] = None
    education_level: Optional[List[str]] = None
    date_range: Optional[Dict[str, str]] = None
    active_within_days: Optional[int] = None
    boosted_only: Optional[bool] = None
    
    # Education/Career filters
    field_of_study: Optional[str] = None
    degree_type: Optional[List[str]] = None
    student_only: Optional[bool] = None
    institution: Optional[str] = None
    
    # Lead filtering
    phone_only: Optional[bool] = Field(
        default=False,
        description="Only collect leads that have phone numbers"
    )


class TaskStatus(BaseModel):
    """Task status response model."""
    task_id: str
    status: str = Field(..., description="Status: running, paused, stopped, completed, error")
    progress: Dict[str, int] = Field(default_factory=dict, description="Progress counts per platform")
    total_results: int = 0
    current_query: Optional[str] = None
    current_platform: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class PhoneData(BaseModel):
    """Phone number extraction data."""
    raw_phone: str
    normalized_e164: Optional[str] = None
    validation_status: str = Field(..., description="valid, possible, invalid")
    confidence_score: int = Field(..., ge=0, le=100, description="Confidence 0-100")
    phone_source: str = Field(..., description="tel_link, visible_text, jsonld, ocr, website")
    phone_element_selector: Optional[str] = None
    phone_screenshot_path: Optional[str] = None
    phone_timestamp: Optional[datetime] = None
    phone_coordinates: Optional[Dict[str, float]] = Field(
        None,
        description="Element coordinates (x, y, width, height normalized 0-1)"
    )
    viewport_info: Optional[Dict[str, int]] = Field(
        None,
        description="Viewport dimensions and scroll position at extraction time"
    )


class ScrapeResult(BaseModel):
    """Scrape result with phone data."""
    search_query: str
    platform: str
    profile_url: str
    handle: Optional[str] = None
    display_name: Optional[str] = None
    bio_about: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None  # Legacy field
    followers: Optional[str] = None
    location: Optional[str] = None
    
    # Phone extraction data
    phones: List[PhoneData] = Field(default_factory=list)
    
    # v2.0+ fields
    business_type: Optional[str] = None
    industry: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    job_title: Optional[str] = None
    seniority_level: Optional[str] = None
    education_level: Optional[str] = None
    institution_name: Optional[str] = None
    
    # v3.0+ fields
    lead_type: Optional[str] = Field(None, description="individual or business")
    field_of_study: Optional[str] = None
    degree_program: Optional[str] = None
    graduation_year: Optional[int] = None
    
    # Metadata
    extracted_at: Optional[datetime] = None


class LogMessage(BaseModel):
    """Log message for WebSocket streaming."""
    timestamp: datetime = Field(default_factory=datetime.now)
    level: str = Field(..., description="INFO, WARNING, ERROR, SUCCESS")
    message: str


class ProgressUpdate(BaseModel):
    """Progress update for WebSocket streaming."""
    platform: str
    count: int
    total_queries: int
    current_query_index: int
    current_query: str

