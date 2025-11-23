import { test, expect } from '@playwright/test';

test.describe('API Integration Tests', () => {
  const API_BASE = 'http://localhost:8000';

  test('Backend health check', async ({ request }) => {
    const response = await request.get(`${API_BASE}/health`);
    expect(response.ok()).toBeTruthy();
  });

  test('Get tasks endpoint', async ({ request }) => {
    const response = await request.get(`${API_BASE}/api/tasks`);
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(Array.isArray(data)).toBeTruthy();
  });

  test('Get platforms endpoint', async ({ request }) => {
    const response = await request.get(`${API_BASE}/api/filters/platforms`);
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(Array.isArray(data)).toBeTruthy();
  });

  test('Create task endpoint validation', async ({ request }) => {
    // Test with invalid data (should return 422)
    const response = await request.post(`${API_BASE}/api/scraper/start`, {
      data: {
        query: 'test', // Missing required 'queries' field
      },
      timeout: 10000, // 10 second timeout
    });
    
    // Should return validation error
    expect([400, 422]).toContain(response.status());
  });

  test('Create task with valid data', async ({ request }) => {
    const response = await request.post(`${API_BASE}/api/scraper/start`, {
      data: {
        queries: ['test query'],
        platforms: ['google_maps'],
        max_results: 1,
      },
      timeout: 10000, // 10 second timeout
    });
    
    // Should accept the request (may timeout, but should return 200/202)
    expect([200, 202, 408]).toContain(response.status());
  });
});

