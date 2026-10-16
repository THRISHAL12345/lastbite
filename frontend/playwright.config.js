import { defineConfig } from 'playwright/test';
export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  workers: 1,
  timeout: 60000,
  globalTimeout: 300000,
  retries: 0,
  outputDir: '../artifacts/browser/results',
  reporter: [['list'], ['html', { outputFolder: '../artifacts/browser/report', open: 'never' }]],
  use: {
    baseURL: process.env.FRONTEND_URL || 'http://127.0.0.1:3000',
    browserName: 'chromium',
    viewport: { width: 1440, height: 1000 },
    screenshot: 'on',
    video: 'on',
    trace: 'retain-on-failure',
  },
});
