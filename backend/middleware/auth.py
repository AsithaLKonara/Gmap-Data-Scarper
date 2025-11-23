"""Authentication middleware."""
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict
from backend.services.auth_service import auth_service


security = HTTPBearer()


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[dict]:
    """
    Get current authenticated user from JWT token.
    
    Args:
        request: FastAPI request
        credentials: HTTP Bearer credentials
        
    Returns:
        User payload from token
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    token = credentials.credentials
    
    # Check if token is blacklisted
    if auth_service.is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = auth_service.verify_token(token, token_type="access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
    }


async def get_optional_user(request: Request) -> Optional[dict]:
    """
    Get current user if authenticated, otherwise None.
    Useful for endpoints that work with or without authentication.
    
    Args:
        request: FastAPI request
        
    Returns:
        User payload or None
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.replace("Bearer ", "")
    payload = auth_service.verify_token(token, token_type="access")
    
    if not payload:
        return None
    
    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
    }

