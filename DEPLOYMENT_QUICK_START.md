# 🚀 Quick Deployment Start

## Fastest Path to Production

### Option 1: Railway (Recommended - 5 minutes)

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push
   ```

2. **Create Railway project**
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub"
   - Select your repository

3. **Add PostgreSQL**
   - Click "+ New" → "Database" → "Add PostgreSQL"
   - Railway auto-creates `DATABASE_URL`

4. **Add Redis**
   - Click "+ New" → "Database" → "Add Redis"
   - Railway auto-creates `REDIS_URL`

5. **Set environment variables**
   - Go to your service → "Variables"
   - Add:
     ```bash
     JWT_SECRET_KEY=<generate-with-python>
     CORS_ORIGINS=https://your-frontend.vercel.app
     ```
   - Generate JWT secret:
     ```bash
     python -c "import secrets; print(secrets.token_urlsafe(32))"
     ```

6. **Deploy frontend to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repo
   - Set root directory: `frontend`
   - Add environment variable:
     ```bash
     NEXT_PUBLIC_API_URL=https://your-backend.railway.app
     ```

7. **Update backend CORS**
   - In Railway, update `CORS_ORIGINS` with your Vercel URL

**Done!** Your app is live. 🎉

---

### Option 2: Render (5 minutes)

1. **Push code to GitHub** (same as above)

2. **Create Render account** at [render.com](https://render.com)

3. **Deploy from render.yaml**
   - Click "New +" → "Blueprint"
   - Connect your GitHub repo
   - Render will detect `render.yaml` automatically
   - Click "Apply"

4. **Set environment variables** in Render dashboard

5. **Deploy frontend** (same as Railway)

**Done!** 🎉

---

### Option 3: Docker Compose (10 minutes)

1. **On your server:**
   ```bash
   git clone <your-repo>
   cd gmap-data-scraper
   cp .env.example .env
   nano .env  # Edit with your values
   ```

2. **Deploy:**
   ```bash
   chmod +x scripts/deploy.sh
   ./scripts/deploy.sh prod
   ```

3. **Set up SSL:**
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```

**Done!** 🎉

---

## Required Environment Variables

### Backend (Railway/Render)

```bash
# Required
DATABASE_URL=<auto-created-by-platform>
REDIS_URL=<auto-created-by-platform>
JWT_SECRET_KEY=<generate-strong-secret>
CORS_ORIGINS=https://your-frontend.vercel.app

# Optional
OPENAI_API_KEY=sk-...
STRIPE_SECRET_KEY=sk_live_...
```

### Frontend (Vercel)

```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

---

## Generate JWT Secret

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Verify Deployment

1. **Backend health:** `https://your-backend.com/api/health`
2. **API docs:** `https://your-backend.com/docs`
3. **Frontend:** `https://your-frontend.vercel.app`

---

## Need Help?

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for detailed instructions.

