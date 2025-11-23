"""Authentication endpoints."""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr
from typing import Optional
from backend.services.auth_service import auth_service
from backend.middleware.auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()


class LoginRequest(BaseModel):
    """Login request model."""
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Registration request model."""
    email: EmailStr
    password: str
    name: Optional[str] = None
    plan_type: Optional[str] = 'free'  # 'free', 'paid_monthly', 'paid_usage'


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""
    refresh_token: str


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """
    Register a new user.
    
    Creates user account and assigns plan based on plan_type.
    """
    from backend.models.database import get_session
    from backend.models.user import User
    from backend.services.plan_service import get_plan_service
    
    db = get_session()
    
    try:
        # Generate user ID
        user_id = auth_service.generate_user_id(request.email)
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = auth_service.hash_password(request.password)
        
        # Create user
        user = User(
            id=user_id,
            email=request.email,
            password_hash=hashed_password,
            name=request.name,
            is_active=True,
            is_verified=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create user plan
        plan_service = get_plan_service(db)
        plan_type = request.plan_type or 'free'
        # Normalize plan type
        if plan_type in ['monthly']:
            plan_type = 'paid_monthly'
        elif plan_type in ['usage']:
            plan_type = 'paid_usage'
        elif plan_type not in ['free', 'paid_monthly', 'paid_usage']:
            plan_type = 'free'
        plan_service.update_user_plan(user_id, plan_type)
        
        # Create tokens
        access_token = auth_service.create_access_token(user_id, request.email)
        refresh_token = auth_service.create_refresh_token(user_id)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=1440  # 24 hours in minutes
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )
    finally:
        db.close()


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Login and get access tokens.
    """
    from backend.models.database import get_session
    from backend.models.user import User
    
    db = get_session()
    
    try:
        # Generate user ID from email
        user_id = auth_service.generate_user_id(request.email)
        
        # Find user in database
        user = db.query(User).filter(User.email == request.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not auth_service.verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Create tokens
        access_token = auth_service.create_access_token(user_id, request.email)
        refresh_token = auth_service.create_refresh_token(user_id)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=1440
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )
    finally:
        db.close()


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token using refresh token."""
    new_access_token = auth_service.refresh_access_token(request.refresh_token)
    
    if not new_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Decode refresh token to get user_id
    payload = auth_service.verify_token(request.refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    new_refresh_token = auth_service.create_refresh_token(user_id)
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=1440
    )


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user information."""
    return {
        "user_id": current_user["user_id"],
        "email": current_user["email"],
    }


@router.post("/logout")
async def logout(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Logout user.
    
    Invalidates the current access token by adding it to the blacklist.
    In a production system, you may also want to invalidate refresh tokens.
    """
    # Get token from Authorization header
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        # Blacklist the access token
        auth_service.blacklist_token(token, current_user["user_id"], token_type="access")
    
    return {"status": "success", "message": "Logged out successfully"}

