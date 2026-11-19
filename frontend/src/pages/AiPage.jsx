import { lazy, Suspense, useEffect, useMemo, useState, useTransition } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { api } from '../api.js';
import { useCompare } from '../compare.jsx';
import { Loading } from '../components/States.jsx';
import { formatMagnitude } from '../format.js';
import { useDocumentTitle } from '../hooks.js';

const ChartView = lazy(() => import('../components/ChartView.jsx'));

const PROMPT_SUGGESTIONS = [
  { label: '⚡ Green Energy Transition (Solar vs Coal)', query: 'solar renewable energy capacity coal' },
  { label: '💳 Digital Public Infrastructure & UPI Velocity', query: 'upi payments digital transactions' },
  { label: '📉 2020 COVID-19 GDP Contraction & Rebound', query: 'real gdp growth contraction pandemic 2020' },
  { label: '⚖️ Judicial Backlog & Court Pendency', query: 'court pendency high court cases disposal' },
  { label: '🌾 Foodgrain Production vs Monsoon', query: 'agriculture foodgrain production monsoon rainfall' },
  { label: '📊 CPI Inflation vs RBI Repo Rate', query: 'inflation cpi consumer prices repo rate' },
];

export const PRESET_PAIRS = [
  {
    name: 'Real GDP Growth vs Gross Capital Formation',
    keys: ['gdp_growth', 'capital_formation_gdp'],
    badge: '65-Year Capital Cycle',
    description: 'Investment rate dynamics vs headline economic expansion across six decades.',
  },
  {
    name: 'Real GDP Growth vs CPI Inflation',
    keys: ['gdp_growth', 'cpi'],
    badge: 'Phillips Curve & Shocks',
    description: 'Growth trajectory vs retail price pressure and monsoon supply shocks.',
  },
  {
    name: 'Exports vs Imports of Goods & Services',
    keys: ['exports_gdp', 'imports_gdp'],
    badge: 'Trade Synchrony',
    description: 'Structural trade co-movement and economic openness since 1991 reforms.',
  },
  {
    name: 'Clean Energy vs Coal Production Trajectory',
    keys: ['state_renewable_energy_capacity_all_india_trend', 'coal_production'],
    badge: 'Energy Transition',
    description: 'Surging renewable capacity alongside thermal baseload power demand.',
  },
];

const SYNTH_INDICATORS = [
  { key: 'gdp_growth', label: 'Real GDP Growth' },
  { key: 'capital_formation_gdp', label: 'Gross Capital Formation' },
  { key: 'cpi', label: 'CPI Inflation' },
  { key: 'public_debt_gdp', label: 'Central Government Debt' },
  { key: 'trade', label: 'Trade Share of GDP' },
];

const PALETTE = ['#2997ff', '#30d158', '#ffd60a', '#ff9f0a', '#bf5af2', '#64d2ff'];

export default function AiPage() {
  useDocumentTitle('AI Intelligence Hub');
  const compare = useCompare();
  const [params, setParams] = useSearchParams();
  const initialQuery = params.get('q') || '';
  const [searchQuery, setSearchQuery] = useState(initialQuery);
  const [searchResults, setSearchResults] = useState(null);
  const [searching, setSearching] = useState(false);
  const [, startTransition] = useTransition();

  // Correlation lab state
  const [selectedPair, setSelectedPair] = useState(PRESET_PAIRS[0].keys);
  const [rebaseNormalised, setRebaseNormalised] = useState(true);
  const [compareData, setCompareData] = useState(null);
  const [pairInsights, setPairInsights] = useState(null);
  const [pairLoading, setPairLoading] = useState(false);
  const [selectedShockYear, setSelectedShockYear] = useState(null);

  // Scenario Simulator state
  const [simShockPct, setSimShockPct] = useState(2.0);

  // Single-indicator synthesis state
  const [synthKey, setSynthKey] = useState('gdp_growth');
  const [synthIndicator, setSynthIndicator] = useState(null);
  const [synthData, setSynthData] = useState(null);
  const [synthLoading, setSynthLoading] = useState(false);

  // Run semantic search when query changes
  useEffect(() => {
    const q = searchQuery.trim();
    if (!q) {
      setSearchResults(null);
      setSearching(false);
      return;
    }
    const controller = new AbortController();
    setSearching(true);
    const timer = setTimeout(() => {
      api.aiSearch(q, undefined, controller.signal)
        .then(res => {
          setSearchResults(res?.results || []);
          setSearching(false);
        })
        .catch(err => {
          if (err.name !== 'AbortError') {
            setSearchResults([]);
            setSearching(false);
          }
        });
    }, 250);

    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [searchQuery]);

  // Load both compare time-series and correlation insights when pair changes
  useEffect(() => {
    if (!selectedPair || selectedPair.length < 2) return;
    const controller = new AbortController();
    setPairLoading(true);

    Promise.allSettled([
      api.compare(selectedPair, controller.signal),
      api.aiCompareInsights(selectedPair, controller.signal),
    ]).then(([compRes, insightRes]) => {
      if (compRes.status === 'fulfilled') {
        setCompareData(compRes.value);
      } else {
        setCompareData(null);
      }
      if (insightRes.status === 'fulfilled') {
        setPairInsights(insightRes.value);
        if (insightRes.value?.decouplings?.length > 0) {
          setSelectedShockYear(insightRes.value.decouplings[0].year);
        }
      } else {
        setPairInsights(null);
      }
      setPairLoading(false);
    });

    return () => controller.abort();
  }, [selectedPair]);

  // Load single-indicator series and insights
  useEffect(() => {
    if (!synthKey) return;
    const controller = new AbortController();
    setSynthLoading(true);

    Promise.allSettled([
      api.indicator(synthKey, controller.signal),
      api.aiInsights(synthKey, controller.signal),
    ]).then(([indRes, insightRes]) => {
      if (indRes.status === 'fulfilled') {
        setSynthIndicator(indRes.value);
      } else {
        setSynthIndicator(null);
      }
      if (insightRes.status === 'fulfilled') {
        setSynthData(insightRes.value);
      } else {
        setSynthData(null);
      }
      setSynthLoading(false);
    });

    return () => controller.abort();
  }, [synthKey]);

  // Chart datasets for correlation lab
  const chartDatasets = useMemo(() => {
    if (!compareData?.series || compareData.series.length === 0) return [];
    return compareData.series.map((item, index) => {
      let values = item.values;
      if (rebaseNormalised) {
        const base = values.find(value => typeof value === 'number' && value !== 0);
        values = base ? values.map(value => (typeof value === 'number' ? Math.round(((value / base) * 100) * 10) / 10 : null)) : values;
      }
      const color = item.color || PALETTE[index % PALETTE.length];
      return {
        label: item.title,
        data: values,
        borderColor: color,
        backgroundColor: color,
        tension: 0.25,
        pointRadius: 2,
      };
    });
  }, [compareData, rebaseNormalised]);

  // Single-series chart dataset & labels
  const singleChartDataset = useMemo(() => {
    const rawDatasets = synthIndicator?.datasets || synthIndicator?.series?.datasets;
    if (!rawDatasets?.[0]?.values) return [];
    const ds = rawDatasets[0];
    const color = synthIndicator?.color || '#2997ff';
    return [
      {
        label: synthIndicator?.title || 'Indicator',
        data: ds.values,
        borderColor: color,
        backgroundColor: color,
        tension: 0.25,
        pointRadius: 2,
      },
    ];
  }, [synthIndicator]);

  const synthLabels = useMemo(() => {
    return synthIndicator?.labels || synthIndicator?.series?.labels || [];
  }, [synthIndicator]);

  const handlePromptClick = query => {
    setSearchQuery(query);
    startTransition(() => {
      setParams({ q: query });
    });
  };

  const loadPairInLab = (keyA, keyB) => {
    setSelectedPair([keyA, keyB]);
    const el = document.getElementById('ai-correlation-lab');
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  const swapPair = () => {
    if (selectedPair && selectedPair.length >= 2) {
      setSelectedPair([selectedPair[1], selectedPair[0]]);
    }
  };

  // Correlation metrics helpers
  const primaryCorrelation = pairInsights?.correlations?.[0];
  const rVal = primaryCorrelation?.r ?? null;
  const rColor = rVal === null ? 'var(--muted, #86868b)' : (rVal >= 0.5 ? '#30d158' : (rVal <= -0.5 ? '#ff453a' : '#ffd60a'));
  const rPercentPos = rVal !== null ? Math.round(((rVal + 1) / 2) * 100) : 50;

  // Simulator elasticity estimation
  const simulatedTargetDelta = useMemo(() => {
    if (rVal === null || !compareData?.series || compareData.series.length < 2) return null;
    const vA = compareData.series[0].values.filter(v => typeof v === 'number');
    const vB = compareData.series[1].values.filter(v => typeof v === 'number');
    if (vA.length < 3 || vB.length < 3) return null;
    const meanA = vA.reduce((s, v) => s + v, 0) / vA.length;
    const meanB = vB.reduce((s, v) => s + v, 0) / vB.length;
    const stdA = Math.sqrt(vA.reduce((s, v) => s + (v - meanA) ** 2, 0) / vA.length);
    const stdB = Math.sqrt(vB.reduce((s, v) => s + (v - meanB) ** 2, 0) / vB.length);
    const beta = stdA > 1e-6 ? rVal * (stdB / stdA) : rVal;
    return Math.round(simShockPct * beta * 100) / 100;
  }, [rVal, compareData, simShockPct]);

  return (
    <div className="page ai-page" style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 16px 80px' }}>
      {/* Hero Header */}
      <header className="page-hero" style={{ padding: '40px 0 28px', textAlign: 'center' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', marginBottom: '10px', flexWrap: 'wrap', justifyContent: 'center' }}>
          <span className="badge" style={{ background: 'rgba(41, 151, 255, 0.15)', color: 'var(--accent, #2997ff)', fontSize: '0.84rem', padding: '4px 12px', fontWeight: 600 }}>
            ✨ Intelligent Policy Studio
          </span>
          <span className="badge" style={{ background: 'rgba(48, 209, 88, 0.15)', color: '#30d158', fontSize: '0.84rem', padding: '4px 12px', fontWeight: 600 }}>
            ₹0 Cloud Budget · Real-Time Statistical In-Memory Engine
          </span>
        </div>
        <h1 style={{ fontSize: 'clamp(2.1rem, 4.2vw, 3rem)', margin: '6px 0 10px', fontWeight: 800 }}>
          AI Intelligence Hub <span className="vintage-nav-sublabel" style={{ fontSize: '1.25rem', color: 'var(--muted, #86868b)' }}>कृत्रिमबुद्धिः</span>
        </h1>
        <p className="lead" style={{ maxWidth: '760px', margin: '0 auto 16px', fontSize: '1.08rem', color: 'var(--muted, #86868b)', lineHeight: '1.5' }}>
          Explore autonomous dual-series co-movement, structural shock detection, and macroeconomic inflection radars across 3,082 verified public indicators.
        </p>
      </header>

      {/* Module 1: AI Dual-Series Correlation & Decoupling Laboratory */}
      <section id="ai-correlation-lab" className="card" style={{ padding: '28px 24px', marginBottom: '36px', borderLeft: '4px solid var(--accent, #2997ff)', borderRadius: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '1.5rem', color: 'var(--accent, #2997ff)' }}>⇄</span>
          <h2 style={{ margin: 0, fontSize: '1.45rem', fontWeight: 700 }}>AI Correlation &amp; Decoupling Laboratory</h2>
          <span className="badge" style={{ marginLeft: 'auto', background: 'rgba(41, 151, 255, 0.15)', color: 'var(--accent, #2997ff)', fontSize: '0.76rem', padding: '4px 10px' }}>
            Phase 2B Engine
          </span>
        </div>
        <p className="muted" style={{ margin: '0 0 20px', fontSize: '0.94rem', lineHeight: '1.45' }}>
          Select an analytical preset or customize any two indicators to render live dual-axis charts, compute in-memory Pearson co-movement ($r$), and isolate structural decoupling shocks.
        </p>

        {/* Preset Cards Grid - Fixes Squished Row & Text Overlap */}
        <div style={{ marginBottom: '22px' }}>
          <span className="muted small" style={{ display: 'block', marginBottom: '10px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Macroeconomic Presets:
          </span>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '12px' }}>
            {PRESET_PAIRS.map(preset => {
              const active = selectedPair[0] === preset.keys[0] && selectedPair[1] === preset.keys[1];
              return (
                <button
                  key={preset.name}
                  type="button"
                  onClick={() => setSelectedPair(preset.keys)}
                  style={{
                    textAlign: 'left',
                    padding: '14px 16px',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'flex-start',
                    gap: '6px',
                    borderRadius: '10px',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease-in-out',
                    border: active ? '2px solid var(--accent, #2997ff)' : '1px solid var(--line, rgba(255,255,255,0.1))',
                    background: active ? 'rgba(41, 151, 255, 0.12)' : 'var(--surface-1, rgba(255,255,255,0.03))',
                    color: 'inherit',
                    whiteSpace: 'normal',
                    wordBreak: 'break-word',
                    boxShadow: active ? '0 0 14px rgba(41,151,255,0.25)' : 'none',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', gap: '6px' }}>
                    <span style={{ fontWeight: 700, fontSize: '0.92rem', color: active ? 'var(--accent, #2997ff)' : 'inherit' }}>
                      {preset.name}
                    </span>
                  </div>
                  <span className="badge" style={{ fontSize: '0.68rem', padding: '2px 6px', background: 'rgba(255,255,255,0.08)' }}>
                    {preset.badge}
                  </span>
                  <span className="muted small" style={{ fontSize: '0.78rem', lineHeight: '1.35', opacity: 0.9 }}>
                    {preset.description}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Interactive Dual-Chart Workbench */}
        {pairLoading && <Loading label="Calculating Pearson co-movement matrix and synchronizing series…" />}

        {compareData && compareData.series?.length >= 2 && !pairLoading && (
          <div style={{ marginTop: '16px', background: 'rgba(255,255,255,0.02)', padding: '20px', borderRadius: '12px', border: '1px solid var(--line, rgba(255,255,255,0.08))' }}>
            {/* Workbench Toolbar */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px', marginBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                <span className="badge" style={{ background: 'rgba(41, 151, 255, 0.2)', color: 'var(--accent, #2997ff)', fontSize: '0.82rem', padding: '4px 10px' }}>
                  Series A: {compareData.series[0]?.title}
                </span>
                <span style={{ color: 'var(--muted, #86868b)' }}>vs</span>
                <span className="badge" style={{ background: 'rgba(48, 209, 88, 0.2)', color: '#30d158', fontSize: '0.82rem', padding: '4px 10px' }}>
                  Series B: {compareData.series[1]?.title}
                </span>
                <button
                  type="button"
                  className="btn btn-ghost"
                  onClick={swapPair}
                  title="Swap lead series"
                  style={{ fontSize: '0.78rem', padding: '4px 8px' }}
                >
                  ⇄ Swap
                </button>
              </div>

              {/* Rebase Toggle */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <label className="switch" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.86rem' }}>
                  <input
                    type="checkbox"
                    checked={rebaseNormalised}
                    onChange={e => setRebaseNormalised(e.target.checked)}
                  />
                  <span><strong>Rebase to 100</strong> (Indexed Co-Movement)</span>
                </label>
              </div>
            </div>

            {/* Visual Interactive Chart */}
            <div className="detail-chart" style={{ minHeight: '340px', marginBottom: '20px' }}>
              <Suspense fallback={<div className="chart-skeleton" style={{ height: '320px' }} />}>
                <ChartView
                  title={`${compareData.series[0]?.title} vs ${compareData.series[1]?.title}`}
                  labels={compareData.labels}
                  datasets={chartDatasets}
                  type="line"
                  suffix={rebaseNormalised ? '' : (compareData.series[0]?.suffix === compareData.series[1]?.suffix ? compareData.series[0]?.suffix : '')}
                />
              </Suspense>
            </div>

            {/* Visual Pearson Correlation Gauge */}
            {primaryCorrelation && (
              <div style={{ background: 'var(--surface-1, rgba(255,255,255,0.03))', padding: '16px 20px', borderRadius: '10px', border: '1px solid var(--line, rgba(255,255,255,0.08))', marginBottom: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', marginBottom: '10px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                    <div style={{ fontSize: '1.9rem', fontWeight: 800, color: rColor, fontFamily: 'monospace' }}>
                      {rVal !== null ? `r = ${rVal >= 0 ? '+' : ''}${rVal.toFixed(2)}` : 'r = N/A'}
                    </div>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: '1.02rem', color: rColor }}>
                        {primaryCorrelation.strength}
                      </div>
                      <div className="muted small" style={{ fontSize: '0.82rem' }}>
                        Sample size: <strong>{primaryCorrelation.sample_size} shared periods</strong> ({primaryCorrelation.start_year || '–'} to {primaryCorrelation.end_year || '–'})
                      </div>
                    </div>
                  </div>

                  <span className="badge" style={{ fontSize: '0.76rem', background: 'rgba(255,255,255,0.08)', padding: '4px 10px' }}>
                    Normalized Pearson Matrix
                  </span>
                </div>

                {/* Linear Gauge Bar */}
                <div style={{ marginTop: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--muted, #86868b)', marginBottom: '4px' }}>
                    <span>-1.00 (Inverse Trade-off)</span>
                    <span>0.00 (Decoupled / Independent)</span>
                    <span>+1.00 (Strong Co-Movement)</span>
                  </div>
                  <div style={{ height: '8px', width: '100%', background: 'rgba(255,255,255,0.1)', borderRadius: '4px', position: 'relative', overflow: 'hidden' }}>
                    <div
                      style={{
                        position: 'absolute',
                        top: 0,
                        bottom: 0,
                        left: `${Math.max(0, Math.min(100, rPercentPos))}%`,
                        width: '12px',
                        transform: 'translateX(-50%)',
                        background: rColor,
                        borderRadius: '3px',
                        boxShadow: `0 0 8px ${rColor}`,
                      }}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Historical Decoupling Shocks */}
            {pairInsights?.decouplings?.length > 0 && (
              <div style={{ marginBottom: '18px', borderTop: '1px solid var(--line, rgba(255,255,255,0.08))', paddingTop: '16px' }}>
                <span style={{ fontWeight: 700, fontSize: '0.92rem', display: 'block', marginBottom: '10px' }}>
                  ⚡ Historical Decoupling Shocks &amp; Divergent Inflections:
                </span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '12px' }}>
                  {pairInsights.decouplings.map((dec, i) => {
                    const isSelected = selectedShockYear === dec.year;
                    return (
                      <button
                        key={i}
                        type="button"
                        onClick={() => setSelectedShockYear(dec.year)}
                        className={`btn ${isSelected ? 'btn-primary' : 'btn-ghost'}`}
                        style={{ fontSize: '0.8rem', padding: '6px 12px', borderRadius: '16px' }}
                      >
                        <strong>{dec.year}</strong>: {dec.event || dec.note || 'Shock'}
                      </button>
                    );
                  })}
                </div>

                {/* Active Selected Shock Callout */}
                {selectedShockYear && (
                  <div style={{ padding: '12px 16px', background: 'rgba(255, 69, 58, 0.08)', borderLeft: '3px solid #ff453a', borderRadius: '6px', fontSize: '0.86rem', lineHeight: '1.45' }}>
                    {(() => {
                      const shock = pairInsights.decouplings.find(d => d.year === selectedShockYear);
                      return shock?.observation || shock?.note || `Divergence observed in ${selectedShockYear}.`;
                    })()}
                  </div>
                )}
              </div>
            )}

            {/* AI Synthesized Policy Takeaways */}
            {pairInsights?.takeaways?.length > 0 && (
              <div style={{ marginTop: '14px', borderTop: '1px solid var(--line, rgba(255,255,255,0.08))', paddingTop: '14px' }}>
                <span style={{ fontWeight: 700, fontSize: '0.9rem', display: 'block', marginBottom: '8px' }}>
                  AI Structural Synthesis:
                </span>
                <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '0.88rem', lineHeight: '1.5' }}>
                  {pairInsights.takeaways.map((t, idx) => (
                    <li key={idx} style={{ marginBottom: '4px' }}>{t}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Action Bar */}
            <div style={{ marginTop: '20px', display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
              <Link
                to={`/compare?keys=${selectedPair.join(',')}`}
                className="btn btn-primary"
                style={{ fontSize: '0.88rem' }}
              >
                Open in Full Multi-Indicator Compare Tray →
              </Link>
              <button
                type="button"
                className="btn btn-ghost"
                onClick={() => {
                  const el = document.getElementById('ai-what-if-sim');
                  if (el) el.scrollIntoView({ behavior: 'smooth' });
                }}
                style={{ fontSize: '0.88rem' }}
              >
                Simulate Policy Shock ↓
              </button>
            </div>
          </div>
        )}
      </section>

      {/* Module 2: Interactive What-If Scenario Stress Simulator */}
      <section id="ai-what-if-sim" className="card" style={{ padding: '24px', marginBottom: '36px', border: '1px solid var(--line, rgba(255,255,255,0.08))', borderRadius: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '1.4rem' }}>🧪</span>
          <h2 style={{ margin: 0, fontSize: '1.35rem', fontWeight: 700 }}>What-If Scenario Stress Simulator</h2>
          <span className="badge" style={{ marginLeft: 'auto', background: 'rgba(255, 214, 10, 0.15)', color: '#ffd60a', fontSize: '0.76rem', padding: '4px 10px' }}>
            Elasticity Co-Movement Model
          </span>
        </div>
        <p className="muted small" style={{ margin: '0 0 16px', lineHeight: '1.45' }}>
          Simulate a hypothetical shock on the leading series to observe the estimated statistical elasticity co-movement on the paired series based on historical Pearson covariance.
        </p>

        <div style={{ background: 'var(--surface-1, rgba(255,255,255,0.02))', padding: '18px', borderRadius: '10px', border: '1px solid var(--line, rgba(255,255,255,0.06))' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>
              Simulated Shock on {compareData?.series?.[0]?.title || 'Leading Series'}:
            </span>
            <span style={{ fontSize: '1.1rem', fontWeight: 800, color: simShockPct >= 0 ? '#30d158' : '#ff453a' }}>
              {simShockPct >= 0 ? `+${simShockPct.toFixed(1)}%` : `${simShockPct.toFixed(1)}%`}
            </span>
          </div>

          <input
            type="range"
            min="-5.0"
            max="5.0"
            step="0.5"
            value={simShockPct}
            onChange={e => setSimShockPct(parseFloat(e.target.value))}
            style={{ width: '100%', cursor: 'pointer', margin: '8px 0 14px' }}
          />

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px', paddingTop: '10px', borderTop: '1px solid var(--line, rgba(255,255,255,0.06))' }}>
            <div>
              <span className="muted small" style={{ display: 'block' }}>Estimated Response on {compareData?.series?.[1]?.title || 'Paired Series'}:</span>
              <span style={{ fontSize: '1.2rem', fontWeight: 800, color: simulatedTargetDelta !== null && simulatedTargetDelta >= 0 ? 'var(--accent, #2997ff)' : '#ff9f0a' }}>
                {simulatedTargetDelta !== null ? `${simulatedTargetDelta >= 0 ? '+' : ''}${simulatedTargetDelta.toFixed(2)}% expected co-movement` : 'Calculating…'}
              </span>
            </div>
            <button
              type="button"
              className="btn btn-ghost"
              onClick={() => setSimShockPct(2.0)}
              style={{ fontSize: '0.78rem' }}
            >
              Reset to +2.0%
            </button>
          </div>
        </div>
      </section>

      {/* Module 3: Macroeconomic Inflection & Anomaly Synthesizer */}
      <section className="card" style={{ padding: '28px 24px', marginBottom: '36px', border: '1px solid var(--line, rgba(255,255,255,0.08))', borderRadius: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '1.4rem' }}>📈</span>
          <h2 style={{ margin: 0, fontSize: '1.35rem', fontWeight: 700 }}>Macroeconomic Inflection &amp; Anomaly Synthesizer</h2>
          <span className="badge" style={{ marginLeft: 'auto', fontSize: '0.76rem', padding: '4px 10px' }}>Automated Series Context</span>
        </div>
        <p className="muted small" style={{ margin: '0 0 16px', lineHeight: '1.45' }}>
          Select any foundational indicator to synthesize all-time extremes, structural trajectory, and historical policy lineage.
        </p>

        {/* Indicator Switcher Pills */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '20px' }}>
          {SYNTH_INDICATORS.map(item => (
            <button
              key={item.key}
              type="button"
              className={`btn ${synthKey === item.key ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setSynthKey(item.key)}
              style={{ fontSize: '0.84rem', padding: '8px 14px', borderRadius: '8px' }}
            >
              {item.label}
            </button>
          ))}
        </div>

        {synthLoading && <Loading label="Synthesizing inflection points and anomalies…" />}

        {synthIndicator && synthData && !synthLoading && (
          <div style={{ background: 'rgba(255,255,255,0.02)', padding: '20px', borderRadius: '12px', border: '1px solid var(--line, rgba(255,255,255,0.06))' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px', marginBottom: '16px' }}>
              <div>
                <h3 style={{ margin: '0 0 4px', fontSize: '1.2rem', fontWeight: 700 }}>{synthData.title || synthIndicator.title}</h3>
                <span className="muted small">{synthIndicator.category} · {synthIndicator.subgroup}</span>
              </div>
              <span className="badge" style={{ fontSize: '0.78rem' }}>
                Unit: {synthIndicator.suffix || 'Value'}
              </span>
            </div>

            {/* 4 KPI Metric Cards */}
            {synthData.metrics && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '10px', marginBottom: '20px' }}>
                {synthData.metrics.peak && (
                  <div style={{ background: 'var(--surface-1, rgba(255,255,255,0.03))', padding: '12px 14px', borderRadius: '8px', border: '1px solid var(--line, rgba(255,255,255,0.06))' }}>
                    <span className="muted small" style={{ fontSize: '0.74rem', display: 'block' }}>🌟 All-Time Peak</span>
                    <span style={{ fontSize: '1.25rem', fontWeight: 800, color: '#30d158' }}>
                      {formatMagnitude(synthData.metrics.peak.value, synthData.metrics.unit)}
                    </span>
                    <span className="muted small" style={{ fontSize: '0.74rem', display: 'block', marginTop: '2px' }}>
                      Year {synthData.metrics.peak.label}
                    </span>
                  </div>
                )}

                {synthData.metrics.trough && (
                  <div style={{ background: 'var(--surface-1, rgba(255,255,255,0.03))', padding: '12px 14px', borderRadius: '8px', border: '1px solid var(--line, rgba(255,255,255,0.06))' }}>
                    <span className="muted small" style={{ fontSize: '0.74rem', display: 'block' }}>🔻 Historical Low / Trough</span>
                    <span style={{ fontSize: '1.25rem', fontWeight: 800, color: '#ff453a' }}>
                      {formatMagnitude(synthData.metrics.trough.value, synthData.metrics.unit)}
                    </span>
                    <span className="muted small" style={{ fontSize: '0.74rem', display: 'block', marginTop: '2px' }}>
                      Year {synthData.metrics.trough.label}
                    </span>
                  </div>
                )}

                {synthData.metrics.latest && (
                  <div style={{ background: 'var(--surface-1, rgba(255,255,255,0.03))', padding: '12px 14px', borderRadius: '8px', border: '1px solid var(--line, rgba(255,255,255,0.06))' }}>
                    <span className="muted small" style={{ fontSize: '0.74rem', display: 'block' }}>📌 Latest Observation</span>
                    <span style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--accent, #2997ff)' }}>
                      {formatMagnitude(synthData.metrics.latest.value, synthData.metrics.unit)}
                    </span>
                    <span className="muted small" style={{ fontSize: '0.74rem', display: 'block', marginTop: '2px' }}>
                      Year {synthData.metrics.latest.label}
                    </span>
                  </div>
                )}

                {synthData.metrics.delta !== undefined && (
                  <div style={{ background: 'var(--surface-1, rgba(255,255,255,0.03))', padding: '12px 14px', borderRadius: '8px', border: '1px solid var(--line, rgba(255,255,255,0.06))' }}>
                    <span className="muted small" style={{ fontSize: '0.74rem', display: 'block' }}>📈 Net Cumulative Shift</span>
                    <span style={{ fontSize: '1.25rem', fontWeight: 800, color: synthData.metrics.delta >= 0 ? '#30d158' : '#ff453a' }}>
                      {synthData.metrics.delta >= 0 ? `+${synthData.metrics.delta}` : synthData.metrics.delta} {synthData.metrics.unit}
                    </span>
                    <span className="muted small" style={{ fontSize: '0.74rem', display: 'block', marginTop: '2px' }}>
                      Over Full Historical Horizon
                    </span>
                  </div>
                )}
              </div>
            )}

            {/* Interactive Single Chart */}
            <div className="detail-chart" style={{ minHeight: '300px', marginBottom: '20px' }}>
              <Suspense fallback={<div className="chart-skeleton" style={{ height: '280px' }} />}>
                <ChartView
                  title={synthIndicator.title || 'Indicator'}
                  labels={synthLabels}
                  datasets={singleChartDataset}
                  type="line"
                  suffix={synthIndicator.suffix || ''}
                />
              </Suspense>
            </div>

            {/* Executive Takeaways */}
            {synthData.takeaways && (
              <div style={{ borderTop: '1px solid var(--line, rgba(255,255,255,0.08))', paddingTop: '14px', marginTop: '14px' }}>
                <span style={{ fontWeight: 700, fontSize: '0.9rem', display: 'block', marginBottom: '8px' }}>
                  Macro Inflection Insights:
                </span>
                <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '0.88rem', lineHeight: '1.5' }}>
                  {synthData.takeaways.map((point, idx) => (
                    <li key={idx} style={{ marginBottom: '6px' }}>{point}</li>
                  ))}
                </ul>
              </div>
            )}

            <div style={{ marginTop: '18px', display: 'flex', gap: '10px' }}>
              <Link to={`/indicator/${synthKey}`} className="btn btn-primary" style={{ fontSize: '0.84rem' }}>
                View Indicator Deep-Dive &amp; Raw CSV ›
              </Link>
            </div>
          </div>
        )}
      </section>

      {/* Module 4: Ask India's Journey AI Copilot */}
      <section className="card" style={{ padding: '28px 24px', border: '1px solid var(--line, rgba(255,255,255,0.08))', borderRadius: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '1.4rem' }}>🔍</span>
          <h2 style={{ margin: 0, fontSize: '1.35rem', fontWeight: 700 }}>Ask India's Journey AI</h2>
          <span className="badge" style={{ marginLeft: 'auto', fontSize: '0.76rem', padding: '4px 10px' }}>Semantic Vector Search</span>
        </div>
        <p className="muted small" style={{ margin: '0 0 16px', lineHeight: '1.45' }}>
          Type any macroeconomic, political, or development question in natural language to search across all 3,082 indexed public indicators.
        </p>

        <div style={{ position: 'relative', marginBottom: '16px' }}>
          <input
            type="search"
            className="input"
            value={searchQuery}
            onChange={e => {
              setSearchQuery(e.target.value);
              startTransition(() => {
                setParams(e.target.value ? { q: e.target.value } : {});
              });
            }}
            placeholder="E.g., Which indicators captured the 2020 economic contraction? How fast is UPI growing?"
            style={{
              width: '100%',
              padding: '14px 18px',
              fontSize: '1rem',
              borderRadius: '12px',
              border: '1px solid var(--line, rgba(255,255,255,0.15))',
              background: 'var(--surface-1, rgba(255,255,255,0.02))',
              color: 'inherit',
            }}
          />
        </div>

        {/* Suggested Prompts */}
        <div>
          <span className="muted small" style={{ display: 'block', marginBottom: '8px', fontWeight: 600 }}>
            Suggested Queries:
          </span>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {PROMPT_SUGGESTIONS.map(sug => (
              <button
                key={sug.label}
                type="button"
                className="btn btn-ghost"
                onClick={() => handlePromptClick(sug.query)}
                style={{ fontSize: '0.8rem', padding: '6px 12px', borderRadius: '16px' }}
              >
                {sug.label}
              </button>
            ))}
          </div>
        </div>

        {/* Search Results Display */}
        {searching && (
          <div style={{ marginTop: '20px' }}>
            <Loading label="Running vector cosine similarity search across 3,082 indicators…" />
          </div>
        )}

        {searchResults && !searching && (
          <div style={{ marginTop: '24px', borderTop: '1px solid var(--line, rgba(255,255,255,0.08))', paddingTop: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <span style={{ fontWeight: 700, fontSize: '0.94rem' }}>
                AI Semantic Matches ({searchResults.length})
              </span>
              <span className="muted small">Ranked by In-Memory Cosine Similarity</span>
            </div>

            {searchResults.length === 0 ? (
              <p className="muted small">No direct match found. Try broader terms like &quot;GDP&quot;, &quot;energy&quot;, or &quot;inflation&quot;.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {searchResults.map(result => (
                  <div
                    key={result.key}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '12px 16px',
                      background: 'rgba(255, 255, 255, 0.02)',
                      borderRadius: '8px',
                      border: '1px solid var(--line, rgba(255,255,255,0.05))',
                      flexWrap: 'wrap',
                      gap: '10px',
                    }}
                  >
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontWeight: 600, fontSize: '0.96rem' }}>{result.title}</span>
                        <span className="badge" style={{ fontSize: '0.72rem' }}>
                          {Math.round(result.similarity * 100)}% match
                        </span>
                      </div>
                      <span className="muted small">
                        {result.category} · {result.subgroup}
                      </span>
                    </div>

                    <div style={{ display: 'flex', gap: '8px' }}>
                      <Link to={`/indicator/${result.key}`} className="btn btn-ghost" style={{ fontSize: '0.8rem', padding: '6px 12px' }}>
                        View Chart →
                      </Link>
                      <button
                        type="button"
                        className="btn btn-primary"
                        onClick={() => {
                          if (selectedPair[0] !== result.key) {
                            loadPairInLab(selectedPair[0], result.key);
                          } else {
                            loadPairInLab(result.key, 'capital_formation_gdp');
                          }
                        }}
                        style={{ fontSize: '0.8rem', padding: '6px 12px' }}
                      >
                        Load in AI Lab ⇄
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </section>
    </div>
  );
}
