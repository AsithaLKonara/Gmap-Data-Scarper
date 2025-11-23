# Architecture Documentation
## Lead Intelligence Platform - System Architecture

This document describes the architecture and design of the Lead Intelligence Platform.

---

## System Overview

The Lead Intelligence Platform is a full-stack web application for scraping and managing lead data from various social media platforms. It consists of:

- **Backend**: FastAPI-based REST API with WebSocket support
- **Frontend**: Next.js React application with PWA capabilities
- **Database**: PostgreSQL for persistent storage
- **Task Queue**: Celery with Redis for background processing
- **Browser Automation**: Selenium/Playwright for web scraping

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   React UI   │  │  WebSocket   │  │  Service     │     │
│  │  Components  │  │   Client     │  │  Worker      │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/WebSocket
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   REST API   │  │  WebSocket   │  │  Task        │     │
│  │   Routes     │  │   Handler    │  │  Manager     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Enrichment  │  │  Push        │  │  Orchestrator│     │
│  │  Services    │  │  Service     │  │  Core        │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼──────┐  ┌─────────▼─────────┐  ┌─────▼──────┐
│  PostgreSQL  │  │      Redis       │  │  Chrome    │
│  Database    │  │   (Celery Queue)  │  │  Instances │
└──────────────┘  └───────────────────┘  └────────────┘
```

---

## Component Details

### 1. Frontend Layer

**Technology Stack:**
- Next.js 13+ (React framework)
- TypeScript
- Tailwind CSS
- WebSocket client

**Key Components:**
- `LeftPanel.tsx`: Scraper controls and configuration
- `RightPanel.tsx`: Results display with virtualization
- `TaskList.tsx`: Task management UI
- `PushNotificationService.tsx`: Push notification management
- `PWAInstallPrompt.tsx`: PWA installation prompt

**Features:**
- Real-time updates via WebSocket
- Virtual scrolling for large result sets
- PWA support (offline, installable)
- Push notifications
- Glassmorphism UI theme

---

### 2. Backend Layer

**Technology Stack:**
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- WebSockets (real-time communication)
- Celery (task queue)

**Key Modules:**

#### 2.1 API Routes (`backend/routes/`)
- `scraper.py`: Scraping control endpoints
- `tasks.py`: Task management endpoints
- `export.py`: Data export endpoints
- `analytics.py`: Analytics endpoints
- `enrichment.py`: Enrichment endpoints
- `notifications.py`: Push notification endpoints
- `archival.py`: Data archival endpoints

#### 2.2 Services (`backend/services/`)
- `orchestrator_service.py`: Task orchestration and WebSocket management
- `postgresql_storage.py`: Database storage operations
- `push_service.py`: Web Push notification service
- `enrichment_service.py`: Lead enrichment (Clearbit, Google Places)
- `phone_verifier.py`: Phone verification (Twilio)
- `duplicate_detection.py`: Duplicate lead detection
- `chrome_pool.py`: Chrome instance pooling
- `archival.py`: Data archival service

#### 2.3 Models (`backend/models/`)
- `database.py`: SQLAlchemy models (Lead, Task)
- `push_subscription.py`: Push subscription model
- `schemas.py`: Pydantic schemas for API validation

---

### 3. Scraping Engine

**Core Components:**
- `orchestrator_core.py`: Main scraping orchestration logic
- Platform-specific scrapers (Google Maps, LinkedIn, etc.)
- Anti-detection system
- Chrome pool management

**Features:**
- Multi-platform scraping
- Pause/resume functionality
- Progress tracking
- Error handling and recovery
- Rate limiting

---

### 4. Data Layer

**PostgreSQL Database:**
- `leads`: Lead data storage
- `tasks`: Task tracking
- `push_subscriptions`: Push notification subscriptions

**Indexes:**
- Optimized for common queries (task_id, platform, extracted_at)
- Composite indexes for filtering

**Archival:**
- Old leads archived to JSON files
- Monthly partitions
- Restore capability

---

### 5. Task Queue (Celery)

**Queues:**
- `default`: General tasks
- `archival`: Data archival tasks
- `enrichment`: Lead enrichment tasks

**Scheduled Tasks:**
- Daily archival of old leads
- Hourly archival statistics update

---

## Data Flow

### Scraping Workflow

1. **User initiates scraping** via frontend
2. **Backend creates task** in TaskManager
3. **Orchestrator starts** scraping in background thread
4. **Results streamed** via WebSocket to frontend
5. **Each result processed**:
   - Duplicate detection
   - Phone verification
   - Business enrichment
   - Saved to PostgreSQL
6. **Task completion** triggers push notification

### Push Notification Flow

1. **User subscribes** via frontend
2. **Subscription saved** to database
3. **Task events trigger** notifications:
   - Task completion
   - Task errors
   - Task paused/resumed
4. **Push service sends** notification via Web Push API
5. **Service worker** displays notification

---

## Security

### Authentication & Authorization
- JWT-based authentication (optional)
- User-specific task isolation
- API key support

### Rate Limiting
- Per-user rate limits
- Per-endpoint rate limits
- IP-based throttling

### Input Validation
- Pydantic schema validation
- SQL injection prevention (SQLAlchemy)
- XSS prevention (input sanitization)

### Security Headers
- CORS configuration
- Security headers middleware
- HTTPS enforcement (production)

---

## Performance Optimizations

### Frontend
- Code splitting
- Lazy loading
- Virtual scrolling
- WebSocket batching
- Service worker caching

### Backend
- Database connection pooling
- Query optimization (indexes)
- Chrome instance pooling
- Async operations
- Caching strategies

### Database
- Optimized indexes
- Connection pooling
- Query optimization service
- Data archival

---

## Scalability

### Horizontal Scaling
- Stateless API design
- Database connection pooling
- Redis for shared state
- Load balancer ready

### Vertical Scaling
- Chrome pool management
- Resource limits
- Memory optimization

---

## Monitoring

### Metrics (Prometheus)
- Request rates
- Error rates
- Task completion times
- Database query performance
- Chrome instance usage

### Logging
- Structured JSON logging
- Request context propagation
- Error tracking
- Performance logging

---

## Deployment

### Development
- Local PostgreSQL
- Local Redis
- Hot reload enabled

### Production
- Systemd services
- Nginx reverse proxy
- SSL/TLS certificates
- Database backups
- Monitoring dashboards

---

## Future Enhancements

- Horizontal scaling with Kubernetes
- Multi-region deployment
- Advanced caching (Redis)
- GraphQL API
- Real-time collaboration
- Advanced analytics

---

## Technology Choices

### Why FastAPI?
- High performance
- Automatic API documentation
- Type validation
- WebSocket support
- Async/await support

### Why Next.js?
- Server-side rendering
- Static site generation
- API routes
- Optimized builds
- PWA support

### Why PostgreSQL?
- ACID compliance
- Advanced features
- JSON support
- Excellent performance
- Mature ecosystem

### Why Celery?
- Distributed task queue
- Scheduled tasks
- Retry mechanisms
- Task prioritization
- Monitoring support

---

## Dependencies

See `requirements.txt` for Python dependencies and `frontend/package.json` for Node.js dependencies.

---

## Contributing

See `docs/DEVELOPER_GUIDE.md` for development guidelines.


