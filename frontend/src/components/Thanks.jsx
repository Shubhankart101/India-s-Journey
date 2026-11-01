import { api } from '../api.js';
import { formatDate } from '../format.js';
import { useAsync } from '../hooks.js';

const PUBLISHERS = [
  {
    kind: 'polity_policy',
    name: 'PolityPolicy',
    latest: 'Latest from Polity and Policy',
    href: 'https://politypolicy.substack.com/',
    read: 'Read Polity and Policy',
    body: (
      <>
        With thanks to <a href="https://politypolicy.com/" target="_blank" rel="noopener noreferrer">PolityPolicy</a> and{' '}
        <a href="https://politypolicy.substack.com/" target="_blank" rel="noopener noreferrer">Tushar Gupta's Polity and Policy Substack</a>{' '}
        for their clear, visual explanations of policy and public data.
      </>
    ),
  },
  {
    kind: 'indian_matrix',
    name: 'Indian Matrix',
    latest: 'Latest from Indian Matrix',
    href: 'https://indianmatrix.substack.com/',
    read: 'Read Indian Matrix',
    body: (
      <>
        With thanks to <a href="https://substack.com/@indianmatrix" target="_blank" rel="noopener noreferrer">Indian Matrix</a> for its data-led
        writing on India's economy, institutions and strategy.
      </>
    ),
  },
];

function ThanksCard({ publisher }) {
  const articles = useAsync(signal => api.articles({ kind: publisher.kind, page_size: 3 }, signal), [publisher.kind]);
  const items = articles.data?.results || [];
  return (
    <article className="thanks-card" aria-label={publisher.name}>
      <h3>{publisher.name}</h3>
      <p className="muted">{publisher.body}</p>
      <span className="eyebrow">{publisher.latest}</span>
      {articles.loading && <p className="muted small">Loading latest public articles…</p>}
      {articles.error && <p className="muted small">Articles are temporarily unavailable.</p>}
      {!articles.loading && !articles.error && items.length === 0 && <p className="muted small">No public article snapshot available yet.</p>}
      <ul className="article-list">
        {items.map(article => (
          <li key={article.url}>
            <a href={article.url} target="_blank" rel="noopener noreferrer">{article.title}</a>
            <small className="muted">{formatDate(article.published_at || article.published)}</small>
          </li>
        ))}
      </ul>
      <a className="thanks-read" href={publisher.href} target="_blank" rel="noopener noreferrer">{publisher.read} →</a>
    </article>
  );
}

export default function Thanks() {
  return (
    <section className="thanks" id="thanks" aria-labelledby="thanks-title">
      <span className="eyebrow">With thanks</span>
      <h2 id="thanks-title">The writing that inspired this atlas</h2>
      <p className="muted">This independent project was encouraged by public-data writing from PolityPolicy, Polity and Policy, and Indian Matrix.</p>
      <div className="thanks-columns">
        {PUBLISHERS.map(publisher => <ThanksCard key={publisher.kind} publisher={publisher} />)}
      </div>
    </section>
  );
}
