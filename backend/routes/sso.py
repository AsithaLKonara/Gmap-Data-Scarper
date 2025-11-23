"""SSO authentication endpoints."""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any
from backend.services.sso_service import sso_service

router = APIRouter(prefix="/api/sso", tags=["sso"])


@router.post("/saml", response_model=Dict[str, Any])
async def handle_saml_login(saml_response: str):
    """Handle SAML authentication."""
    try:
        user_info = sso_service.handle_saml_assertion(saml_response)
        
        if "error" in user_info:
            raise HTTPException(status_code=400, detail=user_info["error"])
        
        # Generate token
        if user_info.get("email"):
            token = sso_service.generate_sso_token(
                user_id=user_info.get("user_id", user_info["email"]),
                email=user_info["email"]
            )
            return {
                "token": token,
                "user": user_info
            }
        else:
            raise HTTPException(status_code=400, detail="Email not found in SAML response")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SAML authentication failed: {str(e)}")


@router.get("/oauth/callback", response_model=Dict[str, Any])
async def handle_oauth_callback(
    code: str = Query(...),
    provider: str = Query("google", pattern="^(google|microsoft|okta)$")
):
    """Handle OAuth callback."""
    try:
        user_info = sso_service.handle_oauth_callback(code, provider)
        
        if "error" in user_info:
            raise HTTPException(status_code=400, detail=user_info["error"])
        
        # Generate token
        token = sso_service.generate_sso_token(
            user_id=user_info.get("user_id", user_info["email"]),
            email=user_info["email"]
        )
        
        return {
            "token": token,
            "user": user_info
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth authentication failed: {str(e)}")


@router.get("/oauth/authorize", response_model=Dict[str, str])
async def get_oauth_authorize_url(
    provider: str = Query("google", pattern="^(google|microsoft|okta)$")
):
    """Get OAuth authorization URL."""
    try:
        if provider == "google":
            client_id = sso_service.oauth_client_id
            redirect_uri = sso_service.oauth_redirect_uri
            scope = "openid email profile"
            url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}"
        elif provider == "microsoft":
            client_id = sso_service.oauth_client_id
            redirect_uri = sso_service.oauth_redirect_uri
            scope = "openid email profile"
            url = f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}"
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
        
        return {"authorize_url": url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate authorize URL: {str(e)}")

