import { useState, useMemo, useRef, useEffect } from 'react';
import './PulseArticleView.css';

export default function PulseArticleView({ article, allArticles = [], onClose, onSelectArticle }) {
  if (!article) return null;

  const [activeView, setActiveView] = useState(
    article.chart?.views?.[0]?.id || Object.keys(article.chart?.series || {})[0] || 'all'
  );
  const [hoverIndex, setHoverIndex] = useState(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const svgRef = useRef(null);

  // Reset active view whenever article changes
  useEffect(() => {
    setActiveView(article.chart?.views?.[0]?.id || Object.keys(article.chart?.series || {})[0] || 'all');
    setHoverIndex(null);
  }, [article.slug]);

  // Keyboard navigation: Escape closes, Left/Right navigates
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        if (isFullscreen) setIsFullscreen(false);
        else if (onClose) onClose();
      } else if (e.key === 'ArrowRight') {
        goToNext();
      } else if (e.key === 'ArrowLeft') {
        goToPrev();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [article.slug, isFullscreen, allArticles]);

  const currentIndex = useMemo(() => {
    return allArticles.findIndex(a => a.slug === article.slug);
  }, [allArticles, article.slug]);

  const prevArticle = currentIndex > 0 ? allArticles[currentIndex - 1] : allArticles[allArticles.length - 1];
  const nextArticle = currentIndex < allArticles.length - 1 ? allArticles[currentIndex + 1] : allArticles[0];

  const goToPrev = () => {
    if (prevArticle && onSelectArticle) onSelectArticle(prevArticle.slug);
  };

  const goToNext = () => {
    if (nextArticle && onSelectArticle) onSelectArticle(nextArticle.slug);
  };

  // Determine active series based on selected view
  const visibleSeriesKeys = useMemo(() => {
    const allKeys = Object.keys(article.chart?.series || {});
    if (activeView === 'both' || activeView === 'all' || activeView === 'total' || activeView === 'trade') {
      return allKeys;
    }
    if (activeView === 'rice_wheat') {
      return ['rice', 'wheat'].filter(k => allKeys.includes(k));
    }
    if (allKeys.includes(activeView)) {
      return [activeView];
    }
    // Matching prefixes or aliases
    const matched = allKeys.filter(k => k.toLowerCase().includes(activeView.toLowerCase()));
    return matched.length ? matched : allKeys.slice(0, 2);
  }, [activeView, article.chart]);

  // Chart data dimensions
  const labels = article.chart?.labels || [];
  const seriesData = article.chart?.series || {};

  const { minVal, maxVal, yTicks, xStep, chartWidth, chartHeight, padLeft, padRight, padTop, padBottom } = useMemo(() => {
    const chartWidth = 1000;
    const chartHeight = 400;
    const padLeft = 60;
    const padRight = 30;
    const padTop = 30;
    const padBottom = 40;

    let min = Infinity;
    let max = -Infinity;

    visibleSeriesKeys.forEach(k => {
      const vals = seriesData[k]?.values || [];
      vals.forEach(v => {
        if (typeof v === 'number' && !isNaN(v)) {
          if (v < min) min = v;
          if (v > max) max = v;
        }
      });
    });

    if (article.chart?.baseline?.value !== undefined && article.chart?.baseline?.value !== null) {
      min = Math.min(min, article.chart.baseline.value);
      max = Math.max(max, article.chart.baseline.value);
    }

    if (min === Infinity || max === -Infinity) {
      min = 0;
      max = 100;
    }

    // Add 10% breathing room
    const span = max - min || 1;
    min = Math.floor((min - span * 0.08) * 10) / 10;
    max = Math.ceil((max + span * 0.08) * 10) / 10;

    const count = 5;
    const yTicks = [];
    for (let i = 0; i <= count; i++) {
      yTicks.push(min + (i * (max - min)) / count);
    }

    const n = Math.max(labels.length, 1);
    const innerW = chartWidth - padLeft - padRight;
    const xStep = n > 1 ? innerW / (n - 1) : innerW;

    return { minVal: min, maxVal: max, yTicks, xStep, chartWidth, chartHeight, padLeft, padRight, padTop, padBottom };
  }, [visibleSeriesKeys, seriesData, article.chart, labels.length]);

  const getYPos = (val) => {
    if (maxVal === minVal) return padTop + (chartHeight - padTop - padBottom) / 2;
    const innerH = chartHeight - padTop - padBottom;
    return padTop + innerH - ((val - minVal) / (maxVal - minVal)) * innerH;
  };

  const getXPos = (idx) => {
    return padLeft + idx * xStep;
  };

  // Generate SVG Path definitions
  const paths = useMemo(() => {
    const innerH = chartHeight - padTop - padBottom;
    const baselineY = padTop + innerH;

    return visibleSeriesKeys.map(k => {
      const s = seriesData[k];
      if (!s || !s.values) return null;
      const pts = s.values.map((v, i) => {
        const x = getXPos(i);
        const y = getYPos(v);
        return { x, y, v };
      });

      if (!pts.length) return null;

      const lineD = pts.reduce((acc, p, i) => `${acc} ${i === 0 ? 'M' : 'L'} ${p.x.toFixed(1)},${p.y.toFixed(1)}`, '');
      const areaD = `${lineD} L ${pts[pts.length - 1].x.toFixed(1)},${baselineY} L ${pts[0].x.toFixed(1)},${baselineY} Z`;

      return {
        key: k,
        label: s.label || k,
        color: s.color || article.color || '#38bdf8',
        pts,
        lineD,
        areaD,
      };
    }).filter(Boolean);
  }, [visibleSeriesKeys, seriesData, getXPos, getYPos, chartHeight, padTop, padBottom, article.color]);

  // Handle pointer over chart
  const handleMouseMove = (e) => {
    if (!svgRef.current || !labels.length) return;
    const rect = svgRef.current.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const relX = (mouseX / rect.width) * chartWidth;
    
    // Find closest index
    const innerX = relX - padLeft;
    let idx = Math.round(innerX / xStep);
    if (idx < 0) idx = 0;
    if (idx >= labels.length) idx = labels.length - 1;
    setHoverIndex(idx);
  };

  const handleMouseLeave = () => {
    setHoverIndex(null);
  };

  // Baseline Y
  const baselineYPos = article.chart?.baseline?.value !== undefined
    ? getYPos(article.chart.baseline.value)
    : null;

  return (
    <div className={`pulse-article-modal-backdrop ${isFullscreen ? 'fullscreen' : ''}`} onClick={(e) => {
      if (e.target === e.currentTarget && onClose) onClose();
    }}>
      <div className="pulse-article-container" role="dialog" aria-modal="true" aria-labelledby="pulse-article-title">
        {/* Top Header Controls */}
        <header className="pulse-article-top-nav">
          <button
            type="button"
            className="pulse-nav-back-btn"
            onClick={onClose}
            aria-label="Back to Pulse Dashboard"
          >
            <span className="pulse-nav-back-icon">←</span>
            <span>Back to Indicators</span>
          </button>

          <div className="pulse-nav-center">
            <span className="pulse-badge-idx">{article.idx}</span>
            <span className="pulse-nav-divider">/</span>
            <span className="pulse-badge-pillar">{article.category}</span>
          </div>

          <div className="pulse-nav-actions">
            <button
              type="button"
              className="pulse-icon-btn"
              onClick={() => setIsFullscreen(!isFullscreen)}
              title={isFullscreen ? 'Exit Fullscreen' : 'Enter Fullscreen'}
              aria-label="Toggle Fullscreen"
            >
              {isFullscreen ? '⤦' : '⛶'}
            </button>
            <button
              type="button"
              className="pulse-icon-btn pulse-close-btn"
              onClick={onClose}
              title="Close (Esc)"
              aria-label="Close"
            >
              ✕
            </button>
          </div>
        </header>

        {/* Scrollable Article Body */}
        <div className="pulse-article-content">
          {/* Editorial Masthead */}
          <section className="pulse-masthead">
            <div className="pulse-kicker-row">
              <span className="pulse-kicker-dot" style={{ background: article.color }} />
              <span className="pulse-kicker-text">{article.kicker}</span>
            </div>

            <h1 id="pulse-article-title" className="pulse-article-headline" style={{ '--article-accent': article.color }}>
              {article.title}
            </h1>

            <p className="pulse-article-lead">
              {article.lead}
            </p>
          </section>

          {/* Interactive Chart Section */}
          <section className="pulse-chart-card">
            {/* Chart Toolbar */}
            <div className="pulse-chart-toolbar">
              <div className="pulse-view-tabs" role="tablist">
                {article.chart?.views?.map(v => (
                  <button
                    type="button"
                    key={v.id}
                    role="tab"
                    aria-selected={activeView === v.id}
                    className={`pulse-view-tab ${activeView === v.id ? 'active' : ''}`}
                    onClick={() => setActiveView(v.id)}
                    style={{
                      borderColor: activeView === v.id ? article.color : 'transparent',
                      color: activeView === v.id ? '#ffffff' : '#94a3b8'
                    }}
                  >
                    {v.label}
                  </button>
                ))}
              </div>

              <div className="pulse-chart-legend">
                {paths.map(p => (
                  <div key={p.key} className="pulse-legend-item">
                    <span className="pulse-legend-dot" style={{ background: p.color }} />
                    <span className="pulse-legend-text">{p.label}</span>
                  </div>
                ))}
                {article.chart?.unit && (
                  <span className="pulse-unit-label">Unit: {article.chart.unit}</span>
                )}
              </div>
            </div>

            {/* SVG Chart Display */}
            <div className="pulse-svg-wrapper">
              <svg
                ref={svgRef}
                viewBox={`0 0 ${chartWidth} ${chartHeight}`}
                className="pulse-interactive-svg"
                preserveAspectRatio="none"
                onMouseMove={handleMouseMove}
                onMouseLeave={handleMouseLeave}
                onTouchMove={(e) => {
                  if (e.touches && e.touches[0]) {
                    handleMouseMove(e.touches[0]);
                  }
                }}
              >
                <defs>
                  {paths.map(p => (
                    <linearGradient
                      key={`grad-${p.key}`}
                      id={`grad-${article.slug}-${p.key}`}
                      x1="0" y1="0" x2="0" y2="1"
                    >
                      <stop offset="0%" stopColor={p.color} stopOpacity="0.28" />
                      <stop offset="90%" stopColor={p.color} stopOpacity="0.02" />
                      <stop offset="100%" stopColor={p.color} stopOpacity="0.0" />
                    </linearGradient>
                  ))}
                  <filter id="neon-glow" x="-20%" y="-20%" width="140%" height="140%">
                    <feDropShadow dx="0" dy="2" stdDeviation="3" floodColor={article.color} floodOpacity="0.45" />
                  </filter>
                </defs>

                {/* Horizontal Grid Lines */}
                {yTicks.map((val, idx) => {
                  const y = getYPos(val);
                  return (
                    <g key={`ytick-${idx}`} className="pulse-grid-group">
                      <line
                        x1={padLeft}
                        y1={y}
                        x2={chartWidth - padRight}
                        y2={y}
                        stroke="#222034"
                        strokeDasharray="3 4"
                      />
                      <text
                        x={padLeft - 10}
                        y={y + 4}
                        textAnchor="end"
                        className="pulse-axis-label"
                      >
                        {val >= 1000 ? `${(val / 1000).toFixed(0)}k` : val.toFixed(val % 1 !== 0 ? 1 : 0)}
                      </text>
                    </g>
                  );
                })}

                {/* Baseline reference line if present */}
                {baselineYPos !== null && (
                  <g className="pulse-baseline-group">
                    <line
                      x1={padLeft}
                      y1={baselineYPos}
                      x2={chartWidth - padRight}
                      y2={baselineYPos}
                      stroke={article.color}
                      strokeWidth="1.5"
                      strokeDasharray="5 4"
                      opacity="0.8"
                    />
                    <text
                      x={chartWidth - padRight}
                      y={baselineYPos - 6}
                      textAnchor="end"
                      fill={article.color}
                      className="pulse-baseline-label"
                    >
                      {article.chart.baseline.label}
                    </text>
                  </g>
                )}

                {/* X Axis Date Labels (sample ~6 to 8 ticks) */}
                {labels.map((lbl, idx) => {
                  const step = Math.max(1, Math.floor(labels.length / 7));
                  if (idx % step !== 0 && idx !== labels.length - 1) return null;
                  const x = getXPos(idx);
                  return (
                    <text
                      key={`xlab-${idx}`}
                      x={x}
                      y={chartHeight - 14}
                      textAnchor="middle"
                      className="pulse-axis-label"
                    >
                      {lbl}
                    </text>
                  );
                })}

                {/* Area fills */}
                {paths.map(p => (
                  <path
                    key={`area-${p.key}`}
                    d={p.areaD}
                    fill={`url(#grad-${article.slug}-${p.key})`}
                  />
                ))}

                {/* Main Lines */}
                {paths.map(p => (
                  <path
                    key={`line-${p.key}`}
                    d={p.lineD}
                    fill="none"
                    stroke={p.color}
                    strokeWidth="2.75"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    filter="url(#neon-glow)"
                  />
                ))}

                {/* Hover crosshair & dots */}
                {hoverIndex !== null && hoverIndex < labels.length && (
                  <g className="pulse-hover-group">
                    <line
                      x1={getXPos(hoverIndex)}
                      y1={padTop}
                      x2={getXPos(hoverIndex)}
                      y2={chartHeight - padBottom}
                      stroke="#64748b"
                      strokeWidth="1.5"
                      strokeDasharray="3 3"
                    />
                    {paths.map(p => {
                      const pt = p.pts[hoverIndex];
                      if (!pt) return null;
                      return (
                        <g key={`dot-${p.key}`}>
                          <circle
                            cx={pt.x}
                            cy={pt.y}
                            r="6"
                            fill={p.color}
                            stroke="#0f172a"
                            strokeWidth="2"
                          />
                          <circle
                            cx={pt.x}
                            cy={pt.y}
                            r="10"
                            fill={p.color}
                            opacity="0.3"
                          />
                        </g>
                      );
                    })}
                  </g>
                )}
              </svg>

              {/* Floating Tooltip HTML Overlay */}
              {hoverIndex !== null && hoverIndex < labels.length && (
                <div
                  className="pulse-interactive-tooltip"
                  style={{
                    left: `${Math.min(Math.max(15, (getXPos(hoverIndex) / chartWidth) * 100), 85)}%`,
                    top: '20px'
                  }}
                >
                  <div className="pulse-tooltip-header">
                    <span className="pulse-tooltip-date">{labels[hoverIndex]}</span>
                  </div>
                  <div className="pulse-tooltip-body">
                    {paths.map(p => {
                      const pt = p.pts[hoverIndex];
                      if (!pt) return null;
                      return (
                        <div key={`tip-${p.key}`} className="pulse-tooltip-row">
                          <span className="pulse-tooltip-key" style={{ color: p.color }}>
                            {p.label}:
                          </span>
                          <span className="pulse-tooltip-val">
                            {pt.v.toLocaleString()} {article.chart?.unit?.split('/')[0] || ''}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          </section>

          {/* Key Stat Cards (4 columns) */}
          <section className="pulse-stats-grid" aria-label="Key Indicator Metrics">
            {article.stats?.map((st, i) => (
              <div key={i} className="pulse-stat-card">
                <span className="pulse-stat-label">{st.label}</span>
                <div className="pulse-stat-val-row">
                  <span className="pulse-stat-val">{st.value}</span>
                  {st.trend && (
                    <span className={`pulse-stat-trend ${st.trend}`}>
                      {st.trend === 'up' ? '▲' : '▼'}
                    </span>
                  )}
                </div>
                <span className="pulse-stat-desc">{st.desc}</span>
              </div>
            ))}
          </section>

          {/* Editorial "What you're looking at" section */}
          <section className="pulse-editorial-section">
            <div className="pulse-editorial-header">
              <div className="pulse-editorial-pill">ANALYSIS &amp; MECHANICS</div>
              <h2 className="pulse-editorial-title">What you're looking at</h2>
            </div>

            <div className="pulse-notes-list">
              {article.notes?.map((n, i) => (
                <p key={i} className="pulse-note-para">
                  {n}
                </p>
              ))}
            </div>
          </section>

          {/* Official Source & Navigation Footer */}
          <footer className="pulse-article-footer">
            <div className="pulse-source-box">
              <span className="pulse-source-title">Official Primary Release:</span>
              <p className="pulse-source-text">{article.source}</p>
            </div>

            {/* Previous / Next Indicator Navigation */}
            <div className="pulse-pager-row">
              <button
                type="button"
                className="pulse-pager-btn pulse-pager-prev"
                onClick={goToPrev}
                title={`Go to ${prevArticle?.title || 'Previous'}`}
              >
                <span className="pulse-pager-arrow">←</span>
                <div className="pulse-pager-info">
                  <span className="pulse-pager-sub">Previous Indicator</span>
                  <span className="pulse-pager-title">{prevArticle?.idx}. {prevArticle?.title}</span>
                </div>
              </button>

              <button
                type="button"
                className="pulse-pager-btn pulse-pager-next"
                onClick={goToNext}
                title={`Go to ${nextArticle?.title || 'Next'}`}
              >
                <div className="pulse-pager-info text-right">
                  <span className="pulse-pager-sub">Next Indicator</span>
                  <span className="pulse-pager-title">{nextArticle?.idx}. {nextArticle?.title}</span>
                </div>
                <span className="pulse-pager-arrow">→</span>
              </button>
            </div>
          </footer>
        </div>
      </div>
    </div>
  );
}
