import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const apiDir = path.join(root, 'docs', 'api');
fs.rmSync(path.join(root, 'docs', 'build'), { recursive: true, force: true });
for (const name of ['assets', 'vendor', 'data']) {
  fs.rmSync(path.join(root, 'docs', name), { recursive: true, force: true });
}
for (const name of [
  'atlas.css', 'compare.js', 'data.js', 'fiscal-data.js', 'fiscal-views.css', 'fiscal-views.js',
  'groupcards.css', 'india-maps.css', 'journeys.css', 'parity.css', 'product-theme.css',
  'scripture-data.js', 'scripture.css', 'scripture.js', 'site.js', 'state-elections.js', 'styles.css',
  'themes.css', 'vintage.css', 'voter-roll.css', 'atlas.js', 'journeys.js', 'vintage.js', 'voter-roll.js',
  'compare-data.js', 'overlays.js', 'data.js', 'openapi.json',
]) fs.rmSync(path.join(root, 'docs', name), { force: true });
const readJson = file => JSON.parse(fs.readFileSync(path.join(root, file), 'utf8'));
const catalog = readJson('data/catalog.json');
const aliases = readJson('frontend/src/data/legacy-aliases.json');
if (!Array.isArray(catalog.categories) || !Array.isArray(catalog.indicators) || !Array.isArray(catalog.articles)) {
  throw new Error('data/catalog.json is missing categories, indicators, or articles');
}
const text = value => String(value || '').toLowerCase();
const searchIndex = catalog.indicators.map(item => [item.key, [item.key.replaceAll('_', ' '), item.title, item.subtitle,
  item.category, item.subgroup, item.frequency, item.suffix, item.series?.source].map(text).join(' ')]);
const live = item => !item.series?.error && (item.series?.labels || []).length > 0
  && (item.series?.datasets || []).some(dataset => (dataset.values || []).some(value => value !== null));
const indicators = catalog.indicators;
const articleDate = value => {
  const timestamp = Date.parse(value || '');
  if (Number.isNaN(timestamp)) return null;
  return new Date(timestamp).toISOString().replace(/\.000Z$/, 'Z');
};
const articles = catalog.articles.map(article => ({
  title: String(article.title || 'Untitled public article').slice(0, 500),
  url: String(article.url || '').slice(0, 700),
  published: String(article.published || '').slice(0, 80),
  published_at: articleDate(article.published),
  publisher: String(article.publisher || '').slice(0, 120),
  kind: ['indian_matrix', 'polity_policy', 'pew', 'other'].includes(article.kind) ? article.kind : 'other',
  is_featured: false,
})).filter(article => /^https?:\/\//i.test(article.url));
const stats = {
  indicators: indicators.length,
  live_indicators: indicators.filter(live).length,
  radial_indicators: indicators.filter(item => ['pie', 'doughnut'].includes(item.series?.chart_type)).length,
  categories: catalog.categories.length,
  subgroups: catalog.categories.reduce((total, category) => total + (category.subgroups || []).length, 0),
  articles: articles.length,
  data_points: indicators.reduce((total, item) => total + (item.series?.labels || []).length, 0),
  source_generated_at: catalog.generated_at_utc || null,
  last_refresh: catalog.generated_at_utc ? new Date(catalog.generated_at_utc).toISOString().replace(/\.000Z$/, 'Z') : null,
};
fs.mkdirSync(apiDir, { recursive: true });
for (const [name, data] of Object.entries({
  categories: catalog.categories,
  indicators,
  articles,
  'search-index': searchIndex,
  stats,
  'legacy-aliases': aliases,
})) {
  fs.writeFileSync(path.join(apiDir, `${name}.json`), `${JSON.stringify(data)}\n`);
}
const oldCatalog = path.join(apiDir, 'catalog.json');
if (fs.existsSync(oldCatalog)) fs.unlinkSync(oldCatalog);
console.log(`Exported static API (${indicators.length} indicators, ${catalog.articles.length} articles).`);
