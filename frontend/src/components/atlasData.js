import { loadGeometry } from './IndiaMap.jsx';

const cache = new Map();

// Fetch-once JSON loader for the atlas datasets under /data/ (copied from docs/data by the build scripts).
export function loadAtlasJson(url) {
  if (!cache.has(url)) {
    cache.set(url, fetch(url).then(response => {
      if (!response.ok) throw new Error(`${url}: HTTP ${response.status}`);
      return response.json();
    }).catch(error => { cache.delete(url); throw error; }));
  }
  return cache.get(url);
}

export function loadAtlas(url) {
  return Promise.all([loadAtlasJson(url), loadGeometry()]);
}

export function clearAtlasCache() { cache.clear(); }

export const formatInt = value => Number(value).toLocaleString('en-IN');

export function showTip(event, stage, setTip, content) {
  const box = stage.getBoundingClientRect();
  const target = event.currentTarget.getBoundingClientRect();
  const x = event.clientX ? event.clientX - box.left : target.left - box.left + target.width / 2;
  const y = event.clientY ? event.clientY - box.top : target.top - box.top + target.height / 2;
  setTip({ left: Math.min(Math.max(x + 12, 4), Math.max(box.width - 210, 4)), top: Math.max(y - 10, 4), content });
}
