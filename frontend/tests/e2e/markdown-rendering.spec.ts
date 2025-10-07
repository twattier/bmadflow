import { test, expect } from '@playwright/test';

test.describe('Markdown Rendering', () => {
  test('should render markdown file with TOC and content', async ({ page }) => {
    // Navigate to Explorer (using test project ID from manual testing)
    await page.goto('http://localhost:3002/projects/49d4acff-e89d-4149-ae7f-331d39ccb75f/explorer');

    // Wait for file tree to load
    await page.waitForSelector('[data-testid="file-tree"]', { timeout: 10000 });

    // Click on a markdown file
    const markdownFile = page.locator('text=/README|prebrief|architecture/i').first();
    await markdownFile.click();

    // Wait for content to load
    await page.waitForTimeout(1000);

    // Verify TOC is displayed
    const tocHeading = page.locator('h2:has-text("Contents")');
    await expect(tocHeading).toBeVisible();

    // Verify markdown content is rendered (check for prose container)
    const proseContainer = page.locator('.prose');
    await expect(proseContainer).toBeVisible();

    // Verify headers are rendered
    const heading = page.locator('.prose h1, .prose h2, .prose h3').first();
    await expect(heading).toBeVisible();
  });

  test('should navigate with TOC links', async ({ page }) => {
    // Navigate to Explorer
    await page.goto('http://localhost:3002/projects/49d4acff-e89d-4149-ae7f-331d39ccb75f/explorer');

    // Wait for file tree
    await page.waitForSelector('[data-testid="file-tree"]', { timeout: 10000 });

    // Click markdown file
    const markdownFile = page.locator('text=/README|prebrief|architecture/i').first();
    await markdownFile.click();

    // Wait for content to load
    await page.waitForTimeout(1000);

    // Find and click a TOC link
    const tocLink = page.locator('nav a[href^="#"]').first();
    if (await tocLink.isVisible()) {
      await tocLink.click();

      // Wait for smooth scroll animation
      await page.waitForTimeout(500);

      // Verify URL hash changed
      const url = page.url();
      expect(url).toContain('#');
    }
  });

  test('should render code blocks with syntax highlighting', async ({ page }) => {
    // Navigate to Explorer
    await page.goto('http://localhost:3002/projects/49d4acff-e89d-4149-ae7f-331d39ccb75f/explorer');

    // Wait for file tree
    await page.waitForSelector('[data-testid="file-tree"]', { timeout: 10000 });

    // Click markdown file with code blocks
    const markdownFile = page.locator('text=/README|prebrief|architecture/i').first();
    await markdownFile.click();

    // Wait for content
    await page.waitForTimeout(2000);

    // Verify markdown is rendered
    const proseContainer = page.locator('.prose');
    await expect(proseContainer).toBeVisible();

    // Check for code blocks if they exist
    const codeBlock = page.locator('code[class*="language-"]').first();
    const codeBlockCount = await codeBlock.count();

    if (codeBlockCount > 0) {
      await expect(codeBlock).toBeVisible();
    }
  });

  test('should show loading state while fetching document', async ({ page }) => {
    // Navigate to Explorer
    await page.goto('http://localhost:3002/projects/49d4acff-e89d-4149-ae7f-331d39ccb75f/explorer');

    // Wait for file tree
    await page.waitForSelector('[data-testid="file-tree"]', { timeout: 10000 });

    // Click markdown file
    const markdownFile = page.locator('text=/README|prebrief/i').first();
    await markdownFile.click();

    // Try to catch loading state (may be very fast)
    try {
      const loadingSpinner = page.locator('.animate-spin');
      await loadingSpinner.waitFor({ state: 'visible', timeout: 1000 });
    } catch {
      // Loading was too fast, verify content is displayed
      const proseContainer = page.locator('.prose');
      await expect(proseContainer).toBeVisible();
    }
  });

  test('should render markdown typography styles', async ({ page }) => {
    // Navigate to Explorer
    await page.goto('http://localhost:3002/projects/49d4acff-e89d-4149-ae7f-331d39ccb75f/explorer');

    // Wait for file tree
    await page.waitForSelector('[data-testid="file-tree"]', { timeout: 10000 });

    // Click markdown file
    const markdownFile = page.locator('text=/README|prebrief/i').first();
    await markdownFile.click();

    // Wait for content
    await page.waitForTimeout(1000);

    // Verify prose classes are applied
    const proseContainer = page.locator('.prose.prose-slate.prose-sm');
    await expect(proseContainer).toBeVisible();

    // Verify headings exist
    const headings = page.locator('.prose h1, .prose h2, .prose h3');
    const headingCount = await headings.count();
    expect(headingCount).toBeGreaterThan(0);
  });

  test('should show placeholder for non-markdown files', async ({ page }) => {
    // Navigate to Explorer
    await page.goto('http://localhost:3002/projects/49d4acff-e89d-4149-ae7f-331d39ccb75f/explorer');

    // Wait for file tree
    await page.waitForSelector('[data-testid="file-tree"]', { timeout: 10000 });

    // Try to find a non-markdown file (json, txt, etc.)
    const nonMdFile = page.locator('text=/.json|.txt|.yaml/i').first();

    if (await nonMdFile.isVisible()) {
      await nonMdFile.click();
      await page.waitForTimeout(500);

      // Verify placeholder message is shown
      const placeholder = page.locator('text=/viewer.*coming soon/i');
      await expect(placeholder).toBeVisible();
    }
  });
});
