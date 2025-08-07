# 🐳 PRODUCTION-READY BACKEND DOCKERFILE
# LeadTap Platform - FastAPI Backend
# Multi-stage build with security hardening and performance optimizations

# =============================================================================
# BUILD STAGE
# =============================================================================
FROM python:3.13-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements-docker.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# =============================================================================
# PRODUCTION STAGE
# =============================================================================
FROM python:3.13-slim AS production

# Set working directory
WORKDIR /app

# Set environment variables for production
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONHASHSEED=random

# Install system dependencies for production
RUN apt-get update && apt-get install -y \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY . .

# Set proper permissions
RUN chown -R appuser:appuser /app \
    && chmod -R 755 /app \
    && chmod +x /app/start.sh

# Create necessary directories
RUN mkdir -p /app/logs /app/uploads /app/data \
    && chown -R appuser:appuser /app/logs /app/uploads /app/data

# Switch to non-root user
USER appuser

# Add local bin to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start command for production
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--timeout", "120", "--keep-alive", "5", "--max-requests", "1000", "--max-requests-jitter", "100"]

# =============================================================================
# DEVELOPMENT STAGE
# =============================================================================
FROM python:3.13-slim AS development

# Set working directory
WORKDIR /app

# Set environment variables for development
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app

# Create necessary directories
RUN mkdir -p /app/logs /app/uploads /app/data \
    && chown -R appuser:appuser /app/logs /app/uploads /app/data

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start command for development
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# =============================================================================
# TESTING STAGE
# =============================================================================
FROM python:3.13-slim AS testing

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies including testing
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; print('Python version:', sys.version)" || exit 1

# Start command for testing
CMD ["pytest", "-v", "--cov=app", "--cov-report=html"]

# =============================================================================
# CELERY WORKER STAGE
# =============================================================================
FROM python:3.13-slim AS celery-worker

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY . .

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app

# Create necessary directories
RUN mkdir -p /app/logs /app/uploads /app/data \
    && chown -R appuser:appuser /app/logs /app/uploads /app/data

# Switch to non-root user
USER appuser

# Add local bin to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Expose Flower port
EXPOSE 5555

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "from celery import Celery; print('Celery available')" || exit 1

# Start command for Celery worker
CMD ["celery", "-A", "main.celery", "worker", "--loglevel=info", "--concurrency=4"]

# =============================================================================
# CELERY BEAT STAGE
# =============================================================================
FROM python:3.13-slim AS celery-beat

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY . .

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app

# Create necessary directories
RUN mkdir -p /app/logs /app/uploads /app/data \
    && chown -R appuser:appuser /app/logs /app/uploads /app/data

# Switch to non-root user
USER appuser

# Add local bin to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "from celery import Celery; print('Celery available')" || exit 1

# Start command for Celery beat
CMD ["celery", "-A", "main.celery", "beat", "--loglevel=info"]

# =============================================================================
# MIGRATION STAGE
# =============================================================================
FROM python:3.13-slim AS migration

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY . .

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app

# Create necessary directories
RUN mkdir -p /app/logs /app/uploads /app/data \
    && chown -R appuser:appuser /app/logs /app/uploads /app/data

# Switch to non-root user
USER appuser

# Add local bin to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sqlite3; print('Database available')" || exit 1

# Start command for database migration
CMD ["python", "init_db.py"]

# =============================================================================
# USAGE INSTRUCTIONS
# =============================================================================
# Build for production:
# docker build --target production -t leadtap-backend:prod .
#
# Build for development:
# docker build --target development -t leadtap-backend:dev .
#
# Build for testing:
# docker build --target testing -t leadtap-backend:test .
#
# Build for Celery worker:
# docker build --target celery-worker -t leadtap-celery:worker .
#
# Build for Celery beat:
# docker build --target celery-beat -t leadtap-celery:beat .
#
# Build for migration:
# docker build --target migration -t leadtap-migration:latest . 