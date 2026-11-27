// Playwright tests for the site in /docs. Run with `npm test`.
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: 'tests',
  forbidOnly: !!process.env.CI,
  reporter: process.env.CI ? 'list' : 'line',
  use: {
    baseURL: 'http://localhost:4173',
    trace: 'off',
  },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'] } },
    { name: 'phone', use: { ...devices['Pixel 7'] } },
  ],
  webServer: {
    command: 'npx http-server docs -p 4173 -c-1 --silent',
    url: 'http://localhost:4173/',
    reuseExistingServer: !process.env.CI,
  },
});
