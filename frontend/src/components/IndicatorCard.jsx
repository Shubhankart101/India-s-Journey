import { Link } from 'react-router-dom';
import { useCompare } from '../compare.jsx';
import { chartModes, formatMagnitude } from '../format.js';
import LazyChart from './LazyChart.jsx';

export default function IndicatorCard({ indicator }) {
  const compare = useCompare();
  const preview = indicator.preview || { labels: [], datasets: [] };
  const { initial } = chartModes({ ...indicator, labels: preview.labels, datasets: preview.datasets });
  const inCompare = compare.has(indicator.key);
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
      <button
        type="button"
        className={`compare-toggle${inCompare ? ' active' : ''}`}
        aria-pressed={inCompare}
        disabled={!inCompare && compare.full}
        onClick={() => compare.toggle(indicator)}
        title={!inCompare && compare.full ? 'Compare holds up to four indicators' : 'Add to compare'}
      >
        {inCompare ? '✓ Comparing' : '+ Compare'}
      </button>
    </article>
  );
}
