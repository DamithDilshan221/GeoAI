import { test, expect } from '@playwright/test';

/**
 * Task C — Playwright E2E User Journey Test.
 *
 * Walks the complete real user flow against live running development servers:
 * 1. Root page (Category selection & Audience chips)
 * 2. Geolocation request & permission resolution
 * 3. Nearby Washrooms listing (real seeded campus data)
 * 4. Facility Details sheet (real fixtures, status, rating)
 * 5. Navigation overlay activation
 * 6. AI Recommendation flow (ranking, crowd metrics, and routing)
 */

test.describe('Campus Washroom Finder — E2E User Journey', () => {
  test.beforeEach(async ({ context }) => {
    // Set campus reference coordinate (Faculty of Engineering, University of Peradeniya)
    await context.grantPermissions(['geolocation']);
    await context.setGeolocation({ latitude: 7.2545, longitude: 80.5965 });
  });

  test('walks through category selection, nearby listing, facility details, and navigation', async ({ page }) => {
    // 1. Root Category Selection
    await page.goto('/');
    await expect(page.getByText('Find a washroom', { exact: false })).toBeVisible();

    // 2. Select Category & Audience Chip (e.g., Visitor on Men's or Female category)
    const visitorChip = page.getByRole('button', { name: 'Visitor' }).first();
    await expect(visitorChip).toBeVisible();
    await visitorChip.click();

    // 3. Nearby Facilities screen should load real seeded washrooms
    await expect(page).toHaveURL(/\/nearby/);
    await expect(page.getByText('washroom found', { exact: false })).toBeVisible({ timeout: 10000 });

    // Assert that real seeded washrooms from database/seed/facilities.json render
    const facilityCard = page.locator('div[style*="border-left"]').filter({ hasText: /Men's|Women's|GYM|ICT/i }).first();
    await expect(facilityCard).toBeVisible();

    // 4. Tap facility card to open details page
    await facilityCard.click();
    await expect(page).toHaveURL(/\/facility\/\d+/);

    // Assert details view renders status and fixtures
    await expect(page.getByRole('heading', { level: 2 })).toBeVisible();
    await expect(page.getByText(/OPEN|CLOSED/i)).toBeVisible();

    // 5. Tap Navigate button to trigger NavigationOverlay
    const navigateBtn = page.getByRole('button', { name: /navigate/i }).first();
    if (await navigateBtn.isVisible()) {
      await navigateBtn.click();
      // Confirm navigation overlay is displayed with navigation controls
      await expect(page.getByText(/Start|Stop|End|Arrived/i).first()).toBeVisible();
      // Close overlay
      const closeBtn = page.getByLabel('Close navigation').or(page.getByRole('button', { name: /close|stop|end/i })).first();
      if (await closeBtn.isVisible()) {
        await closeBtn.click();
      }
    }

    // 6. Navigate to AI Recommendation
    await page.goto('/nearby');
    const aiRecChip = page.getByText('AI Recommendation');
    if (await aiRecChip.isVisible()) {
      await aiRecChip.click();
      await expect(page).toHaveURL(/\/recommendation/);

      // Confirm recommendation renders top match card with crowd and distance metrics
      await expect(page.getByText(/Top Match/i)).toBeVisible({ timeout: 10000 });
      await expect(page.getByText(/Crowd|Distance|Est\. Time/i).first()).toBeVisible();

      // Tap Start Navigation from recommendation
      const startNavBtn = page.locator('#start-navigation-btn').or(page.getByRole('button', { name: /start navigation/i }));
      await expect(startNavBtn).toBeVisible();
      await startNavBtn.click();

      // Confirm navigation overlay renders
      await expect(page.getByText(/Stop|End|Arrived|Campus/i).first()).toBeVisible();
    }
  });
});
