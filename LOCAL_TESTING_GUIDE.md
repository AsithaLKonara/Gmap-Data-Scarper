# Local Testing Guide

## Run All Tests Locally - Automatic Server Management

This guide shows you how to run **all tests locally** without manually starting the server.

---

## Quick Start

### Run All Tests (Recommended)
```bash
python run_tests_local.py
```

This will:
1. ✅ Automatically start backend server
2. ✅ Run all pytest tests
3. ✅ Run E2E user journey test
4. ✅ Run QA comprehensive test
5. ✅ Automatically stop server

**That's it!** Everything runs locally with zero manual setup.

---

## Options

### Run Only Pytest Tests
```bash
python run_tests_local.py --pytest-only
```

### Run Only E2E Test
```bash
python run_tests_local.py --e2e-only
```

### Run Only QA Test
```bash
python run_tests_local.py --qa-only
```

### Skip E2E Test
```bash
python run_tests_local.py --no-e2e
```

### Skip QA Test
```bash
python run_tests_local.py --no-qa
```

### Skip Both E2E and QA
```bash
python run_tests_local.py --no-e2e --no-qa
```

---

## How It Works

### Automatic Server Management

The `run_tests_local.py` script:

1. **Checks if server is running**
   - If running, uses existing server
   - If not, starts new server automatically

2. **Starts server in background**
   - Uses subprocess to start uvicorn
   - Waits for server to be ready (health check)
   - Times out after 30 seconds if server doesn't start

3. **Runs all tests**
   - Sets `API_URL` environment variable
   - Runs pytest, E2E, and QA tests
   - All tests use the running server

4. **Stops server automatically**
   - Cleans up server process
   - Handles Windows and Unix differences

---

## What Gets Tested

### 1. Pytest Test Suite
- ✅ Unit tests
- ✅ Integration tests
- ✅ Platform scraper tests
- ✅ Phone extraction tests
- ✅ WebSocket tests (now work with server!)
- ✅ All other pytest tests

### 2. E2E User Journey Test
- ✅ 17-step complete user journey
- ✅ Authentication flow
- ✅ Scraping workflow
- ✅ Data management
- ✅ Analytics

### 3. QA Comprehensive Test
- ✅ QA Tester perspective
- ✅ Lead Collector User perspective
- ✅ Admin perspective

---

## Troubleshooting

### Server Won't Start

**Issue:** Server fails to start automatically

**Solutions:**
1. Check if port 8000 is already in use:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Linux/Mac
   lsof -i :8000
   ```

2. Kill existing process if needed:
   ```bash
   # Windows
   taskkill /F /PID <pid>
   
   # Linux/Mac
   kill <pid>
   ```

3. Start server manually, then run tests:
   ```bash
   # Terminal 1
   python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   
   # Terminal 2
   python run_tests_local.py
   ```

### Tests Timeout

**Issue:** Tests timeout waiting for server

**Solutions:**
1. Increase timeout in `run_tests_local.py`:
   ```python
   SERVER_START_TIMEOUT = 60  # Increase from 30
   ```

2. Check server logs for errors
3. Verify database is accessible

### Permission Errors

**Issue:** Permission denied errors on Windows

**Solutions:**
1. Run as administrator (if needed)
2. Check temp directory permissions
3. Some tests may skip gracefully (expected)

---

## Comparison: Manual vs Automatic

### Manual Method (Old Way)
```bash
# Terminal 1: Start server manually
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Run tests
pytest tests/ -v
python test_e2e_user_journey.py
python test_qa_comprehensive.py

# Terminal 1: Stop server manually (Ctrl+C)
```

**Issues:**
- ❌ Need 2 terminals
- ❌ Manual server management
- ❌ Easy to forget to start/stop server
- ❌ WebSocket tests fail without server

### Automatic Method (New Way)
```bash
# Single command
python run_tests_local.py
```

**Benefits:**
- ✅ Single command
- ✅ Automatic server management
- ✅ No manual setup needed
- ✅ All tests work (including WebSocket)

---

## Environment Variables

The test runner automatically sets:
- `API_URL=http://localhost:8000`
- `TESTING=true`

You can override these:
```bash
export API_URL=http://localhost:8000
export TESTING=true
python run_tests_local.py
```

---

## Test Execution Flow

```
┌─────────────────────────────────┐
│  run_tests_local.py             │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Check if server running        │
└──────────────┬──────────────────┘
               │
        ┌──────┴──────┐
        │             │
        ▼             ▼
    Running?      Not Running?
        │             │
        │             ▼
        │      Start Server
        │             │
        │             ▼
        │      Wait for Health
        │             │
        └──────┬──────┘
               │
               ▼
┌─────────────────────────────────┐
│  Run Pytest Tests               │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Run E2E Test                   │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Run QA Test                     │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Stop Server                     │
└─────────────────────────────────┘
```

---

## Examples

### Example 1: Full Test Run
```bash
$ python run_tests_local.py

================================================================================
LOCAL TEST RUNNER - ALL TESTS
================================================================================
This will:
  1. Start backend server automatically
  2. Run all pytest tests
  3. Run E2E user journey test
  4. Run QA comprehensive test
  5. Stop server automatically
================================================================================

================================================================================
STARTING BACKEND SERVER FOR TESTS
================================================================================
Waiting for server to start...
✅ Server started successfully at http://localhost:8000

================================================================================
RUNNING PYTEST TEST SUITE
================================================================================
...
[test output]
...

================================================================================
RUNNING E2E USER JOURNEY TEST
================================================================================
...
[test output]
...

================================================================================
TEST SUMMARY
================================================================================
Duration: 1234.56 seconds
Pytest: ✅ PASSED
E2E: ✅ PASSED
QA: ✅ PASSED
================================================================================
```

### Example 2: Pytest Only
```bash
$ python run_tests_local.py --pytest-only

================================================================================
STARTING BACKEND SERVER FOR TESTS
================================================================================
✅ Server started successfully at http://localhost:8000

================================================================================
RUNNING PYTEST TEST SUITE
================================================================================
...
[test output]
...
```

---

## Benefits

### ✅ Zero Manual Setup
- No need to start server manually
- No need to manage multiple terminals
- Everything happens automatically

### ✅ All Tests Work
- WebSocket tests work (server running)
- E2E tests work (server running)
- QA tests work (server running)

### ✅ Reliable
- Server starts reliably
- Health checks ensure server is ready
- Automatic cleanup on exit

### ✅ Flexible
- Run all tests or specific subsets
- Skip tests you don't need
- Works with existing server if running

---

## Next Steps

1. **Try it now:**
   ```bash
   python run_tests_local.py
   ```

2. **Check results:**
   - Review test output
   - Check for any failures
   - Review test reports

3. **Integrate into workflow:**
   - Add to CI/CD
   - Run before commits
   - Schedule regular runs

---

## Support

If you encounter issues:

1. Check server logs
2. Verify port 8000 is available
3. Check database connectivity
4. Review test output for errors

**All tests can now run locally with a single command!** 🎉

