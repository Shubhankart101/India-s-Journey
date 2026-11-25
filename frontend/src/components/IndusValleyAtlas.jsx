import { useState, useMemo, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import sitesData from '../data/indus-civilisation.json';
import { assetUrl } from '../config.js';
import { useTheme } from '../theme.js';
import { HistoricalMapViewer } from './AncientEmpiresAtlas.jsx';
import './IndusAtlas.css';

const MAJOR_METROPOLIS_IDS = new Set(['rakhigarhi', 'mohenjo-daro', 'harappa', 'dholavira', 'ganweriwala', 'kalibangan', 'lothal', 'banawali']);
const DARK_THEME_IDS = new Set(['dark', 'military', 'parliamentary', 'airforce']);

// De-collide adjacent metropolis labels in the Haryana–Punjab–Gujarat core
const METROPOLIS_LABEL_OFFSETS = {
  harappa: { dx: 0, dy: -8, anchor: 'middle' },
  kalibangan: { dx: -14, dy: -6, anchor: 'end' },
  banawali: { dx: 6, dy: -11, anchor: 'start' },
  rakhigarhi: { dx: 12, dy: 9, anchor: 'start' },
  ganweriwala: { dx: -8, dy: 10, anchor: 'end' },
  'mohenjo-daro': { dx: -8, dy: -8, anchor: 'end' },
  dholavira: { dx: -10, dy: -6, anchor: 'end' },
  lothal: { dx: 10, dy: 9, anchor: 'start' },
};

const CATEGORY_COLORS = {
  metropolis: '#d4a72c',
  port: '#38bdf8',
  craft: '#f59e0b',
  fortified: '#ec4899',
  cemetery: '#8b5cf6',
  frontier: '#ef4444',
  foreign_trade: '#10b981',
};

const TIER_FILTERS = [
  { id: 'all', label: 'All Excavations (49)', icon: '🏛' },
  { id: 'metropolis', label: 'Great Metropolises (8)', icon: '★' },
  { id: 'port', label: 'Ports & Dockyards', icon: '⚓' },
  { id: 'craft', label: 'Craft & Metallurgy', icon: '⚒' },
  { id: 'foreign_trade', label: 'International / Gulf', icon: '🌍' },
];

const REGION_PRESETS = [
  { id: 'full', label: 'Pan-Indus & Gulf', vb: { x: 410, y: -460, w: 410, h: 285 } },
  { id: 'heartland', label: 'Indus-Saraswati Heartland', vb: { x: 570, y: -420, w: 180, h: 160 } },
  { id: 'gujarat', label: 'Gujarat, Saurashtra & Kutch', vb: { x: 670, y: -260, w: 90, h: 80 } },
  { id: 'meso', label: 'Persian Gulf & Mesopotamia', vb: { x: 420, y: -380, w: 170, h: 140 } },
];

export default function IndusValleyAtlas() {
  const themeId = useTheme();
  const isDarkMap = DARK_THEME_IDS.has(themeId);
  const [mapPaths, setMapPaths] = useState([]);
  const [selectedSiteId, setSelectedSiteId] = useState('rakhigarhi');
  const [selectedPeriodId, setSelectedPeriodId] = useState('all');
  const [dossierTab, setDossierTab] = useState('site'); // 'site' | 'periods'
  const [activeDossierPeriodId, setActiveDossierPeriodId] = useState('mature');
  const [tierFilter, setTierFilter] = useState('all');
  const [countryFilter, setCountryFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showRoutes, setShowRoutes] = useState(true);
  const [showRivers, setShowRivers] = useState(true);
  const [hoveredSiteId, setHoveredSiteId] = useState(null);
  const [tooltip, setTooltip] = useState(null);
  const [mapViewMode, setMapViewMode] = useState('interactive');
  const mapStageRef = useRef(null);
  const dragRef = useRef({ active: false, moved: false, startX: 0, startY: 0, startVb: null });

  // Zoom & Pan state
  const [viewBox, setViewBox] = useState(REGION_PRESETS[0].vb);
  const [activeRegion, setActiveRegion] = useState('full');

  useEffect(() => {
    fetch(assetUrl('maps/world-asia.json'))
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
  const periods = sitesData.periods || [];

  const currentDossierPeriod = useMemo(() => {
    return periods.find(p => p.id === activeDossierPeriodId) || periods[1] || periods[0] || {};
  }, [periods, activeDossierPeriodId]);

  const filteredSites = useMemo(() => {
    return sites.filter(site => {
      if (selectedPeriodId !== 'all' && site.period_era && site.period_era !== selectedPeriodId) {
        if (!searchQuery.trim()) return false;
      }
      if (tierFilter !== 'all' && site.category !== tierFilter) return false;
      if (countryFilter !== 'all' && site.country !== countryFilter) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchName = site.name.toLowerCase().includes(q) || (site.name_hi && site.name_hi.includes(q));
        const matchArtifact = site.key_artifacts?.some(a => a.toLowerCase().includes(q));
        const matchStruct = site.key_structures?.some(s => s.toLowerCase().includes(q));
        const matchCountry = site.country?.toLowerCase().includes(q) || (site.state_or_province && site.state_or_province.toLowerCase().includes(q));
        const matchExcavator = site.excavators && site.excavators.toLowerCase().includes(q);
        const matchSource = site.official_sources && site.official_sources.some(src => (src.title + (src.authors || '') + (src.publisher || '')).toLowerCase().includes(q));
        if (!matchName && !matchArtifact && !matchStruct && !matchCountry && !matchExcavator && !matchSource) return false;
      }
      return true;
    });
  }, [sites, selectedPeriodId, tierFilter, countryFilter, searchQuery]);

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

  const focusSite = (site) => {
    if (!site) return;
    setSelectedSiteId(site.id);
    const sx = site.x !== undefined ? site.x : (site.lon * 10);
    const sy = site.y !== undefined ? site.y : (-site.lat * 10);
    setViewBox(curr => {
      const targetW = Math.min(curr.w, 160);
      const targetH = Math.min(curr.h, 112);
      return {
        x: sx - targetW / 2,
        y: sy - targetH / 2,
        w: targetW,
        h: targetH,
      };
    });
  };

  const handleZoom = (factor) => {
    setViewBox(curr => {
      const nw = Math.max(40, Math.min(500, curr.w * factor));
      const nh = Math.max(30, Math.min(380, curr.h * factor));
      const nx = curr.x + (curr.w - nw) / 2;
      const ny = curr.y + (curr.h - nh) / 2;
      return { x: nx, y: ny, w: nw, h: nh };
    });
  };

  const handleSvgPointerDown = (e) => {
    if (e.button !== 0 || e.target.closest('.indus-site-pin, .indus-route-group')) return;
    dragRef.current = { active: true, moved: false, startX: e.clientX, startY: e.clientY, startVb: viewBox };
  };

  const handleSvgPointerMove = (e) => {
    if (!dragRef.current.active || !mapStageRef.current || !dragRef.current.startVb) return;
    const rect = mapStageRef.current.getBoundingClientRect();
    const dxPx = e.clientX - dragRef.current.startX;
    const dyPx = e.clientY - dragRef.current.startY;
    if (Math.hypot(dxPx, dyPx) > 4) dragRef.current.moved = true;
    const scaleX = dragRef.current.startVb.w / Math.max(1, rect.width);
    const scaleY = dragRef.current.startVb.h / Math.max(1, rect.height);
    setViewBox({
      ...dragRef.current.startVb,
      x: dragRef.current.startVb.x - dxPx * scaleX,
      y: dragRef.current.startVb.y - dyPx * scaleY,
    });
  };

  const handleSvgPointerUp = () => {
    dragRef.current.active = false;
  };

  const handleMouseMove = (e) => {
    if (dragRef.current.active) {
      handleSvgPointerMove(e);
      return;
    }
    if (!mapStageRef.current) return;
    const rect = mapStageRef.current.getBoundingClientRect();
    if (hoveredSiteId) {
      const site = sites.find(s => s.id === hoveredSiteId);
      if (site) {
        setTooltip({
          x: Math.max(10, Math.min(rect.width - 265, e.clientX - rect.left + 15)),
          y: Math.max(10, Math.min(rect.height - 155, e.clientY - rect.top - 10)),
          site,
        });
      }
    } else if (!tooltip?.route) {
      setTooltip(null);
    }
  };

  return (
    <div className="indus-valley-atlas">
      {/* Top Atlas Header Banner */}
      <header className="indus-atlas-header">
        <div className="indus-title-group">
          <span className="indus-kicker">ARCHAEOLOGICAL SURVEY OF INDIA & PEER-REVIEWED CORPUS</span>
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
            <span className="isc-label">Official Sources</span>
          </div>
        </div>
      </header>

      {/* Tier Filter Tabs */}
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
            placeholder="Search excavations by name, artifacts, excavator (e.g. Rakhigarhi, Great Bath, seals)..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="indus-search-input"
            aria-label="Search excavation sites"
          />
          {searchQuery && (
            <button type="button" className="indus-search-clear" onClick={() => setSearchQuery('')}>×</button>
          )}
        </div>

        {/* Country Filter */}
        <div className="indus-select-wrap">
          <label htmlFor="country-select">Country:</label>
          <select
            id="country-select"
            value={countryFilter}
            onChange={e => setCountryFilter(e.target.value)}
            className="indus-select"
          >
            {countries.map(c => (
              <option key={c} value={c}>{c === 'all' ? 'All Nations (9)' : c}</option>
            ))}
          </select>
        </div>

        {/* Region Presets */}
        <div className="indus-presets-wrap" role="group" aria-label="Geographic focus">
          {REGION_PRESETS.map(r => (
            <button
              key={r.id}
              type="button"
              className={`preset-btn ${activeRegion === r.id ? 'active' : ''}`}
              onClick={() => handleRegionChange(r)}
            >
              {r.label}
            </button>
          ))}
        </div>

        {/* Toggle Trade Routes & Rivers */}
        <div className="indus-toggles-row">
          <button
            type="button"
            className={`toggle-routes-btn ${showRoutes ? 'active' : ''}`}
            onClick={() => setShowRoutes(!showRoutes)}
            aria-pressed={showRoutes}
            title="Toggle Meluhha maritime and overland caravan trade networks"
          >
            {showRoutes ? '⛵ Trade Routes: On' : '⛵ Trade Routes: Off'}
          </button>
          <button
            type="button"
            className={`toggle-routes-btn ${showRivers ? 'active' : ''}`}
            onClick={() => setShowRivers(!showRivers)}
            aria-pressed={showRivers}
            title="Toggle Indus, Saraswati/Ghaggar-Hakra, and Oxus paleochannels"
          >
            {showRivers ? '🌊 Paleo-Rivers: On' : '🌊 Paleo-Rivers: Off'}
          </button>
        </div>
      </div>

      {/* Harappan Period / Era Horizons & Territorial Boundary Selector */}
      <div className="indus-periods-strip" role="group" aria-label="Harappan Era Horizons & Boundaries">
        <span className="ips-label">⏳ Chronological Eras &amp; Map Boundaries:</span>
        <button
          type="button"
          className={`ips-pill ${selectedPeriodId === 'all' ? 'active' : ''}`}
          aria-pressed={selectedPeriodId === 'all'}
          onClick={() => setSelectedPeriodId('all')}
        >
          All Eras (3300–1300 BCE)
        </button>
        {periods.map(p => (
          <button
            key={p.id}
            type="button"
            className={`ips-pill ${selectedPeriodId === p.id ? 'active' : ''}`}
            aria-pressed={selectedPeriodId === p.id}
            style={{ '--period-color': p.color }}
            onClick={() => {
              setSelectedPeriodId(p.id);
              setActiveDossierPeriodId(p.id);
              setDossierTab('periods');
            }}
          >
            <span className="ips-dot" style={{ background: p.color }} />
            <span>{p.name.split('/')[0].trim()}</span>
            <small className="ips-span">({p.span})</small>
          </button>
        ))}
      </div>

      {/* View Mode Switcher */}
      <div className="indus-mode-bar" role="tablist" aria-label="Atlas Display Mode">
        <button
          type="button"
          role="tab"
          aria-selected={mapViewMode === 'interactive'}
          className={`indus-mode-btn ${mapViewMode === 'interactive' ? 'active' : ''}`}
          onClick={() => setMapViewMode('interactive')}
        >
          🗺️ 49 Excavation Sites (Interactive GPS &amp; Artifacts)
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={mapViewMode === 'historical'}
          className={`indus-mode-btn ${mapViewMode === 'historical' ? 'active' : ''}`}
          onClick={() => setMapViewMode('historical')}
        >
          📜 Authentic Harappan Civilisation Atlas (Tapas Banerjee Cartography)
        </button>
        <button
          type="button"
          className="indus-mode-btn"
          onClick={() => {
            const el = document.getElementById('ivc-script-decoder-dock');
            if (el) el.scrollIntoView({ behavior: 'smooth' });
          }}
          title="Scroll down to the docked Indus Script Decryption tool"
        >
          🔤 Script Decryption &amp; Concordance Engine ↓
        </button>
      </div>

      {/* Interactive Map & Site Dossier Split View */}
      <div className="indus-workbench">
          {/* SVG Interactive Map */}
          <div
            className="indus-map-container"
            ref={mapStageRef}
            onMouseMove={handleMouseMove}
            onMouseLeave={() => { setHoveredSiteId(null); setTooltip(null); }}
          >
            {mapViewMode === 'historical' ? (
              <div className="authentic-historical-map-frame">
                <div className="ahm-toolbar">
                  <span className="ahm-title">Cities of the Indus — the Harappan Civilisation · c. 3300–1300 BCE</span>
                  <span className="ahm-credit">Open-source South Asian Historical Atlas · Tapas Banerjee</span>
                </div>
                <HistoricalMapViewer
                  svgUrl={assetUrl('maps/historical/indus-civilisation.svg')}
                  title="Cities of the Indus — the Harappan Civilisation"
                  onFallbackToInteractive={() => setMapViewMode('interactive')}
                />
              </div>
            ) : (
              <>
                <div className="indus-map-toolbar">
                  <div className="indus-map-toolbar-meta">
                    <span className="showing-sites-count">
                      Showing {filteredSites.length} of {sites.length} Excavations
                    </span>
                    <span className="indus-drag-hint">Drag map to pan · Click pin to inspect</span>
                  </div>
                  <div className="map-zoom-btns">
                    <button type="button" onClick={() => handleZoom(0.8)} title="Zoom In" aria-label="Zoom in">+</button>
                    <button type="button" onClick={() => handleZoom(1.25)} title="Zoom Out" aria-label="Zoom out">−</button>
                    <button type="button" onClick={() => handleRegionChange(REGION_PRESETS[0])} title="Reset View" aria-label="Reset view">⟲</button>
                  </div>
                </div>

          <svg
            className="indus-svg"
            viewBox={`${viewBox.x} ${viewBox.y} ${viewBox.w} ${viewBox.h}`}
            preserveAspectRatio="xMidYMid meet"
            onPointerDown={handleSvgPointerDown}
            onPointerUp={handleSvgPointerUp}
            onPointerLeave={handleSvgPointerUp}
            style={{ cursor: dragRef.current.active ? 'grabbing' : 'grab' }}
          >
            <defs>
              <radialGradient id="metropolisGlow" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="#d4a72c" stopOpacity="0.8" />
                <stop offset="60%" stopColor="#d4a72c" stopOpacity="0.25" />
                <stop offset="100%" stopColor="#d4a72c" stopOpacity="0" />
              </radialGradient>
              <filter id="siteShadow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="1.5" stdDeviation="1.5" floodColor="#000" floodOpacity="0.55" />
              </filter>
            </defs>

            {/* Geographical Background */}
            <rect
              x={viewBox.x - 200}
              y={viewBox.y - 200}
              width={viewBox.w + 400}
              height={viewBox.h + 400}
              fill={isDarkMap ? '#0d1117' : '#d6e4ee'}
            />

            {/* Country boundary polygons */}
            <g className="indus-basemap-countries">
              {mapPaths.map((p, idx) => (
                <path
                  key={idx}
                  d={p.d}
                  fill={isDarkMap ? '#181f2a' : '#f4efe3'}
                  stroke={isDarkMap ? '#2c3c52' : '#c0b297'}
                  strokeWidth="0.75"
                  vectorEffect="non-scaling-stroke"
                />
              ))}
            </g>

            {/* Ancient River Courses & Paleochannels */}
            {showRivers && (
              <g className="indus-rivers" fill="none" strokeLinecap="round" vectorEffect="non-scaling-stroke">
                {/* Saraswati / Ghaggar-Hakra Paleochannel */}
                <path d="M 772 -306 Q 748 -297 720 -286 Q 705 -274 690 -248" stroke={isDarkMap ? '#38bdf8' : '#0284c7'} strokeWidth="1.6" strokeDasharray="3,2" opacity="0.8" />
                {/* Indus Main Trunk */}
                <path d="M 755 -352 Q 726 -335 712 -304 Q 695 -272 678 -244" stroke={isDarkMap ? '#0ea5e9' : '#0369a1'} strokeWidth="2.1" opacity="0.85" />
                {/* Ravi / Sutlej Tributaries */}
                <path d="M 752 -324 Q 735 -310 715 -296" stroke={isDarkMap ? '#0ea5e9' : '#0369a1'} strokeWidth="1.2" opacity="0.65" />
                <path d="M 766 -312 Q 738 -302 710 -291" stroke={isDarkMap ? '#0ea5e9' : '#0369a1'} strokeWidth="1.2" opacity="0.65" />
                {/* Narmada / Tapi */}
                <path d="M 730 -216 Q 765 -218 795 -220" stroke={isDarkMap ? '#0284c7' : '#0369a1'} strokeWidth="1.2" opacity="0.55" />
                {/* River Labels */}
                <text x="698" y="-266" fill={isDarkMap ? '#7dd3fc' : '#0369a1'} fontSize="4.2" fontStyle="italic" fontWeight="600" opacity="0.85">Indus (Sindhu)</text>
                <text x="724" y="-281" fill={isDarkMap ? '#7dd3fc' : '#0284c7'} fontSize="4" fontStyle="italic" fontWeight="600" opacity="0.85">Saraswati–Hakra</text>
              </g>
            )}

            {/* Harappan Period Territorial Boundaries */}
            <g className="indus-period-boundaries">
              {periods.map(p => {
                const isActive = selectedPeriodId === p.id;
                const isShowing = selectedPeriodId === 'all' || isActive;
                if (!isShowing || !p.boundary_path_d) return null;
                return (
                  <path
                    key={p.id}
                    d={p.boundary_path_d}
                    fill={isActive ? (p.fill_color || 'rgba(245, 158, 11, 0.12)') : (selectedPeriodId === 'all' ? p.fill_color || 'transparent' : 'none')}
                    stroke={p.color}
                    strokeWidth={isActive ? '2.5' : '1.4'}
                    strokeDasharray={isActive ? '5,3' : '3,3'}
                    opacity={isActive ? 0.95 : 0.55}
                    vectorEffect="non-scaling-stroke"
                    className={`period-boundary-path ${isActive ? 'active-pulse' : ''}`}
                  />
                );
              })}
            </g>

            {/* Maritime & Caravan Trade Routes */}
            {showRoutes && (
              <g className="indus-routes">
                {tradeRoutes.map(route => (
                  <g
                    key={route.id}
                    className="indus-route-group"
                    onMouseEnter={(e) => {
                      if (!mapStageRef.current) return;
                      const rect = mapStageRef.current.getBoundingClientRect();
                      setTooltip({
                        x: Math.max(10, Math.min(rect.width - 240, e.clientX - rect.left + 15)),
                        y: Math.max(10, Math.min(rect.height - 150, e.clientY - rect.top - 10)),
                        route,
                      });
                    }}
                    onMouseLeave={() => setTooltip(null)}
                    style={{ cursor: 'pointer' }}
                  >
                      <path
                        d={route.path_d}
                        fill="none"
                        stroke={route.type === 'maritime' ? (isDarkMap ? '#38bdf8' : '#0284c7') : (isDarkMap ? '#fbbf24' : '#b45309')}
                        strokeWidth={route.type === 'maritime' ? '1.6' : '1.3'}
                        strokeDasharray={route.type === 'maritime' ? '5,3' : '3,3'}
                        opacity={isDarkMap ? '0.78' : '0.88'}
                        vectorEffect="non-scaling-stroke"
                      />
                    {route.label_pos && (
                      <text
                        x={route.label_pos.x}
                        y={route.label_pos.y}
                        fill={route.type === 'maritime' ? (isDarkMap ? '#7dd3fc' : '#0369a1') : (isDarkMap ? '#fde68a' : '#92400e')}
                        fontSize="4.6"
                        fontFamily="sans-serif"
                        fontWeight="650"
                        textAnchor="middle"
                        stroke={isDarkMap ? '#0d1117' : '#f4efe3'}
                        strokeWidth="1.8"
                        paintOrder="stroke"
                        opacity="0.92"
                      >
                        {route.name}
                      </text>
                    )}
                  </g>
                ))}
              </g>
            )}

            {/* Sites Markers */}
            <g className="indus-sites-layer">
              {filteredSites.map(site => {
                const sx = site.x !== undefined ? site.x : (site.lon * 10);
                const sy = site.y !== undefined ? site.y : (-site.lat * 10);
                const isSelected = site.id === selectedSiteId;
                const isHovered = site.id === hoveredSiteId;
                const isMajor = MAJOR_METROPOLIS_IDS.has(site.id) || site.category === 'metropolis';
                const isForeign = site.category === 'foreign_trade';
                const color = CATEGORY_COLORS[site.category] || '#94a3b8';

                // Prominently label major metropolises and active site to avoid clutter
                const shouldShowLabel = isMajor || isSelected || isHovered || filteredSites.length <= 10;

                return (
                  <g
                    key={site.id}
                    className={`indus-site-pin ${isSelected ? 'selected' : ''} ${isHovered ? 'hovered' : ''}`}
                    onClick={() => { if (!dragRef.current.moved) setSelectedSiteId(site.id); }}
                    onMouseEnter={() => setHoveredSiteId(site.id)}
                    onMouseLeave={() => setHoveredSiteId(null)}
                    style={{ cursor: 'pointer' }}
                  >
                    {/* Metropolis glowing halo */}
                    {isMajor && (
                      <circle
                        cx={sx}
                        cy={sy}
                        r="10"
                        fill="url(#metropolisGlow)"
                      />
                    )}

                    {/* Outer pulse ring on selection */}
                    {isSelected && (
                      <circle
                        cx={sx}
                        cy={sy}
                        r={isMajor ? 8 : 6}
                        fill="none"
                        stroke="#fff"
                        strokeWidth="1.5"
                        strokeDasharray="2,2"
                        className="pin-pulse"
                      />
                    )}

                    {/* Site Base Marker */}
                    <circle
                      cx={sx}
                      cy={sy}
                      r={isMajor ? 5 : isForeign ? 4 : 3}
                      fill={color}
                      stroke={isSelected ? '#fff' : '#0b0f15'}
                      strokeWidth={isSelected ? '2' : '1'}
                      filter="url(#siteShadow)"
                    />

                    {/* Inner iconic dot */}
                    <circle
                      cx={sx}
                      cy={sy}
                      r={isMajor ? 2 : 1.2}
                      fill="#0b0f15"
                    />

                    {/* Clean de-collided label */}
                    {shouldShowLabel && (() => {
                      const off = METROPOLIS_LABEL_OFFSETS[site.id] || { dx: 0, dy: -(isMajor ? 7 : 5), anchor: 'middle' };
                      const labelFill = isSelected
                        ? (isDarkMap ? '#ffffff' : '#0b0f15')
                        : isMajor
                          ? (isDarkMap ? '#fef08a' : '#78350f')
                          : (isDarkMap ? '#cbd5e1' : '#1e293b');
                      const labelStroke = isDarkMap ? '#0b0f15' : '#fffdf8';
                      return (
                        <g className="site-label-wrap">
                          <text
                            x={sx + off.dx}
                            y={sy + off.dy}
                            fill={labelFill}
                            fontSize={isMajor ? '5.4' : '4.2'}
                            fontWeight={isMajor ? '750' : '600'}
                            fontFamily="sans-serif"
                            textAnchor={off.anchor}
                            stroke={labelStroke}
                            strokeWidth="2.2"
                            paintOrder="stroke"
                            strokeLinejoin="round"
                          >
                            {site.name}
                          </text>
                        </g>
                      );
                    })()}
                  </g>
                );
              })}
            </g>
          </svg>

          {/* Interactive Floating Tooltip */}
          {tooltip && (
            <div className="indus-floating-tooltip" style={{ left: tooltip.x, top: tooltip.y }}>
              {tooltip.site ? (
                <>
                  <div className="ift-tag" style={{ color: CATEGORY_COLORS[tooltip.site.category] || '#fbbf24' }}>
                    {tooltip.site.badge || tooltip.site.category.replace(/_/g, ' ').toUpperCase()}
                  </div>
                  <strong className="ift-title">{tooltip.site.name}</strong>
                  {tooltip.site.name_hi && <span className="ift-hi"> ({tooltip.site.name_hi})</span>}
                  <p className="ift-loc">{tooltip.site.state_or_province}, {tooltip.site.country}</p>
                  {tooltip.site.area_hectares && (
                    <p className="ift-area"><strong>Area:</strong> {tooltip.site.area_hectares} hectares</p>
                  )}
                  {tooltip.site.period && <p className="ift-period"><strong>Era:</strong> {tooltip.site.period}</p>}
                </>
              ) : tooltip.route ? (
                <>
                  <div className="ift-tag" style={{ color: tooltip.route.type === 'maritime' ? '#38bdf8' : '#fbbf24' }}>
                    {tooltip.route.type === 'maritime' ? '⚓ MARITIME SEA LANE' : '🐪 OVERLAND CARAVAN CORRIDOR'}
                  </div>
                  <strong className="ift-title">{tooltip.route.name}</strong>
                  <p className="ift-loc">{tooltip.route.description || 'Ancient commercial trade corridor linking Harappan cities with Mesopotamia, Dilmun, and the Iranian plateau.'}</p>
                </>
              ) : null}
            </div>
          )}

          {/* Quick Site Directory Rail under Map Legend for instant 1-click access across all filtered sites */}
          <div className="indus-site-rail" aria-label="Quick site selector">
            <span className="isr-label">Quick Site Jump ({filteredSites.length}):</span>
            <div className="isr-chips">
              {filteredSites.slice(0, 18).map(s => (
                <button
                  key={s.id}
                  type="button"
                  className={`isr-chip ${s.id === selectedSiteId ? 'active' : ''}`}
                  onClick={() => { focusSite(s); setDossierTab('site'); }}
                >
                  {MAJOR_METROPOLIS_IDS.has(s.id) ? '★ ' : ''}{s.name}
                </button>
              ))}
            </div>
          </div>

          {/* Quick Legend at bottom of map */}
          <div className="indus-map-legend">
            <span className="iml-item"><span className="iml-dot" style={{ background: CATEGORY_COLORS.metropolis }} /> Great Metropolis (8)</span>
            <span className="iml-item"><span className="iml-dot" style={{ background: CATEGORY_COLORS.port }} /> Port &amp; Dockyard</span>
            <span className="iml-item"><span className="iml-dot" style={{ background: CATEGORY_COLORS.craft }} /> Craft / Bead Hub</span>
            <span className="iml-item"><span className="iml-dot" style={{ background: CATEGORY_COLORS.foreign_trade }} /> Mesopotamian Outpost</span>
            <span className="iml-item"><span className="iml-line blue" /> Maritime Route</span>
            <span className="iml-item"><span className="iml-line gold" /> Overland Route</span>
          </div>
          </>
        )}
        </div>

        {/* Polished Detailed Excavation Dossier Sidebar */}
        <aside className="indus-site-dossier" aria-labelledby="dossier-site-title">
          {/* Dossier Tabs: Site vs Periods & ASI Memoirs (Pinned at top) */}
          <div className="dossier-tab-bar" role="tablist" aria-label="Indus Dossier Sections">
            <button
              type="button"
              role="tab"
              aria-selected={dossierTab === 'site'}
              className={`dossier-tab-btn ${dossierTab === 'site' ? 'active' : ''}`}
              onClick={() => setDossierTab('site')}
            >
              🏛 Excavation Site {selectedSite ? `(${selectedSite.name})` : ''}
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={dossierTab === 'periods'}
              className={`dossier-tab-btn ${dossierTab === 'periods' ? 'active' : ''}`}
              onClick={() => setDossierTab('periods')}
            >
              ⏳ Harappan Periods &amp; ASI Quotes ({periods.length})
            </button>
          </div>

          <div className="dossier-body-scroll">
            {/* TAB 1: Site Excavations */}
            {dossierTab === 'site' && (
              selectedSite ? (
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
                      <strong>Chronology:</strong> {selectedSite.period}
                    </p>

                    {/* Integrated Harappan Period & Memoirs Bridge Button */}
                    <div className="dossier-era-bridge">
                      <button
                        type="button"
                        className="dossier-era-btn"
                        onClick={() => {
                          const era = selectedSite.period_era || 'mature';
                          setActiveDossierPeriodId(era);
                          setSelectedPeriodId(era);
                          setDossierTab('periods');
                        }}
                        title={`View ${selectedSite.period_era ? selectedSite.period_era.toUpperCase() : 'MATURE'} Harappan boundaries & memoirs`}
                      >
                        <span className="deb-icon">⏳</span>
                        <span className="deb-text">
                          View <strong>{selectedSite.period_era ? `${selectedSite.period_era.toUpperCase()} ERA` : 'ERA'}</strong> Boundaries &amp; Memoirs
                        </span>
                        <span className="deb-arrow">→</span>
                      </button>
                    </div>
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

                {/* Description */}
                {selectedSite.description && (
                  <div className="dossier-section">
                    <p className="dossier-desc-text">{selectedSite.description}</p>
                  </div>
                )}

                {/* Key Architectural Structures */}
                {selectedSite.key_structures && (
                  <div className="dossier-section">
                    <h4>Excavated Architecture &amp; Civil Engineering</h4>
                    <ul className="dossier-list">
                      {selectedSite.key_structures.map((struct, idx) => (
                        <li key={idx}><strong>✓</strong> {struct}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Key Artifacts & Inscriptions */}
                {selectedSite.key_artifacts && (
                  <div className="dossier-section">
                    <h4>Diagnostic Artifacts &amp; Epigraphy</h4>
                    <div className="dossier-chips">
                      {selectedSite.key_artifacts.map((art, idx) => (
                        <span key={idx} className="dossier-chip">{art}</span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Foreign Trade Connection if any */}
                {selectedSite.foreign_connection && (
                  <div className="dossier-foreign-alert">
                    <strong>🌍 International Trade Link:</strong> {selectedSite.foreign_connection}
                  </div>
                )}

                {/* Official Academic & Excavation Sources (ASI Memoirs, Cell, Nature) */}
                <div className="dossier-section dossier-sources">
                  <h4>Official Peer-Reviewed &amp; ASI Excavation Reports</h4>
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
                        {src.url && (
                          <a
                            href={src.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="scc-link"
                          >
                            View Official Record / Report →
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
            )
          )}

          {/* TAB 2: Harappan Periods, Boundaries & Quoted ASI Memoirs */}
          {dossierTab === 'periods' && (
            <div className="dossier-inner">
              <div className="dossier-hero">
                <div className="dossier-kicker">
                  <span className="dossier-category-badge" style={{ '--cat-color': currentDossierPeriod.color || '#f59e0b' }}>
                    {currentDossierPeriod.badge || 'HARAPPAN HORIZON'}
                  </span>
                  <span className="dossier-country">Geographic Extent: {currentDossierPeriod.area_sq_km}</span>
                </div>
                <h3 className="dossier-title">{currentDossierPeriod.name}</h3>
                <p className="dossier-period">
                  <strong>Radiocarbon Dating:</strong> {currentDossierPeriod.span}
                </p>
              </div>

              {/* Sub-period Selector Switcher */}
              <div className="ivc-period-subswitcher" role="group" aria-label="Select Harappan Horizon">
                {periods.map(p => (
                  <button
                    key={p.id}
                    type="button"
                    className={`ips-sub-btn ${activeDossierPeriodId === p.id ? 'active' : ''}`}
                    style={{ '--period-color': p.color }}
                    onClick={() => {
                      setActiveDossierPeriodId(p.id);
                      setSelectedPeriodId(p.id);
                    }}
                  >
                    <span className="ips-dot" style={{ background: p.color }} />
                    {p.name.split('/')[0].trim()}
                  </button>
                ))}
              </div>

              {/* Archaeological Overview */}
              <div className="dossier-box">
                <h4>Archaeological Trajectory &amp; Urban Morphology</h4>
                <p className="history-overview-text">{currentDossierPeriod.overview}</p>
              </div>

              {/* Chronicle of Horizons */}
              {currentDossierPeriod.chronicle && (
                <div className="dossier-section chronicle-section">
                  <h4>Chronological Horizons &amp; Stratigraphic Phases</h4>
                  <div className="chronicle-timeline">
                    {currentDossierPeriod.chronicle.map((ch, idx) => (
                      <div key={idx} className="chronicle-card">
                        <span className="chronicle-era-badge" style={{ color: currentDossierPeriod.color, borderColor: currentDossierPeriod.color }}>
                          {ch.era || ch.phase}
                        </span>
                        <p className="chronicle-narrative">{ch.narrative || ch.details}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Quoted Primary Source Documentation & ASI Memoirs */}
              {currentDossierPeriod.primary_sources && (
                <div className="dossier-section primary-sources-section">
                  <h4>Quoted Primary Excavation Memoirs &amp; Official Monographs</h4>
                  <div className="primary-sources-list">
                    {currentDossierPeriod.primary_sources.map((ps, idx) => (
                      <div key={idx} className="primary-quote-card">
                        <div className="pqc-header">
                          <span className="pqc-badge" style={{ color: currentDossierPeriod.color, borderColor: currentDossierPeriod.color }}>
                            ASI EXCAVATION MEMOIR
                          </span>
                          <span className="pqc-script">{ps.year}</span>
                        </div>
                        <h5 className="pqc-title">{ps.source_title}</h5>
                        <div className="pqc-meta">
                          <span><strong>Excavation Director / Scholar:</strong> {ps.director}</span>
                        </div>

                        {/* Quoted Memoir Text */}
                        <blockquote className="memoir-quote">
                          “{ps.quote}”
                        </blockquote>

                        <div className="pqc-footer">
                          <p className="pqc-citation">
                            <strong>Official Citation:</strong> {ps.citation}
                          </p>
                          <p className="pqc-significance">
                            <strong>Diagnostic Archaeological Significance:</strong> {ps.significance}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
          </div>
        </aside>
      </div>
    </div>
  );
}
