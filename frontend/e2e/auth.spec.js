import { expect, test } from '@playwright/test';

test.describe('account features (currently disabled)', () => {
  test('password endpoints do not exist', async ({ request }) => {
    expect((await request.post('/api/auth/login/', { data: { username: 'a', password: 'b' } })).status()).toBe(404);
    expect((await request.post('/api/auth/register/', { data: { username: 'a', password: 'b' } })).status()).toBe(404);
  });

  test('login and saved routes are not exposed in the app', async ({ page }) => {
    await page.goto('/login');
    await expect(page.getByRole('heading', { name: 'This page wandered off.' })).toBeVisible();
    const primary = page.getByRole('navigation', { name: 'Primary' });
    await expect(primary.getByRole('link', { name: 'API' })).toHaveAttribute('href', '/api');
    await expect(page.getByRole('link', { name: 'Sign in' })).toHaveCount(0);
    await expect(page.getByRole('link', { name: 'Saved' })).toHaveCount(0);

    await page.goto('/saved');
    await expect(page.getByRole('heading', { name: 'This page wandered off.' })).toBeVisible();
  });

  test('generic allauth login and signup URLs return to the dashboard', async ({ request }) => {
    const login = await request.get('/accounts/login/?next=/compare', { maxRedirects: 0 });
    expect(login.status()).toBe(302);
    expect(login.headers().location).toBe('/?next=/compare');
    const signup = await request.get('/accounts/signup/', { maxRedirects: 0 });
    expect(signup.status()).toBe(302);
    expect(signup.headers().location).toBe('/');
  });
});
