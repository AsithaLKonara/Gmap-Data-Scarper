
# LeadTap Deployment Configuration

## Frontend (Vercel)
- **Framework**: Vite
- **Root Directory**: `frontend/`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Environment Variables**:
  - `VITE_API_URL`: [Your Backend URL]

## Backend (Railway)
- **Stack**: Python (FastAPI)
- **Root Directory**: `.`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- **Nixpacks Configuration**:
  - Includes `google-chrome-stable` and `chromedriver` for the X-Ray discovery engine.
- **Persistent Storage**:
  - Mount a volume at `/app/data` and update the SQLite path to `/app/data/leadtap.db`.
