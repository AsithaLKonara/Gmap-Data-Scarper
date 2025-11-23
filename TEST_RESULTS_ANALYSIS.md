# Test Results Analysis

## Current Status
- **Pass Rate**: 64.75% (90/139 tests)
- **Categories Passed**: 21/36
- **Categories Failed**: 15

## Critical Issues

### 1. Missing `backend.config.pricing` Module (BLOCKING)
**Affected Categories:**
- Backend API - New Endpoints
- Integration - WebSocket
- E2E - Scraping Flow
- E2E - WebSocket Stability
- E2E - Concurrency
- E2E - Data Volume
- E2E - Deployment
- Backend - WebSocket

**Error**: `ModuleNotFoundError: No module named 'backend.config.pricing'`

### 2. E2E/Orchestrator Mock Path Issues
**Affected Categories:**
- Integration - E2E (3 errors)
- Integration - Orchestrator (5 errors)

**Error**: `AttributeError: module 'enrichment.activity_scraper' has no attribute 'requests'`
**Fix**: Should patch `scrapers.social_common.HttpClient.get` instead

### 3. PostgreSQL Duplicate Prevention
**Test**: `test_duplicate_prevention`
**Issue**: Expected 1 lead, got 2 (duplicate prevention not working)

### 4. Push Notifications Session Issue
**Test**: `test_subscribe_to_push_notifications`
**Error**: `DetachedInstanceError: Instance is not bound to a Session`

### 5. Google Maps Test
**Test**: `test_search_handles_single_place_page`
**Error**: `AttributeError: does not have the attribute '_enter_search_query'`

### 6. Performance Benchmarks
**Issue**: Server not running (ConnectionRefusedError)
**Fix**: Need to mock or skip if server not available

### 7. CLI Main
**Issue**: Timeout (exceeded 10 minutes)

