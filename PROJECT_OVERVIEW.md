# Lead Intelligence Platform - Complete Project Overview

**Version**: 3.9  
**Status**: Production Ready  
**Last Updated**: 2025-01-13

---

## Table of Contents

1. [What is Lead Intelligence Platform?](#what-is-lead-intelligence-platform)
2. [Architecture Overview](#architecture-overview)
3. [How It Works](#how-it-works)
4. [Key Components](#key-components)
5. [Technology Stack](#technology-stack)
6. [Data Flow](#data-flow)
7. [User Journey](#user-journey)
8. [Technical Deep Dive](#technical-deep-dive)
9. [Deployment Architecture](#deployment-architecture)

---

## What is Lead Intelligence Platform?

The **Lead Intelligence Platform** is an enterprise-grade web application for automated lead generation and data extraction from multiple social media and business platforms. It combines browser automation, AI-powered enrichment, and real-time analytics to help businesses discover and qualify leads at scale.

### Core Capabilities

1. **Multi-Platform Scraping**: Extract leads from Google Maps, LinkedIn, Twitter/X, Facebook, Instagram, and more
2. **Phone Extraction**: Advanced multi-layer phone number extraction with OCR and verification
3. **Real-Time Monitoring**: Live browser view with WebSocket streaming
4. **Data Enrichment**: AI-powered business intelligence and phone verification
5. **Analytics Dashboard**: Comprehensive insights and reporting
6. **Enterprise Scale**: Optimized for 100K+ records with performance tuning

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Dashboard│  │ Scraper  │  │ Analytics│  │  Tasks   │    │
│  │   UI     │  │   UI     │  │   UI     │  │   UI     │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
                          │
                    WebSocket │ HTTP/REST
                          │
┌─────────────────────────────────────────────────────────────┐
│              Backend API (FastAPI)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Scraper    │  │  Analytics   │  │  Enrichment  │     │
│  │   Service    │  │   Service    │  │   Service    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Chrome Pool  │  │  PostgreSQL  │  │  Data        │     │
│  │  Manager     │  │    Cache     │  │  Archival    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                          │
                    Selenium │ HTTP
                          │
┌─────────────────────────────────────────────────────────────┐
│              Browser Automation Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Chrome     │  │   Chrome     │  │   Chrome     │     │
│  │  Instance 1  │  │  Instance 2  │  │  Instance N  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                          │
                    HTTP Requests
                          │
┌─────────────────────────────────────────────────────────────┐
│              External Platforms                              │
│  Google Maps │ LinkedIn │ Twitter │ Facebook │ Instagram    │
└─────────────────────────────────────────────────────────────┘
```

### Component Layers

1. **Presentation Layer** (Frontend)
   - Next.js React application
   - Real-time UI updates via WebSocket
   - Interactive charts and visualizations

2. **Application Layer** (Backend API)
   - FastAPI REST API
   - WebSocket servers
   - Business logic and orchestration

3. **Service Layer** (Backend Services)
   - Scraping services
   - Enrichment services
   - Analytics services
   - Caching services

4. **Data Layer**
   - PostgreSQL (cache and metadata)
   - CSV files (lead data)
   - Archive storage (cold data)

5. **Infrastructure Layer**
   - Chrome instances (Selenium)
   - Docker containers
   - CI/CD pipelines

---

## How It Works

### End-to-End Workflow

```
1. USER INPUT
   ↓
   User enters search queries (e.g., "ICT students in Toronto")
   Selects platforms (Google Maps, LinkedIn, etc.)
   Configures filters (field of study, location, etc.)
   ↓
2. TASK CREATION
   ↓
   Frontend sends POST /api/scraper/start
   Backend creates task with unique ID
   Allocates Chrome instance from pool
   Starts background scraping thread
   ↓
3. BROWSER AUTOMATION
   ↓
   Chrome navigates to platform
   Performs search with query
   Scrolls through results
   Extracts business/lead information
   ↓
4. PHONE EXTRACTION
   ↓
   Multi-layer extraction:
   - DOM tel: links
   - Visible text patterns
   - JSON-LD structured data
   - Website crawling
   - OCR from screenshots
   ↓
5. DATA PROCESSING
   ↓
   Normalize phone numbers (E.164 format)
   Calculate confidence scores
   Extract coordinates for highlighting
   Classify leads (student vs business)
   ↓
6. REAL-TIME UPDATES
   ↓
   WebSocket streams:
   - Live browser screenshots (MJPEG)
   - Extracted results
   - Progress updates
   - Log messages
   ↓
7. DATA ENRICHMENT (Optional)
   ↓
   Phone verification (Twilio)
   Business enrichment (Clearbit, Google Places)
   AI-powered descriptions
   Quality assessment
   ↓
8. DATA STORAGE
   ↓
   Save to CSV files
   Update PostgreSQL cache
   Store in user-specific directories
   ↓
9. ANALYTICS & EXPORT
   ↓
   Real-time analytics dashboard
   Multi-format export (CSV, JSON, Excel)
   Archive old records
```

### Detailed Process Flow

#### 1. Task Initialization

```python
# User starts scraping task
POST /api/scraper/start
{
  "queries": ["ICT students in Toronto"],
  "platforms": ["google_maps", "linkedin"],
  "max_results": 100,
  "filters": {
    "field_of_study": "Information Technology",
    "student_only": true
  }
}

# Backend creates task
task_id = generate_unique_id()
chrome_instance = chrome_pool.acquire(task_id)
task_manager.create_task(request, user_id)
start_background_scraper(task_id)
```

#### 2. Browser Automation

```python
# For each platform
for platform in platforms:
    scraper = get_scraper(platform)
    
    # Navigate and search
    driver.get(platform_search_url)
    search_box.send_keys(query)
    search_button.click()
    
    # Extract results
    results = []
    while len(results) < max_results:
        # Scroll to load more
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        wait_for_new_results()
        
        # Extract current page results
        page_results = extract_results(driver)
        results.extend(page_results)
        
        # Check for next page
        if not has_next_page():
            break
```

#### 3. Phone Extraction Process

```python
# Multi-layer phone extraction
def extract_phones(driver, url):
    phones = []
    
    # Layer 1: tel: links (highest confidence)
    tel_links = driver.find_elements(By.CSS_SELECTOR, "a[href^='tel:']")
    for link in tel_links:
        phone = link.get_attribute("href").replace("tel:", "")
        phones.append({
            "raw_phone": phone,
            "source": "tel_link",
            "confidence": 95
        })
    
    # Layer 2: Visible text patterns
    page_text = driver.find_element(By.TAG_NAME, "body").text
    phone_patterns = re.findall(PHONE_REGEX, page_text)
    for pattern in phone_patterns:
        phones.append({
            "raw_phone": pattern,
            "source": "visible_text",
            "confidence": 70
        })
    
    # Layer 3: JSON-LD structured data
    json_ld = extract_json_ld(driver)
    phones.extend(extract_from_json_ld(json_ld))
    
    # Layer 4: Website crawling
    website_url = extract_website(driver)
    if website_url:
        website_phones = crawl_website(website_url)
        phones.extend(website_phones)
    
    # Layer 5: OCR (if enabled)
    if enable_ocr:
        screenshot = driver.get_screenshot_as_png()
        ocr_phones = extract_from_image(screenshot)
        phones.extend(ocr_phones)
    
    # Normalize and deduplicate
    normalized_phones = []
    seen = set()
    for phone in phones:
        normalized = normalize_phone(phone["raw_phone"])
        if normalized and normalized not in seen:
            seen.add(normalized)
            normalized_phones.append({
                **phone,
                "normalized_e164": normalized
            })
    
    return normalized_phones
```

#### 4. Real-Time Streaming

```python
# WebSocket connection for live updates
@router.websocket("/ws/logs/{task_id}")
async def websocket_logs(websocket: WebSocket, task_id: str):
    await websocket.accept()
    
    # Stream logs
    async for log_message in log_stream(task_id):
        await websocket.send_json({
            "type": "log",
            "message": log_message,
            "timestamp": datetime.now().isoformat()
        })

# MJPEG stream for live browser view
@router.get("/live_feed/{task_id}")
async def live_feed(task_id: str):
    driver = stream_service.get_driver(task_id)
    
    async def generate_frames():
        while True:
            # Capture screenshot
            screenshot = driver.get_screenshot_as_png()
            
            # Compress image
            compressed = resource_optimizer.optimize_screenshot(screenshot)
            
            # Send as MJPEG frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + 
                   compressed + b'\r\n')
            
            await asyncio.sleep(0.5)  # 2 FPS
    
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
```

#### 5. Data Enrichment Pipeline

```python
# Enrichment workflow
async def enrich_lead(lead_data):
    results = {
        "phone_verification": None,
        "business_enrichment": None,
        "ai_enhancement": None
    }
    
    # Phone verification
    if lead_data.get("phone"):
        verifier = get_phone_verifier()
        results["phone_verification"] = verifier.verify(lead_data["phone"])
    
    # Business enrichment
    enrichment_service = get_enrichment_service()
    results["business_enrichment"] = enrichment_service.enrich_business(
        business_name=lead_data["name"],
        website=lead_data.get("website"),
        location=lead_data.get("location")
    )
    
    # AI enhancement
    ai_service = get_ai_enhancement_service()
    results["ai_enhancement"] = {
        "description": ai_service.generate_business_description(...),
        "quality_score": ai_service.assess_lead_quality(...),
        "insights": ai_service.extract_key_insights(...)
    }
    
    return results
```

---

## Key Components

### Frontend Components

#### 1. **Dashboard** (`frontend/pages/dashboard.tsx`)
- Summary statistics cards
- Interactive charts (Recharts)
- Period selectors (daily/weekly/monthly)
- Real-time data refresh

#### 2. **Scraper Interface** (`frontend/pages/index.tsx`)
- **Left Panel**: Query input, platform selection, filters
- **Center Panel**: Live browser stream with phone highlighting
- **Right Panel**: Results table with real-time updates

#### 3. **Task Management** (`frontend/components/TaskList.tsx`)
- List of all user tasks
- Status badges (running, paused, completed, error)
- Progress indicators
- Task controls (stop/pause/resume)

#### 4. **Phone Overlay** (`frontend/components/PhoneOverlay.tsx`)
- Visual highlighting on live browser stream
- Coordinate-based positioning
- Confidence-based color coding
- Click to view details

### Backend Services

#### 1. **Orchestrator Service** (`backend/services/orchestrator_service.py`)
- Manages scraping tasks
- Coordinates platform scrapers
- Handles task lifecycle
- Broadcasts updates via WebSocket

#### 2. **Stream Service** (`backend/services/stream_service.py`)
- Manages Chrome instances
- Handles MJPEG streaming
- Dynamic port allocation
- Timeout monitoring

#### 3. **Phone Extractor** (`extractors/phone_extractor.py`)
- Multi-layer extraction
- Normalization to E.164
- Confidence scoring
- Coordinate extraction

#### 4. **Chrome Pool** (`backend/services/chrome_pool.py`)
- Instance pooling
- Tab isolation
- Resource management
- Automatic cleanup

#### 5. **Analytics Service** (`backend/services/data_aggregation.py`)
- Daily/weekly/monthly summaries
- Period comparisons
- Platform statistics
- Category breakdowns

---

## Technology Stack

### Frontend
- **Framework**: Next.js 14 (React 18)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **State Management**: React Hooks
- **WebSocket**: Native WebSocket API

### Backend
- **Framework**: FastAPI (Python 3.9+)
- **ASGI Server**: Uvicorn
- **WebSocket**: FastAPI WebSocket
- **Database**: PostgreSQL (optional), SQLite (fallback)
- **Caching**: PostgreSQL, in-memory

### Browser Automation
- **Tool**: Selenium WebDriver
- **Browser**: Chrome/Chromium
- **Driver**: ChromeDriver
- **Protocol**: Chrome DevTools Protocol (CDP)

### Data Processing
- **Phone Parsing**: phonenumbers library
- **OCR**: Tesseract OCR
- **Image Processing**: Pillow, OpenCV
- **HTTP Client**: httpx (async), requests (sync)

### External APIs
- **Phone Verification**: Twilio Lookup API
- **Business Enrichment**: Clearbit API, Google Places API
- **AI**: OpenAI GPT-3.5-turbo (optional)

### DevOps
- **Containerization**: Docker
- **CI/CD**: GitHub Actions
- **Deployment**: Vercel (frontend), Docker (backend)
- **Testing**: pytest, Playwright, Jest

---

## Data Flow

### Input Flow

```
User Input
    ↓
Frontend Validation
    ↓
REST API (POST /api/scraper/start)
    ↓
Task Manager (Create Task)
    ↓
Orchestrator (Start Scraping)
    ↓
Platform Scrapers
    ↓
Browser Automation (Selenium)
    ↓
External Platforms
```

### Output Flow

```
Browser Automation
    ↓
Data Extraction
    ↓
Phone Extraction & Normalization
    ↓
Data Enrichment (Optional)
    ↓
Result Processing
    ↓
WebSocket Broadcast
    ↓
CSV Storage
    ↓
PostgreSQL Cache (if enabled)
    ↓
Frontend Display
```

### Real-Time Streaming Flow

```
Chrome Instance
    ↓
Screenshot Capture (every 0.5s)
    ↓
Image Compression
    ↓
MJPEG Frame Encoding
    ↓
WebSocket Stream
    ↓
Frontend Display (<img> tag)
```

---

## User Journey

### 1. **Initial Setup**

```
User opens application
    ↓
Authentication (if enabled)
    ↓
Consent modal (first time)
    ↓
Main dashboard
```

### 2. **Starting a Scrape**

```
User navigates to Scraper page
    ↓
Enters search queries
    ↓
Selects platforms
    ↓
Configures filters
    ↓
Clicks "Start Scraping"
    ↓
Task created, Chrome instance allocated
    ↓
Live browser view appears
    ↓
Results start streaming in real-time
```

### 3. **Monitoring Progress**

```
User watches live browser stream
    ↓
Sees phone numbers highlighted on page
    ↓
Clicks highlighted phone for details
    ↓
Views results table (auto-updates)
    ↓
Checks progress indicators
    ↓
Reviews logs in real-time
```

### 4. **Analyzing Results**

```
User navigates to Dashboard
    ↓
Views summary statistics
    ↓
Explores charts (platforms, timeline, categories)
    ↓
Compares periods
    ↓
Exports data (CSV, JSON, Excel)
```

### 5. **Data Management**

```
User views archived data
    ↓
Restores from archive if needed
    ↓
Exports specific date ranges
    ↓
Manages data retention
```

---

## Technical Deep Dive

### Phone Extraction Algorithm

```python
# Multi-layer extraction with confidence scoring
def extract_phones(driver, url):
    phones = []
    confidence_weights = {
        "tel_link": 0.95,
        "json_ld": 0.90,
        "visible_text": 0.70,
        "website_crawl": 0.60,
        "ocr": 0.50
    }
    
    # Extract from each layer
    for layer in ["tel_link", "json_ld", "visible_text", "website_crawl", "ocr"]:
        layer_phones = extract_from_layer(driver, layer)
        for phone in layer_phones:
            phone["confidence"] = confidence_weights[layer]
            phones.append(phone)
    
    # Normalize all phones
    normalized = []
    for phone in phones:
        normalized_phone = normalize_to_e164(phone["raw_phone"])
        if normalized_phone:
            phone["normalized_e164"] = normalized_phone
            normalized.append(phone)
    
    # Deduplicate by normalized number
    unique_phones = {}
    for phone in normalized:
        key = phone["normalized_e164"]
        if key not in unique_phones or phone["confidence"] > unique_phones[key]["confidence"]:
            unique_phones[key] = phone
    
    return list(unique_phones.values())
```

### Chrome Pool Management

```python
# Efficient Chrome instance reuse
class ChromePool:
    def acquire(self, task_id):
        # Try to reuse existing instance
        for instance in self.instances:
            if instance.has_available_tab():
                tab = instance.create_tab(task_id)
                return tab
        
        # Create new instance if pool not full
        if len(self.instances) < self.max_size:
            instance = self.create_instance()
            tab = instance.create_tab(task_id)
            return tab
        
        # Pool exhausted, wait or fail
        return None
    
    def release(self, task_id, tab):
        instance = tab.instance
        instance.close_tab(task_id)
        
        # Clean up instance if no tabs
        if instance.tab_count == 0:
            instance.cleanup()
```

### Async Scraping

```python
# Parallel HTTP requests for social platforms
async def scrape_social_platforms(urls):
    async with AsyncScraperService(max_concurrent=5) as scraper:
        async def scrape_url(url, client):
            response = await client.get(url)
            return parse_response(response)
        
        results = await scraper.scrape_batch(
            urls,
            scrape_url,
            delay_seconds=1.0
        )
        return results
```

### Data Archival Process

```python
# Automated archival to cold storage
def archive_old_records(cutoff_date):
    # Read all CSV files
    for csv_file in get_all_csv_files():
        old_records = []
        new_records = []
        
        # Partition by date
        for record in read_csv(csv_file):
            if record.date < cutoff_date:
                old_records.append(record)
            else:
                new_records.append(record)
        
        # Archive old records
        partition = get_partition(cutoff_date)
        archive_file = get_archive_file(partition, csv_file)
        write_to_archive(archive_file, old_records)
        
        # Update original file
        write_csv(csv_file, new_records)
```

---

## Deployment Architecture

### Production Setup

```
┌─────────────────────────────────────────┐
│         Vercel (Frontend)               │
│  - Next.js application                 │
│  - Automatic deployments               │
│  - CDN distribution                    │
└─────────────────────────────────────────┘
                    │
              HTTPS │
                    │
┌─────────────────────────────────────────┐
│    Load Balancer / Reverse Proxy        │
└─────────────────────────────────────────┘
                    │
                    │
┌─────────────────────────────────────────┐
│    Docker Container (Backend)           │
│  - FastAPI application                  │
│  - Chrome instances                     │
│  - PostgreSQL connection                │
└─────────────────────────────────────────┘
                    │
                    │
┌─────────────────────────────────────────┐
│         PostgreSQL Database             │
│  - URL cache                            │
│  - User data                            │
│  - Task metadata                        │
└─────────────────────────────────────────┘
```

### Environment Configuration

```bash
# Frontend (Vercel)
NEXT_PUBLIC_API_URL=https://api.yourdomain.com

# Backend (Docker)
DATABASE_URL=postgresql://user:pass@host:5432/db
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
CLEARBIT_API_KEY=your_key
GOOGLE_PLACES_API_KEY=your_key
OPENAI_API_KEY=your_key
JWT_SECRET_KEY=your_secret
CORS_ORIGINS=https://yourfrontend.vercel.app
```

---

## Key Features Explained

### 1. **Real-Time Browser Streaming**

The platform streams live browser screenshots to the frontend using MJPEG (Motion JPEG) format. This allows users to see exactly what the scraper is doing in real-time.

**How it works**:
- Chrome captures screenshots every 0.5 seconds
- Images are compressed to ~200KB
- Sent as MJPEG frames via HTTP stream
- Frontend displays in `<img>` tag with `src="/live_feed/{task_id}"`

### 2. **Phone Highlighting**

Phone numbers are visually highlighted on the live browser stream using coordinate-based overlays.

**How it works**:
- Chrome DevTools Protocol extracts element coordinates
- Coordinates normalized to 0-1 range (viewport relative)
- Frontend calculates pixel positions based on container size
- Overlay divs positioned absolutely over phone numbers

### 3. **Multi-Layer Phone Extraction**

Uses 5 different methods to maximize phone number discovery:

1. **tel: links** (95% confidence) - Direct HTML links
2. **JSON-LD** (90% confidence) - Structured data
3. **Visible text** (70% confidence) - Regex pattern matching
4. **Website crawl** (60% confidence) - Crawls linked websites
5. **OCR** (50% confidence) - Image-based extraction

### 4. **Chrome Instance Pooling**

Reuses Chrome instances across tasks to reduce startup overhead.

**Benefits**:
- Faster task initialization
- Lower memory usage
- Better resource utilization
- Automatic cleanup of idle instances

### 5. **Data Enrichment Pipeline**

Enhances lead data with external APIs and AI:

1. **Phone Verification**: Validates phone numbers via Twilio
2. **Business Enrichment**: Gets company data from Clearbit/Google Places
3. **AI Enhancement**: Generates descriptions and quality scores

---

## Performance Characteristics

### Scalability

- **Concurrent Tasks**: 10+ simultaneous scraping tasks
- **Throughput**: ~50 requests/second (async HTTP)
- **Data Volume**: Handles 100K+ records efficiently
- **Memory**: ~500MB per Chrome instance (shared pool)

### Optimization Techniques

1. **Connection Pooling**: Reuses HTTP connections
2. **Image Compression**: Reduces screenshot sizes by 60%
3. **Database Indexing**: Fast cache lookups (~5ms)
4. **Async Processing**: Parallel HTTP requests
5. **Resource Pooling**: Shared Chrome instances

---

## Security & Compliance

### Authentication
- JWT-based authentication
- Token refresh mechanism
- User isolation

### Data Privacy
- GDPR compliance
- Data retention policies
- Opt-out mechanism
- Consent management

### Security Measures
- CORS protection
- Input validation
- SQL injection prevention
- XSS protection

---

## Monitoring & Observability

### Health Checks
- `/api/health` - System health
- `/api/metrics` - Performance metrics

### Logging
- Real-time log streaming via WebSocket
- Task-specific log channels
- Error tracking

### Analytics
- Dashboard with real-time statistics
- Performance metrics
- Usage analytics

---

## Getting Started

### Quick Start

1. **Install Dependencies**:
   ```bash
   # Backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm install
   ```

2. **Configure Environment**:
   ```bash
   # Set environment variables
   export DATABASE_URL=postgresql://...
   export TWILIO_ACCOUNT_SID=...
   ```

3. **Start Services**:
   ```bash
   # Backend
   python -m backend.main
   
   # Frontend
   cd frontend
   npm run dev
   ```

4. **Access Application**:
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs

---

## Conclusion

The Lead Intelligence Platform is a comprehensive, enterprise-ready solution for automated lead generation. It combines advanced browser automation, AI-powered enrichment, and real-time analytics to deliver a powerful tool for businesses seeking to scale their lead generation efforts.

**Key Strengths**:
- ✅ Multi-platform support
- ✅ Advanced phone extraction
- ✅ Real-time monitoring
- ✅ Enterprise-scale performance
- ✅ Comprehensive analytics
- ✅ Production-ready infrastructure

For detailed implementation guides, see:
- `DEPLOYMENT.md` - Deployment instructions
- `CI_CD_DOCUMENTATION.md` - CI/CD setup
- `PERFORMANCE_TUNING_PLAN.md` - Performance optimization
- `ROADMAP_COMPLETION_SUMMARY.md` - Feature completion status

