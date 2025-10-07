import { test } from '@playwright/test';

test('debug page content', async ({ page }) => {
  const TEST_PROJECT_ID = '49d4acff-e89d-4149-ae7f-331d39ccb75f';

  await page.goto(`http://localhost:3002/projects/${TEST_PROJECT_ID}`);

  // Wait for page to load
  await page.waitForTimeout(3000);

  // Get page content
  const content = await page.content();
  console.log('Page HTML length:', content.length);

  // Get page text
  const text = await page.textContent('body');
  console.log('Page text:', text?.substring(0, 500));

  // Check for errors
  const errors = await page.evaluate(() => {
    const errorElements = document.querySelectorAll('[class*="error"]');
    return Array.from(errorElements).map(el => el.textContent);
  });
  console.log('Errors on page:', errors);

  // Take screenshot
  await page.screenshot({ path: 'debug-screenshot.png', fullPage: true });
});
