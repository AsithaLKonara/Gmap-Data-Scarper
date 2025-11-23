# Detailed Test Cases - Lead Intelligence Platform

**QA Document**  
**Version:** 1.0  
**Date:** 2025-01-17

---

## Test Case Index

### Functional Test Cases
- [Scraping Functionality](#scraping-functionality)
- [Phone Extraction](#phone-extraction)
- [Authentication & Authorization](#authentication--authorization)
- [Data Export](#data-export)
- [Analytics](#analytics)
- [GDPR Compliance](#gdpr-compliance)
- [WebSocket Real-Time](#websocket-real-time)

### Non-Functional Test Cases
- [Performance](#performance)
- [Security](#security)
- [Error Handling](#error-handling)
- [Browser Compatibility](#browser-compatibility)

---

## Scraping Functionality

### TC-SCRAPE-001: Start Scraping Task - Valid Input
**Priority:** High  
**Type:** Integration  
**Prerequisites:** Backend running, authenticated user

**Test Steps:**
1. Authenticate and get access token
2. POST `/api/scraper/start` with:
   ```json
   {
     "queries": ["restaurants in Toronto"],
     "platforms": ["google_maps"],
     "max_results": 10,
     "headless": true
   }
   ```
3. Verify response status 200
4. Verify response contains `task_id`
5. Verify response contains `status: "started"`
6. Query task status endpoint
7. Verify task exists and is running

**Expected Result:** Task created and started successfully

**Pass Criteria:**
- Status code 200
- Valid task_id returned
- Task status is "started"
- Task appears in task list

---

### TC-SCRAPE-002: Start Scraping - Invalid Platform
**Priority:** High  
**Type:** Integration

**Test Steps:**
1. POST `/api/scraper/start` with invalid platform:
   ```json
   {
     "queries": ["test"],
     "platforms": ["invalid_platform"]
   }
   ```
2. Verify response status 422

**Expected Result:** Validation error returned

**Pass Criteria:**
- Status code 422 (Unprocessable Entity)
- Error message indicates invalid platform

---

### TC-SCRAPE-003: Start Scraping - Empty Queries
**Priority:** High  
**Type:** Integration

**Test Steps:**
1. POST `/api/scraper/start` with empty queries array:
   ```json
   {
     "queries": [],
     "platforms": ["google_maps"]
   }
   ```
2. Verify response status 422

**Expected Result:** Validation error returned

**Pass Criteria:**
- Status code 422
- Error message indicates queries required

---

### TC-SCRAPE-004: Pause Task
**Priority:** Medium  
**Type:** Integration

**Test Steps:**
1. Start a scraping task
2. Wait for task to be running
3. POST `/api/scraper/pause/{task_id}`
4. Verify response status 200
5. Get task status
6. Verify status is "paused"

**Expected Result:** Task paused successfully

**Pass Criteria:**
- Pause endpoint returns 200
- Task status changes to "paused"
- Task can be resumed later

---

### TC-SCRAPE-005: Resume Task
**Priority:** Medium  
**Type:** Integration

**Test Steps:**
1. Start and pause a task
2. POST `/api/scraper/resume/{task_id}`
3. Verify response status 200
4. Get task status
5. Verify status is "running"

**Expected Result:** Task resumed successfully

**Pass Criteria:**
- Resume endpoint returns 200
- Task status changes to "running"
- Task continues from where it paused

---

### TC-SCRAPE-006: Stop Task
**Priority:** High  
**Type:** Integration

**Test Steps:**
1. Start a scraping task
2. POST `/api/scraper/stop/{task_id}`
3. Verify response status 200
4. Get task status
5. Verify status is "stopped"
6. Verify Chrome processes cleaned up

**Expected Result:** Task stopped and resources released

**Pass Criteria:**
- Stop endpoint returns 200
- Task status is "stopped"
- No orphaned Chrome processes
- Ports released

---

### TC-SCRAPE-007: Multi-Platform Scraping
**Priority:** High  
**Type:** Integration

**Test Steps:**
1. Start task with multiple platforms:
   ```json
   {
     "queries": ["restaurants"],
     "platforms": ["google_maps", "facebook", "instagram"],
     "max_results": 5
   }
   ```
2. Monitor task progress
3. Verify results from all platforms
4. Verify CSV files created for each platform

**Expected Result:** All platforms scraped successfully

**Pass Criteria:**
- Task completes successfully
- Results from all platforms present
- CSV files created correctly

---

## Phone Extraction

### TC-PHONE-001: Extract from tel: Link
**Priority:** High  
**Type:** Unit

**Test Steps:**
1. Create HTML with tel: link:
   ```html
   <a href="tel:+1234567890">Call Us</a>
   ```
2. Run phone extractor
3. Verify phone extracted: `+1234567890`
4. Verify confidence: 95%
5. Verify source: "tel_link"

**Expected Result:** Phone extracted with high confidence

**Pass Criteria:**
- Phone number extracted correctly
- Confidence ≥ 95%
- Source identified correctly

---

### TC-PHONE-002: Extract from JSON-LD
**Priority:** High  
**Type:** Unit

**Test Steps:**
1. Create HTML with JSON-LD:
   ```html
   <script type="application/ld+json">
   {
     "@type": "LocalBusiness",
     "telephone": "+1-234-567-8900"
   }
   </script>
   ```
2. Run phone extractor
3. Verify phone extracted
4. Verify confidence: 90%
5. Verify source: "json_ld"

**Expected Result:** Phone extracted from structured data

**Pass Criteria:**
- Phone extracted correctly
- Confidence ≥ 90%
- Normalized to E.164 format

---

### TC-PHONE-003: Extract from Visible Text
**Priority:** Medium  
**Type:** Unit

**Test Steps:**
1. Create HTML with visible phone:
   ```html
   <p>Call us at (234) 567-8900</p>
   ```
2. Run phone extractor
3. Verify phone extracted
4. Verify confidence: 70%
5. Verify normalized format

**Expected Result:** Phone extracted from text

**Pass Criteria:**
- Phone extracted correctly
- Confidence ≥ 70%
- Normalized format

---

### TC-PHONE-004: Extract from Website Crawl
**Priority:** Medium  
**Type:** Integration

**Test Steps:**
1. Provide profile with website URL
2. Run phone extractor (will crawl website)
3. Verify phone extracted from contact page
4. Verify confidence: 60%
5. Verify source: "website_crawl"

**Expected Result:** Phone found by crawling website

**Pass Criteria:**
- Phone extracted from website
- Confidence ≥ 60%
- Website crawled successfully

---

### TC-PHONE-005: Extract using OCR
**Priority:** Low  
**Type:** Integration  
**Prerequisites:** Tesseract OCR installed

**Test Steps:**
1. Provide screenshot/image with phone number
2. Run OCR extraction
3. Verify phone extracted
4. Verify confidence: 50%
5. Verify source: "ocr"

**Expected Result:** Phone extracted from image

**Pass Criteria:**
- Phone extracted from image
- Confidence ≥ 50%
- OCR processing successful

---

### TC-PHONE-006: Phone Deduplication
**Priority:** Medium  
**Type:** Unit

**Test Steps:**
1. Extract phones from same source:
   - `+1234567890`
   - `(123) 456-7890`
   - `123-456-7890`
2. Verify all normalized to same E.164 format
3. Verify only one phone in results (deduplicated)

**Expected Result:** Duplicate phones removed

**Pass Criteria:**
- All formats normalized to same number
- Only one phone in results
- Deduplication works correctly

---

## Authentication & Authorization

### TC-AUTH-001: User Registration
**Priority:** High  
**Type:** Integration

**Test Steps:**
1. POST `/api/auth/register` with:
   ```json
   {
     "email": "newuser@example.com",
     "password": "SecurePass123!",
     "name": "New User"
   }
   ```
2. Verify response status 200/201
3. Verify `access_token` returned
4. Verify `refresh_token` returned
5. Verify user created in database
6. Verify password hashed (not plain text)

**Expected Result:** User registered successfully

**Pass Criteria:**
- Status 200/201
- Tokens returned
- User in database
- Password hashed

---

### TC-AUTH-002: User Login - Valid Credentials
**Priority:** High  
**Type:** Integration

**Test Steps:**
1. Register a user
2. POST `/api/auth/login` with valid credentials
3. Verify response status 200
4. Verify `access_token` returned
5. Verify `refresh_token` returned
6. Use token to access protected endpoint
7. Verify access granted

**Expected Result:** Login successful, token works

**Pass Criteria:**
- Status 200
- Tokens returned
- Token valid for protected endpoints

---

### TC-AUTH-003: User Login - Invalid Credentials
**Priority:** High  
**Type:** Integration

**Test Steps:**
1. POST `/api/auth/login` with invalid password
2. Verify response status 401
3. Verify no tokens returned
4. Verify error message appropriate

**Expected Result:** Login rejected

**Pass Criteria:**
- Status 401
- No tokens returned
- Error message clear

---

### TC-AUTH-004: Token Refresh
**Priority:** Medium  
**Type:** Integration

**Test Steps:**
1. Login and get refresh_token
2. POST `/api/auth/refresh` with refresh_token
3. Verify new access_token returned
4. Verify new token works
5. Verify old access_token still works (until expiry)

**Expected Result:** Token refreshed successfully

**Pass Criteria:**
- New access_token returned
- New token works
- Refresh mechanism functional

---

### TC-AUTH-005: Token Blacklist on Logout
**Priority:** High  
**Type:** Integration

**Test Steps:**
1. Login and get access_token
2. Use token to access protected endpoint (verify works)
3. POST `/api/auth/logout` with token
4. Try to use same token for protected endpoint
5. Verify response status 401
6. Verify token in blacklist

**Expected Result:** Token blacklisted after logout

**Pass Criteria:**
- Logout successful
- Token blacklisted
- Token rejected after logout

---

### TC-AUTH-006: Protected Endpoint - No Token
**Priority:** High  
**Type:** Integration

**Test Steps:**
1. GET `/api/teams/` without Authorization header
2. Verify response status 401
3. Verify error message indicates authentication required

**Expected Result:** Access denied

**Pass Criteria:**
- Status 401
- Clear error message

---

### TC-AUTH-007: Protected Endpoint - Invalid Token
**Priority:** High  
**Type:** Integration

**Test Steps:**
1. GET `/api/teams/` with invalid token:
   ```
   Authorization: Bearer invalid_token_123
   ```
2. Verify response status 401
3. Verify error message indicates invalid token

**Expected Result:** Access denied

**Pass Criteria:**
- Status 401
- Error message clear

---

## Data Export

### TC-EXPORT-001: Export CSV - All Data
**Priority:** High  
**Type:** Integration

**Test Steps:**
1. Create test data (multiple leads)
2. GET `/api/export/csv`
3. Verify response status 200
4. Verify Content-Type: `text/csv`
5. Verify CSV contains all leads
6. Verify CSV format correct
7. Verify all expected columns present

**Expected Result:** CSV export successful

**Pass Criteria:**
- Status 200
- Valid CSV format
- All data present
- All columns present

---

### TC-EXPORT-002: Export CSV - Task Specific
**Priority:** Medium  
**Type:** Integration

**Test Steps:**
1. Create task and collect leads
2. GET `/api/export/csv?task_id={task_id}`
3. Verify only leads from that task exported
4. Verify CSV format correct

**Expected Result:** Task-specific export works

**Pass Criteria:**
- Only task-specific data exported
- Format correct

---

### TC-EXPORT-003: Export JSON
**Priority:** Medium  
**Type:** Integration

**Test Steps:**
1. GET `/api/export/json`
2. Verify response status 200
3. Verify Content-Type: `application/json`
4. Verify valid JSON
5. Verify all data present

**Expected Result:** JSON export successful

**Pass Criteria:**
- Status 200
- Valid JSON
- All data present

---

### TC-EXPORT-004: Export Excel
**Priority:** Low  
**Type:** Integration

**Test Steps:**
1. GET `/api/export/excel`
2. Verify response status 200
3. Verify Content-Type: Excel MIME type
4. Verify file can be opened in Excel
5. Verify all data present

**Expected Result:** Excel export successful

**Pass Criteria:**
- Status 200
- Valid Excel file
- Opens in Excel
- All data present

---

## Analytics

### TC-ANALYTICS-001: Dashboard Metrics
**Priority:** Medium  
**Type:** Integration

**Test Steps:**
1. Create test data (leads from multiple platforms)
2. GET `/api/analytics/dashboard?date_range_days=30`
3. Verify response status 200
4. Verify `total_leads` present
5. Verify `platform_breakdown` present
6. Verify `category_breakdown` present
7. Verify numbers match actual data

**Expected Result:** Dashboard metrics accurate

**Pass Criteria:**
- Status 200
- All metrics present
- Numbers accurate

---

### TC-ANALYTICS-002: Timeline Data
**Priority:** Medium  
**Type:** Integration

**Test Steps:**
1. GET `/api/analytics/timeline?period=weekly`
2. Verify response status 200
3. Verify timeline data structure
4. Verify data points for each week
5. Verify trends calculated correctly

**Expected Result:** Timeline data accurate

**Pass Criteria:**
- Status 200
- Timeline structure correct
- Data points accurate

---

## GDPR Compliance

### TC-GDPR-001: Data Access Request
**Priority:** High  
**Type:** Integration

**Test Steps:**
1. Create test data with email
2. POST `/api/legal/data-access-request`:
   ```json
   {
     "email": "user@example.com",
     "profile_url": null
   }
   ```
3. Verify response status 200
4. Verify `request_id` returned
5. Verify request stored in database
6. Verify status is "pending"
7. GET `/api/legal/data-requests`
8. Verify request appears in list

**Expected Result:** Request tracked properly

**Pass Criteria:**
- Request created
- Request_id returned
- Request in database
- Request appears in admin list

---

### TC-GDPR-002: Email-Based Data Deletion
**Priority:** High  
**Type:** Integration

**Test Steps:**
1. Create test data with email `test@example.com`:
   - Database records
   - CSV file entries
2. POST `/api/legal/data-deletion-request`:
   ```json
   {
     "email": "test@example.com"
   }
   ```
3. Verify response status 200
4. Verify `removed_count` > 0
5. Verify data deleted from database
6. Verify data removed from CSV files
7. Verify request status is "completed"

**Expected Result:** All data deleted

**Pass Criteria:**
- Data deleted from database
- Data removed from CSV files
- Request completed
- No data remains for email

---

### TC-GDPR-003: URL-Based Data Deletion
**Priority:** High  
**Type:** Integration

**Test Steps:**
1. Create test data with profile URL
2. POST `/api/legal/data-deletion-request`:
   ```json
   {
     "email": "user@example.com",
     "profile_url": "https://example.com/profile"
   }
   ```
3. Verify response status 200
4. Verify `removed_count` > 0
5. Verify data removed from CSV files
6. Verify request completed

**Expected Result:** Data deleted by URL

**Pass Criteria:**
- Data removed from files
- Request completed
- Correct count returned

---

### TC-GDPR-004: Data Request Tracking
**Priority:** Medium  
**Type:** Integration

**Test Steps:**
1. Create multiple data requests (access and deletion)
2. GET `/api/legal/data-requests`
3. Verify all requests returned
4. Verify correct status for each
5. Verify filtering by status works

**Expected Result:** All requests tracked

**Pass Criteria:**
- All requests returned
- Status correct
- Filtering works

---

## WebSocket Real-Time

### TC-WS-001: Logs WebSocket Connection
**Priority:** High  
**Type:** Integration

**Test Steps:**
1. Start a scraping task
2. Connect to `/ws/logs/{task_id}`
3. Verify connection established
4. Verify initial connection message received
5. Monitor for log messages
6. Verify messages received during scraping
7. Close connection
8. Verify cleanup successful

**Expected Result:** WebSocket connection stable

**Pass Criteria:**
- Connection established
- Messages received
- Connection stable
- Cleanup successful

---

### TC-WS-002: Progress WebSocket Stream
**Priority:** High  
**Type:** Integration

**Test Steps:**
1. Start a scraping task
2. Connect to `/ws/progress/{task_id}`
3. Verify connection established
4. Monitor for progress updates
5. Verify progress updates received
6. Verify progress counts accurate

**Expected Result:** Progress updates streamed

**Pass Criteria:**
- Connection established
- Progress updates received
- Counts accurate

---

### TC-WS-003: Results WebSocket Stream
**Priority:** High  
**Type:** Integration

**Test Steps:**
1. Start a scraping task
2. Connect to `/ws/results/{task_id}`
3. Verify connection established
4. Monitor for result messages
5. Verify results received as they're extracted
6. Verify result data structure correct

**Expected Result:** Results streamed in real-time

**Pass Criteria:**
- Connection established
- Results received
- Data structure correct

---

### TC-WS-004: WebSocket Reconnection
**Priority:** Medium  
**Type:** Integration

**Test Steps:**
1. Connect to WebSocket
2. Simulate network interruption
3. Reconnect
4. Verify connection re-established
5. Verify state recovery (if applicable)

**Expected Result:** Reconnection works

**Pass Criteria:**
- Reconnection successful
- State recovered (if applicable)

---

## Performance

### TC-PERF-001: API Response Time
**Priority:** Medium  
**Type:** Performance

**Test Steps:**
1. Measure response time for `/api/health`
2. Measure response time for `/api/scraper/start`
3. Measure response time for `/api/export/csv`
4. Verify all < 2 seconds (except export)
5. Export can take longer for large datasets

**Expected Result:** Response times acceptable

**Pass Criteria:**
- Health: < 100ms
- Start task: < 2s
- Export: < 10s for 1000 records

---

### TC-PERF-002: Concurrent Tasks
**Priority:** High  
**Type:** Performance

**Test Steps:**
1. Start 10 concurrent scraping tasks
2. Monitor resource usage
3. Verify all tasks complete
4. Verify no resource leaks
5. Verify Chrome pool handles load

**Expected Result:** System handles concurrency

**Pass Criteria:**
- All tasks complete
- No crashes
- Resources released
- Pool management works

---

### TC-PERF-003: Large Dataset Export
**Priority:** Medium  
**Type:** Performance

**Test Steps:**
1. Create 10,000 test leads
2. Export to CSV
3. Measure export time
4. Verify export completes
5. Verify CSV file valid

**Expected Result:** Large exports work

**Pass Criteria:**
- Export completes
- File valid
- Time acceptable (< 60s)

---

## Security

### TC-SEC-001: SQL Injection Prevention
**Priority:** High  
**Type:** Security

**Test Steps:**
1. POST `/api/scraper/start` with malicious query:
   ```json
   {
     "queries": ["'; DROP TABLE leads; --"],
     "platforms": ["google_maps"]
   }
   ```
2. Verify request handled safely
3. Verify no SQL executed
4. Verify database intact

**Expected Result:** SQL injection prevented

**Pass Criteria:**
- Request rejected or sanitized
- No SQL executed
- Database safe

---

### TC-SEC-002: XSS Prevention
**Priority:** High  
**Type:** Security

**Test Steps:**
1. POST `/api/scraper/start` with XSS payload:
   ```json
   {
     "queries": ["<script>alert('XSS')</script>"],
     "platforms": ["google_maps"]
   }
   ```
2. Verify input sanitized
3. Verify no script execution
4. Verify data stored safely

**Expected Result:** XSS prevented

**Pass Criteria:**
- Input sanitized
- No script execution
- Data safe

---

### TC-SEC-003: Rate Limiting
**Priority:** Medium  
**Type:** Security

**Test Steps:**
1. Make 20 rapid requests to `/api/scraper/start`
2. Verify rate limit enforced (429 after limit)
3. Verify rate limit headers present
4. Wait for window to reset
5. Verify requests allowed again

**Expected Result:** Rate limiting works

**Pass Criteria:**
- Rate limit enforced
- 429 returned after limit
- Headers present
- Reset works

---

### TC-SEC-004: CORS Configuration
**Priority:** Medium  
**Type:** Security

**Test Steps:**
1. Make cross-origin request
2. Verify CORS headers present
3. Verify allowed origins correct
4. Verify credentials handling

**Expected Result:** CORS configured correctly

**Pass Criteria:**
- CORS headers present
- Origins correct
- Credentials handled

---

## Error Handling

### TC-ERR-001: Invalid Task ID
**Priority:** Medium  
**Type:** Integration

**Test Steps:**
1. GET `/api/scraper/status/invalid-task-id`
2. Verify response status 404
3. Verify error message clear

**Expected Result:** Proper error handling

**Pass Criteria:**
- Status 404
- Error message clear

---

### TC-ERR-002: Network Error Recovery
**Priority:** Medium  
**Type:** Integration

**Test Steps:**
1. Start scraping task
2. Simulate network interruption
3. Verify task handles error gracefully
4. Verify retry logic works
5. Verify task recovers or fails cleanly

**Expected Result:** Error recovery works

**Pass Criteria:**
- Error handled gracefully
- Retry logic works
- Clean failure if needed

---

### TC-ERR-003: Chrome Process Cleanup
**Priority:** High  
**Type:** Integration

**Test Steps:**
1. Start multiple tasks
2. Stop tasks abruptly
3. Verify Chrome processes cleaned up
4. Verify ports released
5. Verify no orphaned processes

**Expected Result:** Cleanup works

**Pass Criteria:**
- Processes cleaned up
- Ports released
- No orphans

---

## Browser Compatibility

### TC-BROWSER-001: Chrome Compatibility
**Priority:** High  
**Type:** E2E

**Test Steps:**
1. Test scraping in Chrome
2. Verify all features work
3. Verify UI displays correctly
4. Verify WebSocket works

**Expected Result:** Chrome fully supported

**Pass Criteria:**
- All features work
- UI correct
- WebSocket works

---

### TC-BROWSER-002: Frontend Responsiveness
**Priority:** Medium  
**Type:** E2E

**Test Steps:**
1. Test on desktop (1920x1080)
2. Test on tablet (768x1024)
3. Test on mobile (375x667)
4. Verify UI responsive
5. Verify functionality works on all sizes

**Expected Result:** Responsive design works

**Pass Criteria:**
- UI responsive
- Functionality works
- No layout breaks

---

## Test Execution Summary

### Test Case Count:
- **Total Test Cases:** 50+
- **High Priority:** 25
- **Medium Priority:** 20
- **Low Priority:** 5

### Coverage:
- **Functional:** 35 test cases
- **Non-Functional:** 15 test cases

### Status:
- **Automated:** 40+ test cases
- **Manual:** 10+ test cases
- **Pending:** All need execution

---

**Next:** Execute test cases and track results in test management system.

