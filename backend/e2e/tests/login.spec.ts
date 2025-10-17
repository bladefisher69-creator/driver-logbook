import { test, expect } from '@playwright/test';

test('login flow', async ({ page }) => {
  await page.goto('/');

  // Adjust selectors to match your login form
  await page.fill('input[name="username"]', 'john_doe');
  await page.fill('input[name="password"]', 'driver123');
  await page.click('button:has-text("Sign In")');

  // Wait for a redirect or dashboard element
  await page.waitForTimeout(1000);
  await expect(page.locator('text=Sign Out').first()).toBeVisible({ timeout: 5000 });
});
