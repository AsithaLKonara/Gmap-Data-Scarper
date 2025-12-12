# Deep End-to-End Test Guide

## Overview

This comprehensive E2E test simulates a complete user journey through the Lead Intelligence Platform, testing all major features from authentication to data export.

## Prerequisites

1. **Backend server must be running**
2. **Database must be accessible**
3. **Python dependencies installed**

## Starting the Server

### Option 1: Using PowerShell Script (Windows)
```powershell
.\start_backend.ps1
```

### Option 2: Manual Start
```powershell
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: Direct Python
```powershell
python backend/main.py
```

The server should be available at: `http://localhost:8000`

## Running the E2E Test

### Basic Usage
```bash
python test_e2e_user_journey.py
```

### With Custom API URL
```bash
set API_URL=http://localhost:8000
python test_e2e_user_journey.py
```

Or on Linux/Mac:
```bash
export API_URL=http://localhost:8000
python test_e2e_user_journey.py
```

## Test Phases

The E2E test is organized into 5 phases:

### Phase 1: Authentication & Setup
- ✅ Health check
- ✅ User registration
- ✅ User login
- ✅ Get user profile

### Phase 2: Exploration
- ✅ Get available filters
- ✅ List existing tasks
- ✅ Get analytics summary

### Phase 3: Scraping
- ✅ Start scraping task
- ✅ Monitor task status
- ✅ Get task details

### Phase 4: Data Management
- ✅ Export data as JSON
- ✅ Export data as CSV
- ✅ Soft delete lead
- ✅ Get platform analytics
- ✅ Get timeline analytics

### Phase 5: Task Management
- ✅ Stop scraping task
- ✅ Validate token

## Test Output

The test generates:
1. **Console output** - Real-time progress and results
2. **JSON report** - Detailed test report saved as `e2e_test_report_{timestamp}.json`

### Report Structure
```json
{
  "summary": {
    "total_steps": 17,
    "passed": 15,
    "failed": 2,
    "success_rate": 88.2,
    "test_user": "e2e_test_...@example.com",
    "task_id": "..."
  },
  "results": [
    {
      "step": "1. Health Check",
      "status": "✅ PASS",
      "message": "API is healthy",
      "timestamp": "2025-01-17T...",
      "data": {...}
    }
  ]
}
```

## Expected Results

### Success Criteria
- ✅ All authentication steps pass
- ✅ Scraping task starts successfully
- ✅ Data export works
- ✅ Analytics endpoints respond
- ✅ Soft delete functionality works

### Common Issues

#### Server Not Running
**Error**: `Connection refused` or `No connection could be made`

**Solution**: Start the backend server first (see "Starting the Server" above)

#### Database Connection Issues
**Error**: `Database status: disconnected`

**Solution**: 
- Check database configuration in `backend/config.py`
- Ensure database is running
- Verify `DATABASE_URL` environment variable

#### Authentication Failures
**Error**: `401 Unauthorized` or `403 Forbidden`

**Solution**:
- Check if user already exists (test creates unique users)
- Verify JWT token generation is working
- Check authentication middleware

#### Task Creation Fails
**Error**: `403 Forbidden - Daily lead limit exceeded`

**Solution**:
- This is expected for free tier users
- Test will continue with other steps
- Check usage limits in database

## Test Coverage

### Endpoints Tested
- `/api/health` - Health check
- `/api/auth/register` - User registration
- `/api/auth/login` - User login
- `/api/auth/me` - Get user profile
- `/api/filters/*` - Filter endpoints
- `/api/tasks` - List tasks
- `/api/tasks/{id}` - Get task details
- `/api/scraper/start` - Start scraping
- `/api/scraper/status/{id}` - Task status
- `/api/scraper/stop/{id}` - Stop task
- `/api/export/json` - JSON export
- `/api/export/csv` - CSV export
- `/api/analytics/summary` - Analytics summary
- `/api/analytics/platforms` - Platform analytics
- `/api/analytics/timeline` - Timeline analytics
- `/api/soft-delete/leads/{id}/delete` - Soft delete

### Features Tested
- ✅ User authentication flow
- ✅ Task creation and management
- ✅ Real-time task monitoring
- ✅ Data export (JSON, CSV)
- ✅ Analytics and reporting
- ✅ Soft delete functionality
- ✅ Token validation

## Customization

### Modify Test User
Edit the test file to change:
```python
TEST_USER_EMAIL = "your_email@example.com"
TEST_USER_PASSWORD = "YourPassword123!"
```

### Modify Scraping Parameters
Edit `step_8_start_scraping_task()`:
```python
scrape_request = {
    "queries": ["your query"],
    "platforms": ["google_maps"],
    "max_results": 10,
    "headless": True
}
```

### Add More Test Steps
Add new methods following the pattern:
```python
def step_X_your_test(self) -> bool:
    """Step X: Description"""
    try:
        # Your test code
        self.log_step("X. Your Test", True, "Success message")
        return True
    except Exception as e:
        self.log_step("X. Your Test", False, f"Error: {str(e)}")
        return False
```

Then call it in `run_complete_journey()`.

## Integration with CI/CD

### GitHub Actions Example
```yaml
- name: Run E2E Tests
  run: |
    # Start backend server
    python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
    sleep 5
    
    # Run E2E test
    python test_e2e_user_journey.py
    
    # Check exit code
    if [ $? -ne 0 ]; then
      echo "E2E tests failed"
      exit 1
    fi
```

## Troubleshooting

### Test Hangs
- Check if scraping task is stuck
- Verify Chrome/ChromeDriver is installed
- Check server logs for errors

### Timeout Issues
- Increase timeout in `make_request()` method
- Check network connectivity
- Verify server is responding

### Data Not Found
- Some steps may pass even if no data exists (expected behavior)
- Check database for existing leads
- Verify scraping task completed successfully

## Next Steps

After running the E2E test:
1. Review the generated JSON report
2. Fix any failing steps
3. Re-run the test to verify fixes
4. Integrate into CI/CD pipeline
5. Schedule regular test runs

## Support

For issues or questions:
1. Check server logs
2. Review test report JSON
3. Verify all prerequisites are met
4. Check database connectivity

