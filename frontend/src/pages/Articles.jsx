import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api.js';
import { formatDate } from '../format.js';
import { useAsync, useDebounced, useDocumentTitle } from '../hooks.js';
import { Empty, ErrorState, Loading } from '../components/States.jsx';
import ArtBackdrop from '../components/ArtBackdrop.jsx';
import { AMBIENT_ART } from '../art.js';

const KINDS = [
  ['', 'All publishers'],
  ['indian_matrix', 'Indian Matrix'],
  ['polity_policy', 'Polity and Policy'],
  ['pew', 'Pew Research Center'],
];

export default function Articles() {
  useDocumentTitle('Articles and reports');
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
    if (articles.data) setItems(current => (articles.data.page === 1 ? articles.data.results : [...current, ...articles.data.results]));
  }, [articles.data]);

  return (
    <>
      <section className="page-hero with-art">
        <ArtBackdrop art={AMBIENT_ART} />
        <p className="eyebrow">About the atlas</p>
        <h1>Articles and reports</h1>
        <p className="lead">Browse the full collection of public-data writing and research reports.</p>
        <Link to="/about">Back to About</Link>
      </section>

      <section className="section" aria-label="Articles and reports">
        <div className="filter-row">
          <label>
            <span className="sr-only">Publisher</span>
            <select aria-label="Publisher" value={kind} onChange={event => setKind(event.target.value)}>
              {KINDS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
          </label>
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