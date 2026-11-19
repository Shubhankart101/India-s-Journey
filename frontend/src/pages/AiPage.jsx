import { useEffect, useState, useTransition } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { api } from '../api.js';
import { useCompare } from '../compare.jsx';
import { Loading } from '../components/States.jsx';
import { useDocumentTitle } from '../hooks.js';

const PROMPT_SUGGESTIONS = [
  { label: '⚡ Green Energy Transition (Solar vs Coal)', query: 'solar renewable energy capacity coal' },
  { label: '💳 Digital Public Infrastructure & UPI Velocity', query: 'upi payments digital transactions' },
  { label: '📉 2020 COVID-19 GDP Contraction & Rebound', query: 'real gdp growth contraction pandemic 2020' },
  { label: '⚖️ Judicial Backlog & Court Pendency', query: 'court pendency high court cases disposal' },
  { label: '🌾 Foodgrain Production vs Monsoon', query: 'agriculture foodgrain production monsoon rainfall' },
  { label: '📊 CPI Inflation vs RBI Repo Rate', query: 'inflation cpi consumer prices repo rate' },
];

const PRESET_PAIRS = [
  {
    name: 'Real GDP Growth vs Industrial Production',
    keys: ['gdp_growth', 'iip_growth'],
    description: 'Headline economic expansion vs physical manufacturing throughput.',
  },
  {
    name: 'Renewable Power vs Thermal Generation',
    keys: ['solar_installed_gw', 'coal_generation_twh'],
    description: 'Decarbonization trajectory and clean energy substitution.',
  },
  {
    name: 'Digital Payments (UPI) vs Currency in Circulation',
    keys: ['upi_volume_crores', 'currency_in_circulation_lakh_cr'],
    description: 'Cash-to-digital velocity shift across India’s payments rails.',
  },
  {
    name: 'Headline CPI Inflation vs 10-Yr Benchmark Yield',
    keys: ['cpi_inflation', 'gsec_10yr_yield'],
    description: 'Monetary transmission and sovereign debt risk pricing.',
  },
];

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
  const [pairInsights, setPairInsights] = useState(null);
  const [pairLoading, setPairLoading] = useState(false);

  // Single-indicator synthesis state
  const [synthKey, setSynthKey] = useState('gdp_growth');
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

  // Run correlation synthesis when pair changes
  useEffect(() => {
    if (!selectedPair || selectedPair.length < 2) return;
    const controller = new AbortController();
    setPairLoading(true);
    api.aiCompareInsights(selectedPair, controller.signal)
      .then(res => {
        setPairInsights(res);
        setPairLoading(false);
      })
      .catch(() => {
        setPairLoading(false);
      });
    return () => controller.abort();
  }, [selectedPair]);

  // Run single-indicator insights when key changes
  useEffect(() => {
    if (!synthKey) return;
    const controller = new AbortController();
    setSynthLoading(true);
    api.aiInsights(synthKey, controller.signal)
      .then(res => {
        setSynthData(res);
        setSynthLoading(false);
      })
      .catch(() => {
        setSynthLoading(false);
      });
    return () => controller.abort();
  }, [synthKey]);

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

  return (
    <div className="page ai-page" style={{ maxWidth: '1180px', margin: '0 auto', padding: '0 16px 64px' }}>
      {/* Hero Header */}
      <header className="page-hero" style={{ padding: '40px 0 24px', textAlign: 'center' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <span className="badge" style={{ background: 'rgba(41, 151, 255, 0.15)', color: 'var(--accent, #2997ff)', fontSize: '0.82rem', padding: '4px 10px' }}>
            ✨ Intelligent Policy Analytics
          </span>
          <span className="badge" style={{ background: 'rgba(48, 209, 88, 0.15)', color: '#30d158', fontSize: '0.82rem', padding: '4px 10px' }}>
            ₹0 Budget · In-Memory Vectors
          </span>
        </div>
        <h1 style={{ fontSize: 'clamp(2rem, 4vw, 2.8rem)', margin: '4px 0 8px' }}>
          AI Intelligence Hub <span className="vintage-nav-sublabel" style={{ fontSize: '1.2rem', color: 'var(--muted, #86868b)' }}>कृत्रिमबुद्धिः</span>
        </h1>
        <p className="lead" style={{ maxWidth: '720px', margin: '0 auto 16px', fontSize: '1.05rem', color: 'var(--muted, #86868b)' }}>
          Autonomous statistical correlation, structural shock detection, and semantic inquiry across all 3,082 verified public indicators.
        </p>
      </header>

      {/* Module 1: Ask India's Journey AI */}
      <section className="card" style={{ padding: '24px', marginBottom: '32px', border: '1px solid var(--line, rgba(255,255,255,0.08))' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
          <span style={{ fontSize: '1.4rem' }}>🔍</span>
          <h2 style={{ margin: 0, fontSize: '1.35rem' }}>Ask India's Journey AI</h2>
          <span className="badge" style={{ marginLeft: 'auto', fontSize: '0.74rem' }}>Semantic Vector Search</span>
        </div>
        <p className="muted small" style={{ margin: '0 0 16px' }}>
          Type any macroeconomic, political, or development question in natural language to retrieve indexed public series.
        </p>

        <div style={{ position: 'relative', marginBottom: '14px' }}>
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
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>
                AI Semantic Matches ({searchResults.length})
              </span>
              <span className="muted small">Ranked by Cosine Similarity</span>
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
                            loadPairInLab(result.key, 'gdp_growth');
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

      {/* Module 2: AI Cross-Series Correlation & Shock Lab */}
      <section id="ai-correlation-lab" className="card" style={{ padding: '24px', marginBottom: '32px', borderLeft: '4px solid var(--accent, #2997ff)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '1.4rem' }}>⇄</span>
          <h2 style={{ margin: 0, fontSize: '1.35rem' }}>AI Correlation &amp; Decoupling Laboratory</h2>
          <span className="badge" style={{ marginLeft: 'auto', background: 'rgba(41, 151, 255, 0.15)', color: 'var(--accent, #2997ff)', fontSize: '0.74rem' }}>
            Phase 2B Engine
          </span>
        </div>
        <p className="muted small" style={{ margin: '0 0 16px' }}>
          Select or customize series pairs to calculate in-memory Pearson co-movement ($r$) and isolate structural decoupling shocks.
        </p>

        {/* Quick Pair Presets */}
        <div style={{ marginBottom: '16px' }}>
          <span className="muted small" style={{ display: 'block', marginBottom: '8px', fontWeight: 600 }}>
            Macroeconomic Presets:
          </span>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '8px' }}>
            {PRESET_PAIRS.map(preset => {
              const active = selectedPair[0] === preset.keys[0] && selectedPair[1] === preset.keys[1];
              return (
                <button
                  key={preset.name}
                  type="button"
                  className={`btn ${active ? 'btn-primary' : 'btn-ghost'}`}
                  onClick={() => setSelectedPair(preset.keys)}
                  style={{
                    textAlign: 'left',
                    padding: '10px 14px',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'flex-start',
                    gap: '2px',
                    height: 'auto',
                  }}
                >
                  <span style={{ fontWeight: 600, fontSize: '0.86rem' }}>{preset.name}</span>
                  <span className="muted small" style={{ fontSize: '0.72rem', opacity: 0.85 }}>{preset.description}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Active Analysis Output */}
        {pairLoading && <Loading label="Calculating real-time Pearson matrix and historical divergence points…" />}

        {pairInsights && !pairLoading && (
          <div style={{ marginTop: '16px', background: 'rgba(255,255,255,0.02)', padding: '16px', borderRadius: '10px', border: '1px solid var(--line, rgba(255,255,255,0.06))' }}>
            {/* Correlation Header */}
            {pairInsights.correlations && pairInsights.correlations.length > 0 && (
              <div>
                {pairInsights.correlations.map(corr => {
                  const rVal = corr.r;
                  const color = rVal === null ? 'var(--muted, #86868b)' : (rVal >= 0.5 ? '#30d158' : (rVal <= -0.5 ? '#ff453a' : '#ffd60a'));
                  return (
                    <div key={`${corr.pair[0]}-${corr.pair[1]}`} style={{ marginBottom: '16px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flexWrap: 'wrap', marginBottom: '10px' }}>
                        <span style={{ fontSize: '1.6rem', fontWeight: 800, color }}>
                          {rVal !== null ? `r = ${rVal >= 0 ? '+' : ''}${rVal.toFixed(2)}` : 'r = N/A'}
                        </span>
                        <div>
                          <span style={{ fontWeight: 700, fontSize: '1rem', display: 'block' }}>{corr.strength}</span>
                          <span className="muted small">
                            {corr.titles[0]} &amp; {corr.titles[1]} · Sample size: {corr.sample_size} periods ({corr.start_year || '–'} to {corr.end_year || '–'})
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Decoupling Shocks */}
            {pairInsights.decouplings && pairInsights.decouplings.length > 0 && (
              <div style={{ marginTop: '14px', borderTop: '1px solid var(--line, rgba(255,255,255,0.08))', paddingTop: '12px' }}>
                <span style={{ fontWeight: 600, fontSize: '0.88rem', display: 'block', marginBottom: '8px' }}>
                  ⚡ Historical Decoupling Shocks &amp; Divergence
                </span>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {pairInsights.decouplings.map((dec, i) => (
                    <div
                      key={i}
                      style={{
                        padding: '8px 12px',
                        background: 'rgba(255, 69, 58, 0.08)',
                        borderLeft: '3px solid #ff453a',
                        borderRadius: '4px',
                        fontSize: '0.84rem',
                      }}
                    >
                      <strong>{dec.year}:</strong> {dec.note}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* AI Synthesized Takeaways */}
            {pairInsights.takeaways && (
              <div style={{ marginTop: '14px', borderTop: '1px solid var(--line, rgba(255,255,255,0.08))', paddingTop: '12px' }}>
                <span style={{ fontWeight: 600, fontSize: '0.88rem', display: 'block', marginBottom: '8px' }}>
                  AI Policy Synthesis
                </span>
                <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '0.86rem', lineHeight: '1.5' }}>
                  {pairInsights.takeaways.map((t, idx) => (
                    <li key={idx} style={{ marginBottom: '4px' }}>{t}</li>
                  ))}
                </ul>
              </div>
            )}

            <div style={{ marginTop: '18px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
              <Link
                to={`/compare?keys=${selectedPair.join(',')}`}
                className="btn btn-primary"
                style={{ fontSize: '0.85rem' }}
              >
                Open in Full Multi-Indicator Compare Tray →
              </Link>
            </div>
          </div>
        )}
      </section>

      {/* Module 3: Macroeconomic Inflection & Anomaly Synthesizer */}
      <section className="card" style={{ padding: '24px', border: '1px solid var(--line, rgba(255,255,255,0.08))' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '1.4rem' }}>📈</span>
          <h2 style={{ margin: 0, fontSize: '1.35rem' }}>Macroeconomic Inflection &amp; Anomaly Synthesizer</h2>
          <span className="badge" style={{ marginLeft: 'auto', fontSize: '0.74rem' }}>Automated Series Context</span>
        </div>
        <p className="muted small" style={{ margin: '0 0 16px' }}>
          Select any core indicator to synthesize all-time extremes, structural trajectory, and historical lineage.
        </p>

        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '16px' }}>
          {[
            { key: 'gdp_growth', label: 'Real GDP Growth' },
            { key: 'solar_installed_gw', label: 'Solar Power Capacity' },
            { key: 'upi_volume_crores', label: 'UPI Transaction Volume' },
            { key: 'cpi_inflation', label: 'CPI Headline Inflation' },
            { key: 'high_court_pendency', label: 'High Court Case Pendency' },
          ].map(item => (
            <button
              key={item.key}
              type="button"
              className={`btn ${synthKey === item.key ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setSynthKey(item.key)}
              style={{ fontSize: '0.82rem', padding: '6px 12px' }}
            >
              {item.label}
            </button>
          ))}
        </div>

        {synthLoading && <Loading label="Synthesizing inflection points and anomalies…" />}

        {synthData && !synthLoading && (
          <div style={{ background: 'rgba(255,255,255,0.02)', padding: '16px', borderRadius: '10px' }}>
            <h3 style={{ margin: '0 0 8px', fontSize: '1.05rem' }}>{synthData.title}</h3>
            <p style={{ margin: '0 0 12px', fontSize: '0.9rem', lineHeight: '1.45' }}>{synthData.summary}</p>
            {synthData.takeaways && (
              <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '0.85rem', lineHeight: '1.5' }}>
                {synthData.takeaways.map((point, idx) => (
                  <li key={idx} style={{ marginBottom: '4px' }}>{point}</li>
                ))}
              </ul>
            )}
            <div style={{ marginTop: '12px' }}>
              <Link to={`/indicator/${synthKey}`} className="btn btn-ghost" style={{ fontSize: '0.8rem' }}>
                View Interactive Chart &amp; Downloads ›
              </Link>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}