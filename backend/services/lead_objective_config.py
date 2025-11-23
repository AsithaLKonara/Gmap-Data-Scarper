"""Lead objective configuration service for auto-configuring filters."""
from typing import Dict, Any, Optional
from enum import Enum


class LeadObjective(str, Enum):
    """Lead objective types."""
    STUDENTS = "students"
    BUSINESSES = "businesses"
    JOB_SEEKERS = "job_seekers"
    INFLUENCERS = "influencers"
    SERVICE_PROVIDERS = "service_providers"
    REAL_ESTATE = "real_estate"
    ECOMMERCE = "ecommerce"
    RESTAURANTS = "restaurants"
    MEDICAL_CLINICS = "medical_clinics"
    SOFTWARE_COMPANIES = "software_companies"
    FREELANCERS = "freelancers"


class LeadObjectiveConfig:
    """Configuration service for lead objectives."""
    
    # Pre-configured filter sets for each objective
    OBJECTIVE_CONFIGS: Dict[str, Dict[str, Any]] = {
        LeadObjective.STUDENTS: {
            "student_only": True,
            "education_level": ["Undergraduate", "Postgraduate", "High School"],
            "recommended_platforms": ["linkedin", "facebook", "instagram"],
            "recommended_filters": {
                "field_of_study": None,  # User can specify
                "education_level": ["Undergraduate", "Postgraduate"]
            }
        },
        LeadObjective.BUSINESSES: {
            "student_only": False,
            "recommended_platforms": ["google_maps", "linkedin", "facebook", "crunchbase"],
            "recommended_filters": {
                "business_type": None,  # User can specify
                "location": None  # User can specify
            }
        },
        LeadObjective.JOB_SEEKERS: {
            "student_only": False,
            "recommended_platforms": ["linkedin", "indeed", "upwork"],
            "recommended_filters": {
                "job_level": None,  # User can specify
                "education_level": None
            }
        },
        LeadObjective.INFLUENCERS: {
            "student_only": False,
            "recommended_platforms": ["instagram", "youtube", "tiktok", "x"],
            "recommended_filters": {
                "followers": ">1000"  # Minimum followers
            }
        },
        LeadObjective.SERVICE_PROVIDERS: {
            "student_only": False,
            "recommended_platforms": ["google_maps", "upwork", "fiverr", "linkedin"],
            "recommended_filters": {
                "business_type": ["service", "consulting", "freelance"]
            }
        },
        LeadObjective.REAL_ESTATE: {
            "student_only": False,
            "recommended_platforms": ["google_maps", "facebook", "linkedin"],
            "recommended_filters": {
                "business_type": ["real_estate", "property", "realty"]
            }
        },
        LeadObjective.ECOMMERCE: {
            "student_only": False,
            "recommended_platforms": ["google_maps", "instagram", "facebook", "crunchbase"],
            "recommended_filters": {
                "business_type": ["ecommerce", "online_store", "retail"]
            }
        },
        LeadObjective.RESTAURANTS: {
            "student_only": False,
            "recommended_platforms": ["google_maps", "yelp", "tripadvisor", "facebook"],
            "recommended_filters": {
                "business_type": ["restaurant", "cafe", "food"]
            }
        },
        LeadObjective.MEDICAL_CLINICS: {
            "student_only": False,
            "recommended_platforms": ["google_maps", "linkedin", "facebook"],
            "recommended_filters": {
                "business_type": ["medical", "clinic", "healthcare", "hospital"]
            }
        },
        LeadObjective.SOFTWARE_COMPANIES: {
            "student_only": False,
            "recommended_platforms": ["linkedin", "crunchbase", "github", "google_maps"],
            "recommended_filters": {
                "business_type": ["software", "saas", "tech", "it"]
            }
        },
        LeadObjective.FREELANCERS: {
            "student_only": False,
            "recommended_platforms": ["upwork", "fiverr", "linkedin", "github"],
            "recommended_filters": {
                "job_level": ["Freelancer"]
            }
        }
    }
    
    @classmethod
    def get_config(cls, objective: Optional[str]) -> Dict[str, Any]:
        """
        Get configuration for a lead objective.
        
        Args:
            objective: Lead objective string
            
        Returns:
            Configuration dictionary with recommended filters and platforms
        """
        if not objective or objective not in cls.OBJECTIVE_CONFIGS:
            return {
                "student_only": None,
                "recommended_platforms": [],
                "recommended_filters": {}
            }
        
        return cls.OBJECTIVE_CONFIGS[objective]
    
    @classmethod
    def get_all_objectives(cls) -> list[str]:
        """Get list of all available lead objectives."""
        return [obj.value for obj in LeadObjective]
    
    @classmethod
    def apply_config_to_request(cls, objective: Optional[str], request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply objective configuration to a scrape request.
        
        Args:
            objective: Lead objective
            request_data: Existing request data
            
        Returns:
            Updated request data with objective-based filters
        """
        if not objective:
            return request_data
        
        config = cls.get_config(objective)
        
        # Apply recommended platforms if none specified
        if not request_data.get("platforms") or request_data["platforms"] == ["google_maps"]:
            request_data["platforms"] = config.get("recommended_platforms", ["google_maps"])
        
        # Apply student_only filter
        if config.get("student_only") is not None:
            request_data["student_only"] = config["student_only"]
        
        # Apply recommended filters
        recommended_filters = config.get("recommended_filters", {})
        for key, value in recommended_filters.items():
            if value is not None and request_data.get(key) is None:
                request_data[key] = value
        
        return request_data

