import { describe, expect, it } from 'vitest';
import { api, ApiError, request, toQuery } from '../api.js';
import { Chart as ChartJS } from 'chart.js';
import { buildChartData, buildOptions, radialPoints } from '../components/ChartView.jsx';
import { normalise } from '../pages/Compare.jsx';
import { safeNext } from '../pages/AuthPage.jsx';
import { json, mockApi } from './helpers.jsx';

describe('api client', () => {
  it('builds query strings without empty values', () => {
    expect(toQuery({ q: 'coal', category: '', page: 2, live: null })).toBe('?q=coal&page=2');
    expect(toQuery({})).toBe('');
  });

  it('sends the CSRF token on writes, fetching it first when missing', async () => {
    const { calls } = mockApi({
      'GET /api/auth/csrf/': () => {
        document.cookie = 'csrftoken=abc123';
        return { detail: 'ok' };
      },
      'POST /api/saved/': { key: 'gdp_growth' },
    });
    await api.save('gdp_growth');
    expect(calls.map(call => `${call.method} ${call.path}`)).toEqual(['GET /api/auth/csrf/', 'POST /api/saved/']);
    expect(calls[1].init.headers['X-CSRFToken']).toBe('abc123');
    expect(JSON.parse(calls[1].init.body)).toEqual({ key: 'gdp_growth', note: '' });
  });

  it('raises ApiError with the server message', async () => {
    mockApi({ 'POST /api/saved/': json({ detail: 'Authentication credentials were not provided.' }, 403) });
    document.cookie = 'csrftoken=t';
    await expect(api.save('gdp_growth')).rejects.toMatchObject({ status: 403, message: 'Authentication credentials were not provided.' });
  });

  it('has no password login or registration methods', () => {
    expect(api.login).toBeUndefined();
    expect(api.register).toBeUndefined();
  });

  it('loads OAuth providers and reads the CSRF cookie', async () => {
    mockApi();
    document.cookie = 'csrftoken=a%2Bb';
    expect((await api.providers()).map(item => item.id)).toEqual(['google', 'microsoft']);
    expect(api.csrfToken()).toBe('a+b');
  });

  it('announces when the API is unreachable', async () => {
    const seen = [];
    const listener = () => seen.push('down');
    window.addEventListener('api:unreachable', listener);
    globalThis.fetch = async () => { throw new TypeError('Failed to fetch'); };
    await expect(request('/api/stats/')).rejects.toMatchObject({ status: 0 });
    mockApi({ '/api/stats/': json({ detail: 'Bad gateway' }, 502) });
    await expect(request('/api/stats/')).rejects.toMatchObject({ status: 502 });
    window.removeEventListener('api:unreachable', listener);
    expect(seen).toEqual(['down', 'down']);
  });

  it('formats field errors and network failures', () => {
    expect(new ApiError(400, { password: ['Too short.', 'Too common.'] }).message).toBe('password: Too short. Too common.');
    expect(new ApiError(400, { non_field_errors: ['Nope'] }).message).toBe('Nope');
    expect(new ApiError(0, null).message).toMatch(/Network error/);
  });

  it('returns null for 204 responses', async () => {
    mockApi({ 'DELETE /api/saved/x/': { ok: true, status: 204, json: async () => null } });
    document.cookie = 'csrftoken=t';
    expect(await request('/api/saved/x/', { method: 'DELETE' })).toBeNull();
  });

  it('caches catalogue lookups', async () => {
    const { fetchMock } = mockApi({ 'GET /api/categories/': [] });
    await api.categories();
    await api.categories();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it('builds download links', () => {
    expect(api.downloadUrl('gdp_growth', 'csv')).toBe('/api/indicators/gdp_growth/download/?format=csv');
  });
});

describe('chart building', () => {
  it('registers a controller for every chart type the app renders', () => {
    for (const type of ['line', 'bar', 'pie', 'doughnut']) expect(ChartJS.registry.getController(type)).toBeTruthy();
  });
  it('folds long pie tails into Other and drops non-positive slices', () => {
    const labels = Array.from({ length: 15 }, (_, index) => `P${index}`);
    const values = labels.map((_, index) => 15 - index);
    values[3] = null;
    values[4] = 0;
    const points = radialPoints(labels, values);
    expect(points).toHaveLength(12);
    expect(points[0]).toEqual({ label: 'P0', value: 15 });
    expect(points.at(-1).label).toBe('Other (2)');
    expect(points.map(point => point.label)).not.toContain('P3');
  });

  it('builds pie data with one colour per slice', () => {
    const data = buildChartData({ labels: ['A', 'B'], datasets: [{ label: 'Seats', values: [3, 5] }], type: 'doughnut', color: '#fff' });
    expect(data.labels).toEqual(['B', 'A']);
    expect(data.datasets[0].backgroundColor).toHaveLength(2);
  });

  it('builds horizontal bar options and hides axes when compact', () => {
    const options = buildOptions({ type: 'bar', suffix: '', compact: true, horizontal: true, multi: false });
    expect(options.indexAxis).toBe('y');
    expect(options.scales.x.ticks.display).toBe(false);
    expect(options.plugins.tooltip.enabled).toBe(false);
  });

  it('formats tooltips with the right number system', () => {
    const options = buildOptions({ type: 'line', suffix: ' USD', compact: false, horizontal: false, multi: false });
    const label = options.plugins.tooltip.callbacks.label({ parsed: { y: 2e9 }, dataset: { label: 'Exports' } });
    expect(label).toBe(' Exports: 2 billion USD');
    const pie = buildOptions({ type: 'pie', suffix: ' seats', compact: false });
    expect(pie.plugins.tooltip.callbacks.label({ parsed: 30, label: 'BJP', dataset: { data: [30, 70] } })).toBe(' BJP: 30 seats (30.0%)');
  });
});

describe('page helpers', () => {
  it('rebases series to 100', () => {
    expect(normalise([null, 50, 100, null])).toEqual([null, 100, 200, null]);
    expect(normalise([null, 0])).toEqual([null, null]);
  });

  it('only allows same-site redirects after sign-in', () => {
    expect(safeNext('/indicator/x')).toBe('/indicator/x');
    expect(safeNext('//evil.com')).toBe('/saved');
    expect(safeNext('https://evil.com')).toBe('/saved');
    expect(safeNext(null)).toBe('/saved');
  });
});
