import process from 'node:process';
import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E configuration for GeoAI (Pera Rest Nav).
 *
 * NOTE: Playwright does NOT auto-launch backend or frontend servers.
 * Ensure both development servers are already running before executing E2E tests:
 *   1. Backend:  `uvicorn app.main:app --port 8000` (from backend/ with venv)
 *   2. Frontend: `npm run dev` (from frontend/ on port 5173)
 */
export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers: 1,
  reporter: 'list',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    viewport: { width: 390, height: 844 }, // Mobile viewport for campus finder
    geolocation: { latitude: 7.2545, longitude: 80.5965 },
    permissions: ['geolocation'],
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
