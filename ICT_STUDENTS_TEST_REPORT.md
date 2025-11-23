# ICT Students Test Report

**Date**: 2025-01-13  
**Test Query**: "ICT related students in kandy undergraduates"  
**Filters Applied**: Field of Study: ICT, Students Only: ✓

---

## Test Configuration

### Query Details
- **Search Query**: "ICT related students in kandy undergraduates"
- **Field of Study Filter**: ICT
- **Students Only**: Enabled ✓
- **Location**: Kandy, Sri Lanka
- **Target**: Undergraduate students

### Expected Behavior
1. Search for ICT-related students in Kandy
2. Filter for undergraduate students only
3. Extract student information (name, contact, institution, field of study)
4. Classify leads as "Individual" (student) vs "Business"
5. Save results to CSV files

---

## Test Status

### ✅ UI Configuration Complete
- Query entered: "ICT related students in kandy undergraduates"
- Field of Study: "ICT" ✓
- Students Only checkbox: Checked ✓
- Start Scraping button: Clicked ✓

### ⚠️ Backend Connection Issue
- Backend not currently running
- Frontend shows "Failed to fetch" error
- Cannot test real-time scraping via UI

### ✅ Alternative Testing Method
- Created test query file: `test_ict_students.txt`
- Can be tested via CLI: `python main.py --platforms google_maps`
- Or via: `python app.py` (after editing search_queries.txt)

---

## Data Analysis

### Existing Data Search
Searched existing CSV files for ICT/student-related content:

**Results**: Found 44 potentially relevant leads containing:
- Keywords: "ICT", "ict", "student", "kandy", "undergraduate"

**Note**: These are from previous searches. New query-specific results will be generated when the scraper runs.

---

## How to Run the Test

### Option 1: Via CLI (Recommended)
```bash
# Edit search_queries.txt
echo "ICT related students in kandy undergraduates" > search_queries.txt

# Run scraper
python app.py
```

### Option 2: Via Main Script
```bash
# Use test file
python main.py --platforms google_maps
```

### Option 3: Via Web UI (When Backend is Running)
1. Navigate to http://localhost:3000
2. Enter query: "ICT related students in kandy undergraduates"
3. Set Field of Study: "ICT"
4. Check "Students Only"
5. Click "Start Scraping"

---

## Expected Output

### CSV Files
Results will be saved to:
- `C:\Users\asith\Documents\social_leads\all_platforms.csv`
- `C:\Users\asith\Documents\social_leads\google_maps.csv`
- Platform-specific files (if other platforms selected)

### Data Fields
Each lead should include:
- Search Query: "ICT related students in kandy undergraduates"
- Platform: google_maps (or other selected platforms)
- Display Name: Student name or profile name
- Bio/About: Student description, field of study, institution
- Location: Kandy (or related location)
- Classification: "Individual" (student)
- Field of Study: ICT (extracted from bio/description)

---

## Student Classification Features

The application should:
1. ✅ Detect if lead is a student vs professional
2. ✅ Extract field of study (ICT)
3. ✅ Identify education level (undergraduate)
4. ✅ Extract institution name
5. ✅ Filter for students only (when checkbox enabled)

---

## Next Steps

1. **Start Backend** (if testing via UI):
   ```bash
   python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Run CLI Test** (if testing via CLI):
   ```bash
   python app.py
   ```

3. **Monitor Results**:
   - Check CSV files for new leads
   - Verify student classification
   - Confirm ICT field of study extraction
   - Validate location filtering (Kandy)

---

## Verification Checklist

- [ ] Query executed successfully
- [ ] Leads collected from search
- [ ] Student classification working
- [ ] Field of study (ICT) extracted
- [ ] Location (Kandy) filtered correctly
- [ ] Undergraduate level identified
- [ ] Data saved to CSV files
- [ ] Phone numbers extracted (if available)
- [ ] Contact information captured

---

**Test Status**: ⏳ Ready to Execute  
**Backend Status**: ⚠️ Not Running (for UI testing)  
**CLI Status**: ✅ Ready (alternative method available)

