import { test, expect } from '@playwright/test';

test.describe('Projects Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/projects');
  });

  test('create project flow', async ({ page }) => {
    // Navigate to /projects
    await expect(page).toHaveURL('/projects');
    await expect(page.getByRole('heading', { name: 'Projects' })).toBeVisible();

    // Click "+ New Project" card
    await page.getByTestId('new-project-card').click();

    // Verify dialog opens
    await expect(page.getByRole('dialog')).toBeVisible();
    await expect(page.getByText('Create New Project')).toBeVisible();

    // Fill in form
    await page.getByTestId('project-name-input').fill('Test Project');
    await page.getByTestId('project-description-input').fill('Test Description');

    // Submit form
    await page.getByTestId('create-project-button').click();

    // Verify success toast appears (if backend is running)
    // await expect(page.getByText('Project created successfully')).toBeVisible({ timeout: 5000 });

    // Verify dialog closes
    await expect(page.getByRole('dialog')).not.toBeVisible({ timeout: 5000 });
  });

  test('project navigation flow', async ({ page }) => {
    // This test requires existing project data
    // Skip if no projects exist

    const projectCards = page.getByTestId('project-card');
    const count = await projectCards.count();

    if (count > 0) {
      // Click "View" button on first project card
      const firstCard = projectCards.first();
      const viewButton = firstCard.getByTestId('view-button');
      await viewButton.click();

      // Verify navigation to Project Overview page
      await expect(page).toHaveURL(/\/projects\/[\w-]+/);

      // Verify project details displayed
      await expect(page.getByRole('heading', { level: 1 })).toBeVisible();

      // Verify breadcrumb shows "Projects > [Project Name]"
      const breadcrumb = page.getByRole('navigation', { name: /breadcrumb/i }).or(page.locator('nav[aria-label="breadcrumb"]')).or(page.locator('[data-testid="breadcrumbs"]'));
      await expect(breadcrumb.getByText('Projects')).toBeVisible();

      // Verify sidebar shows project-specific navigation
      await expect(page.getByRole('link', { name: 'Overview' })).toBeVisible();
      await expect(page.getByRole('link', { name: 'Explorer' })).toBeVisible();
      await expect(page.getByRole('link', { name: 'Chat' })).toBeVisible();
      await expect(page.getByRole('link', { name: 'Settings' })).toBeVisible();
    }
  });

  test('empty states', async ({ page }) => {
    // Test empty state for no projects
    const emptyMessage = page.getByText('No projects yet. Create your first project to get started.');
    const hasProjects = (await page.getByTestId('project-card').count()) > 0;

    if (!hasProjects) {
      await expect(emptyMessage).toBeVisible();
    }
  });
});
