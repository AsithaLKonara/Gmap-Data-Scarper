# 🐳 LeadTap Docker Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- At least 2GB of available RAM
- Ports 3000 and 8000 available

### 1. Build and Run (Recommended)
```bash
# Make the build script executable
chmod +x build-docker.sh

# Build and run the entire application
./build-docker.sh
```

### 2. Manual Build and Run
```bash
# Build the images
docker-compose build

# Start the services
docker-compose up -d

# Check status
docker-compose ps
```

## 📊 Service Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   SQLite DB     │
│   (Nginx)       │◄──►│   (FastAPI)     │◄──►│   (Alpine)      │
│   Port: 3000    │    │   Port: 8000    │    │   Volume Mount  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env or docker-compose.yml)
```bash
DATABASE_URL=sqlite:///app/leadtap.db
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=false
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

#### Frontend (docker-compose.yml)
```bash
NODE_ENV=production
VITE_API_URL=http://localhost:8000
```

## 📁 File Structure

```
gmap-data-scraper/
├── docker-compose.yml          # Main Docker Compose file
├── docker-compose.prod.yml     # Production configuration
├── build-docker.sh            # Build script
├── backend/
│   ├── Dockerfile             # Backend container
│   ├── requirements-docker.txt # Python dependencies
│   └── leadtap.db            # SQLite database
└── frontend/
    ├── Dockerfile             # Frontend container
    ├── nginx.conf            # Nginx configuration
    └── .dockerignore         # Docker ignore file
```

## 🛠️ Development vs Production

### Development
```bash
# Use development configuration
docker-compose -f docker-compose.yml up -d

# With hot reload
docker-compose up
```

### Production
```bash
# Use production configuration
docker-compose -f docker-compose.prod.yml up -d

# Or use the build script
./build-docker.sh
```

## 🔍 Monitoring and Logs

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Health Checks
```bash
# Check service health
docker-compose ps

# Test endpoints
curl http://localhost:8000/docs  # Backend API
curl http://localhost:3000       # Frontend
```

## 🚀 Deployment Options

### 1. Local Development
```bash
./build-docker.sh
```

### 2. Production Server
```bash
# Set production environment variables
export SECRET_KEY="your-production-secret-key"
export NODE_ENV="production"

# Build and run
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Cloud Deployment (AWS, GCP, Azure)
```bash
# Build images
docker-compose build

# Push to registry (example with AWS ECR)
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-west-2.amazonaws.com
docker tag leadtap-backend:latest 123456789012.dkr.ecr.us-west-2.amazonaws.com/leadtap-backend:latest
docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/leadtap-backend:latest
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the ports
lsof -i :3000
lsof -i :8000

# Kill processes or change ports in docker-compose.yml
```

#### 2. Database Issues
```bash
# Reset database
docker-compose down
rm backend/leadtap.db
docker-compose up -d
```

#### 3. Build Failures
```bash
# Clean build
docker-compose down
docker system prune -f
docker-compose build --no-cache
```

#### 4. Frontend Not Loading
```bash
# Check nginx logs
docker-compose logs frontend

# Check if API is accessible
curl http://localhost:8000/docs
```

### Performance Optimization

#### 1. Resource Limits
Add to docker-compose.yml:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

#### 2. Caching
```bash
# Use Docker layer caching
docker-compose build --parallel
```

## 📊 Monitoring

### Health Checks
- Backend: `http://localhost:8000/docs`
- Frontend: `http://localhost:3000`

### Metrics
```bash
# Container stats
docker stats

# Resource usage
docker-compose top
```

## 🔒 Security

### Production Checklist
- [ ] Change default SECRET_KEY
- [ ] Use HTTPS in production
- [ ] Configure proper CORS origins
- [ ] Set up firewall rules
- [ ] Use non-root users in containers
- [ ] Regular security updates

### SSL/HTTPS Setup
```bash
# Add SSL certificates
# Update nginx.conf for HTTPS
# Use reverse proxy (Traefik, Nginx Proxy Manager)
```

## 🚀 Scaling

### Horizontal Scaling
```bash
# Scale backend services
docker-compose up -d --scale backend=3
```

### Load Balancer
```bash
# Add nginx load balancer
# Configure multiple backend instances
```

## 📝 Maintenance

### Regular Tasks
```bash
# Update images
docker-compose pull
docker-compose up -d

# Clean up
docker system prune -f

# Backup database
docker cp leadtap-backend:/app/leadtap.db ./backup/leadtap-$(date +%Y%m%d).db
```

## 🆘 Support

### Useful Commands
```bash
# Enter container
docker-compose exec backend bash
docker-compose exec frontend sh

# View real-time logs
docker-compose logs -f --tail=100

# Restart services
docker-compose restart backend
docker-compose restart frontend
```

### Getting Help
- Check logs: `docker-compose logs`
- Verify configuration: `docker-compose config`
- Test connectivity: `docker-compose exec backend curl localhost:8000/docs`

---

## 🎉 Success!

Your LeadTap application is now running with Docker!

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

Happy coding! 🚀 