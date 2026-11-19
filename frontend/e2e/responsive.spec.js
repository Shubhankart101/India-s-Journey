import { expect, test } from '@playwright/test';

test.describe('responsive layout', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      window.localStorage.setItem('ij_auth_user', JSON.stringify({
        username: 'guest',
        first_name: 'Guest User',
        email: 'guest@example.com',
      }));
    });
  });
  test('mobile shows the tab bar, desktop shows the top nav', async ({ page, isMobile }) => {
    await page.goto('/');
    await expect(page.getByRole('link', { name: "India's Journey" })).toBeVisible();
    const tabs = page.getByRole('navigation', { name: 'Mobile' });
    const primary = page.getByRole('navigation', { name: 'Primary' });
    if (isMobile) {
      await expect(tabs).toBeVisible();
      await expect(primary).toBeHidden();
      await tabs.getByRole('link', { name: /Explore/ }).click();
      await expect(page).toHaveURL(/\/explore$/);
    } else {
      await expect(primary).toBeVisible();
      await expect(tabs).toBeHidden();
    }
  });

  test('no page scrolls sideways', async ({ page }) => {
    for (const path of ['/', '/explore', '/about', '/api']) {
      await page.goto(path);
      await expect(page.locator('main')).toBeVisible();
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      expect(overflow, path).toBeLessThanOrEqual(1);
    }
  });
});
