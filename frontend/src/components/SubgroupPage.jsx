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
import ArtBackdrop from './ArtBackdrop.jsx';
import IndusValleyAtlas from './IndusValleyAtlas.jsx';
import IndusScriptDecoder from './IndusScriptDecoder.jsx';
import AncientEmpiresAtlas from './AncientEmpiresAtlas.jsx';
import GroupArtCarousel from './GroupArtCarousel.jsx';
import empiresData from '../data/ancient-empires.json';
import sitesData from '../data/indus-civilisation.json';
import legacyAliases from '../data/legacy-aliases.json';
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

export function SubgroupArticleView({
  category,
  subgroup,
  indicators,
  lead = null,
  keyExtra = [],
  callout = null,
  sectionsFilter,
  emptySections = false,
  customSections = null,
}) {
  const { group, subgroup: article } = articleFor(category.name, subgroup.name);
  const byKey = useMemo(() => new Map(indicators.map(item => [item.key, item])), [indicators]);
  const isIvc = category.slug === 'indus-valley-civilisation' || (slugify(category.name).includes('indus') && !slugify(category.name).includes('industry')) || slugify(category.name).includes('harapp');
  const isEmpires = category.slug === 'empires-ancient-india' || category.slug === 'empires-of-ancient-india' || slugify(category.name).includes('empire');
  const generated = article?.sections?.length ? article.sections : [{
    title: 'The evidence', text: subgroup.description || '', keys: indicators.slice(0, 5).map(item => item.key),
  }];
  const sections = customSections
    ? customSections
    : ((emptySections || (!customSections && (isIvc || isEmpires))) ? [] : (sectionsFilter ? sectionsFilter(generated) : generated));

  const names = (group?.subgroups || []).map(item => item.name);
  const verse = pickSubgroupVerse(category.name, subgroup.name, names);
  const shown = sections.map(section => ({
    title: section.title,
    text: section.text,
    quote: section.quote,
    content: section.content || ((section.keys || []).length ? <div className="subgroup-figures">{section.keys.map(key => byKey.get(key)).filter(Boolean).map(item => <ChartFigure key={item.key} indicator={item} />)}</div> : null),
  }));
  const extra = indicators.length > 0 ? [{ label: 'Charts in this subgroup', value: String(indicators.length) }] : [];

  // Rotating live artwork playlist for IVC and Empires
  const artPlaylist = isIvc
    ? ['indus-valley.svg', 'ivc-artifacts.svg', 'indus-trade.svg', 'indus-script.svg', 'ivc-excavations.svg']
    : isEmpires
      ? ['ancient-empires.svg', 'mahajanapadas.svg', 'magadha-nanda.svg', 'alexander-campaign.svg', 'maurya-empire.svg', 'indo-greek.svg', 'satavahana-empire.svg', 'kushan-empire.svg', 'gupta-empire.svg', 'harsha-empire.svg', 'southern-dynasties.svg']
      : (subgroup.art || category.art);

  return (
    <>
      <ArtBackdrop art={artPlaylist} />
      {crumbs(category, subgroup)}
      <SubgroupArticle
        headline={article?.headline || subgroup.title || subgroup.name}
        dek={subgroup.description || article?.dek || ''}
        kicker={`${category.name} · ${subgroup.name}`}
        sections={shown}
        emptySections={false}
        keyNumbers={isIvc || isEmpires ? keyExtra : keyNumbersFor(sections, byKey, [...keyExtra, ...extra])}
        quote={article?.pullQuote}
        quoteAfterSection={-1}
        verse={verse}
        lead={<>{callout}{lead}</>}
        after={(sectionsFilter || isIvc || isEmpires) ? null : <AllCharts indicators={indicators} />}
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
    <>
      <ArtBackdrop art={subgroup.art || category.art} />
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
    </>
  );
}

function useSubgroup(categorySlug, subgroupSlug) {
  const categories = useAsync(signal => api.categories(signal), []);
  const normCatSlug = slugify(categorySlug);
  const normSubSlug = slugify(subgroupSlug);

  const isIvcMatch = str => (str.includes('indus') && !str.includes('industry')) || str.includes('harapp');
  const isEmpireMatch = str => str.includes('empire') || str.includes('ancient');

  // Check legacy aliases
  const legacyGroups = legacyAliases?.groups || {};
  const legacySubgroups = legacyAliases?.subgroups || {};

  let targetGroupSlug = '';
  let targetSubSlug = '';
  for (const [key, val] of Object.entries(legacySubgroups)) {
    const parts = key.split('|');
    if (parts.length === 2) {
      const gSlug = slugify(parts[0]);
      const sSlug = slugify(parts[1]);
      if ((gSlug === normCatSlug && sSlug === normSubSlug) || sSlug === normSubSlug) {
        targetGroupSlug = slugify(val.group);
        targetSubSlug = slugify(val.subgroup);
        break;
      }
    }
  }

  if (!targetGroupSlug && legacyGroups) {
    for (const [k, v] of Object.entries(legacyGroups)) {
      if (slugify(k) === normCatSlug) {
        targetGroupSlug = slugify(v);
        break;
      }
    }
  }

  // 1. Robust category resolution matching exact slugs, names, legacy targets, or key substrings
  const category = (categories.data || []).find(item => {
    const itemSlug = slugify(item.slug);
    const itemName = slugify(item.name);
    return (
      item.slug === categorySlug
      || itemSlug === normCatSlug
      || itemName === normCatSlug
      || (targetGroupSlug && (itemSlug === targetGroupSlug || itemName === targetGroupSlug))
      || (isIvcMatch(normCatSlug) && isIvcMatch(itemSlug))
      || (isEmpireMatch(normCatSlug) && isEmpireMatch(itemSlug))
    );
  }) || ((isIvcMatch(normSubSlug) || normSubSlug.includes('script') || normSubSlug.includes('excavation'))
    ? (categories.data || []).find(item => isIvcMatch(slugify(item.slug)))
    : null)
    || ((isEmpireMatch(normSubSlug) || normSubSlug.includes('dynast') || normSubSlug.includes('battle') || normSubSlug.includes('maurya'))
    ? (categories.data || []).find(item => isEmpireMatch(slugify(item.slug)))
    : null)
    || (categories.data || []).find(item => {
      const words = normCatSlug.split('-').filter(w => w.length > 3);
      const catWords = slugify(item.name).split('-');
      return words.some(w => catWords.includes(w));
    })
    || (categories.data?.[0] || null);

  // 2. Robust subgroup resolution:
  const subgroup = category?.subgroups?.find(item => {
    const itemSlug = slugify(item.slug);
    const itemName = slugify(item.name);
    return (
      item.slug === subgroupSlug
      || itemSlug === normSubSlug
      || itemName === normSubSlug
      || (targetSubSlug && (itemSlug === targetSubSlug || itemName === targetSubSlug))
      || (normSubSlug.includes('script') && itemName.includes('script'))
      || (normSubSlug.includes('excavation') && itemName.includes('excavation'))
      || (isIvcMatch(normSubSlug) && isIvcMatch(itemName))
      || (normSubSlug.includes('empire') && itemName.includes('empire'))
      || (normSubSlug.includes('atlas') && itemName.includes('atlas'))
    );
  }) || (category?.subgroups?.find(item => {
    const subWords = normSubSlug.split('-').filter(w => w.length > 3);
    const itemWords = slugify(item.slug).split('-');
    return subWords.some(w => itemWords.includes(w));
  }))
  || (category?.subgroups?.[0] || null);

  const list = useAsync(signal => (category && subgroup ? loadSubgroupIndicators(category.slug, subgroup.slug, signal) : Promise.resolve([])), [category?.slug, subgroup?.slug]);
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

export function buildEmpiresArticleSections(currentEmpire, onSelectEmpire, allEmpires) {
  if (!currentEmpire) return [];
  const hist = currentEmpire.detailed_history || {};
  const chronicle = hist.chronicle || [];
  const primarySources = hist.primary_sources || [];

  return [
    {
      title: `${currentEmpire.name} — Imperial Epoch, Ideological Imperative & Sovereign Zenith`,
      text: hist.overview || currentEmpire.description || '',
      quote: currentEmpire.shloka_epigraph?.translation ? `“${currentEmpire.shloka_epigraph.translation}”` : undefined,
      content: (
        <div className="article-empire-context-card">
          <div className="aecc-toolbar">
            <span className="aecc-label">Select Dynastic Era to Inspect Article Chronicle:</span>
            <div className="aecc-chips">
              {allEmpires.map(emp => (
                <button
                  key={emp.id}
                  type="button"
                  className={`aecc-chip ${emp.id === currentEmpire.id ? 'active' : ''}`}
                  onClick={() => onSelectEmpire(emp.id)}
                >
                  {emp.name.split(':')[0].split('—')[0].trim()}
                </button>
              ))}
            </div>
          </div>
          <div className="aecc-meta-row">
            <div><strong>Period:</strong> {currentEmpire.period}</div>
            <div><strong>Ideology / Faith:</strong> {currentEmpire.religion}</div>
            <div><strong>Imperial Form:</strong> {currentEmpire.era_type}</div>
          </div>
        </div>
      ),
    },
    {
      title: 'Dynastic Chronology & Historical Trajectory',
      text: `Across successive reigns and territorial transformations, the historical evolution of ${currentEmpire.name} is documented through primary epigraphs and classical archaeological strata:`,
      content: (
        <div className="article-chronicle-list">
          {chronicle.map((item, idx) => (
            <div key={idx} className="article-chronicle-item">
              <span className="aci-era-badge">{item.era}</span>
              <p className="aci-narrative">{item.narrative}</p>
            </div>
          ))}
        </div>
      ),
    },
    {
      title: 'Authentic Primary Epigraphic & Classical Documentation Quoted Directly',
      text: `Original epigraphic inscriptions and classical literary accounts quoted verbatim in their original ancient scripts with Romanized transliteration, scholarly translation, and official academic citations:`,
      content: (
        <div className="article-primary-sources-grid">
          {primarySources.map((ps, idx) => (
            <div key={idx} className="article-source-card">
              <div className="asc-top">
                <span className="asc-badge">{ps.type || 'Primary Epigraph'}</span>
                <span className="asc-script">{ps.script || 'Original Script'}</span>
                {ps.date && <span className="asc-date">{ps.date}</span>}
              </div>
              <h4 className="asc-title">{ps.source_title || ps.title}</h4>
              {(ps.author || ps.ruler) && <p className="asc-author"><strong>Author / Sovereign:</strong> {ps.author || ps.ruler}</p>}

              {ps.original_text && (
                <blockquote className="asc-original" lang="sa">
                  {ps.original_text}
                </blockquote>
              )}

              {ps.transliteration && (
                <div className="asc-translit">
                  <span className="asc-label">Transliteration (IAST / Classical):</span>
                  <p><em>{ps.transliteration}</em></p>
                </div>
              )}

              {ps.translation && (
                <div className="asc-translation">
                  <span className="asc-label">English Translation:</span>
                  <p>“{ps.translation}”</p>
                </div>
              )}

              <div className="asc-footer">
                {ps.academic_citation && (
                  <p className="asc-citation"><strong>Academic Citation:</strong> {ps.academic_citation}</p>
                )}
                {(ps.historical_significance || ps.significance) && (
                  <p className="asc-significance"><strong>Historical Significance:</strong> {ps.historical_significance || ps.significance}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      ),
    },
    {
      title: 'Decisive Military Campaigns & Battlefield Coordinates',
      text: `Key military engagements and strategic campaigns that defined the territorial boundaries and geopolitical hegemony of ${currentEmpire.name}:`,
      content: currentEmpire.battles?.length > 0 ? (
        <div className="article-battles-grid">
          {currentEmpire.battles.map((bt, idx) => (
            <div key={idx} className="article-battle-card">
              <div className="abc-header">
                <span className="abc-year">{bt.year}</span>
                <span className="abc-tag">⚔ DECISIVE BATTLE</span>
              </div>
              <h4 className="abc-title">{bt.name}</h4>
              <p className="abc-parties"><strong>Opponents:</strong> {bt.parties}</p>
              <p className="abc-summary">{bt.summary}</p>
              {bt.source && <p className="abc-source"><strong>Ancient Source:</strong> {bt.source}</p>}
            </div>
          ))}
        </div>
      ) : null,
    },
    {
      title: 'Imperial Capitals, Epigraphic Charters & Classical Legacy',
      text: `Administrative viceroyalties, monumental architecture, and scholarly monographs verifying the historical primacy of ${currentEmpire.name}:`,
      content: (
        <div className="article-capitals-sources">
          {currentEmpire.capitals?.length > 0 && (
            <div className="article-capitals-block">
              <h5>Administrative Capitals &amp; Viceroyalties</h5>
              <div className="article-capitals-chips">
                {currentEmpire.capitals.map((cap, idx) => (
                  <div key={idx} className="acc-item">
                    <strong>★ {cap.name}:</strong> <span>{cap.desc || cap.role}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
          {currentEmpire.sources?.length > 0 && (
            <div className="article-sources-block">
              <h5>Peer-Reviewed Academic &amp; Epigraphic Sources</h5>
              <ul className="article-sources-ul">
                {currentEmpire.sources.map((src, idx) => (
                  <li key={idx}>
                    <strong>{src.title}</strong> ({src.year}) — {src.author || src.authors}, <em>{src.publisher}</em>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ),
    },
  ];
}

export function buildIvcArticleSections(sitesData) {
  const periods = sitesData.periods || [];

  return [
    {
      title: 'The Three Chronometric Horizons & Territorial Period Boundaries (3300 – 1300 BCE)',
      text: `The Harappan Civilization developed through three distinct, radiocarbon-calibrated horizons spanning over two millennia: the formative Early Harappan (Regionalisation Era), the peak urban Mature Harappan (Integration Era), and the post-urban Late Harappan (Localisation Era). Territorial boundaries on the map reflect these dynamic shifts across 1.5 million square kilometres:`,
      quote: `“One cannot fail to be impressed by the immense antiquity of this civilization and its vast geographical expanse, which exceeded that of contemporary Egypt and Mesopotamia combined.” — Sir John Marshall, Director-General ASI, 1931`,
      content: (
        <div className="article-ivc-periods-grid">
          {periods.map(p => (
            <div key={p.id} className="article-ivc-period-card" style={{ '--p-color': p.color }}>
              <div className="aipc-header">
                <span className="aipc-badge" style={{ color: p.color, borderColor: p.color }}>{p.badge}</span>
                <span className="aipc-span">{p.span}</span>
              </div>
              <h4 className="aipc-title">{p.name}</h4>
              <p className="aipc-extent"><strong>Geographical Extent:</strong> {p.area_sq_km}</p>
              <p className="aipc-overview">{p.overview}</p>
              <div className="aipc-chronicle">
                <strong className="aipc-chronicle-header">Stratigraphic Phases:</strong>
                <ul>
                  {p.chronicle?.map((c, i) => {
                    const phaseTitle = (c.era || c.phase || c.title || '').trim();
                    const phaseDesc = (c.narrative || c.details || c.text || c.desc || '').trim();
                    if (!phaseTitle && !phaseDesc) return null;
                    return (
                      <li key={i}>
                        {phaseTitle && <strong className="aipc-phase-title">{phaseTitle}</strong>}
                        {phaseDesc && <span className="aipc-phase-desc"> — {phaseDesc}</span>}
                      </li>
                    );
                  })}
                </ul>
              </div>
            </div>
          ))}
        </div>
      ),
    },
    {
      title: 'Quoted Excavation Memoirs & Archaeological Survey of India Monograph Reports',
      text: `Official primary testimonies directly quoted from excavation directors, ASI memoirs (MASI), and peer-reviewed archaeological monographs establishing the stratigraphic reality of Harappan urbanism:`,
      content: (
        <div className="article-primary-sources-grid">
          {periods.flatMap(p => p.primary_sources || []).map((ps, idx) => (
            <div key={idx} className="article-source-card">
              <div className="asc-top">
                <span className="asc-badge">ASI EXCAVATION MEMOIR</span>
                <span className="asc-date">{ps.year}</span>
              </div>
              <h4 className="asc-title">{ps.source_title}</h4>
              <p className="asc-author"><strong>Director / Scholar:</strong> {ps.director}</p>

              <blockquote className="asc-memoir-quote">
                “{ps.quote}”
              </blockquote>

              <div className="asc-footer">
                <p className="asc-citation"><strong>Official Citation:</strong> {ps.citation}</p>
                <p className="asc-significance"><strong>Diagnostic Significance:</strong> {ps.significance}</p>
              </div>
            </div>
          ))}
        </div>
      ),
    },
    {
      title: 'Orthogonal Urban Planning, Underground Drainage & Hydraulic Engineering',
      text: `Every major Harappan metropolis was laid out along a strict cardinal orthogonal grid with standardized 4:2:1 fired-brick metrology. Underground corbelled brick sewer networks with inspection chambers, soak pits, private bathing platforms, and the Great Bath of Mohenjo-daro demonstrate a level of municipal sanitation unmatched anywhere in antiquity until imperial Rome two millennia later. At Dholavira, rock-cut reservoirs impounded over 250,000 cubic meters of storm runoff, engineering survival in arid Kutch.`,
      content: (
        <div className="article-stat-highlights">
          <div className="ash-box">
            <span className="ash-num">4:2:1</span>
            <span className="ash-label">Standardized Brick Ratio</span>
            <p>Uniform across thousands of settlements from the Makran coast to Uttar Pradesh.</p>
          </div>
          <div className="ash-box">
            <span className="ash-num">16</span>
            <span className="ash-label">Rock-Cut Reservoirs</span>
            <p>Impounded water cascade system excavated at Dholavira citadel.</p>
          </div>
          <div className="ash-box">
            <span className="ash-num">100%</span>
            <span className="ash-label">Covered Drainage</span>
            <p>Underground street sewer mains with lime-mortar corbelled vaults.</p>
          </div>
        </div>
      ),
    },
    {
      title: 'Glyptic Seals, Binary-Decimal Metrology & Computational Epigraphy',
      text: `The Harappan glyptic tradition yielded thousands of exquisitely carved steatite stamp seals depicting unicorn bovines, humped bulls, tigers, elephants, and the 'Pashupati' proto-Shiva motif. Indus metrology utilized a strict binary progression (1, 2, 4, 8, 16, 32, 64) in lower denominations transitioning to decimal multiples (160, 200, 320, 640) for larger weights, manufactured with precision of fractions of a gram. Over 400 distinct glyphic signs have been cataloged in the Mahadevan and Parpola concordances, read predominantly right-to-left.`,
    },
    {
      title: 'Long-Distance Maritime Trade Corridors: Meluhha, Dilmun & Mesopotamia',
      text: `Harappan merchants commanded maritime sea lanes across the Arabian Sea, Persian Gulf, and into Mesopotamia. Cuneiform tablets from Sargon of Akkad (c. 2334–2279 BCE) boast of 'ships from Meluhha, Magan, and Dilmun tied up at the quay of Akkad.' The tidal dockyard at Lothal, featuring an engineered 214-meter brick basin with sluice gates, facilitated trans-shipment of carnelian etched beads, lapis lazuli, shell ornaments, ivory dice, and copper ingots across western Asia.`,
    },
  ];
}

function IndusValleyWorkbench() {
  return (
    <div className="ivc-consolidated-workbench">
      <GroupArtCarousel groupSlug="indus-valley-civilisation" title="Indus Valley Civilisation Artworks" />
      <IndusValleyAtlas />
      {/* Docked Dedicated Script Decryption Window below map */}
      <div id="ivc-script-decoder-dock" className="ivc-script-decoder-dock">
        <IndusScriptDecoder />
      </div>
    </div>
  );
}

function AncientEmpiresWorkbench({ selectedEmpireId, onSelectEmpire }) {
  return (
    <div className="empires-consolidated-workbench">
      <GroupArtCarousel groupSlug="empires-of-ancient-india" title="Empires of Ancient India Artworks" />
      <AncientEmpiresAtlas
        selectedEmpireId={selectedEmpireId}
        onSelectEmpire={onSelectEmpire}
      />
    </div>
  );
}

export function SubgroupPage({ categorySlug, subgroupSlug }) {
  const state = useSubgroup(categorySlug, subgroupSlug);
  const [selectedEmpireId, setSelectedEmpireId] = useState('maurya-empire');

  return <Shell state={state}>{({ category, subgroup, indicators, geometry }) => {
    const mapped = geometry ? buildMetrics(indicators, Object.keys(geometry.states)) : [];
    const mapFormat = mapped.length >= 1;
    const isIvc = category.slug === 'indus-valley-civilisation' || (slugify(category.name).includes('indus') && !slugify(category.name).includes('industry')) || slugify(category.name).includes('harapp');
    const isEmpires = category.slug === 'empires-ancient-india' || category.slug === 'empires-of-ancient-india' || slugify(category.name).includes('empire');
    let customLead = null;
    let customKeyExtra = mapFormat ? [{ label: 'Measures on the map', value: String(mapped.length) }] : [];
    let customSections = null;

    if (isIvc) {
      customLead = <IndusValleyWorkbench />;
      customSections = buildIvcArticleSections(sitesData);
      customKeyExtra = [
        { label: 'Cataloged Excavations', value: '49 Sites', note: '9 modern nations' },
        { label: 'Script Corpus', value: '400+ Signs', note: 'Mahadevan concordance' },
        { label: 'Geographical Extent', value: '1.5M km²', note: 'Oxus to Arabian Sea' },
        { label: 'Mature Era Climax', value: '2600–1900 BCE', note: 'Radiocarbon calibrated' },
      ];
    } else if (isEmpires) {
      const allEmpires = empiresData.empires || [];
      const currentEmpire = allEmpires.find(e => e.id === selectedEmpireId) || allEmpires[3] || allEmpires[0];
      customLead = <AncientEmpiresWorkbench selectedEmpireId={selectedEmpireId} onSelectEmpire={setSelectedEmpireId} />;
      customSections = buildEmpiresArticleSections(currentEmpire, setSelectedEmpireId, allEmpires);
      customKeyExtra = [
        { label: 'Major Dynasties', value: '10 Empires', note: 'Magadha to Imperial Cholas' },
        { label: 'Historical Span', value: '1,600+ Years', note: '600 BCE – 850 CE' },
        { label: 'Mahajanapadas', value: '16 States', note: 'Iron Age urbanisation' },
        { label: 'Primary Epigraphs', value: 'Brahmi & Tamil', note: 'Rock edicts & copper plates' },
      ];
    } else if (mapFormat) {
      customLead = <SubgroupMap category={category} subgroup={subgroup} indicators={indicators} geometry={geometry} />;
    }
    return <SubgroupArticleView
      category={category}
      subgroup={subgroup}
      indicators={indicators}
      keyExtra={customKeyExtra}
      lead={customLead}
      callout={electionsCallout(category, subgroup)}
      customSections={customSections}
      emptySections={false}
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
