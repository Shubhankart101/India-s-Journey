// Exports the dashboard's indicator catalogue (definitions, groups, subgroups, chart data and articles)
// to data/catalog.json so the Django app can import exactly what the static site shows.
// It evaluates the definition code from scripts/catalog_sources/app.js in a sandbox, so scripts/catalog_sources/app.js stays the single source of truth.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';
import { resolveSourceUrl } from './source_urls.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const catalogSources = path.join(root, 'scripts', 'catalog_sources');
const read = file => fs.readFileSync(path.join(catalogSources, file), 'utf8');
const readJson = (file, fallback) => {
  try {
    return JSON.parse(fs.readFileSync(path.join(root, 'data', file), 'utf8'));
  } catch {
    return fallback;
  }
};

const appSource = read('app.js');

// Returns the source of `const NAME = {...};` (or `[...]`) using bracket matching that skips strings.
const extractLiteral = name => {
  const start = appSource.search(new RegExp(`const ${name} = [\\[{]`));
  if (start < 0) throw new Error(`Could not find ${name} in scripts/catalog_sources/app.js`);
  const open = appSource.indexOf('=', start) + 1;
  let index = appSource.slice(open).search(/[[{]/) + open;
  let depth = 0;
  let quote = null;
  for (; index < appSource.length; index += 1) {
    const char = appSource[index];
    if (quote) {
      if (char === '\\') index += 1;
      else if (char === quote) quote = null;
      continue;
    }
    if (char === '"' || char === "'" || char === '`') quote = char;
    else if (char === '{' || char === '[') depth += 1;
    else if (char === '}' || char === ']') {
      depth -= 1;
      if (depth === 0) return appSource.slice(start, index + 1) + ';';
    }
  }
  throw new Error(`Unbalanced literal for ${name}`);
};
const extractLine = name => {
  const match = appSource.match(new RegExp(`^\\s*const ${name} = .*$`, 'm'));
  if (!match) throw new Error(`Could not find ${name} in scripts/catalog_sources/app.js`);
  return match[0].trim();
};

const context = vm.createContext({ window: {}, console });
vm.runInContext(read('additional-chart-definitions.js'), context);
const sandboxScript = [
  extractLiteral('definitions'),
  extractLine('categoryFor'),
  extractLine('subgroupFor'),
  'const extraChartPlacement = window.INDIA_EXTRA_CHART_PLACEMENT || {};',
  'definitions.push(...(window.INDIA_EXTRA_CHART_DEFINITIONS || []));',
  extractLine('categoryOrder'),
  extractLine('dashboardCategoryFor'),
  extractLine('dashboardSubgroupFor'),
  extractLiteral('categoryBgMap'),
  extractLiteral('groupHeroData'),
  extractLiteral('subgroupArtMap'),
  extractLiteral('subgroupHeroData'),
  '({ definitions, extraChartPlacement, categoryOrder, dashboardCategoryFor, dashboardSubgroupFor, categoryBgMap, groupHeroData, subgroupArtMap, subgroupHeroData });',
].join('\n');
const app = vm.runInContext(sandboxScript, context);

const payload = readJson('chart-latest.json', { series: {} });
const electionResults = readJson('election-results.json', { series: {} });
const series = {
  ...(payload.series || {}),
  ...(readJson('economic-survey-monthly.json', {}).series || {}),
  ...(readJson('ncrb-and-analyses.json', {}).series || {}),
  ...(readJson('pew-snapshots.json', {}).series || {}),
  ...(electionResults.series || {}),
  ...(readJson('us-campaign-finance.json', {}).series || {}),
  ...(readJson('election-indices.json', {}).series || {}),
  ...(readJson('sports.json', {}).series || {}),
  ...(readJson('atlas-series.json', {}).series || {}),
  ...(readJson('fiscal-series.json', {}).series || {}),
  ...(readJson('niti-reports.json', {}).series || {}),
  ...(readJson('lwe-insurgency.json', {}).series || {}),
};

const definitions = [...app.definitions];
const voterRoll = readJson('voter-roll.json', null);
if (voterRoll?.elections?.length) {
  const electionKey = 'india_lok_sabha_registered_electors';
  const atlasKey = 'india_voter_roll_ssr_sir_atlas';
  series[electionKey] = {
    labels: voterRoll.elections.map(row => row.label),
    values: voterRoll.elections.map(row => row.electors),
    chartType: 'bar',
    source: voterRoll.sources.electors.url,
    note: 'ECI totals from Annexure I, with turnout and population context in the accompanying voter-roll atlas.',
    meta: { title: 'Electors by Lok Sabha election', subtitle: 'Registered electors, 1951–52 to 2024', frequency: 'Per Lok Sabha election', color: '#ff9933', suffix: ' electors', category: 'India in Maps', subgroup: 'Electoral Rolls' },
  };
  series[atlasKey] = {
    labels: ['Interactive atlas'], values: [1], chartType: 'voter-roll', scope: 'module', source: 'https://www.eci.gov.in',
    note: 'An interactive, source-linked guide to Special Summary Revision (SSR), Special Intensive Revision (SIR), roll changes and voter forms.',
    meta: { title: 'Electoral rolls: SSR and SIR', subtitle: 'How rolls are revised, checked and corrected', frequency: 'Interactive explainer', color: '#ff9933', category: 'India in Maps', subgroup: 'Electoral Rolls' },
  };
}(electionResults.india_constituencies || []).forEach((record, index) => {
  const key = `india_live_constituency_vote_composition_${index + 1}`;
  definitions.push([key, `${record.constituency} candidate vote composition`, `Reported candidate votes in ${record.constituency}, ${record.state_or_ut}`,
    'Live ECI snapshot', '#ff9933', ' votes', record.source || 'https://results.eci.gov.in/',
    'Reported candidate votes for this currently published constituency. The five highest-vote candidates are shown individually; remaining candidates, including NOTA where present, are combined as Other candidates. ECI results are provisional until Form 20.']);
  app.extraChartPlacement[key] = { category: 'Elections', subgroup: 'Indian Elections' };
});
const definedKeys = new Set(definitions.map(definition => definition[0]));
const explainDetails = explain => explain ? [['what', 'What it shows'], ['read', 'How to read it'], ['why', 'Why it matters']]
  .filter(([part]) => explain[part]).map(([part, heading]) => `${heading} — ${explain[part]}`).join('\n\n') : '';
for (const [key, item] of Object.entries(series)) {
  const meta = item?.meta;
  if (!meta) continue;
  if (meta.category) app.extraChartPlacement[key] = { category: meta.category, subgroup: meta.subgroup || meta.category };
  if (definedKeys.has(key)) continue;
  definitions.push([key, meta.title, meta.subtitle || '', meta.frequency || 'Periodic', meta.color || '#58a6ff', meta.suffix || '', item.source || '', explainDetails(meta.explain) || item.note || meta.subtitle || '']);
  definedKeys.add(key);
}

// "India in Maps": same derivation as the static site (scripts/catalog_sources/india-maps.js).
vm.runInContext(read('india-maps.js'), context);
const { IndiaMaps } = context.window;
const definitionByKey = new Map(definitions.map(definition => [definition[0], definition]));
const mapGroups = [];
Object.entries(IndiaMaps.deriveMapSeries(series, key => {
  const definition = definitionByKey.get(key);
  return definition && { group: app.dashboardCategoryFor(key), subgroup: app.dashboardSubgroupFor(key), title: definition[1], subtitle: definition[2], frequency: definition[3], color: definition[4], suffix: definition[5] };
}))
  .sort(([, left], [, right]) => (app.categoryOrder[left.meta.sourceGroup] ?? 99) - (app.categoryOrder[right.meta.sourceGroup] ?? 99))
  .forEach(([key, item]) => {
    series[key] = item;
    app.extraChartPlacement[key] = { category: item.meta.category, subgroup: item.meta.subgroup };
    definitions.push([key, item.meta.title, item.meta.subtitle, item.meta.frequency, item.meta.color, item.meta.suffix, definitionByKey.get(item.meta.sourceKey)[6], item.note]);
    if (!mapGroups.includes(item.meta.mapTheme)) mapGroups.push(item.meta.mapTheme);
  });
IndiaMaps.decorate(app, mapGroups);

// Final step: remap everything onto the 10 catalogue groups (scripts/catalog_sources/regroup.js is shared with the static site).
vm.runInContext(read('regroup.js'), context);
const { IndiaRegroup } = context.window;
const regroupState = IndiaRegroup.applyPlacement({
  definitions,
  categoryFor: app.dashboardCategoryFor,
  subgroupFor: app.dashboardSubgroupFor,
  extraChartPlacement: app.extraChartPlacement,
  categoryOrder: app.categoryOrder,
});
IndiaRegroup.applyMeta(app);
const legacyAliases = regroupState.aliases;

const indianMatrix = readJson('indian-matrix-latest.json', { cadence: {}, articles: [] });
const polityPolicy = readJson('substack-latest.json', { articles: [] });
const pewReports = readJson('pew-india-reports.json', { cadence: {}, reports: [] });
const cadence = (key, fallback, source) => {
  const current = series[key]?.values?.length ? series[key] : fallback || {};
  series[key] = { labels: current.labels || [], values: current.values || [], source };
};
cadence('indian_matrix', indianMatrix.cadence, 'Indian Matrix public RSS feed');
cadence('pew_india_reports', pewReports.cadence, 'Pew Research Center India public report catalog');

const marketKeys = [['sensex', 'Sensex', '#58a6ff'], ['nifty', 'Nifty', '#3fb950'], ['nifty_vix', 'Nifty VIX', '#f2cc60']];
const marketLabels = [...new Set(marketKeys.flatMap(([key]) => series[key]?.labels || []))].sort();
series.market_indices = {
  labels: marketLabels,
  datasets: marketKeys.map(([key, label, color]) => {
    const source = series[key] || {};
    const values = new Map((source.labels || []).map((itemLabel, index) => [itemLabel, (source.values || [])[index]]));
    const first = [...values.values()].find(value => value !== null && value !== undefined);
    return { label, color, values: marketLabels.map(itemLabel => (values.has(itemLabel) && first ? values.get(itemLabel) / first * 100 : null)) };
  }),
  source: 'BSE and NSE index histories, rebased to 100',
};

const toNumber = value => (value === null || value === undefined || value === '' || Number.isNaN(Number(value)) ? null : Number(value));
const normaliseSeries = (item, title, color) => {
  if (!item || item.error) return { labels: [], datasets: [], error: item?.error || 'No generated series is available yet' };
  const labels = (item.labels || []).map(String);
  const datasets = item.datasets?.length
    ? item.datasets.map((dataset, index) => ({
      label: dataset.label || `Series ${index + 1}`,
      color: (dataset.color || dataset.borderColor || '').slice(0, 7) || null,
      values: (dataset.values || dataset.data || []).map(toNumber),
    }))
    : item.values?.length ? [{ label: title, color, values: item.values.map(toNumber) }] : [];
  return {
    labels,
    datasets,
    chart_type: item.chartType || 'line',
    index_axis: item.indexAxis || 'x',
    scope: item.scope || '',
    scope_label: item.scopeLabel || '',
    note: item.note || '',
    source: item.source || '',
    unit: item.unit || '',
  };
};

const categoryNames = Object.keys(app.categoryOrder);
const indicators = definitions
  .map(([key, title, subtitle, frequency, color, suffix, sourceUrl, details], index) => ({
    key,
    title,
    subtitle: subtitle || '',
    frequency: frequency || '',
    color: color || '#58a6ff',
    suffix: suffix || '',
    source_url: resolveSourceUrl(sourceUrl, series[key]?.source),
    details: details || '',
    category: app.dashboardCategoryFor(key),
    subgroup: app.dashboardSubgroupFor(key),
    position: index,
    series: normaliseSeries(series[key], title, color || '#58a6ff'),
  }))
  .sort((left, right) => (app.categoryOrder[left.category] ?? 99) - (app.categoryOrder[right.category] ?? 99)
    || IndiaRegroup.subgroupRank(left.key) - IndiaRegroup.subgroupRank(right.key) || left.position - right.position)
  .map((indicator, position) => ({ ...indicator, position }));

const seen = new Set();
const duplicates = indicators.filter(indicator => seen.has(indicator.key) || !seen.add(indicator.key)).map(indicator => indicator.key);
if (duplicates.length) throw new Error(`Duplicate indicator keys: ${duplicates.join(', ')}`);

const artName = artPath => (artPath ? path.basename(artPath) : '');
const categories = [...new Set([...categoryNames, ...indicators.map(indicator => indicator.category)])].map((name, order) => {
  const hero = app.groupHeroData[name] || {};
  const subgroupNames = [...new Set(indicators.filter(indicator => indicator.category === name).map(indicator => indicator.subgroup))];
  return {
    name,
    order,
    title: hero.title || name,
    description: hero.desc || '',
    badges: [hero.badge1, hero.badge2].filter(Boolean),
    color: IndiaRegroup.GROUPS.find(group => group.name === name)?.color || '',
    icon: IndiaRegroup.GROUPS.find(group => group.name === name)?.icon || '',
    art: artName(app.categoryBgMap[name]),
    subgroups: subgroupNames.map((subgroupName, subgroupOrder) => {
      const subHero = app.subgroupHeroData[subgroupName] || {};
      return {
        name: subgroupName,
        order: subgroupOrder,
        title: subHero.title || subgroupName,
        description: subHero.desc || '',
        art: artName(app.subgroupArtMap[subgroupName] || app.categoryBgMap[name]),
      };
    }),
  };
}).filter(category => category.subgroups.length);

const article = (item, publisher, kind) => ({
  title: item.title || 'Untitled public article',
  url: item.link || item.url || '',
  published: item.published || item.date || '',
  publisher,
  kind,
});
const articles = [
  ...(indianMatrix.articles?.length ? indianMatrix.articles : payload.indian_matrix_articles || []).map(item => article(item, 'Indian Matrix', 'indian_matrix')),
  ...(polityPolicy.articles?.length ? polityPolicy.articles : payload.polity_policy_articles || []).map(item => article(item, 'Polity and Policy', 'polity_policy')),
  ...(pewReports.reports?.length ? pewReports.reports : payload.pew_reports || []).map(item => article(item, 'Pew Research Center', 'pew')),
].filter(item => item.url.startsWith('http'));

const catalog = {
  generated_at_utc: payload.generated_at_utc || new Date().toISOString(),
  categories,
  legacy_aliases: legacyAliases,
  indicators,
  articles,
};
const outFile = process.argv[2] ? path.resolve(process.argv[2]) : path.join(root, 'data', 'catalog.json');
fs.mkdirSync(path.dirname(outFile), { recursive: true });
fs.writeFileSync(outFile, `${JSON.stringify(catalog)}\n`);
if (!process.argv[2]) {
  const aliasFile = path.join(root, 'frontend', 'src', 'data', 'legacy-aliases.json');
  fs.writeFileSync(aliasFile, `${JSON.stringify(legacyAliases)}\n`);
}
const live = indicators.filter(indicator => indicator.series.datasets.length).length;
console.log(`Exported ${indicators.length} indicators (${live} with data), ${categories.length} groups and ${articles.length} articles to ${path.relative(root, outFile)}`);
