import { memo, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useInView } from '../hooks.js';
import { groupSanskrit } from '../sanskrit.js';
import { assetUrl } from '../config.js';

const MAP_SLUG = 'india-in-maps';
const MAP_CHIPS = ['36 states & UTs', '17 Metro Networks', 'Lok Sabha 1952–2024', 'Primary ECI data'];

const slugOf = cat => cat?.slug || String(cat?.name || '').normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

let outlinePromise = null;
export const loadOutline = () => {
  outlinePromise = outlinePromise || fetch(import.meta.env.BASE_URL + 'maps/india-states.json').then(response => {
    if (!response.ok) throw new Error(`Map outline unavailable (HTTP ${response.status})`);
    return response.json();
  }).catch(error => {
    outlinePromise = null;
    throw error;
  });
  return outlinePromise;
};

// A line-drawn India: the state outlines, fetched only once the card is close to the viewport.
function IndiaOutline() {
  const [ref, inView] = useInView('200px');
  const [geometry, setGeometry] = useState(null);
  useEffect(() => {
    if (!inView) return undefined;
    let live = true;
    loadOutline().then(data => live && setGeometry(data)).catch(() => {});
    return () => { live = false; };
  }, [inView]);
  return (
    <span className="group-card-map" ref={ref} aria-hidden="true">
      {geometry && (
        <svg viewBox={geometry.viewBox} focusable="false">
          {Object.entries(geometry.states).map(([name, d]) => <path key={name} d={d} />)}
        </svg>
      )}
    </span>
  );
}

const GroupCard = memo(function GroupCard({ category, to, cta }) {
  const slug = slugOf(category);
  const featured = slug === MAP_SLUG;
  const sanskrit = groupSanskrit(slug);
  const kicker = `${(category.subgroups || []).length} subgroups`;
  const rawArt = (category.art || 'parliament.svg').split('?')[0];
  return (
    <Link to={to} className={`group-card${featured ? ' featured' : ''}`}>
      {featured ? <IndiaOutline /> : (
        <span className="group-card-art" aria-hidden="true">
          <img src={assetUrl(`art/${rawArt}`)} alt="" loading="lazy" decoding="async" width="72" height="72" />
        </span>
      )}
      <div className="group-card-body">
        <span className="group-card-kicker">{sanskrit && <span className="sa-kicker" lang="sa" aria-hidden="true">{sanskrit}</span>}{kicker}</span>
        <h3 className="group-card-title">{category.name}</h3>
        <p className="group-card-dek clamp-2">{category.description}</p>
        <span className="group-card-link">{cta} <span aria-hidden="true">→</span></span>
      </div>
      {featured && (
        <ul className="group-card-chips" aria-label="About India in Maps">
          {MAP_CHIPS.map(chip => <li key={chip}>{chip}</li>)}
        </ul>
      )}
    </Link>
  );
});

// Editorial "browse by group" grid shared by Home; the featured map card spans the full row.
export default function GroupCards({ categories = [], cta = 'Explore' }) {
  const ordered = [...categories.filter(item => slugOf(item) === MAP_SLUG), ...categories.filter(item => slugOf(item) !== MAP_SLUG)];
  return (
    <div className="group-cards">
      {ordered.map(category => {
        const slug = slugOf(category);
        const singleSubgroup = category.subgroups?.length === 1 ? category.subgroups[0] : null;
        const targetUrl = slug === 'elections-democracy'
          ? '/elections'
          : (singleSubgroup ? `/explore/${slug}/${singleSubgroup.slug}` : `/explore?category=${slug}`);
        return (
          <GroupCard
            key={slug || category.name}
            category={{ ...category, slug }}
            cta={cta}
            to={targetUrl}
          />
        );
      })}
    </div>
  );
}
