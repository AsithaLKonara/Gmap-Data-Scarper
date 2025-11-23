# ❌ Failed Tests List (39 Total)

**Test Execution Date:** 2025-01-17  
**Total Failed:** 39 tests

---

## 📋 Complete List of Failed Tests

### 1. E2E Deployment Tests (11 failures)

#### API Health Tests
1. `tests/e2e/test_deployment.py::TestAPIHealth::test_root_endpoint`
   - **Error:** Connection refused - Backend not running

2. `tests/e2e/test_deployment.py::TestAPIHealth::test_health_endpoint`
   - **Error:** Connection refused - Backend not running

3. `tests/e2e/test_deployment.py::TestAPIHealth::test_metrics_endpoint`
   - **Error:** Connection refused - Backend not running

#### Scraping Workflow Tests
4. `tests/e2e/test_deployment.py::TestScrapingWorkflow::test_start_scraping_task`
   - **Error:** Connection refused - Backend not running

5. `tests/e2e/test_deployment.py::TestScrapingWorkflow::test_get_task_status`
   - **Error:** Connection refused - Backend not running

6. `tests/e2e/test_deployment.py::TestScrapingWorkflow::test_stop_task`
   - **Error:** Connection refused - Backend not running

7. `tests/e2e/test_deployment.py::TestScrapingWorkflow::test_list_tasks`
   - **Error:** Connection refused - Backend not running

#### Concurrency & Data Volume
8. `tests/e2e/test_deployment.py::TestConcurrency::test_multiple_concurrent_tasks`
   - **Error:** Connection refused - Backend not running

9. `tests/e2e/test_deployment.py::TestDataVolume::test_export_with_many_results`
   - **Error:** Connection refused - Backend not running

#### Error Recovery
10. `tests/e2e/test_deployment.py::TestErrorRecovery::test_invalid_task_id`
    - **Error:** Connection refused - Backend not running

11. `tests/e2e/test_deployment.py::TestErrorRecovery::test_invalid_request_data`
    - **Error:** Connection refused - Backend not running

---

### 2. E2E Scraping Flow Tests (3 failures)

12. `tests/e2e/test_scraping_flow.py::TestCompleteScrapingFlow::test_start_scrape_and_get_results`
    - **Error:** Connection refused - Backend not running

13. `tests/e2e/test_scraping_flow.py::TestCompleteScrapingFlow::test_pause_and_resume_workflow`
    - **Error:** Connection refused - Backend not running

14. `tests/e2e/test_scraping_flow.py::TestCompleteScrapingFlow::test_bulk_actions_workflow`
    - **Error:** Connection refused - Backend not running

---

### 3. E2E WebSocket Stability Tests (3 failures)

15. `tests/e2e/test_websocket_stability.py::TestWebSocketStability::test_websocket_logs_stream_stability`
    - **Error:** Connection refused - Backend not running

16. `tests/e2e/test_websocket_stability.py::TestWebSocketStability::test_websocket_progress_stream`
    - **Error:** Connection refused - Backend not running

17. `tests/e2e/test_websocket_stability.py::TestWebSocketStability::test_websocket_results_stream`
    - **Error:** Connection refused - Backend not running

---

### 4. E2E Data Volume Test (1 failure)

18. `tests/e2e/test_data_volume.py::TestDataVolume::test_error_recovery_scenarios`
    - **Error:** Rate limit exceeded (429) - Too many requests

---

### 5. Comprehensive API Tests (8 failures)

#### Scraper Endpoints
19. `tests/test_comprehensive_api.py::TestScraperEndpoints::test_start_scraper_empty_queries`
    - **Error:** Expected 400, got 422 (validation status code)

20. `tests/test_comprehensive_api.py::TestScraperEndpoints::test_start_scraper_invalid_platform`
    - **Error:** Expected 200 or 400, got 422 (validation status code)

#### AI Endpoints
21. `tests/test_comprehensive_api.py::TestAIEndpoints::test_generate_queries`
    - **Error:** Got 404 - Endpoint not found

#### Security Tests
22. `tests/test_comprehensive_api.py::TestSecurity::test_protected_endpoint_without_auth`
    - **Error:** Expected 401, got 404 - Endpoint not found

23. `tests/test_comprehensive_api.py::TestSecurity::test_protected_endpoint_with_invalid_token`
    - **Error:** Expected 401, got 404 - Endpoint not found

24. `tests/test_comprehensive_api.py::TestSecurity::test_sql_injection_prevention`
    - **Error:** Rate limit exceeded (429)

25. `tests/test_comprehensive_api.py::TestSecurity::test_xss_prevention`
    - **Error:** Rate limit exceeded (429)

#### Additional
26. `tests/test_comprehensive_api.py::TestScraperEndpoints::test_stop_scraper`
    - **Error:** Rate limit exceeded (429)

---

### 6. New Endpoints Tests (14 failures)

#### Teams API
27. `tests/test_new_endpoints.py::TestTeamsAPI::test_create_team`
    - **Error:** Expected 200, got 401 - Missing authentication

28. `tests/test_new_endpoints.py::TestTeamsAPI::test_list_teams`
    - **Error:** Expected 200, got 401 - Missing authentication

#### Analytics API
29. `tests/test_new_endpoints.py::TestAnalyticsAPI::test_dashboard_metrics`
    - **Error:** Expected 200, got 401 - Missing authentication

30. `tests/test_new_endpoints.py::TestAnalyticsAPI::test_pipeline_metrics`
    - **Error:** Expected 200, got 401 - Missing authentication

31. `tests/test_new_endpoints.py::TestAnalyticsAPI::test_forecast`
    - **Error:** Expected 200, got 401 - Missing authentication

#### Predictive API
32. `tests/test_new_endpoints.py::TestPredictiveAPI::test_conversion_prediction`
    - **Error:** Expected 200, got 401 - Missing authentication

33. `tests/test_new_endpoints.py::TestPredictiveAPI::test_churn_prediction`
    - **Error:** Expected 200, got 401 - Missing authentication

34. `tests/test_new_endpoints.py::TestPredictiveAPI::test_sentiment_analysis`
    - **Error:** Expected 200, got 401 - Missing authentication

35. `tests/test_new_endpoints.py::TestPredictiveAPI::test_intent_detection`
    - **Error:** Expected 200, got 401 - Missing authentication

#### Reports API
36. `tests/test_new_endpoints.py::TestReportsAPI::test_build_report`
    - **Error:** Expected 200, got 401 - Missing authentication

37. `tests/test_new_endpoints.py::TestReportsAPI::test_create_scheduled_report`
    - **Error:** Expected 200, got 401 - Missing authentication

#### Workflows API
38. `tests/test_new_endpoints.py::TestWorkflowsAPI::test_create_workflow`
    - **Error:** Expected 200, got 401 - Missing authentication

#### Branding API
39. `tests/test_new_endpoints.py::TestBrandingAPI::test_get_branding`
    - **Error:** Expected 200, got 401 - Missing authentication

---

## 📊 Failure Summary by Category

| Category | Count | Primary Issue |
|----------|-------|---------------|
| **Backend Not Running** | 20 | Connection refused errors |
| **Missing Authentication** | 14 | Tests need JWT tokens |
| **Rate Limiting** | 4 | Rate limit exceeded (429) |
| **Validation Status Codes** | 2 | Expected 400, got 422 |
| **Endpoint Not Found** | 2 | Got 404 instead of expected status |
| **Total** | **39** | |

---

## 🔧 Quick Fix Summary

1. **Start Backend** → Fixes 20 tests
2. **Add Auth Tokens** → Fixes 14 tests
3. **Fix Rate Limiting** → Fixes 4 tests
4. **Update Status Codes** → Fixes 2 tests
5. **Fix Endpoints** → Fixes 2 tests

**Total Fixable:** 39 tests → **Expected Pass Rate: 95%+**

