import { test } from '@playwright/test';

test('check network response for project.ts', async ({ page }) => {
  const TEST_PROJECT_ID = '49d4acff-e89d-4149-ae7f-331d39ccb75f';

  // Listen for the specific file
  page.on('response', async response => {
    if (response.url().includes('project.ts')) {
      console.log('[FILE URL]:', response.url());
      console.log('[STATUS]:', response.status());
      const text = await response.text();
      console.log('[CONTENT]:', text);
    }
  });

  await page.goto(`http://localhost:3002/projects/${TEST_PROJECT_ID}`);
  await page.waitForTimeout(3000);
});
