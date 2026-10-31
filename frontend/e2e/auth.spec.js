import { expect, test } from '@playwright/test';

test.describe('sign-in (Google and Microsoft only)', () => {
  test('lists exactly the two OAuth providers and no password form', async ({ page }) => {
    await page.goto('/login');
    await expect(page.getByRole('button', { name: /Continue with Google/ })).toBeVisible();
    await expect(page.getByRole('button', { name: /Continue with Microsoft/ })).toBeVisible();
    await expect(page.locator('input[type=password]')).toHaveCount(0);
  });

  test('password endpoints do not exist', async ({ request }) => {
    expect((await request.post('/api/auth/login/', { data: { username: 'a', password: 'b' } })).status()).toBe(404);
    expect((await request.post('/api/auth/register/', { data: { username: 'a', password: 'b' } })).status()).toBe(404);
  });

  for (const [name, host, clientId] of [
    ['Google', 'accounts.google.com', 'e2e-google-client'],
    ['Microsoft', 'login.microsoftonline.com', 'e2e-microsoft-client'],
  ]) {
    test(`${name} button starts the OAuth redirect with PKCE and state`, async ({ page }) => {
      // Capture allauth's redirect instead of following it to the real provider.
      let location;
      await page.route(/\/accounts\/(google|microsoft)\/login\/$/, async route => {
        const response = await route.fetch({ maxRedirects: 0 });
        location = response.headers().location;
        await route.fulfill({ status: 200, contentType: 'text/html', body: '<h1>provider</h1>' });
      });
      await page.goto('/login?next=/saved');
      await page.getByRole('button', { name: new RegExp(`Continue with ${name}`) }).click();
      await expect(page.getByRole('heading', { name: 'provider' })).toBeVisible();
      const authorizeUrl = new URL(location);
      expect(authorizeUrl.host).toBe(host);
      expect(authorizeUrl.searchParams.get('client_id')).toBe(clientId);
      expect(authorizeUrl.searchParams.get('response_type')).toBe('code');
      expect(authorizeUrl.searchParams.get('state')).toBeTruthy();
      expect(authorizeUrl.searchParams.get('code_challenge_method')).toBe('S256');
      expect(authorizeUrl.searchParams.get('redirect_uri')).toMatch(/\/accounts\/(google|microsoft)\/login\/callback\/$/);
    });
  }

  test('allauth local login and signup pages redirect to the SPA', async ({ page }) => {
    await page.goto('/accounts/login/?next=/compare');
    await expect(page).toHaveURL(/\/login\?next=(%2F|\/)compare/);
    await page.goto('/accounts/signup/');
    await expect(page).toHaveURL(/\/login/);
  });

  test('saved charts require sign-in', async ({ page }) => {
    await page.goto('/saved');
    await expect(page).toHaveURL(/\/login\?next=/);
  });
});
