# Deployment Guide

This guide covers deploying the Lead Intelligence Platform to production.

## Architecture

- **Frontend**: Next.js 14 deployed on Vercel
- **Backend**: FastAPI deployed on Railway/Render/AWS (requires Chrome/Selenium)
- **Database**: SQLite (local) or PostgreSQL (production)

## Prerequisites

- Vercel account
- Railway/Render account (or AWS account)
- Domain name (optional)

## Frontend Deployment (Vercel)

### 1. Prepare Frontend

```bash
cd frontend
npm install
npm run build
```

### 2. Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel
```

Or use the Vercel dashboard:
1. Import your GitHub repository
2. Set root directory to `frontend`
3. Configure build settings:
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Install Command: `npm install`

### 3. Configure Environment Variables

In Vercel dashboard, set:
- `NEXT_PUBLIC_API_URL`: Your backend API URL (e.g., `https://your-backend.railway.app`)

## Backend Deployment

### Option 1: Railway

1. Create a new Railway project
2. Connect your GitHub repository
3. Set root directory to project root
4. Railway will auto-detect the Dockerfile
5. Configure environment variables (see `.env.example`)
6. Deploy

### Option 2: Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Use Docker deployment
4. Set build command: `docker build -t lead-intelligence .`
5. Set start command: `docker run -p 8000:8000 lead-intelligence`
6. Configure environment variables

### Option 3: AWS (EC2/ECS)

1. Build Docker image:
```bash
docker build -t lead-intelligence .
```

2. Push to ECR or deploy to ECS
3. Configure security groups for port 8000
4. Set environment variables

## Environment Variables

### Backend

```bash
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://your-vercel-app.vercel.app
CHROME_DEBUG_PORT=9222
STREAM_FPS=2
TASK_TIMEOUT_SECONDS=3600
OUTPUT_DIR=/app/data
OPENAI_API_KEY=your_key_here  # Optional
USE_HUGGINGFACE=true
```

### Frontend

```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

## Docker Deployment

### Local Testing

```bash
docker-compose up
```

### Production

```bash
docker build -t lead-intelligence .
docker run -d \
  -p 8000:8000 \
  -e CORS_ORIGINS=https://your-app.vercel.app \
  -v $(pwd)/data:/app/data \
  lead-intelligence
```

## Troubleshooting

### Chrome/Chromium Issues

- Ensure Chrome is installed in the container
- Check shared memory: `--shm-size=2gb`
- Verify ChromeDriver version matches Chrome version

### CORS Errors

- Add your Vercel domain to `CORS_ORIGINS`
- Check that backend allows credentials

### WebSocket Connection Issues

- Verify WebSocket URL uses `wss://` in production
- Check firewall rules allow WebSocket connections

## Production Checklist

- [ ] Backend deployed and accessible
- [ ] Frontend deployed to Vercel
- [ ] Environment variables configured
- [ ] CORS origins set correctly
- [ ] Health endpoint responding (`/health`)
- [ ] Metrics endpoint working (`/metrics`)
- [ ] WebSocket connections working
- [ ] Chrome instances starting correctly
- [ ] Data persistence configured
- [ ] Monitoring/logging set up

## Monitoring

- Check `/health` endpoint regularly
- Monitor `/metrics` for system stats
- Set up alerts for error rates
- Monitor Chrome instance count
- Track memory usage

## Scaling

For high traffic:
- Use Redis for task queue
- Deploy multiple backend instances
- Use load balancer
- Consider PostgreSQL for data storage
- Implement rate limiting per user

