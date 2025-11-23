"""Filter metadata endpoints."""
from fastapi import APIRouter
from typing import List, Dict

router = APIRouter(prefix="/api/filters", tags=["filters"])


@router.get("/business-types", response_model=List[str])
async def get_business_types():
    """Get available business types."""
    # Load from business_keywords.yaml
    import yaml
    import os
    
    keywords_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "classification",
        "business_keywords.yaml"
    )
    
    if os.path.exists(keywords_path):
        with open(keywords_path, "r") as f:
            data = yaml.safe_load(f) or {}
            return list(data.keys())
    
    return []


@router.get("/job-levels", response_model=List[str])
async def get_job_levels():
    """Get available job levels."""
    return ["Junior", "Mid", "Senior", "Executive", "Freelancer"]


@router.get("/education-levels", response_model=List[str])
async def get_education_levels():
    """Get available education levels."""
    return ["High School", "Undergraduate", "Postgraduate", "Doctorate"]


@router.get("/degree-types", response_model=List[str])
async def get_degree_types():
    """Get available degree types."""
    return ["Bachelor's", "Master's", "PhD", "Associate", "Diploma", "Certificate"]


@router.get("/platforms", response_model=List[str])
async def get_platforms():
    """Get available platforms."""
    return [
        "google_maps",
        "facebook",
        "instagram",
        "linkedin",
        "x",
        "youtube",
        "tiktok",
        "yelp",
        "crunchbase",
        "tripadvisor",
        "indeed",
        "github"
    ]


@router.get("/lead-objectives", response_model=List[Dict[str, str]])
async def get_lead_objectives():
    """Get available lead objectives."""
    from backend.services.lead_objective_config import LeadObjectiveConfig
    
    objectives = LeadObjectiveConfig.get_all_objectives()
    
    # Return with human-readable labels
    labels = {
        "students": "Students",
        "businesses": "Businesses",
        "job_seekers": "Job Seekers",
        "influencers": "Influencers",
        "service_providers": "Service Providers",
        "real_estate": "Real Estate",
        "ecommerce": "E-commerce",
        "restaurants": "Restaurants",
        "medical_clinics": "Medical Clinics",
        "software_companies": "Software Companies",
        "freelancers": "Freelancers"
    }
    
    return [
        {"value": obj, "label": labels.get(obj, obj.replace("_", " ").title())}
        for obj in objectives
    ]