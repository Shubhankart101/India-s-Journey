import { lazy, Suspense, useEffect, useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { api } from '../api.js';
import { MAX_COMPARE, useCompare } from '../compare.jsx';
import { formatMagnitude } from '../format.js';
import { useAsync, useDebounced, useDocumentTitle } from '../hooks.js';
import { PALETTE_COMPARE } from '../palette.js';
import { Empty, ErrorState, Loading } from '../components/States.jsx';

const ChartView = lazy(() => import('../components/ChartView.jsx'));

// Rebases each series to 100 at its first available value so different units can share one axis.
export function normalise(values) {
  const base = values.find(value => value !== null && value !== undefined && Number(value) !== 0);
  if (base === undefined) return values.map(() => null);
  return values.map(value => (value === null || value === undefined ? null : (Number(value) / Number(base)) * 100));
}

export default function Compare() {
  useDocumentTitle('Compare');
  const [params, setParams] = useSearchParams();
  const compare = useCompare();
  const urlKeys = (params.get('keys') || '').split(',').map(key => key.trim()).filter(Boolean).slice(0, MAX_COMPARE);
  const keys = urlKeys.length ? urlKeys : compare.items.map(item => item.key);
  const keyString = keys.join(',');
  const [normalised, setNormalised] = useState(params.get('normalise') === '1');

  useEffect(() => {
    if (!urlKeys.length && keys.length) setParams({ keys: keyString }, { replace: true });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [keyString]);

  const result = useAsync(signal => (keys.length ? api.compare(keys, signal) : Promise.resolve(null)), [keyString]);
  const setKeys = next => {
    const query = {};
    if (next.length) query.keys = next.join(',');
    if (normalised) query.normalise = '1';
    setParams(query, { replace: true });
  };
  const remove = key => {
    setKeys(keys.filter(item => item !== key));
    if (compare.has(key)) compare.toggle({ key });
  };
  const add = indicator => {
    if (keys.includes(indicator.key) || keys.length >= MAX_COMPARE) return;
    setKeys([...keys, indicator.key]);
    if (!compare.has(indicator.key)) compare.toggle(indicator);
  };

  const data = result.data;
  const mixedUnits = data ? new Set(data.series.map(item => item.suffix.trim())).size > 1 : false;
  const datasets = useMemo(() => (data?.series || []).map((item, index) => ({
    label: item.title,
    color: PALETTE_COMPARE[index % PALETTE_COMPARE.length],
    values: normalised ? normalise(item.values) : item.values,
  })), [data, normalised]);

  return (
    <>
      <section className="page-hero">
        <p className="eyebrow">Compare</p>
        <h1>Side by side.</h1>
        <p className="lead">Pick up to {MAX_COMPARE} indicators. Rebase to 100 when the units differ.</p>
      </section>

      <section className="section">
        <IndicatorPicker onPick={add} disabled={keys.length >= MAX_COMPARE} exclude={keys} />
        <ul className="pill-list" aria-label="Selected indicators">
          {(data?.series || []).map((item, index) => (
            <li key={item.key} className="pill" style={{ '--pill': PALETTE_COMPARE[index % PALETTE_COMPARE.length] }}>
              <Link to={`/indicator/${item.key}`}>{item.title}</Link>
              <button type="button" aria-label={`Remove ${item.title}`} onClick={() => remove(item.key)}>×</button>
            </li>
          ))}
        </ul>
        {data?.missing?.length > 0 && <p className="form-error">Not found: {data.missing.join(', ')}</p>}
      </section>

      <section className="section">
        {!keys.length && <Empty>Nothing to compare yet. Search above, or use “+ Compare” on any chart.</Empty>}
        {keys.length > 0 && result.loading && <Loading label="Aligning series…" />}
        {result.error && <ErrorState error={result.error} onRetry={result.reload} />}
        {data && data.series.length > 0 && (
          <div className="card chart-card">
            <div className="chart-toolbar">
              <label className="switch">
                <input
                  type="checkbox"
                  checked={normalised}
                  onChange={event => {
                    setNormalised(event.target.checked);
                    const next = new URLSearchParams(params);
                    if (event.target.checked) next.set('normalise', '1'); else next.delete('normalise');
                    setParams(next, { replace: true });
                  }}
                />
                <span>Rebase to 100</span>
              </label>
              {mixedUnits && !normalised && <span className="muted small">Units differ — rebasing makes trends comparable.</span>}
            </div>
            <div className="detail-chart">
              <Suspense fallback={<div className="chart-skeleton" />}>
                <ChartView title="Comparison" labels={data.labels} datasets={datasets} type="line" suffix={normalised || mixedUnits ? '' : data.series[0].suffix} />
              </Suspense>
            </div>
            <div className="table-wrap">
              <table>
                <thead><tr><th scope="col">Indicator</th><th scope="col">Latest</th><th scope="col">Group</th></tr></thead>
                <tbody>
                  {data.series.map(item => {
                    const lastIndex = item.values.findLastIndex(value => value !== null);
                    return (
                      <tr key={item.key}>
                        <th scope="row"><Link to={`/indicator/${item.key}`}>{item.title}</Link></th>
                        <td>{lastIndex >= 0 ? `${formatMagnitude(item.values[lastIndex], item.suffix)} (${data.labels[lastIndex]})` : '—'}</td>
                        <td>{item.category}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </section>
    </>
  );
}

function IndicatorPicker({ onPick, disabled, exclude }) {
  const [query, setQuery] = useState('');
  const debounced = useDebounced(query.trim(), 250);
  const results = useAsync(
    signal => (debounced.length >= 2 ? api.indicators({ q: debounced, page_size: 8, live: 'true' }, signal) : Promise.resolve(null)),
    [debounced],
  );
  const options = (results.data?.results || []).filter(item => !exclude.includes(item.key));
  return (
    <div className="picker">
      <label className="search">
        <span className="sr-only">Add an indicator to compare</span>
        <input
          type="search"
          placeholder={disabled ? `Maximum of ${MAX_COMPARE} reached` : 'Add an indicator, e.g. inflation'}
          value={query}
          disabled={disabled}
          onChange={event => setQuery(event.target.value)}
        />
      </label>
      {debounced.length >= 2 && !disabled && (
        <ul className="picker-results" role="listbox" aria-label="Matching indicators">
          {results.loading && <li className="muted">Searching…</li>}
          {!results.loading && options.length === 0 && <li className="muted">No matches</li>}
          {options.map(item => (
            <li key={item.key} role="option" aria-selected="false">
              <button type="button" onClick={() => { onPick(item); setQuery(''); }}>
                <strong>{item.title}</strong>
                <small className="muted">{item.category} · {item.subgroup}</small>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
