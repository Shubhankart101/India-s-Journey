import { useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { api } from '../api.js';
import { chartModes, formatMagnitude } from '../format.js';
import { useAsync, useDocumentTitle } from '../hooks.js';
import { pickSubgroupVerse, pickVerse } from '../scripture.js';
import {
  articleFor, buildMetrics, loadSubgroupIndicators, ordinal, rankOf, slugify, stemOf,
} from '../subgroup.js';
import { loadGeometry, stateKey } from './IndiaMap.jsx';
import LazyChart from './LazyChart.jsx';
import MapSelector, { choropleth, QuintileLegend } from './MapSelector.jsx';
import RegionArticle, { RankBars, RegionSwitch } from './RegionArticle.jsx';
import SubgroupArticle from './SubgroupArticle.jsx';
import { ErrorState, Loading } from './States.jsx';

const SPECIAL_HEIGHT = 560;
const SPECIAL_TYPES = new Set(['voter-roll', 'journey-map', 'categorical-map', 'point-map', 'fiscal-matrix', 'fiscal-compare', 'fiscal-spending', 'budget-anatomy']);
const PERIOD_LABEL = /^(19|20)\d{2}/;
const finite = value => value !== null && value !== undefined && Number.isFinite(Number(value));

function figureHeight(indicator, type, labelCount) {
  if (SPECIAL_TYPES.has(indicator.chart_type)) return SPECIAL_HEIGHT;
  if (type === 'bar' && indicator.index_axis === 'y') return Math.min(560, 70 + 26 * labelCount);
  return type === 'doughnut' || type === 'pie' ? 320 : 300;
}

// One inline, interactive chart; maps become a top-ten bar chart because the full map lives in the selector.
export function ChartFigure({ indicator }) {
  const preview = indicator.preview || { labels: [], datasets: [] };
  const modes = chartModes({ ...indicator, labels: preview.labels, datasets: preview.datasets });
  const isMap = indicator.chart_type === 'map';
  const [mode, setMode] = useState(isMap ? 'bar' : modes.initial);
  if (!indicator.is_live) return null;
  let { labels, datasets } = preview;
  let type = mode;
  let axis = indicator.index_axis;
  let note = '';
  if (isMap) {
    const ranked = labels.map((label, index) => [label, datasets[0]?.values?.[index]]).filter(([, value]) => finite(value))
      .sort((a, b) => b[1] - a[1]);
    const top = ranked.slice(0, 10);
    labels = top.map(([label]) => label);
    datasets = [{ ...datasets[0], values: top.map(([, value]) => value) }];
    type = 'bar';
    axis = 'y';
    note = `Top ${top.length} of ${ranked.length} places. Use the map above for every State and UT.`;
  }
  const switchable = !isMap && modes.modes.length > 1;
  return (
    <figure className="subgroup-figure">
      <div className="subgroup-figure-head">
        <h3><Link to={`/indicator/${indicator.key}`}>{stemOf(indicator.title)}</Link></h3>
        {switchable
          ? <div className="subgroup-figure-modes" role="group" aria-label={`Chart type for ${indicator.title}`}>
            {modes.modes.map(item => <button type="button" key={item} aria-pressed={item === mode} onClick={() => setMode(item)}>{item === 'doughnut' || item === 'pie' ? 'Share' : item === 'bar' ? 'Bars' : 'Line'}</button>)}
          </div>
          : <span className="subgroup-figure-latest">{finite(indicator.latest_value) && !SPECIAL_TYPES.has(indicator.chart_type) && indicator.chart_type !== 'journey-map' ? `${formatMagnitude(indicator.latest_value, indicator.suffix)}${indicator.latest_label ? ` · ${indicator.latest_label}` : ''}` : ''}</span>}
      </div>
      <LazyChart
        height={figureHeight(indicator, type, labels.length)}
        title={indicator.title}
        labels={labels}
        datasets={datasets}
        type={type}
        indexAxis={axis}
        suffix={indicator.suffix}
        color={indicator.color}
      />
      {note && <p className="subgroup-figure-note">{note}</p>}
    </figure>
  );
}

function keyNumbersFor(sections, byKey, extra) {
  const numbers = [];
  for (const section of sections) {
    const hit = (section.keys || []).map(key => byKey.get(key)).find(item => item && item.chart_type === 'line' && finite(item.latest_value) && PERIOD_LABEL.test(item.latest_label || ''));
    if (hit && numbers.length < 3) numbers.push({ label: stemOf(hit.title), value: formatMagnitude(hit.latest_value, hit.suffix), note: hit.latest_label });
  }
  return [...numbers, ...extra].slice(0, 4);
}

function AllCharts({ indicators }) {
  if (!indicators.length) return null;
  return (
    <section className="subgroup-all-charts" aria-labelledby="subgroup-all-charts">
      <h2 id="subgroup-all-charts">All charts in this subgroup</h2>
      <ol>
        {indicators.map(item => (
          <li key={item.key}>
            <Link to={`/indicator/${item.key}`}>{stemOf(item.title)}</Link>
            <span>{finite(item.latest_value) && item.chart_type === 'line' ? formatMagnitude(item.latest_value, item.suffix) : item.chart_type}</span>
          </li>
        ))}
      </ol>
    </section>
  );
}

const crumbs = (category, subgroup) => (
  <nav className="subgroup-crumbs" aria-label="Breadcrumb">
    <Link to="/explore">All groups</Link><span aria-hidden="true">/</span>
    <Link to={`/explore?category=${category.slug}`}>{category.name}</Link><span aria-hidden="true">/</span>
    <span aria-current="page">{subgroup.name}</span>
  </nav>
);

export function SubgroupArticleView({ category, subgroup, indicators, lead = null, keyExtra = [], callout = null, sectionsFilter }) {
  const { group, subgroup: article } = articleFor(category.name, subgroup.name);
  const byKey = useMemo(() => new Map(indicators.map(item => [item.key, item])), [indicators]);
  const generated = article?.sections?.length ? article.sections : [{
    title: 'The evidence', text: subgroup.description || '', keys: indicators.slice(0, 5).map(item => item.key),
  }];
  const sections = sectionsFilter ? sectionsFilter(generated) : generated;
  const names = (group?.subgroups || []).map(item => item.name);
  const verse = pickSubgroupVerse(category.name, subgroup.name, names);
  const shown = sections.map(section => ({
    title: section.title,
    text: section.text,
    content: (section.keys || []).length ? <div className="subgroup-figures">{section.keys.map(key => byKey.get(key)).filter(Boolean).map(item => <ChartFigure key={item.key} indicator={item} />)}</div> : null,
  }));
  const extra = [{ label: 'Charts in this subgroup', value: String(indicators.length) }];
  return (
    <>
      {crumbs(category, subgroup)}
      <SubgroupArticle
        headline={article?.headline || subgroup.title || subgroup.name}
        dek={subgroup.description || article?.dek || ''}
        kicker={`${category.name} · ${subgroup.name}`}
        sections={shown}
        keyNumbers={keyNumbersFor(sections, byKey, [...keyExtra, ...extra])}
        quote={article?.pullQuote}
        quoteAfterSection={1}
        verse={verse}
        lead={<>{callout}{lead}</>}
        after={<AllCharts indicators={indicators} />}
        sources={article?.sources || []}
        chipSources
        className="generated-subgroup-article"
      />
    </>
  );
}

const regionHref = (category, subgroup, name) => `/explore/${category.slug}/${subgroup.slug}/${slugify(name)}`;

function SubgroupMap({ category, subgroup, indicators, geometry }) {
  const navigate = useNavigate();
  const metrics = useMemo(() => buildMetrics(indicators, Object.keys(geometry.states)), [indicators, geometry]);
  const [metricId, setMetricId] = useState(metrics[0]?.id);
  const [periodIndex, setPeriodIndex] = useState(null);
  const metric = metrics.find(item => item.id === metricId) || metrics[0];
  const entry = metric.entries[periodIndex ?? metric.entries.length - 1] || metric.entries[metric.entries.length - 1];
  const regions = useMemo(() => {
    const { fillOf } = choropleth(entry.points);
    const map = new Map();
    entry.points.forEach((value, name) => {
      const text = formatMagnitude(value, metric.suffix);
      map.set(stateKey(name), { fill: fillOf(value), summary: `${text}${entry.period ? ` (${entry.period})` : ''}`, detail: text, to: regionHref(category, subgroup, name) });
    });
    Object.keys(geometry.states).forEach(name => {
      const key = stateKey(name);
      if (!map.has(key)) map.set(key, { summary: 'No figure published', detail: 'No figure published', to: regionHref(category, subgroup, name) });
    });
    return map;
  }, [entry, metric, geometry, category, subgroup]);
  const { edges } = choropleth(entry.points);
  return (
    <MapSelector
      geometry={geometry}
      regions={regions}
      heading="Choose a State or Union Territory"
      intro={`Shaded by ${metric.base}${entry.period ? ` (${entry.period})` : ''}. Hover for the figure, select a shape or a name to open that place's page.`}
      ariaLabel={`India map selector shaded by ${metric.base}`}
      onSelect={to => navigate(to)}
      controls={<>
        <label>
          <span>Measure ({metrics.length})</span>
          <select value={metric.id} onChange={event => { setMetricId(event.target.value); setPeriodIndex(null); }} aria-label="Measure shown on the map">
            {metrics.map(item => <option key={item.id} value={item.id}>{item.base}</option>)}
          </select>
        </label>
        {metric.entries.length > 1 && <div className="map-selector-periods" role="group" aria-label="Period">
          {metric.entries.map((item, index) => <button type="button" key={item.key} aria-pressed={item === entry} onClick={() => setPeriodIndex(index)}>{item.period || `View ${index + 1}`}</button>)}
        </div>}
      </>}
      legend={<QuintileLegend edges={edges} format={value => formatMagnitude(value, metric.suffix)} label="Quintile shading" />}
    />
  );
}

function RegionPage({ category, subgroup, indicators, geometry, slug }) {
  const names = Object.keys(geometry.states);
  const name = names.find(item => slugify(item) === slug);
  const metrics = useMemo(() => buildMetrics(indicators, names), [indicators, names]);
  const { group, subgroup: article } = articleFor(category.name, subgroup.name);
  if (!name) return <ErrorState error={new Error('State or Union Territory not found.')} />;
  const rows = metrics.map(metric => {
    const entry = metric.entries[metric.entries.length - 1];
    const standing = rankOf(entry.points, name);
    return standing ? { metric, entry, ...standing } : null;
  }).filter(Boolean);
  const byPosition = [...rows].sort((a, b) => a.rank / a.total - b.rank / b.total);
  const history = metrics.map(metric => {
    const series = metric.entries.map(item => [item.period, item.points.get(name)]).filter(([period, value]) => period && finite(value));
    return series.length > 1 ? { metric, series } : null;
  }).filter(Boolean);
  const stem = row => row.metric.base;
  const sentence = row => `${stem(row)} is ${formatMagnitude(row.value, row.metric.suffix)}${row.entry.period ? ` (${row.entry.period})` : ''}, ${ordinal(row.rank)} of ${row.total}, ${row.value >= row.median ? 'above' : 'below'} the median of ${formatMagnitude(row.median, row.metric.suffix)}.`;
  const best = byPosition[0];
  const lowest = byPosition[byPosition.length - 1];
  const firsts = rows.filter(row => row.rank === 1).length;
  const ranked = (list, key) => list.map(row => (
    <figure className="subgroup-figure" key={`${key}-${row.metric.id}`}>
      <div className="subgroup-figure-head"><h3>{stem(row)}</h3><span className="subgroup-figure-latest">{ordinal(row.rank)} of {row.total}</span></div>
      <RankBars points={row.entry.points} name={name} suffix={row.metric.suffix} />
    </figure>
  ));
  const sections = [{
    title: `Where ${name} stands`,
    text: rows.length ? `${name} has a published figure on ${rows.length} of the ${metrics.length} measures in ${subgroup.name}. ${best ? sentence(best) : ''}` : `${name} has no published figure in this subgroup's maps.`,
    content: rows.length ? <div className="rank-table-wrap"><table className="rank-table">
      <thead><tr><th scope="col">Measure</th><th scope="col">Value</th><th scope="col">Rank</th><th scope="col">Period</th></tr></thead>
      <tbody>{rows.map(row => <tr key={row.metric.id}><td>{stem(row)}</td><td>{formatMagnitude(row.value, row.metric.suffix)}</td><td>{row.rank} / {row.total}</td><td>{row.entry.period || '—'}</td></tr>)}</tbody>
    </table></div> : null,
  }];
  if (byPosition.length >= 2) {
    sections.push({
      title: `Where ${name} ranks highest`,
      text: `Ranks follow the published value, highest first. ${sentence(best)} The bars show ${name} with the places just above and below it.`,
      content: <div className="subgroup-figures">{ranked(byPosition.slice(0, 3), 'top')}</div>,
    });
    sections.push({
      title: `Where ${name} ranks lowest`,
      text: `${sentence(lowest)} A low rank only says the figure sits near the bottom of the published list; read it with the unit and period.`,
      content: <div className="subgroup-figures">{ranked([...byPosition].reverse().slice(0, 3), 'low')}</div>,
    });
  }
  if (history.length) {
    sections.push({
      title: `${name} across periods`,
      text: `${history.length} measure${history.length === 1 ? ' is' : 's are'} published for more than one period, so ${name}'s own history can be followed.`,
      content: <div className="subgroup-figures">{history.slice(0, 5).map(({ metric, series }) => (
        <figure className="subgroup-figure" key={metric.id}>
          <div className="subgroup-figure-head"><h3>{metric.base}</h3></div>
          <LazyChart height={260} title={`${name}: ${metric.base}`} labels={series.map(([period]) => period)} datasets={[{ label: name, values: series.map(([, value]) => value) }]} type="line" suffix={metric.suffix} color="#ff9933" />
        </figure>
      ))}</div>,
    });
  }
  const names2 = (group?.subgroups || []).map(item => item.name);
  return (
    <RegionArticle
      backTo={`/explore/${category.slug}/${subgroup.slug}`}
      backLabel={`All of ${subgroup.name}`}
      switcher={<RegionSwitch names={names} current={name} hrefFor={target => regionHref(category, subgroup, target)} />}
      headline={name}
      dek={rows.length ? `${name} across ${rows.length} measures in ${subgroup.name}. It ranks first on ${firsts} of them; its lowest position is ${ordinal(lowest.rank)} of ${lowest.total} on ${stem(lowest)}.` : `${name} in ${subgroup.name}.`}
      kicker={`${subgroup.name} · State page`}
      sections={sections}
      keyNumbers={[
        { label: 'Measures with a figure', value: `${rows.length} of ${metrics.length}` },
        { label: 'Ranked first on', value: String(firsts) },
        ...(best ? [{ label: 'Highest standing', value: `${ordinal(best.rank)} of ${best.total}`, note: stem(best) }] : []),
        ...(lowest ? [{ label: 'Lowest standing', value: `${ordinal(lowest.rank)} of ${lowest.total}`, note: stem(lowest) }] : []),
      ]}
      verse={pickVerse(`region:${category.name}/${subgroup.name}/${name}`, category.name, pickSubgroupVerse(category.name, subgroup.name, names2).id)}
      sources={article?.sources || []}
      chipSources
      className="generated-subgroup-article region-article"
    />
  );
}

function useSubgroup(categorySlug, subgroupSlug) {
  const categories = useAsync(signal => api.categories(signal), []);
  const category = (categories.data || []).find(item => item.slug === categorySlug);
  const subgroup = category?.subgroups.find(item => item.slug === subgroupSlug);
  const list = useAsync(signal => (category && subgroup ? loadSubgroupIndicators(categorySlug, subgroupSlug, signal) : Promise.resolve([])), [category?.slug, subgroup?.slug]);
  const wantsMap = Boolean(category && subgroup && articleFor(category.name, subgroup.name).subgroup?.format === 'map');
  const geometry = useAsync(signal => (wantsMap ? loadGeometry() : Promise.resolve(null)), [wantsMap]);
  return { categories, category, subgroup, list, wantsMap, geometry };
}

function Shell({ state, children }) {
  const { categories, category, subgroup, list, wantsMap, geometry } = state;
  useDocumentTitle(subgroup?.name || category?.name || 'Explore');
  if (categories.error) return <ErrorState error={categories.error} onRetry={categories.reload} />;
  if (categories.loading || list.loading || (wantsMap && geometry.loading)) return <Loading label="Loading the article…" />;
  if (!category || !subgroup) return <p className="subgroup-page-state" role="alert">That subgroup was not found. <Link to="/explore">Browse every group</Link>.</p>;
  if (list.error) return <ErrorState error={list.error} onRetry={list.reload} />;
  return children({ category, subgroup, indicators: list.data || [], geometry: geometry.data });
}

// Subgroups whose maps can colour at least MIN_MAP_STATES places use the map selector; the rest are long-form articles.
const electionsCallout = (category, subgroup) => (category.slug === 'elections-democracy' || /elections/i.test(subgroup.name)
  ? <p className="subgroup-callout">For results by place, open the <Link to="/elections">State and Union Territory election map</Link>: every Lok Sabha and Assembly history on one clickable India map.</p>
  : null);

export function SubgroupPage({ categorySlug, subgroupSlug }) {
  const state = useSubgroup(categorySlug, subgroupSlug);
  return <Shell state={state}>{({ category, subgroup, indicators, geometry }) => {
    const mapped = geometry ? buildMetrics(indicators, Object.keys(geometry.states)) : [];
    const mapFormat = mapped.length >= 1;
    return <SubgroupArticleView
      category={category}
      subgroup={subgroup}
      indicators={indicators}
      keyExtra={mapFormat ? [{ label: 'Measures on the map', value: String(mapped.length) }] : []}
      lead={mapFormat ? <SubgroupMap category={category} subgroup={subgroup} indicators={indicators} geometry={geometry} /> : null}
      callout={electionsCallout(category, subgroup)}
    />;
  }}</Shell>;
}

export function SubgroupRegionPage({ categorySlug, subgroupSlug, stateSlug }) {
  const state = useSubgroup(categorySlug, subgroupSlug);
  return <Shell state={state}>{({ category, subgroup, indicators, geometry }) => (geometry
    ? <RegionPage category={category} subgroup={subgroup} indicators={indicators} geometry={geometry} slug={stateSlug} />
    : <p className="subgroup-page-state" role="alert">This subgroup has no State/UT pages. <Link to={`/explore/${category.slug}/${subgroup.slug}`}>Back to the article</Link>.</p>)}</Shell>;
}

export function SubgroupRoute() {
  const { group, subgroup, stateSlug } = useParams();
  return stateSlug
    ? <SubgroupRegionPage categorySlug={group} subgroupSlug={subgroup} stateSlug={stateSlug} />
    : <SubgroupPage categorySlug={group} subgroupSlug={subgroup} />;
}
