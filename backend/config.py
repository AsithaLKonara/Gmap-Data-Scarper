import os

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', 'sk_test_...')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', 'whsec_...')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

# Use SQLite for development, MySQL for production
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./leadtap.db')

# Simple in-memory cache for backend endpoints
from functools import lru_cache

CACHE_TIMEOUT_SECONDS = 60  # Default cache timeout for stats endpoints 