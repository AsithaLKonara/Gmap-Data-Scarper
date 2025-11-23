# 🚀 Production Deployment Guide

Complete guide for deploying the Lead Intelligence Platform to production.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Deployment Options](#deployment-options)
3. [Railway Deployment](#railway-deployment)
4. [Render Deployment](#render-deployment)
5. [Docker Compose Deployment](#docker-compose-deployment)
6. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
7. [Environment Variables](#environment-variables)
8. [Post-Deployment Checklist](#post-deployment-checklist)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

- **Docker** (v20.10+) and **Docker Compose** (v2.0+)
- **Git** for version control
- **Node.js** (v18+) for frontend builds
- **Python** (v3.11+) for local development

### Required Accounts

- **Railway** or **Render** account (for backend)
- **Vercel** account (for frontend)
- **PostgreSQL** database (provided by Railway/Render or external)
- **Redis** instance (provided by Railway/Render or external)

---

## Deployment Options

### Option 1: Railway (Recommended - Free Tier Available)

✅ **Pros:**
- Free tier with $5 credit/month
- Easy PostgreSQL and Redis setup
- Automatic HTTPS
- Simple deployment from Git

❌ **Cons:**
- Limited free tier resources
- May require upgrade for production traffic

### Option 2: Render

✅ **Pros:**
- Free tier available
- Good PostgreSQL support
- Automatic SSL
- Docker support

❌ **Cons:**
- Free tier spins down after inactivity
- Limited resources on free tier

### Option 3: Docker Compose (Self-Hosted)

✅ **Pros:**
- Full control
- No vendor lock-in
- Can run on any VPS/cloud

❌ **Cons:**
- Requires server management
- Manual SSL setup
- More complex setup

---

## Railway Deployment

### Step 1: Prepare Your Repository

1. Ensure all files are committed to Git
2. Push to GitHub/GitLab/Bitbucket

### Step 2: Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository

### Step 3: Add PostgreSQL Database

1. In Railway dashboard, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway will automatically create a `DATABASE_URL` environment variable

### Step 4: Add Redis

1. Click **"+ New"**
2. Select **"Database"** → **"Add Redis"**
3. Railway will automatically create a `REDIS_URL` environment variable

### Step 5: Configure Backend Service

1. Railway should auto-detect the `Dockerfile`
2. If not, go to **Settings** → **Source** and set:
   - **Root Directory**: `/` (root)
   - **Dockerfile Path**: `Dockerfile`

### Step 6: Set Environment Variables

In Railway dashboard, go to your service → **Variables** and add:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=$PORT  # Railway sets this automatically
API_RELOAD=false

# CORS - Set your frontend URL
CORS_ORIGINS=https://your-frontend.vercel.app

# JWT Authentication
JWT_SECRET_KEY=<generate-strong-secret>
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# Task Management
TASK_TIMEOUT_SECONDS=3600

# Chrome Configuration
CHROME_DEBUG_PORT=9222
STREAM_FPS=2
SCREENSHOT_DIR=/app/screenshots

# Output Directory
OUTPUT_DIR=/app/data

# AI Configuration (Optional)
OPENAI_API_KEY=sk-...
USE_HUGGINGFACE=true

# Stripe (Optional)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID_MONTHLY=price_...
STRIPE_PRICE_ID_USAGE_BASED=price_...
```

**Generate JWT Secret:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 7: Deploy

1. Railway will automatically deploy on push
2. Or click **"Deploy"** in the dashboard
3. Wait for deployment to complete
4. Check logs for any errors

### Step 8: Get Your Backend URL

1. Go to your service → **Settings**
2. Click **"Generate Domain"** or use custom domain
3. Copy the URL (e.g., `https://your-app.railway.app`)

---

## Render Deployment

### Step 1: Prepare Repository

Same as Railway - ensure code is in Git.

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub

### Step 3: Create New Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your repository
3. Render will detect `render.yaml` automatically

### Step 4: Manual Configuration (if not using render.yaml)

If you prefer manual setup:

1. **Name**: `lead-intelligence-api`
2. **Environment**: `Docker`
3. **Dockerfile Path**: `./Dockerfile`
4. **Docker Context**: `.`
5. **Start Command**: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### Step 5: Add PostgreSQL Database

1. Click **"New +"** → **"PostgreSQL"**
2. Name: `lead-intelligence-db`
3. Plan: `Starter` (free tier available)
4. Render will create `DATABASE_URL` automatically

### Step 6: Add Redis

1. Click **"New +"** → **"Redis"**
2. Name: `lead-intelligence-redis`
3. Plan: `Starter` (free tier available)
4. Render will create `REDIS_URL` automatically

### Step 7: Set Environment Variables

In your web service → **Environment**, add all variables from [Environment Variables](#environment-variables) section.

### Step 8: Deploy

1. Render will auto-deploy on push
2. Or click **"Manual Deploy"**
3. Monitor logs for errors

---

## Docker Compose Deployment

### Step 1: Prepare Server

**Requirements:**
- Ubuntu 20.04+ or similar Linux distribution
- Docker and Docker Compose installed
- Domain name pointing to server IP
- Ports 80, 443, 8000 open

**Install Docker:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**Install Docker Compose:**
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Step 2: Clone Repository

```bash
git clone <your-repo-url>
cd gmap-data-scraper
```

### Step 3: Configure Environment

```bash
cp .env.example .env
nano .env  # Edit with your values
```

**Important variables:**
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `JWT_SECRET_KEY`: Strong random secret
- `CORS_ORIGINS`: Your frontend URL

### Step 4: Deploy

**Using deployment script:**
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh prod
```

**Or manually:**
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### Step 5: Set Up SSL (Let's Encrypt)

**Install Certbot:**
```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx
```

**Get SSL Certificate:**
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

**Update nginx.conf:**
Uncomment HTTPS server block and update SSL paths.

### Step 6: Configure Nginx

1. Copy SSL certificates to `nginx/ssl/`
2. Update `nginx/nginx.conf` with your domain
3. Restart nginx:
```bash
docker-compose -f docker-compose.prod.yml restart nginx
```

---

## Frontend Deployment (Vercel)

### Step 1: Prepare Frontend

1. Ensure `frontend/package.json` exists
2. Check `vercel.json` is configured
3. Commit all changes

### Step 2: Connect to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click **"Add New Project"**
3. Import your GitHub repository
4. Vercel will auto-detect Next.js

### Step 3: Configure Build Settings

**Root Directory:** `frontend`

**Build Command:** `npm run build` (auto-detected)

**Output Directory:** `.next` (auto-detected)

### Step 4: Set Environment Variables

In Vercel dashboard → **Settings** → **Environment Variables**:

```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

**Important:** 
- Use `NEXT_PUBLIC_` prefix for client-side variables
- Set for all environments (Production, Preview, Development)

### Step 5: Deploy

1. Click **"Deploy"**
2. Vercel will build and deploy automatically
3. Get your frontend URL (e.g., `https://your-app.vercel.app`)

### Step 6: Update Backend CORS

Update backend `CORS_ORIGINS` to include your Vercel URL:

```bash
CORS_ORIGINS=https://your-app.vercel.app,https://your-custom-domain.com
```

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `REDIS_URL` | Redis connection string | `redis://host:6379/0` |
| `JWT_SECRET_KEY` | Secret for JWT tokens | Generate with Python secrets |
| `CORS_ORIGINS` | Allowed frontend origins | `https://yourdomain.com` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for AI features | None |
| `STRIPE_SECRET_KEY` | Stripe secret key | None |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret | None |
| `TASK_TIMEOUT_SECONDS` | Task timeout in seconds | `3600` |
| `STREAM_FPS` | Browser stream FPS | `2` |

### Generate JWT Secret

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Post-Deployment Checklist

### Backend

- [ ] Backend is accessible at `/api/health`
- [ ] API docs accessible at `/docs`
- [ ] Database migrations ran successfully
- [ ] Redis connection working
- [ ] CORS configured correctly
- [ ] JWT authentication working
- [ ] Environment variables set correctly

### Frontend

- [ ] Frontend loads without errors
- [ ] API connection working (check browser console)
- [ ] Authentication flow works
- [ ] Scraping tasks can be created
- [ ] Data export works

### Security

- [ ] HTTPS enabled (SSL certificates valid)
- [ ] Strong JWT secret set
- [ ] Database credentials secure
- [ ] CORS restricted to frontend domain
- [ ] Rate limiting enabled
- [ ] Security headers configured

### Monitoring

- [ ] Health checks configured
- [ ] Logs accessible
- [ ] Error tracking set up (optional)
- [ ] Uptime monitoring (optional)

---

## Troubleshooting

### Backend Won't Start

**Check logs:**
```bash
# Railway/Render: Check dashboard logs
# Docker: docker-compose logs backend
```

**Common issues:**
- Database connection failed → Check `DATABASE_URL`
- Redis connection failed → Check `REDIS_URL`
- Port conflict → Check `API_PORT`
- Missing environment variables → Verify all required vars are set

### Frontend Can't Connect to Backend

**Check:**
1. Backend URL is correct in `NEXT_PUBLIC_API_URL`
2. CORS is configured with frontend URL
3. Backend is accessible (test `/api/health`)
4. No firewall blocking requests

### Database Migration Errors

**Run migrations manually:**
```bash
docker-compose exec backend python -m backend.scripts.create_migrations
```

### Chrome/Scraping Issues

**Check:**
- Chrome is installed in Docker image
- Shared memory (`shm_size`) is sufficient (2GB+)
- No resource limits too restrictive

### High Memory Usage

**Solutions:**
- Reduce `STREAM_FPS` (lower = less memory)
- Limit concurrent tasks
- Increase server resources
- Use Chrome headless mode

---

## Quick Reference

### Railway Commands

```bash
# View logs
railway logs

# Open shell
railway shell

# View variables
railway variables
```

### Docker Commands

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart service
docker-compose -f docker-compose.prod.yml restart backend

# View status
docker-compose -f docker-compose.prod.yml ps

# Stop all
docker-compose -f docker-compose.prod.yml down

# Update and restart
docker-compose -f docker-compose.prod.yml up -d --build
```

### Health Check URLs

- Backend Health: `https://your-backend.com/api/health`
- API Docs: `https://your-backend.com/docs`
- Metrics: `https://your-backend.com/api/metrics`

---

## Support

For issues or questions:
1. Check logs first
2. Review this guide
3. Check GitHub issues
4. Contact support

---

**Last Updated:** 2025-01-17

