import { Link, useNavigate } from 'react-router-dom';
import SubgroupArticle from './SubgroupArticle.jsx';
import { formatMagnitude } from '../format.js';
import './MapSelector.css';

// Generic per-region (State/UT) article page: back link, an optional switcher and the shared long-form layout.
export default function RegionArticle({ backTo, backLabel, switcher = null, ...article }) {
  return (
    <>
      <Link className="region-back" to={backTo}>← {backLabel}</Link>
      {switcher}
      <SubgroupArticle {...article} />
    </>
  );
}

export function RegionSwitch({ names, current, hrefFor, label = 'Jump to another State/UT' }) {
  const navigate = useNavigate();
  return (
    <label className="region-switch">
      <span>{label}</span>
      <select value={current} onChange={event => navigate(hrefFor(event.target.value))} aria-label={label}>
        {names.map(name => <option key={name} value={name}>{name}</option>)}
      </select>
    </label>
  );
}

// The region's neighbours in rank order, drawn as plain bars so the region itself can be highlighted.
export function RankBars({ points, name, suffix = '', size = 9 }) {
  const ranked = [...points.entries()].sort((a, b) => b[1] - a[1]);
  const index = Math.max(0, ranked.findIndex(([label]) => label === name));
  const start = Math.max(0, Math.min(index - Math.floor(size / 2), ranked.length - size));
  const visible = ranked.slice(start, start + size);
  const max = Math.max(...visible.map(([, value]) => Math.abs(value)), 1e-9);
  return (
    <ol className="rank-bars" aria-label={`Ranking around ${name}`}>
      {visible.map(([label, value], position) => (
        <li key={label} className={label === name ? 'is-self' : undefined} aria-current={label === name ? 'true' : undefined}>
          <span title={label}>{start + position + 1}. {label}</span>
          <i style={{ width: `${Math.max(3, (Math.abs(value) / max) * 100)}%` }} />
          <b>{formatMagnitude(value, suffix)}</b>
        </li>
      ))}
    </ol>
  );
}
