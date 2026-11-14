import { useState, useMemo, useEffect } from 'react';
import sitesData from '../data/indus-civilisation.json';
import './IndusAtlas.css';

const CATEGORY_COLORS = {
  metropolis: '#d4a72c',
  port: '#38bdf8',
  craft: '#fb923c',
  fortified_town: '#a855f7',
  agricultural_rural: '#4ade80',
  frontier_outpost: '#f59e0b',
  foreign_trade: '#f43f5e'
};

const CATEGORY_LABELS = {
  all: 'All Excavated Sites (49)',
  metropolis: 'Major Metropolises',
  port: 'Ports & Tidal Harbors',
  craft: 'Craft & Industrial Hubs',
  fortified_town: 'Fortified Towns & Bastions',
  agricultural_rural: 'Agricultural Settlements',
  frontier_outpost: 'Frontier Border Outposts',
  foreign_trade: 'Overseas Trade Enclaves (Mesopotamia / Gulf)'
};

// Projected bounding box for world-asia.json (covers Mesopotamia to Northwest India)
const VIEWBOX = { x: 410, y: -460, w: 410, h: 285 };

export default function IndusValleyAtlas() {
  const [mapPaths, setMapPaths] = useState([]);
  const [selectedSiteId, setSelectedSiteId] = useState('rakhigarhi');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [countryFilter, setCountryFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showRoutes, setShowRoutes] = useState(true);

  useEffect(() => {
    fetch('/maps/world-asia.json')
      .then(res => res.json())
      .then(data => {
        if (data && data.paths) {
          // Focus on countries surrounding the Indus & international trade sphere
          const targetIsos = new Set(['IND', 'PAK', 'AFG', 'IRQ', 'IRN', 'OMN', 'KWT', 'ARE', 'SAU', 'QAT', 'BHR', 'TKM', 'UZB', 'TJK', 'SYR']);
          const relevant = data.paths.filter(p => targetIsos.has(p.i));
          setMapPaths(relevant);
        }
      })
      .catch(() => {});
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
        const matchCountry = site.country.toLowerCase().includes(q) || (site.state_or_province && site.state_or_province.toLowerCase().includes(q));
        const matchExcavator = site.excavators && site.excavators.toLowerCase().includes(q);
        const matchSource = site.official_sources && site.official_sources.some(src => (src.title + src.authors + (src.publisher || '')).toLowerCase().includes(q));
        if (!matchName && !matchArtifact && !matchStruct && !matchCountry && !matchExcavator && !matchSource) return false;
      }
      return true;
    });
  }, [sites, categoryFilter, countryFilter, searchQuery]);

  const selectedSite = useMemo(() => {
    return sites.find(s => s.id === selectedSiteId) || sites[0];
  }, [sites, selectedSiteId]);

  const countries = useMemo(() => {
    const set = new Set(sites.map(s => s.country));
    return ['all', ...Array.from(set).sort()];
  }, [sites]);

  return (
    <div className="indus-atlas">
      {/* Top Banner & Stats */}
      <header className="indus-atlas-header">
        <div className="indus-atlas-title-group">
          <span className="indus-atlas-tag">OFFICIAL ARCHEOLOGICAL & EXCAVATION SURVEY ATLAS</span>
          <h2>The Indus Valley Civilisation Comprehensive Excavation Map</h2>
          <p className="indus-atlas-lead">
            Explore 49 comprehensively cataloged major and minor archeological excavations, rural farmsteads,
            tidal dockyards, border bastions, and international trading enclaves across India, Pakistan, Afghanistan,
            Iraq, Iran, Kuwait, Oman, Bahrain, and the UAE. Every single site includes verified official academic sources,
            excavation memoirs, and research papers.
          </p>
        </div>

        <div className="indus-stats-grid">
          <div className="indus-stat-card">
            <span className="indus-stat-num">{sites.length}</span>
            <span className="indus-stat-label">Cataloged Sites</span>
          </div>
          <div className="indus-stat-card">
            <span className="indus-stat-num">9</span>
            <span className="indus-stat-label">Modern Nations</span>
          </div>
          <div className="indus-stat-card">
            <span className="indus-stat-num">1.5M</span>
            <span className="indus-stat-label">km² Extent</span>
          </div>
          <div className="indus-stat-card">
            <span className="indus-stat-num">100%</span>
            <span className="indus-stat-label">Official Sources</span>
          </div>
        </div>
      </header>

      {/* Filter & Search Bar */}
      <div className="indus-controls">
        <div className="indus-search-wrap">
          <input
            type="search"
            placeholder="Search site, artifact, excavator, or research paper (e.g. Rakhigarhi, Lothal, Cell, Shinde, Bisht)..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="indus-search-input"
            aria-label="Search Indus Valley excavations, artifacts, or sources"
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
            <option value="all">All Nations ({countries.length - 1})</option>
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
            <span className="route-indicator" /> Trade Corridors {showRoutes ? 'On' : 'Off'}
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
            {/* Background Country Polygons */}
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

            {/* Ancient Trade Routes */}
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
                const r = isSelected ? 4.5 : site.category === 'metropolis' ? 3.6 : 2.4;

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
                    {isSelected && (
                      <circle r={r + 3.8} className="pin-pulse" stroke={pinColor} />
                    )}

                    <circle
                      r={r}
                      fill={pinColor}
                      stroke="#0f172a"
                      strokeWidth={isSelected ? 1.2 : 0.6}
                      className="pin-circle"
                    />

                    {/* Site Label on Map */}
                    <text
                      x={r + 2.2}
                      y={1.1}
                      className={`pin-text ${isSelected ? 'pin-text-active' : ''}`}
                      fontSize={isSelected ? '3.8' : site.category === 'metropolis' ? '3.0' : '2.3'}
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
              <span className="legend-chip"><i style={{ background: CATEGORY_COLORS.port }} /> Port & Dock</span>
              <span className="legend-chip"><i style={{ background: CATEGORY_COLORS.craft }} /> Craft / Bead Hub</span>
              <span className="legend-chip"><i style={{ background: CATEGORY_COLORS.fortified_town }} /> Fortified Town</span>
              <span className="legend-chip"><i style={{ background: CATEGORY_COLORS.agricultural_rural }} /> Rural Farmstead</span>
              <span className="legend-chip"><i style={{ background: CATEGORY_COLORS.frontier_outpost }} /> Frontier Outpost</span>
              <span className="legend-chip"><i style={{ background: CATEGORY_COLORS.foreign_trade }} /> Overseas Trade Hub</span>
            </div>
          </div>
        </div>

        {/* Site Inspector Drawer */}
        {selectedSite && (
          <aside className="indus-site-inspector" aria-label={`Details of ${selectedSite.name}`}>
            <div className="inspector-badge-row">
              <span className="inspector-badge" style={{ borderColor: CATEGORY_COLORS[selectedSite.category] }}>
                {selectedSite.badge}
              </span>
              <span className="inspector-country">
                {selectedSite.country} • {selectedSite.state_or_province}
              </span>
            </div>

            <div className="inspector-header">
              <h3 className="inspector-site-name">{selectedSite.name}</h3>
              {selectedSite.name_hi && <p className="inspector-site-hi">{selectedSite.name_hi}</p>}
            </div>

            <p className="inspector-desc">{selectedSite.description}</p>

            <div className="inspector-meta-grid">
              <div className="meta-box">
                <span className="meta-k">Estimated Area</span>
                <span className="meta-v">{selectedSite.area_hectares ? `${selectedSite.area_hectares} ha` : 'Trade Station'}</span>
              </div>
              <div className="meta-box">
                <span className="meta-k">Chronology</span>
                <span className="meta-v">{selectedSite.period}</span>
              </div>
              <div className="meta-box full-span">
                <span className="meta-k">Excavators & Archaeological Missions</span>
                <span className="meta-v">{selectedSite.excavators}</span>
              </div>
            </div>

            {/* Monumental Structures */}
            <div className="inspector-section">
              <h4>Excavated Architectural Structures</h4>
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

            {/* OFFICIAL SOURCES & CITATIONS (Academic / ASI / Peer-reviewed) */}
            <div className="inspector-section official-sources-panel">
              <h4>Official Excavation Sources & Academic Research Papers</h4>
              <div className="sources-citation-list">
                {selectedSite.official_sources && selectedSite.official_sources.map((src, idx) => (
                  <div key={idx} className="source-citation-card">
                    <span className="citation-type">{src.type}</span>
                    <h5 className="citation-title">
                      {src.url ? (
                        <a href={src.url} target="_blank" rel="noopener noreferrer">
                          "{src.title}" ↗
                        </a>
                      ) : (
                        `"${src.title}"`
                      )}
                    </h5>
                    <p className="citation-authors">
                      <strong>Author(s):</strong> {src.authors} ({src.year})
                    </p>
                    <p className="citation-pub">
                      <strong>Publication:</strong> {src.publisher}{src.volume ? `, ${src.volume}` : ''}{src.pages ? `, pp. ${src.pages}` : ''}
                    </p>
                    {src.doi && (
                      <p className="citation-doi">
                        <strong>DOI:</strong> <a href={`https://doi.org/${src.doi}`} target="_blank" rel="noopener noreferrer">{src.doi}</a>
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </aside>
        )}
      </div>

      {/* Sites Quick Grid Selector */}
      <footer className="indus-site-selector-strip">
        <span className="strip-heading">Browse All Excavated Sites ({filteredSites.length} of {sites.length} shown):</span>
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
