"""Backend configuration settings."""
import os
from typing import Optional

# API Configuration
API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
API_PORT: int = int(os.getenv("API_PORT", "8000"))
API_RELOAD: bool = os.getenv("API_RELOAD", "true").lower() == "true"

# CORS Configuration
# Add Vercel domains and allow environment-based configuration
_cors_origins_env = os.getenv("CORS_ORIGINS", "")
CORS_ORIGINS: list = (
    _cors_origins_env.split(",") if _cors_origins_env
    else [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        # Add common Vercel preview URLs (will be set via env in production)
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

