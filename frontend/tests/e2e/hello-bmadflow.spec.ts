import { test, expect } from '@playwright/test';

test.describe('Hello BMADFlow E2E Integration', () => {
  test('should display Hello BMADFlow message from backend API', async ({ page }) => {
    // Navigate to Dashboard (using FRONTEND_PORT from .env: 3002)
    await page.goto('http://localhost:3002');

    // Wait for API response to load - use specific text from API
    await page.waitForSelector('text=Hello BMADFlow');

    // Verify message from backend API displays (target main content, not sidebar)
    const heading = await page.locator('main h1').textContent();
    expect(heading).toContain('Hello BMADFlow');

    // Verify server timestamp is present (confirms API call succeeded)
    const timestamp = await page.locator('text=Server timestamp:').textContent();
    expect(timestamp).toContain('Server timestamp:');

    // Capture screenshot for validation
    await page.screenshot({ path: './tests/e2e/screenshots/hello-bmadflow.png', fullPage: true });
  });

  // TODO: Implement error handling test
  // test('should handle API error gracefully', async ({ page }) => {
  //   // Simulate backend down by navigating before starting backend
  //   // This test verifies error handling
  //   // For this test, we'd need to stop backend temporarily
  //   // Or mock the API to return error
  //   // For POC, this is optional - focus on happy path
  // });
});
