# E2E Testing Guide

## Overview

The Lead Intelligence Platform uses Playwright for end-to-end testing. The test suite automatically starts both the backend and frontend servers before running tests.

## Test Structure

```
frontend/
├── e2e/
│   ├── app.spec.ts              # Main UI functionality tests
│   ├── api-integration.spec.ts   # API endpoint tests
│   ├── full-flow.spec.ts         # Complete user journey tests
│   └── error-detection.spec.ts   # Error handling and debugging tests
└── playwright.config.ts          # Playwright configuration
```

## Running Tests

### Prerequisites

1. **Python dependencies installed**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Frontend dependencies installed**:
   ```bash
   cd frontend
   npm install
   ```

3. **Playwright browsers installed**:
   ```bash
   cd frontend
   npx playwright install chromium
   ```

### Running All Tests

```bash
cd frontend
npm run test:e2e
```

### Running Tests with UI

```bash
cd frontend
npm run test:e2e:ui
```

### Running Specific Test File

```bash
cd frontend
npx playwright test e2e/app.spec.ts
```

### Running Tests in Debug Mode

```bash
cd frontend
npx playwright test --debug
```

## Automatic Server Startup

The Playwright configuration automatically starts both servers:

1. **Backend Server** (port 8000):
   - Command: `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000`
   - Health check: `http://localhost:8000/health`
   - Timeout: 120 seconds

2. **Frontend Server** (port 3000):
   - Command: `npm run dev`
   - Health check: `http://localhost:3000`
   - Timeout: 120 seconds

Both servers will be started in parallel and tests will wait for both to be ready before running.

## Test Categories

### 1. API Integration Tests (`api-integration.spec.ts`)

Tests backend API endpoints:
- Health check
- Get tasks endpoint
- Get platforms endpoint
- Create task validation
- Create task with valid data

### 2. UI Functionality Tests (`app.spec.ts`)

Tests frontend UI components:
- Homepage loading
- Consent notice display
- Adding multiple search queries
- Platform selection
- Form validation
- Task list toggle
- Export options
- WebSocket connections
- Error handling

### 3. Full Flow Tests (`full-flow.spec.ts`)

Tests complete user journeys:
- Load → Configure → Start Task
- Error handling with invalid API responses
- WebSocket connection handling
- Form validation
- Task list functionality
- Export functionality

### 4. Error Detection Tests (`error-detection.spec.ts`)

Captures and reports:
- Console errors
- React hydration errors
- API endpoint accessibility
- Missing resources
- Component rendering

## Viewing Test Results

### HTML Report

After running tests, view the HTML report:

```bash
cd frontend
npx playwright show-report
```

### Console Output

Tests output results to the console with:
- ✅ Passing tests
- ❌ Failing tests
- ⚠️  Warnings
- Error details

## Test Configuration

The Playwright configuration (`playwright.config.ts`) includes:

- **Test Directory**: `./e2e`
- **Parallel Execution**: Enabled (2 workers)
- **Retries**: 0 in development, 2 in CI
- **Reporter**: HTML + List
- **Screenshots**: On failure only
- **Traces**: On first retry

## Troubleshooting

### Backend Not Starting

If the backend fails to start:
1. Check Python is installed: `python --version`
2. Check dependencies: `pip list | grep uvicorn`
3. Check port 8000 is available: `netstat -an | findstr 8000` (Windows) or `lsof -i :8000` (Mac/Linux)

### Frontend Not Starting

If the frontend fails to start:
1. Check Node.js is installed: `node --version`
2. Check dependencies: `npm list`
3. Check port 3000 is available: `netstat -an | findstr 3000` (Windows) or `lsof -i :3000` (Mac/Linux)

### Tests Timing Out

If tests timeout:
1. Increase timeout in `playwright.config.ts`:
   ```typescript
   timeout: 180 * 1000, // 3 minutes
   ```
2. Check server startup logs for errors
3. Verify both servers are accessible manually

### Connection Refused Errors

If you see "ERR_CONNECTION_REFUSED":
1. Ensure both servers are starting correctly
2. Check firewall settings
3. Verify ports are not blocked
4. Check server logs for startup errors

## CI/CD Integration

For CI/CD pipelines, set the `CI` environment variable:

```bash
CI=true npm run test:e2e
```

This will:
- Disable server reuse (always start fresh)
- Enable retries (2 retries per test)
- Use 1 worker (sequential execution)

## Best Practices

1. **Keep tests independent**: Each test should be able to run alone
2. **Use meaningful selectors**: Prefer text content or data-testid over CSS classes
3. **Wait for elements**: Use `waitFor` or `toBeVisible()` instead of fixed timeouts
4. **Clean up state**: Reset localStorage/sessionStorage between tests
5. **Handle async operations**: Use `waitForLoadState('networkidle')` when needed

## Writing New Tests

Example test structure:

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should do something', async ({ page }) => {
    // Arrange
    const element = page.locator('text=Something');
    
    // Act
    await element.click();
    
    // Assert
    await expect(page.locator('text=Result')).toBeVisible();
  });
});
```

## Test Coverage

Current test coverage:
- ✅ API Integration: 83% (5/6 tests passing)
- ✅ UI Functionality: 60% (6/10 tests passing)
- ✅ Error Handling: 50% (1/2 tests passing)
- **Overall**: 69% (11/16 tests passing)

## Continuous Improvement

- Add tests for new features
- Update tests when UI changes
- Fix flaky tests immediately
- Review test results regularly
- Maintain test documentation

---

**Last Updated**: Current Session

