# CONSOLIDATED DEPLOYMENT GUIDE
# Google Maps Data Scraper - LeadTap Platform

This guide consolidates all deployment scenarios and configurations for the LeadTap platform.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Deployment Scenarios](#deployment-scenarios)
3. [Environment Configuration](#environment-configuration)
4. [Docker Compose Profiles](#docker-compose-profiles)
5. [Production Deployment](#production-deployment)
6. [Development Setup](#development-setup)
7. [Monitoring & Health Checks](#monitoring--health-checks)
8. [Troubleshooting](#troubleshooting)
9. [Security Considerations](#security-considerations)
10. [Scaling & Performance](#scaling--performance)

---

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git for cloning the repository
- At least 4GB RAM available
- Ports 8000, 3000, 80, 443 available

### Basic Setup
```bash
# Clone the repository
git clone https://github.com/your-repo/gmap-data-scraper.git
cd gmap-data-scraper

# Create environment file
cp .env.example .env

# Start development environment
docker-compose --profile development up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## 🎯 Deployment Scenarios

### 1. Development Environment
**Use Case:** Local development with hot reload
**Services:** Backend, Frontend, SQLite Database
**Profile:** `development`

```bash
docker-compose --profile development up -d
```

**Features:**
- Hot reload for both frontend and backend
- SQLite database for simplicity
- Development debugging enabled
- Volume mounts for live code changes

### 2. Simple Production
**Use Case:** Minimal production deployment
**Services:** Backend, Frontend, SQLite Database
**Profile:** `simple`

```bash
docker-compose --profile simple up -d
```

**Features:**
- Optimized for production
- SQLite database (suitable for small to medium workloads)
- No monitoring overhead
- Fast startup time

### 3. Full Production
**Use Case:** Enterprise-grade production deployment
**Services:** Backend, Frontend, PostgreSQL, Redis, Nginx, Monitoring
**Profile:** `production`

```bash
docker-compose --profile production up -d
```

**Features:**
- PostgreSQL database for scalability
- Redis caching for performance
- Nginx reverse proxy with SSL
- Prometheus monitoring
- Grafana dashboards
- Health checks and auto-restart

### 4. Backend Only
**Use Case:** API-only deployment
**Services:** Backend, SQLite Database
**Profile:** None (manual selection)

```bash
docker-compose up backend sqlite-db -d
```

**Features:**
- Minimal resource usage
- API-only access
- Suitable for microservices architecture

---

## ⚙️ Environment Configuration

### Required Environment Variables

Create a `.env` file in the project root:

```bash
# =============================================================================
# CORE CONFIGURATION
# =============================================================================
ENVIRONMENT=development  # development, production
DEBUG=true              # true, false
DEPLOYMENT_TYPE=development  # development, simple, production

# =============================================================================
# SECURITY
# =============================================================================
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET=your-jwt-secret-key-change-this-in-production

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
# For SQLite (development/simple)
DATABASE_URL=sqlite:///./leadtap.db

# For PostgreSQL (production)
POSTGRES_DB=leadtap
POSTGRES_USER=leadtap
POSTGRES_PASSWORD=your-secure-password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# For MySQL (alternative production)
MYSQL_DATABASE=leadtap
MYSQL_USER=leadtap
MYSQL_PASSWORD=your-secure-password
MYSQL_ROOT_PASSWORD=your-root-password

# =============================================================================
# FRONTEND CONFIGURATION
# =============================================================================
VITE_API_URL=http://localhost:8000
VITE_ENVIRONMENT=development
VITE_APP_NAME=LeadTap
VITE_APP_VERSION=1.0.0

# =============================================================================
# EXTERNAL SERVICES
# =============================================================================
REDIS_URL=redis://redis:6379
SENTRY_DSN=your-sentry-dsn-for-error-tracking

# =============================================================================
# FEATURE FLAGS
# =============================================================================
ENABLE_SSO=false
ENABLE_MONITORING=false
ENABLE_CACHING=false

# =============================================================================
# MONITORING
# =============================================================================
GRAFANA_ADMIN_PASSWORD=admin

# =============================================================================
# PAYMENT INTEGRATION
# =============================================================================
PAYHERE_MERCHANT_ID=your-payhere-merchant-id
PAYHERE_SECRET=your-payhere-secret
PAYHERE_SANDBOX=true  # true for testing, false for production
```

---

## 🐳 Docker Compose Profiles

### Profile: Development
```yaml
# Services included: backend, frontend, sqlite-db
# Features: hot reload, debugging, development tools
docker-compose --profile development up -d
```

### Profile: Simple
```yaml
# Services included: backend, frontend, sqlite-db
# Features: production optimized, minimal overhead
docker-compose --profile simple up -d
```

### Profile: Production
```yaml
# Services included: backend, frontend, postgres-db, redis, nginx, prometheus, grafana
# Features: full production stack with monitoring
docker-compose --profile production up -d
```

### Manual Service Selection
```yaml
# Backend only
docker-compose up backend sqlite-db -d

# Backend + PostgreSQL
docker-compose up backend postgres-db redis -d

# Custom combination
docker-compose up backend frontend postgres-db nginx -d
```

---

## 🚀 Production Deployment

### 1. Pre-deployment Checklist
- [ ] Environment variables configured
- [ ] SSL certificates obtained
- [ ] Domain DNS configured
- [ ] Database backup strategy planned
- [ ] Monitoring alerts configured
- [ ] Security audit completed

### 2. Production Deployment Steps

```bash
# 1. Set production environment
export ENVIRONMENT=production
export DEBUG=false

# 2. Update environment variables
cp .env.example .env.production
# Edit .env.production with production values

# 3. Deploy with production profile
docker-compose --profile production -f docker-compose.yml --env-file .env.production up -d

# 4. Verify deployment
docker-compose ps
docker-compose logs -f
```

### 3. SSL Configuration
```bash
# Create SSL directory
mkdir -p nginx/ssl

# Copy your SSL certificates
cp your-certificate.crt nginx/ssl/
cp your-private-key.key nginx/ssl/

# Update nginx configuration
# Edit nginx/nginx.conf with your domain
```

### 4. Database Migration
```bash
# For PostgreSQL
docker-compose exec backend python -m alembic upgrade head

# For SQLite (automatic)
# Database will be created automatically
```

---

## 🛠️ Development Setup

### Local Development
```bash
# 1. Start development environment
docker-compose --profile development up -d

# 2. View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# 3. Access services
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Development Workflow
```bash
# 1. Make code changes (hot reload enabled)
# 2. View changes immediately in browser
# 3. Check logs for errors
docker-compose logs -f

# 4. Restart services if needed
docker-compose restart backend
docker-compose restart frontend
```

### Debugging
```bash
# Access container shell
docker-compose exec backend bash
docker-compose exec frontend sh

# View real-time logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Check service health
docker-compose ps
```

---

## 📊 Monitoring & Health Checks

### Health Check Endpoints
- **Backend:** `http://localhost:8000/api/health`
- **Frontend:** `http://localhost:3000/`
- **Database:** Automatic health checks
- **Redis:** Automatic health checks

### Monitoring Services (Production)
- **Prometheus:** `http://localhost:9090`
- **Grafana:** `http://localhost:3001` (admin/admin)

### Health Check Commands
```bash
# Check all services
docker-compose ps

# View health check logs
docker-compose logs backend | grep health
docker-compose logs frontend | grep health

# Manual health checks
curl -f http://localhost:8000/api/health
curl -f http://localhost:3000/
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Conflicts
```bash
# Check what's using the ports
lsof -i :8000
lsof -i :3000
lsof -i :80

# Stop conflicting services
sudo systemctl stop apache2  # if using port 80
sudo systemctl stop nginx    # if using port 80
```

#### 2. Database Connection Issues
```bash
# Check database logs
docker-compose logs db
docker-compose logs postgres-db

# Restart database
docker-compose restart db
docker-compose restart postgres-db

# Check database connectivity
docker-compose exec backend python -c "from database import engine; print(engine.connect())"
```

#### 3. Frontend Build Issues
```bash
# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend

# Check build logs
docker-compose logs frontend
```

#### 4. Memory Issues
```bash
# Check resource usage
docker stats

# Increase Docker memory limit
# In Docker Desktop: Settings > Resources > Memory

# Restart with more memory
docker-compose down
docker-compose up -d
```

### Log Analysis
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db

# Follow logs in real-time
docker-compose logs -f

# View logs with timestamps
docker-compose logs -t
```

---

## 🔒 Security Considerations

### Production Security Checklist
- [ ] Change default passwords
- [ ] Use strong SECRET_KEY and JWT_SECRET
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up regular backups
- [ ] Enable monitoring and alerting
- [ ] Use non-root containers
- [ ] Keep images updated

### Security Best Practices
```bash
# 1. Use environment variables for secrets
# Never commit .env files to version control

# 2. Regular security updates
docker-compose pull
docker-compose build --no-cache

# 3. Network security
# Use Docker networks for service isolation

# 4. Volume security
# Use named volumes instead of bind mounts for sensitive data
```

---

## 📈 Scaling & Performance

### Horizontal Scaling
```bash
# Scale backend services
docker-compose up -d --scale backend=3

# Scale with load balancer
# Add nginx load balancer configuration
```

### Performance Optimization
```bash
# 1. Enable Redis caching
export ENABLE_CACHING=true

# 2. Use PostgreSQL for large datasets
export DATABASE_URL=postgresql://user:pass@host:port/db

# 3. Configure nginx caching
# Edit nginx/nginx.conf

# 4. Monitor performance
# Use Prometheus and Grafana
```

### Resource Limits
```yaml
# Add to docker-compose.yml services
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
```

---

## 📚 Additional Resources

### Documentation
- [API Documentation](http://localhost:8000/docs)
- [Swagger UI](http://localhost:8000/redoc)
- [Project README](./README.md)

### Support
- [GitHub Issues](https://github.com/your-repo/issues)
- [Documentation](./docs/)
- [Troubleshooting Guide](./TROUBLESHOOTING.md)

### Community
- [Discord Server](https://discord.gg/your-server)
- [GitHub Discussions](https://github.com/your-repo/discussions)

---

**Last Updated:** $(date)  
**Version:** 1.0.0  
**Status:** Production Ready ✅ 