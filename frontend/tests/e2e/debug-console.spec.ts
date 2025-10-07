import { test } from '@playwright/test';

test('check console errors', async ({ page }) => {
  const TEST_PROJECT_ID = '49d4acff-e89d-4149-ae7f-331d39ccb75f';

  // Listen for console messages
  page.on('console', msg => {
    console.log(`[BROWSER ${msg.type().toUpperCase()}]:`, msg.text());
  });

  // Listen for page errors
  page.on('pageerror', error => {
    console.log('[PAGE ERROR]:', error.message);
  });

  await page.goto(`http://localhost:3002/projects/${TEST_PROJECT_ID}`);
  await page.waitForTimeout(5000);
});
