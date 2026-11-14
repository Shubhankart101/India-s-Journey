import { useState, useMemo, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import sitesData from '../data/indus-civilisation.json';
import './IndusAtlas.css';

const TIER_FILTERS = [
  { id: 'all', label: 'All 49 Sites', icon: '🗺️' },
  { id: 'metropolis', label: '8 Major Metropolises', icon: '🏛️' },
  { id: 'port', label: 'Ports & Harbors', icon: '⚓' },
  { id: 'craft', label: 'Craft & Metallurgy', icon: '🏺' },
  { id: 'foreign_trade', label: 'Overseas Trade (Gulf / Mesopotamia)', icon: '🌍' },
  { id: 'fortified_town', label: 'Fortified Citadels', icon: '🏰' }
];

const REGION_PRESETS = [
  { id: 'full', label: 'Pan-Indus & Gulf', vb: { x: 410, y: -460, w: 410, h: 285 } },
  { id: 'heartland', label: 'Indus-Saraswati Heartland', vb: { x: 570, y: -420, w: 180, h: 160 } },
  { id: 'gujarat', label: 'Gujarat, Kutch & Saurashtra', vb: { x: 620, y: -330, w: 120, h: 110 } },
  { id: 'gulf', label: 'Persian Gulf & Mesopotamia', vb: { x: 410, y: -440, w: 200, h: 170 } }
];

const CATEGORY_COLORS = {
  metropolis: '#d4a72c',
  port: '#38bdf8',
  craft: '#fb923c',
  fortified_town: '#a855f7',
  agricultural_rural: '#4ade80',
  frontier_outpost: '#f59e0b',
  foreign_trade: '#f43f5e'
};

export default function IndusValleyAtlas() {
  const [mapPaths, setMapPaths] = useState([]);
  const [selectedSiteId, setSelectedSiteId] = useState('rakhigarhi');
  const [tierFilter, setTierFilter] = useState('all');
  const [countryFilter, setCountryFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showRoutes, setShowRoutes] = useState(true);
  const [hoveredSiteId, setHoveredSiteId] = useState(null);

  // Zoom & Pan state
  const [viewBox, setViewBox] = useState(REGION_PRESETS[0].vb);
  const [activeRegion, setActiveRegion] = useState('full');

  useEffect(() => {
    fetch('/maps/world-asia.json')
      .then(res => res.json())
      .then(data => {
        if (data && data.paths) {
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
      if (tierFilter !== 'all' && site.category !== tierFilter) return false;
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
  }, [sites, tierFilter, countryFilter, searchQuery]);

  const selectedSite = useMemo(() => {
    return sites.find(s => s.id === selectedSiteId) || sites[0];
  }, [sites, selectedSiteId]);

  const countries = useMemo(() => {
    const set = new Set(sites.map(s => s.country));
    return ['all', ...Array.from(set).sort()];
  }, [sites]);

  const handleRegionChange = (preset) => {
    setActiveRegion(preset.id);
    setViewBox(preset.vb);
  };

  const handleZoom = (factor) => {
    setViewBox(curr => {
      const nw = Math.max(80, Math.min(500, curr.w * factor));
      const nh = Math.max(60, Math.min(350, curr.h * factor));
      const nx = curr.x + (curr.w - nw) / 2;
      const ny = curr.y + (curr.h - nh) / 2;
      return { x: nx, y: ny, w: nw, h: nh };
    });
  };

  return (
    <div className="indus-atlas">
      {/* Header & Meta */}
      <header className="indus-atlas-header">
        <div className="indus-atlas-title-group">
          <span className="indus-atlas-tag">OFFICIAL ASI & PEER-REVIEWED ARCHAEOLOGICAL ATLAS</span>
          <h2>The Indus Valley Civilisation Comprehensive Excavation Map</h2>
          <p className="indus-atlas-lead">
            49 cataloged excavations across 9 countries with exact GPS coordinates, excavated structures,
            material culture, and peer-reviewed monograph citations from the Archaeological Survey of India (ASI),
            Nature, Cell, and the French National Centre for Scientific Research (CNRS).
          </p>
        </div>

        {/* Global Stats Counter */}
        <div className="indus-stats-counter">
          <div className="indus-stat-chip">
            <span className="isc-num">49</span>
            <span className="isc-label">Excavated Sites</span>
          </div>
          <div className="indus-stat-chip">
            <span className="isc-num">9</span>
            <span className="isc-label">Modern Nations</span>
          </div>
          <div className="indus-stat-chip">
            <span className="isc-num">3,500+</span>
            <span className="isc-label">BCE to 1300 BCE</span>
          </div>
          <div className="indus-stat-chip">
            <span className="isc-num">100%</span>
            <span className="isc-label">Official Scholarly Sources</span>
          </div>
        </div>
      </header>

      {/* Tier Filter Tabs (Prevents visual clutter) */}
      <div className="indus-tier-tabs" role="tablist" aria-label="Excavation site hierarchy">
        {TIER_FILTERS.map(tab => (
          <button
            key={tab.id}
            type="button"
            role="tab"
            aria-selected={tierFilter === tab.id}
            className={`indus-tier-tab ${tierFilter === tab.id ? 'active' : ''}`}
            onClick={() => setTierFilter(tab.id)}
          >
            <span className="tab-icon" aria-hidden="true">{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Secondary Controls Bar */}
      <div className="indus-controls-bar">
        {/* Search */}
        <div className="indus-search-wrap">
          <input
            type="search"
            placeholder="Search site, artifact, excavator, or paper (e.g. Dancing Girl, Dholavira, Marshall)..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="indus-search-input"
          />
          {searchQuery && (
            <button type="button" className="indus-clear-btn" onClick={() => setSearchQuery('')}>×</button>
          )}
        </div>

        {/* Country filter */}
        <div className="indus-select-wrap">
          <label htmlFor="country-filter">Country:</label>
          <select
            id="country-filter"
            value={countryFilter}
            onChange={e => setCountryFilter(e.target.value)}
            className="indus-select"
          >
            <option value="all">All 9 Countries</option>
            {countries.filter(c => c !== 'all').map(c => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>

        {/* Region focus presets */}
        <div className="indus-region-presets" role="group" aria-label="Map Region View">
          <span className="preset-label">Region:</span>
          {REGION_PRESETS.map(preset => (
            <button
              key={preset.id}
              type="button"
              className={`preset-btn ${activeRegion === preset.id ? 'active' : ''}`}
              onClick={() => handleRegionChange(preset)}
            >
              {preset.label}
            </button>
          ))}
        </div>

        {/* Toggle Trade Routes */}
        <label className="indus-toggle-label">
          <input
            type="checkbox"
            checked={showRoutes}
            onChange={e => setShowRoutes(e.target.checked)}
          />
          <span>Show Maritime & Silk Trade Routes</span>
        </label>
      </div>

      {/* Main Atlas Content: Map Viewport + Rich Excavation Detail Drawer */}
      <div className="indus-workbench">
        {/* Map Canvas with SVG Vector Basemap */}
        <div className="indus-map-canvas">
          {/* Zoom floating buttons */}
          <div className="indus-zoom-controls" aria-label="Map zoom controls">
            <button type="button" onClick={() => handleZoom(0.8)} title="Zoom In" aria-label="Zoom in">+</button>
            <button type="button" onClick={() => handleZoom(1.25)} title="Zoom Out" aria-label="Zoom out">−</button>
            <button type="button" onClick={() => handleRegionChange(REGION_PRESETS[0])} title="Reset View" aria-label="Reset view">⟲</button>
          </div>

          <svg
            className="indus-svg"
            viewBox={`${viewBox.x} ${viewBox.y} ${viewBox.w} ${viewBox.h}`}
            preserveAspectRatio="xMidYMid meet"
          >
            <defs>
              <radialGradient id="metropolisGlow" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="#d4a72c" stopOpacity="0.8" />
                <stop offset="60%" stopColor="#d4a72c" stopOpacity="0.25" />
                <stop offset="100%" stopColor="#d4a72c" stopOpacity="0" />
              </radialGradient>
              <filter id="siteShadow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="1.5" stdDeviation="1.5" floodColor="#000" floodOpacity="0.6" />
              </filter>
            </defs>

            {/* Geographical Background */}
            <rect x={viewBox.x - 200} y={viewBox.y - 200} width={viewBox.w + 400} height={viewBox.h + 400} fill="#0d1117" />

            {/* Country boundary polygons */}
            <g className="indus-basemap-countries">
              {mapPaths.map((p, idx) => (
                <path
                  key={idx}
                  d={p.d}
                  fill="#181f2a"
                  stroke="#263345"
                  strokeWidth="0.75"
                  vectorEffect="non-scaling-stroke"
                />
              ))}
            </g>

            {/* Ancient River Courses (Indus, Saraswati / Ghaggar-Hakra, Ravi, Chenab, Sutlej, Narmada) */}
            <g className="indus-rivers" stroke="#1d4ed8" strokeWidth="1.2" fill="none" opacity="0.65" strokeLinecap="round" vectorEffect="non-scaling-stroke">
              {/* Saraswati / Ghaggar-Hakra Dry Riverbed */}
              <path d="M 688 -395 Q 675 -385 660 -370 T 640 -340 T 628 -315" stroke="#38bdf8" strokeWidth="1.5" strokeDasharray="3,2" />
              {/* Indus Trunk */}
              <path d="M 660 -420 Q 645 -400 635 -380 T 620 -355 T 612 -330 T 605 -300" stroke="#0284c7" strokeWidth="2" />
            </g>

            {/* Maritime & Caravan Trade Routes */}
            {showRoutes && (
              <g className="indus-routes">
                {tradeRoutes.map(route => (
                  <g key={route.id} className="indus-route-group">
                    <path
                      d={route.path_d}
                      fill="none"
                      stroke={route.type === 'maritime' ? '#38bdf8' : '#fbbf24'}
                      strokeWidth={route.type === 'maritime' ? '1.5' : '1.2'}
                      strokeDasharray={route.type === 'maritime' ? '5,3' : '3,3'}
                      opacity="0.7"
                      vectorEffect="non-scaling-stroke"
                    />
                    <text
                      x={route.label_pos.x}
                      y={route.label_pos.y}
                      fill={route.type === 'maritime' ? '#7dd3fc' : '#fde68a'}
                      fontSize="5"
                      fontFamily="sans-serif"
                      fontWeight="600"
                      textAnchor="middle"
                      opacity="0.85"
                    >
                      {route.name}
                    </text>
                  </g>
                ))}
              </g>
            )}

            {/* Sites Markers */}
            <g className="indus-sites-layer">
              {filteredSites.map(site => {
                const isSelected = site.id === selectedSiteId;
                const isHovered = site.id === hoveredSiteId;
                const isMetropolis = site.category === 'metropolis';
                const isForeign = site.category === 'foreign_trade';
                const color = CATEGORY_COLORS[site.category] || '#94a3b8';

                // Only show labels for metropolises or hovered/selected sites to eliminate visual clutter
                const shouldShowLabel = isMetropolis || isSelected || isHovered || filteredSites.length <= 10;

                return (
                  <g
                    key={site.id}
                    className={`indus-site-pin ${isSelected ? 'selected' : ''} ${isHovered ? 'hovered' : ''}`}
                    onClick={() => setSelectedSiteId(site.id)}
                    onMouseEnter={() => setHoveredSiteId(site.id)}
                    onMouseLeave={() => setHoveredSiteId(null)}
                    style={{ cursor: 'pointer' }}
                  >
                    {/* Metropolis glowing halo */}
                    {isMetropolis && (
                      <circle
                        cx={site.proj_x}
                        cy={site.proj_y}
                        r="12"
                        fill="url(#metropolisGlow)"
                      />
                    )}

                    {/* Outer pulse ring on selection */}
                    {isSelected && (
                      <circle
                        cx={site.proj_x}
                        cy={site.proj_y}
                        r={isMetropolis ? 9 : 7}
                        fill="none"
                        stroke="#fff"
                        strokeWidth="1.5"
                        strokeDasharray="2,2"
                        className="pin-pulse"
                      />
                    )}

                    {/* Site Base Marker */}
                    <circle
                      cx={site.proj_x}
                      cy={site.proj_y}
                      r={isMetropolis ? 5.5 : isForeign ? 4.5 : 3.5}
                      fill={color}
                      stroke={isSelected ? '#fff' : '#0b0f15'}
                      strokeWidth={isSelected ? '2' : '1'}
                      filter="url(#siteShadow)"
                    />

                    {/* Inner iconic dot */}
                    <circle
                      cx={site.proj_x}
                      cy={site.proj_y}
                      r={isMetropolis ? 2.2 : 1.4}
                      fill="#0b0f15"
                    />

                    {/* Clean uncluttered label */}
                    {shouldShowLabel && (
                      <g className="site-label-wrap">
                        <text
                          x={site.proj_x}
                          y={site.proj_y - (isMetropolis ? 8 : 6)}
                          fill={isSelected ? '#fff' : isMetropolis ? '#fef08a' : '#cbd5e1'}
                          fontSize={isMetropolis ? '6.5' : '5'}
                          fontWeight={isMetropolis ? '750' : '600'}
                          fontFamily="sans-serif"
                          textAnchor="middle"
                          stroke="#0b0f15"
                          strokeWidth="2.5"
                          paintOrder="stroke"
                          strokeLinejoin="round"
                        >
                          {site.name}
                        </text>
                      </g>
                    )}
                  </g>
                );
              })}
            </g>
          </svg>

          {/* Quick Legend at bottom of map */}
          <div className="indus-map-legend">
            <span className="iml-item"><span className="iml-dot" style={{ background: CATEGORY_COLORS.metropolis }} /> Metropolis (8)</span>
            <span className="iml-item"><span className="iml-dot" style={{ background: CATEGORY_COLORS.port }} /> Port & Dockyard</span>
            <span className="iml-item"><span className="iml-dot" style={{ background: CATEGORY_COLORS.craft }} /> Craft / Bead Hub</span>
            <span className="iml-item"><span className="iml-dot" style={{ background: CATEGORY_COLORS.foreign_trade }} /> Mesopotamian Outpost</span>
            <span className="iml-item"><span className="iml-line blue" /> Maritime Route</span>
            <span className="iml-item"><span className="iml-line gold" /> Overland Route</span>
          </div>
        </div>

        {/* Polished Detailed Excavation Dossier Sidebar */}
        <aside className="indus-site-dossier" aria-labelledby="dossier-site-title">
          {selectedSite ? (
            <div className="dossier-inner">
              <div className="dossier-hero">
                <div className="dossier-kicker">
                  <span className="dossier-category-badge" style={{ '--cat-color': CATEGORY_COLORS[selectedSite.category] }}>
                    {selectedSite.category.replace(/_/g, ' ').toUpperCase()}
                  </span>
                  <span className="dossier-country">{selectedSite.country} · {selectedSite.state_or_province}</span>
                </div>

                <h3 id="dossier-site-title" className="dossier-title">
                  {selectedSite.name}
                  {selectedSite.name_hi && <span className="dossier-hindi" lang="hi">({selectedSite.name_hi})</span>}
                </h3>

                <p className="dossier-period">
                  <strong>Chronology:</strong> {selectedSite.period_era}
                </p>
              </div>

              {/* Quick Info Grid */}
              <div className="dossier-grid">
                <div className="dossier-cell">
                  <span className="cell-label">Principal Excavators</span>
                  <span className="cell-value">{selectedSite.excavators || 'Surveyed by ASI'}</span>
                </div>
                <div className="dossier-cell">
                  <span className="cell-label">Estimated Extent</span>
                  <span className="cell-value">{selectedSite.area_hectares ? `${selectedSite.area_hectares} Hectares` : 'Settlement mound'}</span>
                </div>
              </div>

              {/* Key Architectural Structures */}
              <div className="dossier-section">
                <h4>Excavated Architecture & Civil Engineering</h4>
                <ul className="dossier-list">
                  {selectedSite.key_structures.map((struct, idx) => (
                    <li key={idx}><strong>✓</strong> {struct}</li>
                  ))}
                </ul>
              </div>

              {/* Key Artifacts & Inscriptions */}
              <div className="dossier-section">
                <h4>Diagnostic Artifacts & Epigraphy</h4>
                <div className="dossier-chips">
                  {selectedSite.key_artifacts.map((art, idx) => (
                    <span key={idx} className="dossier-chip">{art}</span>
                  ))}
                </div>
              </div>

              {/* Foreign Trade Connection if any */}
              {selectedSite.foreign_connection && (
                <div className="dossier-foreign-alert">
                  <strong>🌍 International Trade Link:</strong> {selectedSite.foreign_connection}
                </div>
              )}

              {/* Direct Deep Link to Decryption Workbench for sites with famous seals */}
              {selectedSite.key_artifacts.some(a => /seal|signboard|script/i.test(a)) && (
                <div className="dossier-script-banner">
                  <div>
                    <strong>⚚ Indus Epigraphic Corpus:</strong>
                    <p>Decipher the Harappan seals found at {selectedSite.name} with our computational cryptanalysis workbench.</p>
                  </div>
                  <Link to="/ivc-translator" className="btn btn-primary btn-sm">Open Script Decoder →</Link>
                </div>
              )}

              {/* Official Academic & Excavation Sources (ASI Memoirs, Cell, Nature) */}
              <div className="dossier-section dossier-sources">
                <h4>Official Peer-Reviewed & ASI Excavation Reports</h4>
                <div className="dossier-sources-list">
                  {selectedSite.official_sources && selectedSite.official_sources.map((src, idx) => (
                    <div key={idx} className="source-citation-card">
                      <div className="scc-header">
                        <span className="scc-type">{src.type || 'Monograph'}</span>
                        <span className="scc-year">{src.year}</span>
                      </div>
                      <h5 className="scc-title">{src.title}</h5>
                      <p className="scc-authors">{src.authors}</p>
                      <p className="scc-pub">{src.publisher}</p>
                      {src.doi && (
                        <a
                          href={src.doi.startsWith('http') ? src.doi : `https://doi.org/${src.doi}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="scc-link"
                        >
                          View Official Record / DOI →
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="dossier-empty">
              <p>Select any excavation site on the map to inspect its structures, artifacts, and ASI memoirs.</p>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}
