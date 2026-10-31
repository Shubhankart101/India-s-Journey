import { expect, test } from '@playwright/test';

test.describe('responsive layout', () => {
  test('mobile shows the tab bar, desktop shows the top nav', async ({ page, isMobile }) => {
    await page.goto('/');
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
    for (const path of ['/', '/explore', '/about', '/login']) {
      await page.goto(path);
      await page.waitForLoadState('networkidle');
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      expect(overflow, path).toBeLessThanOrEqual(1);
    }
  });
});
