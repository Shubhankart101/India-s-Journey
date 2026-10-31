import { useEffect, useState } from 'react';
import { api } from '../api.js';
import { formatDate } from '../format.js';
import { useAsync, useDebounced, useDocumentTitle } from '../hooks.js';
import { Empty, ErrorState, Loading } from '../components/States.jsx';

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
      <section className="page-hero with-art" style={{ '--hero-art': 'url(/art/lotus-temple.svg)' }}>
        <p className="eyebrow">About</p>
        <h1>Built on official, public data.</h1>
        <p className="lead">India's Journey collects public series from MOSPI, RBI, the World Bank, the Election Commission of India, the U.S. FEC, NCRB, Pew Research and other official publishers. Scheduled pipelines refresh each dataset on its own release cadence, and every chart links back to its source.</p>
        {stats.data && (
          <p className="muted">
            {stats.data.indicators.toLocaleString('en-IN')} indicators · {stats.data.subgroups} subgroups · last refresh {formatDate(stats.data.last_refresh) || 'pending'}
          </p>
        )}
      </section>

      <section className="section two-col">
        <div>
          <h2>How numbers are shown</h2>
          <p>Values in U.S. dollars use the international system (thousand, million, billion). Everything else uses the Indian system (lakh, crore).</p>
          <p>Pie charts show the largest eleven slices and fold the rest into “Other”. Additive categorical charts can switch between pie and bar views.</p>
        </div>
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
