# 🚀 Test Execution Guide

## Quick Start

### Prerequisites
```bash
# Install dependencies
cd frontend && npm install
cd ../backend && pip install -r requirements.txt

# Set up test database
export TEST_DATABASE_URL="postgresql://user:pass@localhost/test_db"

# Set up environment variables
cp .env.example .env.test
```

### Running Tests

#### Frontend Tests
```bash
cd frontend
npm test                    # Run all tests
npm test -- --watch        # Watch mode
npm test -- --coverage     # With coverage
npm run test:e2e           # E2E tests with Playwright
```

#### Backend Tests
```bash
cd backend
pytest                     # Run all tests
pytest -v                  # Verbose output
pytest --cov               # With coverage
pytest tests/test_api.py  # Specific test file
pytest -k "test_scraper"  # Run tests matching pattern
```

#### Integration Tests
```bash
# Start test services
docker-compose -f docker-compose.test.yml up -d

# Run integration tests
pytest tests/integration/

# Cleanup
docker-compose -f docker-compose.test.yml down
```

---

## Test Scenarios by Priority

### 🔴 Critical (Must Pass Before Release)

#### 1. User Registration & Login
```bash
# Test: User can register
POST /api/auth/register
Body: { "email": "test@example.com", "password": "SecurePass123!" }
Expected: 201, returns user data

# Test: User can login
POST /api/auth/login
Body: { "email": "test@example.com", "password": "SecurePass123!" }
Expected: 200, returns JWT token

# Test: Invalid credentials rejected
POST /api/auth/login
Body: { "email": "test@example.com", "password": "wrong" }
Expected: 401, error message
```

#### 2. Start Scraping Task
```bash
# Test: Start scraping with valid data
POST /api/scraper/start
Body: {
  "queries": ["restaurants in Toronto"],
  "platforms": ["google_maps"]
}
Expected: 200, returns task_id

# Test: WebSocket connection established
WS /api/scraper/ws/results/{task_id}
Expected: Receives result updates
```

#### 3. Lead Data Collection
```bash
# Test: Results are received via WebSocket
# Expected: Results array populated with lead data
# Expected: Phone numbers are extracted
# Expected: Lead scores are calculated
```

#### 4. Export Functionality
```bash
# Test: CSV export
GET /api/export/csv?task_id={task_id}
Expected: CSV file downloads with all leads

# Test: JSON export
GET /api/export/json?task_id={task_id}
Expected: JSON file downloads with all leads
```

---

### 🟡 High Priority (Should Pass Before Release)

#### 5. Lead Scoring
- [ ] Hot leads (score >= 80) are correctly identified
- [ ] Warm leads (50-79) are correctly identified
- [ ] Low leads (< 50) are correctly identified
- [ ] Scores are displayed in dashboard

#### 6. Search & Filter
- [ ] Search by name works
- [ ] Search by location works
- [ ] Search by phone works
- [ ] Filter by lead score works
- [ ] Multiple filters work together

#### 7. Platform Selection
- [ ] All platforms can be selected
- [ ] Multiple platforms work together
- [ ] Platform-specific data is extracted

#### 8. AI Features
- [ ] Query generation works
- [ ] Natural language input is processed
- [ ] Generated queries are relevant

---

### 🟢 Medium Priority (Nice to Have)

#### 9. Workflow Automation
- [ ] Workflows can be created
- [ ] Workflows trigger on new leads
- [ ] Actions execute correctly

#### 10. Team Features
- [ ] Teams can be created
- [ ] Members can be added
- [ ] Permissions work correctly

#### 11. Analytics
- [ ] Dashboard metrics are accurate
- [ ] Charts render correctly
- [ ] Date filtering works

---

## Manual Testing Scenarios

### Scenario 1: Complete Lead Collection Flow
1. **Register/Login** → User creates account
2. **Configure Search** → Set queries, platforms, filters
3. **Start Task** → Begin scraping
4. **Monitor Results** → Watch dashboard for incoming leads
5. **Filter Leads** → Use search and filters
6. **Export Data** → Export to CSV/JSON/Excel
7. **Stop Task** → End scraping

**Expected Result:** All steps complete successfully, leads are collected and exportable

### Scenario 2: Lead Scoring & Categorization
1. **Start Scraping** → Collect 50+ leads
2. **View Dashboard** → Check lead scores
3. **Filter Hot Leads** → View only high-score leads
4. **Verify Scores** → Ensure scores match lead quality

**Expected Result:** Leads are correctly scored and categorized

### Scenario 3: Multi-Platform Scraping
1. **Select Multiple Platforms** → Google Maps, LinkedIn, Yelp
2. **Start Scraping** → Begin multi-platform search
3. **Monitor Progress** → Check progress for each platform
4. **Verify Results** → Ensure data from all platforms

**Expected Result:** Data collected from all selected platforms

### Scenario 4: Error Handling
1. **Invalid Query** → Submit empty query
2. **Network Error** → Disconnect internet
3. **Invalid Platform** → Select non-existent platform
4. **Verify Recovery** → System handles errors gracefully

**Expected Result:** Appropriate error messages, system recovers

---

## Automated Test Scripts

### API Test Script
```python
# tests/test_api_comprehensive.py
import pytest
import requests

BASE_URL = "http://localhost:8000"

def test_complete_flow():
    # 1. Register
    register_response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={"email": "test@example.com", "password": "SecurePass123!"}
    )
    assert register_response.status_code == 201
    
    # 2. Login
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "test@example.com", "password": "SecurePass123!"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # 3. Start scraping
    headers = {"Authorization": f"Bearer {token}"}
    scrape_response = requests.post(
        f"{BASE_URL}/api/scraper/start",
        json={
            "queries": ["restaurants in Toronto"],
            "platforms": ["google_maps"]
        },
        headers=headers
    )
    assert scrape_response.status_code == 200
    task_id = scrape_response.json()["task_id"]
    
    # 4. Check status
    status_response = requests.get(
        f"{BASE_URL}/api/scraper/status/{task_id}",
        headers=headers
    )
    assert status_response.status_code == 200
    
    # 5. Export results
    export_response = requests.get(
        f"{BASE_URL}/api/export/csv?task_id={task_id}",
        headers=headers
    )
    assert export_response.status_code == 200
    assert export_response.headers["content-type"] == "text/csv"
```

### Frontend E2E Test
```typescript
// frontend/e2e/lead-collection.spec.ts
import { test, expect } from '@playwright/test';

test('Complete lead collection flow', async ({ page }) => {
  // 1. Navigate to app
  await page.goto('http://localhost:3000');
  
  // 2. Fill search form
  await page.fill('input[placeholder*="query"]', 'restaurants in Toronto');
  await page.check('input[type="checkbox"][value="google_maps"]');
  
  // 3. Start scraping
  await page.click('button:has-text("Start Scraping")');
  
  // 4. Wait for results
  await page.waitForSelector('[data-testid="lead-result"]', { timeout: 30000 });
  
  // 5. Verify results appear
  const results = await page.locator('[data-testid="lead-result"]').count();
  expect(results).toBeGreaterThan(0);
  
  // 6. Test filtering
  await page.click('button:has-text("Hot")');
  const filteredResults = await page.locator('[data-testid="lead-result"]').count();
  expect(filteredResults).toBeLessThanOrEqual(results);
  
  // 7. Test export
  await page.click('button:has-text("Export")');
  // Verify download started
});
```

---

## Performance Testing

### Load Test Script
```python
# tests/performance/load_test.py
from locust import HttpUser, task, between

class LeadScraperUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "SecurePass123!"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def start_scraping(self):
        self.client.post(
            "/api/scraper/start",
            json={"queries": ["test"], "platforms": ["google_maps"]},
            headers=self.headers
        )
    
    @task(5)
    def get_status(self):
        self.client.get(
            "/api/scraper/status/test_id",
            headers=self.headers
        )
    
    @task(2)
    def export_data(self):
        self.client.get(
            "/api/export/csv?task_id=test_id",
            headers=self.headers
        )
```

Run with:
```bash
locust -f tests/performance/load_test.py --host=http://localhost:8000
```

---

## Security Testing

### SQL Injection Test
```python
# Test: SQL injection in query field
POST /api/scraper/start
Body: {
  "queries": ["'; DROP TABLE leads; --"],
  "platforms": ["google_maps"]
}
Expected: Query is sanitized, no SQL execution
```

### XSS Test
```python
# Test: XSS in query field
POST /api/scraper/start
Body: {
  "queries": ["<script>alert('XSS')</script>"],
  "platforms": ["google_maps"]
}
Expected: Script tags are escaped
```

### Authentication Test
```python
# Test: Access protected endpoint without token
GET /api/scraper/status/123
Expected: 401 Unauthorized

# Test: Access with invalid token
GET /api/scraper/status/123
Headers: {"Authorization": "Bearer invalid_token"}
Expected: 401 Unauthorized
```

---

## Test Data Management

### Test Fixtures
```python
# tests/fixtures.py
@pytest.fixture
def test_user():
    return {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "user_id": "test_user_123"
    }

@pytest.fixture
def test_lead():
    return {
        "display_name": "Test Business",
        "location": "Toronto, ON",
        "phones": [{"raw_phone": "+1234567890"}],
        "lead_score": 75
    }
```

### Database Seeding
```python
# tests/seed_db.py
def seed_test_data():
    # Create test users
    # Create test leads
    # Create test tasks
    pass
```

---

## Test Reporting

### Generate Coverage Report
```bash
# Backend
pytest --cov=backend --cov-report=html
open htmlcov/index.html

# Frontend
npm test -- --coverage
open coverage/lcov-report/index.html
```

### Generate Test Report
```bash
# Pytest HTML report
pytest --html=report.html --self-contained-html

# Playwright HTML report
npx playwright show-report
```

---

## Continuous Testing

### GitHub Actions Workflow
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest --cov --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## Test Checklist Execution

### Daily Testing (Smoke Tests)
- [ ] User can login
- [ ] User can start scraping
- [ ] Results are received
- [ ] Export works

### Weekly Testing (Regression Tests)
- [ ] All critical paths
- [ ] All high-priority features
- [ ] Performance benchmarks

### Pre-Release Testing (Full Suite)
- [ ] Complete test checklist
- [ ] All automated tests pass
- [ ] Manual testing complete
- [ ] Performance testing complete
- [ ] Security testing complete

---

## Troubleshooting

### Common Issues

#### Tests Failing Due to Database
```bash
# Reset test database
pytest --fixtures
# Or manually:
dropdb test_db && createdb test_db
```

#### WebSocket Tests Failing
```bash
# Ensure WebSocket server is running
# Check CORS settings
# Verify WebSocket URL
```

#### Frontend Tests Timing Out
```bash
# Increase timeout
# Check if dev server is running
# Verify API is accessible
```

---

**Remember:** Testing is an ongoing process. Update this guide as new features are added and new test scenarios are discovered.

