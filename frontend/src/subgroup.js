import { api } from './api.js';
import explainers from './data/group-explainers.json';
import { mapPoints } from './components/IndiaMap.jsx';

export const slugify = value => String(value ?? '').toLowerCase().replace(/&/g, ' and ').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
export const MIN_MAP_STATES = 10;

export function articleFor(categoryName, subgroupName) {
  const group = explainers.groups.find(item => item.name === categoryName);
  const subgroup = group?.article.subgroups.find(item => item.name === subgroupName);
  return { group: group?.article, subgroup };
}

export async function loadSubgroupIndicators(categorySlug, subgroupSlug, signal) {
  const items = [];
  for (let page = 1; page < 6; page += 1) {
    const data = await api.indicators({ category: categorySlug, subgroup: subgroupSlug, page_size: 100, page }, signal);
    items.push(...data.results);
    if (!data.next) break;
  }
  return items;
}

export const stemOf = title => String(title || '').replace(/\s+[\u2014\u2013-]\s+map$/i, '').trim();

// "Birth rate by State/UT (2023) — map" -> { base: "Birth rate by State/UT", period: "2023" }
export function splitMetric(title) {
  const text = stemOf(title);
  const match = text.match(/^(.*?)\s*\(([^()]*\d[^()]*)\)\s*$/);
  return match && match[1] ? { base: match[1].trim(), period: match[2].trim() } : { base: text, period: '' };
}

// Map metrics the geometry can draw; the same measure published for several periods becomes one metric with a period switch.
export function buildMetrics(indicators, stateNames) {
  const metrics = [];
  const byBase = new Map();
  indicators.filter(item => item.chart_type === 'map').forEach(indicator => {
    const preview = indicator.preview || {};
    const points = mapPoints(preview.labels || [], preview.datasets?.[0]?.values || [], stateNames);
    if (points.size < MIN_MAP_STATES) return;
    const { base, period } = splitMetric(indicator.title);
    const entry = { key: indicator.key, period, indicator, points };
    if (byBase.has(base)) byBase.get(base).entries.push(entry);
    else {
      const metric = { id: indicator.key, base, suffix: indicator.suffix, entries: [entry] };
      byBase.set(base, metric);
      metrics.push(metric);
    }
  });
  return metrics;
}

export function rankOf(points, name) {
  const value = points.get(name);
  if (value === undefined) return null;
  const sorted = [...points.values()].sort((a, b) => b - a);
  const middle = Math.floor(sorted.length / 2);
  const median = sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
  return { value, rank: sorted.indexOf(value) + 1, total: sorted.length, median };
}

export const ordinal = number => {
  const tens = number % 100;
  const suffix = tens >= 11 && tens <= 13 ? 'th' : ({ 1: 'st', 2: 'nd', 3: 'rd' }[number % 10] || 'th');
  return `${number}${suffix}`;
};
