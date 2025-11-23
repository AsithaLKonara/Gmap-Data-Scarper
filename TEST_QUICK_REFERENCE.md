# ⚡ Test Quick Reference

## 🚀 Quick Test Commands

### Frontend
```bash
npm test                    # Run all tests
npm test -- --watch        # Watch mode
npm test -- --coverage     # Coverage report
npm run test:e2e           # E2E tests
npm run lint              # Lint check
```

### Backend
```bash
pytest                     # Run all tests
pytest -v                  # Verbose
pytest --cov               # Coverage
pytest -k "scraper"        # Filter tests
pytest tests/test_api.py   # Specific file
```

---

## 🔍 Common Test Scenarios

### 1. User Registration
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}'
```

### 2. User Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}'
```

### 3. Start Scraping
```bash
curl -X POST http://localhost:8000/api/scraper/start \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"queries":["restaurants in Toronto"],"platforms":["google_maps"]}'
```

### 4. Get Task Status
```bash
curl http://localhost:8000/api/scraper/status/TASK_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Export CSV
```bash
curl http://localhost:8000/api/export/csv?task_id=TASK_ID \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o leads.csv
```

---

## 🧪 Test Data

### Valid Test User
```json
{
  "email": "test@example.com",
  "password": "SecurePass123!",
  "name": "Test User"
}
```

### Valid Scrape Request
```json
{
  "queries": ["restaurants in Toronto"],
  "platforms": ["google_maps", "yelp"],
  "lead_objective": "restaurants",
  "phone_only": false
}
```

### Expected Lead Response
```json
{
  "display_name": "Test Restaurant",
  "location": "Toronto, ON",
  "phones": [{
    "raw_phone": "+1234567890",
    "normalized_e164": "+1234567890",
    "confidence_score": 95
  }],
  "lead_score": 75,
  "lead_score_category": "warm"
}
```

---

## ✅ Quick Validation Checklist

### Before Each Test Session
- [ ] Test database is clean
- [ ] Test user exists
- [ ] API server is running
- [ ] Frontend dev server is running
- [ ] Environment variables are set

### After Each Test
- [ ] Clean up test data
- [ ] Reset database state
- [ ] Clear browser cache
- [ ] Check logs for errors

---

## 🐛 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Tests timeout | Increase timeout, check server |
| Database locked | Close connections, restart DB |
| WebSocket fails | Check CORS, verify URL |
| Auth fails | Check token expiration |
| Export fails | Verify task_id, check permissions |

---

## 📊 Test Coverage Goals

- **Unit Tests**: > 80%
- **Integration Tests**: > 70%
- **E2E Tests**: Critical paths only
- **API Tests**: 100% of endpoints

---

## 🎯 Priority Test Areas

1. **Authentication** - Login, Register, Token
2. **Scraping** - Start, Stop, Results
3. **Export** - CSV, JSON, Excel
4. **Lead Scoring** - Calculation, Display
5. **Search/Filter** - Functionality, Performance

---

## 📝 Test Report Template

```
Test: [Test Name]
Date: [Date]
Tester: [Name]
Status: [Pass/Fail]
Notes: [Any observations]
Bugs: [Bug IDs if any]
```

---

**Pro Tip:** Keep this file open while testing for quick reference!

