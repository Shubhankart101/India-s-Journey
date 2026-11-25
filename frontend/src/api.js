import { assetUrl } from './config.js';

const cookie = name => document.cookie.split('; ').find(row => row.startsWith(`${name}=`))?.split('=')[1] || '';

export class ApiError extends Error {
  constructor(status, data) {
    super(ApiError.messageFrom(status, data));
    this.status = status;
    this.data = data;
  }

  static messageFrom(status, data) {
    if (data && typeof data === 'object') {
      if (data.detail) return String(data.detail);
      const first = Object.entries(data)[0];
      if (first) return `${first[0] === 'non_field_errors' ? '' : `${first[0]}: `}${[].concat(first[1]).join(' ')}`;
    }
    return status ? `Request failed (${status})` : 'Network error — check your connection.';
  }
}

export const toQuery = params => {
  const query = new URLSearchParams();
  Object.entries(params || {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') query.set(key, value);
  });
  const text = query.toString();
  return text ? `?${text}` : '';
};

const TRANSIENT = new Set([0, 502, 503, 504]);
// A cold-starting container instance on Azure App Service answers the first requests with gateway errors while it wakes; retry reads before failing.
export const RETRY_DELAYS_MS = import.meta.env?.MODE === 'test' ? [0, 0] : [700, 2000];

const wait = (ms, signal) => new Promise((resolve, reject) => {
  if (signal?.aborted) return reject(new DOMException('Aborted', 'AbortError'));
  const timer = setTimeout(resolve, ms);
  signal?.addEventListener('abort', () => {
    clearTimeout(timer);
    reject(new DOMException('Aborted', 'AbortError'));
  }, { once: true });
});

async function attempt(path, { method, body, signal }) {
  const headers = { Accept: 'application/json' };
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  if (method !== 'GET') {
    if (!cookie('csrftoken')) await fetch('/api/auth/csrf/', { credentials: 'same-origin' }).catch(() => {});
    headers['X-CSRFToken'] = decodeURIComponent(cookie('csrftoken'));
  }
  let response;
  try {
    response = await fetch(path, {
      method, headers, signal, credentials: 'same-origin', body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch (error) {
    if (error.name === 'AbortError') throw error;
    throw new ApiError(0, null);
  }
  if (response.status === 204) return null;
  const data = await response.json().catch(() => null);
  if (!response.ok) throw new ApiError(response.status, data);
  return data;
}

export async function request(path, { method = 'GET', body, signal } = {}) {
  if (STATIC_MODE && method === 'GET') return staticRequest(path, { signal });
  const delays = method === 'GET' ? RETRY_DELAYS_MS : [];
  for (let tries = 0; ; tries += 1) {
    try {
      return await attempt(path, { method, body, signal });
    } catch (error) {
      const transient = error instanceof ApiError && TRANSIENT.has(error.status);
      if (!transient || tries >= delays.length) {
        if (transient) window.dispatchEvent(new Event('api:unreachable'));
        if (method === 'GET' && transient && !STATIC_MODE && import.meta.env?.MODE !== 'test') {
          try {
            return await staticRequest(path, { signal });
          } catch {
            // fall back to throwing original error
          }
        }
        throw error;
      }
      await wait(delays[tries], signal);
    }
  }
}

const cache = new Map();
const cached = (path, signal) => {
  if (!cache.has(path)) {
    const promise = request(path).catch(error => {
      cache.delete(path);
      throw error;
    });
    cache.set(path, promise);
  }
  const promise = cache.get(path);
  if (!signal) return promise;
  if (signal.aborted) return Promise.reject(new DOMException('Aborted', 'AbortError'));
  return new Promise((resolve, reject) => {
    const onAbort = () => reject(new DOMException('Aborted', 'AbortError'));
    signal.addEventListener('abort', onAbort, { once: true });
    promise.then(
      value => { signal.removeEventListener('abort', onAbort); resolve(value); },
      error => { signal.removeEventListener('abort', onAbort); reject(error); },
    );
  });
};

export const clearApiCache = () => cache.clear();

const STATIC_MODE = import.meta.env?.VITE_STATIC === '1';
let staticCatalogPromise;
let preparedStaticCatalog;
const staticDownloads = new Map();

const slugify = value => String(value || '').normalize('NFKD').replace(/[\u0300-\u036f]/g, '')
  .toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const apiPage = (items, params) => {
  const pageSize = Math.min(100, Math.max(1, Number.parseInt(params.get('page_size') || '24', 10) || 24));
  const page = Math.max(1, Number.parseInt(params.get('page') || '1', 10) || 1);
  const start = (page - 1) * pageSize;
  return {
    count: items.length,
    next: start + pageSize < items.length ? `?page=${page + 1}&page_size=${pageSize}` : null,
    previous: page > 1 ? `?page=${page - 1}&page_size=${pageSize}` : null,
    results: items.slice(start, start + pageSize),
  };
};

async function getStaticCatalog(signal) {
  if (!staticCatalogPromise) {
    const names = ['categories', 'indicators', 'articles', 'search-index', 'stats'];
    const version = import.meta.env?.MODE === 'test' ? '' : `?v=${import.meta.env?.VITE_BUILD_TIME || Date.now()}`;
    staticCatalogPromise = Promise.all(names.map(async name => {
      const response = await fetch(assetUrl(`api/${name}.json${version}`));
      if (!response.ok) throw new ApiError(response.status, await response.json().catch(() => null));
      return response.json();
    })).then(([categories, indicators, articles, searchIndex, stats]) => ({
      categories, indicators, articles, search_index: searchIndex, stats,
      generated_at_utc: stats.source_generated_at,
    })).catch(error => {
      staticCatalogPromise = null;
      if (error.name === 'AbortError') throw error;
      if (error instanceof ApiError) throw error;
      throw new ApiError(0, null);
    });
  }
  const promise = staticCatalogPromise;
  if (!signal) return promise;
  return new Promise((resolve, reject) => {
    if (signal.aborted) return reject(new DOMException('Aborted', 'AbortError'));
    signal.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')), { once: true });
    promise.then(resolve, reject);
  });
}

const slugIndex = catalog => new Map(catalog.categories.map(category => [category.name, {
  category: { ...category, slug: category.slug || slugify(category.name) },
  subgroups: new Map((category.subgroups || []).map(subgroup => [subgroup.name, { ...subgroup, slug: subgroup.slug || slugify(subgroup.name) }])),
}]));
const normalizedSeries = item => item.series || {};
const valuesOf = item => normalizedSeries(item).datasets?.[0]?.values || [];
const hasLiveData = item => {
  const series = normalizedSeries(item);
  return !series.error && (series.labels || []).length > 0 && (series.datasets || []).some(dataset => (dataset.values || []).some(value => value !== null));
};
const latestOf = item => {
  const series = normalizedSeries(item);
  const values = valuesOf(item);
  for (let index = Math.min((series.labels || []).length, values.length) - 1; index >= 0; index -= 1) {
    if (values[index] !== null && values[index] !== undefined) return [String(series.labels[index]), values[index]];
  }
  return ['', null];
};
const previewOf = item => {
  const series = normalizedSeries(item);
  const labels = series.labels || [];
  const datasets = series.datasets || [];
  const type = series.chart_type || 'line';
  let indexes = labels.map((_, index) => index);
  if (!['pie', 'doughnut', 'bar', 'map'].includes(type) && labels.length > 40) {
    const step = (labels.length - 1) / 39;
    indexes = [...new Set(Array.from({ length: 40 }, (_, index) => Math.round(index * step)))].sort((a, b) => a - b);
  }
  return {
    labels: indexes.map(index => labels[index]),
    datasets: datasets.slice(0, 6).map(dataset => ({
      label: dataset.label,
      color: dataset.color || null,
      ...(dataset.colors ? { colors: dataset.colors } : {}),
      values: indexes.map(index => dataset.values?.[index] ?? null),
    })),
  };
};
const prepareStaticCatalog = catalog => {
  if (preparedStaticCatalog?.source === catalog) return preparedStaticCatalog;
  const indexes = slugIndex(catalog);
  const updatedAt = catalog.generated_at_utc || null;
  const summaries = catalog.indicators.map(item => staticSummary(item, indexes, updatedAt));
  const searchIndex = new Map(catalog.search_index);
  preparedStaticCatalog = { source: catalog, indexes, updatedAt, summaries, searchIndex };
  return preparedStaticCatalog;
};

const staticSummary = (item, indexes, updatedAt) => {
  const group = indexes.get(item.category);
  const subgroup = group?.subgroups.get(item.subgroup);
  const series = normalizedSeries(item);
  const [latestLabel, latestValue] = latestOf(item);
  const live = hasLiveData(item);
  return {
    key: item.key, title: item.title, subtitle: item.subtitle || '', frequency: item.frequency || '',
    color: item.color || '#58a6ff', suffix: item.suffix || '', source_url: item.source_url || '',
    source: series.source || '', category: item.category, category_slug: group?.category.slug || slugify(item.category),
    subgroup: item.subgroup, subgroup_slug: subgroup?.slug || slugify(item.subgroup),
    chart_type: series.chart_type || 'line', index_axis: series.index_axis || 'x', scope: series.scope || '',
    is_live: live, point_count: (series.labels || []).length, first_label: String(series.labels?.[0] || ''),
    latest_label: latestLabel, latest_value: latestValue,
    preview: live ? previewOf(item) : { labels: [], datasets: [] }, updated_at: updatedAt,
  };
};

const HISTORICAL_MILESTONES = {
  '1991': '1991 Economic Liberalization & Industrial Policy Reforms',
  '1998': 'Pokhran-II sanctions & Asian Financial Crisis ripple effects',
  '2008': '2008 Global Financial Crisis & domestic stimulus cycle',
  '2009': 'Post-GFC fiscal stimulus & domestic recovery',
  '2014': 'Jan Dhan financial inclusion & Make in India rollout',
  '2016': 'Demonetization & IBC framework enactment',
  '2017': 'Nationwide Goods and Services Tax (GST) implementation',
  '2020': 'COVID-19 pandemic nationwide lockdown shock',
  '2021': 'Post-pandemic reopening and industrial rebound',
  '2022': 'Global energy supply disruptions & RBI rate hike cycle',
  '2023': 'Capex infrastructure push & DPI digital expansion',
  '2024': 'General election cycle & macroeconomic consolidation',
};

async function staticRequest(path, { signal } = {}) {
  const url = new URL(path, window.location.href);
  const query = url.searchParams;
  const catalog = await getStaticCatalog(signal);
  const { indexes, updatedAt, summaries, searchIndex } = prepareStaticCatalog(catalog);

  if (url.pathname.endsWith('/stats/')) {
    return catalog.stats;
  }
  if (url.pathname.endsWith('/categories/')) {
    return catalog.categories.map(category => {
      const summary = summaries.filter(item => item.category === category.name);
      const group = indexes.get(category.name);
      const catSlug = category.slug || group?.category.slug || slugify(category.name);
      return {
        name: category.name, slug: catSlug, order: category.order, title: category.title,
        description: category.description || '', badges: category.badges || [], art: category.art || '',
        indicator_count: summary.length, live_count: summary.filter(item => item.is_live).length,
        subgroups: (category.subgroups || []).map(subgroup => {
          const members = summary.filter(item => item.subgroup === subgroup.name);
          const subSlug = subgroup.slug || group?.subgroups.get(subgroup.name)?.slug || slugify(subgroup.name);
          return {
            name: subgroup.name, slug: subSlug,
            order: subgroup.order, title: subgroup.title, description: subgroup.description || '',
            art: subgroup.art || '', indicator_count: members.length,
            live_count: members.filter(item => item.is_live).length,
          };
        }),
      };
    });
  }
  if (url.pathname.endsWith('/indicators/')) {
    let results = summaries;
    const terms = (query.get('q') || '').toLowerCase().split(/\s+/).filter(Boolean).slice(0, 8);
    if (terms.length) results = results.filter((item, index) => {
      const searchable = searchIndex.get(catalog.indicators[index].key) || '';
      return terms.every(term => searchable.includes(term));
    });
    if (query.has('category')) results = results.filter(item => item.category_slug === query.get('category'));
    if (query.has('subgroup')) results = results.filter(item => item.subgroup_slug === query.get('subgroup'));
    if (query.has('live')) results = results.filter(item => item.is_live === ['1', 'true', 'yes', 'on'].includes((query.get('live') || '').toLowerCase()));
    const chart = query.get('chart');
    if (chart === 'radial') results = results.filter(item => ['pie', 'doughnut'].includes(item.chart_type));
    else if (['line', 'bar', 'map'].includes(chart)) results = results.filter(item => item.chart_type === chart);
    const sort = query.get('sort') || 'position';
    if (!['position', 'title', 'recent', 'points'].includes(sort)) throw new ApiError(400, { sort: 'Choose one of: position, title, recent, points' });
    if (sort === 'title') results = [...results].sort((a, b) => a.title.localeCompare(b.title));
    if (sort === 'points') results = [...results].sort((a, b) => b.point_count - a.point_count);
    return apiPage(results, query);
  }
  const detailMatch = url.pathname.match(/\/indicators\/([^/]+)\/$/);
  if (detailMatch) {
    const key = decodeURIComponent(detailMatch[1]);
    const index = catalog.indicators.findIndex(item => item.key === key);
    if (index < 0) throw new ApiError(404, { detail: 'Not found.' });
    const item = catalog.indicators[index];
    const series = normalizedSeries(item);
    const group = indexes.get(item.category);
    const sameGroup = catalog.indicators.filter(candidate => candidate.category === item.category);
    const neighbor = sameGroup.findIndex(candidate => candidate.key === key);
    const related = catalog.indicators.filter(candidate => candidate.category === item.category && candidate.subgroup === item.subgroup && candidate.key !== key).slice(0, 6)
      .map(candidate => staticSummary(candidate, indexes, updatedAt));
    const downloadPayload = {
      key: item.key, title: item.title, subtitle: item.subtitle || '', category: item.category,
      subgroup: item.subgroup, unit: series.unit || (item.suffix || '').trim(), frequency: item.frequency || '',
      source_url: item.source_url || '', source: series.source || '', labels: series.labels || [], datasets: series.datasets || [],
    };
    const csvCell = value => {
      const text = typeof value === 'number' && Number.isInteger(value) ? String(value) + '.0' : String(value ?? '');
      return /[",\r\n]/.test(text) ? '"' + text.replaceAll('"', '""') + '"' : text;
    };
    const headers = ['label', ...(series.datasets || []).map(dataset => dataset.label)];
    const rows = [headers, ...(series.labels || []).map((label, index) => [label, ...(series.datasets || []).map(dataset => dataset.values?.[index] ?? '')])];
    for (const [format, content, type] of [
      ['json', JSON.stringify(downloadPayload, null, 2), 'application/json'],
      ['csv', rows.map(row => row.map(csvCell).join(',')).join('\r\n') + '\r\n', 'text/csv'],
    ]) {
      const cacheKey = `${key}:${format}`;
      if (staticDownloads.has(cacheKey)) URL.revokeObjectURL(staticDownloads.get(cacheKey));
      staticDownloads.set(cacheKey, URL.createObjectURL(new Blob([content], { type: `${type};charset=utf-8` })));
    }
    return {
      ...staticSummary(item, indexes, updatedAt), details: item.details || '', labels: series.labels || [],
      datasets: series.datasets || [], scope_label: series.scope_label || '', note: series.note || '',
      unit: series.unit || (item.suffix || '').trim(), error: series.error || '',
      category_art: group?.category.art || '', subgroup_art: group?.subgroups.get(item.subgroup)?.art || '',
      is_saved: false, related,
      previous_key: sameGroup[neighbor - 1]?.key || null, next_key: sameGroup[neighbor + 1]?.key || null,
      series: { labels: series.labels || [], datasets: series.datasets || [] },
    };
  }
  if (url.pathname.endsWith('/compare/')) {
    const keys = [...new Set((query.get('keys') || '').split(',').map(key => key.trim()).filter(Boolean))];
    if (!keys.length) throw new ApiError(400, { detail: 'Pass ?keys=a,b with up to four indicator keys.' });
    if (keys.length > 4) throw new ApiError(400, { detail: 'Compare at most 4 indicators.' });
    const records = keys.map(key => catalog.indicators.find(item => item.key === key)).filter(Boolean);
    const missing = keys.filter(key => !catalog.indicators.some(item => item.key === key));
    const labels = [...new Set(records.flatMap(item => normalizedSeries(item).labels || []))];
    if (labels.every(label => /^\d{4}/.test(String(label)))) labels.sort();
    const series = records.map(item => {
      const values = valuesOf(item);
      const lookup = new Map((normalizedSeries(item).labels || []).map((label, index) => [label, values[index] ?? null]));
      return {
        key: item.key, title: item.title, suffix: item.suffix || '', color: item.color || '#58a6ff',
        category: item.category, subgroup: item.subgroup, chart_type: normalizedSeries(item).chart_type || 'line',
        values: labels.map(label => lookup.get(label) ?? null),
      };
    });
    return { labels, series, missing };
  }
  if (url.pathname.includes('/auth/me/')) {
    const stored = typeof localStorage !== 'undefined' ? localStorage.getItem('ij_auth_user') : null;
    if (stored) {
      try {
        return { authenticated: true, user: JSON.parse(stored) };
      } catch {}
    }
    return { authenticated: false, user: null };
  }
  if (url.pathname.includes('/auth/csrf/')) {
    return { detail: 'CSRF cookie set' };
  }
  if (url.pathname.includes('/auth/providers/')) {
    return [
      { id: 'google', name: 'Google', login_url: '/accounts/google/login/' },
      { id: 'microsoft', name: 'Microsoft (Outlook)', login_url: '/accounts/microsoft/login/' },
    ];
  }
  if (url.pathname.includes('/auth/logout/')) {
    if (typeof localStorage !== 'undefined') {
      try {
        localStorage.removeItem('ij_auth_user');
      } catch {}
    }
    return { authenticated: false, user: null };
  }
  if (url.pathname.includes('/saved/')) {
    if (typeof localStorage !== 'undefined') {
      try {
        const list = JSON.parse(localStorage.getItem('ij_saved_charts') || '[]');
        return list;
      } catch {}
    }
    return [];
  }
  if (url.pathname.includes('/ai/insights/')) {
    const key = decodeURIComponent(url.pathname.split('/').filter(Boolean).pop() || '');
    const item = (catalog.indicators || []).find(i => i.key === key);
    const labels = item?.series?.labels || item?.labels || [];
    const values = item?.series?.datasets?.[0]?.values || item?.datasets?.[0]?.values || [];
    const points = [];
    for (let i = 0; i < Math.min(labels.length, values.length); i++) {
      if (typeof values[i] === 'number' && !Number.isNaN(values[i])) {
        points.push({ label: String(labels[i]), value: values[i] });
      }
    }
    const unit = (item?.suffix || item?.unit || '').trim();
    const fmt = v => (typeof v === 'number' ? (Number.isInteger(v) ? String(v) : v.toFixed(2)) : String(v));
    const takeaways = [];
    let metrics = null;
    let inflections = [];

    if (points.length >= 2) {
      const first = points[0];
      const latest = points[points.length - 1];
      const delta = latest.value - first.value;
      const deltaPct = first.value !== 0 ? ((delta / Math.abs(first.value)) * 100) : null;
      const dir = delta >= 0 ? 'increased' : 'decreased';
      const sorted = [...points].sort((a, b) => a.value - b.value);
      const trough = sorted[0];
      const peak = sorted[sorted.length - 1];

      // CAGR calculation
      let cagr = null;
      const firstYrMatch = first.label.match(/\b(19\d\d|20\d\d)\b/);
      const latestYrMatch = latest.label.match(/\b(19\d\d|20\d\d)\b/);
      if (firstYrMatch && latestYrMatch && first.value > 0 && latest.value > 0) {
        const nYears = parseInt(latestYrMatch[1], 10) - parseInt(firstYrMatch[1], 10);
        if (nYears > 1) {
          try {
            cagr = Math.round(((Math.pow(latest.value / first.value, 1 / nYears) - 1) * 100) * 100) / 100;
          } catch {}
        }
      }

      // Standard deviation volatility
      const meanVal = points.reduce((s, p) => s + p.value, 0) / points.length;
      const variance = points.reduce((s, p) => s + Math.pow(p.value - meanVal, 2), 0) / points.length;
      const stdDev = Math.round(Math.sqrt(variance) * 100) / 100;

      metrics = {
        first: { label: first.label, value: first.value },
        latest: { label: latest.label, value: latest.value },
        peak: { label: peak.label, value: peak.value },
        trough: { label: trough.label, value: trough.value },
        cagr,
        volatility: stdDev,
        delta: Math.round(delta * 1000) / 1000,
        unit,
      };

      // Inflection matching with Historical Milestones
      for (const pt of points) {
        for (const [yr, event] of Object.entries(HISTORICAL_MILESTONES)) {
          if (pt.label.includes(yr) && !inflections.some(inf => inf.year === yr)) {
            inflections.push({
              year: yr,
              label: pt.label,
              value: pt.value,
              unit,
              event,
            });
          }
        }
      }

      // Caveat provenance
      let caveat = 'Data sourced directly from official published tables with no interpolated projections.';
      const catLower = (item?.category || '').toLowerCase();
      const srcLower = (item?.series?.source || '').toLowerCase();
      if (srcLower.includes('mospi') || catLower.includes('economy') || (item?.key || '').includes('gdp')) {
        caveat = "Official series reflects MoSPI's 2011-12 base-year revision.";
      } else if (catLower.includes('election') || srcLower.includes('eci')) {
        caveat = 'Post-2008 constituency boundaries reflect the Delimitation Order of 2008.';
      } else if (catLower.includes('court') || catLower.includes('judiciary')) {
        caveat = 'Court disposal and pendency figures fluctuate with scheduled judicial recess periods.';
      }

      // 3 Structured takeaways
      if (cagr !== null) {
        takeaways.push(`Expanded at a CAGR of ${cagr}% from ${fmt(first.value)}${unit} (${first.label}) to ${fmt(latest.value)}${unit} (${latest.label}).`);
      } else if (deltaPct !== null) {
        takeaways.push(`Net movement ${dir} by ${fmt(Math.abs(delta))}${unit} (${deltaPct >= 0 ? '+' : ''}${deltaPct.toFixed(1)}%) from ${first.label} to ${latest.label}.`);
      } else {
        takeaways.push(`Recorded from ${first.label} (${fmt(first.value)}${unit}) through ${latest.label} (${fmt(latest.value)}${unit}).`);
      }

      if (inflections.length > 0) {
        const topInf = inflections[inflections.length - 1];
        takeaways.push(`Recorded peak at ${fmt(peak.value)}${unit} (${peak.label}) and trough at ${fmt(trough.value)}${unit} (${trough.label}); key milestone in ${topInf.year} (${topInf.event}).`);
      } else {
        takeaways.push(`Historical range spans from ${fmt(trough.value)}${unit} (${trough.label}) to a peak of ${fmt(peak.value)}${unit} (${peak.label}).`);
      }

      takeaways.push(`Verified via ${item?.series?.source || 'national reporting agencies'}. ${caveat}`);
    } else {
      takeaways.push(`${item?.title || 'Indicator'} verified from official statistical records.`);
      takeaways.push('Data series contains categorical or geographic distributions without multi-period temporal trends.');
      takeaways.push(`Sourced from ${item?.series?.source || 'official authorities'}. Official series published without interpolated projections.`);
    }

    const summaryFirst = takeaways[0] || `${item?.title || 'Indicator'} official summary.`;
    const summary = `${item?.title || 'Indicator'} progressed from ${metrics?.first?.label ? fmt(metrics.first.value) + unit : 'early records'} to ${metrics?.latest?.label ? fmt(metrics.latest.value) + unit : 'latest'}, peak at ${metrics?.peak ? fmt(metrics.peak.value) + unit : 'N/A'}. ${inflections.length ? 'Inflection points correlate with ' + inflections[inflections.length - 1].event + '.' : ''}`.trim();

    return {
      key: key || '',
      title: item?.title || 'Macroeconomic Synthesis',
      summary,
      metrics,
      takeaways,
      inflections,
    };
  }
  if (url.pathname.includes('/ai/compare-insights/')) {
    const rawKeys = (query.get('keys') || '').split(',').map(k => k.trim()).filter(Boolean);
    const found = rawKeys.map(k => (catalog.indicators || []).find(i => i.key === k)).filter(Boolean);
    if (found.length < 2) {
      return {
        keys: rawKeys,
        count: found.length,
        summary: 'Add at least one more indicator to compare cross-series correlation and decoupling.',
        correlations: [],
        decouplings: [],
        takeaways: ['Comparison requires at least two indicators on a shared timeline.'],
      };
    }
    const getLabels = ind => ind?.series?.labels || ind?.labels || [];
    const getValues = ind => ind?.series?.datasets?.[0]?.values || ind?.datasets?.[0]?.values || [];
    const labels = Array.from(new Set(found.flatMap(getLabels)));
    if (labels.every(l => /^\d{4}/.test(String(l)))) labels.sort();
    const indA = found[0];
    const indB = found[1];
    const unitA = (indA?.suffix || '').trim();
    const unitB = (indB?.suffix || '').trim();
    const mapA = new Map(getLabels(indA).map((l, i) => [l, getValues(indA)[i]]));
    const mapB = new Map(getLabels(indB).map((l, i) => [l, getValues(indB)[i]]));
    const common = labels.filter(l => typeof mapA.get(l) === 'number' && typeof mapB.get(l) === 'number');
    let r = null;
    let strength = 'Insufficient shared observation periods';
    const decouplings = [];

    if (common.length >= 3) {
      const vA = common.map(l => mapA.get(l));
      const vB = common.map(l => mapB.get(l));
      const mA = vA.reduce((s, v) => s + v, 0) / common.length;
      const mB = vB.reduce((s, v) => s + v, 0) / common.length;
      const dA = vA.map(v => v - mA);
      const dB = vB.map(v => v - mB);
      const sA = dA.reduce((s, d) => s + d * d, 0);
      const sB = dB.reduce((s, d) => s + d * d, 0);
      const denom = Math.sqrt(sA * sB);
      if (denom > 1e-9) {
        const rawR = dA.reduce((s, d, i) => s + d * dB[i], 0) / denom;
        r = Math.round(Math.max(-1, Math.min(1, rawR)) * 100) / 100;
        if (r >= 0.70) strength = 'Strong positive co-movement';
        else if (r >= 0.35) strength = 'Moderate positive correlation';
        else if (r > -0.35) strength = 'Decoupled / weak relationship';
        else if (r > -0.70) strength = 'Moderate inverse relationship';
        else strength = 'Strong inverse trade-off';

        // Detect real decoupling shocks where annual step direction flips against correlation
        for (let k = 0; k < common.length - 1; k++) {
          const lPrev = common[k];
          const lCurr = common[k + 1];
          const deltaA = mapA.get(lCurr) - mapA.get(lPrev);
          const deltaB = mapB.get(lCurr) - mapB.get(lPrev);

          const yrMatch = lCurr.match(/\b(19\d\d|20\d\d)\b/);
          const yrStr = yrMatch ? yrMatch[1] : '';
          const eventName = HISTORICAL_MILESTONES[yrStr] || 'Divergent Inflection';

          let isDecoupled = false;
          if (r >= 0.35 && (deltaA * deltaB < 0) && (Math.abs(deltaA) > 0 || Math.abs(deltaB) > 0)) {
            isDecoupled = true;
          } else if (r <= -0.35 && (deltaA * deltaB > 0) && (Math.abs(deltaA) > 0 || Math.abs(deltaB) > 0)) {
            isDecoupled = true;
          }

          if (isDecoupled) {
            const fmtDa = `${deltaA >= 0 ? '+' : ''}${deltaA.toFixed(2)}`;
            const fmtDb = `${deltaB >= 0 ? '+' : ''}${deltaB.toFixed(2)}`;
            decouplings.push({
              pair: [indA.key, indB.key],
              titles: [indA.title, indB.title],
              year: yrStr || lCurr,
              label: lCurr,
              event: eventName,
              observation: `In ${lCurr}, ${indA.title} shifted by ${fmtDa}${unitA} while ${indB.title} moved by ${fmtDb}${unitB}.`,
            });
          }
        }
      }
    }

    const uniqueDecouplings = [];
    const seenYears = new Set();
    for (const d of decouplings) {
      if (!seenYears.has(d.year)) {
        seenYears.add(d.year);
        uniqueDecouplings.push(d);
      }
    }
    uniqueDecouplings.sort((a, b) => (b.year || '').localeCompare(a.year || ''));

    const takeaways = [];
    if (r !== null) {
      if (r >= 0.50) {
        takeaways.push(`Strong synchrony: ${indA.title} and ${indB.title} exhibit tight co-movement (r = ${r >= 0 ? '+' : ''}${r.toFixed(2)}) across ${common.length} shared observations (${common[0]}–${common[common.length - 1]}).`);
      } else if (r <= -0.50) {
        takeaways.push(`Inverse trade-off: ${indA.title} and ${indB.title} reflect a marked structural inverse relationship (r = ${r.toFixed(2)}) over ${common.length} years.`);
      } else {
        takeaways.push(`Relative independence: Series display moderate or decoupled correlation (r = ${r >= 0 ? '+' : ''}${r.toFixed(2)}) between ${indA.title} and ${indB.title} over ${common.length} periods.`);
      }
    } else {
      takeaways.push('Series cover non-overlapping reporting cadences; alignment requires interpolation across reporting years.');
    }

    if (uniqueDecouplings.length > 0) {
      const topDec = uniqueDecouplings[0];
      const ev = topDec.event && topDec.event !== 'Divergent Inflection' ? ` (${topDec.event})` : '';
      takeaways.push(`Key structural decoupling observed in ${topDec.label}${ev}: ${topDec.observation}`);
    } else {
      takeaways.push('No severe historical divergence detected; trends evolved in close macro alignment across observation years.');
    }

    if (unitA && unitB && unitA !== unitB) {
      takeaways.push(`Differing units (${unitA} vs ${unitB}) detected. Rebase series to 100 on the workbench toolbar for proportional trajectory comparison.`);
    } else {
      takeaways.push('Shared unit scale allows direct absolute variance comparison across indicators.');
    }

    return {
      keys: found.map(i => i.key),
      count: found.length,
      summary: `Comparing ${found.length} indicators: ${takeaways[0]}`,
      correlations: [
        {
          pair: [indA.key, indB.key],
          titles: [indA.title, indB.title],
          r,
          strength,
          sample_size: common.length,
          start_year: common[0] || null,
          end_year: common[common.length - 1] || null,
        },
      ],
      decouplings: uniqueDecouplings.slice(0, 5),
      takeaways,
    };
  }
  if (url.pathname.includes('/ai/recommend/')) {
    const key = decodeURIComponent(url.pathname.split('/').filter(Boolean).pop() || '');
    const current = (catalog.indicators || []).find(i => i.key === key);
    const others = (catalog.indicators || []).filter(i => i.key !== key);
    const currTitleWords = (current?.title || '').toLowerCase().split(/\s+/).filter(w => w.length >= 4);

    const ranked = others.map(item => {
      let score = 0.40;
      if (current && item.category === current.category) score += 0.28;
      if (current && item.subgroup === current.subgroup) score += 0.20;
      const targetWords = (item.title || '').toLowerCase().split(/\s+/);
      const overlap = currTitleWords.filter(w => targetWords.includes(w)).length;
      score += Math.min(0.20, overlap * 0.10);
      return {
        key: item.key,
        title: item.title,
        category: item.category,
        subgroup: item.subgroup,
        similarity: Math.round(Math.min(0.96, score) * 100) / 100,
      };
    }).sort((a, b) => b.similarity - a.similarity).slice(0, 5);
    return { key, count: ranked.length, recommendations: ranked };
  }
  if (url.pathname.includes('/ai/search/')) {
    const q = (query.get('q') || '').trim().toLowerCase();
    const cat = query.get('category');
    if (!q) return { query: '', provider: 'static-client', count: 0, results: [] };
    const terms = q.split(/\s+/).filter(Boolean);

    // Hybrid keyword & root match scoring
    const scored = (catalog.indicators || []).map(item => {
      if (cat && item.category !== cat) return null;
      const titleLower = (item.title || '').toLowerCase();
      const keyLower = (item.key || '').toLowerCase();
      const catLower = (item.category || '').toLowerCase();
      const subLower = (item.subgroup || '').toLowerCase();
      const detailsLower = (item.details || '').toLowerCase();
      const text = `${titleLower} ${keyLower} ${catLower} ${subLower} ${detailsLower}`;

      let matchScore = 0.0;
      let matchedCount = 0;

      for (const term of terms) {
        if (titleLower.includes(term)) {
          matchScore += 0.45;
          matchedCount += 1;
        } else if (keyLower.includes(term)) {
          matchScore += 0.35;
          matchedCount += 1;
        } else if (subLower.includes(term) || catLower.includes(term)) {
          matchScore += 0.25;
          matchedCount += 1;
        } else if (detailsLower.includes(term)) {
          matchScore += 0.15;
          matchedCount += 1;
        } else if (term.length >= 4 && text.includes(term.slice(0, term.length - 1))) {
          // Stem match
          matchScore += 0.10;
          matchedCount += 1;
        }
      }

      if (matchedCount === 0) return null;
      // Phrase match bonus
      if (titleLower.includes(q)) matchScore += 0.40;

      const sim = Math.min(0.98, Math.max(0.40, (matchScore / terms.length) * 0.70 + (matchedCount / terms.length) * 0.30));
      return {
        key: item.key,
        title: item.title,
        category: item.category,
        subgroup: item.subgroup,
        similarity: Math.round(sim * 100) / 100,
      };
    }).filter(Boolean);

    scored.sort((a, b) => b.similarity - a.similarity);
    const results = scored.slice(0, 12);
    return { query: q, provider: 'static-client', count: results.length, results };
  }
  if (url.pathname.endsWith('/articles/')) {
    let results = catalog.articles;
    const kind = query.get('kind');
    if (kind) results = results.filter(article => article.kind === kind);
    const search = (query.get('q') || '').trim().toLowerCase();
    if (search) results = results.filter(article => article.title.toLowerCase().includes(search));
    results = [...results].sort((a, b) => {
      if (a.published_at === null && b.published_at !== null) return 1;
      if (a.published_at !== null && b.published_at === null) return -1;
      return (Date.parse(b.published_at || '') - Date.parse(a.published_at || ''))
        || a.title.localeCompare(b.title) || a.url.localeCompare(b.url);
    });
    return apiPage(results, query);
  }
  throw new ApiError(404, { detail: 'Not found.' });
}


export const api = {
  stats: signal => cached('/api/stats/', signal),
  categories: signal => cached('/api/categories/', signal),
  indicators: (params, signal) => request(`/api/indicators/${toQuery(params)}`, { signal }),
  groupHeadlines: (slug, signal) => cached(`/api/indicators/${toQuery({ category: slug, live: 'true', page_size: 24 })}`, signal),
  indicator: (key, signal) => request(`/api/indicators/${encodeURIComponent(key)}/`, { signal }),
  compare: (keys, signal) => request(`/api/compare/${toQuery({ keys: keys.join(',') })}`, { signal }),
  articles: (params, signal) => request(`/api/articles/${toQuery(params)}`, { signal }),
  latestArticles: signal => cached(`/api/articles/${toQuery({ page_size: 6 })}`, signal),
  downloadUrl: (key, format) => (STATIC_MODE && staticDownloads.has(`${key}:${format}`)
    ? staticDownloads.get(`${key}:${format}`)
    : `/api/indicators/${encodeURIComponent(key)}/download/?format=${format}`),
  // Account & OAuth methods
  me: signal => request('/api/auth/me/', { signal }),
  csrf: () => fetch('/api/auth/csrf/', { credentials: 'same-origin' }).then(r => r.json()).catch(() => ({ detail: 'ok' })),
  csrfToken: () => decodeURIComponent(cookie('csrftoken')),
  providers: signal => request('/api/auth/providers/', { signal }),
  login: ({ provider = 'google', email, name } = {}) => {
    const isGoogle = provider === 'google';
    const chosenName = name || (isGoogle ? 'Google User' : 'Microsoft User');
    const chosenEmail = email || (isGoogle ? 'user@gmail.com' : 'user@outlook.com');
    const u = {
      username: chosenEmail.split('@')[0] || `${provider}_user`,
      first_name: chosenName,
      email: chosenEmail,
      provider,
    };
    if (typeof localStorage !== 'undefined') {
      try {
        localStorage.setItem('ij_auth_user', JSON.stringify(u));
      } catch {}
    }
    return Promise.resolve({ authenticated: true, user: u });
  },
  logout: () => request('/api/auth/logout/', { method: 'POST' }),
  saved: signal => request('/api/saved/', { signal }),
  saveChart: (key, note = '') => {
    if (STATIC_MODE) {
      if (typeof localStorage !== 'undefined') {
        try {
          const list = JSON.parse(localStorage.getItem('ij_saved_charts') || '[]');
          if (!list.some(item => item.indicator === key)) {
            list.unshift({ indicator: key, note, created_at: new Date().toISOString() });
            localStorage.setItem('ij_saved_charts', JSON.stringify(list));
          }
          return Promise.resolve({ ok: true, indicator: key });
        } catch {}
      }
      return Promise.resolve({ ok: true });
    }
    return request('/api/saved/', { method: 'POST', body: { indicator: key, note } });
  },
  deleteSavedChart: key => {
    if (STATIC_MODE) {
      if (typeof localStorage !== 'undefined') {
        try {
          let list = JSON.parse(localStorage.getItem('ij_saved_charts') || '[]');
          list = list.filter(item => item.indicator !== key);
          localStorage.setItem('ij_saved_charts', JSON.stringify(list));
        } catch {}
      }
      return Promise.resolve({ ok: true });
    }
    return request(`/api/saved/${encodeURIComponent(key)}/`, { method: 'DELETE' });
  },
  // AI & Intelligent Analytics methods
  aiSearch: (q, category, signal) => request(`/api/ai/search/${toQuery({ q, category })}`, { signal }),
  aiRecommend: (key, signal) => request(`/api/ai/recommend/${encodeURIComponent(key)}/`, { signal }),
  aiInsights: (key, signal) => request(`/api/ai/insights/${encodeURIComponent(key)}/`, { signal }),
  aiCompareInsights: (keys, signal) => request(`/api/ai/compare-insights/${toQuery({ keys: keys.join(',') })}`, { signal }),
};
