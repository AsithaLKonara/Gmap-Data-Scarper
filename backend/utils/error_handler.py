"""Centralized error handling utilities for backend."""
from fastapi import HTTPException, status
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base application error with standardized format."""
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


def create_error_response(
    message: str,
    code: Optional[str] = None,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        code: Error code (optional)
        status_code: HTTP status code
        details: Additional error details (optional)
        
    Returns:
        HTTPException with standardized format
    """
    error_detail = {
        "error": message,
        "code": code or "UNKNOWN_ERROR",
    }
    
    if details:
        error_detail["details"] = details
    
    return HTTPException(
        status_code=status_code,
        detail=error_detail
    )


def handle_exception(
    error: Exception,
    context: Optional[str] = None,
    default_message: str = "An error occurred",
    default_code: str = "INTERNAL_ERROR"
) -> HTTPException:
    """
    Handle exception and return standardized error response.
    
    Args:
        error: Exception to handle
        context: Context where error occurred (for logging)
        default_message: Default error message
        default_code: Default error code
        
    Returns:
        HTTPException with standardized format
    """
    # Log the error
    log_context = f"[{context}]" if context else ""
    logger.error(f"{log_context} {type(error).__name__}: {str(error)}", exc_info=True)
    
    # Handle specific exception types
    if isinstance(error, AppError):
        return create_error_response(
            message=error.message,
            code=error.code or default_code,
            status_code=error.status_code,
            details=error.details
        )
    elif isinstance(error, HTTPException):
        # Already an HTTPException, return as-is but ensure standardized format
        if isinstance(error.detail, dict):
            return error
        else:
            return create_error_response(
                message=str(error.detail),
                status_code=error.status_code
            )
    elif isinstance(error, ValueError):
        return create_error_response(
            message=str(error),
            code="VALIDATION_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    elif isinstance(error, PermissionError):
        return create_error_response(
            message=str(error) or "Permission denied",
            code="PERMISSION_DENIED",
            status_code=status.HTTP_403_FORBIDDEN
        )
    elif isinstance(error, FileNotFoundError):
        return create_error_response(
            message=str(error) or "Resource not found",
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )
    else:
        # Generic error
        return create_error_response(
            message=default_message,
            code=default_code,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"original_error": str(error)} if str(error) != default_message else None
        )


def validation_error(message: str, details: Optional[Dict[str, Any]] = None) -> HTTPException:
    """Create a validation error response."""
    return create_error_response(
        message=message,
        code="VALIDATION_ERROR",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details=details
    )


def not_found_error(resource: str = "Resource") -> HTTPException:
    """Create a not found error response."""
    return create_error_response(
        message=f"{resource} not found",
        code="NOT_FOUND",
        status_code=status.HTTP_404_NOT_FOUND
    )


def unauthorized_error(message: str = "Authentication required") -> HTTPException:
    """Create an unauthorized error response."""
    return create_error_response(
        message=message,
        code="UNAUTHORIZED",
        status_code=status.HTTP_401_UNAUTHORIZED
    )


def forbidden_error(message: str = "Permission denied") -> HTTPException:
    """Create a forbidden error response."""
    return create_error_response(
        message=message,
        code="FORBIDDEN",
        status_code=status.HTTP_403_FORBIDDEN
    )


def rate_limit_error(message: str = "Rate limit exceeded") -> HTTPException:
    """Create a rate limit error response."""
    return create_error_response(
        message=message,
        code="RATE_LIMIT_ERROR",
        status_code=status.HTTP_429_TOO_MANY_REQUESTS
    )

