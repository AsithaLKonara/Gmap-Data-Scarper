from fastapi import APIRouter, Depends, HTTPException, Body, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from models import User, AuditLog, Role, Permission, UserRole
from database import get_db
from auth import get_current_user
import pyotp
import secrets
import json
import logging
from datetime import datetime, timedelta
from enum import Enum

router = APIRouter(prefix="/api/security", tags=["security"])
logger = logging.getLogger("security")

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

# Pydantic models
class BackupCode(BaseModel):
    code: str
    used: bool = False

class TwoFactorSetup(BaseModel):
    secret: str
    qr_code: str
    backup_codes: List[str]

class RoleCreate(BaseModel):
    name: str
    description: str
    permissions: List[str]

class PermissionCheck(BaseModel):
    resource: str
    action: str

class AuditLogEntry(BaseModel):
    user_id: int
    action: str
    resource: str
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

# Security utilities
def generate_backup_codes(count: int = 10) -> List[str]:
    """Generate backup codes for 2FA"""
    codes = []
    for _ in range(count):
        code = secrets.token_hex(4).upper()  # 8-character hex code
        codes.append(code)
    return codes

def verify_backup_code(user: User, code: str, db: Session) -> bool:
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

def log_security_event(
    user_id: int,
    action: str,
    resource: str,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    db: Session = None
):
    """Log security events for audit trail"""
    try:
        if db:
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                resource=resource,
                details=json.dumps(details) if details else None,
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=datetime.utcnow()
            )
            db.add(audit_log)
            db.commit()
        logger.info(f"Security event: {action} on {resource} by user {user_id}")
    except Exception as e:
        logger.error(f"Failed to log security event: {e}")

def check_permission(user: User, resource: str, action: str, db: Session) -> bool:
    """Check if user has permission for specific resource and action"""
    # Admin users have all permissions
    if user.plan == "business" and user.is_admin:
        return True
    
    # Get user roles and permissions
    user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
    
    for user_role in user_roles:
        role = db.query(Role).filter(Role.id == user_role.role_id).first()
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
                if isinstance(arg, User):
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
@router.post("/2fa/setup", response_model=TwoFactorSetup)
def setup_2fa(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Setup 2FA with QR code and backup codes"""
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

@router.post("/2fa/verify-and-enable")
def verify_and_enable_2fa(
    code: str = Body(...),
    request: Request = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Verify 2FA code and enable 2FA"""
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

@router.post("/2fa/verify-login")
def verify_2fa_login(
    code: str = Body(...),
    request: Request = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Verify 2FA code during login"""
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

@router.post("/2fa/disable")
def disable_2fa(
    request: Request = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Disable 2FA"""
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

@router.post("/2fa/regenerate-backup-codes")
def regenerate_backup_codes(
    request: Request = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Regenerate backup codes"""
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
@router.get("/roles")
def get_roles(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get all available roles"""
    if not check_permission(user, "roles", "read", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    roles = db.query(Role).all()
    return [
        {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "permissions": json.loads(role.permissions) if role.permissions else []
        }
        for role in roles
    ]

@router.post("/roles")
def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Create a new role"""
    if not check_permission(user, "roles", "write", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    role = Role(
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

@router.post("/users/{user_id}/roles/{role_id}")
def assign_role(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign a role to a user"""
    if not check_permission(current_user, "users", "write", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    role = db.query(Role).filter(Role.id == role_id).first()
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

# Security audit endpoints
@router.get("/audit-logs")
def get_security_audit_logs(
    page: int = 1,
    page_size: int = 20,
    action: Optional[str] = None,
    resource: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get security audit logs"""
    if not check_permission(current_user, "audit", "read", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    query = db.query(AuditLog)
    
    if action:
        query = query.filter(AuditLog.action == action)
    if resource:
        query = query.filter(AuditLog.resource == resource)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    total = query.count()
    logs = query.order_by(AuditLog.timestamp.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
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

@router.get("/security-status")
def get_security_status(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get user's security status"""
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

def calculate_security_score(user: User) -> int:
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

# Security middleware for logging all requests
@router.middleware("http")
async def security_middleware(request: Request, call_next):
    """Middleware to log security-relevant requests"""
    response = await call_next(request)
    
    # Log security-relevant actions
    if request.url.path.startswith("/api/security/"):
        # Extract user info if available
        user_id = None
        try:
            # This is a simplified version - in practice, you'd extract from JWT
            pass
        except:
            pass
        
        log_security_event(
            user_id=user_id,
            action="security_access",
            resource=request.url.path,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
    
    return response 