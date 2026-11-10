import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { api } from '../api.js';
import { useDocumentTitle } from '../hooks.js';
import { loadGeometry, stateKey } from '../components/IndiaMap.jsx';
import IndicatorCard from '../components/IndicatorCard.jsx';
import StateElections from '../components/StateElections.jsx';
import MapSelector from '../components/MapSelector.jsx';
import RegionArticle from '../components/RegionArticle.jsx';
import { pickVerse } from '../scripture.js';
import './Elections.css';

const INDEX_URL = import.meta.env.BASE_URL + 'data/state-elections/index.json';
const LS_URL = import.meta.env.BASE_URL + 'data/lok-sabha-atlas.json';
const cache = new Map();
const loadJSON = url => {
  if (!cache.has(url)) cache.set(url, fetch(url).then(response => {
    if (!response.ok) throw new Error(`Could not load ${url} (${response.status})`);
    return response.json();
  }).catch(error => { cache.delete(url); throw error; }));
  return cache.get(url);
};
const slugify = value => String(value).toLowerCase().replace(/&/g, ' and ').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const fmt = value => new Intl.NumberFormat('en-IN').format(value);

function PageError({ message }) {
  return <p className="elections-status" role="alert">{message}</p>;
}

function ElectionsGroupPage() {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [charts, setCharts] = useState(null);
  const [chartsError, setChartsError] = useState('');
  const [chartsQuery, setChartsQuery] = useState('');
  const [chartsPage, setChartsPage] = useState(1);
  const navigate = useNavigate();
  useDocumentTitle('Elections & Democracy');

  useEffect(() => {
    let active = true;
    Promise.all([loadGeometry(), loadJSON(INDEX_URL)]).then(([geometry, index]) => {
      if (active) setData({ geometry, index });
    }).catch(reason => { if (active) setError(reason.message); });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    (async () => {
      try {
        let page = 1;
        let result = await api.indicators({ category: 'elections-democracy', page_size: 100, page }, controller.signal);
        const items = [...result.results];
        while (result.next && active) {
          const nextUrl = new URL(result.next, window.location.origin);
          page = Number(nextUrl.searchParams.get('page')) || page + 1;
          result = await api.indicators({ category: 'elections-democracy', page_size: 100, page }, controller.signal);
          items.push(...result.results);
        }
        if (active) setCharts(items);
      } catch (reason) {
        if (active && reason.name !== 'AbortError') setChartsError(reason.message);
      }
    })();
    return () => { active = false; controller.abort(); };
  }, []);

  const filteredCharts = useMemo(() => {
    const query = chartsQuery.trim().toLowerCase();
    return (charts || []).filter(item => !query || `${item.title} ${item.subtitle || ''} ${item.subgroup || ''} ${item.source || ''}`.toLowerCase().includes(query));
  }, [charts, chartsQuery]);
  const chartPageCount = Math.max(1, Math.ceil(filteredCharts.length / 24));
  const visibleCharts = filteredCharts.slice((chartsPage - 1) * 24, chartsPage * 24);

  const lookup = useMemo(() => {
    if (!data) return new Map();
    const items = new Map();
    Object.entries(data.index.states).forEach(([name, result]) => items.set(stateKey(name), { name, ...result }));
    Object.entries(data.index.no_assembly || {}).forEach(([name, note]) => items.set(stateKey(name), { name, note, slug: slugify(name) }));
    return items;
  }, [data]);

  const regions = useMemo(() => {
    const map = new Map();
    if (!data) return map;
    Object.keys(data.geometry.states).forEach(name => {
      const item = lookup.get(stateKey(name));
      const summary = item?.latest_headline || item?.note || 'Lok Sabha history';
      map.set(stateKey(name), { fill: item?.lead_latest ? item.lead_latest_colour : undefined, summary, to: `/elections/${item?.slug || slugify(name)}` });
    });
    return map;
  }, [data, lookup]);
  return <>
    <section className="page-hero elections-hero">
      <p className="eyebrow">Elections · India, in numbers</p>
      <h1>How India votes,<br />state by state.</h1>
      <p className="lead">Choose a State or Union Territory to explore its Lok Sabha and Assembly record. The map is shaded by the party with the most seats in its latest Assembly election; it is not an alliance or government map.</p>
      <Link className="elections-guide-link" to="/voter-list-sir-ssr">Read the interactive SIR &amp; SSR voter-roll guide →</Link>
    </section>
    <section className="elections-atlas-section">
      {error ? <PageError message={error} /> : !data ? <p className="elections-status" role="status">Loading the State/UT map…</p> : <MapSelector
        geometry={data.geometry}
        regions={regions}
        heading="Every State and Union Territory"
        intro="Hover for the latest Assembly result. Select a shape or name to open its history."
        ariaLabel="India map selector showing the latest Assembly election winner by State or Union Territory"
        emptyLabel="Lok Sabha history"
        onSelect={to => navigate(to)}
        legend={<><span><i className="elections-legend-party" />Party with most seats in latest Assembly election</span><span><i className="elections-legend-empty" />No Assembly</span></>}
      />}
    </section>    <section className="elections-charts" aria-labelledby="all-election-charts">
      <div className="elections-section-heading"><div><p className="eyebrow">The complete catalogue</p><h2 id="all-election-charts">All charts</h2></div><p>Election indicators beyond the State/UT histories, with each series linked to its source and period.</p></div>
      {chartsError ? <PageError message={`Election charts could not be loaded: ${chartsError}`} /> : charts === null ? <p className="elections-status" role="status">Loading election charts…</p> : <>
        <div className="elections-chart-tools">
          <label>Find a chart<input type="search" value={chartsQuery} onChange={event => { setChartsQuery(event.target.value); setChartsPage(1); }} placeholder="Title, topic or source" /></label>
          <span className="muted">{filteredCharts.length.toLocaleString('en-IN')} of {charts.length.toLocaleString('en-IN')} charts</span>
        </div>
        {filteredCharts.length ? <div className="explore-grid elections-chart-grid">{visibleCharts.map(item => <IndicatorCard key={item.key} indicator={item} />)}</div> : <p className="muted">No election charts match that search.</p>}
        {filteredCharts.length > 24 && <nav className="elections-pagination" aria-label="Election chart pages">
          <button type="button" onClick={() => setChartsPage(page => Math.max(1, page - 1))} disabled={chartsPage <= 1}>Previous</button>
          <span>Page {chartsPage} of {chartPageCount}</span>
          <button type="button" onClick={() => setChartsPage(page => Math.min(chartPageCount, page + 1))} disabled={chartsPage >= chartPageCount}>Next</button>
        </nav>}
      </>}
    </section>
  </>;
}

function StateElectionPage({ slug }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  useEffect(() => {
    let active = true;
    loadJSON(INDEX_URL).then(async index => {
      const entry = [...Object.entries(index.states), ...Object.entries(index.no_assembly || {}).map(([name, note]) => [name, { note }])].find(([stateName, item]) => (item.slug || slugify(stateName)) === slug);
      if (!entry) throw new Error('State or Union Territory not found.');
      const [atlas, stateData] = await Promise.all([
        loadJSON(LS_URL),
        index.states[entry[0]] ? loadJSON(`${import.meta.env.BASE_URL}data/state-elections/${index.states[entry[0]].slug}.json`) : Promise.resolve(null),
      ]);
      if (active) setData({ index, atlas, name: entry[0], stateData });
    }).catch(reason => { if (active) setError(reason.message); });
    return () => { active = false; };
  }, [slug]);

  const name = data?.name;
  useDocumentTitle(name ? `How ${name} voted` : 'State election history');
  if (error) return <><Link className="region-back" to="/elections">← All State/UT results</Link><PageError message={error} /></>;
  if (!data) return <p className="elections-status" role="status">Loading election history…</p>;

  const { atlas, index, stateData } = data;
  const assemblyYears = stateData?.years || [];
  const latestAssembly = assemblyYears[assemblyYears.length - 1];
  const stateLSRows = Object.entries(atlas.states[name] || {}).sort((left, right) => Number(left[0]) - Number(right[0]));
  const stateLSYears = stateLSRows.map(([year]) => atlas.years.find(item => String(item.year) === year)?.label || year);
  const firstLSYear = stateLSYears[0] || 'Not available';
  const latestLSYear = stateLSYears[stateLSYears.length - 1] || 'Not available';
  const latestLS = stateLSRows[stateLSRows.length - 1]?.[1];
  const result = latestAssembly ? `${stateData.parties[latestAssembly.lead]?.name || latestAssembly.lead} · ${latestAssembly.seats[latestAssembly.lead]} of ${latestAssembly.total} seats` : (index.no_assembly?.[name] || 'Assembly data is not available.');
  const intro = latestAssembly
    ? `${name}'s most recent Assembly election was in ${latestAssembly.label}: ${result}. The record below pairs that state contest with its Lok Sabha results, keeping the two legislatures distinct.`
    : `${name} has no elected State Assembly. Its Lok Sabha record is still available below; Union Territory Assembly results are shown only where the territory has a legislature.`;
  const sources = [...(stateData?.sources || []), ...(atlas.meta.sources || [])].filter((source, i, all) => all.findIndex(other => other.url === source.url) === i);
  const states = Object.keys(atlas.states);
  const stateEntry = index.states[name];
  const sections = [{
    title: 'Two ballots, two legislatures',
    text: `${firstLSYear}–${latestLSYear} Lok Sabha results are available for this State/UT beside the Assembly series${stateEntry ? `, which spans ${stateEntry.first}–${stateEntry.last}` : ''}. The lead party is the party winning the most seats in a single election; the figures do not assign coalition governments or chief ministers. Where structured Chief Minister data is not available, the winning-party timeline is shown instead.`,
    content: <StateElections atlas={atlas} states={states} initial={{ state: name, house: stateData ? 'AE' : 'GE' }} onClose={() => navigate('/elections')} includeVerse={false} showTitle={false} />,
  }];
  return <>
    <RegionArticle backTo="/elections" backLabel="All State/UT results"
      headline={`How ${name} voted`}
      dek={intro}
      kicker="Elections · State history"
      sections={sections}
      keyNumbers={[
        { label: 'Latest Assembly result', value: result },
        { label: 'Assembly elections in the record', value: assemblyYears.length ? `${assemblyYears.length} · ${assemblyYears[0].year}–${latestAssembly.year}` : 'No Assembly' },
        { label: 'Lok Sabha coverage', value: `${firstLSYear}–${latestLSYear}` },
        { label: 'Latest Lok Sabha result', value: latestLS ? `${atlas.parties[latestLS.lead]?.name || latestLS.lead} · ${latestLS.seats[latestLS.lead]} of ${latestLS.total}` : 'Not available' },
      ]}
      verse={pickVerse(`state-elections:${name}`, 'India in Maps')}
      sources={sources}
      className="state-election-article"
    />
  </>;
}

export default function Elections() {
  const { stateSlug } = useParams();
  return stateSlug ? <StateElectionPage slug={stateSlug} /> : <ElectionsGroupPage />;
}
