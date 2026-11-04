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
// A stopped Fly.io machine answers the first requests with gateway errors while it wakes; retry reads before failing.
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

export const api = {
  stats: signal => cached('/api/stats/', signal),
  categories: signal => cached('/api/categories/', signal),
  indicators: (params, signal) => request(`/api/indicators/${toQuery(params)}`, { signal }),
  groupHeadlines: (slug, signal) => cached(`/api/indicators/${toQuery({ category: slug, live: 'true', page_size: 24 })}`, signal),
  indicator: (key, signal) => request(`/api/indicators/${encodeURIComponent(key)}/`, { signal }),
  compare: (keys, signal) => request(`/api/compare/${toQuery({ keys: keys.join(',') })}`, { signal }),
  articles: (params, signal) => request(`/api/articles/${toQuery(params)}`, { signal }),
  latestArticles: signal => cached(`/api/articles/${toQuery({ page_size: 6 })}`, signal),
  downloadUrl: (key, format) => `/api/indicators/${encodeURIComponent(key)}/download/?format=${format}`,
};
