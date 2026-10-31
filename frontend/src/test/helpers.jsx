import { render } from '@testing-library/react';
import { MemoryRouter, useLocation } from 'react-router-dom';
import { vi } from 'vitest';
import { AppRoutes } from '../App.jsx';
import { AuthProvider } from '../auth.jsx';
import { CompareProvider } from '../compare.jsx';

export const json = (body, status = 200) => ({
  ok: status >= 200 && status < 300,
  status,
  json: async () => body,
});

export const providers = [
  { id: 'google', name: 'Google', login_url: '/accounts/google/login/' },
  { id: 'microsoft', name: 'Microsoft (Outlook)', login_url: '/accounts/microsoft/login/' },
];

// routes: { 'GET /api/stats/': body | (url, init) => body | json(body, status) }
export function mockApi(routes = {}) {
  const calls = [];
  const fetchMock = vi.fn(async (input, init = {}) => {
    const url = new URL(String(input), 'http://localhost');
    const method = (init.method || 'GET').toUpperCase();
    calls.push({ method, path: url.pathname, search: url.search, params: url.searchParams, init });
    const handler = routes[`${method} ${url.pathname}`] ?? routes[url.pathname];
    if (handler === undefined) {
      if (url.pathname === '/api/auth/me/') return json({ authenticated: false, user: null });
      if (url.pathname === '/api/auth/csrf/') return json({ detail: 'ok' });
      if (url.pathname === '/api/auth/providers/') return json(providers);
      return json({ detail: 'Not found.' }, 404);
    }
    const result = typeof handler === 'function' ? await handler(url, init) : handler;
    return result && typeof result.json === 'function' && 'status' in result ? result : json(result);
  });
  globalThis.fetch = fetchMock;
  return { fetchMock, calls };
}

export function LocationProbe() {
  const location = useLocation();
  return <output data-testid="location">{`${location.pathname}${location.search}`}</output>;
}

export function renderApp(path = '/') {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <AuthProvider>
        <CompareProvider>
          <AppRoutes />
          <LocationProbe />
        </CompareProvider>
      </AuthProvider>
    </MemoryRouter>,
  );
}

export const summary = (overrides = {}) => ({
  key: 'gdp_growth',
  title: 'Real GDP growth',
  subtitle: 'Annual real GDP growth',
  frequency: 'Annual',
  color: '#ff9933',
  suffix: '%',
  category: 'Economic',
  category_slug: 'economic',
  subgroup: 'Macro Overview',
  subgroup_slug: 'macro-overview',
  chart_type: 'line',
  index_axis: 'x',
  scope: '',
  is_live: true,
  point_count: 3,
  first_label: '2022',
  latest_label: '2024',
  latest_value: 6.5,
  preview: { labels: ['2022', '2023', '2024'], datasets: [{ label: 'Real GDP growth', values: [7, 8.2, 6.5] }] },
  updated_at: '2026-05-01T00:00:00Z',
  ...overrides,
});

export const detail = (overrides = {}) => ({
  ...summary(),
  source_url: 'https://data.worldbank.org/',
  details: 'First paragraph.\n\nSecond paragraph.',
  labels: ['2022', '2023', '2024'],
  datasets: [{ label: 'Real GDP growth', color: '#ff9933', values: [7, 8.2, 6.5] }],
  scope_label: '',
  note: '',
  source: 'World Bank',
  unit: '',
  error: '',
  category_art: 'parliament.svg',
  subgroup_art: 'parliament.svg',
  is_saved: false,
  related: [],
  previous_key: null,
  next_key: 'inflation',
  ...overrides,
});

export const categories = [
  {
    name: 'Economic', slug: 'economic', order: 0, title: 'Economic engine', description: 'Growth and prices', badges: [], art: 'parliament.svg',
    indicator_count: 2, live_count: 2,
    subgroups: [
      { name: 'Macro Overview', slug: 'macro-overview', order: 0, title: 'Macro', description: 'Headline macro', art: 'parliament.svg', indicator_count: 1, live_count: 1 },
      { name: 'Trade', slug: 'trade', order: 1, title: 'Trade', description: 'Exports', art: 'rail-station.svg', indicator_count: 1, live_count: 1 },
    ],
  },
  {
    name: 'Elections', slug: 'elections', order: 1, title: 'Elections', description: 'Votes', badges: [], art: 'eci-building.svg',
    indicator_count: 1, live_count: 1,
    subgroups: [{ name: 'Indian Elections', slug: 'indian-elections', order: 0, title: 'Indian Elections', description: '', art: 'eci-building.svg', indicator_count: 1, live_count: 1 }],
  },
];

export const page = (results, extra = {}) => ({ count: results.length, next: null, previous: null, results, ...extra });
