import { expect, test } from '@playwright/test';

const BACKUP = 'https://shubhankart101.github.io/India-s-Journey/';

test.describe('site', () => {
  test('home loads stats, groups and navigation', async ({ page }) => {
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto('/');
    await expect(page.getByRole('link', { name: "India's Journey" })).toBeVisible();
    await expect(page.locator('main')).toContainText(/indicators/i);
    expect(errors).toEqual([]);
  });

  test('explore filters by search and survives a reload', async ({ page }) => {
    await page.goto('/explore');
    await page.getByRole('searchbox', { name: 'Search indicators' }).fill('GDP');
    await expect(page).toHaveURL(/q=GDP/);
    await expect(page.locator('main h3, main h2').first()).toBeVisible();
    await page.reload();
    await expect(page.getByRole('searchbox', { name: 'Search indicators' })).toHaveValue('GDP');
  });

  test('indicator page renders a chart and downloads CSV', async ({ page, request }) => {
    const list = await (await request.get('/api/indicators/?live=true&page_size=1')).json();
    const key = list.results[0].key;
    await page.goto(`/indicator/${key}`);
    await expect(page.locator('canvas').first()).toBeVisible();
    const csv = await request.get(`/api/indicators/${key}/download/?format=csv`);
    expect(csv.status()).toBe(200);
    expect(csv.headers()['content-type']).toContain('text/csv');
  });

  test('compare draws several series', async ({ page, request }) => {
    const list = await (await request.get('/api/indicators/?live=true&chart=line&page_size=2')).json();
    const keys = list.results.map(item => item.key).join(',');
    await page.goto(`/compare?keys=${keys}`);
    await expect(page.locator('canvas').first()).toBeVisible();
    await expect(page.getByRole('table')).toBeVisible();
  });

  test('deep links work on a hard refresh', async ({ page }) => {
    for (const path of ['/explore', '/compare', '/about', '/login', '/saved']) {
      const response = await page.goto(path);
      expect(response.status(), path).toBe(200);
    }
  });

  test('unknown pages show the 404 with the backup site', async ({ page }) => {
    await page.goto('/no/such/page');
    await expect(page.getByText('This page wandered off.')).toBeVisible();
    await expect(page.getByRole('link', { name: /backup dashboard/ })).toHaveAttribute('href', BACKUP);
  });
});

test.describe('server error pages', () => {
  test('API 404 returns JSON with the backup URL', async ({ request }) => {
    const response = await request.get('/api/definitely-missing/');
    expect(response.status()).toBe(404);
    expect((await response.json()).backup_url).toBe(BACKUP);
  });

  test('server-rendered pages link to the backup site', async ({ page }) => {
    const response = await page.goto('/accounts/definitely-missing/');
    expect(response.status()).toBe(404);
    await expect(page.getByRole('link', { name: /backup/i }).first()).toHaveAttribute('href', BACKUP);
  });

  test('health reports ok', async ({ request }) => {
    const body = await (await request.get('/api/health/')).json();
    expect(body.status).toBe('ok');
    expect(body.indicators).toBeGreaterThan(0);
  });
});
