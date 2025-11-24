"""Authentication middleware."""
from fastapi import Request, HTTPException, status, Depends, WebSocket
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


async def get_websocket_user(websocket: WebSocket) -> Optional[dict]:
    """
    Get authenticated user from WebSocket connection.
    
    WebSocket authentication is done via query parameter.
    Token should be passed as: ws://host/path?token=...
    
    Args:
        websocket: FastAPI WebSocket connection
        
    Returns:
        User payload or None if not authenticated
        
    Raises:
        WebSocketException: If authentication fails
    """
    from fastapi import WebSocketException, status
    import os
    
    # Check if we're in TESTING mode (for automated tests)
    is_testing = os.getenv("TESTING") == "true"
    
    # Try to get token from query parameters
    token = websocket.query_params.get("token")
    
    # If no token and not in testing mode, reject
    if not token:
        if is_testing:
            # Allow test connections in TESTING mode
            return {
                "user_id": "test_user_12345",
                "email": "test@example.com"
            }
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Authentication required. Provide token as query parameter: ?token=..."
        )
    
    # Check if token is blacklisted
    if auth_service.is_token_blacklisted(token):
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Token has been revoked"
        )
    
    # Verify token
    payload = auth_service.verify_token(token, token_type="access")
    if not payload:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid or expired token"
        )
    
    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
    }

