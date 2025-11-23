# Lead Intelligence Platform - Web UI Setup

## Overview

This is the v3.0 web-based interface for the Lead Intelligence Platform, featuring:
- FastAPI backend with WebSocket support
- Next.js frontend with real-time updates
- Live browser streaming
- Comprehensive phone extraction
- Individual lead classification (students, professionals)

## Prerequisites

- Python 3.8+
- Node.js 18+
- Chrome browser installed
- Tesseract OCR (optional, for OCR phone extraction)

## Installation

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Tesseract OCR (optional):
- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
- macOS: `brew install tesseract`
- Linux: `sudo apt-get install tesseract-ocr`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Running the Application

### Start Backend

```bash
python -m backend.main
```

Or using uvicorn directly:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

### Start Frontend

```bash
cd frontend
npm run dev
```

Frontend will be available at: http://localhost:3000

## Usage

1. Open http://localhost:3000 in your browser
2. Enter search queries (e.g., "ICT students in Toronto")
3. Select platforms to scrape
4. Configure filters (field of study, student only, etc.)
5. Click "Start Scraping"
6. Watch live browser view and results in real-time

## Features

### Phone Extraction ✅
- Multi-layer extraction: DOM, tel: links, JSON-LD, website crawling, OCR
- Phone normalization to E.164 format
- Confidence scoring
- Provenance tracking
- **Phone Highlighting UI**: Visual feedback in live browser view
- **Phone Details Modal**: Click to view source, screenshot, and details
- **Obfuscation Parsing**: Handles word-to-number, [dot] replacements

### Individual Lead Classification ✅
- Detects students vs professionals
- Extracts field of study
- Extracts degree program
- Extracts graduation year

### Real-Time Updates ✅
- WebSocket-based log streaming
- Progress updates
- Result streaming
- Live browser view (MJPEG stream with optimized JPEG frames)

### Legal & Compliance ✅
- Data retention policy (6 months, configurable)
- Consent notice on first load
- Opt-out mechanism (API + UI)

### Performance Features ✅
- URL caching (prevents re-scraping)
- Smart rate limiting (dynamic delay adjustment)
- Cross-platform deduplication (by phone and URL)

### AI Insights ✅
- Hugging Face API integration (free tier)
- Optional OpenAI integration (requires API key)
- Intent detection and sentiment analysis
- Automated lead summaries

### Export Enhancement ✅
- Task-specific export
- Date range export
- Platform-specific export
- Export progress indicator

## API Endpoints

- `POST /api/scraper/start` - Start scraping task
- `POST /api/scraper/stop/{task_id}` - Stop task
- `GET /api/scraper/status/{task_id}` - Get task status
- `GET /live_feed/{task_id}` - MJPEG stream
- `WebSocket /api/scraper/ws/logs/{task_id}` - Log stream
- `WebSocket /api/scraper/ws/progress/{task_id}` - Progress stream
- `WebSocket /api/scraper/ws/results/{task_id}` - Results stream

## Configuration

Backend configuration is in `backend/config.py`. Environment variables:
- `API_HOST` - API host (default: 0.0.0.0)
- `API_PORT` - API port (default: 8000)
- `CHROME_DEBUG_PORT` - Chrome remote debugging port (default: 9222)
- `STREAM_FPS` - Screenshot stream FPS (default: 2)

## Troubleshooting

### Chrome not starting
- Ensure Chrome is installed
- Check Chrome driver is up to date (webdriver-manager handles this)

### OCR not working
- Install Tesseract OCR
- Set TESSDATA_PREFIX environment variable if needed

### WebSocket connection issues
- Check CORS settings in `backend/main.py`
- Ensure backend is running on port 8000

## Development

### Backend Development
```bash
uvicorn backend.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm run dev
```

## Production Deployment

See `docker-compose.yml` (to be created) for containerized deployment.

