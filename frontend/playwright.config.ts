import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  timeout: 60000, // Increase test timeout to 60s
  use: {
    baseURL: 'http://localhost:3002', // Use FRONTEND_PORT from .env
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    // headless: false, // Disabled - WSL X server causes browser crashes
  },
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        // launchOptions removed - caused crashes in WSL
      },
    },
  ],
  // Remove webServer - manage services manually for WSL
  // webServer: {
  //   command: 'npm run dev',
  //   url: 'http://localhost:3002',
  //   reuseExistingServer: true,
  //   timeout: 120000,
  // },
});
