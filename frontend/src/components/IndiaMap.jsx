import { useEffect, useMemo, useState } from 'react';
import { formatMagnitude } from '../format.js';

export const MAP_URL = '/maps/india-states.json';
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

export default function IndiaMap({ labels = [], values = [], suffix = '', title = 'Map', compact = false }) {
  const [geometry, setGeometry] = useState(null);
  const [error, setError] = useState('');
  const [active, setActive] = useState('');

  useEffect(() => {
    let cancelled = false;
    loadGeometry().then(data => { if (!cancelled) setGeometry(data); }, err => { if (!cancelled) setError(err.message); });
    return () => { cancelled = true; };
  }, []);

  const model = useMemo(() => {
    if (!geometry) return null;
    const points = mapPoints(labels, values, Object.keys(geometry.states));
    const ranked = [...points.entries()].sort((left, right) => right[1] - left[1]);
    const numbers = [...points.values()];
    return { points, ranked, min: Math.min(...numbers), max: Math.max(...numbers) };
  }, [geometry, labels, values]);

  if (error) return <p className="india-map-status">{error}</p>;
  if (!geometry || !model) return <div className="chart-skeleton" />;
  const { points, ranked, min, max } = model;
  if (!ranked.length) return <p className="india-map-status">No State/UT values to map.</p>;
  const share = value => (max === min ? 100 : Math.round(((value - min) / (max - min)) * 85 + 15));
  const describe = name => (points.has(name)
    ? `${name}: ${formatMagnitude(points.get(name), suffix)} (rank ${ranked.findIndex(([state]) => state === name) + 1} of ${ranked.length})`
    : `${name}: not reported`);
  const [topName, topValue] = ranked[0];
  const [lowName, lowValue] = ranked[ranked.length - 1];
  const summary = `${title}: ${points.size} States/UTs shaded. Highest ${topName} (${formatMagnitude(topValue, suffix)}), lowest ${lowName} (${formatMagnitude(lowValue, suffix)}).`;

  return (
    <figure className={`india-map${compact ? ' compact' : ''}`}>
      <svg viewBox={geometry.viewBox} role="img" aria-label={summary} preserveAspectRatio="xMidYMid meet">
        {Object.entries(geometry.states).map(([name, d]) => {
          const has = points.has(name);
          return (
            <path
              key={name}
              d={d}
              className={has ? 'has-value' : 'no-value'}
              style={{ fill: has ? `color-mix(in oklab, var(--map-high) ${share(points.get(name))}%, var(--map-low))` : 'var(--map-empty)' }}
              tabIndex={has && !compact ? 0 : -1}
              onPointerEnter={() => setActive(name)}
              onFocus={() => setActive(name)}
            >
              <title>{describe(name)}</title>
            </path>
          );
        })}
      </svg>
      {!compact && (
        <figcaption className="india-map-legend">
          <span className="india-map-readout" aria-live="polite">{active ? describe(active) : `Highest: ${topName} · ${formatMagnitude(topValue, suffix)}`}</span>
          <span className="india-map-scale">
            <span>{formatMagnitude(min, suffix)}</span><i aria-hidden="true" /><span>{formatMagnitude(max, suffix)}</span>
          </span>
          <span className="india-map-credit">Boundaries: <a href={geometry.sourceUrl} target="_blank" rel="noreferrer">DataMeet</a> ({geometry.license})</span>
        </figcaption>
      )}
    </figure>
  );
}
