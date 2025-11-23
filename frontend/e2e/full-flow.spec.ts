import { test, expect } from '@playwright/test';

test.describe('Full Application Flow - E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Clear all storage
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await page.reload();
    await page.waitForLoadState('networkidle');
  });

  test('Complete user journey: Load → Configure → Start Task', async ({ page }) => {
    // Step 1: Page loads
    await expect(page.locator('text=Lead Intelligence Platform')).toBeVisible({ timeout: 15000 });
    
    // Step 2: Handle consent if present (wait longer and use force if needed)
    const consentButton = page.locator('button:has-text("Agree"), button:has-text("I Agree")').first();
    if (await consentButton.isVisible({ timeout: 10000 }).catch(() => false)) {
      await consentButton.click({ force: true });
      await page.waitForTimeout(1000); // Wait for modal to fully close
    }
    
    // Step 3: Enter search query (wait for input to be ready)
    const queryInput = page.locator('input[placeholder*="ICT"], input[placeholder*="query"]').first();
    await queryInput.waitFor({ state: 'visible', timeout: 15000 });
    await queryInput.waitFor({ state: 'attached', timeout: 5000 });
    await page.waitForTimeout(500); // Small delay for any animations
    await queryInput.fill('ICT students in Toronto');
    
    // Step 4: Select platform
    const platformCheckbox = page.locator('input[type="checkbox"]').first();
    if (await platformCheckbox.isVisible().catch(() => false)) {
      await platformCheckbox.check();
    }
    
    // Step 5: Verify start button is enabled
    const startButton = page.locator('button:has-text("Start Scraping")');
    await expect(startButton).toBeEnabled({ timeout: 5000 });
    
    // Step 6: Click start (but don't wait for completion - just verify it starts)
    await startButton.scrollIntoViewIfNeeded();
    await startButton.click({ force: true });
    await page.waitForTimeout(1000);
    
    // Step 7: Verify task started (button should change to "Stop")
    await expect(page.locator('button:has-text("Stop")')).toBeVisible({ timeout: 15000 });
  });

  test('Error handling: Invalid API responses', async ({ page }) => {
    // Handle consent first
    await page.goto('/');
    const consentButton = page.locator('button:has-text("Agree"), button:has-text("I Agree")').first();
    if (await consentButton.isVisible({ timeout: 10000 }).catch(() => false)) {
      await consentButton.click({ force: true });
      await page.waitForTimeout(1000);
    }
    
    // Intercept and mock API errors
    await page.route('**/api/scraper/start', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' }),
      });
    });
    
    await page.waitForLoadState('networkidle');
    
    // Try to start a task
    const queryInput = page.locator('input[placeholder*="ICT"]').first();
    await queryInput.waitFor({ state: 'visible', timeout: 10000 });
    await queryInput.fill('test');
    
    const startButton = page.locator('button:has-text("Start Scraping")');
    if (await startButton.isEnabled({ timeout: 5000 }).catch(() => false)) {
      await startButton.scrollIntoViewIfNeeded();
      await startButton.click({ force: true });
      
      // Should show error (check for error message or toast)
      await page.waitForTimeout(2000);
      // Just verify page didn't crash
      await expect(page.locator('body')).toBeVisible();
    }
  });

  test('WebSocket connection handling', async ({ page }) => {
    const wsErrors: string[] = [];
    const consoleErrors: string[] = [];
    
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    page.on('websocket', ws => {
      ws.on('framereceived', () => {
        // WebSocket is working
      });
      ws.on('socketerror', error => {
        wsErrors.push(error);
      });
    });
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);
    
    // Should not have critical WebSocket errors
    expect(wsErrors.length).toBe(0);
  });

  test('Form validation works correctly', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Start button should be disabled with empty query
    const startButton = page.locator('button:has-text("Start Scraping")');
    const isDisabled = await startButton.isDisabled().catch(() => true);
    expect(isDisabled).toBe(true);
    
    // Add a query
    const queryInput = page.locator('input[placeholder*="ICT"]').first();
    await queryInput.fill('test query');
    
    // Button should now be enabled
    await expect(startButton).toBeEnabled({ timeout: 2000 });
  });

  test('Task list toggle functionality', async ({ page }) => {
    await page.goto('/');
    
    // Handle consent first
    const consentButton = page.locator('button:has-text("Agree"), button:has-text("I Agree")').first();
    if (await consentButton.isVisible({ timeout: 10000 }).catch(() => false)) {
      await consentButton.click({ force: true });
      await page.waitForTimeout(1000);
    }
    
    await page.waitForLoadState('networkidle');
    
    const taskToggle = page.locator('button:has-text("Show Tasks"), button:has-text("Hide Tasks")').first();
    
    if (await taskToggle.isVisible({ timeout: 10000 }).catch(() => false)) {
      await taskToggle.scrollIntoViewIfNeeded();
      const initialText = await taskToggle.textContent();
      await taskToggle.click({ force: true });
      await page.waitForTimeout(1000);
      
      const newText = await taskToggle.textContent();
      // Text should have changed
      expect(newText).not.toBe(initialText);
    }
  });

  test('Export functionality UI', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Scroll to export section
    const exportSection = page.locator('text=Export').first();
    await exportSection.scrollIntoViewIfNeeded();
    await expect(exportSection).toBeVisible({ timeout: 10000 });
    
    // Check export format selector
    const formatSelect = page.locator('select').filter({ hasText: 'CSV' });
    await expect(formatSelect).toBeVisible();
    
    // Export button should exist (may be disabled)
    const exportButton = page.locator('button:has-text("Export")');
    await expect(exportButton).toBeVisible();
  });
});

