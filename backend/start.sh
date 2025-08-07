#!/bin/bash
# 🚀 Production Startup Script for LeadTap Platform
# Handles initialization, health checks, and graceful startup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Configuration
APP_NAME="LeadTap Platform"
APP_VERSION="2.0.0"
WORKERS=${WORKERS:-4}
TIMEOUT=${TIMEOUT:-120}
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
LOG_LEVEL=${LOG_LEVEL:-info}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for database
wait_for_database() {
    log "🔍 Checking database connectivity..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if python -c "
import sys
sys.path.append('.')
from database import test_database_connection
if test_database_connection():
    print('Database connection successful')
    sys.exit(0)
else:
    print('Database connection failed')
    sys.exit(1)
" >/dev/null 2>&1; then
            log_success "Database connection established"
            return 0
        fi
        
        log_warning "Database not ready (attempt $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    log_error "Database connection failed after $max_attempts attempts"
    return 1
}

# Function to wait for Redis
wait_for_redis() {
    if [ "$ENABLE_CACHING" = "true" ] && [ -n "$REDIS_URL" ]; then
        log "🔍 Checking Redis connectivity..."
        
        local max_attempts=10
        local attempt=1
        
        while [ $attempt -le $max_attempts ]; do
            if python -c "
import redis
import os
try:
    r = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))
    r.ping()
    print('Redis connection successful')
    exit(0)
except Exception as e:
    print(f'Redis connection failed: {e}')
    exit(1)
" >/dev/null 2>&1; then
                log_success "Redis connection established"
                return 0
            fi
            
            log_warning "Redis not ready (attempt $attempt/$max_attempts)"
            sleep 2
            attempt=$((attempt + 1))
        done
        
        log_warning "Redis connection failed, continuing without cache"
        return 1
    else
        log "⚠️ Redis disabled or not configured"
        return 0
    fi
}

# Function to initialize database
initialize_database() {
    log "🗄️ Initializing database..."
    
    if python init_db.py; then
        log_success "Database initialized successfully"
    else
        log_error "Database initialization failed"
        return 1
    fi
}

# Function to create admin user
create_admin_user() {
    log "👤 Creating admin user..."
    
    if python create_users.py; then
        log_success "Admin user created successfully"
    else
        log_warning "Admin user creation failed (may already exist)"
    fi
}

# Function to run database migrations
run_migrations() {
    log "🔄 Running database migrations..."
    
    if command_exists alembic; then
        if alembic upgrade head; then
            log_success "Database migrations completed"
        else
            log_warning "Database migrations failed (may not be needed)"
        fi
    else
        log_warning "Alembic not available, skipping migrations"
    fi
}

# Function to check application health
check_health() {
    log "🏥 Checking application health..."
    
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:$PORT/api/health >/dev/null 2>&1; then
            log_success "Application health check passed"
            return 0
        fi
        
        log_warning "Health check failed (attempt $attempt/$max_attempts)"
        sleep 3
        attempt=$((attempt + 1))
    done
    
    log_error "Application health check failed"
    return 1
}

# Function to start the application
start_application() {
    log "🚀 Starting $APP_NAME v$APP_VERSION..."
    
    # Set environment variables
    export PYTHONPATH=/app
    export PYTHONUNBUFFERED=1
    
    # Determine startup command based on environment
    if [ "$ENVIRONMENT" = "production" ]; then
        log "🏭 Starting in production mode with Gunicorn..."
        exec gunicorn main:app \
            --bind $HOST:$PORT \
            --workers $WORKERS \
            --worker-class uvicorn.workers.UvicornWorker \
            --timeout $TIMEOUT \
            --keep-alive 5 \
            --max-requests 1000 \
            --max-requests-jitter 100 \
            --access-logfile - \
            --error-logfile - \
            --log-level $LOG_LEVEL
    else
        log "🔧 Starting in development mode with Uvicorn..."
        exec uvicorn main:app \
            --host $HOST \
            --port $PORT \
            --reload \
            --log-level $LOG_LEVEL
    fi
}

# Function to handle graceful shutdown
graceful_shutdown() {
    log "🛑 Received shutdown signal, stopping gracefully..."
    
    # Stop background processes
    if [ -n "$PID" ]; then
        kill -TERM "$PID" 2>/dev/null || true
        wait "$PID" 2>/dev/null || true
    fi
    
    log_success "Application stopped gracefully"
    exit 0
}

# Set up signal handlers
trap graceful_shutdown SIGTERM SIGINT

# Main startup sequence
main() {
    log "🎯 Starting $APP_NAME initialization..."
    
    # Check Python version
    log "🐍 Checking Python version..."
    python --version
    
    # Check dependencies
    log "📦 Checking dependencies..."
    if ! python -c "import fastapi, uvicorn, sqlalchemy" 2>/dev/null; then
        log_error "Required dependencies not found"
        exit 1
    fi
    log_success "Dependencies check passed"
    
    # Wait for external services
    wait_for_database
    wait_for_redis
    
    # Initialize application
    initialize_database
    run_migrations
    create_admin_user
    
    # Start application
    start_application &
    PID=$!
    
    # Wait for application to start
    sleep 5
    
    # Check health
    if check_health; then
        log_success "$APP_NAME is ready!"
        log "🌐 Application available at http://$HOST:$PORT"
        log "📊 Health check: http://$HOST:$PORT/api/health"
        log "📈 Metrics: http://$HOST:$PORT/metrics"
        
        if [ "$ENVIRONMENT" != "production" ]; then
            log "📚 API Documentation: http://$HOST:$PORT/docs"
        fi
    else
        log_error "Application failed to start properly"
        exit 1
    fi
    
    # Wait for background process
    wait $PID
}

# Run main function
main "$@" 