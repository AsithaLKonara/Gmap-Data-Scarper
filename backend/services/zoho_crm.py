"""Zoho CRM integration service."""
from typing import Dict, Any, Optional
import os
import requests
import logging


class ZohoCRMService:
    """Service for integrating with Zoho CRM."""
    
    def __init__(self):
        """Initialize Zoho CRM service."""
        self.client_id = os.getenv("ZOHO_CLIENT_ID")
        self.client_secret = os.getenv("ZOHO_CLIENT_SECRET")
        self.refresh_token = os.getenv("ZOHO_REFRESH_TOKEN")
        self.api_domain = os.getenv("ZOHO_API_DOMAIN", "https://www.zohoapis.com")
        self.access_token = None
    
    def _get_access_token(self) -> Optional[str]:
        """Get or refresh access token."""
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            return None
        
        try:
            url = "https://accounts.zoho.com/oauth/v2/token"
            params = {
                "refresh_token": self.refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token"
            }
            
            response = requests.post(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            self.access_token = data.get("access_token")
            return self.access_token
        except Exception as e:
            logging.info(f"[ZOHO] Failed to get access token: {e}")
            return None
    
    def create_contact(
        self,
        lead_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a contact in Zoho CRM.
        
        Args:
            lead_data: Lead data dictionary
            
        Returns:
            Dict with contact creation result
        """
        if not self._get_access_token():
            return {"success": False, "error": "Zoho credentials not configured"}
        
        try:
            url = f"{self.api_domain}/crm/v3/Contacts"
            headers = {
                "Authorization": f"Zoho-oauthtoken {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # Map lead data to Zoho contact fields
            contact_data = {
                "First_Name": lead_data.get("display_name", "").split()[0] if lead_data.get("display_name") else "",
                "Last_Name": " ".join(lead_data.get("display_name", "").split()[1:]) if lead_data.get("display_name") else "",
                "Phone": lead_data.get("phone", ""),
                "Email": lead_data.get("email", ""),
                "Mailing_City": lead_data.get("city", ""),
                "Mailing_State": lead_data.get("region", ""),
                "Mailing_Country": lead_data.get("country", ""),
                "Description": lead_data.get("bio_about", ""),
            }
            
            payload = {"data": [contact_data]}
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get("data") and len(result["data"]) > 0:
                return {
                    "success": True,
                    "contact_id": result["data"][0].get("details", {}).get("id"),
                    "message": "Contact created successfully"
                }
            else:
                return {"success": False, "error": "No contact created"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}


# Global instance
zoho_crm_service = ZohoCRMService()

