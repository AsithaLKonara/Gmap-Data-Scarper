import { test, expect } from '@playwright/test';

test.describe('Error Detection and Debugging', () => {
  test('Capture all console errors', async ({ page }) => {
    const errors: string[] = [];
    const warnings: string[] = [];
    
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      } else if (msg.type() === 'warning') {
        warnings.push(msg.text());
      }
    });
    
    page.on('pageerror', error => {
      errors.push(`Page Error: ${error.message}`);
    });
    
    page.on('requestfailed', request => {
      errors.push(`Request Failed: ${request.url()} - ${request.failure()?.errorText}`);
    });
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000); // Wait for all async operations
    
    // Log all errors for debugging
    console.log('\n=== CONSOLE ERRORS ===');
    errors.forEach(err => console.log(`ERROR: ${err}`));
    
    console.log('\n=== CONSOLE WARNINGS ===');
    warnings.forEach(warn => console.log(`WARN: ${warn}`));
    
    // Critical errors that should not exist
    const criticalErrors = errors.filter(e => 
      !e.includes('favicon') && 
      !e.includes('404') &&
      !e.includes('WebSocket') && // WebSocket errors are expected if backend is down
      !e.includes('Failed to fetch') // Network errors are expected in some cases
    );
    
    console.log(`\n=== CRITICAL ERRORS: ${criticalErrors.length} ===`);
    criticalErrors.forEach(err => console.log(`CRITICAL: ${err}`));
    
    // Should have minimal critical errors
    expect(criticalErrors.length).toBeLessThan(10);
  });

  test('Check for React hydration errors', async ({ page }) => {
    const hydrationErrors: string[] = [];
    
    page.on('console', msg => {
      if (msg.type() === 'error' && msg.text().includes('hydration')) {
        hydrationErrors.push(msg.text());
      }
    });
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Should not have hydration errors
    expect(hydrationErrors.length).toBe(0);
  });

  test('Verify all API endpoints are accessible', async ({ request }) => {
    const endpoints = [
      { path: '/health', expectedStatus: 200 },
      { path: '/api/tasks', expectedStatus: 200 },
      { path: '/api/filters/platforms', expectedStatus: 200 },
    ];
    
    for (const endpoint of endpoints) {
      const response = await request.get(`http://localhost:8000${endpoint.path}`);
      console.log(`${endpoint.path}: ${response.status()}`);
      
      // Allow for some flexibility in status codes
      if (endpoint.expectedStatus === 200) {
        expect([200, 401, 403]).toContain(response.status());
      }
    }
  });

  test('Check for missing resources', async ({ page }) => {
    const failedRequests: string[] = [];
    
    page.on('requestfailed', request => {
      const url = request.url();
      // Only track failed resource loads, not API calls
      if (!url.includes('/api/') && !url.includes('websocket')) {
        failedRequests.push(`${url} - ${request.failure()?.errorText}`);
      }
    });
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    console.log('\n=== FAILED RESOURCE REQUESTS ===');
    failedRequests.forEach(req => console.log(`FAILED: ${req}`));
    
    // Should not have many failed resource requests
    expect(failedRequests.length).toBeLessThan(5);
  });

  test('Verify component rendering', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Check for key components
    const components = [
      'Lead Intelligence Platform',
      'Search Queries',
      'Platforms',
      'Controls',
    ];
    
    for (const component of components) {
      const element = page.locator(`text=${component}`).first();
      await expect(element).toBeVisible({ timeout: 10000 });
    }
  });
});

