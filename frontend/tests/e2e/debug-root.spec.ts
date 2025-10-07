import { test } from '@playwright/test';

test('check root element and scripts', async ({ page }) => {
  const TEST_PROJECT_ID = '49d4acff-e89d-4149-ae7f-331d39ccb75f';

  // Listen for all requests
  page.on('request', request => {
    if (request.url().includes('.tsx') || request.url().includes('.ts')) {
      console.log('[REQUEST]:', request.url());
    }
  });

  // Listen for responses
  page.on('response', response => {
    if (response.status() >= 400) {
      console.log('[ERROR RESPONSE]:', response.url(), response.status());
    }
  });

  // Listen for console errors
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('[CONSOLE ERROR]:', msg.text());
    }
  });

  // Listen for page errors
  page.on('pageerror', error => {
    console.log('[PAGE ERROR]:', error.message);
    console.log('[STACK]:', error.stack);
  });

  await page.goto(`http://localhost:3002/projects/${TEST_PROJECT_ID}`);
  await page.waitForTimeout(5000);

  // Check if root div has content
  const rootContent = await page.evaluate(() => {
    const root = document.getElementById('root');
    return {
      exists: !!root,
      innerHTML: root?.innerHTML || '',
      childCount: root?.children.length || 0
    };
  });

  console.log('[ROOT ELEMENT]:', rootContent);
});
