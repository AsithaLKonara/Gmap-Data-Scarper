# Quick Start Guide
## Lead Intelligence Platform - Get Started in 5 Minutes

This is a quick guide to get the platform running locally for development.

---

## Prerequisites Check

```bash
# Check Python version (need 3.8+)
python3 --version

# Check Node.js version (need 16+)
node --version

# Check if PostgreSQL is running
pg_isready

# Check if Redis is running (optional)
redis-cli ping
```

---

## Quick Setup

### 1. Clone and Install

```bash
# Clone repository
git clone <your-repo-url>
cd lead-intelligence-platform

# Backend setup
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install
cd ..
```

### 2. Database Setup

```bash
# Create database (if not exists)
createdb lead_intelligence

# Set environment variable
export DATABASE_URL="postgresql://user:password@localhost:5432/lead_intelligence"

# Initialize database
python scripts/init_database.py
```

### 3. Generate VAPID Keys (Optional - for Push Notifications)

```bash
python scripts/generate_vapid_keys.py
```

This creates a `.env` file with VAPID keys.

### 4. Start Services

**Terminal 1 - Backend:**
```bash
python backend/main.py
# Or: uvicorn backend.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Celery Worker (Optional):**
```bash
celery -A backend.celery_app worker --loglevel=info
```

### 5. Access Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## First Steps

1. **Open the frontend** at http://localhost:3000
2. **Enter a search query** (e.g., "ICT students in Toronto")
3. **Select platforms** (Google Maps, LinkedIn, etc.)
4. **Click "Start Scraping"**
5. **Watch results** appear in real-time

---

## Troubleshooting

### Database Connection Error

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U your_user -d lead_intelligence -c "SELECT 1;"
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Module Not Found

```bash
# Reinstall dependencies
pip install -r requirements.txt
cd frontend && npm install
```

---

## Next Steps

- Read [SETUP.md](SETUP.md) for detailed setup
- Read [ARCHITECTURE.md](ARCHITECTURE.md) for system overview
- Read [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment

---

## Need Help?

- Check the [troubleshooting section](SETUP.md#6-troubleshooting)
- Review [API documentation](http://localhost:8000/docs)
- Check application logs


