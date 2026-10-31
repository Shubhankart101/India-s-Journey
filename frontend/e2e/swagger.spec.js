import { expect, test } from '@playwright/test';

test.describe('Swagger / OpenAPI', () => {
  test('Swagger UI loads the schema and lists the endpoints', async ({ page }) => {
    await page.goto('/api/docs/');
    await expect(page.locator('.swagger-ui .title')).toContainText("India's Journey API");
    for (const path of ['/api/indicators/', '/api/compare/', '/api/auth/providers/', '/api/saved/']) {
      await expect(page.locator('.opblock-summary-path', { hasText: path }).first()).toBeAttached();
    }
  });

  test('Try it out executes a request from Swagger UI', async ({ page }) => {
    await page.goto('/api/docs/');
    const block = page.locator('.opblock-get', { has: page.locator('.opblock-summary-path', { hasText: /^\/api\/health\/$/ }) });
    await block.locator('.opblock-summary').click();
    // SPECTACULAR_SETTINGS enables tryItOutEnabled, so Execute is available immediately.
    await block.getByRole('button', { name: 'Execute' }).click();
    await expect(block.locator('.live-responses-table tbody .response-col_status').first()).toContainText('200');
  });

  test('ReDoc and the raw schema are served', async ({ page, request }) => {
    const schema = await request.get('/api/schema/?format=json');
    expect(schema.status()).toBe(200);
    expect((await schema.json()).openapi).toMatch(/^3\./);
    const redoc = await page.goto('/api/redoc/');
    expect(redoc.status()).toBe(200);
  });
});
