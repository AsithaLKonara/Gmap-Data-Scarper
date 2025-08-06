# LeadTap - Google Maps Data Scraper - Docker Setup

This project is containerized using Docker and Docker Compose for easy deployment.

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd gmap-data-scraper
   ```

2. **Set up environment variables**:
   ```bash
   # Copy the example environment file
   cp backend/env.example backend/.env
   
   # Edit the environment file with your actual values
   nano backend/.env
   ```

3. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

4. **Access the application**:
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost/docs

## Environment Variables

Edit `backend/.env` with your actual values:

```env
SECRET_KEY=your-secret-key-change-in-production
STRIPE_SECRET_KEY=sk_test_your_stripe_test_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
FRONTEND_URL=http://localhost
DATABASE_URL=sqlite:///./app.db
```

## Docker Commands

### Build and start services:
```bash
docker-compose up --build
```

### Start services in background:
```bash
docker-compose up -d --build
```

### Stop services:
```bash
docker-compose down
```

### View logs:
```bash
docker-compose logs -f
```

### Rebuild a specific service:
```bash
docker-compose up --build backend
```

### Access container shell:
```bash
docker-compose exec backend bash
docker-compose exec frontend sh
```

## Development

For development, the backend code is mounted as a volume, so changes will be reflected immediately. The frontend needs to be rebuilt for changes to take effect.

### Rebuild frontend after changes:
```bash
docker-compose up --build frontend
```

## Production Deployment

For production deployment:

1. Update environment variables with production values
2. Consider using a production database (PostgreSQL, MySQL)
3. Set up proper SSL certificates
4. Configure proper logging and monitoring

## Troubleshooting

### Port conflicts:
If ports 80 or 8000 are already in use, modify the `docker-compose.yml` file to use different ports.

### Database issues:
The SQLite database is persisted in a volume. If you need to reset it:
```bash
docker-compose down
rm backend/app.db
docker-compose up --build
```

### Build issues:
If you encounter build issues, try:
```bash
docker-compose down
docker system prune -f
docker-compose up --build
``` 