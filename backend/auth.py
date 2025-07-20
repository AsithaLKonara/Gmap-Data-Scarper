from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
from models import Users
from database import get_db
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
import logging
import secrets
import pyotp
import time
from fastapi import Request
from starlette.responses import JSONResponse
import base64
import io
import qrcode
import json
from models import AuditLogs

router = APIRouter(prefix="/api/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
api_key_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger = logging.getLogger("auth")

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    # role: Optional[str] = 'user'  # For future: allow admin to set role

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    plan: str
    role: str
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TwoFASetupResponse(BaseModel):
    secret: str
    qr_code_base64: str
    provisioning_uri: str

def get_password_hash(password):
    print(f"🔐 [AUTH] Hashing password for new user")
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    print(f"🔍 [AUTH] Verifying password for user")
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta = None):
    print(f"🎫 [AUTH] Creating JWT access token for user ID: {data.get('sub', 'unknown')}")
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Simple in-memory rate limiter for login attempts
_login_attempts = {}
RATE_LIMIT = 5  # max attempts
RATE_PERIOD = 60  # seconds

def log_audit_event(db, user, action, resource, details=None):
    log = AuditLogs(
        user_id=user.id if user else None,
        action=action,
        target_type=resource,
        details=json.dumps(details) if details else None
    )
    db.add(log)
    db.commit()

@router.post("/register", response_model=UserOut, summary="Register a new user", description="Register a new user account with email and password.")
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account with email and password."""
    try:
        print(f"📝 [REGISTER] Attempting to register new user: {user.email}")
        
        # Check if user already exists
        existing_user = db.query(Users).filter(Users.email == user.email).first()
        if existing_user:
            print(f"❌ [REGISTER] Registration failed - Email already exists: {user.email}")
            raise HTTPException(status_code=400, detail="Email already registered")
        
        print(f"✅ [REGISTER] Email available, creating new user: {user.email}")
        hashed = get_password_hash(user.password)
        db_user = Users(email=user.email, hashed_password=hashed, role='user')
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        print(f"🎉 [REGISTER] User successfully created - ID: {db_user.id}, Email: {db_user.email}, Plan: {db_user.plan}, Role: {db_user.role}")
        log_audit_event(db, db_user, "register", "user", {"email": db_user.email})
        return db_user
    except Exception as e:
        logger.exception("Error during registration")
        raise HTTPException(status_code=500, detail="Registration failed. Please try again later.")

@router.post("/login", response_model=Token, summary="User login", description="Authenticate a user and return a JWT access token.")
def login(user: UserLogin, db: Session = Depends(get_db), request: Request = None):
    """Authenticate a user and return a JWT access token."""
    client_ip = request.client.host if request else "unknown"
    now = time.time()
    attempts = _login_attempts.get(client_ip, [])
    # Remove old attempts
    attempts = [t for t in attempts if now - t < RATE_PERIOD]
    if len(attempts) >= RATE_LIMIT:
        return JSONResponse(status_code=429, content={"detail": "Too many login attempts. Please wait and try again."})
    attempts.append(now)
    _login_attempts[client_ip] = attempts
    print(f"🔑 [LOGIN] Login attempt for user: {user.email} from {client_ip}")
    
    # Find user in database
    db_user = db.query(Users).filter(Users.email == user.email).first()
    if not db_user:
        print(f"❌ [LOGIN] Login failed - User not found: {user.email}")
        log_audit_event(db, None, "login_failed", "auth", {"email": user.email, "reason": "user_not_found"})
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    print(f"✅ [LOGIN] User found in database - ID: {db_user.id}, Email: {db_user.email}, Plan: {db_user.plan}")
    
    # Verify password
    if not verify_password(user.password, db_user.hashed_password):
        print(f"❌ [LOGIN] Login failed - Invalid password for user: {user.email}")
        log_audit_event(db, db_user, "login_failed", "auth", {"email": user.email, "reason": "invalid_password"})
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    print(f"✅ [LOGIN] Password verified successfully for user: {user.email}")
    
    # 2FA check
    if db_user.two_fa_enabled:
        print(f"🔒 [LOGIN] 2FA required for user: {user.email}")
        log_audit_event(db, db_user, "login_2fa_required", "auth", {"email": user.email})
        return {"2fa_required": True, "user_id": db_user.id}
    
    # Create access token
    token = create_access_token({"sub": str(db_user.id)})
    print(f"🎫 [LOGIN] Access token created successfully for user: {user.email}")
    log_audit_event(db, db_user, "login_success", "auth", {"email": user.email})
    return {"access_token": token, "token_type": "bearer"}

# New endpoint for 2FA step of login
from fastapi import Body

class TwoFALoginRequest(BaseModel):
    user_id: int
    code: str

@router.post("/login/2fa", response_model=Token, summary="2FA login step", description="Authenticate a user with 2FA code and return a JWT access token.")
def login_2fa(data: TwoFALoginRequest, db: Session = Depends(get_db), request: Request = None):
    """Authenticate a user with 2FA code and return a JWT access token using enhanced backup code logic."""
    db_user = db.query(Users).filter(Users.id == data.user_id).first()
    if not db_user or not db_user.two_fa_enabled:
        log_audit_event(db, db_user, "login_2fa_failed", "auth", {"user_id": data.user_id, "reason": "not_enabled_or_not_found"})
        raise HTTPException(status_code=401, detail="2FA not enabled or user not found")
    # Try TOTP
    if db_user.two_fa_secret:
        totp = pyotp.TOTP(db_user.two_fa_secret)
        if totp.verify(data.code):
            token = create_access_token({"sub": str(db_user.id)})
            log_audit_event(db, db_user, "login_2fa_success", "auth", {"user_id": data.user_id})
            return {"access_token": token, "token_type": "bearer"}
    # Try enhanced backup codes (JSON with used flag)
    if db_user.backup_codes:
        backup_codes = json.loads(db_user.backup_codes)
        for backup_code in backup_codes:
            if backup_code["code"] == data.code and not backup_code["used"]:
                backup_code["used"] = True
                db_user.backup_codes = json.dumps(backup_codes)
        db.commit()
        token = create_access_token({"sub": str(db_user.id)})
        log_audit_event(db, db_user, "login_2fa_success_backup", "auth", {"user_id": data.user_id})
        return {"access_token": token, "token_type": "bearer"}
    log_audit_event(db, db_user, "login_2fa_failed", "auth", {"user_id": data.user_id, "reason": "invalid_code"})
    raise HTTPException(status_code=401, detail="Invalid 2FA code")

from fastapi.security import OAuth2PasswordBearer
from fastapi import Request

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    print(f"🔍 [AUTH] Validating JWT token")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            print(f"❌ [AUTH] Token validation failed - No user ID in token")
            raise credentials_exception
        print(f"✅ [AUTH] Token decoded successfully - User ID: {user_id}")
    except JWTError:
        print(f"❌ [AUTH] Token validation failed - JWT decode error")
        raise credentials_exception
    
    # Find user in database
    user = db.query(Users).filter(Users.id == int(user_id)).first()
    if user is None:
        print(f"❌ [AUTH] Token validation failed - User not found in database: {user_id}")
        raise credentials_exception
    
    print(f"✅ [AUTH] User authenticated successfully - ID: {user.id}, Email: {user.email}, Plan: {user.plan}")
    return user

@router.get("/user/me", response_model=UserOut, summary="Get current user", description="Get the authenticated user's profile information.")
def get_me(user: Users = Depends(get_current_user)):
    """Get the authenticated user's profile information."""
    print(f"👤 [USER] Getting current user profile - ID: {user.id}, Email: {user.email}")
    return user

# Helper: Only Pro/Business users can use API key features
def require_api_key_plan(user: Users):
    if user.plan not in ("pro", "business"):
        raise HTTPException(status_code=403, detail="API access is only available for Pro and Business plans.")

@router.get("/api-key", summary="Get API key info", description="Get information about the user's API key (Pro/Business only).")
def get_api_key_info(user: Users = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get information about the user's API key (Pro/Business only)."""
    require_api_key_plan(user)
    return {
        "has_api_key": bool(user.api_key_hash),
        "created_at": user.api_key_created_at,
        "last_used": user.api_key_last_used
    }

@router.post("/api-key", summary="Create API key", description="Generate a new API key for the user (Pro/Business only).")
def create_api_key(user: Users = Depends(get_current_user), db: Session = Depends(get_db)):
    """Generate a new API key for the user (Pro/Business only)."""
    require_api_key_plan(user)
    # Generate a new API key
    api_key = secrets.token_urlsafe(32)
    api_key_hash = api_key_context.hash(api_key)
    user.api_key_hash = api_key_hash
    user.api_key_created_at = datetime.utcnow()
    db.commit()
    return {"api_key": api_key, "created_at": user.api_key_created_at}

@router.delete("/api-key", summary="Revoke API key", description="Revoke the user's API key (Pro/Business only).")
def revoke_api_key(user: Users = Depends(get_current_user), db: Session = Depends(get_db)):
    """Revoke the user's API key (Pro/Business only)."""
    require_api_key_plan(user)
    user.api_key_hash = None
    user.api_key_created_at = None
    user.api_key_last_used = None
    db.commit()
    return {"message": "API key revoked."}

# Utility for future: verify API key
def verify_api_key(api_key: str, user: Users):
    if not user.api_key_hash:
        return False
    return api_key_context.verify(api_key, user.api_key_hash)