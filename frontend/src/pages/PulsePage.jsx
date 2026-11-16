import { useState, useMemo } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import pulseArticles from '../data/pulse-articles.json';
import PulseArticleView from '../components/PulseArticleView.jsx';
import { useDocumentTitle } from '../hooks.js';
import './PulsePage.css';

const PILLARS = [
  { key: 'all', label: 'All 21 Trackers' },
  { key: 'activity', label: 'Activity & Demand' },
  { key: 'prices', label: 'Prices & Inflation' },
  { key: 'fiscal', label: 'Fiscal & Tax' },
  { key: 'monetary', label: 'Monetary & Banking' },
  { key: 'trade', label: 'External & Trade' },
];

function MiniSparkline({ data = [], color = '#38bdf8' }) {
  if (!data || data.length < 2) return null;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const span = max - min || 1;
  const width = 110;
  const height = 36;
  const step = width / (data.length - 1);
  const pts = data.map((v, i) => {
    const x = i * step;
    const y = height - 4 - ((v - min) / span) * (height - 8);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(' ');

  return (
    <svg width={width} height={height} className="pulse-card-sparkline" aria-hidden="true">
      <polyline
        fill="none"
        stroke={color}
        strokeWidth="2.2"
        strokeLinecap="round"
        strokeLinejoin="round"
        points={pts}
      />
    </svg>
  );
}

export default function PulsePage() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [selectedPillar, setSelectedPillar] = useState('all');

  const activeArticle = useMemo(() => {
    if (!slug) return null;
    return pulseArticles.find(a => a.slug === slug.toLowerCase()) || null;
  }, [slug]);

  useDocumentTitle(
    activeArticle
      ? `${activeArticle.title} (${activeArticle.idx}) · India's Economic Pulse`
      : "India's Economic Pulse · 21 High Frequency Indicators"
  );

  const filteredArticles = useMemo(() => {
    if (selectedPillar === 'all') return pulseArticles;
    return pulseArticles.filter(a => a.pillar === selectedPillar);
  }, [selectedPillar]);

  const isEmbedMode = useMemo(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      return params.get('embed') === 'true' || window.location.pathname.startsWith('/embed');
    }
    return false;
  }, []);

  // Handle opening indicator
  const handleSelectArticle = (newSlug) => {
    navigate(`/pulse/${newSlug}`);
  };

  const handleCloseArticle = () => {
    navigate('/pulse');
  };

  // If in embed mode and article is active, return pure embed view
  if (isEmbedMode && activeArticle) {
    return (
      <PulseArticleView
        article={activeArticle}
        allArticles={pulseArticles}
        isEmbed={true}
      />
    );
  }

  return (
    <div className="pulse-page-wrapper">
      {/* If a slug is active, show the rich interactive article modal/reader */}
      {activeArticle && (
        <PulseArticleView
          article={activeArticle}
          allArticles={pulseArticles}
          onClose={handleCloseArticle}
          onSelectArticle={handleSelectArticle}
        />
      )}

      {/* Main Pulse Hub Header */}
      <section className="pulse-hub-hero">
        <div className="pulse-hub-kicker">
          <span className="pulse-hub-dot" />
          <span>High Frequency Indicators · Real-Time Pulse</span>
        </div>
        <h1 className="pulse-hub-title">India's Economic Pulse</h1>
        <p className="pulse-hub-subtitle">
          Tracking 21 high-frequency macroeconomic signals across business activity, consumer prices, fiscal revenue,
          credit expansion, and foreign trade month-by-month before official GDP releases.
          Click any indicator to read the full interactive article with historical datasets, component toggles, and analytical mechanics.
        </p>

        {/* Top Macro Ticker */}
        <div className="pulse-macro-ticker-row">
          <button
            type="button"
            className="pulse-ticker-pill"
            onClick={() => handleSelectArticle('pmi')}
          >
            <span className="ticker-label">MANUFACTURING PMI</span>
            <span className="ticker-val">54.7</span>
            <span className="ticker-badge up">Expansion</span>
          </button>
          <button
            type="button"
            className="pulse-ticker-pill"
            onClick={() => handleSelectArticle('cpi')}
          >
            <span className="ticker-label">CPI INFLATION</span>
            <span className="ticker-val">6.09%</span>
            <span className="ticker-badge">In Focus</span>
          </button>
          <button
            type="button"
            className="pulse-ticker-pill"
            onClick={() => handleSelectArticle('gst')}
          >
            <span className="ticker-label">GROSS GST</span>
            <span className="ticker-val">₹1.87 L Cr</span>
            <span className="ticker-badge up">+8.9% YoY</span>
          </button>
          <button
            type="button"
            className="pulse-ticker-pill"
            onClick={() => handleSelectArticle('forex')}
          >
            <span className="ticker-label">FX RESERVES</span>
            <span className="ticker-val">$719.5 Bn</span>
            <span className="ticker-badge up">Record High</span>
          </button>
        </div>
      </section>

      {/* Pillar Filter Pills */}
      <div className="pulse-hub-filters" role="tablist" aria-label="Economic Pillars">
        {PILLARS.map(p => (
          <button
            type="button"
            key={p.key}
            role="tab"
            aria-selected={selectedPillar === p.key}
            className={`pulse-hub-filter-btn ${selectedPillar === p.key ? 'active' : ''}`}
            onClick={() => setSelectedPillar(p.key)}
          >
            {p.label}
          </button>
        ))}
      </div>

      {/* Grid of 21 Indicators */}
      <div className="pulse-hub-grid">
        {filteredArticles.map(art => {
          // Extract sparkline sample (last 12 points)
          const primarySeriesKey = Object.keys(art.chart?.series || {})[0];
          const rawVals = art.chart?.series?.[primarySeriesKey]?.values || [];
          const sparklineVals = rawVals.slice(-12);
          const topStat = art.stats?.[0];

          return (
            <Link
              key={art.slug}
              to={`/pulse/${art.slug}`}
              className="pulse-hub-card"
              style={{ '--card-accent': art.color }}
            >
              <div className="pulse-hub-card-header">
                <div className="pulse-card-idx-wrap">
                  <span className="pulse-card-idx">{art.idx}</span>
                  <span className="pulse-card-cat">{art.category}</span>
                </div>
                <span className="pulse-card-indicator-tag">Article Available</span>
              </div>

              <h2 className="pulse-hub-card-title">{art.title}</h2>
              <p className="pulse-hub-card-desc">{art.desc}</p>

              <div className="pulse-hub-card-footer">
                <div className="pulse-hub-card-stat">
                  <span className="pulse-card-stat-val">{topStat?.value || '—'}</span>
                  <span className="pulse-card-stat-lbl">{topStat?.label}</span>
                </div>

                <div className="pulse-hub-card-chart-col">
                  <MiniSparkline data={sparklineVals} color={art.color} />
                  <span className="pulse-card-cta">
                    Open Deep Dive →
                  </span>
                </div>
              </div>
            </Link>
          );
        })}
      </div>

      {/* Hub Footer Attribution */}
      <footer className="pulse-hub-footer">
        <p>
          Sources: RBI, Ministry of Statistics and Programme Implementation (MoSPI),
          Ministry of Finance (GSTN), NPCI, S&amp;P Global, CEA, PPAC &amp; FADA.
          Data model compiled from the Polity &amp; Policy High Frequency Pulse series.
        </p>
        <Link to="/" className="pulse-back-home-link">
          ← Return to India's Journey Home
        </Link>
      </footer>
    </div>
  );
}
