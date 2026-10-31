import { lazy, Suspense, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { api } from '../api.js';
import { useAuth } from '../auth.jsx';
import { useCompare } from '../compare.jsx';
import { chartModes, formatMagnitude, isRadial, seriesStats } from '../format.js';
import { useAsync, useDocumentTitle } from '../hooks.js';
import IndicatorCard from '../components/IndicatorCard.jsx';
import { ErrorState, Loading } from '../components/States.jsx';

const ChartView = lazy(() => import('../components/ChartView.jsx'));
const MODE_LABEL = { doughnut: '◔ Pie', pie: '◔ Pie', bar: '▥ Bar', line: '⌇ Line' };
const TABLE_LIMIT = 120;

export default function Indicator() {
  const { key } = useParams();
  const { data, error, loading, reload } = useAsync(signal => api.indicator(key, signal), [key]);
  useDocumentTitle(data?.title || (error ? 'Not found' : 'Loading'));
  if (loading) return <Loading label="Loading indicator…" />;
  if (error) {
    return (
      <section className="section">
        <ErrorState error={error.status === 404 ? new Error('That indicator does not exist.') : error} onRetry={error.status === 404 ? undefined : reload} />
        <p className="center"><Link to="/explore">← Back to Explore</Link></p>
      </section>
    );
  }
  return <IndicatorView key={data.key} indicator={data} />;
}

function IndicatorView({ indicator }) {
  const navigate = useNavigate();
  const { user } = useAuth();
  const compare = useCompare();
  const { modes, initial } = chartModes(indicator);
  const [mode, setMode] = useState(initial);
  const [saved, setSaved] = useState(indicator.is_saved);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState('');
  const [showTable, setShowTable] = useState(false);

  const yearLabels = indicator.labels.length > 2 && indicator.labels.every(label => /^\d{4}/.test(label));
  const years = useMemo(() => (yearLabels ? [...new Set(indicator.labels.map(label => label.slice(0, 4)))] : []), [indicator.labels, yearLabels]);
  const [range, setRange] = useState(() => ({ start: years[0], end: years[years.length - 1] }));
  const visible = useMemo(() => {
    if (!yearLabels || isRadial(mode)) return { labels: indicator.labels, datasets: indicator.datasets };
    const indexes = indicator.labels.map((label, index) => [label.slice(0, 4), index])
      .filter(([year]) => year >= range.start && year <= range.end).map(([, index]) => index);
    return {
      labels: indexes.map(index => indicator.labels[index]),
      datasets: indicator.datasets.map(dataset => ({ ...dataset, values: indexes.map(index => dataset.values[index] ?? null) })),
    };
  }, [indicator, range, yearLabels, mode]);

  const stats = seriesStats(visible.datasets[0]?.values || []);
  const paragraphs = (indicator.details || '').split(/\n\n+/).filter(Boolean);
  const inCompare = compare.has(indicator.key);
  const art = indicator.subgroup_art || indicator.category_art;

  const toggleSave = async () => {
    if (!user) {
      navigate(`/login?next=/indicator/${indicator.key}`);
      return;
    }
    setSaving(true);
    setSaveError('');
    try {
      if (saved) await api.unsave(indicator.key);
      else await api.save(indicator.key);
      setSaved(!saved);
    } catch (error) {
      setSaveError(error.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <section className={`page-hero detail-hero${art ? ' with-art' : ''}`} style={art ? { '--hero-art': `url(/art/${art})` } : undefined}>
        <nav className="breadcrumbs" aria-label="Breadcrumb">
          <Link to="/explore">Explore</Link>
          <span aria-hidden="true">›</span>
          <Link to={`/explore?category=${indicator.category_slug}`}>{indicator.category}</Link>
          <span aria-hidden="true">›</span>
          <Link to={`/explore?category=${indicator.category_slug}&subgroup=${indicator.subgroup_slug}`}>{indicator.subgroup}</Link>
        </nav>
        <h1>{indicator.title}</h1>
        {indicator.subtitle && <p className="lead">{indicator.subtitle}</p>}
        <div className="action-row">
          <button type="button" className={`btn ${saved ? 'btn-primary' : 'btn-ghost'}`} onClick={toggleSave} disabled={saving} aria-pressed={saved}>
            {saved ? '★ Saved' : '☆ Save'}
          </button>
          <button
            type="button"
            className={`btn ${inCompare ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => compare.toggle(indicator)}
            disabled={!inCompare && compare.full}
            aria-pressed={inCompare}
          >
            {inCompare ? '✓ In compare' : '+ Compare'}
          </button>
          <a className="btn btn-ghost" href={api.downloadUrl(indicator.key, 'csv')} download>⇩ CSV</a>
          <a className="btn btn-ghost" href={api.downloadUrl(indicator.key, 'json')} download>⇩ JSON</a>
        </div>
        {saveError && <p className="form-error" role="alert">{saveError}</p>}
      </section>

      <section className="section">
        <div className="card chart-card">
          {indicator.is_live ? (
            <>
              <div className="chart-toolbar">
                {modes.length > 1 && (
                  <div className="segmented" role="group" aria-label="Chart type">
                    {modes.map(item => (
                      <button key={item} type="button" className={item === mode ? 'active' : ''} aria-pressed={item === mode} onClick={() => setMode(item)}>
                        {MODE_LABEL[item] || item}
                      </button>
                    ))}
                  </div>
                )}
                {yearLabels && !isRadial(mode) && years.length > 1 && (
                  <div className="range" aria-label="Year range">
                    <select aria-label="From year" value={range.start} onChange={event => setRange(current => ({ start: event.target.value, end: current.end < event.target.value ? event.target.value : current.end }))}>
                      {years.map(year => <option key={year}>{year}</option>)}
                    </select>
                    <span>to</span>
                    <select aria-label="To year" value={range.end} onChange={event => setRange(current => ({ end: event.target.value, start: current.start > event.target.value ? event.target.value : current.start }))}>
                      {years.map(year => <option key={year}>{year}</option>)}
                    </select>
                  </div>
                )}
              </div>
              <div className="detail-chart">
                <Suspense fallback={<div className="chart-skeleton" />}>
                  <ChartView
                    title={indicator.title}
                    labels={visible.labels}
                    datasets={visible.datasets}
                    type={mode}
                    indexAxis={indicator.index_axis}
                    suffix={indicator.suffix}
                    color={indicator.color}
                  />
                </Suspense>
              </div>
            </>
          ) : <p className="card-pending">{indicator.error || 'Awaiting the next official release.'}</p>}
        </div>

        {stats && (
          <dl className="stat-grid">
            <div><dt>Latest{indicator.latest_label ? ` (${indicator.latest_label})` : ''}</dt><dd>{formatMagnitude(indicator.latest_value, indicator.suffix)}</dd></div>
            <div><dt>Highest</dt><dd>{formatMagnitude(stats.max, indicator.suffix)}</dd></div>
            <div><dt>Lowest</dt><dd>{formatMagnitude(stats.min, indicator.suffix)}</dd></div>
            {yearLabels && stats.change !== null && <div><dt>Change in range</dt><dd>{stats.change >= 0 ? '+' : ''}{stats.change.toFixed(1)}%</dd></div>}
            <div><dt>Data points</dt><dd>{indicator.point_count.toLocaleString('en-IN')}</dd></div>
            <div><dt>Frequency</dt><dd>{indicator.frequency || '—'}</dd></div>
          </dl>
        )}
      </section>

      <section className="section two-col">
        <div>
          <h2>About this indicator</h2>
          {paragraphs.length ? paragraphs.map(text => <p key={text.slice(0, 40)}>{text}</p>) : <p className="muted">No additional notes.</p>}
          {indicator.note && <p className="muted">{indicator.note}</p>}
        </div>
        <aside className="card source-card">
          <h3>Source</h3>
          {indicator.source && <p>{indicator.source}</p>}
          {indicator.source_url && <a href={indicator.source_url} target="_blank" rel="noopener noreferrer">Open official source ↗</a>}
          <p className="muted small">Group: {indicator.category} · {indicator.subgroup}</p>
        </aside>
      </section>

      {indicator.is_live && (
        <section className="section">
          <button type="button" className="btn btn-ghost" onClick={() => setShowTable(value => !value)} aria-expanded={showTable}>
            {showTable ? 'Hide data table' : 'Show data table'}
          </button>
          {showTable && (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr><th scope="col">{indicator.scope_label || 'Label'}</th>{indicator.datasets.map(dataset => <th scope="col" key={dataset.label}>{dataset.label}</th>)}</tr>
                </thead>
                <tbody>
                  {indicator.labels.slice(-TABLE_LIMIT).map((label, offset) => {
                    const index = Math.max(indicator.labels.length - TABLE_LIMIT, 0) + offset;
                    return (
                      <tr key={`${label}-${index}`}>
                        <th scope="row">{label}</th>
                        {indicator.datasets.map(dataset => <td key={dataset.label}>{formatMagnitude(dataset.values[index], indicator.suffix)}</td>)}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
              {indicator.labels.length > TABLE_LIMIT && <p className="muted small">Showing the latest {TABLE_LIMIT} rows — download the CSV for all {indicator.labels.length}.</p>}
            </div>
          )}
        </section>
      )}

      <nav className="section pager" aria-label="More in this group">
        {indicator.previous_key ? <Link className="btn btn-ghost" to={`/indicator/${indicator.previous_key}`}>← Previous</Link> : <span />}
        {indicator.next_key && <Link className="btn btn-ghost" to={`/indicator/${indicator.next_key}`}>Next →</Link>}
      </nav>

      {indicator.related.length > 0 && (
        <section className="section">
          <h2>More in {indicator.subgroup}</h2>
          <div className="card-grid">
            {indicator.related.map(item => <IndicatorCard key={item.key} indicator={item} />)}
          </div>
        </section>
      )}
    </>
  );
}
