import { useMemo } from 'react';
import { Link, useLocation, useParams, useSearchParams } from 'react-router-dom';
import { useAsync } from '../hooks.js';
import { api } from '../api.js';
import { slugify } from '../subgroup.js';
import './Breadcrumbs.css';

export default function Breadcrumbs() {
  const location = useLocation();
  const params = useParams();
  const [searchParams] = useSearchParams();
  const categoriesAsync = useAsync(signal => api.categories(signal), []);

  const crumbs = useMemo(() => {
    const pathname = location.pathname;
    if (pathname === '/' || pathname === '') {
      return [];
    }

    // Subgroup page, region page, and indicator detail have their own dedicated integrated crumbs/back navigation
    if (pathname.startsWith('/explore/') || pathname.startsWith('/indicator/')) {
      return [];
    }

    const items = [
      { label: 'Home', to: '/' }
    ];

    const categoryParam = params.group || searchParams.get('category');
    const subgroupParam = params.subgroup || searchParams.get('subgroup');
    const stateParam = params.stateSlug;

    const allCategories = categoriesAsync.data || [];
    const matchedCategory = categoryParam
      ? allCategories.find(c => c.slug === categoryParam || slugify(c.slug) === slugify(categoryParam) || slugify(c.name) === slugify(categoryParam))
      : null;

    const matchedSubgroup = (matchedCategory && subgroupParam)
      ? matchedCategory.subgroups?.find(s => s.slug === subgroupParam || slugify(s.slug) === slugify(subgroupParam) || slugify(s.name) === slugify(subgroupParam))
      : null;

    if (pathname.startsWith('/explore')) {
      items.push({ label: 'Explore', to: '/explore' });

      if (matchedCategory) {
        items.push({
          label: matchedCategory.name,
          to: `/explore?category=${matchedCategory.slug}`
        });

        if (matchedSubgroup) {
          items.push({
            label: matchedSubgroup.name,
            to: `/explore/${matchedCategory.slug}/${matchedSubgroup.slug}`
          });

          if (stateParam) {
            const formattedState = stateParam
              .split('-')
              .map(word => word.charAt(0).toUpperCase() + word.slice(1))
              .join(' ');
            items.push({
              label: formattedState,
              to: `/explore/${matchedCategory.slug}/${matchedSubgroup.slug}/${stateParam}`
            });
          }
        }
      }
    } else if (pathname.startsWith('/indicator/')) {
      items.push({ label: 'Explore', to: '/explore' });
      const indicatorKey = pathname.replace('/indicator/', '');
      items.push({ label: indicatorKey.replace(/_/g, ' '), to: pathname });
    } else if (pathname === '/articles' || pathname.startsWith('/articles/')) {
      items.push({ label: 'Articles & Reports', to: '/articles' });
    } else if (pathname === '/sources') {
      items.push({ label: 'Data Sources & Methodology', to: '/sources' });
    } else if (pathname === '/compare') {
      items.push({ label: 'Compare Time Series', to: '/compare' });
    } else if (pathname === '/about') {
      items.push({ label: 'About Project', to: '/about' });
    } else if (pathname === '/api') {
      items.push({ label: 'OpenAPI & Architecture', to: '/api' });
    } else if (pathname === '/elections') {
      items.push({ label: 'Elections & Democracy', to: '/elections' });
    } else if (pathname === '/ivc-translator') {
      items.push({ label: 'Explore', to: '/explore' });
      items.push({ label: 'Indus Valley Civilisation', to: '/explore?category=indus-valley-civilisation' });
      items.push({ label: 'Computational Script Decryption', to: '/ivc-translator' });
    } else {
      const segment = pathname.replace(/^\//, '').replace(/\/$/, '');
      const prettyLabel = segment.charAt(0).toUpperCase() + segment.slice(1);
      items.push({ label: prettyLabel, to: pathname });
    }

    return items;
  }, [location.pathname, location.search, params, searchParams, categoriesAsync.data]);

  if (!crumbs.length || crumbs.length === 1) {
    return null;
  }

  return (
    <nav className="breadcrumbs-nav" aria-label="Breadcrumb">
      <div className="breadcrumbs-inner">
        <ol className="breadcrumbs-list">
          {crumbs.map((crumb, idx) => {
            const isLast = idx === crumbs.length - 1;
            return (
              <li key={idx} className="breadcrumbs-item">
                {idx > 0 && (
                  <span className="breadcrumbs-separator" aria-hidden="true">
                    ›
                  </span>
                )}
                {isLast ? (
                  <span className="breadcrumbs-current" aria-current="page">
                    {crumb.label}
                  </span>
                ) : (
                  <Link to={crumb.to} className="breadcrumbs-link">
                    {crumb.label}
                  </Link>
                )}
              </li>
            );
          })}
        </ol>
      </div>
    </nav>
  );
}
