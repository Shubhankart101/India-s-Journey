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

const AUTHENTIC_ARTICLE_IMAGES = {
  // Polity & Policy authentic Substack CDN covers
  midterms: 'https://substackcdn.com/image/fetch/$s_!kf6B!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fac221d2d-405e-42c8-83b1-1b324d598182_1152x768.jpeg',
  'delhi police': 'https://substackcdn.com/image/fetch/$s_!DBFF!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F1c614127-8d4d-4e7d-bac3-61dcc0a7279f_1792x1008.jpeg',
  disproportionate: 'https://substackcdn.com/image/fetch/$s_!DBFF!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F1c614127-8d4d-4e7d-bac3-61dcc0a7279f_1792x1008.jpeg',
  machchhar: 'https://substackcdn.com/image/fetch/$s_!rj5P!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F42fdead7-3365-42c5-aa8c-3a50d0a7c7be_1792x1008.jpeg',
  transactional: 'https://substackcdn.com/image/fetch/$s_!V4l9!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F00644181-53cb-46f7-b4a9-226aa68006ad_1728x1152.jpeg',
  china: 'https://substackcdn.com/image/fetch/$s_!tF2Z!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F86d54965-39ef-4633-aae9-4abda41c7560_1152x768.jpeg',
  gdp: 'https://substackcdn.com/image/fetch/$s_!9RkP!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fe7f22379-cb4a-493f-8461-8ee22030ce14_1152x768.jpeg',
  cities: 'https://substackcdn.com/image/fetch/$s_!t6xQ!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F1c614127-8d4d-4e7d-bac3-61dcc0a7279f_1792x1008.jpeg',

  // Indian Matrix authentic Substack CDN covers
  'white-collar': 'https://substackcdn.com/image/fetch/$s_!7ed1!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F7ed17470-765e-4407-acde-6e21c5df65ae_1677x938.png',
  idbi: 'https://substackcdn.com/image/fetch/$s_!u8ev!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa7998f9e-9f1d-4ddd-897d-f0316c77bee9_1677x938.png',
  nehruvian: 'https://substackcdn.com/image/fetch/$s_!u8ev!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa7998f9e-9f1d-4ddd-897d-f0316c77bee9_1677x938.png',
  'gunda raj': 'https://substackcdn.com/image/fetch/$s_!BbXY!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F9173021a-0d06-4a71-a42c-f903267fc74c_1677x938.png',
  'uttar pradesh': 'https://substackcdn.com/image/fetch/$s_!BbXY!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F9173021a-0d06-4a71-a42c-f903267fc74c_1677x938.png',
  telecom: 'https://substackcdn.com/image/fetch/$s_!m6qA!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Faed47fc2-64dc-4073-ae8a-1d54daf9fefe_1677x938.png',
  tariffs: 'https://substackcdn.com/image/fetch/$s_!d669!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fd669431c-fc84-4072-8e7b-2db98c257b51_1677x938.png',
  ballot: 'https://substackcdn.com/image/fetch/$s_!b29c!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F4978a2cb-ff13-43dc-8fc9-b68bbda7738b_1677x938.png',
  'form 6': 'https://substackcdn.com/image/fetch/$s_!e91a!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fc05f15a1-7785-48fa-bb64-c2bbca93297a_1677x938.png',

  // Pew Research Center authentic covers
  naturalized: 'https://www.pewresearch.org/wp-content/uploads/sites/20/2026/10/SR_26.10.27_naturalized_voters_crop.png',
  g20: 'https://www.pewresearch.org/wp-content/uploads/sites/20/2026/10/FT_26.10.16_G20views_featured.png',
  'social media': 'https://www.pewresearch.org/wp-content/uploads/sites/20/2026/10/FT_26.10.01_socialMedia_featured.png',
};

function getArticleCover(article) {
  if (article.image_url) return article.image_url;
  if (article.image) return article.image;
  if (article.cover_image) return article.cover_image;
  const title = (article.title || '').toLowerCase();
  for (const [key, url] of Object.entries(AUTHENTIC_ARTICLE_IMAGES)) {
    if (title.includes(key)) return url;
  }
  if (article.kind === 'polity_policy') {
    return 'https://substackcdn.com/image/fetch/$s_!kf6B!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fac221d2d-405e-42c8-83b1-1b324d598182_1152x768.jpeg';
  }
  if (article.kind === 'indian_matrix') {
    return 'https://substackcdn.com/image/fetch/$s_!7ed1!,w_1200,h_675,c_fill,f_jpg,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F7ed17470-765e-4407-acde-6e21c5df65ae_1677x938.png';
  }
  if (article.kind === 'pew') {
    return 'https://www.pewresearch.org/wp-content/uploads/sites/20/2026/10/SR_26.10.27_naturalized_voters_crop.png';
  }
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
