"""Pipedrive CRM integration service."""
from typing import Dict, Any, Optional
import os
import requests


class PipedriveCRMService:
    """Service for integrating with Pipedrive CRM."""
    
    def __init__(self):
        """Initialize Pipedrive CRM service."""
        self.api_token = os.getenv("PIPEDRIVE_API_TOKEN")
        self.api_domain = os.getenv("PIPEDRIVE_API_DOMAIN", "https://api.pipedrive.com")
    
    def create_person(
        self,
        lead_data: Dict[str, Any],
        company_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a person in Pipedrive.
        
        Args:
            lead_data: Lead data dictionary
            company_id: Optional company ID to associate with
            
        Returns:
            Dict with person creation result
        """
        if not self.api_token:
            return {"success": False, "error": "Pipedrive API token not configured"}
        
        try:
            url = f"{self.api_domain}/v1/persons"
            params = {
                "api_token": self.api_token
            }
            
            # Map lead data to Pipedrive person fields
            person_data = {
                "name": lead_data.get("display_name", ""),
                "phone": [{"value": lead_data.get("phone", ""), "primary": True}] if lead_data.get("phone") else [],
                "email": [{"value": lead_data.get("email", ""), "primary": True}] if lead_data.get("email") else [],
                "org_id": company_id,
            }
            
            # Add location if available
            if lead_data.get("city"):
                person_data["address"] = {
                    "city": lead_data.get("city", ""),
                    "state": lead_data.get("region", ""),
                    "country": lead_data.get("country", "")
                }
            
            response = requests.post(url, params=params, json=person_data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get("success") and result.get("data"):
                return {
                    "success": True,
                    "person_id": result["data"].get("id"),
                    "message": "Person created successfully"
                }
            else:
                return {"success": False, "error": result.get("error", "Unknown error")}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_organization(
        self,
        lead_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create an organization in Pipedrive.
        
        Args:
            lead_data: Lead data dictionary
            
        Returns:
            Dict with organization creation result
        """
        if not self.api_token:
            return {"success": False, "error": "Pipedrive API token not configured"}
        
        try:
            url = f"{self.api_domain}/v1/organizations"
            params = {
                "api_token": self.api_token
            }
            
            org_data = {
                "name": lead_data.get("display_name", ""),
                "address": {
                    "city": lead_data.get("city", ""),
                    "state": lead_data.get("region", ""),
                    "country": lead_data.get("country", "")
                } if lead_data.get("city") else None,
            }
            
            response = requests.post(url, params=params, json=org_data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get("success") and result.get("data"):
                return {
                    "success": True,
                    "org_id": result["data"].get("id"),
                    "message": "Organization created successfully"
                }
            else:
                return {"success": False, "error": result.get("error", "Unknown error")}
                
        except Exception as e:
            return {"success": False, "error": str(e)}


# Global instance
pipedrive_crm_service = PipedriveCRMService()

