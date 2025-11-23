"""SSO (Single Sign-On) service for enterprise authentication."""
from typing import Dict, Any, Optional
import os
import jwt
from datetime import datetime, timedelta


class SSOService:
    """Service for SSO authentication (SAML/OAuth)."""
    
    def __init__(self):
        """Initialize SSO service."""
        self.saml_cert_path = os.getenv("SAML_CERT_PATH")
        self.saml_issuer = os.getenv("SAML_ISSUER")
        self.oauth_client_id = os.getenv("OAUTH_CLIENT_ID")
        self.oauth_client_secret = os.getenv("OAUTH_CLIENT_SECRET")
        self.oauth_redirect_uri = os.getenv("OAUTH_REDIRECT_URI")
    
    def handle_saml_assertion(
        self,
        saml_response: str
    ) -> Dict[str, Any]:
        """
        Handle SAML assertion.
        
        Args:
            saml_response: SAML response XML
            
        Returns:
            User information from SAML
        """
        try:
            # In production, use a proper SAML library like python3-saml
            # This is a simplified implementation
            import xml.etree.ElementTree as ET
            
            root = ET.fromstring(saml_response)
            
            # Extract user attributes (simplified)
            # In production, properly parse SAML assertion
            user_info = {
                "email": None,
                "name": None,
                "user_id": None,
                "attributes": {}
            }
            
            # Parse SAML attributes (simplified)
            # Real implementation would verify signature, parse properly
            for attr in root.findall(".//{urn:oasis:names:tc:SAML:2.0:assertion}Attribute"):
                name = attr.get("Name")
                value_elem = attr.find(".//{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue")
                if value_elem is not None:
                    value = value_elem.text
                    if name == "email":
                        user_info["email"] = value
                    elif name == "name":
                        user_info["name"] = value
                    user_info["attributes"][name] = value
            
            return user_info
        except Exception as e:
            return {"error": str(e)}
    
    def handle_oauth_callback(
        self,
        code: str,
        provider: str = "google"
    ) -> Dict[str, Any]:
        """
        Handle OAuth callback.
        
        Args:
            code: OAuth authorization code
            provider: OAuth provider (google, microsoft, okta)
            
        Returns:
            User information from OAuth
        """
        try:
            import requests
            
            if provider == "google":
                token_url = "https://oauth2.googleapis.com/token"
                token_data = {
                    "code": code,
                    "client_id": self.oauth_client_id,
                    "client_secret": self.oauth_client_secret,
                    "redirect_uri": self.oauth_redirect_uri,
                    "grant_type": "authorization_code"
                }
            elif provider == "microsoft":
                token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
                token_data = {
                    "code": code,
                    "client_id": self.oauth_client_id,
                    "client_secret": self.oauth_client_secret,
                    "redirect_uri": self.oauth_redirect_uri,
                    "grant_type": "authorization_code"
                }
            else:
                return {"error": f"Unsupported provider: {provider}"}
            
            # Exchange code for token
            response = requests.post(token_url, data=token_data, timeout=10)
            response.raise_for_status()
            token_response = response.json()
            access_token = token_response.get("access_token")
            
            # Get user info
            if provider == "google":
                user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            elif provider == "microsoft":
                user_info_url = "https://graph.microsoft.com/v1.0/me"
            
            headers = {"Authorization": f"Bearer {access_token}"}
            user_response = requests.get(user_info_url, headers=headers, timeout=10)
            user_response.raise_for_status()
            user_data = user_response.json()
            
            # Extract user info
            if provider == "google":
                return {
                    "email": user_data.get("email"),
                    "name": user_data.get("name"),
                    "user_id": user_data.get("id"),
                    "provider": provider
                }
            elif provider == "microsoft":
                return {
                    "email": user_data.get("mail") or user_data.get("userPrincipalName"),
                    "name": user_data.get("displayName"),
                    "user_id": user_data.get("id"),
                    "provider": provider
                }
            
            return {"error": "Failed to extract user info"}
        except Exception as e:
            return {"error": str(e)}
    
    def generate_sso_token(
        self,
        user_id: str,
        email: str
    ) -> str:
        """
        Generate JWT token for SSO user.
        
        Args:
            user_id: User ID
            email: User email
            
        Returns:
            JWT token
        """
        secret = os.getenv("JWT_SECRET", "your-secret-key")
        
        payload = {
            "user_id": user_id,
            "email": email,
            "sso": True,
            "exp": datetime.utcnow() + timedelta(days=1)
        }
        
        token = jwt.encode(payload, secret, algorithm="HS256")
        return token


# Global instance
sso_service = SSOService()

