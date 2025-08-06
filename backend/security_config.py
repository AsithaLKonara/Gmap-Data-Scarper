"""
LeadTap Security Configuration
Implements security best practices and configurations
"""

import os
from typing import List, Dict, Any

class SecurityConfig:
    """Security configuration class with best practices"""
    
    # JWT Configuration
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', 60))
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRE_DAYS', 7))
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', 100))
    RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', 60))
    RATE_LIMIT_BURST = int(os.getenv('RATE_LIMIT_BURST', 10))
    
    # Password Policy
    MIN_PASSWORD_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_NUMBERS = True
    REQUIRE_SPECIAL_CHARS = True
    PASSWORD_HISTORY_COUNT = 5
    
    # Session Security
    SESSION_TIMEOUT_MINUTES = 30
    MAX_CONCURRENT_SESSIONS = 5
    SESSION_INACTIVITY_TIMEOUT = 15  # minutes
    
    # API Security
    API_KEY_LENGTH = 32
    API_KEY_PREFIX = "lt_"
    API_KEY_EXPIRY_DAYS = 365
    
    # CORS Configuration
    ALLOWED_ORIGINS = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://leadtap.com",
        "https://www.leadtap.com"
    ]
    
    ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    ALLOWED_HEADERS = [
        "Authorization",
        "Content-Type",
        "X-Requested-With",
        "Accept",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers"
    ]
    
    # Security Headers
    SECURITY_HEADERS = {
        "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Content-Security-Policy": (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none';"
        ),
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    }
    
    # Audit Logging
    AUDIT_LOG_RETENTION_DAYS = 90
    AUDIT_LOG_SENSITIVE_FIELDS = ["password", "token", "secret", "key"]
    
    # Input Validation
    MAX_INPUT_LENGTH = 10000
    ALLOWED_FILE_TYPES = [".csv", ".xlsx", ".json"]
    MAX_FILE_SIZE_MB = 10
    
    # Database Security
    DB_CONNECTION_TIMEOUT = 30
    DB_MAX_CONNECTIONS = 20
    DB_CONNECTION_RETRY_ATTEMPTS = 3
    
    @classmethod
    def validate_password(cls, password: str) -> Dict[str, Any]:
        """Validate password against security policy"""
        errors = []
        
        if len(password) < cls.MIN_PASSWORD_LENGTH:
            errors.append(f"Password must be at least {cls.MIN_PASSWORD_LENGTH} characters long")
        
        if cls.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if cls.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if cls.REQUIRE_NUMBERS and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        if cls.REQUIRE_SPECIAL_CHARS and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Password must contain at least one special character")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    @classmethod
    def sanitize_input(cls, input_data: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        if not input_data:
            return ""
        
        # Remove potentially dangerous characters
        dangerous_chars = ["<", ">", "'", '"', "&", ";", "--", "/*", "*/"]
        sanitized = input_data
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, "")
        
        # Limit length
        if len(sanitized) > cls.MAX_INPUT_LENGTH:
            sanitized = sanitized[:cls.MAX_INPUT_LENGTH]
        
        return sanitized.strip()
    
    @classmethod
    def generate_secure_token(cls) -> str:
        """Generate a secure random token"""
        import secrets
        return secrets.token_urlsafe(32)
    
    @classmethod
    def hash_sensitive_data(cls, data: str) -> str:
        """Hash sensitive data for logging"""
        import hashlib
        return hashlib.sha256(data.encode()).hexdigest()[:16] + "..."
    
    @classmethod
    def get_allowed_origins(cls) -> List[str]:
        """Get allowed origins for CORS"""
        return cls.ALLOWED_ORIGINS.copy()
    
    @classmethod
    def get_security_headers(cls) -> Dict[str, str]:
        """Get security headers configuration"""
        return cls.SECURITY_HEADERS.copy()

# Global security config instance
security_config = SecurityConfig() 