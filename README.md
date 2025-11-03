# 🗺️ Google Maps Lead Scraper - CLI Version

A reliable and efficient command-line tool for scraping business leads from Google Maps. This streamlined version focuses on core functionality with maximum stability and performance.

---

## ✨ Features

* 🔍 **Automated Google Maps Search** - Processes multiple search queries automatically
* 📊 **Comprehensive Data Extraction** - Captures essential business information:
  * Business Name
  * Category/Type
  * Full Address
  * Phone Number
  * Website URL
  * Google Plus Code
* 💾 **Incremental CSV Saving** - Each result saved immediately to prevent data loss
* 🔄 **Resume Capability** - Continue from where you left off if interrupted
* 🛡️ **Error Handling** - Robust retry mechanisms and graceful error recovery
* ⚡ **Performance Optimized** - Headless mode for faster, resource-efficient operation
* 🌐 **Cross-Platform** - Works on Windows, macOS, and Linux

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
headless: true
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

Options:
```bash
# Skip Google Maps
python main.py --skip-gmaps

# Only specific platforms
python main.py --platforms instagram,facebook

# Override max results per query
python main.py --max-results 3
```

### Outputs
- Per-platform CSVs in `~/Documents/social_leads/{platform}.csv`
- Consolidated CSV in `~/Documents/social_leads/all_platforms.csv`

Common columns: `Search Query`, `Platform`, `Profile URL`, `Handle`, `Display Name`, `Bio/About`, `Website`, `Email`, `Phone`, `Followers`, `Location`.

### Notes
- Public-only: no logins or API tokens are used.
- Uses conservative rate limiting and retry/backoff. Increase delays if you encounter blocks.
