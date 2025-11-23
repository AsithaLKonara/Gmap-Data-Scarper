"""Security middleware for headers and input sanitization."""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import re
from typing import Optional


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' ws: wss:; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
        
        return response


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Truncate to max length
    text = text[:max_length]
    
    # Remove null bytes
    text = text.replace("\x00", "")
    
    # Remove control characters (except newline, tab, carriage return)
    text = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]", "", text)
    
    # Normalize whitespace
    text = " ".join(text.split())
    
    return text.strip()


def validate_query(query: str) -> tuple[bool, Optional[str]]:
    """
    Validate search query for security.
    
    Args:
        query: Search query string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not query or not query.strip():
        return False, "Query cannot be empty"
    
    if len(query) > 500:
        return False, "Query is too long (maximum 500 characters)"
    
    if len(query) < 2:
        return False, "Query is too short (minimum 2 characters)"
    
    # Check for potentially dangerous patterns
    dangerous_patterns = [
        r"<script",
        r"javascript:",
        r"on\w+\s*=",  # Event handlers
        r"data:text/html",
        r"vbscript:",
    ]
    
    query_lower = query.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, query_lower):
            return False, f"Query contains potentially unsafe content"
    
    # Check for SQL injection patterns (basic)
    sql_patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|\#|/\*|\*/)",
        r"(\b(UNION|OR|AND)\s+\d+\s*=\s*\d+)",
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, query_lower):
            return False, "Query contains potentially unsafe SQL patterns"
    
    return True, None


def validate_platform(platform: str) -> tuple[bool, Optional[str]]:
    """
    Validate platform name against whitelist.
    
    Args:
        platform: Platform name
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    allowed_platforms = {
        "google_maps",
        "facebook",
        "instagram",
        "linkedin",
        "x",
        "twitter",
        "youtube",
        "tiktok",
    }
    
    if platform not in allowed_platforms:
        return False, f"Invalid platform: {platform}. Allowed: {', '.join(sorted(allowed_platforms))}"
    
    return True, None


def sanitize_url(url: str) -> Optional[str]:
    """
    Sanitize and validate URL.
    
    Args:
        url: URL to sanitize
        
    Returns:
        Sanitized URL or None if invalid
    """
    if not url:
        return None
    
    # Basic URL validation
    url_pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # IP
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE
    )
    
    if not url_pattern.match(url):
        return None
    
    # Remove dangerous protocols
    if url.lower().startswith(("javascript:", "data:", "vbscript:")):
        return None
    
    return url.strip()

