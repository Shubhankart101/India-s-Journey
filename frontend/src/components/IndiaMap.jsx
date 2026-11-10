import { useEffect, useMemo, useRef, useState } from 'react';
import { formatMagnitude } from '../format.js';
import ScriptureVerse from './ScriptureVerse.jsx';
import './IndiaMap.css';

export const MAP_URL = import.meta.env.BASE_URL + 'maps/india-states.json';
let geometryPromise = null;

export function loadGeometry(url = MAP_URL) {
  geometryPromise = geometryPromise || fetch(url).then(response => {
    if (!response.ok) throw new Error(`Map outline unavailable (HTTP ${response.status})`);
    return response.json();
  }).catch(error => {
    geometryPromise = null;
    throw error;
  });
  return geometryPromise;
}

// Matches the static site's State/UT spellings (docs/india-maps.js and scripts/rbi_state_layer.py).
const ALIASES = {
  'andaman & nicobar islands': 'Andaman & Nicobar Islands', 'andaman & nicobar': 'Andaman & Nicobar Islands',
  'a & n islands': 'Andaman & Nicobar Islands', 'nct delhi': 'Delhi', 'nct of delhi': 'Delhi', 'delhi ncr': 'Delhi',
  'j & k': 'Jammu & Kashmir', 'dadra & nagar haveli': 'Dadra & Nagar Haveli and Daman & Diu',
  'dadra & nagar haveli & daman & diu': 'Dadra & Nagar Haveli and Daman & Diu', 'dnh & dd': 'Dadra & Nagar Haveli and Daman & Diu',
  orissa: 'Odisha', pondicherry: 'Puducherry', uttaranchal: 'Uttarakhand', chattisgarh: 'Chhattisgarh', tamilnadu: 'Tamil Nadu',
};

export function stateKey(name) {
  const text = String(name ?? '').replace(/\(.*?\)/g, '').trim().replace(/^\d+\.?\s+/, '')
    .replace(/&amp;/g, '&').replace(/\s+and\s+/gi, ' & ').replace(/^the\s+/i, '').trim()
    .replace(/[*#@^$]+|\d+$/g, '').replace(/\s*&\s*/g, ' & ');
  return text.split(/\s+/).filter(Boolean).join(' ').replace(/^[ .:-]+|[ .:-]+$/g, '').toLowerCase();
}

export function mapPoints(labels, values, stateNames) {
  const byKey = new Map(stateNames.map(name => [name.toLowerCase(), name]));
  const points = new Map();
  labels.forEach((label, index) => {
    const key = stateKey(label);
    const state = byKey.get(key) || ALIASES[key];
    const value = values[index];
    if (state && !points.has(state) && value !== null && value !== undefined && Number.isFinite(Number(value))) points.set(state, Number(value));
  });
  return points;
}

const NBINS = 5;
const median = list => {
  const sorted = [...list].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
};
export function binEdges(values, scale) {
  const sorted = [...values].sort((a, b) => a - b);
  const min = sorted[0];
  const max = sorted[sorted.length - 1];
  return Array.from({ length: NBINS - 1 }, (_, i) => (scale === 'linear'
    ? min + ((i + 1) * (max - min)) / NBINS
    : sorted[Math.min(sorted.length - 1, Math.floor(((i + 1) * sorted.length) / NBINS))]));
}
export const binOf = (value, edges) => edges.reduce((count, edge) => count + (value >= edge ? 1 : 0), 0);
const binFill = bin => `color-mix(in oklab, var(--map-high) ${Math.round(15 + (bin * 85) / (NBINS - 1))}%, var(--map-low))`;
const slugOf = text => String(text).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');

// Frames are the periods of a map (one per dataset); year-labelled periods run oldest to newest.
export function buildFrames(labels, values, datasets, stateNames) {
  const sets = Array.isArray(datasets) && datasets.length > 1 ? datasets : [{ label: '', values }];
  let frames = sets.map(set => ({ label: String(set.label ?? ''), points: mapPoints(labels, set.values || [], stateNames) })).filter(frame => frame.points.size);
  const years = frames.map(frame => (frame.label.match(/\b(19|20)\d{2}\b/) || [])[0]);
  const timeline = frames.length > 1 && years.every(Boolean);
  if (timeline) frames = frames.map((frame, i) => ({ ...frame, year: Number(years[i]) })).sort((a, b) => a.year - b.year);
  return { frames, timeline };
}

function readHash(mapId, frameCount, stateNames) {
  const params = new URLSearchParams(String(window.location.hash || '').replace(/^#/, ''));
  if (params.get('map') !== mapId) return {};
  const f = params.has('f') ? Number(params.get('f')) : NaN;
  const bins = new Set((params.get('b') || '').split(',').filter(b => /^[0-4]$/.test(b)).map(Number));
  return {
    f: Number.isInteger(f) && f >= 0 && f < frameCount ? f : undefined,
    scale: params.get('s') === 'linear' ? 'linear' : 'quantile',
    sort: ['rank', 'asc', 'name'].includes(params.get('o')) ? params.get('o') : 'rank',
    pin: stateNames.includes(params.get('st')) ? params.get('st') : null,
    q: params.get('q') || '',
    bins,
  };
}

function Sparkline({ name, frames, index }) {
  const series = frames.map(frame => frame.points.get(name));
  const known = series.filter(value => value !== undefined);
  if (known.length < 2) return null;
  const lo = Math.min(...known);
  const hi = Math.max(...known);
  const x = i => (i / (frames.length - 1)) * 120 + 4;
  const y = value => (hi === lo ? 15 : 28 - ((value - lo) / (hi - lo)) * 26);
  const pts = series.map((value, i) => (value === undefined ? null : `${x(i).toFixed(1)},${y(value).toFixed(1)}`)).filter(Boolean).join(' ');
  return (
    <>
      <svg className="india-map-spark" viewBox="0 0 128 32" role="img" aria-label={`${name} over ${frames[0].label} to ${frames[frames.length - 1].label}`}>
        <polyline points={pts} />
        <circle cx={x(index).toFixed(1)} cy={y(frames[index].points.get(name) ?? lo).toFixed(1)} r="3" />
      </svg>
      <small>{frames[0].label} – {frames[frames.length - 1].label}</small>
    </>
  );
}

export default function IndiaMap({ labels = [], values = [], datasets = null, suffix = '', title = 'Map', compact = false, mapId = '' }) {
  const [geometry, setGeometry] = useState(null);
  const [error, setError] = useState('');
  const [hover, setHover] = useState(null);
  const [tip, setTip] = useState({ x: 0, y: 0 });
  const [frameIndex, setFrameIndex] = useState(null);
  const [scale, setScale] = useState('quantile');
  const [sort, setSort] = useState('rank');
  const [pin, setPin] = useState(null);
  const [query, setQuery] = useState('');
  const [bins, setBins] = useState(() => new Set());
  const [playing, setPlaying] = useState(false);
  const [copied, setCopied] = useState(false);
  const stageRef = useRef(null);
  const svgRef = useRef(null);
  const hydrated = useRef(false);
  const id = mapId || slugOf(title);

  useEffect(() => {
    let cancelled = false;
    loadGeometry().then(data => { if (!cancelled) setGeometry(data); }, err => { if (!cancelled) setError(err.message); });
    return () => { cancelled = true; };
  }, []);

  const stateNames = useMemo(() => (geometry ? Object.keys(geometry.states) : []), [geometry]);
  const { frames, timeline } = useMemo(() => (geometry ? buildFrames(labels, values, datasets, stateNames) : { frames: [], timeline: false }), [geometry, labels, values, datasets, stateNames]);

  useEffect(() => {
    if (!geometry || compact || hydrated.current || !frames.length) return;
    hydrated.current = true;
    const saved = readHash(id, frames.length, stateNames);
    if (saved.f !== undefined) setFrameIndex(saved.f);
    if (saved.scale) setScale(saved.scale);
    if (saved.sort) setSort(saved.sort);
    if (saved.pin) setPin(saved.pin);
    if (saved.q) setQuery(saved.q);
    if (saved.bins?.size) setBins(saved.bins);
  }, [geometry, compact, frames, id, stateNames]);

  const current = frameIndex === null ? (timeline ? frames.length - 1 : 0) : Math.min(frameIndex, frames.length - 1);

  useEffect(() => {
    if (!hydrated.current || compact || !frames.length) return;
    const params = new URLSearchParams({ map: id, f: String(current), s: scale, o: sort });
    if (pin) params.set('st', pin);
    if (query) params.set('q', query);
    if (bins.size) params.set('b', [...bins].sort().join(','));
    window.history.replaceState(null, '', `${window.location.pathname}${window.location.search}#${params}`);
  }, [compact, frames.length, id, current, scale, sort, pin, query, bins]);

  useEffect(() => {
    if (!playing) return undefined;
    const timer = setInterval(() => {
      setFrameIndex(prev => {
        const at = prev === null ? (timeline ? frames.length - 1 : 0) : prev;
        if (at >= frames.length - 1) { setPlaying(false); return at; }
        return at + 1;
      });
    }, 1100);
    return () => clearInterval(timer);
  }, [playing, frames.length, timeline]);

  const model = useMemo(() => {
    if (!frames.length) return null;
    const frame = frames[current];
    const entries = [...frame.points.entries()].sort((a, b) => b[1] - a[1]);
    const nums = entries.map(([, value]) => value);
    const pooled = frames.flatMap(item => [...item.points.values()]);
    return {
      frame, entries, pooled, edges: binEdges(pooled, scale),
      rank: new Map(entries.map(([name], i) => [name, i + 1])),
      mean: nums.reduce((a, b) => a + b, 0) / nums.length, median: median(nums),
    };
  }, [frames, current, scale]);

  if (error) return <p className="india-map-status">{error}</p>;
  if (!geometry) return <div className="chart-skeleton" />;
  if (!model) return <p className="india-map-status">No State/UT values to map.</p>;
  const { frame, entries, pooled, edges, rank, mean, median: mid } = model;
  const points = frame.points;
  const fmt = value => formatMagnitude(value, suffix);
  const describe = name => (points.has(name) ? `${name}: ${fmt(points.get(name))} · rank ${rank.get(name)} of ${entries.length}` : `${name}: not reported`);
  const matches = name => !query || name.toLowerCase().includes(query.toLowerCase());
  const highlighting = bins.size > 0 || query !== '';
  const passes = name => points.has(name) && matches(name) && (!bins.size || bins.has(binOf(points.get(name), edges)));
  const [topName, topValue] = entries[0];
  const [lowName, lowValue] = entries[entries.length - 1];
  const summary = compact
    ? `${title}: ${points.size} States/UTs shaded. Highest ${topName} (${fmt(topValue)}), lowest ${lowName} (${fmt(lowValue)}).`
    : `${title}: interactive map of India by State/UT. Use Tab or arrow keys to move between States/UTs, Enter to pin a detail panel.`;

  const place = event => {
    const box = stageRef.current?.getBoundingClientRect();
    if (!box) return;
    if (event.clientX || event.clientY) setTip({ x: event.clientX - box.left, y: event.clientY - box.top });
    else {
      const rect = event.currentTarget.getBoundingClientRect();
      setTip({ x: rect.left + rect.width / 2 - box.left, y: rect.top + rect.height / 2 - box.top });
    }
  };
  const togglePin = name => setPin(prev => (prev === name ? null : name));
  const onKey = (event, name) => {
    if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); if (points.has(name)) togglePin(name); return; }
    const dir = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] }[event.key];
    if (!dir) return;
    event.preventDefault();
    const centre = node => { const b = node.getBBox(); return [b.x + b.width / 2, b.y + b.height / 2]; };
    const nodes = [...svgRef.current.querySelectorAll('path.has-value')];
    const [cx, cy] = centre(event.currentTarget);
    let best = null;
    let bestScore = Infinity;
    nodes.forEach(node => {
      if (node === event.currentTarget) return;
      const [ox, oy] = centre(node);
      const dx = ox - cx;
      const dy = oy - cy;
      if (dx * dir[0] + dy * dir[1] <= 0) return;
      const score = Math.hypot(dx, dy) + Math.abs(dir[0] ? dy : dx);
      if (score < bestScore) { best = node; bestScore = score; }
    });
    if (best) best.focus();
  };
  const toggleBin = bin => setBins(prev => { const next = new Set(prev); if (next.has(bin)) next.delete(bin); else next.add(bin); return next; });
  const share = () => {
    const url = window.location.href;
    const done = () => { setCopied(true); setTimeout(() => setCopied(false), 1600); };
    (navigator.clipboard ? navigator.clipboard.writeText(url) : Promise.reject(new Error('no clipboard'))).then(done, () => window.prompt('Copy this link', url));
  };
  const togglePlay = () => {
    if (playing) { setPlaying(false); return; }
    if (current >= frames.length - 1) setFrameIndex(0);
    setPlaying(true);
  };

  let rows = entries.filter(([name]) => matches(name));
  if (sort === 'asc') rows = [...rows].reverse();
  if (sort === 'name') rows = [...rows].sort((a, b) => a[0].localeCompare(b[0]));
  const maxAbs = Math.max(...pooled.map(Math.abs)) || 1;
  const bounds = [Math.min(...pooled), ...edges, Math.max(...pooled)];
  const pinnedValue = pin ? points.get(pin) : undefined;
  const names = Object.keys(geometry.states);
  const ordered = pin ? [...names.filter(name => name !== pin), pin] : names;

  const paths = ordered.map(name => {
    const has = points.has(name);
    const classes = [has ? 'has-value' : 'no-value', highlighting && !passes(name) ? 'is-dim' : '', pin === name ? 'is-pinned' : '', hover === name ? 'is-hover' : ''].filter(Boolean).join(' ');
    return (
      <path
        key={name}
        d={geometry.states[name]}
        data-state={name}
        className={classes}
        style={{ fill: has ? binFill(binOf(points.get(name), edges)) : 'var(--map-empty)' }}
        tabIndex={has && !compact ? 0 : -1}
        role={compact ? undefined : 'button'}
        aria-pressed={compact ? undefined : pin === name}
        aria-label={compact ? undefined : describe(name)}
        onPointerMove={compact ? undefined : event => { setHover(name); place(event); }}
        onPointerLeave={compact ? undefined : () => setHover(null)}
        onFocus={compact ? undefined : event => { setHover(name); place(event); }}
        onBlur={compact ? undefined : () => setHover(null)}
        onClick={compact ? undefined : () => { if (has) togglePin(name); }}
        onKeyDown={compact ? undefined : event => onKey(event, name)}
      />
    );
  });

  if (compact) {
    return (
      <figure className="india-map compact">
        <div className="india-map-stage">
          <svg ref={svgRef} viewBox={geometry.viewBox} role="img" aria-label={summary} preserveAspectRatio="xMidYMid meet">{paths}</svg>
        </div>
      </figure>
    );
  }

  return (
    <figure className="india-map" onKeyDown={event => { if (event.key === 'Escape' && pin) { setPin(null); event.stopPropagation(); } }}>
      <div className="india-map-ui india-map-toolbar">
        <label className="india-map-search">
          <span className="sr-only">Find a State or UT</span>
          <input
            type="search"
            placeholder="Find a State/UT…"
            autoComplete="off"
            value={query}
            onChange={event => setQuery(event.target.value)}
            onKeyDown={event => { if (event.key === 'Enter') { const first = entries.find(([name]) => matches(name)); if (first) setPin(first[0]); } }}
          />
        </label>
        <div className="india-map-switch" role="group" aria-label="Colour scale">
          {['quantile', 'linear'].map(option => (
            <button key={option} type="button" aria-pressed={scale === option} onClick={() => setScale(option)}>{option === 'quantile' ? 'Quantile' : 'Linear'}</button>
          ))}
        </div>
        <button type="button" className="india-map-share" onClick={share}>{copied ? 'Link copied' : 'Copy link'}</button>
      </div>
      <div className="india-map-main">
        <div className="india-map-stage" ref={stageRef}>
          <svg ref={svgRef} viewBox={geometry.viewBox} role="group" aria-label={summary} preserveAspectRatio="xMidYMid meet">{paths}</svg>
          {hover && (
            <div className="india-map-tip" role="tooltip" style={{ left: tip.x + 12, top: tip.y + 12 }}>
              <strong>{hover}</strong>
              {points.has(hover) ? (
                <>
                  <span>{fmt(points.get(hover))}</span>
                  <small>Rank {rank.get(hover)} of {entries.length} · {points.get(hover) >= mid ? 'above' : 'below'} median</small>
                </>
              ) : <span>Not reported</span>}
            </div>
          )}
        </div>
        <aside className="india-map-ui india-map-side">
          <div className="india-map-detail" aria-live="polite">
            {!pin ? <p className="india-map-hint">Hover for a quick look. Click a State/UT (or press Enter) to pin its details here.</p> : (
              <>
                <div className="india-map-detail-head">
                  <strong>{pin}</strong>
                  <button type="button" className="india-map-unpin" aria-label={`Unpin ${pin}`} onClick={() => setPin(null)}>×</button>
                </div>
                {pinnedValue === undefined ? <p>Not reported by the source.</p> : (
                  <>
                    <p className="big">{fmt(pinnedValue)}</p>
                    <dl>
                      <dt>Rank</dt><dd>{rank.get(pin)} of {entries.length}</dd>
                      <dt>National average</dt><dd>{fmt(mean)}</dd>
                      <dt>Median</dt><dd>{fmt(mid)}</dd>
                      <dt>vs median</dt><dd>{pinnedValue - mid >= 0 ? '+' : '−'}{fmt(Math.abs(pinnedValue - mid))}</dd>
                    </dl>
                  </>
                )}
                {timeline && <Sparkline name={pin} frames={frames} index={current} />}
                {frames.length > 1 && <small className="india-map-period">{frame.label}</small>}
              </>
            )}
          </div>
          <div className="india-map-sortbar" role="group" aria-label="Sort ranking">
            {[['rank', 'High → low'], ['asc', 'Low → high'], ['name', 'A–Z']].map(([key, text]) => (
              <button key={key} type="button" aria-pressed={sort === key} onClick={() => setSort(key)}>{text}</button>
            ))}
          </div>
          <ol className="india-map-list">
            {rows.length ? rows.map(([name, value]) => {
              const dim = bins.size > 0 && !passes(name);
              return (
                <li key={name}>
                  <button
                    type="button"
                    className={`${dim ? 'is-dim' : ''}${pin === name ? ' is-pinned' : ''}${hover === name ? ' is-hover' : ''}`}
                    aria-pressed={pin === name}
                    onPointerEnter={() => setHover(name)}
                    onPointerLeave={() => setHover(null)}
                    onFocus={() => setHover(name)}
                    onBlur={() => setHover(null)}
                    onClick={() => togglePin(name)}
                  >
                    <span className="rk">{rank.get(name)}</span>
                    <span className="nm">{name}</span>
                    <span className="bar" aria-hidden="true"><i style={{ width: `${Math.max(2, (Math.abs(value) / maxAbs) * 100)}%`, background: binFill(binOf(value, edges)) }} /></span>
                    <span className="vl">{fmt(value)}</span>
                  </button>
                </li>
              );
            }) : <li className="india-map-empty">No State/UT matches.</li>}
          </ol>
        </aside>
      </div>
      {frames.length > 1 && (
        <div className="india-map-ui india-map-timebar">
          <button type="button" className="india-map-play" aria-label={playing ? 'Pause' : 'Play through periods'} onClick={togglePlay}>{playing ? '⏸' : '▶'}</button>
          <input type="range" min="0" max={frames.length - 1} step="1" value={current} aria-label="Period" aria-valuetext={frame.label} onChange={event => { setPlaying(false); setFrameIndex(Number(event.target.value)); }} />
          <output>{frame.label}</output>
        </div>
      )}
      <figcaption className="india-map-legend">
        <span className="india-map-readout" aria-live="polite">{hover ? describe(hover) : `Highest: ${topName} · ${fmt(topValue)}`}</span>
        <span className="india-map-bins india-map-ui" role="group" aria-label="Legend: click a band to highlight its States/UTs">
          {Array.from({ length: NBINS }, (_, i) => (
            <button key={i} type="button" aria-pressed={bins.has(i)} title={`${entries.filter(([, value]) => binOf(value, edges) === i).length} States/UTs`} onClick={() => toggleBin(i)}>
              <i style={{ background: binFill(i) }} />{fmt(bounds[i])} – {fmt(bounds[i + 1])}
            </button>
          ))}
          {bins.size > 0 && <button type="button" className="india-map-clear" onClick={() => setBins(new Set())}>Clear</button>}
        </span>
        <span className="india-map-credit">Boundaries: <a href={geometry.sourceUrl} target="_blank" rel="noreferrer">DataMeet</a> ({geometry.license})</span>
      </figcaption>
      <ScriptureVerse verseKey={`map:${mapId || title}`} group="India in Maps" className="compact" />
    </figure>
  );
}
