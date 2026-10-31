import { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { api } from '../api.js';
import { useAsync, useDebounced, useDocumentTitle } from '../hooks.js';
import IndicatorCard from '../components/IndicatorCard.jsx';
import { Empty, ErrorState, Loading } from '../components/States.jsx';
import ArtBackdrop from '../components/ArtBackdrop.jsx';

const PAGE_SIZE = 24;
const FILTER_KEYS = ['q', 'category', 'subgroup', 'live', 'chart', 'sort'];

export default function Explore() {
  const [params, setParams] = useSearchParams();
  const [query, setQuery] = useState(params.get('q') || '');
  const debouncedQuery = useDebounced(query.trim(), 300);
  const filters = useMemo(() => Object.fromEntries(FILTER_KEYS.map(key => [key, params.get(key) || ''])), [params]);
  const categories = useAsync(signal => api.categories(signal), []);
  const category = (categories.data || []).find(item => item.slug === filters.category);
  const subgroup = category?.subgroups.find(item => item.slug === filters.subgroup);
  useDocumentTitle(subgroup?.name || category?.name || 'Explore');

  const update = changes => {
    const next = new URLSearchParams(params);
    Object.entries(changes).forEach(([key, value]) => (value ? next.set(key, value) : next.delete(key)));
    setParams(next, { replace: true });
  };

  const urlQuery = params.get('q') || '';
  useEffect(() => {
    if (debouncedQuery !== urlQuery) update({ q: debouncedQuery });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedQuery]);
  useEffect(() => {
    // Only external URL changes (back button, clear filters) should overwrite what the user is typing.
    if (urlQuery !== debouncedQuery) setQuery(urlQuery);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [urlQuery]);

  const [pages, setPages] = useState({ items: [], next: null, count: 0, page: 1 });
  const [loadingMore, setLoadingMore] = useState(false);
  const [moreError, setMoreError] = useState(null);
  const filterKey = JSON.stringify(filters);
  const first = useAsync(signal => api.indicators({ ...filters, page_size: PAGE_SIZE }, signal), [filterKey]);
  useEffect(() => {
    if (first.data) setPages({ items: first.data.results, next: first.data.next, count: first.data.count, page: 1 });
  }, [first.data]);

  const loadMore = async () => {
    setLoadingMore(true);
    setMoreError(null);
    try {
      const data = await api.indicators({ ...filters, page_size: PAGE_SIZE, page: pages.page + 1 });
      setPages(current => ({ items: [...current.items, ...data.results], next: data.next, count: data.count, page: current.page + 1 }));
    } catch (error) {
      setMoreError(error);
    } finally {
      setLoadingMore(false);
    }
  };

  const heroArt = subgroup?.art || category?.art || 'economy.svg';
  const activeFilters = FILTER_KEYS.filter(key => filters[key] && key !== 'sort').length;

  return (
    <>
      <section className="page-hero with-art">
        <ArtBackdrop art={heroArt} />
        <p className="eyebrow">{category ? 'Group' : 'Explore'}</p>
        <h1>{subgroup?.title || category?.title || 'Every indicator, one search away.'}</h1>
        <p className="lead">{subgroup?.description || category?.description || 'Filter by group and subgroup, search any keyword, then open an indicator for the full chart, data table and downloads.'}</p>
      </section>

      <section className="filters" aria-label="Filters">
        <label className="search">
          <span className="sr-only">Search indicators</span>
          <input
            type="search"
            placeholder="Search e.g. coal, GDP, Lok Sabha, tourism"
            value={query}
            onChange={event => setQuery(event.target.value)}
          />
        </label>
        <div className="filter-row">
          <label>
            <span className="sr-only">Group</span>
            <select value={filters.category} onChange={event => update({ category: event.target.value, subgroup: '' })} aria-label="Group">
              <option value="">All groups</option>
              {(categories.data || []).map(item => <option key={item.slug} value={item.slug}>{item.name}</option>)}
            </select>
          </label>
          <label>
            <span className="sr-only">Subgroup</span>
            <select value={filters.subgroup} onChange={event => update({ subgroup: event.target.value })} disabled={!category} aria-label="Subgroup">
              <option value="">All subgroups</option>
              {(category?.subgroups || []).map(item => <option key={item.slug} value={item.slug}>{item.name} ({item.indicator_count})</option>)}
            </select>
          </label>
          <label>
            <span className="sr-only">Chart type</span>
            <select value={filters.chart} onChange={event => update({ chart: event.target.value })} aria-label="Chart type">
              <option value="">All chart types</option>
              <option value="radial">Pie charts</option>
              <option value="line">Line charts</option>
              <option value="bar">Bar charts</option>
            </select>
          </label>
          <label>
            <span className="sr-only">Sort</span>
            <select value={filters.sort} onChange={event => update({ sort: event.target.value })} aria-label="Sort">
              <option value="">Default order</option>
              <option value="title">A–Z</option>
              <option value="points">Most data points</option>
              <option value="recent">Recently updated</option>
            </select>
          </label>
          {activeFilters > 0 && (
            <button type="button" className="btn btn-ghost" onClick={() => { setQuery(''); setParams({}, { replace: true }); }}>
              Clear filters
            </button>
          )}
        </div>
        {category ? (
          <div className="picture-rail" role="list" aria-label="Subgroups">
            {category.subgroups.map(item => (
              <button
                type="button"
                role="listitem"
                key={item.slug}
                aria-pressed={item.slug === filters.subgroup}
                className={`picture-card${item.slug === filters.subgroup ? ' active' : ''}`}
                style={{ '--card-art': `url(/art/${item.art || category.art})` }}
                onClick={() => update({ subgroup: item.slug === filters.subgroup ? '' : item.slug })}
              >
                <span className="picture-name">{item.name}</span>
                <span className="picture-meta">{item.indicator_count} charts</span>
              </button>
            ))}
          </div>
        ) : (categories.data || []).length > 0 && (
          <div className="picture-rail" role="list" aria-label="Groups">
            {categories.data.map(item => (
              <button
                type="button"
                role="listitem"
                key={item.slug}
                className="picture-card"
                style={{ '--card-art': `url(/art/${item.art || 'economy.svg'})` }}
                onClick={() => update({ category: item.slug, subgroup: '' })}
              >
                <span className="picture-name">{item.name}</span>
                <span className="picture-meta">{item.subgroups.length} subgroups</span>
              </button>
            ))}
          </div>
        )}
      </section>

      <section className="section" aria-live="polite">
        {first.loading && <Loading label="Finding indicators…" />}
        {first.error && <ErrorState error={first.error} onRetry={first.reload} />}
        {!first.loading && !first.error && (
          <>
            <p className="muted result-count">{pages.count.toLocaleString('en-IN')} indicator{pages.count === 1 ? '' : 's'}</p>
            {pages.items.length === 0 ? <Empty>No indicators match. Try a broader search.</Empty> : (
              <div className="card-grid">
                {pages.items.map(indicator => <IndicatorCard key={indicator.key} indicator={indicator} />)}
              </div>
            )}
            {moreError && <ErrorState error={moreError} />}
            {pages.next && (
              <div className="center">
                <button type="button" className="btn btn-primary" onClick={loadMore} disabled={loadingMore}>
                  {loadingMore ? 'Loading…' : `Load more (${pages.count - pages.items.length} left)`}
                </button>
              </div>
            )}
          </>
        )}
      </section>
    </>
  );
}
