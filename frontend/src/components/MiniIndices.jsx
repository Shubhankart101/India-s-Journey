import { Link } from 'react-router-dom';
import { api } from '../api.js';
import { formatMagnitude, isRadial } from '../format.js';
import { useAsync } from '../hooks.js';

const MAX_TILES = 3;
const SNAPSHOT_PARTS = 4;
const SHARE_COLORS = ['#ff9933', '#58a6ff', '#3fb950', '#bc8cff', '#8b949e'];

const numeric = value => value !== null && value !== undefined && value !== '' && Number.isFinite(Number(value));

const trendPoints = item => {
  const labels = item.preview?.labels || [];
  const values = item.preview?.datasets?.[0]?.values || [];
  return labels.map((label, index) => ({ label: String(label), value: values[index] }))
    .filter(point => /^\d{4}/.test(point.label) && numeric(point.value))
    .map(point => ({ label: point.label, value: Number(point.value) }));
};

// Largest parts first, with the tail folded into "Other" so the share bar stays readable.
const snapshotParts = (item, foldOther = true) => {
  const labels = item.preview?.labels || [];
  const values = item.preview?.datasets?.[0]?.values || [];
  const parts = labels.map((label, index) => ({ label: String(label), value: Number(values[index]) }))
    .filter(part => numeric(part.value) && part.value > 0)
    .sort((left, right) => right.value - left.value);
  if (parts.length <= SNAPSHOT_PARTS) return parts;
  if (!foldOther) return parts.slice(0, SNAPSHOT_PARTS);
  const rest = parts.slice(SNAPSHOT_PARTS - 1).reduce((sum, part) => sum + part.value, 0);
  return [...parts.slice(0, SNAPSHOT_PARTS - 1), { label: 'Other', value: rest }];
};

// Prefers headline time series (sparkline tiles); groups without enough trends are topped up with
// latest-snapshot tiles (share bars), so every group gets a mini view.
export function pickMiniIndices(results = [], limit = MAX_TILES) {
  const live = results.filter(item => item.is_live);
  const trends = live.filter(item => !isRadial(item.chart_type) && item.scope !== 'state')
    .map(item => ({ kind: 'trend', item, points: trendPoints(item) }))
    .filter(({ points }) => points.length >= 3)
    .slice(0, limit);
  if (trends.length >= limit) return trends;
  const used = new Set(trends.map(({ item }) => item.key));
  const snapshots = live.filter(item => !used.has(item.key) && item.scope !== 'state' && trendPoints(item).length < 3)
    .map(item => ({ kind: 'snapshot', item, parts: snapshotParts(item, isRadial(item.chart_type)) }))
    .filter(({ parts }) => parts.length >= 2)
    .slice(0, limit - trends.length);
  return [...trends, ...snapshots];
}

export function miniChange(points, suffix = '') {
  const [previous, latest] = points.slice(-2).map(point => point.value);
  if (previous === undefined || latest === undefined) return null;
  if (/%/.test(suffix)) return { value: latest - previous, text: `${latest - previous >= 0 ? '+' : '−'}${Math.abs(latest - previous).toFixed(1)} pp` };
  if (!previous) return null;
  const change = ((latest - previous) / Math.abs(previous)) * 100;
  return { value: change, text: `${change >= 0 ? '+' : '−'}${Math.abs(change).toFixed(1)}%` };
}

function Sparkline({ points, color }) {
  const width = 120;
  const height = 34;
  const values = points.map(point => point.value);
  const min = Math.min(...values);
  const span = Math.max(...values) - min || 1;
  const coords = values.map((value, index) => [
    (index / (values.length - 1)) * width,
    height - 3 - ((value - min) / span) * (height - 6),
  ]);
  const line = coords.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(' ');
  return (
    <svg className="mini-spark" viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none" aria-hidden="true" style={{ '--spark': color }}>
      <polygon points={`0,${height} ${line} ${width},${height}`} />
      <polyline points={line} />
    </svg>
  );
}

function ShareBar({ parts }) {
  const total = parts.reduce((sum, part) => sum + part.value, 0);
  return (
    <span className="mini-share" aria-hidden="true">
      {parts.map((part, index) => (
        <span key={part.label} style={{ width: `${(part.value / total) * 100}%`, background: SHARE_COLORS[index % SHARE_COLORS.length] }} />
      ))}
    </span>
  );
}

function RankBars({ parts, suffix }) {
  const max = parts[0].value;
  return (
    <span className="mini-ranks" aria-hidden="true">
      {parts.map((part, index) => (
        <span key={part.label} title={`${part.label}: ${formatMagnitude(part.value, suffix)}`} style={{ width: `${(part.value / max) * 100}%`, background: SHARE_COLORS[index % SHARE_COLORS.length] }} />
      ))}
    </span>
  );
}

function TrendTile({ item, points }) {
  const latest = points[points.length - 1];
  const change = miniChange(points, item.suffix);
  return (
    <>
      <span className="mini-row">
        <strong>{formatMagnitude(latest.value, item.suffix)}</strong>
        {change && <span className={`mini-change ${change.value >= 0 ? 'up' : 'down'}`}>{change.value >= 0 ? '▲' : '▼'} {change.text}</span>}
      </span>
      <Sparkline points={points} color={item.color || '#ff9933'} />
      <span className="mini-period">{points[0].label.slice(0, 4)}–{latest.label}</span>
    </>
  );
}

function SnapshotTile({ item, parts }) {
  const total = parts.reduce((sum, part) => sum + part.value, 0);
  const [leader] = parts;
  const radial = isRadial(item.chart_type);
  const shown = radial ? `${((leader.value / total) * 100).toFixed(1)}%` : formatMagnitude(leader.value, item.suffix);
  return (
    <>
      <strong className="mini-value">{shown}</strong>
      <span className="mini-leader">{leader.label}</span>
      {radial ? <ShareBar parts={parts} /> : <RankBars parts={parts} suffix={item.suffix} />}
      <span className="mini-period">{radial ? 'Share of total' : 'Highest values'} · latest snapshot</span>
    </>
  );
}

export default function MiniIndices({ category }) {
  const { data } = useAsync(signal => api.groupHeadlines(category.slug, signal), [category.slug]);
  const picks = pickMiniIndices((data?.results || []).filter(item => item.category_slug === category.slug));
  if (!picks.length) return null;
  return (
    <ul className="mini-indices" aria-label={`Headline ${category.name} indicators`} key={category.slug}>
      {picks.map(pick => (
        <li key={pick.item.key}>
          <Link className={`mini-index mini-${pick.kind}`} to={`/indicator/${pick.item.key}`} title={pick.item.subtitle || pick.item.title}>
            <span className="mini-title">{pick.item.title}</span>
            {pick.kind === 'trend' ? <TrendTile {...pick} /> : <SnapshotTile {...pick} />}
          </Link>
        </li>
      ))}
    </ul>
  );
}