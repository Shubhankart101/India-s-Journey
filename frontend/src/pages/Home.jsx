import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api.js';
import { formatDate } from '../format.js';
import { useAsync, useDocumentTitle } from '../hooks.js';
import { ErrorState, Loading } from '../components/States.jsx';
import ArtBackdrop from '../components/ArtBackdrop.jsx';

const SLIDE_MS = 7000;

const tilt = event => {
  const node = event.currentTarget;
  const box = node.getBoundingClientRect();
  node.style.setProperty('--rx', `${(((event.clientY - box.top) / box.height) - 0.5) * -8}deg`);
  node.style.setProperty('--ry', `${(((event.clientX - box.left) / box.width) - 0.5) * 10}deg`);
  node.style.setProperty('--gx', `${((event.clientX - box.left) / box.width) * 100}%`);
};
const untilt = event => {
  ['--rx', '--ry', '--gx'].forEach(name => event.currentTarget.style.removeProperty(name));
};

export default function Home() {
  useDocumentTitle('');
  const stats = useAsync(signal => api.stats(signal), []);
  const categories = useAsync(signal => api.categories(signal), []);
  const articles = useAsync(signal => api.articles({ page_size: 6 }, signal), []);
  const s = stats.data;
  const slides = (categories.data || []).filter(category => category.art);
  const [slide, setSlide] = useState(0);
  const [paused, setPaused] = useState(false);
  useEffect(() => {
    if (paused || slides.length < 2) return undefined;
    const timer = setInterval(() => setSlide(current => (current + 1) % slides.length), SLIDE_MS);
    return () => clearInterval(timer);
  }, [paused, slides.length]);
  const current = slides[slide % (slides.length || 1)];

  return (
    <>
      <section
        className="hero"
        onPointerEnter={() => setPaused(true)}
        onPointerLeave={() => setPaused(false)}
        onFocus={() => setPaused(true)}
        onBlur={() => setPaused(false)}
      >
        <ArtBackdrop art={current?.art || 'parliament.svg'} />
        <p className="eyebrow">Official data · refreshed on schedule</p>
        <h1>India's Journey.<br /><span className="gradient-text">Every number, sourced.</span></h1>
        <p className="lead">Search hundreds of indicators on the economy, industry, mining, elections, health, society and tourism — open any chart, compare up to four side by side, and download the data.</p>
        <div className="hero-actions">
          <Link className="btn btn-primary" to="/explore">Explore indicators</Link>
          <Link className="btn btn-ghost" to="/compare">Compare</Link>
        </div>
        {s && (
          <dl className="stat-row">
            <div><dt>Indicators</dt><dd>{s.indicators.toLocaleString('en-IN')}</dd></div>
            <div><dt>Interactive pies</dt><dd>{s.radial_indicators.toLocaleString('en-IN')}</dd></div>
            <div><dt>Groups</dt><dd>{s.categories}</dd></div>
            <div><dt>Data points</dt><dd>{s.data_points.toLocaleString('en-IN')}</dd></div>
          </dl>
        )}
        {s?.source_generated_at && <p className="muted small">Data generated {formatDate(s.source_generated_at)}</p>}
        {slides.length > 1 && (
          <div className="hero-slides">
            <Link className="hero-caption" to={`/explore?category=${current.slug}`}>
              Now showing <strong>{current.name}</strong> →
            </Link>
            <div className="slide-dots" role="group" aria-label="Choose background scene">
              {slides.map((category, index) => (
                <button
                  type="button"
                  key={category.slug}
                  className={`slide-dot${index === slide % slides.length ? ' active' : ''}`}
                  aria-label={`Show ${category.name} scene`}
                  aria-pressed={index === slide % slides.length}
                  onClick={() => setSlide(index)}
                />
              ))}
            </div>
          </div>
        )}
      </section>

      <section className="section">
        <div className="section-head">
          <h2>Browse by group</h2>
          <Link to="/explore">See all →</Link>
        </div>
        {categories.loading && <Loading label="Loading groups…" />}
        {categories.error && <ErrorState error={categories.error} onRetry={categories.reload} />}
        <div className="group-grid">
          {(categories.data || []).map(category => (
            <Link
              key={category.slug}
              to={`/explore?category=${category.slug}`}
              className="group-tile"
              style={{ '--tile-art': `url(/art/${category.art || 'parliament.svg'})` }}
              onPointerMove={tilt}
              onPointerLeave={untilt}
            >
              <span className="eyebrow">{category.subgroups.length} subgroups</span>
              <h3>{category.name}</h3>
              <p className="muted clamp-2">{category.description}</p>
              <span className="chip">{category.live_count} live charts</span>
            </Link>
          ))}
        </div>
      </section>

      <section className="section">
        <div className="section-head">
          <h2>Latest analysis</h2>
          <Link to="/about#articles">All articles →</Link>
        </div>
        {articles.loading && <Loading label="Loading articles…" />}
        {articles.error && <ErrorState error={articles.error} onRetry={articles.reload} />}
        <ul className="article-list">
          {(articles.data?.results || []).map(article => (
            <li key={article.url}>
              <a href={article.url} target="_blank" rel="noopener noreferrer">{article.title}</a>
              <small className="muted">{article.publisher} · {formatDate(article.published_at || article.published)}</small>
            </li>
          ))}
        </ul>
      </section>
    </>
  );
}
