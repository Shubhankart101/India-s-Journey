import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api.js';
import { formatDate } from '../format.js';
import { useAsync, useDocumentTitle } from '../hooks.js';
import { Empty, ErrorState, Loading } from '../components/States.jsx';
import ArtBackdrop from '../components/ArtBackdrop.jsx';
import MiniIndices from '../components/MiniIndices.jsx';
import { CountUp, Marquee, Typewriter } from '../components/Motion.jsx';

const SLIDE_MS = 7000;
const TOPICS = ['GDP and inflation', 'UPI payments', 'coal and iron ore', 'Lok Sabha results', 'public health', 'defence and security', 'tourism and heritage'];

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
  const articles = useAsync(signal => api.latestArticles(signal), []);
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
  const subgroupLinks = (categories.data || []).flatMap(category => category.subgroups.map(sub => ({
    to: `/explore?category=${category.slug}&subgroup=${sub.slug}`,
    label: sub.name,
    art: sub.art || category.art,
  })));
  const half = Math.ceil(subgroupLinks.length / 2);
  const articleResults = articles.data?.results || [];
  const articleGroups = [
    { key: 'indian-matrix', title: 'Indian Matrix', kinds: ['indian_matrix'] },
    { key: 'polity-policy', title: 'PolityPolicy', kinds: ['polity_policy'] },
    { key: 'other', title: 'Other articles', kinds: [] },
  ].map(group => ({
    ...group,
    items: articleResults.filter(article => group.kinds.length ? group.kinds.includes(article.kind) : !['indian_matrix', 'polity_policy'].includes(article.kind)),
  }));

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
        <div className="hero-orbs" aria-hidden="true"><span /><span /><span /></div>
        <p className="eyebrow">A living atlas · 1947 to today</p>
        <h1>India, in <span className="gradient-text">perspective.</span></h1>
        <p className="hero-typed">Track <Typewriter phrases={TOPICS} /></p>
        <p className="lead">A thousand signals. One changing nation. Explore the data behind India’s economy, people, health, industry and public life—with the context and sources to follow every line.</p>
        <div className="hero-actions">
          <Link className="btn btn-primary" to="/explore">Explore the data</Link>
          <Link className="btn btn-ghost" to="/about">How it works ›</Link>
        </div>
        {s && (
          <dl className="stat-row">
            <div><dt>Indicators</dt><dd><CountUp value={s.indicators} /></dd></div>
            <div><dt>Interactive pies</dt><dd><CountUp value={s.radial_indicators} /></dd></div>
            <div><dt>Groups</dt><dd><CountUp value={s.categories} /></dd></div>
            <div><dt>Data points</dt><dd><CountUp value={s.data_points} /></dd></div>
          </dl>
        )}
        {s?.source_generated_at && <p className="muted small">Data generated {formatDate(s.source_generated_at)}</p>}
        {slides.length > 1 && (
          <div className="hero-slides">
            <Link className="hero-caption" to={`/explore?category=${current.slug}`}>
              Now showing <strong>{current.name}</strong> →
            </Link>
            <MiniIndices category={current} />
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

      {subgroupLinks.length > 0 && (
        <div className="marquee-band">
          <Marquee items={subgroupLinks.slice(0, half)} label="Featured subgroups" />
          <Marquee items={subgroupLinks.slice(half)} label="More subgroups" reverse />
        </div>
      )}

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
        {articles.loading && !articles.data && <Loading label="Loading articles…" />}
        {articles.error && <ErrorState error={articles.error} onRetry={articles.reload} />}
        {articles.data && !articles.data.results?.length && <Empty>No articles yet — check back after the next data refresh.</Empty>}
        {articles.data && (
          <div className="latest-analysis-grid" aria-busy={articles.loading}>
            {articleGroups.map(group => (
              <article className="latest-source-box" key={group.key}>
                <h3>{group.title}</h3>
                {group.items.length ? (
                  <ul className="article-list" aria-label={`${group.title} articles`}>
                    {group.items.map(article => (
                      <li key={article.url}>
                        <a href={article.url} target="_blank" rel="noopener noreferrer">{article.title}</a>
                        <small className="muted">{article.publisher} · {formatDate(article.published_at || article.published)}</small>
                      </li>
                    ))}
                  </ul>
                ) : <p className="muted small">No recent articles.</p>}
              </article>
            ))}
          </div>
        )}
      </section>
    </>
  );
}
