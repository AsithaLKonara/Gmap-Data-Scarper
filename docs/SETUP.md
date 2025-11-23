# Setup Guide
## Lead Intelligence Platform - Complete Setup Instructions

This guide will help you set up the Lead Intelligence Platform from scratch.

---

## Prerequisites

- Python 3.8+ installed
- Node.js 16+ and npm/yarn installed
- PostgreSQL 12+ installed and running
- Redis installed and running (for Celery)
- Chrome/Chromium browser installed

---

## 1. Backend Setup

### 1.1 Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 1.2 Database Configuration

1. Create a PostgreSQL database:
```bash
createdb lead_intelligence
```

2. Set environment variable:
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/lead_intelligence"
```

Or create a `.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/lead_intelligence
```

### 1.3 Initialize Database

```bash
# Run database initialization script
python scripts/init_database.py
```

This will create all required tables:
- `leads` - Lead data storage
- `tasks` - Task tracking
- `push_subscriptions` - Push notification subscriptions

### 1.4 Configure VAPID Keys (for Push Notifications)

```bash
# Generate VAPID keys
python scripts/generate_vapid_keys.py
```

This will:
- Generate VAPID private and public keys
- Save them to `.env` file
- Set up `NEXT_PUBLIC_VAPID_PUBLIC_KEY` for frontend

**Note**: The `.env` file will be created automatically. Make sure to add it to `.gitignore`.

### 1.5 Start Backend Server

```bash
# Development mode
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Or use the main.py directly
python backend/main.py
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

---

## 2. Frontend Setup

### 2.1 Install Dependencies

```bash
cd frontend
npm install
# or
yarn install
```

### 2.2 Environment Configuration

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_VAPID_PUBLIC_KEY=your_vapid_public_key_base64_here
```

The VAPID public key should be set automatically if you ran `scripts/generate_vapid_keys.py`.

### 2.3 Start Frontend Development Server

```bash
cd frontend
npm run dev
# or
yarn dev
```

The frontend will be available at `http://localhost:3000`

---

## 3. Celery & Redis Setup (Optional - for Background Tasks)

### 3.1 Start Redis

```bash
# On macOS with Homebrew
brew services start redis

# On Linux
sudo systemctl start redis

# Or run directly
redis-server
```

### 3.2 Start Celery Worker

```bash
# In a separate terminal
celery -A backend.celery_app worker --loglevel=info
```

### 3.3 Start Celery Beat (for Scheduled Tasks)

```bash
# In another terminal
celery -A backend.celery_app beat --loglevel=info
```

---

## 4. Environment Variables Reference

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/lead_intelligence

# VAPID Keys (for Push Notifications)
VAPID_PRIVATE_KEY=your_private_key_here
VAPID_PUBLIC_KEY=your_public_key_here
VAPID_EMAIL=admin@leadintelligence.com

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Optional: External Services
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
OPENAI_API_KEY=your_openai_key
CLEARBIT_API_KEY=your_clearbit_key
GOOGLE_PLACES_API_KEY=your_google_places_key
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_VAPID_PUBLIC_KEY=your_vapid_public_key_base64_here
```

---

## 5. Verification

### 5.1 Check Backend Health

```bash
curl http://localhost:8000/api/health
```

Should return:
```json
{"status": "healthy", "version": "3.1.0"}
```

### 5.2 Check Database Connection

```bash
# Check if tables exist
python -c "from backend.models.database import get_engine; from sqlalchemy import inspect; print(inspect(get_engine()).get_table_names())"
```

Should show: `['leads', 'tasks', 'push_subscriptions']`

### 5.3 Test Push Notifications

1. Open the frontend at `http://localhost:3000`
2. Navigate to the Push Notifications section
3. Click "Subscribe to Notifications"
4. Grant notification permission
5. Start a scraping task and wait for completion
6. You should receive a push notification

---

## 6. Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running: `pg_isready`
- Check database credentials in `DATABASE_URL`
- Ensure database exists: `psql -l | grep lead_intelligence`

### Push Notifications Not Working

- Verify VAPID keys are set: `echo $VAPID_PRIVATE_KEY`
- Check browser console for errors
- Ensure service worker is registered (check Application tab in DevTools)
- Verify `NEXT_PUBLIC_VAPID_PUBLIC_KEY` is set in frontend

### Frontend Can't Connect to Backend

- Check `NEXT_PUBLIC_API_URL` is correct
- Verify backend is running on the specified port
- Check CORS settings in `backend/config.py`

### Import Errors

- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python path: `python -c "import sys; print(sys.path)"`
- Verify virtual environment is activated

---

## 7. Production Deployment

See `docs/DEPLOYMENT.md` for production deployment instructions.

---

## 8. Next Steps

- Review `docs/ARCHITECTURE.md` for system architecture
- Check `docs/API.md` for API documentation
- Read `docs/DEVELOPER_GUIDE.md` for development guidelines

---

## Support

For issues or questions:
- Check the troubleshooting section above
- Review existing GitHub issues
- Create a new issue with detailed error logs


