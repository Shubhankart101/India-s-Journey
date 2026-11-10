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
// A sleeping Render (or stopped Fly.io) instance answers the first requests with gateway errors while it wakes; retry reads before failing.
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
  return new Promise((resolve, reject) => {
    signal.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')), { once: true });
    promise.then(resolve, reject);
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
    staticCatalogPromise = Promise.all(names.map(async name => {
      const response = await fetch(`${import.meta.env.BASE_URL}api/${name}.json`);
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
  category: { ...category, slug: slugify(category.name) },
  subgroups: new Map(category.subgroups.map(subgroup => [subgroup.name, { ...subgroup, slug: slugify(subgroup.name) }])),
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
    color: item.color || '#58a6ff', suffix: item.suffix || '', source_url: item.source_url || '',
    source: series.source || '', category: item.category, category_slug: group?.category.slug || slugify(item.category),
    subgroup: item.subgroup, subgroup_slug: subgroup?.slug || slugify(item.subgroup),
    chart_type: series.chart_type || 'line', index_axis: series.index_axis || 'x', scope: series.scope || '',
    is_live: live, point_count: (series.labels || []).length, first_label: String(series.labels?.[0] || ''),
    latest_label: latestLabel, latest_value: latestValue,
    preview: live ? previewOf(item) : { labels: [], datasets: [] }, updated_at: updatedAt,
  };
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
      return {
        name: category.name, slug: group.category.slug, order: category.order, title: category.title,
        description: category.description || '', badges: category.badges || [], art: category.art || '',
        indicator_count: summary.length, live_count: summary.filter(item => item.is_live).length,
        subgroups: category.subgroups.map(subgroup => {
          const members = summary.filter(item => item.subgroup === subgroup.name);
          return {
            name: subgroup.name, slug: group.subgroups.get(subgroup.name).slug,
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
    };
  }
  if (url.pathname.endsWith('/compare/')) {
    const keys = [...new Set((query.get('keys') || '').split(',').map(key => key.trim()).filter(Boolean))];
    if (!keys.length) throw new ApiError(400, { detail: 'Pass ?keys=a,b with up to four indicator keys.' });
    if (keys.length > 4) throw new ApiError(400, { detail: 'Compare at most 4 indicators.' });
    const records = keys.map(key => catalog.indicators.find(item => item.key === key)).filter(Boolean);
    const missing = keys.filter(key => !catalog.indicators.some(item => item.key === key));
    const labels = [...new Set(records.flatMap(item => normalizedSeries(item).labels || []))];
    if (labels.every(label => /^\d{4}/.test(label))) labels.sort();
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
};
