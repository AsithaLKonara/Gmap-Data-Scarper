import os
from typing import List, Optional
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    """Production-ready configuration settings"""
    
    # Environment Configuration
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'development')
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    
    # Security Configuration
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET: str = os.getenv('JWT_SECRET', SECRET_KEY)
    ALGORITHM: str = 'HS256'
    
    # JWT Token Configuration
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', 60))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRE_DAYS', 7))
    
    # Database Configuration
    DATABASE_URL: str = os.getenv(
        'DATABASE_URL', 
        'sqlite:////app/data/leadtap.db' if os.getenv('ENVIRONMENT') == 'production' else 'sqlite:///./leadtap.db'
    )
    POSTGRES_DB: str = os.getenv('POSTGRES_DB', 'leadtap')
    POSTGRES_USER: str = os.getenv('POSTGRES_USER', 'leadtap')
    POSTGRES_PASSWORD: str = os.getenv('POSTGRES_PASSWORD', 'leadtap')
    POSTGRES_HOST: str = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT: int = int(os.getenv('POSTGRES_PORT', '5432'))
    
    # Redis Configuration
    REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379')
    REDIS_PASSWORD: Optional[str] = os.getenv('REDIS_PASSWORD')
    
    # Application URLs
    FRONTEND_URL: str = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    BACKEND_URL: str = os.getenv('BACKEND_URL', 'http://localhost:8000')
    
    # Rate Limiting Configuration
    RATE_LIMIT_REQUESTS: int = int(os.getenv('RATE_LIMIT_REQUESTS', 100))
    RATE_LIMIT_WINDOW: int = int(os.getenv('RATE_LIMIT_WINDOW', 60))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = os.getenv('LOG_FORMAT', 'json')
    
    # Cache Configuration
    CACHE_TIMEOUT_SECONDS: int = int(os.getenv('CACHE_TIMEOUT_SECONDS', 60))
    
    # Payment Configuration
    STRIPE_SECRET_KEY: str = os.getenv('STRIPE_SECRET_KEY', 'sk_test_...')
    STRIPE_WEBHOOK_SECRET: str = os.getenv('STRIPE_WEBHOOK_SECRET', 'whsec_...')
    
    # External Services
    SENTRY_DSN: Optional[str] = os.getenv('SENTRY_DSN')
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv('GOOGLE_CLIENT_SECRET')
    
    # Feature Flags
    ENABLE_SSO: bool = os.getenv('ENABLE_SSO', 'false').lower() == 'true'
    ENABLE_MONITORING: bool = os.getenv('ENABLE_MONITORING', 'false').lower() == 'true'
    ENABLE_CACHING: bool = os.getenv('ENABLE_CACHING', 'false').lower() == 'true'
    ENABLE_2FA: bool = os.getenv('ENABLE_2FA', 'true').lower() == 'true'
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = [
        FRONTEND_URL,
        "http://localhost:3000",
        "https://leadtap.com",
        "https://www.leadtap.com"
    ]
    
    # Security Headers
    SECURITY_HEADERS: dict = {
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    }
    
    # Performance Configuration
    WORKERS_PER_CORE: int = int(os.getenv('WORKERS_PER_CORE', '1'))
    MAX_WORKERS: int = int(os.getenv('MAX_WORKERS', '4'))
    WORKER_TIMEOUT: int = int(os.getenv('WORKER_TIMEOUT', '120'))
    
    # Monitoring Configuration
    PROMETHEUS_ENABLED: bool = os.getenv('PROMETHEUS_ENABLED', 'true').lower() == 'true'
    HEALTH_CHECK_INTERVAL: int = int(os.getenv('HEALTH_CHECK_INTERVAL', '30'))
    
    # Backup Configuration
    BACKUP_ENABLED: bool = os.getenv('BACKUP_ENABLED', 'false').lower() == 'true'
    BACKUP_RETENTION_DAYS: int = int(os.getenv('BACKUP_RETENTION_DAYS', '30'))
    
    # Email Configuration
    SMTP_HOST: Optional[str] = os.getenv('SMTP_HOST')
    SMTP_PORT: int = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USER: Optional[str] = os.getenv('SMTP_USER')
    SMTP_PASSWORD: Optional[str] = os.getenv('SMTP_PASSWORD')
    SMTP_TLS: bool = os.getenv('SMTP_TLS', 'true').lower() == 'true'
    
    # WhatsApp Configuration
    WHATSAPP_API_KEY: Optional[str] = os.getenv('WHATSAPP_API_KEY')
    WHATSAPP_PHONE_ID: Optional[str] = os.getenv('WHATSAPP_PHONE_ID')
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = int(os.getenv('MAX_FILE_SIZE', '10485760'))  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'csv', 'xlsx']
    UPLOAD_DIR: str = os.getenv('UPLOAD_DIR', './uploads')
    
    @validator('SECRET_KEY')
    def validate_secret_key(cls, v):
        if v == 'dev-secret-key-change-in-production' and os.getenv('ENVIRONMENT') == 'production':
            raise ValueError('SECRET_KEY must be changed in production')
        return v
    
    @validator('JWT_SECRET')
    def validate_jwt_secret(cls, v):
        if v == 'dev-jwt-secret-change-in-production' and os.getenv('ENVIRONMENT') == 'production':
            raise ValueError('JWT_SECRET must be changed in production')
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Export individual settings for backward compatibility
SECRET_KEY = settings.SECRET_KEY
JWT_SECRET = settings.JWT_SECRET
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
DATABASE_URL = settings.DATABASE_URL
POSTGRES_DB = settings.POSTGRES_DB
POSTGRES_USER = settings.POSTGRES_USER
POSTGRES_PASSWORD = settings.POSTGRES_PASSWORD
POSTGRES_HOST = settings.POSTGRES_HOST
POSTGRES_PORT = settings.POSTGRES_PORT
REDIS_URL = settings.REDIS_URL
FRONTEND_URL = settings.FRONTEND_URL
BACKEND_URL = settings.BACKEND_URL
RATE_LIMIT_REQUESTS = settings.RATE_LIMIT_REQUESTS
RATE_LIMIT_WINDOW = settings.RATE_LIMIT_WINDOW
ENVIRONMENT = settings.ENVIRONMENT
DEBUG = settings.DEBUG
LOG_LEVEL = settings.LOG_LEVEL
CACHE_TIMEOUT_SECONDS = settings.CACHE_TIMEOUT_SECONDS
STRIPE_SECRET_KEY = settings.STRIPE_SECRET_KEY
STRIPE_WEBHOOK_SECRET = settings.STRIPE_WEBHOOK_SECRET
ALLOWED_ORIGINS = settings.ALLOWED_ORIGINS
SECURITY_HEADERS = settings.SECURITY_HEADERS 