import { test, expect } from '@playwright/test';

test.describe('Sync Status Display', () => {
  // Use actual project ID from seeded data
  const TEST_PROJECT_ID = '49d4acff-e89d-4149-ae7f-331d39ccb75f';

  test('should display sync status badges on ProjectDoc cards', async ({ page }) => {
    // Navigate to ProjectOverview page
    await page.goto(`http://localhost:3002/projects/${TEST_PROJECT_ID}`, {
      waitUntil: 'networkidle',
    });

    // Wait for ProjectDoc cards to load (increased timeout for React rendering)
    await page.waitForSelector('[data-testid="project-doc-card"]', { timeout: 15000 });

    // Verify sync status badge is visible
    const badge = page.locator('[data-testid="sync-status-badge"]').first();
    await expect(badge).toBeVisible();

    // Verify relative time is displayed
    const relativeTime = page.locator('[data-testid="last-synced-time"]').first();
    await expect(relativeTime).toBeVisible();
  });

  test('should trigger sync and show completion', async ({ page }) => {
    await page.goto(`http://localhost:3002/projects/${TEST_PROJECT_ID}`, {
      waitUntil: 'networkidle',
    });

    // Wait for cards to load
    await page.waitForSelector('[data-testid="project-doc-card"]', { timeout: 15000 });

    // Click sync button on first ProjectDoc card
    const syncButton = page.locator('[data-testid="sync-button"]').first();
    await syncButton.click();

    // Verify button shows spinner and is disabled
    await expect(syncButton).toBeDisabled();
    await expect(page.locator('[data-testid="sync-spinner"]')).toBeVisible();

    // Wait for success toast (max 60s for sync operation)
    await expect(
      page.locator('text=/Sync completed|synced successfully/i')
    ).toBeVisible({
      timeout: 60000,
    });

    // Verify sync status badge updates (wait for refetch)
    await page.waitForTimeout(1000);
    const badge = page.locator('[data-testid="sync-status-badge"]').first();
    await expect(badge).toBeVisible();
  });

  test('should display error tooltip for unavailable source', async ({ page }) => {
    // Note: This test requires a project with unavailable source
    // Skip if no error badge exists in current test data
    await page.goto(`http://localhost:3002/projects/${TEST_PROJECT_ID}`);

    // Find badge with "Source unavailable" state
    const errorBadge = page
      .locator('[data-testid="sync-status-badge"]:has-text("Source unavailable")')
      .first();

    // Check if error badge exists (may not exist depending on test data)
    const badgeCount = await errorBadge.count();
    if (badgeCount > 0) {
      // Hover to show tooltip
      await errorBadge.hover();

      // Verify tooltip content
      await expect(page.locator('text=/GitHub repository not accessible/i')).toBeVisible();
    } else {
      test.skip();
    }
  });
});
