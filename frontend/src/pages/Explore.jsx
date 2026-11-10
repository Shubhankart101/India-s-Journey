import { useEffect, useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { api } from '../api.js';
import { useAsync, useBatchedCount, useDebounced, useDocumentTitle } from '../hooks.js';
import IndicatorCard from '../components/IndicatorCard.jsx';
import { Empty, ErrorState, Loading } from '../components/States.jsx';
import ArtBackdrop from '../components/ArtBackdrop.jsx';
import { AMBIENT_ART } from '../art.js';
import ExplainerArticle from '../components/ExplainerArticle.jsx';
import { SubgroupPage } from '../components/SubgroupPage.jsx';
import GroupCards from '../components/GroupCards.jsx';
import { articleFor } from '../subgroup.js';
import { EXPLORE_KICKER, groupSanskrit } from '../sanskrit.js';

const PAGE_SIZE = 24;
// Maps draw lazily, so the India in Maps group loads every card (100 per request, the API maximum).
const MAP_CATEGORY = 'india-in-maps';
const MAP_PAGE_SIZE = 100;
const FILTER_KEYS = ['q', 'category', 'subgroup', 'live', 'chart', 'sort'];

const toSlug = value => String(value || '').toLowerCase().replace(/&/g, ' ').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

function resolveLegacyFilters(categorySlug, subgroupSlug, categories, aliases) {
  const legacyGroupAliases = new Map(Object.entries(aliases.groups).map(([name, target]) => [toSlug(name), target]));
  const legacySubgroupAliases = new Map(Object.entries(aliases.subgroups).map(([key, target]) => {
    const [group, subgroup] = key.split('|');
    return [`${toSlug(group)}|${toSlug(subgroup)}`, target];
  }));
  const target = legacySubgroupAliases.get(`${categorySlug}|${subgroupSlug}`)
    || legacyGroupAliases.get(categorySlug);
  if (!target) return { category: categorySlug, subgroup: subgroupSlug };
  const category = categories.find(item => item.slug === toSlug(target.group));
  if (!category) return { category: categorySlug, subgroup: subgroupSlug };
  const subgroup = target.subgroup
    ? category.subgroups.find(item => item.slug === toSlug(target.subgroup))
    : null;
  return { category: category.slug, subgroup: subgroup?.slug || '' };
}

function ExploreBrowse() {
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

  useEffect(() => {
    if (!categories.data || !filters.category) return undefined;
    const currentCategory = categories.data.find(item => item.slug === filters.category);
    const currentSubgroup = currentCategory?.subgroups.some(item => item.slug === filters.subgroup);
    if (currentCategory && (!filters.subgroup || currentSubgroup)) return undefined;
    let active = true;
    import('../data/legacy-aliases.json').then(({ default: aliases }) => {
      if (!active) return;
      const resolved = resolveLegacyFilters(filters.category, filters.subgroup, categories.data, aliases);
      if (resolved.category === filters.category && resolved.subgroup === filters.subgroup) return;
      const next = new URLSearchParams(params);
      next.set('category', resolved.category);
      if (resolved.subgroup) next.set('subgroup', resolved.subgroup);
      else next.delete('subgroup');
      setParams(next, { replace: true });
    });
    return () => { active = false; };
  }, [categories.data, filters.category, filters.subgroup, params, setParams]);

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
  const showAll = filters.category === MAP_CATEGORY;
  const pageSize = showAll ? MAP_PAGE_SIZE : PAGE_SIZE;
  const first = useAsync(signal => api.indicators({ ...filters, page_size: pageSize }, signal), [filterKey]);
  useEffect(() => {
    if (first.data) setPages({ items: first.data.results, next: first.data.next, count: first.data.count, page: 1, key: filterKey });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [first.data]);

  const [shown, sentinel, windowDone] = useBatchedCount(pages.items.length, filterKey);

  const loadMore = async () => {
    setLoadingMore(true);
    setMoreError(null);
    try {
      const data = await api.indicators({ ...filters, page_size: pageSize, page: pages.page + 1 });
      setPages(current => ({ ...current, items: [...current.items, ...data.results], next: data.next, count: data.count, page: current.page + 1 }));
    } catch (error) {
      setMoreError(error);
    } finally {
      setLoadingMore(false);
    }
  };
  useEffect(() => {
    if (showAll && pages.key === filterKey && pages.next && !loadingMore && !moreError) loadMore();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showAll, pages.key, pages.next, loadingMore, moreError]);

  const heroArt = useMemo(() => {
    if (subgroup) return subgroup.art || category?.art || AMBIENT_ART;
    if (category) return [...new Set([category.art, ...category.subgroups.map(item => item.art)].filter(Boolean))];
    return AMBIENT_ART;
  }, [category, subgroup]);
  const activeFilters = FILTER_KEYS.filter(key => filters[key] && key !== 'sort').length;

  return (
    <>
      <section className="page-hero with-art">
        <ArtBackdrop art={heroArt} />
        <p className="eyebrow">{category ? 'Group' : 'Explore'}<span className="sa-kicker" lang="sa" aria-hidden="true">{category ? groupSanskrit(category.slug) : EXPLORE_KICKER}</span></p>
        <h1>{subgroup?.title || category?.title || 'Every indicator, one search away.'}</h1>
        <p className="lead">{subgroup?.description || category?.description || 'Filter by group and subgroup, search any keyword, then open an indicator for the full chart, data table and downloads.'}</p>
      </section>

      {category && <ExplainerArticle category={category} subgroup={subgroup} indicators={first.data?.results || []} />}
      {category?.slug === 'elections-democracy' && <p className="subgroup-callout">Looking for results by place? Open the <Link to="/elections">State and Union Territory election map</Link> for Lok Sabha and Assembly histories.</p>}

      <section className="explore-browse" aria-label="Browse">
        <div className="explore-browse-head">
          <h2>{category ? `Inside ${category.name}` : 'Browse by group'}</h2>
          <span className="muted">{category ? `${category.subgroups.length} subgroups` : `${(categories.data || []).length} groups`}</span>
        </div>
        {category ? (
          <div className="explore-grid" role="list" aria-label="Subgroups">
            <button type="button" role="listitem" className="explore-tile explore-tile-back" onClick={() => update({ category: '', subgroup: '' })}>
              <span className="explore-tile-name">← All groups</span>
              <span className="explore-tile-meta">Back to every group</span>
            </button>
            {category.subgroups.map(item => {
              const info = articleFor(category.name, item.name).subgroup;
              return (
                <Link
                  role="listitem"
                  key={item.slug}
                  to={`/explore/${category.slug}/${item.slug}`}
                  className="explore-tile explore-article-card"
                  style={{ '--card-art': `url(${import.meta.env.BASE_URL}art/${item.art || category.art})` }}
                >
                  <span className="explore-tile-count">{item.indicator_count}</span>
                  <span className="explore-tile-name">{item.name}</span>
                  {item.description && <span className="explore-tile-dek">{item.description}</span>}
                  <span className="explore-tile-meta">{item.indicator_count} charts · {info?.format === 'map' ? 'Map + articles' : 'Long-form article'}</span>
                </Link>
              );
            })}
          </div>
        ) : (categories.data || []).length > 0 && <GroupCards categories={categories.data} />}
      </section>

      <section className="filters" aria-label="Filters">
        <div className="filter-row">
          <label className="search">
            <span className="sr-only">Search indicators</span>
            <input
              type="search"
              placeholder="Search e.g. coal, GDP, Lok Sabha, tourism"
              value={query}
              onChange={event => setQuery(event.target.value)}
            />
          </label>
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
        <p className="filter-summary muted">
          {first.loading ? 'Counting…' : `${pages.count.toLocaleString('en-IN')} indicator${pages.count === 1 ? '' : 's'}`}
          {category ? ` in ${subgroup?.name || category.name}` : ' across every group'}
        </p>
      </section>

      <section className="section" aria-live="polite">
        {first.loading && <Loading label="Finding indicators…" />}
        {first.error && <ErrorState error={first.error} onRetry={first.reload} />}
        {!first.loading && !first.error && (
          <>
            {pages.items.length === 0 ? <Empty>No indicators match. Try a broader search.</Empty> : (
              <div className="card-grid">
                {pages.items.slice(0, shown).map(indicator => <IndicatorCard key={indicator.key} indicator={indicator} />)}
                {!windowDone && <div ref={sentinel} className="card-sentinel" aria-hidden="true" />}
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

// A group + subgroup URL opens that subgroup's article (or map selector); everything else is the browser above.
export default function Explore() {
  const [params] = useSearchParams();
  const categories = useAsync(signal => api.categories(signal), []);
  const categorySlug = params.get('category') || '';
  const subgroupSlug = params.get('subgroup') || '';
  if (categorySlug && subgroupSlug && categories.loading) return <Loading label="Loading the article…" />;
  const category = (categories.data || []).find(item => item.slug === categorySlug);
  if (category?.subgroups.some(item => item.slug === subgroupSlug)) return <SubgroupPage categorySlug={categorySlug} subgroupSlug={subgroupSlug} />;
  return <ExploreBrowse />;
}
