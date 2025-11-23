# Quick Start Guide

## 🚀 Start the Application

### Easiest Way (Both Backend + Frontend)
```powershell
.\start_all.ps1
```

This opens two windows:
1. Backend server (http://localhost:8000)
2. Frontend app (http://localhost:3000)

### Manual Start

**Terminal 1 - Backend:**
```powershell
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

## 📱 Using the Application

1. **Open Browser**: Navigate to http://localhost:3000

2. **Enter Search Query**: 
   - Example: "ICT students in Toronto"
   - Example: "Computer Science students"
   - Example: "Restaurants in New York"

3. **Select Platforms**:
   - Check Google Maps (always recommended)
   - Check other platforms as needed

4. **Configure Filters** (Optional):
   - **Field of Study**: e.g., "ICT", "Computer Science"
   - **Students Only**: Check if you only want students
   - Other filters available in the UI

5. **Start Scraping**: Click "Start Scraping" button

6. **Watch Results**:
   - Left panel: See results table with phone numbers
   - Right panel: Live browser view (shows what Chrome is doing)
   - Bottom: Real-time logs

7. **Export Data**: Results are automatically saved to CSV files

## 📊 Where Data is Saved

- **Location**: `C:\Users\asith\Documents\social_leads\`
- **Files**:
  - `all_platforms.csv` - All results combined
  - `google_maps.csv` - Google Maps results only
  - `facebook.csv` - Facebook results only
  - (etc. for each platform)

## 🎯 Key Features

### Phone Extraction
- Automatically extracts phone numbers from:
  - Tel: links (highest confidence)
  - Visible text on page
  - JSON-LD structured data
  - Website contact pages
  - OCR from images (if Tesseract installed)

### Individual Lead Classification
- Detects if lead is:
  - **Individual** (student, professional)
  - **Business** (company, organization)
- Extracts:
  - Field of study
  - Degree program
  - Institution name
  - Graduation year

### Real-Time Monitoring
- Live browser view (see what Chrome is doing)
- Real-time logs
- Progress updates
- Results streaming

## 🔧 Troubleshooting

### Backend won't start
- Check if port 8000 is already in use
- Try: `netstat -ano | findstr :8000`
- Kill process or change port in `backend/config.py`

### Frontend won't start
- Check if port 3000 is already in use
- Make sure you're in the `frontend` directory
- Try: `npm install` again

### Chrome errors
- Ensure Chrome browser is installed
- Chrome driver is auto-downloaded by webdriver-manager

### No phone numbers found
- Phone extraction works but may not find numbers if:
  - Numbers are in images (need Tesseract OCR)
  - Numbers are behind login/paywall
  - Page structure changed

## 📚 API Documentation

When backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎓 Example Use Cases

### Find ICT Students
1. Query: "ICT students"
2. Field of Study: "ICT"
3. Students Only: ✓
4. Platform: Google Maps

### Find Restaurants with Phone Numbers
1. Query: "Restaurants in [City]"
2. Platform: Google Maps
3. Phone extraction happens automatically

### Find Professionals by Field
1. Query: "Software engineers"
2. Field of Study: "Computer Science"
3. Students Only: ✗ (unchecked)
4. Platform: LinkedIn, Google Maps

## 💡 Tips

- Start with Google Maps (most reliable)
- Use specific queries for better results
- Field of study filter works best with student-focused queries
- Phone extraction is automatic - no configuration needed
- Results save incrementally - safe to stop anytime

