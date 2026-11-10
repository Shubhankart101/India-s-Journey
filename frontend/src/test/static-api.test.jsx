import { afterEach, describe, expect, it, vi } from 'vitest';

const category = {
  name: 'Economy & Markets', order: 0, title: 'Economy & Markets', description: 'Growth and prices',
  badges: [], art: 'economy.svg', subgroups: [{ name: 'Growth & Income', order: 0, title: 'Growth & Income', description: '', art: 'growth.svg' }],
};
const indicators = [
  {
    key: 'gdp_growth', title: 'Real GDP growth', subtitle: 'Annual real GDP growth', frequency: 'Annual',
    color: '#ff9933', suffix: '%', source_url: 'https://example.com/gdp', category: category.name,
    subgroup: category.subgroups[0].name, position: 0, details: 'GDP detail',
    series: { labels: ['2020', '2021'], datasets: [{ label: 'GDP', color: '#ff9933', values: [1, 2] }], chart_type: 'line', source: 'Example' },
  },
  {
    key: 'cpi_inflation', title: 'CPI inflation', subtitle: 'Consumer prices', frequency: 'Annual',
    color: '#ff9933', suffix: '%', source_url: 'https://example.com/cpi', category: category.name,
    subgroup: category.subgroups[0].name, position: 1,
    series: { labels: ['2020', '2021'], datasets: [{ label: 'CPI', color: '#ff9933', values: [3, 4] }], chart_type: 'line', source: 'Example' },
  },
];
const snapshot = {
  categories: [category], indicators,
  articles: [{ title: 'Weekly report', url: 'https://example.com/report', published: 'Mon, 02 Nov 2026 12:05:30 GMT', published_at: '2026-11-02T12:05:30Z', publisher: 'Example', kind: 'pew', is_featured: false }],
  'search-index': [['gdp_growth', 'real gdp growth annual economy growth income example'], ['cpi_inflation', 'cpi inflation consumer prices annual economy growth income example']],
  stats: { indicators: 2, articles: 1, source_generated_at: '2026-11-03T00:00:00+00:00' },
};

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
  vi.resetModules();
});

describe('static API mode', () => {
  it('filters, paginates, compares and searches the exported API snapshots', async () => {
    vi.stubEnv('VITE_STATIC', '1');
    vi.stubGlobal('fetch', vi.fn(async input => {
      const name = String(input).split('/').pop().replace('.json', '');
      const value = snapshot[name];
      return { ok: value !== undefined, status: value === undefined ? 404 : 200, json: async () => value };
    }));
    vi.resetModules();
    const { api } = await import('../api.js');

    await expect(api.categories()).resolves.toMatchObject([{ slug: 'economy-markets', badges: [], indicator_count: 2 }]);
    await expect(api.indicators({ q: 'GDP growth', category: 'economy-markets', subgroup: 'growth-income', live: 'true', chart: 'line' }))
      .resolves.toMatchObject({ count: 1, results: [{ key: 'gdp_growth', source_url: 'https://example.com/gdp', color: '#ff9933', suffix: '%' }] });
    await expect(api.indicators({ page_size: 1, page: 2 }))
      .resolves.toMatchObject({ count: 2, results: [{ key: 'cpi_inflation' }] });
    await expect(api.indicator('gdp_growth'))
      .resolves.toMatchObject({ key: 'gdp_growth', source_url: 'https://example.com/gdp', color: '#ff9933', suffix: '%', details: 'GDP detail' });
    await expect(api.compare(['gdp_growth', 'cpi_inflation']))
      .resolves.toMatchObject({ labels: ['2020', '2021'], series: [{ key: 'gdp_growth', values: [1, 2] }, { key: 'cpi_inflation', values: [3, 4] }], missing: [] });
    await expect(api.articles({ kind: 'pew', q: 'weekly', page_size: 1 }))
      .resolves.toMatchObject({ count: 1, results: [{ title: 'Weekly report', published_at: '2026-11-02T12:05:30Z', is_featured: false }] });
  });
});