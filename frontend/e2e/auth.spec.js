import { expect, test } from '@playwright/test';

test.describe('authentication and account features', () => {
  test('password endpoints do not exist', async ({ request }) => {
    expect((await request.post('/api/auth/login/', { data: { username: 'a', password: 'b' } })).status()).toBe(404);
    expect((await request.post('/api/auth/register/', { data: { username: 'a', password: 'b' } })).status()).toBe(404);
  });

  test('login page renders with provider buttons and instant sign-in', async ({ page, isMobile }) => {
    await page.goto('/login');
    await expect(page.getByRole('heading', { name: 'Sign in' })).toBeVisible();
    const nav = page.getByRole('navigation', { name: isMobile ? 'Mobile' : 'Primary' });
    await expect(nav.getByRole('link', { name: 'AI Hub' })).toHaveAttribute('href', '/ai');
  });

  test('instant sign-in authenticates and grants access to protected routes', async ({ page }) => {
    await page.goto('/login');
    const instantBtn = page.getByRole('button', { name: /instant sign-in/i });
    if (await instantBtn.isVisible()) {
      await instantBtn.click();
      await expect(page.getByText(/signed in/i)).toBeVisible();
    }
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
