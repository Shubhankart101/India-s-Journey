import { useState, useMemo, useEffect } from 'react';
import sitesData from '../data/indus-civilisation.json';
import './IndusAtlas.css';

const CATEGORY_COLORS = {
  metropolis: '#d4a72c',
  port: '#38bdf8',
  craft: '#fb923c',
  outpost: '#4ade80',
  foreign: '#f43f5e'
};

const CATEGORY_LABELS = {
  all: 'All Sites (23)',
  metropolis: 'Metropolises (5)',
  port: 'Coastal & Ports (4)',
  craft: 'Craft & Mining (5)',
  outpost: 'Inland Strongholds (5)',
  foreign: 'Foreign Trade Hubs (4)'
};

// Projected bounding box for world-asia.json (covers Mesopotamia to Northwest India)
const VIEWBOX = { x: 420, y: -435, w: 375, h: 255 };

export default function IndusValleyAtlas() {
  const [mapPaths, setMapPaths] = useState([]);
  const [selectedSiteId, setSelectedSiteId] = useState('mohenjo-daro');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [countryFilter, setCountryFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showRoutes, setShowRoutes] = useState(true);

  useEffect(() => {
    fetch('/maps/world-asia.json')
      .then(res => res.json())
      .then(data => {
        if (data && data.paths) {
          // Focus on countries surrounding the Indus & trade sphere
          const targetIsos = new Set(['IND', 'PAK', 'AFG', 'IRQ', 'IRN', 'OMN', 'KWT', 'ARE', 'SAU', 'QAT', 'BHR', 'TKM', 'UZB', 'TJK', 'SYR']);
          const relevant = data.paths.filter(p => targetIsos.has(p.i));
          setMapPaths(relevant);
        }
      })
      .catch(() => {
        // Fallback gracefully if map path fails to load
      });
  }, []);

  const sites = sitesData.sites || [];
  const tradeRoutes = sitesData.trade_routes || [];

  const filteredSites = useMemo(() => {
    return sites.filter(site => {
      if (categoryFilter !== 'all' && site.category !== categoryFilter) return false;
      if (countryFilter !== 'all' && site.country !== countryFilter) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchName = site.name.toLowerCase().includes(q) || (site.name_hi && site.name_hi.includes(q));
        const matchArtifact = site.key_artifacts.some(a => a.toLowerCase().includes(q));
        const matchStruct = site.key_structures.some(s => s.toLowerCase().includes(q));
        const matchCountry = site.country.toLowerCase().includes(q);
        if (!matchName && !matchArtifact && !matchStruct && !matchCountry) return false;
      }
      return true;
    });
  }, [sites, categoryFilter, countryFilter, searchQuery]);

  const selectedSite = useMemo(() => {
    return sites.find(s => s.id === selectedSiteId) || sites[0];
  }, [sites, selectedSiteId]);

  const countries = useMemo(() => {
    const set = new Set(sites.map(s => s.country));
    return ['all', ...Array.from(set)];
  }, [sites]);

  return (
    <div className="indus-atlas">
      {/* Top Banner / Stats */}
      <header className="indus-atlas-header">
        <div className="indus-atlas-title-group">
          <span className="indus-atlas-tag">HARAPPAN GEOGRAPHY & ARCHEOLOGY</span>
          <h2>The Indus Valley Civilisation Interactive Atlas</h2>
          <p className="indus-atlas-lead">
            Explore 23 major excavated metropolises, dockyards, bead-making factories, and overseas trade colonies
            across ancient Meluhha, Dilmun, Magan, and Mesopotamia (c. 3300 BCE – 1300 BCE).
          </p>
        </div>

        <div className="indus-stats-grid">
          <div className="indus-stat-card">
            <span className="indus-stat-num">23</span>
            <span className="indus-stat-label">Mapped Centers</span>
          </div>
          <div className="indus-stat-card">
            <span className="indus-stat-num">7</span>
            <span className="indus-stat-label">Modern Nations</span>
          </div>
          <div className="indus-stat-card">
            <span className="indus-stat-num">1.5M</span>
            <span className="indus-stat-label">km² Extent</span>
          </div>
          <div className="indus-stat-card">
            <span className="indus-stat-num">4,000+</span>
            <span className="indus-stat-label">Seals & Inscriptions</span>
          </div>
        </div>
      </header>

      {/* Filter Controls Bar */}
      <div className="indus-controls">
        <div className="indus-search-wrap">
          <input
            type="search"
            placeholder="Search site, artifact (e.g. dancing girl, lapis, seal)..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="indus-search-input"
            aria-label="Search Indus Valley sites or artifacts"
          />
        </div>

        <div className="indus-filter-group">
          <label htmlFor="cat-filter" className="sr-only">Filter by category</label>
          <select
            id="cat-filter"
            value={categoryFilter}
            onChange={e => setCategoryFilter(e.target.value)}
            className="indus-select"
          >
            {Object.entries(CATEGORY_LABELS).map(([k, label]) => (
              <option key={k} value={k}>{label}</option>
            ))}
          </select>

          <label htmlFor="country-filter" className="sr-only">Filter by country</label>
          <select
            id="country-filter"
            value={countryFilter}
            onChange={e => setCountryFilter(e.target.value)}
            className="indus-select"
          >
            <option value="all">All Countries ({countries.length - 1})</option>
            {countries.filter(c => c !== 'all').map(c => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>

          <button
            type="button"
            className={`indus-toggle-btn ${showRoutes ? 'active' : ''}`}
            onClick={() => setShowRoutes(r => !r)}
            aria-pressed={showRoutes}
          >
            <span className="route-indicator" /> Trade Routes {showRoutes ? 'On' : 'Off'}
          </button>
        </div>
      </div>

      {/* Main Interactive Stage */}
      <div className="indus-atlas-stage">
        {/* SVG Map Canvas */}
        <div className="indus-map-container" role="region" aria-label="Indus Civilisation Interactive Map">
          <svg
            className="indus-map-svg"
            viewBox={`${VIEWBOX.x} ${VIEWBOX.y} ${VIEWBOX.w} ${VIEWBOX.h}`}
            preserveAspectRatio="xMidYMid meet"
          >
            <defs>
              <linearGradient id="maritime-grad" x1="1" y1="1" x2="0" y2="0">
                <stop offset="0%" stopColor="#38bdf8" />
                <stop offset="50%" stopColor="#818cf8" />
                <stop offset="100%" stopColor="#f43f5e" />
              </linearGradient>
              <linearGradient id="lapis-grad" x1="0" y1="1" x2="0" y2="0">
                <stop offset="0%" stopColor="#d4a72c" />
                <stop offset="100%" stopColor="#60a5fa" />
              </linearGradient>
              <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="1.5" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>

            {/* Background Base Map Countries */}
            <g className="indus-country-base">
              {mapPaths.map(p => (
                <path
                  key={p.i}
                  d={p.d}
                  className={`country-poly ${p.i === 'IND' || p.i === 'PAK' ? 'core-indus-poly' : ''}`}
                  title={p.n}
                />
              ))}
            </g>

            {/* Ancient Maritime & Overland Trade Routes */}
            {showRoutes && (
              <g className="indus-trade-routes" aria-label="Ancient Trade Corridors">
                {tradeRoutes.map(route => {
                  const pathStr = route.waypoints
                    .map((pt, i) => `${i === 0 ? 'M' : 'L'}${pt.x} ${pt.y}`)
                    .join(' ');
                  return (
                    <g key={route.id} className="trade-route-group">
                      <path
                        d={pathStr}
                        className={`trade-route-path ${route.type}`}
                        strokeDasharray={route.type === 'maritime' ? '3,2' : '2,2'}
                      />
                    </g>
                  );
                })}
              </g>
            )}

            {/* Site Pins */}
            <g className="indus-site-pins">
              {filteredSites.map(site => {
                const isSelected = site.id === selectedSiteId;
                const pinColor = CATEGORY_COLORS[site.category] || '#d4a72c';
                const r = isSelected ? 4.8 : site.category === 'metropolis' ? 3.8 : 2.8;

                return (
                  <g
                    key={site.id}
                    className={`site-pin-group ${isSelected ? 'selected' : ''} ${site.is_foreign ? 'foreign-site' : ''}`}
                    transform={`translate(${site.x}, ${site.y})`}
                    onClick={() => setSelectedSiteId(site.id)}
                    tabIndex={0}
                    role="button"
                    aria-label={`${site.name}, ${site.country} (${site.category})`}
                    onKeyDown={e => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        setSelectedSiteId(site.id);
                      }
                    }}
                  >
                    {/* Pulsing ring for selected site */}
                    {isSelected && (
                      <circle r={r + 4} className="pin-pulse" stroke={pinColor} />
                    )}

                    <circle
                      r={r}
                      fill={pinColor}
                      stroke="#0f172a"
                      strokeWidth={isSelected ? 1.4 : 0.8}
                      className="pin-circle"
                    />

                    {/* Site label on map */}
                    <text
                      x={r + 2.5}
                      y={1.2}
                      className={`pin-text ${isSelected ? 'pin-text-active' : ''}`}
                      fontSize={isSelected ? '4.2' : site.category === 'metropolis' ? '3.4' : '2.8'}
                    >
                      {site.name}
                    </text>
                  </g>
                );
              })}
            </g>
          </svg>

          {/* Map Legend */}
          <div className="indus-map-legend">
            <span className="legend-title">Site Classification:</span>
            <div className="legend-items">
              <span className="legend-chip"><i style={{ background: CATEGORY_COLORS.metropolis }} /> Metropolis</span>
              <span className="legend-chip"><i style={{ background: CATEGORY_COLORS.port }} /> Port & Dockyard</span>
              <span className="legend-chip"><i style={{ background: CATEGORY_COLORS.craft }} /> Bead / Craft Hub</span>
              <span className="legend-chip"><i style={{ background: CATEGORY_COLORS.outpost }} /> Outpost / Frontier</span>
              <span className="legend-chip"><i style={{ background: CATEGORY_COLORS.foreign }} /> Foreign Trade Hub (Mesopotamia/Gulf)</span>
            </div>
          </div>
        </div>

        {/* Site Detail Inspector Panel */}
        {selectedSite && (
          <aside className="indus-site-inspector" aria-label={`Details of ${selectedSite.name}`}>
            <div className="inspector-badge-row">
              <span className="inspector-badge" style={{ borderColor: CATEGORY_COLORS[selectedSite.category] }}>
                {selectedSite.badge}
              </span>
              <span className="inspector-country">{selectedSite.country} • {selectedSite.region}</span>
            </div>

            <div className="inspector-header">
              <h3 className="inspector-site-name">{selectedSite.name}</h3>
              {selectedSite.name_hi && <p className="inspector-site-hi">{selectedSite.name_hi}</p>}
            </div>

            <p className="inspector-desc">{selectedSite.description}</p>

            <div className="inspector-meta-grid">
              <div className="meta-box">
                <span className="meta-k">Estimated Area</span>
                <span className="meta-v">{selectedSite.area_hectares ? `${selectedSite.area_hectares} ha` : 'Trade Enclave'}</span>
              </div>
              <div className="meta-box">
                <span className="meta-k">Chronology</span>
                <span className="meta-v">{selectedSite.period}</span>
              </div>
              <div className="meta-box">
                <span className="meta-k">Discovery & Excavation</span>
                <span className="meta-v">{selectedSite.discovered_by}</span>
              </div>
              <div className="meta-box">
                <span className="meta-k">Inscriptions Found</span>
                <span className="meta-v">{selectedSite.sign_count ? `${selectedSite.sign_count}+ seals` : 'Epigraphic Trade Links'}</span>
              </div>
            </div>

            {/* Key Structures */}
            <div className="inspector-section">
              <h4>Monumental Structures</h4>
              <ul className="inspector-list">
                {selectedSite.key_structures.map((s, idx) => (
                  <li key={idx}><strong>{s}</strong></li>
                ))}
              </ul>
            </div>

            {/* Key Artifacts */}
            <div className="inspector-section">
              <h4>Key Excavated Artifacts</h4>
              <div className="artifacts-tag-list">
                {selectedSite.key_artifacts.map((a, idx) => (
                  <span key={idx} className="artifact-tag">{a}</span>
                ))}
              </div>
            </div>

            {/* Foreign Trade Connection */}
            {selectedSite.foreign_connection && (
              <div className="inspector-section foreign-box">
                <h4>International Artifact & Trade Links</h4>
                <p>{selectedSite.foreign_connection}</p>
              </div>
            )}
          </aside>
        )}
      </div>

      {/* Sites Quick Grid Selector */}
      <footer className="indus-site-selector-strip">
        <span className="strip-heading">Browse All 23 Excavated Centers ({filteredSites.length} shown):</span>
        <div className="site-pills-row">
          {filteredSites.map(s => (
            <button
              key={s.id}
              type="button"
              className={`site-pill-btn ${s.id === selectedSiteId ? 'active' : ''}`}
              onClick={() => setSelectedSiteId(s.id)}
            >
              <i style={{ background: CATEGORY_COLORS[s.category] || '#d4a72c' }} />
              <span>{s.name}</span>
            </button>
          ))}
        </div>
      </footer>
    </div>
  );
}
