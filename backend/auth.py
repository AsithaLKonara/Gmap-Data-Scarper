from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
from models import User
from database import get_db
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
import logging
import secrets
import pyotp
import time
from fastapi import Request
from starlette.responses import JSONResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
api_key_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger = logging.getLogger("auth")

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    plan: str
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

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

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        print(f"📝 [REGISTER] Attempting to register new user: {user.email}")
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            print(f"❌ [REGISTER] Registration failed - Email already exists: {user.email}")
            raise HTTPException(status_code=400, detail="Email already registered")
        
        print(f"✅ [REGISTER] Email available, creating new user: {user.email}")
        hashed = get_password_hash(user.password)
        db_user = User(email=user.email, hashed_password=hashed)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        print(f"🎉 [REGISTER] User successfully created - ID: {db_user.id}, Email: {db_user.email}, Plan: {db_user.plan}")
        return db_user
    except Exception as e:
        logger.exception("Error during registration")
        raise HTTPException(status_code=500, detail="Registration failed. Please try again later.")

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db), request: Request = None):
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
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        print(f"❌ [LOGIN] Login failed - User not found: {user.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    print(f"✅ [LOGIN] User found in database - ID: {db_user.id}, Email: {db_user.email}, Plan: {db_user.plan}")
    
    # Verify password
    if not verify_password(user.password, db_user.hashed_password):
        print(f"❌ [LOGIN] Login failed - Invalid password for user: {user.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    print(f"✅ [LOGIN] Password verified successfully for user: {user.email}")
    
    # Create access token
    token = create_access_token({"sub": str(db_user.id)})
    print(f"🎫 [LOGIN] Access token created successfully for user: {user.email}")
    
    return {"access_token": token, "token_type": "bearer"}

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
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        print(f"❌ [AUTH] Token validation failed - User not found in database: {user_id}")
        raise credentials_exception
    
    print(f"✅ [AUTH] User authenticated successfully - ID: {user.id}, Email: {user.email}, Plan: {user.plan}")
    return user

@router.get("/user/me", response_model=UserOut)
def get_me(user: User = Depends(get_current_user)):
    print(f"👤 [USER] Getting current user profile - ID: {user.id}, Email: {user.email}")
    return user

# Helper: Only Pro/Business users can use API key features
def require_api_key_plan(user: User):
    if user.plan not in ("pro", "business"):
        raise HTTPException(status_code=403, detail="API access is only available for Pro and Business plans.")

@router.get("/api-key")
def get_api_key_info(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_api_key_plan(user)
    return {
        "has_api_key": bool(user.api_key_hash),
        "created_at": user.api_key_created_at,
        "last_used": user.api_key_last_used
    }

@router.post("/api-key")
def create_api_key(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_api_key_plan(user)
    # Generate a new API key
    api_key = secrets.token_urlsafe(32)
    api_key_hash = api_key_context.hash(api_key)
    user.api_key_hash = api_key_hash
    user.api_key_created_at = datetime.utcnow()
    db.commit()
    return {"api_key": api_key, "created_at": user.api_key_created_at}

@router.delete("/api-key")
def revoke_api_key(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_api_key_plan(user)
    user.api_key_hash = None
    user.api_key_created_at = None
    user.api_key_last_used = None
    db.commit()
    return {"message": "API key revoked."}

# Utility for future: verify API key
def verify_api_key(api_key: str, user: User):
    if not user.api_key_hash:
        return False
    return api_key_context.verify(api_key, user.api_key_hash)

@router.post("/2fa/enable")
def enable_2fa(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.notes and '2fa_secret:' in user.notes:
        raise HTTPException(status_code=400, detail="2FA already enabled")
    secret = pyotp.random_base32()
    user.notes = (user.notes or "") + f"\n2fa_secret:{secret}"
    db.commit()
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=user.email, issuer_name="LeadTap")
    return {"secret": secret, "uri": uri}

@router.post("/2fa/verify")
def verify_2fa(code: str = Body(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    secret = None
    if user.notes and '2fa_secret:' in user.notes:
        for line in user.notes.split('\n'):
            if line.startswith('2fa_secret:'):
                secret = line.split(':', 1)[1]
    if not secret:
        raise HTTPException(status_code=400, detail="2FA not enabled")
    totp = pyotp.TOTP(secret)
    if not totp.verify(code):
        raise HTTPException(status_code=400, detail="Invalid 2FA code")
    return {"status": "verified"}

@router.post("/2fa/disable")
def disable_2fa(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not user.notes or '2fa_secret:' not in user.notes:
        raise HTTPException(status_code=400, detail="2FA not enabled")
    user.notes = '\n'.join([line for line in (user.notes or '').split('\n') if not line.startswith('2fa_secret:')])
    db.commit()
    return {"status": "2FA disabled"} 