import { defineConfig, devices } from '@playwright/test';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const PORT = Number(process.env.E2E_PORT || 8010);
const baseURL = process.env.E2E_BASE_URL || `http://127.0.0.1:${PORT}`;
const python = process.env.PYTHON || (process.platform === 'win32' ? 'python' : 'python3');

export default defineConfig({
  testDir: './e2e',
  timeout: 30_000,
  expect: { timeout: 10_000 },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [['list'], ['html', { open: 'never' }]] : 'list',
  use: { baseURL, trace: 'retain-on-failure', screenshot: 'only-on-failure' },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile', use: { ...devices['Pixel 7'] } },
  ],
  // Boots the real Django app serving the built SPA (run `npm run build` first). Set E2E_BASE_URL to test a deployed site instead.
  webServer: process.env.E2E_BASE_URL ? undefined : {
    command: `${python} manage.py migrate --noinput && ${python} manage.py collectstatic --noinput -v 0 && ${python} manage.py import_catalog && ${python} manage.py runserver 127.0.0.1:${PORT} --noreload --insecure`,
    cwd: '../webapp',
    url: `${baseURL}/api/health/`,
    timeout: 180_000,
    reuseExistingServer: !process.env.CI,
    // Production settings (DEBUG off) so the custom 404/500 pages and manifest static files are exercised.
    env: {
      DJANGO_DEBUG: '0',
      DJANGO_SECRET_KEY: 'e2e-only-not-secret',
      DJANGO_SECURE_COOKIES: '0',
      DJANGO_SQLITE_PATH: join(tmpdir(), 'indias-journey-e2e.sqlite3'),
      GOOGLE_CLIENT_ID: 'e2e-google-client',
      GOOGLE_CLIENT_SECRET: 'e2e-google-secret',
      MICROSOFT_CLIENT_ID: 'e2e-microsoft-client',
      MICROSOFT_CLIENT_SECRET: 'e2e-microsoft-secret',
      PYTHONIOENCODING: 'utf-8',
    },
  },
});
