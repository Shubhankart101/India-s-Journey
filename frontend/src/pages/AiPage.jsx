import { lazy, Suspense, useCallback, useEffect, useMemo, useState, useTransition } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { api } from '../api.js';
import { useCompare } from '../compare.jsx';
import { Loading } from '../components/States.jsx';
import { formatMagnitude } from '../format.js';
import { useDebounced, useDocumentTitle } from '../hooks.js';

const ChartView = lazy(() => import('../components/ChartView.jsx'));

const PROMPT_SUGGESTIONS = [
  { label: '⚡ Green Energy Transition (Solar vs Coal)', query: 'solar renewable energy capacity coal' },
  { label: '💳 Digital Public Infrastructure & UPI Velocity', query: 'upi payments digital transactions' },
  { label: '📉 2020 COVID-19 GDP Contraction & Rebound', query: 'real gdp growth contraction pandemic 2020' },
  { label: '⚖️ Judicial Backlog & Court Pendency', query: 'court pendency cases disposal' },
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
    description: 'Growth trajectory vs retail price pressure and supply shocks.',
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
  {
    name: 'Digital UPI Volume vs Headline Inflation',
    keys: ['upi', 'cpi'],
    badge: 'Financial Deepening',
    description: 'DPI adoption speed through retail price fluctuation regimes.',
  },
  {
    name: 'Central Government Debt vs Real GDP Growth',
    keys: ['public_debt_gdp', 'gdp_growth'],
    badge: 'Fiscal Sustainability',
    description: 'Sovereign borrowing trajectory across business cycles and consolidation phases.',
  },
];

export const CORE_INDICATOR_OPTIONS = [
  { key: 'gdp_growth', label: 'Real GDP Growth (%)', category: 'Economy' },
  { key: 'capital_formation_gdp', label: 'Gross Capital Formation (% of GDP)', category: 'Economy' },
  { key: 'cpi', label: 'CPI Headline Inflation (%)', category: 'Prices' },
  { key: 'public_debt_gdp', label: 'Central Government Debt (% of GDP)', category: 'Fiscal' },
  { key: 'trade', label: 'Trade Share of GDP (%)', category: 'Trade' },
  { key: 'exports_gdp', label: 'Merchandise Exports (% of GDP)', category: 'Trade' },
  { key: 'imports_gdp', label: 'Merchandise Imports (% of GDP)', category: 'Trade' },
  { key: 'state_renewable_energy_capacity_all_india_trend', label: 'Renewable Power Capacity (MW)', category: 'Energy' },
  { key: 'coal_production', label: 'Coal Production (MT)', category: 'Energy' },
  { key: 'upi', label: 'Digital Payments - UPI (Cr Volume)', category: 'Finance' },
  { key: 'forex', label: 'Foreign Exchange Reserves ($ Bn)', category: 'External' },
];

const SYNTH_INDICATORS = [
  { key: 'gdp_growth', label: 'Real GDP Growth' },
  { key: 'capital_formation_gdp', label: 'Gross Capital Formation' },
  { key: 'cpi', label: 'CPI Inflation' },
  { key: 'public_debt_gdp', label: 'Central Debt' },
  { key: 'trade', label: 'Trade Share' },
  { key: 'state_renewable_energy_capacity_all_india_trend', label: 'Renewable Power' },
  { key: 'coal_production', label: 'Coal Production' },
  { key: 'upi', label: 'UPI Payments' },
  { key: 'forex', label: 'Forex Reserves' },
];

const ERAS = [
  { id: 'all', label: 'All Horizons', startYear: 0 },
  { id: '1991', label: 'Post-1991 Reforms', startYear: 1991 },
  { id: '2000', label: '2000 – Present', startYear: 2000 },
  { id: '2015', label: 'Last Decade (2015+)', startYear: 2015 },
];

const SCENARIO_PRESETS = [
  { name: 'Capex Stimulus Boom', shock: 5.0, icon: '🚀', desc: '+5% public & private capital push' },
  { name: 'Severe Macro Contraction', shock: -4.0, icon: '📉', desc: '-4% global recession or pandemic drop' },
  { name: 'Commodity Inflation Surge', shock: 3.5, icon: '💸', desc: '+3.5% energy/food supply disruption' },
  { name: 'Clean Energy Push', shock: 8.0, icon: '☀️', desc: '+8% accelerated renewable grid deployment' },
  { name: 'Neutral Trend Drift', shock: 1.0, icon: '⚖️', desc: '+1% steady macroeconomic continuation' },
];

const SEARCH_CATEGORIES = ['All', 'Economy', 'Energy', 'Finance', 'Trade', 'Fiscal'];

const PALETTE = ['#2997ff', '#30d158', '#ffd60a', '#ff9f0a', '#bf5af2', '#64d2ff'];

/**
 * Universal Searchable Indicator Picker for picking any of the 3,082 indicators
 */
function SearchableIndicatorPicker({ label, selectedKey, onSelect, placeholder = 'Search 3,082 indicators…' }) {
  const [open, setOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const debouncedTerm = useDebounced(searchTerm.trim(), 250);

  useEffect(() => {
    if (!debouncedTerm || debouncedTerm.length < 2) {
      setResults([]);
      setSearching(false);
      return;
    }
    const controller = new AbortController();
    setSearching(true);
    api.indicators({ q: debouncedTerm, page_size: 8, live: 'true' }, controller.signal)
      .then(res => {
        setResults(res?.results || []);
        setSearching(false);
      })
      .catch(err => {
        if (err.name !== 'AbortError') {
          setResults([]);
          setSearching(false);
        }
      });
    return () => controller.abort();
  }, [debouncedTerm]);

  const selectedCore = CORE_INDICATOR_OPTIONS.find(o => o.key === selectedKey);

  return (
    <div style={{ position: 'relative', minWidth: '240px', flex: '1 1 240px' }}>
      <label className="muted small" style={{ display: 'block', marginBottom: '4px', fontWeight: 600 }}>
        {label}:
      </label>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '8px 12px',
          background: 'var(--surface-1, rgba(255,255,255,0.03))',
          borderRadius: '8px',
          border: '1px solid var(--line, rgba(255,255,255,0.12))',
          cursor: 'pointer',
        }}
        onClick={() => setOpen(!open)}
        role="button"
        tabIndex={0}
      >
        <span style={{ fontSize: '0.88rem', fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {selectedCore ? `[${selectedCore.category}] ${selectedCore.label}` : selectedKey}
        </span>
        <span style={{ fontSize: '0.75rem', color: 'var(--muted, #86868b)', marginLeft: '8px' }}>
          {open ? '▲ Close' : '▼ Change'}
        </span>
      </div>

      {open && (
        <div
          style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            zIndex: 100,
            marginTop: '6px',
            background: 'var(--surface-overlay, #1c1c1e)',
            borderRadius: '10px',
            border: '1px solid var(--line, rgba(255,255,255,0.15))',
            boxShadow: '0 12px 32px rgba(0,0,0,0.6)',
            padding: '12px',
            maxHeight: '380px',
            overflowY: 'auto',
          }}
        >
          <input
            type="search"
            className="input"
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            placeholder={placeholder}
            autoFocus
            style={{ width: '100%', padding: '8px 12px', fontSize: '0.86rem', borderRadius: '6px', marginBottom: '10px' }}
          />

          {searching && <p className="muted small" style={{ margin: '6px 0' }}>Searching indicators…</p>}

          {results.length > 0 && (
            <div style={{ marginBottom: '12px' }}>
              <span className="muted small" style={{ display: 'block', marginBottom: '6px', fontWeight: 700 }}>
                Matched Indicators:
              </span>
              {results.map(r => (
                <button
                  key={r.key}
                  type="button"
                  onClick={() => {
                    onSelect(r.key);
                    setOpen(false);
                    setSearchTerm('');
                  }}
                  style={{
                    display: 'block',
                    width: '100%',
                    textAlign: 'left',
                    padding: '8px 10px',
                    borderRadius: '6px',
                    border: 'none',
                    background: selectedKey === r.key ? 'rgba(41, 151, 255, 0.2)' : 'transparent',
                    color: 'inherit',
                    cursor: 'pointer',
                    fontSize: '0.84rem',
                    marginBottom: '4px',
                  }}
                >
                  <strong style={{ display: 'block' }}>{r.title}</strong>
                  <span className="muted small" style={{ fontSize: '0.74rem' }}>{r.category} · {r.subgroup}</span>
                </button>
              ))}
            </div>
          )}

          <div>
            <span className="muted small" style={{ display: 'block', marginBottom: '6px', fontWeight: 700 }}>
              Quick Macroeconomic Core:
            </span>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
              {CORE_INDICATOR_OPTIONS.map(opt => (
                <button
                  key={opt.key}
                  type="button"
                  onClick={() => {
                    onSelect(opt.key);
                    setOpen(false);
                  }}
                  style={{
                    textAlign: 'left',
                    padding: '6px 10px',
                    borderRadius: '6px',
                    border: 'none',
                    background: selectedKey === opt.key ? 'rgba(41, 151, 255, 0.2)' : 'transparent',
                    color: 'inherit',
                    cursor: 'pointer',
                    fontSize: '0.82rem',
                  }}
                >
                  <span style={{ color: 'var(--accent, #2997ff)', fontSize: '0.74rem', marginRight: '6px' }}>[{opt.category}]</span>
                  {opt.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function AiPage() {
  useDocumentTitle('AI Intelligence Hub');
  const compare = useCompare();
  const [params, setParams] = useSearchParams();
  const initialQuery = params.get('q') || '';
  const [searchQuery, setSearchQuery] = useState(initialQuery);
  const [searchCategory, setSearchCategory] = useState('All');
  const [searchResults, setSearchResults] = useState(null);
  const [searching, setSearching] = useState(false);
  const [, startTransition] = useTransition();

  // Correlation lab state
  const [selectedPair, setSelectedPair] = useState(PRESET_PAIRS[0].keys);
  const [rebaseNormalised, setRebaseNormalised] = useState(true);
  const [selectedEra, setSelectedEra] = useState('all');
  const [compareData, setCompareData] = useState(null);
  const [pairInsights, setPairInsights] = useState(null);
  const [pairLoading, setPairLoading] = useState(false);
  const [selectedShockYear, setSelectedShockYear] = useState(null);

  // Scenario Simulator state
  const [simShockPct, setSimShockPct] = useState(2.0);
  const [overlayScenarioOnChart, setOverlayScenarioOnChart] = useState(true);

  // Single-indicator synthesis state
  const [synthKey, setSynthKey] = useState('gdp_growth');
  const [synthIndicator, setSynthIndicator] = useState(null);
  const [synthData, setSynthData] = useState(null);
  const [synthLoading, setSynthLoading] = useState(false);

  // Run semantic search when query or category changes
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
      const catParam = searchCategory !== 'All' ? searchCategory : undefined;
      api.aiSearch(q, catParam, controller.signal)
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
  }, [searchQuery, searchCategory]);

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

  // Filter series by selected macroeconomic era
  const eraFilteredCompare = useMemo(() => {
    if (!compareData?.labels || !compareData?.series) return compareData;
    const eraConfig = ERAS.find(e => e.id === selectedEra);
    const startYear = eraConfig?.startYear || 0;
    if (startYear === 0) return compareData;

    const indices = [];
    compareData.labels.forEach((label, idx) => {
      const yrMatch = String(label).match(/\b(19\d\d|20\d\d)\b/);
      const yr = yrMatch ? parseInt(yrMatch[1], 10) : 0;
      if (yr >= startYear) indices.push(idx);
    });

    if (indices.length === 0) return compareData;

    return {
      labels: indices.map(i => compareData.labels[i]),
      series: compareData.series.map(s => ({
        ...s,
        values: indices.map(i => s.values?.[i] ?? null),
      })),
    };
  }, [compareData, selectedEra]);

  // Dynamically compute Pearson r, Concordance, and Lead-Lag for the active era slice
  const eraEconometrics = useMemo(() => {
    if (!eraFilteredCompare?.series || eraFilteredCompare.series.length < 2) return null;
    const labels = eraFilteredCompare.labels || [];
    const sA = eraFilteredCompare.series[0]?.values || [];
    const sB = eraFilteredCompare.series[1]?.values || [];

    const common = [];
    for (let i = 0; i < Math.min(labels.length, sA.length, sB.length); i++) {
      if (typeof sA[i] === 'number' && typeof sB[i] === 'number' && !Number.isNaN(sA[i]) && !Number.isNaN(sB[i])) {
        common.push({ label: labels[i], a: sA[i], b: sB[i] });
      }
    }

    if (common.length < 3) return null;

    const vA = common.map(c => c.a);
    const vB = common.map(c => c.b);
    const n = common.length;
    const mA = vA.reduce((s, v) => s + v, 0) / n;
    const mB = vB.reduce((s, v) => s + v, 0) / n;
    const dA = vA.map(v => v - mA);
    const dB = vB.map(v => v - mB);
    const varA = dA.reduce((s, d) => s + d * d, 0);
    const varB = dB.reduce((s, d) => s + d * d, 0);
    const denom = Math.sqrt(varA * varB);

    if (denom < 1e-9) return null;

    const rawR = dA.reduce((s, d, i) => s + d * dB[i], 0) / denom;
    const r = Math.round(Math.max(-1, Math.min(1, rawR)) * 100) / 100;
    let strength = 'Decoupled / Weak Relationship';
    if (r >= 0.70) strength = 'Strong Positive Co-Movement';
    else if (r >= 0.35) strength = 'Moderate Positive Correlation';
    else if (r <= -0.70) strength = 'Strong Inverse Trade-Off';
    else if (r <= -0.35) strength = 'Moderate Inverse Relationship';

    // Directional Concordance Rate: % of years moving in the same direction
    let concordantSteps = 0;
    let totalSteps = 0;
    for (let k = 0; k < n - 1; k++) {
      const stepA = vA[k + 1] - vA[k];
      const stepB = vB[k + 1] - vB[k];
      if (Math.abs(stepA) > 1e-6 && Math.abs(stepB) > 1e-6) {
        totalSteps += 1;
        if (stepA * stepB > 0) concordantSteps += 1;
      }
    }
    const concordancePct = totalSteps > 0 ? Math.round((concordantSteps / totalSteps) * 100) : null;

    // Lead/Lag correlation: test if Series A leads Series B by 1 year
    let lagR = null;
    if (n >= 5) {
      const vAlag = vA.slice(0, -1);
      const vBlead = vB.slice(1);
      const mAlag = vAlag.reduce((s, v) => s + v, 0) / (n - 1);
      const mBlead = vBlead.reduce((s, v) => s + v, 0) / (n - 1);
      const dAlag = vAlag.map(v => v - mAlag);
      const dBlead = vBlead.map(v => v - mBlead);
      const denomLag = Math.sqrt(dAlag.reduce((s, d) => s + d * d, 0) * dBlead.reduce((s, d) => s + d * d, 0));
      if (denomLag > 1e-9) {
        lagR = Math.round(dAlag.reduce((s, d, i) => s + d * dBlead[i], 0) / denomLag * 100) / 100;
      }
    }

    return {
      r,
      sampleSize: n,
      strength,
      concordancePct,
      concordantSteps,
      totalSteps,
      lagR,
      start: common[0].label,
      end: common[n - 1].label,
    };
  }, [eraFilteredCompare]);

  // Primary correlation reference
  const primaryCorrelation = eraEconometrics || pairInsights?.correlations?.[0];
  const rVal = primaryCorrelation?.r ?? null;
  const rColor = rVal === null ? 'var(--muted, #86868b)' : (rVal >= 0.5 ? '#30d158' : (rVal <= -0.5 ? '#ff453a' : '#ffd60a'));
  const rPercentPos = rVal !== null ? Math.round(((rVal + 1) / 2) * 100) : 50;

  // Simulator elasticity & value projection estimation with confidence bounds
  const simStats = useMemo(() => {
    if (rVal === null || !compareData?.series || compareData.series.length < 2) return null;
    const sA = compareData.series[0];
    const sB = compareData.series[1];
    const vA = (sA.values || []).filter(v => typeof v === 'number');
    const vB = (sB.values || []).filter(v => typeof v === 'number');
    if (vA.length < 3 || vB.length < 3) return null;

    const meanA = vA.reduce((s, v) => s + v, 0) / vA.length;
    const meanB = vB.reduce((s, v) => s + v, 0) / vB.length;
    const stdA = Math.sqrt(vA.reduce((s, v) => s + (v - meanA) ** 2, 0) / vA.length);
    const stdB = Math.sqrt(vB.reduce((s, v) => s + (v - meanB) ** 2, 0) / vB.length);
    const beta = stdA > 1e-6 ? rVal * (stdB / stdA) : rVal;

    const deltaPctB = Math.round(simShockPct * beta * 100) / 100;
    const latestA = vA[vA.length - 1];
    const latestB = vB[vB.length - 1];

    const projectedA = Math.round((latestA * (1 + simShockPct / 100)) * 100) / 100;
    const projectedB = Math.round((latestB * (1 + deltaPctB / 100)) * 100) / 100;

    // Standard error and 95% confidence interval
    const se = stdB * Math.sqrt(Math.max(0, 1 - rVal * rVal));
    const ciDeltaPct = meanB > 1e-6 ? Math.round((1.96 * se / meanB * 100) * 10) / 10 : 1.5;

    return {
      beta: Math.round(beta * 100) / 100,
      deltaPctB,
      stdA: Math.round(stdA * 100) / 100,
      stdB: Math.round(stdB * 100) / 100,
      latestA,
      latestB,
      projectedA,
      projectedB,
      ciLowerPct: Math.round((deltaPctB - ciDeltaPct) * 10) / 10,
      ciUpperPct: Math.round((deltaPctB + ciDeltaPct) * 10) / 10,
      unitA: sA.suffix || '',
      unitB: sB.suffix || '',
    };
  }, [rVal, compareData, simShockPct]);

  // Chart datasets for correlation lab with optional simulated trajectory overlay
  const { chartLabels, chartDatasets } = useMemo(() => {
    const dataToUse = eraFilteredCompare || compareData;
    if (!dataToUse?.series || dataToUse.series.length === 0) return { chartLabels: [], chartDatasets: [] };

    let labels = [...(dataToUse.labels || [])];
    const seriesList = dataToUse.series;

    if (overlayScenarioOnChart && simStats && labels.length > 0) {
      // Append forecast projection year
      const lastLabel = labels[labels.length - 1];
      const lastYearMatch = String(lastLabel).match(/\b(19\d\d|20\d\d)\b/);
      const nextYear = lastYearMatch ? parseInt(lastYearMatch[1], 10) + 1 : 'Forecast';
      const forecastLabel = `${nextYear} (Simulated)`;
      labels = [...labels, forecastLabel];

      const datasets = seriesList.map((item, index) => {
        let values = [...(item.values || [])];
        const isLead = index === 0;
        const projVal = isLead ? simStats.projectedA : simStats.projectedB;

        if (rebaseNormalised) {
          const base = values.find(value => typeof value === 'number' && value !== 0);
          if (base) {
            values = values.map(v => (typeof v === 'number' ? Math.round(((v / base) * 100) * 10) / 10 : null));
            const rebasedProj = Math.round(((projVal / base) * 100) * 10) / 10;
            values.push(rebasedProj);
          } else {
            values.push(projVal);
          }
        } else {
          values.push(projVal);
        }

        const color = item.color || PALETTE[index % PALETTE.length];
        return {
          label: `${item.title}`,
          color,
          values,
          data: values,
          borderColor: color,
          backgroundColor: color,
          tension: 0.25,
          pointRadius: 2,
        };
      });

      return { chartLabels: labels, chartDatasets: datasets };
    }

    const datasets = seriesList.map((item, index) => {
      let values = item.values || [];
      if (rebaseNormalised) {
        const base = values.find(value => typeof value === 'number' && value !== 0);
        values = base ? values.map(value => (typeof value === 'number' ? Math.round(((value / base) * 100) * 10) / 10 : null)) : values;
      }
      const color = item.color || PALETTE[index % PALETTE.length];
      return {
        label: item.title,
        color,
        values,
        data: values,
        borderColor: color,
        backgroundColor: color,
        tension: 0.25,
        pointRadius: 2,
      };
    });

    return { chartLabels: labels, chartDatasets: datasets };
  }, [eraFilteredCompare, compareData, rebaseNormalised, overlayScenarioOnChart, simStats]);

  // Single-series chart dataset & labels for Synthesizer
  const singleChartDataset = useMemo(() => {
    const rawDatasets = synthIndicator?.datasets || synthIndicator?.series?.datasets;
    if (!rawDatasets?.[0]?.values) return [];
    const ds = rawDatasets[0];
    const color = synthIndicator?.color || '#2997ff';
    return [
      {
        label: synthIndicator?.title || 'Indicator',
        color,
        values: ds.values,
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

  // Synthesizer statistical anomalies & regime calculation
  const synthAnomalies = useMemo(() => {
    const rawDatasets = synthIndicator?.datasets || synthIndicator?.series?.datasets;
    const labels = synthIndicator?.labels || synthIndicator?.series?.labels || [];
    const values = rawDatasets?.[0]?.values || [];
    if (!labels.length || !values.length) return null;

    const points = [];
    for (let i = 0; i < Math.min(labels.length, values.length); i++) {
      if (typeof values[i] === 'number' && !Number.isNaN(values[i])) {
        points.push({ label: String(labels[i]), val: values[i] });
      }
    }
    if (points.length < 4) return null;

    // Year-over-year deltas and percentage changes
    let maxSurge = null;
    let maxDrop = null;
    const yoySteps = [];

    for (let k = 0; k < points.length - 1; k++) {
      const prev = points[k];
      const curr = points[k + 1];
      const delta = curr.val - prev.val;
      const pct = prev.val !== 0 ? (delta / Math.abs(prev.val)) * 100 : null;
      yoySteps.push({ year: curr.label, delta, pct });

      if (pct !== null) {
        if (!maxSurge || pct > maxSurge.pct) maxSurge = { year: curr.label, pct, delta, fromVal: prev.val, toVal: curr.val };
        if (!maxDrop || pct < maxDrop.pct) maxDrop = { year: curr.label, pct, delta, fromVal: prev.val, toVal: curr.val };
      }
    }

    // Regimes calculation (Pre-1991, 1991-2014, 2014+)
    const regimePre91 = points.filter(p => {
      const y = parseInt(p.label.match(/\b(19\d\d|20\d\d)\b/)?.[1] || '0', 10);
      return y > 0 && y < 1991;
    });
    const regime91_14 = points.filter(p => {
      const y = parseInt(p.label.match(/\b(19\d\d|20\d\d)\b/)?.[1] || '0', 10);
      return y >= 1991 && y < 2014;
    });
    const regimePost14 = points.filter(p => {
      const y = parseInt(p.label.match(/\b(19\d\d|20\d\d)\b/)?.[1] || '0', 10);
      return y >= 2014;
    });

    const getRegimeStats = pts => {
      if (!pts.length) return null;
      const vals = pts.map(p => p.val);
      const avg = vals.reduce((s, v) => s + v, 0) / vals.length;
      return {
        avg: Math.round(avg * 100) / 100,
        min: Math.round(Math.min(...vals) * 100) / 100,
        max: Math.round(Math.max(...vals) * 100) / 100,
        count: pts.length,
      };
    };

    return {
      maxSurge,
      maxDrop,
      regimes: {
        pre91: getRegimeStats(regimePre91),
        post91: getRegimeStats(regime91_14),
        post14: getRegimeStats(regimePost14),
      },
    };
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

  const loadSynthIndicator = key => {
    setSynthKey(key);
    const el = document.getElementById('ai-synthesizer');
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  const swapPair = () => {
    if (selectedPair && selectedPair.length >= 2) {
      setSelectedPair([selectedPair[1], selectedPair[0]]);
    }
  };

  // Dynamic natural language query answer synthesizer
  const queryAnswer = useMemo(() => {
    if (!searchQuery.trim() || !searchResults || searchResults.length === 0) return null;
    const qLower = searchQuery.toLowerCase();

    if (qLower.includes('covid') || qLower.includes('2020') || qLower.includes('contraction')) {
      return {
        headline: 'COVID-19 Economic Shock Synthesis (2020–2021)',
        summary: 'The 2020 pandemic triggered a historic -5.8% contraction in Indian Real GDP alongside widespread supply disruptions. However, Digital Public Infrastructure (UPI transactions) and agriculture showed counter-cyclical growth, with digital volume expanding by over +84% during the period.',
        highlightKey: 'gdp_growth',
      };
    }
    if (qLower.includes('solar') || qLower.includes('renewable') || qLower.includes('coal') || qLower.includes('energy')) {
      return {
        headline: 'Energy Transition & Thermal Baseload Synthesis',
        summary: 'India has installed over 180 GW of non-fossil capacity with solar leading the expansion, while coal generation continues to support baseload grid inertia during peak evening industrial demand hours.',
        highlightKey: 'state_renewable_energy_capacity_all_india_trend',
      };
    }
    if (qLower.includes('upi') || qLower.includes('digital') || qLower.includes('payment')) {
      return {
        headline: 'Digital Public Infrastructure (DPI) & Velocity Synthesis',
        summary: 'UPI volume expanded from under 10 crore monthly transactions in 2017 to over 1,400+ crore transactions monthly in 2024, driving widespread formalization and reducing currency transaction friction nationwide.',
        highlightKey: 'upi',
      };
    }
    if (qLower.includes('court') || qLower.includes('pendency') || qLower.includes('backlog')) {
      return {
        headline: 'Judicial Capacity & Case Clearance Synthesis',
        summary: 'Official National Judicial Data Grid records reflect substantial pending case backlogs across Subordinate and High Courts, with quarterly disposal rates demonstrating cyclical pauses during scheduled judicial vacations.',
        highlightKey: 'jud_supreme_court_pending_case_mix',
      };
    }
    if (qLower.includes('inflation') || qLower.includes('cpi') || qLower.includes('repo')) {
      return {
        headline: 'Monetary Transmission & Retail Inflation Synthesis',
        summary: 'Consumer price inflation in India is driven predominantly by food and fuel supply volatility. The Reserve Bank of India utilizes repo rate corridor adjustments to anchor medium-term inflation within the 4% (±2%) statutory band.',
        highlightKey: 'cpi',
      };
    }

    // Default dynamic synthesis across top results
    const topResults = searchResults.slice(0, 3);
    const categories = [...new Set(topResults.map(r => r.category))].join(' and ');
    return {
      headline: `Semantic Synthesis for "${searchQuery}"`,
      summary: `Found ${searchResults.length} verified public series covering ${categories}. Top indicators include ${topResults.map(r => r.title).join(', ')}. These datasets provide multi-decade official telemetry without interpolated models.`,
      highlightKey: topResults[0]?.key,
    };
  }, [searchQuery, searchResults]);

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
        <p className="lead" style={{ maxWidth: '780px', margin: '0 auto 16px', fontSize: '1.08rem', color: 'var(--muted, #86868b)', lineHeight: '1.5' }}>
          Real-time macroeconomic co-movement, structural shock detection, elasticity stress simulation, and natural language inquiry across 3,082 verified public indicators.
        </p>
      </header>

      {/* Module 1: AI Dual-Series Correlation & Decoupling Laboratory */}
      <section id="ai-correlation-lab" className="card" style={{ padding: '28px 24px', marginBottom: '36px', borderLeft: '4px solid var(--accent, #2997ff)', borderRadius: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '1.5rem', color: 'var(--accent, #2997ff)' }}>⇄</span>
          <h2 style={{ margin: 0, fontSize: '1.45rem', fontWeight: 700 }}>AI Correlation &amp; Decoupling Laboratory</h2>
          <span className="badge" style={{ marginLeft: 'auto', background: 'rgba(41, 151, 255, 0.15)', color: 'var(--accent, #2997ff)', fontSize: '0.76rem', padding: '4px 10px' }}>
            Phase 2B Statistical Engine
          </span>
        </div>
        <p className="muted" style={{ margin: '0 0 20px', fontSize: '0.94rem', lineHeight: '1.45' }}>
          Select an analytical preset or search any two indicators across 3,082 series to compute live Pearson co-movement ($r$), directional concordance, and isolate structural decoupling shocks.
        </p>

        {/* Universal Searchable Indicator Selectors */}
        <div style={{ background: 'var(--surface-1, rgba(255,255,255,0.03))', padding: '16px 18px', borderRadius: '12px', border: '1px solid var(--line, rgba(255,255,255,0.08))', marginBottom: '20px' }}>
          <span className="muted small" style={{ display: 'block', marginBottom: '10px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            🔬 Active Pair Workbench:
          </span>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', flexWrap: 'wrap' }}>
            <SearchableIndicatorPicker
              label="Series A (Lead)"
              selectedKey={selectedPair[0]}
              onSelect={k => setSelectedPair([k, selectedPair[1]])}
            />

            <button
              type="button"
              className="btn btn-ghost"
              onClick={swapPair}
              title="Swap Series A and Series B"
              style={{ marginTop: '24px', padding: '8px 14px', borderRadius: '8px', fontSize: '0.86rem' }}
            >
              ⇄ Swap
            </button>

            <SearchableIndicatorPicker
              label="Series B (Paired)"
              selectedKey={selectedPair[1]}
              onSelect={k => setSelectedPair([selectedPair[0], k])}
            />
          </div>
        </div>

        {/* Macroeconomic Presets Grid */}
        <div style={{ marginBottom: '22px' }}>
          <span className="muted small" style={{ display: 'block', marginBottom: '10px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Quick Analytical Presets:
          </span>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '12px' }}>
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
              </div>

              {/* Controls: Rebase, Horizon Filter & Simulation Overlay */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flexWrap: 'wrap' }}>
                {/* Era Filter */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <span className="muted small" style={{ marginRight: '4px' }}>Horizon:</span>
                  {ERAS.map(era => (
                    <button
                      key={era.id}
                      type="button"
                      className={`btn ${selectedEra === era.id ? 'btn-primary' : 'btn-ghost'}`}
                      onClick={() => setSelectedEra(era.id)}
                      style={{ fontSize: '0.76rem', padding: '3px 8px', borderRadius: '6px' }}
                    >
                      {era.label}
                    </button>
                  ))}
                </div>

                {/* Rebase Toggle */}
                <label className="switch" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.86rem' }}>
                  <input
                    type="checkbox"
                    checked={rebaseNormalised}
                    onChange={e => setRebaseNormalised(e.target.checked)}
                  />
                  <span><strong>Rebase to 100</strong></span>
                </label>

                {/* Simulation Overlay Toggle */}
                <label className="switch" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.86rem' }}>
                  <input
                    type="checkbox"
                    checked={overlayScenarioOnChart}
                    onChange={e => setOverlayScenarioOnChart(e.target.checked)}
                  />
                  <span><strong>Overlay Shock Forecast</strong></span>
                </label>
              </div>
            </div>

            {/* Visual Interactive Chart */}
            <div className="detail-chart" style={{ minHeight: '340px', marginBottom: '20px' }}>
              <Suspense fallback={<div className="chart-skeleton" style={{ height: '320px' }} />}>
                <ChartView
                  title={`${compareData.series[0]?.title} vs ${compareData.series[1]?.title}`}
                  labels={chartLabels}
                  datasets={chartDatasets}
                  type="line"
                  suffix={rebaseNormalised ? '' : (compareData.series[0]?.suffix === compareData.series[1]?.suffix ? compareData.series[0]?.suffix : '')}
                />
              </Suspense>
            </div>

            {/* Visual Pearson Correlation & Econometric Gauge */}
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
                        Sample size: <strong>{primaryCorrelation.sampleSize || primaryCorrelation.sample_size} shared periods</strong> ({primaryCorrelation.start || primaryCorrelation.start_year || '–'} to {primaryCorrelation.end || primaryCorrelation.end_year || '–'})
                      </div>
                    </div>
                  </div>

                  {/* Concordance Metric */}
                  {primaryCorrelation.concordancePct !== undefined && primaryCorrelation.concordancePct !== null && (
                    <div style={{ textAlign: 'right' }}>
                      <span className="badge" style={{ fontSize: '0.76rem', background: 'rgba(48,209,88,0.15)', color: '#30d158', padding: '4px 10px' }}>
                        {primaryCorrelation.concordancePct}% Directional Concordance
                      </span>
                      <span className="muted small" style={{ display: 'block', marginTop: '3px' }}>
                        {primaryCorrelation.concordantSteps} of {primaryCorrelation.totalSteps} intervals co-moved
                      </span>
                    </div>
                  )}
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

                {/* Lead/Lag Econometric Signal */}
                {primaryCorrelation.lagR !== undefined && primaryCorrelation.lagR !== null && Math.abs(primaryCorrelation.lagR - rVal) >= 0.10 && (
                  <div style={{ marginTop: '12px', padding: '8px 12px', background: 'rgba(41, 151, 255, 0.08)', borderRadius: '6px', fontSize: '0.8rem', color: 'var(--accent, #2997ff)' }}>
                    ⚡ <strong>Econometric Signal:</strong> Series A leads Series B with 1-year lag correlation of <strong>r = {primaryCorrelation.lagR >= 0 ? '+' : ''}{primaryCorrelation.lagR.toFixed(2)}</strong> (vs concurrent r = {rVal >= 0 ? '+' : ''}{rVal.toFixed(2)}).
                  </div>
                )}
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
          Simulate a hypothetical shock on the leading series to observe the estimated statistical elasticity co-movement on the paired series based on historical covariance.
        </p>

        <div style={{ background: 'var(--surface-1, rgba(255,255,255,0.02))', padding: '18px', borderRadius: '10px', border: '1px solid var(--line, rgba(255,255,255,0.06))' }}>
          {/* Shock Input Slider */}
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
            min="-10.0"
            max="10.0"
            step="0.5"
            value={simShockPct}
            onChange={e => setSimShockPct(parseFloat(e.target.value))}
            style={{ width: '100%', cursor: 'pointer', margin: '8px 0 14px' }}
          />

          {/* Quick Scenario Preset Buttons */}
          <div style={{ marginBottom: '16px' }}>
            <span className="muted small" style={{ display: 'block', marginBottom: '8px', fontWeight: 600 }}>
              Curated Policy Stress Scenarios:
            </span>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              {SCENARIO_PRESETS.map(scen => (
                <button
                  key={scen.name}
                  type="button"
                  className={`btn ${simShockPct === scen.shock ? 'btn-primary' : 'btn-ghost'}`}
                  onClick={() => setSimShockPct(scen.shock)}
                  style={{ fontSize: '0.78rem', padding: '6px 10px', borderRadius: '8px' }}
                  title={scen.desc}
                >
                  <span style={{ marginRight: '4px' }}>{scen.icon}</span>
                  {scen.name} ({scen.shock >= 0 ? `+${scen.shock}%` : `${scen.shock}%`})
                </button>
              ))}
            </div>
          </div>

          {/* Detailed Dual-Series Projection Cards */}
          {simStats && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '14px', marginBottom: '16px' }}>
              {/* Leading Series Card */}
              <div style={{ background: 'rgba(41, 151, 255, 0.05)', padding: '14px 16px', borderRadius: '8px', border: '1px solid rgba(41, 151, 255, 0.2)' }}>
                <span className="muted small" style={{ display: 'block', color: 'var(--accent, #2997ff)', fontWeight: 600 }}>
                  Series A: {compareData?.series?.[0]?.title}
                </span>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginTop: '6px' }}>
                  <div>
                    <span className="muted small" style={{ display: 'block' }}>Baseline:</span>
                    <strong style={{ fontSize: '1.1rem' }}>{simStats.latestA} {simStats.unitA}</strong>
                  </div>
                  <span style={{ fontSize: '1.2rem', color: 'var(--muted, #86868b)' }}>→</span>
                  <div>
                    <span className="muted small" style={{ display: 'block' }}>Projected:</span>
                    <strong style={{ fontSize: '1.1rem', color: simShockPct >= 0 ? '#30d158' : '#ff453a' }}>
                      {simStats.projectedA} {simStats.unitA}
                    </strong>
                  </div>
                </div>
              </div>

              {/* Paired Series Card */}
              <div style={{ background: 'rgba(48, 209, 88, 0.05)', padding: '14px 16px', borderRadius: '8px', border: '1px solid rgba(48, 209, 88, 0.2)' }}>
                <span className="muted small" style={{ display: 'block', color: '#30d158', fontWeight: 600 }}>
                  Series B: {compareData?.series?.[1]?.title}
                </span>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginTop: '6px' }}>
                  <div>
                    <span className="muted small" style={{ display: 'block' }}>Baseline:</span>
                    <strong style={{ fontSize: '1.1rem' }}>{simStats.latestB} {simStats.unitB}</strong>
                  </div>
                  <span style={{ fontSize: '1.2rem', color: 'var(--muted, #86868b)' }}>→</span>
                  <div>
                    <span className="muted small" style={{ display: 'block' }}>Projected:</span>
                    <strong style={{ fontSize: '1.1rem', color: simStats.deltaPctB >= 0 ? 'var(--accent, #2997ff)' : '#ff9f0a' }}>
                      {simStats.projectedB} {simStats.unitB}
                    </strong>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Statistical Breakdown Bar */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px', paddingTop: '10px', borderTop: '1px solid var(--line, rgba(255,255,255,0.06))' }}>
            <div>
              <span className="muted small" style={{ display: 'block' }}>Estimated Elastic Response:</span>
              <span style={{ fontSize: '1.15rem', fontWeight: 800, color: simStats?.deltaPctB !== undefined && simStats.deltaPctB >= 0 ? 'var(--accent, #2997ff)' : '#ff9f0a' }}>
                {simStats ? `${simStats.deltaPctB >= 0 ? '+' : ''}${simStats.deltaPctB.toFixed(2)}% expected co-movement (β = ${simStats.beta})` : 'Calculating…'}
              </span>
              {simStats && (
                <span className="muted small" style={{ display: 'block', marginTop: '2px' }}>
                  95% Confidence Band: [{simStats.ciLowerPct >= 0 ? '+' : ''}{simStats.ciLowerPct}%, {simStats.ciUpperPct >= 0 ? '+' : ''}{simStats.ciUpperPct}%]
                </span>
              )}
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
      <section id="ai-synthesizer" className="card" style={{ padding: '28px 24px', marginBottom: '36px', border: '1px solid var(--line, rgba(255,255,255,0.08))', borderRadius: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '1.4rem' }}>📈</span>
          <h2 style={{ margin: 0, fontSize: '1.35rem', fontWeight: 700 }}>Macroeconomic Inflection &amp; Anomaly Synthesizer</h2>
          <span className="badge" style={{ marginLeft: 'auto', fontSize: '0.76rem', padding: '4px 10px' }}>Automated Series Context</span>
        </div>
        <p className="muted small" style={{ margin: '0 0 16px', lineHeight: '1.45' }}>
          Select or search any indicator to synthesize all-time extremes, structural regimes, volatility, and historical policy lineage.
        </p>

        {/* Search & Pick any indicator for Synthesizer */}
        <div style={{ marginBottom: '16px', maxWidth: '420px' }}>
          <SearchableIndicatorPicker
            label="Synthesize Custom Indicator"
            selectedKey={synthKey}
            onSelect={k => setSynthKey(k)}
            placeholder="Type any indicator name, e.g. fertilizer, forest, mortality…"
          />
        </div>

        {/* Quick Foundational Indicator Switcher Pills */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '20px' }}>
          {SYNTH_INDICATORS.map(item => (
            <button
              key={item.key}
              type="button"
              className={`btn ${synthKey === item.key ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setSynthKey(item.key)}
              style={{ fontSize: '0.84rem', padding: '6px 12px', borderRadius: '8px' }}
            >
              {item.label}
            </button>
          ))}
        </div>

        {synthLoading && <Loading label="Synthesizing inflection points, anomalies and regime averages…" />}

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

            {/* 6 KPI Metric Cards */}
            {synthData.metrics && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '10px', marginBottom: '20px' }}>
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
                      Over Full Horizon
                    </span>
                  </div>
                )}

                {synthData.metrics.cagr !== undefined && synthData.metrics.cagr !== null && (
                  <div style={{ background: 'var(--surface-1, rgba(255,255,255,0.03))', padding: '12px 14px', borderRadius: '8px', border: '1px solid var(--line, rgba(255,255,255,0.06))' }}>
                    <span className="muted small" style={{ fontSize: '0.74rem', display: 'block' }}>📊 Annualized CAGR</span>
                    <span style={{ fontSize: '1.25rem', fontWeight: 800, color: synthData.metrics.cagr >= 0 ? '#30d158' : '#ff453a' }}>
                      {synthData.metrics.cagr >= 0 ? `+${synthData.metrics.cagr}%` : `${synthData.metrics.cagr}%`}
                    </span>
                    <span className="muted small" style={{ fontSize: '0.74rem', display: 'block', marginTop: '2px' }}>
                      Compound Annual Rate
                    </span>
                  </div>
                )}

                {synthData.metrics.volatility !== undefined && synthData.metrics.volatility !== null && (
                  <div style={{ background: 'var(--surface-1, rgba(255,255,255,0.03))', padding: '12px 14px', borderRadius: '8px', border: '1px solid var(--line, rgba(255,255,255,0.06))' }}>
                    <span className="muted small" style={{ fontSize: '0.74rem', display: 'block' }}>⚡ Series Volatility (σ)</span>
                    <span style={{ fontSize: '1.25rem', fontWeight: 800, color: '#ffd60a' }}>
                      {synthData.metrics.volatility} {synthData.metrics.unit}
                    </span>
                    <span className="muted small" style={{ fontSize: '0.74rem', display: 'block', marginTop: '2px' }}>
                      Standard Deviation
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

            {/* Statistical Outliers & Annual Surge / Contraction Radar */}
            {synthAnomalies && (synthAnomalies.maxSurge || synthAnomalies.maxDrop) && (
              <div style={{ marginBottom: '18px', background: 'var(--surface-1, rgba(255,255,255,0.02))', padding: '14px 16px', borderRadius: '10px', border: '1px solid var(--line, rgba(255,255,255,0.06))' }}>
                <span style={{ fontWeight: 700, fontSize: '0.88rem', display: 'block', marginBottom: '8px' }}>
                  ⚡ Historical Volatility Extremes:
                </span>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '10px' }}>
                  {synthAnomalies.maxSurge && (
                    <div style={{ padding: '8px 12px', background: 'rgba(48, 209, 88, 0.08)', borderRadius: '6px', borderLeft: '3px solid #30d158' }}>
                      <span className="muted small" style={{ display: 'block' }}>🚀 Steepest Annual Acceleration</span>
                      <strong>{synthAnomalies.maxSurge.year}: +{synthAnomalies.maxSurge.pct.toFixed(1)}% YoY</strong>
                      <span className="muted small" style={{ display: 'block' }}>Shift from {synthAnomalies.maxSurge.fromVal} to {synthAnomalies.maxSurge.toVal}</span>
                    </div>
                  )}
                  {synthAnomalies.maxDrop && (
                    <div style={{ padding: '8px 12px', background: 'rgba(255, 69, 58, 0.08)', borderRadius: '6px', borderLeft: '3px solid #ff453a' }}>
                      <span className="muted small" style={{ display: 'block' }}>🔻 Sharpest Annual Contraction</span>
                      <strong>{synthAnomalies.maxDrop.year}: {synthAnomalies.maxDrop.pct.toFixed(1)}% YoY</strong>
                      <span className="muted small" style={{ display: 'block' }}>Shift from {synthAnomalies.maxDrop.fromVal} to {synthAnomalies.maxDrop.toVal}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Historical Policy Regimes Breakdown */}
            {synthAnomalies?.regimes && (synthAnomalies.regimes.pre91 || synthAnomalies.regimes.post91 || synthAnomalies.regimes.post14) && (
              <div style={{ marginBottom: '18px' }}>
                <span style={{ fontWeight: 700, fontSize: '0.88rem', display: 'block', marginBottom: '8px' }}>
                  🏛️ Structural Regime Evolution:
                </span>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '8px' }}>
                  {synthAnomalies.regimes.pre91 && (
                    <div style={{ padding: '10px 12px', background: 'rgba(255,255,255,0.03)', borderRadius: '6px', border: '1px solid var(--line, rgba(255,255,255,0.06))' }}>
                      <span className="muted small" style={{ display: 'block' }}>Pre-1991 Planned Economy</span>
                      <strong style={{ fontSize: '1.05rem' }}>Avg: {synthAnomalies.regimes.pre91.avg} {synthIndicator.suffix}</strong>
                      <span className="muted small" style={{ display: 'block' }}>Range: {synthAnomalies.regimes.pre91.min} – {synthAnomalies.regimes.pre91.max}</span>
                    </div>
                  )}
                  {synthAnomalies.regimes.post91 && (
                    <div style={{ padding: '10px 12px', background: 'rgba(255,255,255,0.03)', borderRadius: '6px', border: '1px solid var(--line, rgba(255,255,255,0.06))' }}>
                      <span className="muted small" style={{ display: 'block' }}>1991–2014 Post-Reforms</span>
                      <strong style={{ fontSize: '1.05rem', color: 'var(--accent, #2997ff)' }}>Avg: {synthAnomalies.regimes.post91.avg} {synthIndicator.suffix}</strong>
                      <span className="muted small" style={{ display: 'block' }}>Range: {synthAnomalies.regimes.post91.min} – {synthAnomalies.regimes.post91.max}</span>
                    </div>
                  )}
                  {synthAnomalies.regimes.post14 && (
                    <div style={{ padding: '10px 12px', background: 'rgba(255,255,255,0.03)', borderRadius: '6px', border: '1px solid var(--line, rgba(255,255,255,0.06))' }}>
                      <span className="muted small" style={{ display: 'block' }}>2014–2025 Capex &amp; DPI</span>
                      <strong style={{ fontSize: '1.05rem', color: '#30d158' }}>Avg: {synthAnomalies.regimes.post14.avg} {synthIndicator.suffix}</strong>
                      <span className="muted small" style={{ display: 'block' }}>Range: {synthAnomalies.regimes.post14.min} – {synthAnomalies.regimes.post14.max}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Historical Milestone Inflections Timeline */}
            {synthData.inflections?.length > 0 && (
              <div style={{ marginBottom: '20px', borderTop: '1px solid var(--line, rgba(255,255,255,0.08))', paddingTop: '16px' }}>
                <span style={{ fontWeight: 700, fontSize: '0.92rem', display: 'block', marginBottom: '10px' }}>
                  🏛️ Key Historical Milestone Inflections:
                </span>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '10px' }}>
                  {synthData.inflections.map((inf, i) => (
                    <div
                      key={i}
                      style={{
                        padding: '10px 14px',
                        background: 'var(--surface-1, rgba(255,255,255,0.03))',
                        borderRadius: '8px',
                        border: '1px solid var(--line, rgba(255,255,255,0.06))',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                        <strong style={{ color: 'var(--accent, #2997ff)', fontSize: '0.9rem' }}>{inf.year}</strong>
                        <span className="badge" style={{ fontSize: '0.72rem' }}>
                          {formatMagnitude(inf.value, inf.unit)}
                        </span>
                      </div>
                      <span className="muted small" style={{ fontSize: '0.78rem', lineHeight: '1.35', display: 'block' }}>
                        {inf.event}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

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

            <div style={{ marginTop: '18px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => {
                  loadPairInLab(synthKey, selectedPair[0] === synthKey ? selectedPair[1] : selectedPair[0]);
                }}
                style={{ fontSize: '0.84rem' }}
              >
                Load into Correlation Lab ⇄
              </button>
              <Link to={`/indicator/${synthKey}`} className="btn btn-ghost" style={{ fontSize: '0.84rem' }}>
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
          <span className="badge" style={{ marginLeft: 'auto', fontSize: '0.76rem', padding: '4px 10px' }}>Semantic Vector Search &amp; Copilot</span>
        </div>
        <p className="muted small" style={{ margin: '0 0 16px', lineHeight: '1.45' }}>
          Type any macroeconomic, political, or development question in natural language to query and synthesize across 3,082 verified public indicators.
        </p>

        {/* Search Bar with Clear Button */}
        <div style={{ position: 'relative', marginBottom: '12px' }}>
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
          {searchQuery && (
            <button
              type="button"
              onClick={() => {
                setSearchQuery('');
                startTransition(() => setParams({}));
              }}
              style={{
                position: 'absolute',
                right: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                background: 'transparent',
                border: 'none',
                color: 'var(--muted, #86868b)',
                cursor: 'pointer',
                fontSize: '1.1rem',
              }}
              aria-label="Clear search"
            >
              ✕
            </button>
          )}
        </div>

        {/* Category Filter Chips */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '14px', flexWrap: 'wrap' }}>
          <span className="muted small" style={{ marginRight: '4px' }}>Domain:</span>
          {SEARCH_CATEGORIES.map(cat => (
            <button
              key={cat}
              type="button"
              className={`btn ${searchCategory === cat ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setSearchCategory(cat)}
              style={{ fontSize: '0.76rem', padding: '3px 10px', borderRadius: '12px' }}
            >
              {cat}
            </button>
          ))}
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

        {/* AI Executive Synthesis Answer Box */}
        {queryAnswer && !searching && (
          <div style={{ marginTop: '20px', padding: '18px 20px', background: 'linear-gradient(135deg, rgba(41, 151, 255, 0.08), rgba(48, 209, 88, 0.04))', borderRadius: '12px', border: '1px solid rgba(41, 151, 255, 0.25)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <span style={{ fontSize: '1.1rem' }}>🤖</span>
              <strong style={{ fontSize: '1rem', color: 'var(--accent, #2997ff)' }}>
                {queryAnswer.headline}
              </strong>
            </div>
            <p style={{ margin: '0 0 12px', fontSize: '0.92rem', lineHeight: '1.5' }}>
              {queryAnswer.summary}
            </p>
            {searchResults && searchResults.length >= 2 && (
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => loadPairInLab(searchResults[0].key, searchResults[1].key)}
                style={{ fontSize: '0.82rem', padding: '6px 14px' }}
              >
                ⇄ Compare Top 2 Matches in Correlation Lab ({searchResults[0].title} vs {searchResults[1].title})
              </button>
            )}
          </div>
        )}

        {searchResults && !searching && (
          <div style={{ marginTop: '24px', borderTop: '1px solid var(--line, rgba(255,255,255,0.08))', paddingTop: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <span style={{ fontWeight: 700, fontSize: '0.94rem' }}>
                AI Semantic Matches ({searchResults.length})
              </span>
              <span className="muted small">Ranked by Vector Relevance</span>
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
                        <span className="badge" style={{ fontSize: '0.72rem', background: result.similarity >= 0.7 ? 'rgba(48,209,88,0.15)' : 'rgba(255,255,255,0.08)', color: result.similarity >= 0.7 ? '#30d158' : 'inherit' }}>
                          {Math.round(result.similarity * 100)}% match
                        </span>
                      </div>
                      <span className="muted small">
                        {result.category} · {result.subgroup}
                      </span>
                    </div>

                    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                      <button
                        type="button"
                        className="btn btn-ghost"
                        onClick={() => loadSynthIndicator(result.key)}
                        style={{ fontSize: '0.8rem', padding: '6px 10px' }}
                        title="Analyze historical inflections & anomalies"
                      >
                        📈 Synthesize
                      </button>
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
                      <Link to={`/indicator/${result.key}`} className="btn btn-ghost" style={{ fontSize: '0.8rem', padding: '6px 10px' }}>
                        Deep Dive ›
                      </Link>
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
