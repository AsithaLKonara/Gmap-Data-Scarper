"""Backend configuration settings (package form).

Historically the project used a single ``backend/config.py`` module. A
``backend.config`` package was later added for pricing and other config
concerns, which caused imports like::

    from backend.config import CORS_ORIGINS, API_HOST, API_PORT, API_RELOAD, TASK_TIMEOUT_SECONDS

to break, because Python started resolving ``backend.config`` as the package
instead of the original module.  This file now hosts the canonical runtime
configuration so those imports continue to work.
"""

import os
from typing import Optional, List

# API Configuration
API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
API_PORT: int = int(os.getenv("API_PORT", "8000"))
API_RELOAD: bool = os.getenv("API_RELOAD", "true").lower() == "true"

# CORS Configuration
_cors_origins_env = os.getenv("CORS_ORIGINS", "")
CORS_ORIGINS: List[str] = (
    _cors_origins_env.split(",")
    if _cors_origins_env
    else [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]
)

# Chrome Streaming Configuration
CHROME_DEBUG_PORT: int = int(os.getenv("CHROME_DEBUG_PORT", "9222"))
STREAM_FPS: int = int(os.getenv("STREAM_FPS", "2"))  # Frames per second for MJPEG stream
SCREENSHOT_DIR: str = os.getenv("SCREENSHOT_DIR", "screenshots")

# Task Management
TASK_TIMEOUT_SECONDS: int = int(os.getenv("TASK_TIMEOUT_SECONDS", "3600"))  # 1 hour default

# Output Directory
DEFAULT_OUTPUT_DIR: str = os.path.expanduser(
    os.getenv("OUTPUT_DIR", "~/Documents/social_leads")
)

# AI Configuration
OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
USE_OPENAI: bool = OPENAI_API_KEY is not None
USE_HUGGINGFACE: bool = os.getenv("USE_HUGGINGFACE", "true").lower() == "true"

__all__ = [
    "API_HOST",
    "API_PORT",
    "API_RELOAD",
    "CORS_ORIGINS",
    "CHROME_DEBUG_PORT",
    "STREAM_FPS",
    "SCREENSHOT_DIR",
    "TASK_TIMEOUT_SECONDS",
    "DEFAULT_OUTPUT_DIR",
    "OPENAI_API_KEY",
    "USE_OPENAI",
    "USE_HUGGINGFACE",
]


