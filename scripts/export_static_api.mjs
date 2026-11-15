import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const apiDir = path.join(root, 'docs', 'api');
for (const name of ['assets', 'vendor', 'build']) {
  fs.rmSync(path.join(root, 'docs', name), { recursive: true, force: true });
}
for (const name of [
  'atlas.css', 'compare.js', 'data.js', 'fiscal-data.js', 'fiscal-views.css', 'fiscal-views.js',
  'groupcards.css', 'india-maps.css', 'journeys.css', 'parity.css', 'product-theme.css',
  'scripture-data.js', 'scripture.css', 'scripture.js', 'site.js', 'state-elections.js', 'styles.css',
  'themes.css', 'vintage.css', 'voter-roll.css', 'atlas.js', 'journeys.js', 'vintage.js', 'voter-roll.js',
  'compare-data.js', 'overlays.js', 'data.js',
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
  image_url: article.image_url || null,
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
const slugify = val => String(val || '').normalize('NFKD').replace(/[\u0300-\u036f]/g, '')
  .toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

const categories = catalog.categories.map(cat => ({
  ...cat,
  slug: cat.slug || slugify(cat.name),
  indicator_count: indicators.filter(i => i.category === cat.name).length,
  subgroups: (cat.subgroups || []).map(sub => {
    const count = indicators.filter(i => i.category === cat.name && i.subgroup === sub.name).length;
    return {
      ...sub,
      indicator_count: count,
      slug: sub.slug || slugify(sub.name),
      art: (sub.art || '').split('?')[0] || (cat.art || '').split('?')[0] || 'parliament.svg',
    };
  }),
}));

fs.mkdirSync(apiDir, { recursive: true });
const publicApiDir = path.join(root, 'frontend', 'public', 'api');
fs.mkdirSync(publicApiDir, { recursive: true });

for (const [name, data] of Object.entries({
  categories,
  indicators,
  articles,
  'search-index': searchIndex,
  stats,
  'legacy-aliases': aliases,
})) {
  const content = `${JSON.stringify(data)}\n`;
  fs.writeFileSync(path.join(apiDir, `${name}.json`), content);
  fs.writeFileSync(path.join(publicApiDir, `${name}.json`), content);
}
const oldCatalog = path.join(apiDir, 'catalog.json');
if (fs.existsSync(oldCatalog)) fs.unlinkSync(oldCatalog);
const openApiSource = path.join(root, 'data', 'openapi.json');
if (fs.existsSync(openApiSource)) {
  fs.copyFileSync(openApiSource, path.join(apiDir, 'openapi.json'));
  fs.copyFileSync(openApiSource, path.join(root, 'docs', 'openapi.json'));
}
console.log(`Exported static API (${indicators.length} indicators, ${catalog.articles.length} articles).`);
