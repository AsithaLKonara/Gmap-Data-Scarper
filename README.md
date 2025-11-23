# 🗺️ Lead Intelligence Platform v3.9

A comprehensive, enterprise-grade lead intelligence platform for scraping and analyzing business leads from Google Maps and social media platforms. Features interactive web UI, real-time browser streaming, advanced phone extraction, AI-powered enrichment, comprehensive analytics, and production-ready infrastructure.

> 📖 **For complete project overview and architecture details, see [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)**

## 🎯 What It Does

The Lead Intelligence Platform automates lead generation by:
1. **Scraping** multiple platforms (Google Maps, LinkedIn, Facebook, etc.) using browser automation
2. **Extracting** phone numbers using 5 different methods (DOM, tel: links, JSON-LD, website crawl, OCR)
3. **Enriching** leads with phone verification, business data, and AI-powered insights
4. **Analyzing** data with comprehensive analytics and visualizations
5. **Exporting** results in multiple formats (CSV, JSON, Excel)

**Key Innovation**: Real-time browser streaming lets you watch the scraper work live, with phone numbers visually highlighted on the page.

---

## ✨ Features

### Core Scraping (v1.0)
* 🔍 **Automated Multi-Platform Search** - Google Maps, Facebook, Instagram, LinkedIn, X/Twitter, YouTube, TikTok
* 📊 **Comprehensive Data Extraction** - Business information, contact details, social profiles
* 💾 **Incremental CSV Saving** - Each result saved immediately to prevent data loss
* 🔄 **Resume Capability** - Continue from where you left off if interrupted
* 🛡️ **Error Handling** - Robust retry mechanisms and graceful error recovery
* ⚡ **Performance Optimized** - Headless mode for faster, resource-efficient operation
* 🌐 **Cross-Platform** - Works on Windows, macOS, and Linux

### Lead Intelligence (v2.0+)
* 🏢 **Business Classification** - Automatic categorization by business type and industry
* 📍 **Location Segmentation** - Extract and filter by city, region, country
* 👔 **Job-Level Classification** - Identify job titles and seniority levels
* 🎓 **Education Parsing** - Extract and classify education levels
* 📈 **Activity Detection** - Detect boosted posts and recent activity
* ⭐ **Lead Scoring** - Automatic lead ranking (0-100 score)
* 🎯 **Multi-Filter Search** - Combine filters (business, job, location, time, education)
* 🤖 **AI Insights** - Intent detection (Hugging Face), sentiment analysis, automated summaries (optional OpenAI)
* 📊 **Analytics Dashboard** - Optional Streamlit dashboard for visualization
* 🔄 **Data Enrichment API** - Re-scrape and enrich existing datasets

### Web UI & Phone Extraction (v3.0+)
* 🌐 **Interactive Web Interface** - Next.js frontend with real-time updates
* 📱 **Phone Extraction** - Multi-layer extraction (DOM, tel: links, JSON-LD, website crawl, OCR)
* 📞 **Phone Normalization** - E.164 formatting with validation and confidence scoring
* 🎯 **Phone Highlighting** - Visual feedback in live browser view with source tracking
* 👤 **Individual Lead Classification** - Detect students vs professionals with field of study extraction
* ⚖️ **Legal Compliance** - Data retention policy (6 months), consent notices, opt-out mechanism
* ⚡ **Performance Features** - URL caching, smart rate limiting, parallel scraping ready
* 🎥 **Live Browser Streaming** - Real-time MJPEG stream of scraping process
* 📤 **Enhanced Export** - Task-specific, date range, and platform-specific CSV export

### Enterprise Features (v3.2+)
* 🔐 **User Authentication** - JWT-based multi-user support with task isolation
* 📊 **Analytics Dashboard** - Comprehensive analytics with daily/weekly/monthly summaries
* 🔍 **Lead Enrichment** - Phone verification (Twilio), business enrichment (Clearbit, Google Places)
* 🤖 **AI Enhancement** - Business descriptions, quality assessment, key insights (OpenAI)
* ⚡ **Performance Tuning** - Chrome instance pooling, async scraping, PostgreSQL caching
* 📦 **Data Archival** - Automated archival to cold storage with partition-based organization
* 🚀 **CI/CD** - Automated testing, deployment pipelines, quality gates
* 📈 **Scalability** - Optimized for 100K+ records with 5x performance improvements

---

## 📁 Project Structure

```
gmap-data-scraper/
├── app.py                  # Main scraper script (CLI)
├── run_batch.py            # Batch processing for large datasets
├── search_queries.txt      # Input file with search terms
├── requirements.txt        # Python dependencies
├── README.md              # This documentation
└── venv/                  # Python virtual environment
```

---

## 🚀 Quick Start

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Prepare Search Queries**
Edit `search_queries.txt` with your search terms (one per line):
```
clothing store in Colombo
fashion store in Kandy
boutique in Galle
textile shop in Negombo
garment shop in Jaffna
```

### 3. **Run the Scraper**
```bash
python app.py
```

### 4. **For Large Datasets (Recommended)**
```bash
python run_batch.py
```

---

## ⚙️ Configuration

The scraper is pre-configured with optimal settings:

```python
# Key settings in app.py
HEADLESS = True                    # Run without browser window
MAX_RESULTS_PER_QUERY = 5         # Limit results per search
DELAY_BETWEEN_QUERIES = 10        # Pause between searches (seconds)
RESUME_MODE = True                # Skip already processed queries
OUTPUT_CSV = "~/Documents/gmap_all_leads.csv"  # Output location
```

---

## 📊 Output Format

Results are saved to CSV with the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| Search Query | Original search term | "clothing store in Colombo" |
| Business Name | Company name | "Swastik Boutiques" |
| Category | Business type | "Clothing store" |
| Address | Full address | "95 Kotahena St, Colombo 01300" |
| Phone | Contact number | "077 567 4586" |
| Website | Company website | "swastikboutiques.com" |
| Plus Code | Google location code | "WVX7+X3 Colombo" |

---

## 🛡️ Safety Features

### **Data Protection**
- ✅ **Immediate Saving** - Each result saved instantly to CSV
- ✅ **No Data Loss** - Safe even if program stops unexpectedly
- ✅ **Resume Mode** - Automatically skips completed queries
- ✅ **Error Recovery** - Continues despite individual failures

### **System Protection**
- ✅ **Headless Mode** - Reduces resource usage
- ✅ **Result Limits** - Prevents system overload
- ✅ **Delays** - Gives system time to recover
- ✅ **Memory Management** - Optimized for stability

---

## 🔧 Advanced Usage

### **Batch Processing**
For large datasets, use the batch processor:
```bash
python run_batch.py
```
- Processes queries in small batches
- Prevents system overload
- Automatic cleanup between batches

### **Custom Configuration**
Modify settings in `app.py`:
```python
# Adjust these values as needed
MAX_RESULTS_PER_QUERY = 10    # More results per search
DELAY_BETWEEN_QUERIES = 5     # Faster processing
HEADLESS = False              # Show browser window
```

---

## 📈 Performance

### **Typical Performance**
- **Speed**: ~30-60 seconds per query
- **Success Rate**: 95%+ for valid queries
- **Data Quality**: 80%+ complete records
- **Memory Usage**: <500MB typical

### **Optimization Tips**
1. **Use Batch Mode** for 50+ queries
2. **Increase delays** if getting blocked
3. **Reduce max results** for faster processing
4. **Monitor system resources** during large runs

---

## 🚨 Troubleshooting

### **Common Issues**

**No results found:**
- Check internet connection
- Verify search queries are valid
- Try different search terms
- Check if Google Maps is accessible

**Scraping stops unexpectedly:**
- Check system resources (CPU, Memory)
- Reduce max results per query
- Increase delay between queries
- Use batch mode for large datasets

**Browser errors:**
- Update Chrome browser
- Clear browser cache
- Restart the application

---

## 📋 Requirements

- **Python**: 3.8 or higher
- **Chrome Browser**: Latest version
- **Memory**: 2GB RAM minimum (4GB recommended)
- **Storage**: 100MB free space
- **OS**: Windows, macOS, or Linux

---

## 👨‍💻 Author

**Asitha L Konara**

---

## ⚠️ Disclaimer

This tool is intended for personal or educational use. Please use responsibly and in accordance with Google Maps' terms of service. Respect rate limits and don't overload Google's servers.

---

## 🎯 Ready to Start?

1. Make sure you have `search_queries.txt` with your search terms
2. Run: `python app.py`
3. Watch your leads get collected! 🎯

**For large datasets**: Use `python run_batch.py` for safer processing.

---

## 🌐 Multi-Platform Social Scraper (Public-only)

In addition to Google Maps, this project can discover and collect public profile metadata from Facebook, Instagram, LinkedIn, X (Twitter), YouTube, and TikTok — without logins or API keys.

### Quick Start (Multi-Platform)

1) Install dependencies
```bash
pip install -r requirements.txt
```

2) Configure (optional): edit `config.yaml` to enable/disable platforms and tune limits
```yaml
enabled_platforms: [facebook, instagram, linkedin, x, youtube, tiktok]
max_results_per_query: 5
headless: false  # Set to false to see browser window, or use --no-headless flag
per_platform_delay_seconds: 8
per_request_delay_seconds: 2
resume: true
site_search_engine: google
output_dir: "~/Documents/social_leads"
```

3) Run the orchestrator
```bash
python main.py
```

### CLI Options

```bash
# Show help and available platforms
python main.py --help

# Run all platforms (from config.yaml)
python main.py

# Select specific platforms to run
python main.py --platforms google_maps,facebook,instagram

# Skip Google Maps (only social platforms)
python main.py --skip-gmaps

# Show browser window (see what's happening)
python main.py --no-headless

# Run specific platforms with visible browser
python main.py --platforms google_maps,instagram --no-headless

# Override max results per query
python main.py --max-results 10

# Combine options
python main.py --platforms facebook,instagram --no-headless --max-results 5
```

**Available Platforms:**
- `google_maps` - Google Maps business listings
- `facebook` - Facebook Pages
- `instagram` - Instagram Business profiles
- `linkedin` - LinkedIn Company pages
- `x` - X (Twitter) profiles
- `youtube` - YouTube Channels
- `tiktok` - TikTok profiles

### Outputs
- Per-platform CSVs in `~/Documents/social_leads/{platform}.csv`
- Consolidated CSV in `~/Documents/social_leads/all_platforms.csv`

Common columns: `Search Query`, `Platform`, `Profile URL`, `Handle`, `Display Name`, `Bio/About`, `Website`, `Email`, `Phone`, `Followers`, `Location`.

### Notes
- Public-only: no logins or API tokens are used.
- Uses conservative rate limiting and retry/backoff. Increase delays if you encounter blocks.

---

## 🧪 Testing

Comprehensive test suite included. Run tests with:

```bash
# Install test dependencies (already in requirements.txt)
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage report
pytest --cov=scrapers --cov=utils --cov=orchestrator_core --cov-report=html

# Run specific test categories
pytest tests/unit/        # Unit tests
pytest tests/platform/   # Platform-specific tests
pytest tests/cli/         # CLI tests
```

See `TESTING.md` and `tests/README.md` for detailed testing documentation.

**Current Status**: 50+ tests passing ✅

### Recent Improvements
- ✅ **Fixed Critical Bug**: Results list disappearing issue resolved using URL-based navigation
- ✅ **Enhanced Testing**: Added comprehensive tests for all platforms including Google Maps
- ✅ **Improved Reliability**: URL-based navigation allows processing all results, not just 1-2

