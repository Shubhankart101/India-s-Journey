import { useEffect, useState } from 'react';
import { api } from '../api.js';
import { formatDate } from '../format.js';
import { useAsync, useDebounced, useDocumentTitle } from '../hooks.js';
import { Empty, ErrorState, Loading } from '../components/States.jsx';
import ArtBackdrop from '../components/ArtBackdrop.jsx';

const KINDS = [
  ['', 'All publishers'],
  ['indian_matrix', 'Indian Matrix'],
  ['polity_policy', 'Polity and Policy'],
  ['pew', 'Pew Research Center'],
];

export default function About() {
  useDocumentTitle('About');
  const stats = useAsync(signal => api.stats(signal), []);
  const [kind, setKind] = useState('');
  const [query, setQuery] = useState('');
  const q = useDebounced(query.trim(), 300);
  const [filter, setFilter] = useState({ kind: '', q: '', page: 1 });
  const [items, setItems] = useState([]);
  useEffect(() => {
    setFilter(current => (current.kind === kind && current.q === q ? current : { kind, q, page: 1 }));
  }, [kind, q]);
  const { page } = filter;
  const setPage = update => setFilter(current => ({ ...current, page: update(current.page) }));
  const articles = useAsync(
    signal => api.articles({ kind: filter.kind, q: filter.q, page, page_size: 20 }, signal).then(data => ({ ...data, page })),
    [filter],
  );
  useEffect(() => {
    // Use the page the response belongs to, not the current page, so a pending page change can't duplicate rows.
    if (articles.data) setItems(current => (articles.data.page === 1 ? articles.data.results : [...current, ...articles.data.results]));
  }, [articles.data]);

  return (
    <>
      <section className="page-hero with-art">
        <ArtBackdrop art="heritage-sites.svg" />
        <p className="eyebrow">About the atlas</p>
        <h1>Understand the data, <span className="gradient-text">not just the line.</span></h1>
        {stats.data && (
          <p className="muted">
            {stats.data.indicators.toLocaleString('en-IN')} indicators · {stats.data.subgroups} subgroups · last refresh {formatDate(stats.data.last_refresh) || 'pending'}
          </p>
        )}
      </section>

      <section className="section two-col" id="about">
        <div>
          <span className="eyebrow">The idea behind the atlas</span>
          <h2>Big change is easier to see, one signal at a time.</h2>
          <p>India’s story isn’t a single headline or a single number. This independent, public-data project brings together long-run indicators and current snapshots so you can explore what changed, when it changed, and how the evidence is measured.</p>
          <p>Start with a theme, search for an indicator and narrow the period. Hover for exact values, zoom into a moment, or open any chart for the full series, notes and cited source. Every chart keeps its frequency and limitations visible; unavailable data is never filled with an estimate.</p>
        </div>
        <div>
          <span className="eyebrow">Reading the numbers</span>
          <h2>How numbers are shown</h2>
          <p>Values in U.S. dollars use the international system (thousand, million, billion). Everything else uses the Indian system (lakh, crore).</p>
          <p>Pie charts show the largest eleven slices and fold the rest into “Other”. Additive categorical charts can switch between pie and bar views.</p>
        </div>
      </section>

      <section className="section">
        <span className="eyebrow">Evidence before inference</span>
        <h2>Public data. Clear provenance.</h2>
        <p className="muted">Each graph links to its underlying source and explains its unit and cadence. Some indicators are annual, some are survey snapshots, and some are assembled from official tables. Read the chart note before comparing unlike measures.</p>
        <div className="about-steps">
          <div className="card about-step"><span className="eyebrow">1 · Choose</span><strong>Pick a theme.</strong><span className="muted">Thirteen themes cover the economy, industry, health, security, elections and more. Each has subgroups.</span></div>
          <div className="card about-step"><span className="eyebrow">2 · Inspect</span><strong>Hover, zoom, switch.</strong><span className="muted">Hover for exact values, zoom in, and switch between line, bar and pie views where the data allows.</span></div>
          <div className="card about-step"><span className="eyebrow">3 · Verify</span><strong>Open the source.</strong><span className="muted">Open any chart for the full series, the method and the cited publisher behind each indicator.</span></div>
        </div>
      </section>

      <section className="section two-col">
        <div>
          <h2>Using the data</h2>
          <p>Every indicator has its own page with a CSV and JSON download. The same data is available from the <a href="/api/">JSON API</a>.</p>
          <p>Create an account to save charts. Compare works without an account.</p>
        </div>
      </section>

      <section className="section" id="articles">
        <h2>Articles and reports</h2>
        <div className="filter-row">
          <select aria-label="Publisher" value={kind} onChange={event => setKind(event.target.value)}>
            {KINDS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>
          <label className="search">
            <span className="sr-only">Search articles</span>
            <input type="search" placeholder="Search article titles" value={query} onChange={event => setQuery(event.target.value)} />
          </label>
        </div>
        {articles.error && <ErrorState error={articles.error} onRetry={articles.reload} />}
        {!articles.loading && !articles.error && items.length === 0 && <Empty>No articles match.</Empty>}
        <ul className="article-list">
          {items.map(article => (
            <li key={article.url}>
              <a href={article.url} target="_blank" rel="noopener noreferrer">{article.title}</a>
              <small className="muted">{article.publisher} · {formatDate(article.published_at || article.published)}</small>
            </li>
          ))}
        </ul>
        {articles.loading && <Loading label="Loading articles…" />}
        {articles.data?.next && !articles.loading && (
          <div className="center"><button type="button" className="btn btn-primary" onClick={() => setPage(value => value + 1)}>Load more</button></div>
        )}
      </section>
    </>
  );
}
