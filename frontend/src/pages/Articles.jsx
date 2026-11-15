import { useEffect, useMemo, useState } from 'react';
import { api } from '../api.js';
import { assetUrl } from '../config.js';
import { useAsync, useDebounced, useDocumentTitle } from '../hooks.js';
import { Empty, ErrorState, Loading } from '../components/States.jsx';
import './Articles.css';

const KINDS = [
  ['', 'All publishers'],
  ['polity_policy', 'Polity & Policy'],
  ['indian_matrix', 'Indian Matrix'],
  ['pew', 'Pew Research Center'],
];

function formatSubstackDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return String(dateStr).toUpperCase();
  const day = d.getDate();
  const months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];
  const month = months[d.getMonth()];
  const year = d.getFullYear();
  return `${day} ${month} ${year}`;
}

function getArticleCover(article) {
  const title = (article.title || '').toLowerCase();
  if (title.includes('midterms') || title.includes('modi after')) {
    return assetUrl('art/modi-midterms.svg');
  }
  if (title.includes('delhi police') || title.includes('disproportionate')) {
    return assetUrl('art/delhi-police.svg');
  }
  if (title.includes('machchhar') || title.includes('saves the day')) {
    return assetUrl('art/captain-machchhar.svg');
  }
  if (title.includes('idbi') || title.includes('nehruvian')) {
    return assetUrl('art/central-bank.svg');
  }
  if (title.includes('gunda raj') || title.includes('uttar pradesh')) {
    return assetUrl('art/counter-terror.svg');
  }
  if (title.includes('gb to almost free') || title.includes('telecom')) {
    return assetUrl('art/innovation.svg');
  }
  if (title.includes('ballot') || title.includes('paper')) {
    return assetUrl('art/ballot-box.svg');
  }
  if (title.includes('form 6') || title.includes('supreme court')) {
    return assetUrl('art/supreme-court.svg');
  }
  if (title.includes('tariffs') || title.includes('trade')) {
    return assetUrl('art/port-trade.svg');
  }
  if (article.kind === 'polity_policy') return assetUrl('art/opinion.svg');
  if (article.kind === 'indian_matrix') return assetUrl('art/parliament.svg');
  if (article.kind === 'pew') return assetUrl('art/public-opinion.svg');
  return assetUrl('art/media-press.svg');
}

export default function Articles() {
  useDocumentTitle('From The Substack · Articles & Reports');
  const [kind, setKind] = useState('');
  const [query, setQuery] = useState('');
  const q = useDebounced(query.trim(), 300);
  const [page, setPage] = useState(1);
  const [items, setItems] = useState([]);

  const articles = useAsync(
    signal => api.articles({ kind, q, page, page_size: 20 }, signal).then(data => ({ ...data, page })),
    [kind, q, page],
  );

  useEffect(() => {
    setPage(1);
    setItems([]);
  }, [kind, q]);

  useEffect(() => {
    if (articles.data?.results) {
      setItems(current => (articles.data.page === 1 ? articles.data.results : [...current, ...articles.data.results]));
    }
  }, [articles.data]);

  // Featured order prioritizing the three Substack pieces when browsing without a search query
  const displayItems = useMemo(() => {
    if (q || kind) return items;
    const featuredTitles = [
      'What’s Next for Modi After the Midterms?',
      'Delhi Police And Virtue Of A Disproportionate Response',
      'Captain Smit Machchhar Saves The Day',
    ];
    const topPicks = [];
    const rest = [];
    for (const item of items) {
      if (featuredTitles.some(ft => item.title?.toLowerCase().includes(ft.toLowerCase().slice(0, 15)))) {
        topPicks.push(item);
      } else {
        rest.push(item);
      }
    }
    // Sort topPicks in exact order of the screenshot
    topPicks.sort((a, b) => {
      const idxA = featuredTitles.findIndex(ft => a.title?.toLowerCase().includes(ft.toLowerCase().slice(0, 15)));
      const idxB = featuredTitles.findIndex(ft => b.title?.toLowerCase().includes(ft.toLowerCase().slice(0, 15)));
      return (idxA === -1 ? 99 : idxA) - (idxB === -1 ? 99 : idxB);
    });
    return [...topPicks, ...rest];
  }, [items, q, kind]);

  return (
    <main className="articles-page">
      {/* Header matching screenshot media_1794752837498_c86f0423.jpg */}
      <header className="substack-header">
        <h1 className="substack-title">From The Substack</h1>
        <a
          href="https://politypolicy.substack.com"
          target="_blank"
          rel="noopener noreferrer"
          className="substack-see-all"
        >
          See All Writing ↗
        </a>
      </header>

      {/* Substack Cards Grid */}
      {articles.error && <ErrorState error={articles.error} onRetry={articles.reload} />}
      {!articles.loading && !articles.error && displayItems.length === 0 && (
        <Empty>No articles match your search.</Empty>
      )}

      <div className="substack-grid" aria-label="Substack Articles Grid">
        {displayItems.map(article => {
          const coverUrl = getArticleCover(article);
          const dateStr = formatSubstackDate(article.published_at || article.published);
          return (
            <a
              key={article.url}
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              className="substack-card"
            >
              <div className="substack-card-cover">
                <img
                  src={coverUrl}
                  alt={article.title}
                  className="substack-card-img"
                  loading="lazy"
                />
              </div>
              <div className="substack-card-body">
                <span className="substack-card-date">{dateStr}</span>
                <h2 className="substack-card-title">{article.title}</h2>
                <div className="substack-card-publisher">
                  <span>{article.publisher}</span>
                  <span aria-hidden="true">↗</span>
                </div>
              </div>
            </a>
          );
        })}
      </div>

      {articles.loading && <Loading label="Loading essays and analysis…" />}

      {/* Secondary Filter & Search Strip */}
      <section className="substack-filter-strip" aria-label="Filter archive">
        <label>
          <span className="sr-only">Publisher</span>
          <select
            aria-label="Publisher"
            value={kind}
            onChange={e => setKind(e.target.value)}
            className="substack-pill"
            style={{ padding: '6px 12px' }}
          >
            {KINDS.map(([val, label]) => (
              <option key={val} value={val}>{label}</option>
            ))}
          </select>
        </label>
        <div className="substack-pills">
          {KINDS.map(([val, label]) => (
            <button
              type="button"
              key={val}
              className={`substack-pill ${kind === val ? 'active' : ''}`}
              onClick={() => setKind(val)}
            >
              {label}
            </button>
          ))}
        </div>
        <div>
          <input
            type="search"
            placeholder="Search essay topics..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            className="substack-search-input"
            aria-label="Search essays"
          />
        </div>
      </section>

      {articles.data?.next && !articles.loading && (
        <div style={{ textAlign: 'center', marginTop: '24px' }}>
          <button
            type="button"
            className="btn btn-ghost"
            onClick={() => setPage(p => p + 1)}
          >
            Load more
          </button>
        </div>
      )}
    </main>
  );
}
