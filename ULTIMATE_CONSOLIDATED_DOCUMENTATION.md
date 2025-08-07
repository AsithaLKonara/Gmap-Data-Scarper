# 🏺️ ULTIMATE CONSOLIDATED DOCUMENTATION
# Google Maps Data Scraper - LeadTap Platform
# Complete Documentation & Deployment Guide

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Quick Start](#quick-start)
5. [Installation & Setup](#installation--setup)
6. [Docker Deployment](#docker-deployment)
7. [Local Development](#local-development)
8. [API Documentation](#api-documentation)
9. [Database Schema](#database-schema)
10. [Security](#security)
11. [Monitoring & Analytics](#monitoring--analytics)
12. [Troubleshooting](#troubleshooting)
13. [Production Deployment](#production-deployment)
14. [Development Roadmap](#development-roadmap)
15. [Contributing](#contributing)

---

## 🎯 Project Overview

The Google Maps Data Scraper (LeadTap Platform) is a comprehensive SaaS solution for lead generation and management. It combines web scraping capabilities with advanced CRM features, analytics, and automation tools.

### Core Components

- **Web Scraper**: Automated Google Maps data extraction
- **Lead Management**: CRM with scoring and categorization
- **Analytics Dashboard**: Real-time insights and reporting
- **WhatsApp Automation**: Bulk messaging and workflow automation
- **Multi-tenant Architecture**: SaaS-ready with tenant isolation
- **API-First Design**: RESTful and GraphQL APIs

### Technology Stack

**Backend:**
- Python 3.13 with FastAPI
- SQLAlchemy ORM
- JWT Authentication
- Redis Caching
- Celery for background tasks

**Frontend:**
- React 18 with TypeScript
- Vite build system
- Tailwind CSS
- Chakra UI components
- React Router for navigation

**Infrastructure:**
- Docker & Docker Compose
- Nginx reverse proxy
- PostgreSQL (production) / SQLite (development)
- Redis for caching and sessions

---

## ✨ Features

### 🔍 Core Scraping Features
- Automated Google Maps searches
- Multi-query batch processing
- Data extraction: Business name, category, address, phone, website
- CSV export functionality
- Retry mechanism for failed attempts
- Cross-platform compatibility

### 🏢 LeadTap Platform Features
- **Multi-tenant SaaS architecture**
- **JWT Authentication & SSO integration**
- **Advanced lead scoring algorithms**
- **Real-time analytics dashboard**
- **Bulk WhatsApp messaging**
- **AI-powered lead categorization**
- **Custom workflow automation**
- **API-first design with GraphQL support**
- **Role-based access control**
- **Audit logging and compliance**

### 📊 Analytics & Reporting
- Real-time lead analytics
- Conversion tracking
- Performance metrics
- Custom report generation
- Data visualization
- Export capabilities

### 🤖 Automation Features
- Automated lead scoring
- Workflow automation
- Bulk messaging campaigns
- Email automation
- Task scheduling
- Integration webhooks

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Database      │
│   (React/TS)    │◄──►│   (FastAPI)     │◄──►│   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │    │   Redis Cache   │    │   File Storage  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Architecture

**Frontend Layer:**
- React components with TypeScript
- State management with React hooks
- Responsive design with Tailwind CSS
- Real-time updates via WebSocket

**API Layer:**
- FastAPI with automatic OpenAPI docs
- JWT authentication middleware
- Rate limiting and security headers
- GraphQL endpoint for complex queries

**Data Layer:**
- SQLAlchemy ORM with migrations
- Multi-tenant data isolation
- Redis for caching and sessions
- File storage for uploads

**Infrastructure Layer:**
- Docker containerization
- Nginx reverse proxy with SSL
- Monitoring with Prometheus/Grafana
- CI/CD pipeline support

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-repo/gmap-data-scraper.git
cd gmap-data-scraper

# Start development environment
docker-compose -f CONSOLIDATED_DOCKER_COMPOSE.yml --profile development up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
python main.py

# Frontend setup (in another terminal)
cd frontend
npm install
npm run dev
```

---

## 📦 Installation & Setup

### Prerequisites

- Python 3.8+ (3.13 recommended)
- Node.js 18+ and npm
- Docker and Docker Compose
- Git

### Environment Variables

Create a `.env` file in the root directory:

```bash
# Core Configuration
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# Database Configuration
DATABASE_URL=sqlite:///./leadtap.db
POSTGRES_DB=leadtap
POSTGRES_USER=leadtap
POSTGRES_PASSWORD=leadtap
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Frontend Configuration
FRONTEND_URL=http://localhost:3000

# External Services
SENTRY_DSN=your-sentry-dsn
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Feature Flags
ENABLE_SSO=false
ENABLE_MONITORING=false
ENABLE_CACHING=false
```

### Database Setup

```bash
# Initialize database
cd backend
python init_db.py

# Run migrations (if using Alembic)
alembic upgrade head
```

---

## 🐳 Docker Deployment

### Development Environment

```bash
# Start with hot reload
docker-compose -f CONSOLIDATED_DOCKER_COMPOSE.yml --profile development up -d

# View logs
docker-compose -f CONSOLIDATED_DOCKER_COMPOSE.yml logs -f
```

### Simple Production

```bash
# Minimal production setup
docker-compose -f CONSOLIDATED_DOCKER_COMPOSE.yml --profile simple up -d
```

### Full Production

```bash
# Complete production stack
docker-compose -f CONSOLIDATED_DOCKER_COMPOSE.yml --profile production up -d
```

### Backend Only

```bash
# API-only deployment
docker-compose -f CONSOLIDATED_DOCKER_COMPOSE.yml --profile backend-only up -d
```

### Docker Configuration Files

The project includes several Docker configurations:

- **CONSOLIDATED_DOCKER_COMPOSE.yml**: Complete multi-profile configuration
- **CONSOLIDATED_DOCKERFILE**: Multi-stage Dockerfile for all scenarios
- **backend/Dockerfile**: Backend-specific Dockerfile
- **frontend/Dockerfile**: Frontend-specific Dockerfile

### Docker Profiles

1. **development**: Full stack with hot reload
2. **simple**: Minimal production (backend + frontend + SQLite)
3. **production**: Full production with PostgreSQL, Redis, monitoring
4. **backend-only**: Backend API only

---

## 💻 Local Development

### Backend Development

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Run linting
flake8 .
black .
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Run linting
npm run lint
```

### Database Management

```bash
# Initialize database
python backend/init_db.py

# Create admin user
python backend/create_users.py

# Run migrations
alembic upgrade head
```

---

## 📚 API Documentation

### Authentication

All API endpoints require JWT authentication except for public routes.

```bash
# Login to get token
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "password"}'

# Use token in subsequent requests
curl -X GET "http://localhost:8000/api/leads" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Core Endpoints

#### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/refresh` - Refresh JWT token
- `POST /api/auth/logout` - User logout

#### Leads Management
- `GET /api/leads` - List leads
- `POST /api/leads` - Create lead
- `GET /api/leads/{id}` - Get lead details
- `PUT /api/leads/{id}` - Update lead
- `DELETE /api/leads/{id}` - Delete lead

#### Analytics
- `GET /api/analytics/overview` - Dashboard overview
- `GET /api/analytics/leads` - Lead analytics
- `GET /api/analytics/conversions` - Conversion metrics

#### WhatsApp Automation
- `POST /api/whatsapp/send` - Send bulk messages
- `GET /api/whatsapp/campaigns` - List campaigns
- `POST /api/whatsapp/campaigns` - Create campaign

### GraphQL API

The application also provides a GraphQL endpoint at `/api/graphql` for complex queries.

---

## 🗄️ Database Schema

### Core Tables

#### Users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    first_name VARCHAR,
    last_name VARCHAR,
    role VARCHAR DEFAULT 'user',
    tenant_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Leads
```sql
CREATE TABLE leads (
    id INTEGER PRIMARY KEY,
    business_name VARCHAR NOT NULL,
    category VARCHAR,
    address TEXT,
    phone VARCHAR,
    website VARCHAR,
    plus_code VARCHAR,
    score INTEGER DEFAULT 0,
    status VARCHAR DEFAULT 'new',
    tenant_id INTEGER,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Tenants
```sql
CREATE TABLE tenants (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    domain VARCHAR UNIQUE,
    settings JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Relationships

- Users belong to Tenants (multi-tenant architecture)
- Leads belong to Tenants and Users
- All data is isolated by tenant_id

---

## 🔐 Security

### Authentication & Authorization

- JWT-based authentication
- Role-based access control (RBAC)
- Multi-tenant data isolation
- SSO integration support
- Session management with Redis

### Data Protection

- Password hashing with bcrypt
- HTTPS enforcement in production
- CORS configuration
- Rate limiting on API endpoints
- Input validation and sanitization

### Security Headers

```python
# Security middleware configuration
SECURITY_HEADERS = {
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
}
```

---

## 📊 Monitoring & Analytics

### Application Monitoring

- Health check endpoints
- Performance metrics collection
- Error tracking with Sentry
- Log aggregation

### Analytics Features

- Real-time dashboard
- Lead conversion tracking
- User activity analytics
- Campaign performance metrics
- Custom report generation

### Monitoring Stack

```yaml
# Prometheus configuration
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

# Grafana configuration
grafana:
  image: grafana/grafana
  ports:
    - "3001:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
```

---

## 🔧 Troubleshooting

### Common Issues

#### Backend Issues

1. **Database Connection Error**
   ```bash
   # Check database status
   docker-compose ps
   
   # Restart database
   docker-compose restart db
   ```

2. **Port Already in Use**
   ```bash
   # Check port usage
   lsof -i :8000
   
   # Kill process
   kill -9 <PID>
   ```

3. **Import Errors**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt --force-reinstall
   ```

#### Frontend Issues

1. **Build Errors**
   ```bash
   # Clear cache
   npm run clean
   
   # Reinstall dependencies
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Hot Reload Not Working**
   ```bash
   # Restart development server
   npm run dev
   ```

### Logs and Debugging

```bash
# View application logs
docker-compose logs -f backend

# View frontend logs
docker-compose logs -f frontend

# Access container shell
docker-compose exec backend bash
```

---

## 🚀 Production Deployment

### Environment Setup

1. **Set Production Environment Variables**
   ```bash
   ENVIRONMENT=production
   DEBUG=false
   SECRET_KEY=<strong-secret-key>
   DATABASE_URL=postgresql://user:pass@host:port/db
   ```

2. **SSL Configuration**
   ```bash
   # Generate SSL certificates
   certbot certonly --standalone -d yourdomain.com
   ```

3. **Database Migration**
   ```bash
   # Run migrations
   alembic upgrade head
   ```

### Deployment Checklist

- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates installed
- [ ] Monitoring configured
- [ ] Backup strategy implemented
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Error tracking configured

### Performance Optimization

1. **Database Optimization**
   - Index creation
   - Query optimization
   - Connection pooling

2. **Caching Strategy**
   - Redis caching
   - CDN configuration
   - Static file optimization

3. **Load Balancing**
   - Nginx configuration
   - Horizontal scaling
   - Health checks

---

## 🗺️ Development Roadmap

### Phase 1: Core Features ✅
- [x] Basic scraping functionality
- [x] Lead management system
- [x] User authentication
- [x] Multi-tenant architecture

### Phase 2: Advanced Features 🚧
- [x] Analytics dashboard
- [x] WhatsApp automation
- [x] Lead scoring
- [x] API documentation

### Phase 3: Enterprise Features 📋
- [ ] Advanced reporting
- [ ] Custom workflows
- [ ] Third-party integrations
- [ ] Mobile application

### Phase 4: AI & ML 📋
- [ ] AI-powered lead scoring
- [ ] Predictive analytics
- [ ] Natural language processing
- [ ] Automated categorization

---

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Standards

- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Write comprehensive tests
- Document all new features
- Update documentation as needed

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

---

## 📞 Support

### Documentation
- [Complete Documentation](./ALL_DOCUMENTATION.md)
- [API Documentation](http://localhost:8000/docs)
- [GraphQL Playground](http://localhost:8000/graphql)

### Community
- GitHub Issues: [Report bugs and feature requests](https://github.com/your-repo/gmap-data-scraper/issues)
- Discussions: [Community forum](https://github.com/your-repo/gmap-data-scraper/discussions)

### Contact
- Email: support@leadtap.com
- Documentation: [docs.leadtap.com](https://docs.leadtap.com)

---

*This documentation was last updated on $(date)*
*Version: 2.0.0* 