# Upgrade Guide: v1.0 → v2.0

This guide helps you migrate from v1.0 to v2.0 of the Google Maps & Social Media Lead Scraper.

## Overview

v2.0 introduces significant new features:
- **Lead Classification**: Business type, job title, education level
- **Location Segmentation**: City, region, country extraction
- **Activity Detection**: Boosted posts, recent activity
- **Lead Scoring**: Automatic ranking (0-100)
- **Multi-Filter Search**: Combined filtering capabilities
- **AI Insights**: Intent detection, sentiment analysis, summaries
- **Analytics Dashboard**: Optional visualization tool
- **Data Enrichment**: Re-scrape existing datasets

## Backward Compatibility

v2.0 is **fully backward compatible** with v1.0:
- ✅ All v1.0 CSV files work without modification
- ✅ All v1.0 config files are still valid
- ✅ All v1.0 CLI commands work as before
- ✅ New fields default to "N/A" if not available

## Installation

### 1. Update Dependencies

```bash
pip install -r requirements.txt
```

New optional dependencies (for dashboard):
```bash
pip install streamlit pandas
```

### 2. No Code Changes Required

Your existing scripts and configs will work without modification. New features are opt-in.

## New Features

### 1. Business Classification

Automatically classifies leads by business type:

```bash
# Filter by business type
python main.py --business-type restaurant,clinic,salon
```

Or in `config.yaml`:
```yaml
filters:
  business_type: ["restaurant", "clinic", "salon"]
```

### 2. Location Filtering

Filter leads by location:

```bash
# Filter by location
python main.py --location "New York" --radius 50
```

### 3. Job Level Filtering

Filter by job seniority:

```bash
# Filter by job level
python main.py --job-level "Senior,Executive"
```

### 4. Category-Based Query Generation

Generate queries automatically from categories:

```bash
# Generate queries from categories
python main.py --category restaurant,marketing,technology
```

### 5. Time-Based Filtering

Filter by activity recency:

```bash
# Only active within 30 days
python main.py --active-within 30

# Date range filter
python main.py --date-range "2025-01-01:2025-03-31"
```

### 6. Boosted Posts Only

Filter for leads with boosted/sponsored posts:

```bash
python main.py --boosted-only
```

### 7. Education Level Filtering

Filter by education level:

```bash
python main.py --education-level "Postgraduate,Doctorate"
```

## New CSV Fields

v2.0 adds new fields to CSV output (all default to "N/A" if not available):

### Classification Fields
- `business_type`: Business category (restaurant, clinic, etc.)
- `industry`: Industry classification
- `sub_category`: Sub-category classification
- `job_title`: Extracted job title
- `seniority_level`: Job seniority (Junior, Mid, Senior, Executive, Freelancer)
- `education_level`: Education level (High School, Undergraduate, Postgraduate, Doctorate)
- `institution_name`: Educational institution name

### Location Fields
- `city`: City name
- `region`: State/region name
- `country`: Country name
- `postal_code`: Postal/ZIP code

### Activity Fields
- `last_post_date`: Date of last post
- `is_boosted`: Whether post is boosted/sponsored (true/false)
- `post_engagement`: Engagement metrics

### Intelligence Fields
- `lead_score`: Lead quality score (0-100)
- `intent_category`: Detected intent (Hiring, Promoting, Expanding, Inactive)
- `sentiment_score`: Sentiment score (0-100)
- `sentiment_trend`: Sentiment trend (Positive, Neutral, Negative)
- `lead_summary`: Automated summary text
- `extracted_at`: Timestamp of extraction

## Configuration Updates

### New Config Options

Add to `config.yaml`:

```yaml
# v2.0+ Filter Options
filters:
  business_type: []  # Empty = no filter
  job_level: []       # Empty = no filter
  location: null      # null = no filter
  radius_km: null     # null = no radius limit
  education_level: []
  date_range: null    # YYYY-MM-DD:YYYY-MM-DD
  active_within_days: null
  boosted_only: false

# Category-based query generation
categories: []  # List of categories to auto-generate queries
```

## Data Enrichment

Enrich existing v1.0 CSV files with v2.0 data:

```bash
python -m enrichment.enrich_existing input.csv output_enriched.csv
```

This will:
- Add business classification
- Extract location data
- Detect activity
- Calculate lead scores
- Add AI insights

## Analytics Dashboard

Launch the optional dashboard:

```bash
streamlit run dashboard/app.py
```

Features:
- Visualize leads by platform, business type, location
- Filter and export data
- View lead score distribution
- Analyze engagement metrics

## Migration Steps

### Step 1: Backup Existing Data

```bash
cp all_platforms.csv all_platforms_v1_backup.csv
```

### Step 2: Update Code

```bash
git pull  # or update your codebase
pip install -r requirements.txt
```

### Step 3: Test with Existing Config

Run your existing commands - they should work identically:

```bash
python main.py
```

### Step 4: Enable New Features (Optional)

Gradually enable new features:

1. Start with classification (no filters):
   ```bash
   python main.py  # Classification runs automatically
   ```

2. Add filters as needed:
   ```bash
   python main.py --business-type restaurant --location "New York"
   ```

3. Use enrichment API for existing data:
   ```bash
   python -m enrichment.enrich_existing all_platforms.csv
   ```

## Troubleshooting

### Issue: New fields show "N/A"

**Solution**: This is normal. Fields default to "N/A" if data isn't available. Classification runs automatically but may not find matches for all leads.

### Issue: Classification not working

**Solution**: Check that classification modules are installed:
```bash
python -c "from classification import BusinessClassifier; print('OK')"
```

### Issue: Dashboard not loading

**Solution**: Install Streamlit:
```bash
pip install streamlit pandas
```

### Issue: Enrichment API errors

**Solution**: Ensure all dependencies are installed and input CSV is valid.

## Performance Notes

- Classification adds minimal overhead (~10-50ms per lead)
- Activity scraping adds ~2-5 seconds per social media profile
- Lead scoring is instant
- AI insights add ~100-200ms per lead

## Rollback

If you need to rollback to v1.0 behavior:

1. Use v1.0 codebase
2. Ignore new CSV columns
3. Don't use new CLI flags

All v1.0 functionality remains unchanged.

## Support

For issues or questions:
1. Check this guide
2. Review `README.md` for usage examples
3. Check `TECHNICAL_REVIEW.md` for technical details

## What's Next?

v2.0 is the foundation for future enhancements:
- v2.1: Enhanced activity detection
- v2.2: Advanced analytics
- v2.3: Performance optimizations
- v3.0: Advanced AI features

Enjoy the new features! 🚀

