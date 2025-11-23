"""Structured logging with JSON format and context propagation."""
import json
import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime
from contextvars import ContextVar

# Context variable for request context
request_context: ContextVar[Dict[str, Any]] = ContextVar('request_context', default={})


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add context if available
        ctx = request_context.get({})
        if ctx:
            log_data["context"] = ctx
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data)


def setup_structured_logging(
    level: str = "INFO",
    output_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up structured logging.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        output_file: Optional file path for log output
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    
    # File handler if specified
    if output_file:
        file_handler = logging.FileHandler(output_file)
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
    
    return logger


def set_request_context(**kwargs):
    """Set request context for logging."""
    ctx = request_context.get({}).copy()
    ctx.update(kwargs)
    request_context.set(ctx)


def clear_request_context():
    """Clear request context."""
    request_context.set({})


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    return logging.getLogger(name)


class ContextLogger:
    """Logger with context support."""
    
    def __init__(self, name: str, **context):
        self.logger = logging.getLogger(name)
        self.context = context
    
    def _log(self, level: int, message: str, **extra):
        """Internal log method with context."""
        ctx = request_context.get({}).copy()
        ctx.update(self.context)
        ctx.update(extra)
        
        # Create a new record with extra fields
        record = logging.LogRecord(
            name=self.logger.name,
            level=level,
            pathname="",
            lineno=0,
            msg=message,
            args=(),
            exc_info=None
        )
        record.extra_fields = ctx
        self.logger.handle(record)
    
    def debug(self, message: str, **extra):
        """Log debug message."""
        self._log(logging.DEBUG, message, **extra)
    
    def info(self, message: str, **extra):
        """Log info message."""
        self._log(logging.INFO, message, **extra)
    
    def warning(self, message: str, **extra):
        """Log warning message."""
        self._log(logging.WARNING, message, **extra)
    
    def error(self, message: str, **extra):
        """Log error message."""
        self._log(logging.ERROR, message, **extra)
    
    def critical(self, message: str, **extra):
        """Log critical message."""
        self._log(logging.CRITICAL, message, **extra)

