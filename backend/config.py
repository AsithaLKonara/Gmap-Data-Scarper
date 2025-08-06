import os

# Security Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
JWT_SECRET = os.getenv('JWT_SECRET', SECRET_KEY)
ALGORITHM = 'HS256'

# JWT Token Configuration - More Secure
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', 60))  # 1 hour
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRE_DAYS', 7))  # 7 days

# Payment Configuration
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', 'sk_test_...')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', 'whsec_...')

# Application URLs
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./leadtap.db')

# Rate Limiting Configuration
RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', 100))
RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', 60))

# Environment Configuration
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Cache Configuration
CACHE_TIMEOUT_SECONDS = 60  # Default cache timeout for stats endpoints 