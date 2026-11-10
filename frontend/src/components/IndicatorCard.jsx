import { memo } from 'react';
import { Link } from 'react-router-dom';
import { MAX_COMPARE, useCompare } from '../compare.jsx';
import { PALETTE_COMPARE } from '../palette.js';
import { chartModes, formatMagnitude } from '../format.js';
import { useInView } from '../hooks.js';
import LazyChart from './LazyChart.jsx';
import ScriptureVerse from './ScriptureVerse.jsx';

function IndicatorCard({ indicator }) {
  const compare = useCompare();
  const [verseRef, verseNear] = useInView('400px');
  const preview = indicator.preview || { labels: [], datasets: [] };
  const { initial } = chartModes({ ...indicator, labels: preview.labels, datasets: preview.datasets });
  const inCompare = compare.has(indicator.key);
  const slot = compare.items.findIndex(item => item.key === indicator.key);
  return (
    <article className="card indicator-card">
      <Link to={`/indicator/${indicator.key}`} className="card-link" aria-label={`Open ${indicator.title}`}>
        <div className="card-head">
          <span className="eyebrow">{indicator.subgroup}</span>
          <h3>{indicator.title}</h3>
          {indicator.subtitle && <p className="muted clamp-2">{indicator.subtitle}</p>}
        </div>
        {indicator.is_live ? (
          <LazyChart
            height={170}
            compact
            title={indicator.title}
            labels={preview.labels}
            datasets={preview.datasets}
            type={initial}
            indexAxis={indicator.index_axis}
            suffix={indicator.suffix}
            color={indicator.color}
          />
        ) : <div className="card-pending">Awaiting the next official release</div>}
        <div className="card-foot">
          <span className="latest">
            <strong>{formatMagnitude(indicator.latest_value, indicator.suffix)}</strong>
            {indicator.latest_label && <small> · {indicator.latest_label}</small>}
          </span>
          <span className="chip">{indicator.frequency || indicator.chart_type}</span>
        </div>
      </Link>
      <div ref={verseRef} className="scripture-slot">
        {verseNear && <ScriptureVerse verseKey={indicator.key} group={indicator.category} />}
      </div>
      <button
        type="button"
        className={`compare-toggle${inCompare ? ' active' : ''}`}
        style={slot >= 0 ? { '--slot': PALETTE_COMPARE[slot % PALETTE_COMPARE.length] } : undefined}
        aria-pressed={inCompare}
        disabled={!inCompare && compare.full}
        onClick={() => compare.toggle(indicator)}
        title={!inCompare && compare.full ? `Compare holds up to ${MAX_COMPARE} indicators — remove one first` : inCompare ? 'Remove from compare' : 'Add to compare'}
      >
        {inCompare ? '✓ Added' : '+ Compare'}
      </button>
    </article>
  );
}

export default memo(IndicatorCard);
