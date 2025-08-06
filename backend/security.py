from fastapi import APIRouter, Depends, HTTPException, status, Request, Body, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from models import Users, AuditLogs, UserRole
from database import get_db
from auth import get_current_user
import pyotp
import secrets
import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from audit import audit_log
import time
import hashlib
from config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW

router = APIRouter(prefix="/api/security", tags=["security"])
security = HTTPBearer()
logger = logging.getLogger(__name__)

# In-memory rate limiting (replace with Redis in production)
_rate_limit_store: Dict[str, Dict[str, Any]] = {}

class RateLimiter:
    def __init__(self, max_requests: int = RATE_LIMIT_REQUESTS, window_seconds: int = RATE_LIMIT_WINDOW):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed based on rate limiting rules"""
        now = time.time()
        
        if key not in _rate_limit_store:
            _rate_limit_store[key] = {
                'requests': [],
                'blocked_until': None
            }
        
        # Check if currently blocked
        if _rate_limit_store[key]['blocked_until'] and now < _rate_limit_store[key]['blocked_until']:
            return False
        
        # Clean old requests outside the window
        window_start = now - self.window_seconds
        _rate_limit_store[key]['requests'] = [
            req_time for req_time in _rate_limit_store[key]['requests'] 
            if req_time > window_start
        ]
        
        # Check if under limit
        if len(_rate_limit_store[key]['requests']) < self.max_requests:
            _rate_limit_store[key]['requests'].append(now)
            return True
        
        # Block for window duration
        _rate_limit_store[key]['blocked_until'] = now + self.window_seconds
        return False
    
    def get_remaining_requests(self, key: str) -> int:
        """Get remaining requests for the current window"""
        now = time.time()
        window_start = now - self.window_seconds
        
        if key not in _rate_limit_store:
            return self.max_requests
        
        # Clean old requests
        _rate_limit_store[key]['requests'] = [
            req_time for req_time in _rate_limit_store[key]['requests'] 
            if req_time > window_start
        ]
        
        return max(0, self.max_requests - len(_rate_limit_store[key]['requests']))

# Global rate limiter instance
rate_limiter = RateLimiter()

def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host

def get_rate_limit_key(request: Request, user_id: Optional[int] = None) -> str:
    """Generate rate limiting key based on IP and user"""
    client_ip = get_client_ip(request)
    if user_id:
        return f"user:{user_id}:{client_ip}"
    return f"ip:{client_ip}"

def check_rate_limit(request: Request, user_id: Optional[int] = None) -> bool:
    """Check if request is within rate limits"""
    key = get_rate_limit_key(request, user_id)
    return rate_limiter.is_allowed(key)

# Security enums
class PermissionType(str, Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    EXPORT = "export"
    ANALYTICS = "analytics"
    TEAM_MANAGE = "team_manage"
    API_ACCESS = "api_access"

class RoleType(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"
    USER = "user"

# --- Pydantic Models for OpenAPI ---
class BackupCode(BaseModel):
    code: str = Field(..., description="Backup code string.")
    used: bool = Field(False, description="Whether the code has been used.")

class TwoFactorSetup(BaseModel):
    secret: str = Field(..., description="TOTP secret for 2FA.")
    qr_code: str = Field(..., description="QR code URI for authenticator apps.")
    backup_codes: List[str] = Field(..., description="List of backup codes.")

class TwoFactorVerifyRequest(BaseModel):
    code: str = Field(..., description="TOTP or backup code to verify.")

class TwoFactorDisableResponse(BaseModel):
    success: bool
    message: str

class RoleCreate(BaseModel):
    name: str = Field(..., description="Role name.")
    description: str = Field(..., description="Role description.")
    permissions: List[str] = Field(..., description="List of permissions for the role.")

class RoleOut(BaseModel):
    id: int
    name: str
    description: str
    permissions: List[str]

class PermissionCheck(BaseModel):
    resource: str = Field(..., description="Resource name.")
    action: str = Field(..., description="Action name.")

class AuditLogEntry(BaseModel):
    user_id: int
    action: str
    resource: str
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class SecurityAuditLogOut(BaseModel):
    id: int
    user_id: int
    action: str
    resource: str
    details: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    user_agent: Optional[str]
    timestamp: datetime

class SecurityAuditLogListResponse(BaseModel):
    results: List[SecurityAuditLogOut]
    total: int

class SecurityStatusResponse(BaseModel):
    two_fa_enabled: bool
    roles: List[str]
    permissions: List[str]
    security_score: int

# Security utilities
def generate_backup_codes(count: int = 10) -> List[str]:
    """Generate backup codes for 2FA"""
    codes = []
    for _ in range(count):
        code = secrets.token_hex(4).upper()  # 8-character hex code
        codes.append(code)
    return codes

def verify_backup_code(user: Users, code: str, db: Session) -> bool:
    """Verify a backup code and mark it as used"""
    if not user.backup_codes:
        return False
    
    backup_codes = json.loads(user.backup_codes)
    for backup_code in backup_codes:
        if backup_code["code"] == code and not backup_code["used"]:
            backup_code["used"] = True
            user.backup_codes = json.dumps(backup_codes)
            db.commit()
            return True
    return False

def log_security_event(db: Session, user_id: Optional[int], event_type: str, details: Dict[str, Any]):
    """Log security events for audit purposes"""
    try:
        audit_log = AuditLogs(
            user_id=user_id,
            action=event_type,
            target_type="security",
            details=json.dumps(details)
        )
        db.add(audit_log)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to log security event: {e}")

def check_permission(user: Users, resource: str, action: str, db: Session) -> bool:
    """Check if user has permission for specific resource and action"""
    # Admin users have all permissions
    if user.plan == "business" and user.is_admin:
        return True
    
    # Get user roles and permissions
    user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
    
    for user_role in user_roles:
        role = db.query(Roles).filter(Roles.id == user_role.role_id).first()
        if role:
            permissions = json.loads(role.permissions) if role.permissions else []
            if f"{resource}:{action}" in permissions or f"{resource}:*" in permissions:
                return True
    
    # Plan-based permissions
    plan_permissions = {
        "free": ["jobs:read", "leads:read"],
        "pro": ["jobs:read", "jobs:write", "leads:read", "leads:write", "export:read", "analytics:read"],
        "business": ["jobs:*", "leads:*", "export:*", "analytics:*", "team:manage", "api:access"]
    }
    
    user_permissions = plan_permissions.get(user.plan, [])
    return f"{resource}:{action}" in user_permissions or f"{resource}:*" in user_permissions

def require_permission(resource: str, action: str):
    """Decorator to require specific permission"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract user and db from function arguments
            user = None
            db = None
            for arg in args:
                if isinstance(arg, Users):
                    user = arg
                elif hasattr(arg, 'query'):  # Session object
                    db = arg
            
            if not user or not db:
                raise HTTPException(status_code=500, detail="Internal server error")
            
            if not check_permission(user, resource, action, db):
                log_security_event(
                    user_id=user.id,
                    action="permission_denied",
                    resource=f"{resource}:{action}",
                    details={"attempted_action": action, "resource": resource}
                )
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Enhanced 2FA endpoints
@router.post("/2fa/setup", response_model=TwoFactorSetup, summary="Setup 2FA", description="Setup 2FA with QR code and backup codes.")
def setup_2fa(
    request: Request,
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Setup 2FA with QR code and backup codes."""
    if user.two_fa_enabled:
        raise HTTPException(status_code=400, detail="2FA is already enabled")
    
    # Generate TOTP secret
    secret = pyotp.random_base32()
    
    # Generate QR code URI
    totp = pyotp.TOTP(secret)
    qr_code = totp.provisioning_uri(
        name=user.email,
        issuer_name="LeadTap"
    )
    
    # Generate backup codes
    backup_codes = generate_backup_codes()
    backup_codes_json = json.dumps([{"code": code, "used": False} for code in backup_codes])
    
    # Store secret temporarily (user needs to verify before enabling)
    user.two_fa_secret = secret
    user.backup_codes = backup_codes_json
    db.commit()
    
    log_security_event(
        user_id=user.id,
        action="2fa_setup_initiated",
        resource="security",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        db=db
    )
    
    return {
        "secret": secret,
        "qr_code": qr_code,
        "backup_codes": backup_codes
    }

@router.post("/2fa/verify-and-enable", response_model=TwoFactorSetup, summary="Verify and enable 2FA", description="Verify 2FA code and enable 2FA for the user.")
def verify_and_enable_2fa(
    code: str = Body(..., embed=True, description="TOTP or backup code to verify."),
    request: Request = None,
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Verify 2FA code and enable 2FA for the user."""
    if not user.two_fa_secret:
        raise HTTPException(status_code=400, detail="2FA setup not initiated")
    
    # Verify TOTP code
    totp = pyotp.TOTP(user.two_fa_secret)
    if not totp.verify(code):
        log_security_event(
            user_id=user.id,
            action="2fa_verification_failed",
            resource="security",
            ip_address=request.client.host if request else None,
            db=db
        )
        raise HTTPException(status_code=400, detail="Invalid verification code")
    
    # Enable 2FA
    user.two_fa_enabled = True
    user.two_fa_enabled_at = datetime.utcnow()
    db.commit()
    
    log_security_event(
        user_id=user.id,
        action="2fa_enabled",
        resource="security",
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None,
        db=db
    )
    
    return {"status": "2FA enabled successfully"}

@router.post("/2fa/verify-login", response_model=TwoFactorSetup, summary="Verify 2FA login", description="Verify 2FA code during login.")
def verify_2fa_login(
    code: str = Body(..., embed=True, description="TOTP or backup code to verify."),
    request: Request = None,
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Verify 2FA code during login."""
    if not user.two_fa_enabled:
        raise HTTPException(status_code=400, detail="2FA not enabled")
    
    # Try TOTP first
    if user.two_fa_secret:
        totp = pyotp.TOTP(user.two_fa_secret)
        if totp.verify(code):
            log_security_event(
                user_id=user.id,
                action="2fa_login_success",
                resource="security",
                ip_address=request.client.host if request else None,
                db=db
            )
            return {"status": "verified"}
    
    # Try backup code
    if verify_backup_code(user, code, db):
        log_security_event(
            user_id=user.id,
            action="2fa_backup_code_used",
            resource="security",
            ip_address=request.client.host if request else None,
            db=db
        )
        return {"status": "verified_with_backup"}
    
    log_security_event(
        user_id=user.id,
        action="2fa_verification_failed",
        resource="security",
        ip_address=request.client.host if request else None,
        db=db
    )
    raise HTTPException(status_code=400, detail="Invalid 2FA code")

@router.post("/2fa/disable", response_model=TwoFactorDisableResponse, summary="Disable 2FA", description="Disable 2FA for the user.")
def disable_2fa(
    request: Request = None,
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Disable 2FA for the user."""
    if not user.two_fa_enabled:
        raise HTTPException(status_code=400, detail="2FA not enabled")
    
    user.two_fa_enabled = False
    user.two_fa_secret = None
    user.backup_codes = None
    user.two_fa_enabled_at = None
    db.commit()
    
    log_security_event(
        user_id=user.id,
        action="2fa_disabled",
        resource="security",
        ip_address=request.client.host if request else None,
        db=db
    )
    
    return {"status": "2FA disabled successfully"}

@router.post("/2fa/regenerate-backup-codes", response_model=TwoFactorSetup, summary="Regenerate backup codes", description="Regenerate backup codes for 2FA.")
def regenerate_backup_codes(
    request: Request = None,
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Regenerate backup codes for 2FA."""
    if not user.two_fa_enabled:
        raise HTTPException(status_code=400, detail="2FA not enabled")
    
    backup_codes = generate_backup_codes()
    backup_codes_json = json.dumps([{"code": code, "used": False} for code in backup_codes])
    user.backup_codes = backup_codes_json
    db.commit()
    
    log_security_event(
        user_id=user.id,
        action="backup_codes_regenerated",
        resource="security",
        ip_address=request.client.host if request else None,
        db=db
    )
    
    return {"backup_codes": backup_codes}

# RBAC endpoints
@router.get("/roles", response_model=List[RoleOut], summary="List roles", description="Get all available roles.")
def get_roles(db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    """Get all available roles."""
    if not check_permission(user, "roles", "read", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    roles = db.query(Roles).all()
    return [
        {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "permissions": json.loads(role.permissions) if role.permissions else []
        }
        for role in roles
    ]

@router.post("/roles", response_model=RoleOut, summary="Create role", description="Create a new role.")
@audit_log(action="create_role", target_type="role")
def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Create a new role."""
    if not check_permission(user, "roles", "write", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    role = Roles(
        name=role_data.name,
        description=role_data.description,
        permissions=json.dumps(role_data.permissions)
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    
    log_security_event(
        user_id=user.id,
        action="role_created",
        resource="roles",
        details={"role_name": role_data.name, "permissions": role_data.permissions},
        db=db
    )
    
    return {"id": role.id, "name": role.name}

@router.put("/roles/{role_id}", response_model=RoleOut, summary="Update role", description="Update a role by ID.")
@audit_log(action="update_role", target_type="role", target_id_param="role_id")
def update_role(
    role_id: int = Path(..., description="ID of the role."),
    role_data: RoleCreate = Body(...),
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Update a role by ID."""
    if not check_permission(user, "roles", "write", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    role = db.query(Roles).filter(Roles.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    role.name = role_data.name
    role.description = role_data.description
    role.permissions = json.dumps(role_data.permissions)
    db.commit()
    log_security_event(
        user_id=user.id,
        action="role_updated",
        resource="roles",
        details={"role_id": role_id, "role_name": role_data.name, "permissions": role_data.permissions},
        db=db
    )
    return {"id": role.id, "name": role.name}

@router.delete("/roles/{role_id}", summary="Delete role", description="Delete a role by ID.")
@audit_log(action="delete_role", target_type="role", target_id_param="role_id")
def delete_role(
    role_id: int = Path(..., description="ID of the role."),
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Delete a role by ID."""
    if not check_permission(user, "roles", "delete", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    role = db.query(Roles).filter(Roles.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    db.delete(role)
    db.commit()
    log_security_event(
        user_id=user.id,
        action="role_deleted",
        resource="roles",
        details={"role_id": role_id},
        db=db
    )
    return {"status": "Role deleted successfully"}

@router.post("/users/{user_id}/roles/{role_id}", summary="Assign role to user", description="Assign a role to a user by user ID and role ID.")
@audit_log(action="assign_role", target_type="user", target_id_param="user_id")
def assign_role(
    user_id: int = Path(..., description="ID of the user."),
    role_id: int = Path(..., description="ID of the role."),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Assign a role to a user by user ID and role ID."""
    if not check_permission(current_user, "users", "write", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    target_user = db.query(Users).filter(Users.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    role = db.query(Roles).filter(Roles.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Check if role is already assigned
    existing = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.role_id == role_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Role already assigned")
    
    user_role = UserRole(user_id=user_id, role_id=role_id)
    db.add(user_role)
    db.commit()
    
    log_security_event(
        user_id=current_user.id,
        action="role_assigned",
        resource="users",
        details={"target_user_id": user_id, "role_id": role_id},
        db=db
    )
    
    return {"status": "Role assigned successfully"}

@router.delete("/users/{user_id}/roles/{role_id}", summary="Remove role from user", description="Remove a role from a user by user ID and role ID.")
@audit_log(action="remove_role", target_type="user", target_id_param="user_id")
def remove_role_from_user(
    user_id: int = Path(..., description="ID of the user."),
    role_id: int = Path(..., description="ID of the role."),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Remove a role from a user by user ID and role ID."""
    if not check_permission(current_user, "users", "write", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    user_role = db.query(UserRole).filter(UserRole.user_id == user_id, UserRole.role_id == role_id).first()
    if not user_role:
        raise HTTPException(status_code=404, detail="Role assignment not found")
    db.delete(user_role)
    db.commit()
    log_security_event(
        user_id=current_user.id,
        action="role_removed",
        resource="users",
        details={"target_user_id": user_id, "role_id": role_id},
        db=db
    )
    return {"status": "Role removed from user successfully"}

# Security audit endpoints
@router.get("/audit-logs", response_model=SecurityAuditLogListResponse, summary="Get security audit logs", description="Get a paginated list of security audit logs with optional filters.")
def get_security_audit_logs(
    page: int = 1,
    page_size: int = 20,
    action: Optional[str] = None,
    resource: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Get a paginated list of security audit logs with optional filters."""
    if not check_permission(current_user, "audit", "read", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    query = db.query(AuditLogs)
    
    if action:
        query = query.filter(AuditLogs.action == action)
    if resource:
        query = query.filter(AuditLogs.resource == resource)
    if user_id:
        query = query.filter(AuditLogs.user_id == user_id)
    
    total = query.count()
    logs = query.order_by(AuditLogs.timestamp.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "resource": log.resource,
                "details": json.loads(log.details) if log.details else None,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None
            }
            for log in logs
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/security-status", response_model=SecurityStatusResponse, summary="Get security status", description="Get the current user's security status, roles, permissions, and security score.")
def get_security_status(
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user)
):
    """Get the current user's security status, roles, permissions, and security score."""
    return {
        "two_fa_enabled": user.two_fa_enabled,
        "two_fa_enabled_at": user.two_fa_enabled_at.isoformat() if user.two_fa_enabled_at else None,
        "backup_codes_remaining": len([c for c in json.loads(user.backup_codes) if not c["used"]]) if user.backup_codes else 0,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "failed_login_attempts": user.failed_login_attempts or 0,
        "account_locked": user.account_locked or False,
        "session_timeout": user.session_timeout or 30,
        "security_score": calculate_security_score(user)
    }

def calculate_security_score(user: Users) -> int:
    """Calculate user's security score (0-100)"""
    score = 0
    
    # 2FA enabled: +30 points
    if user.two_fa_enabled:
        score += 30
    
    # Strong password (would need password strength check): +20 points
    # For now, assume all passwords are strong
    score += 20
    
    # Recent login: +10 points
    if user.last_login and (datetime.utcnow() - user.last_login).days < 7:
        score += 10
    
    # No failed attempts: +10 points
    if not user.failed_login_attempts or user.failed_login_attempts == 0:
        score += 10
    
    # Account not locked: +10 points
    if not user.account_locked:
        score += 10
    
    # Business plan (more security features): +10 points
    if user.plan == "business":
        score += 10
    
    return min(score, 100)

# Removed @router.middleware('http') and its function, as APIRouter does not support middleware. If needed, move to main.py as app middleware. 

@router.get("/rate-limit/status")
async def get_rate_limit_status(request: Request, db: Session = Depends(get_db)):
    """Get current rate limiting status for the client"""
    client_ip = get_client_ip(request)
    key = get_rate_limit_key(request)
    
    remaining = rate_limiter.get_remaining_requests(key)
    
    return {
        "remaining_requests": remaining,
        "max_requests": RATE_LIMIT_REQUESTS,
        "window_seconds": RATE_LIMIT_WINDOW,
        "client_ip": client_ip
    }

@router.post("/audit/log")
async def log_security_event_endpoint(
    request: Request,
    event_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Log a security event"""
    client_ip = get_client_ip(request)
    user_id = getattr(request.state, 'user_id', None)
    
    log_security_event(db, user_id, "security_event", {
        "client_ip": client_ip,
        "user_agent": request.headers.get("User-Agent"),
        "event_data": event_data
    })
    
    return {"status": "logged"}

# Security middleware for rate limiting
async def security_middleware(request: Request, call_next):
    """Middleware to apply security checks including rate limiting"""
    client_ip = get_client_ip(request)
    
    # Skip rate limiting for health checks and static files
    if request.url.path in ["/health", "/api/health", "/docs", "/redoc"]:
        return await call_next(request)
    
    # Check rate limiting
    if not check_rate_limit(request):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    # Add security headers
    response = await call_next(request)
    response.headers["X-RateLimit-Remaining"] = str(rate_limiter.get_remaining_requests(get_rate_limit_key(request)))
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_REQUESTS)
    response.headers["X-RateLimit-Reset"] = str(int(time.time() + RATE_LIMIT_WINDOW))
    
    return response 