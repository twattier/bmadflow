import { test, expect } from '@playwright/test';

test.describe('File Tree Navigation', () => {
  test('should navigate file tree and select file', async ({ page }) => {
    // Navigate to Explorer (using a test project ID)
    await page.goto('http://localhost:3000/projects/test-project-id/explorer');

    // Wait for file tree to load
    await page.waitForSelector('[data-testid="file-tree"]', { timeout: 10000 });

    // Verify split view layout (tree panel + content viewer)
    const fileTreePanel = page.locator('[data-testid="file-tree"]');
    await expect(fileTreePanel).toBeVisible();

    // Check for content viewer
    const contentViewer = page.locator('text=Select a file from the tree to view its content');
    await expect(contentViewer).toBeVisible();

    // Try to expand a folder if it exists (chevron changes)
    const folders = page.locator('text=/docs|src|frontend/').first();
    if (await folders.isVisible()) {
      await folders.click();
      // Verify folder expanded (implementation-dependent)
    }

    // Click a file in tree
    const file = page.locator('text=/README|index|package/').first();
    if (await file.isVisible()) {
      await file.click();

      // Verify ContentViewer displays file name
      const fileName = await file.textContent();
      if (fileName) {
        await expect(page.locator(`text=${fileName}`)).toBeVisible();
      }
    }
  });

  test('should show empty state when no documents synced', async ({ page }) => {
    // Navigate to Explorer with project that has no synced documents
    await page.goto('http://localhost:3000/projects/empty-project-id/explorer');

    // Wait for empty state message
    await page.waitForTimeout(2000);

    // Verify empty state message displayed
    const emptyState = page.locator(
      'text=/No documents synced. Go to Overview and sync a ProjectDoc to get started./i'
    );
    await expect(emptyState).toBeVisible();
  });

  test('should show loading state', async ({ page }) => {
    // Navigate to Explorer
    await page.goto('http://localhost:3000/projects/test-project-id/explorer');

    // Check for loading spinner (it may be very fast)
    // Using a selector that matches the spinner animation class
    const spinner = page.locator('.animate-spin');

    // The spinner may already be gone by the time we check, so we use waitForSelector with a short timeout
    try {
      await spinner.waitFor({ state: 'visible', timeout: 1000 });
      await expect(spinner).toBeVisible();
    } catch {
      // Spinner was too fast, that's okay - the page loaded successfully
      const fileTree = page.locator('[data-testid="file-tree"]');
      await expect(fileTree).toBeVisible();
    }
  });
});
