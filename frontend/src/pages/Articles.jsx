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

// Authentic editorial vector and Substack covers
const THEMATIC_ARTICLE_COVERS = {
  // Polity & Policy authentic covers & local vectors
  midterms: assetUrl('art/modi-midterms.svg'),
  'delhi police': assetUrl('art/delhi-police.svg'),
  disproportionate: assetUrl('art/delhi-police.svg'),
  machchhar: assetUrl('art/captain-machchhar.svg'),
  transactional: assetUrl('art/parliament.svg'),
  china: assetUrl('art/defence-strategic.svg'),
  gdp: assetUrl('art/economy.svg'),
  cities: assetUrl('art/infrastructure.svg'),

  // Indian Matrix editorial covers
  'white-collar': assetUrl('art/media-press.svg'),
  idbi: assetUrl('art/central-bank.svg'),
  nehruvian: assetUrl('art/parliament.svg'),
  'gunda raj': assetUrl('art/security.svg'),
  'uttar pradesh': assetUrl('art/states.svg'),
  telecom: assetUrl('art/innovation.svg'),
  tariffs: assetUrl('art/economy.svg'),
  ballot: assetUrl('art/ballot-box.svg'),
  'form 6': assetUrl('art/vote-map.svg'),

  // Pew Research Center authentic covers & curated thematic vectors
  g20: assetUrl('art/public-opinion.svg'),
  naturalized: assetUrl('art/us-elections.svg'),
  voter: assetUrl('art/us-elections.svg'),
  election: assetUrl('art/us-elections.svg'),
  poll: assetUrl('art/us-elections.svg'),
  'social media': assetUrl('art/media-press.svg'),
  flock: assetUrl('art/media-press.svg'),
  camera: assetUrl('art/media-press.svg'),
};

function getArticleCover(article) {
  if (article.image_url && !article.image_url.includes('pewresearch.org')) return article.image_url;
  if (article.image && !article.image.includes('pewresearch.org')) return article.image;
  if (article.cover_image && !article.cover_image.includes('pewresearch.org')) return article.cover_image;

  const title = (article.title || '').toLowerCase();
  for (const [key, url] of Object.entries(THEMATIC_ARTICLE_COVERS)) {
    if (title.includes(key)) return url;
  }

  if (article.kind === 'pew' || /pew\s*research/i.test(article.publisher || '')) {
    if (title.includes('g20') || title.includes('country') || title.includes('opinion')) return assetUrl('art/public-opinion.svg');
    if (title.includes('election') || title.includes('voter') || title.includes('poll') || title.includes('u.s.')) return assetUrl('art/us-elections.svg');
    return assetUrl('art/maps-pew-research.svg');
  }

  if (article.kind === 'polity_policy') {
    return assetUrl('art/parliament.svg');
  }

  if (article.kind === 'indian_matrix') {
    return assetUrl('art/media-press.svg');
  }

  return assetUrl('art/media-press.svg');
}

export default function Articles() {
  useDocumentTitle('From The Substack · Articles & Reports');
  const [kind, setKind] = useState('');
  const [query, setQuery] = useState('');
  const q = useDebounced(query.trim(), 300);
  const [page, setPage] = useState(1);
  const [accumulated, setAccumulated] = useState([]);

  const articles = useAsync(
    signal => api.articles({ kind, q, page, page_size: 20 }, signal).then(data => ({ ...data, page })),
    [kind, q, page],
  );

  useEffect(() => {
    setPage(1);
    setAccumulated([]);
  }, [kind, q]);

  useEffect(() => {
    if (articles.data?.results) {
      if (articles.data.page === 1) {
        setAccumulated(articles.data.results);
      } else {
        setAccumulated(current => [...current, ...articles.data.results]);
      }
    }
  }, [articles.data]);

  const items = accumulated.length > 0 ? accumulated : (articles.data?.results || []);

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
                  alt=""
                  className="substack-card-img"
                  loading="lazy"
                  onError={e => {
                    e.currentTarget.onerror = null;
                    e.currentTarget.src = article.kind === 'pew' ? assetUrl('art/maps-pew-research.svg') : assetUrl('art/media-press.svg');
                  }}
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
