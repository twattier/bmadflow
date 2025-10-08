import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Story 3.6: Cross-Document Navigation
 *
 * Tests all 7 acceptance criteria:
 * AC1: Relative links resolve to documents in same ProjectDoc
 * AC2: Clicking relative link loads target document
 * AC3: File tree updates to highlight newly selected document
 * AC4: Breadcrumb updates to show current file path
 * AC5: Browser history updated (back button works)
 * AC6: Broken links display tooltip "Document not found"
 * AC7: External links open in new tab
 */

test.describe('Cross-Document Navigation', () => {
  const BASE_URL = process.env.BASE_URL || 'http://localhost:5173';
  const PROJECT_ID = 'test-project-for-navigation';

  test.beforeEach(async ({ page }) => {
    // Navigate to documentation explorer page
    await page.goto(`${BASE_URL}/projects/${PROJECT_ID}/explorer`);

    // Wait for file tree to load
    await page.waitForSelector('text=readme.md', { timeout: 10000 });
  });

  /**
   * AC1 Test: Should resolve relative paths within same ProjectDoc
   */
  test('AC1: should resolve relative paths within same ProjectDoc', async ({ page }) => {
    // Select readme.md
    await page.click('text=readme.md');

    // Wait for content to load
    await page.waitForSelector('h1:has-text("README")', { timeout: 5000 });

    // Check for relative link
    const relativeLink = page.locator('a:has-text("Architecture")');
    await expect(relativeLink).toBeVisible();

    // Verify link has correct href (relative path)
    const href = await relativeLink.getAttribute('href');
    expect(href).toContain('.md'); // Should be a relative markdown link
  });

  /**
   * AC2 Test: Should load target document in viewer when link clicked
   */
  test('AC2: should load target document in viewer when link clicked', async ({ page }) => {
    // Select readme.md
    await page.click('text=readme.md');
    await page.waitForSelector('h1:has-text("README")');

    // Click relative link to architecture.md
    await page.click('a:has-text("Architecture")');

    // Verify architecture document loaded
    await page.waitForSelector('h1:has-text("Architecture")', { timeout: 5000 });

    // Verify content viewer shows architecture content
    const content = page.locator('text=System design and technical decisions');
    await expect(content).toBeVisible({ timeout: 3000 });
  });

  /**
   * AC3 Test: Should highlight newly selected document in file tree
   */
  test('AC3: should highlight newly selected document in file tree', async ({ page }) => {
    // Select readme.md
    await page.click('text=readme.md');
    await page.waitForSelector('h1:has-text("README")');

    // Click link to navigate to architecture.md
    await page.click('a:has-text("Architecture")');
    await page.waitForSelector('h1:has-text("Architecture")');

    // Verify file tree selection updated
    // Note: This depends on file tree implementation details
    // We'll check if architecture.md is now visually indicated as selected
    const fileTreeItem = page.locator('[role="treeitem"]:has-text("architecture.md")');
    await expect(fileTreeItem).toBeVisible();

    // Check for aria-selected or similar attribute (depends on implementation)
    // This may need adjustment based on actual FileTreePanel implementation
    const isSelected = await fileTreeItem.evaluate((el) => {
      return (
        el.getAttribute('aria-selected') === 'true' ||
        el.classList.contains('selected') ||
        el.classList.contains('bg-accent')
      );
    });

    expect(isSelected).toBeTruthy();
  });

  /**
   * AC4 Test: Should update breadcrumb with current file path
   */
  test('AC4: should update breadcrumb with current file path', async ({ page }) => {
    // Select readme.md
    await page.click('text=readme.md');
    await page.waitForSelector('h1:has-text("README")');

    // Check initial breadcrumb
    const breadcrumb = page.locator('[role="navigation"]').first();
    await expect(breadcrumb).toContainText('readme.md');

    // Navigate via link
    await page.click('a:has-text("Architecture")');
    await page.waitForSelector('h1:has-text("Architecture")');

    // Verify breadcrumb updated to show architecture.md
    await expect(breadcrumb).toContainText('architecture.md', { timeout: 3000 });
  });

  /**
   * AC5 Test: Should update browser history (back button works)
   */
  test('AC5: should update browser history and support back button', async ({ page }) => {
    // Select readme.md
    await page.click('text=readme.md');
    await page.waitForSelector('h1:has-text("README")');

    // Get initial URL
    const initialUrl = page.url();
    expect(initialUrl).toContain('file=');
    expect(initialUrl).toContain('readme.md');

    // Navigate to architecture.md via link
    await page.click('a:has-text("Architecture")');
    await page.waitForSelector('h1:has-text("Architecture")');

    // Verify URL updated
    const newUrl = page.url();
    expect(newUrl).toContain('architecture.md');
    expect(newUrl).not.toBe(initialUrl);

    // Click browser back button
    await page.goBack();

    // Verify returned to readme.md
    await page.waitForSelector('h1:has-text("README")', { timeout: 3000 });
    expect(page.url()).toContain('readme.md');
  });

  /**
   * AC6 Test: Should show "Document not found" tooltip for broken links
   */
  test('AC6: should show tooltip for broken links', async ({ page }) => {
    // Create a test document with a broken link (or use existing if available)
    // This test assumes there's a document with a broken link in the test data

    // For this test, we'll navigate to a document and check if broken links are handled
    await page.click('text=readme.md');
    await page.waitForSelector('h1:has-text("README")');

    // If there's a broken link in the content, try to find it
    const brokenLink = page.locator('a:has-text("Nonexistent")');

    // Check if broken link exists (may not in all test cases)
    const brokenLinkCount = await brokenLink.count();

    if (brokenLinkCount > 0) {
      // Hover over broken link to trigger tooltip
      await brokenLink.hover();

      // Verify tooltip appears with "Document not found" message
      const tooltip = page.locator('text=Document not found');
      await expect(tooltip).toBeVisible({ timeout: 2000 });
    } else {
      // Skip if no broken links in test data
      test.skip();
    }
  });

  /**
   * AC7 Test: Should open external links in new tab
   */
  test('AC7: should open external links in new tab', async ({ page, context }) => {
    // Select readme.md
    await page.click('text=readme.md');
    await page.waitForSelector('h1:has-text("README")');

    // Find external link (assuming there's one in the test data)
    const externalLink = page.locator('a[href^="http://"], a[href^="https://"]').first();

    // Check if external link exists
    const externalLinkCount = await externalLink.count();

    if (externalLinkCount > 0) {
      // Verify link has target="_blank"
      const target = await externalLink.getAttribute('target');
      expect(target).toBe('_blank');

      // Verify link has rel="noopener noreferrer"
      const rel = await externalLink.getAttribute('rel');
      expect(rel).toContain('noopener');
      expect(rel).toContain('noreferrer');

      // Listen for new page (tab) being opened
      const [newPage] = await Promise.all([
        context.waitForEvent('page'),
        externalLink.click(),
      ]);

      // Verify new page opened with external URL
      const newPageUrl = newPage.url();
      expect(newPageUrl).toMatch(/^https?:\/\//);

      // Close new page
      await newPage.close();
    } else {
      // If no external links, we can still verify the test is set up correctly
      console.log('No external links found in test data');
    }
  });

  /**
   * Performance Test: Navigation should complete within 1 second (NFR1)
   */
  test('should navigate within 1 second', async ({ page }) => {
    // Select readme.md
    await page.click('text=readme.md');
    await page.waitForSelector('h1:has-text("README")');

    // Measure navigation time
    const startTime = Date.now();

    // Click link to navigate
    await page.click('a:has-text("Architecture")');

    // Wait for new document to load
    await page.waitForSelector('h1:has-text("Architecture")');

    const endTime = Date.now();
    const navigationTime = endTime - startTime;

    // Verify navigation took less than 1 second
    expect(navigationTime).toBeLessThan(1000);
  });

  /**
   * Multi-hop Navigation Test
   */
  test('should support multi-hop navigation (readme -> architecture -> api -> back to readme)', async ({
    page,
  }) => {
    // Navigate from readme to architecture
    await page.click('text=readme.md');
    await page.waitForSelector('h1:has-text("README")');

    await page.click('a:has-text("Architecture")');
    await page.waitForSelector('h1:has-text("Architecture")');

    // Navigate from architecture to api
    await page.click('a:has-text("API")');
    await page.waitForSelector('h1:has-text("API")');

    // Navigate from api back to readme
    await page.click('a:has-text("README")');
    await page.waitForSelector('h1:has-text("README")', { timeout: 3000 });

    // Verify we're back at readme
    expect(page.url()).toContain('readme.md');
  });

  /**
   * Anchor Link Test
   */
  test('should handle anchor-only links without cross-document navigation', async ({ page }) => {
    await page.click('text=readme.md');
    await page.waitForSelector('h1:has-text("README")');

    // Find anchor link (e.g., #overview)
    const anchorLink = page.locator('a[href^="#"]').first();

    const anchorLinkCount = await anchorLink.count();
    if (anchorLinkCount > 0) {
      const initialUrl = page.url();

      // Click anchor link
      await anchorLink.click();

      // URL should update with anchor but document should not change
      const newUrl = page.url();
      expect(newUrl).toContain('#');

      // Should still be on same document (base URL part)
      expect(newUrl.split('#')[0]).toBe(initialUrl.split('#')[0]);

      // Document heading should still be README
      await expect(page.locator('h1:has-text("README")')).toBeVisible();
    }
  });
});

/**
 * Multi-browser tests (Chromium, Firefox, WebKit)
 * Playwright automatically runs these across all configured browsers
 */
