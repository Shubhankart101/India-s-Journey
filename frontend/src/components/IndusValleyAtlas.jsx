import { useState, useMemo, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import sitesData from '../data/indus-civilisation.json';
import { assetUrl } from '../config.js';
import { useTheme } from '../theme.js';
import { HistoricalMapViewer } from './AncientEmpiresAtlas.jsx';
import './IndusAtlas.css';

const MAJOR_METROPOLIS_IDS = new Set(['rakhigarhi', 'mohenjo-daro', 'harappa', 'dholavira', 'ganweriwala', 'kalibangan', 'lothal', 'banawali']);
const FOREIGN_LABEL_IDS = new Set(['ur', 'qal-at-al-bahrain', 'ras-al-jinz', 'susa', 'shortugai']);
const DARK_THEME_IDS = new Set(['dark', 'military', 'parliamentary', 'airforce']);

// De-collide adjacent metropolis & Gulf anchor labels across the Harappan corridor
const METROPOLIS_LABEL_OFFSETS = {
  harappa: { dx: 0, dy: -9, anchor: 'middle' },
  kalibangan: { dx: -11, dy: -8, anchor: 'end', leader: true },
  banawali: { dx: -9, dy: -11, anchor: 'end', leader: true },
  rakhigarhi: { dx: 12, dy: 9, anchor: 'start', leader: true },
  ganweriwala: { dx: -10, dy: 9, anchor: 'end' },
  'mohenjo-daro': { dx: -10, dy: -7, anchor: 'end' },
  dholavira: { dx: -12, dy: -10, anchor: 'end', leader: true },
  lothal: { dx: 11, dy: 9, anchor: 'start' },
  ur: { dx: 0, dy: -8, anchor: 'middle' },
  susa: { dx: 10, dy: -4, anchor: 'start' },
  'qal-at-al-bahrain': { dx: -9, dy: 8, anchor: 'end' },
  'ras-al-jinz': { dx: 9, dy: 8, anchor: 'start' },
  shortugai: { dx: 0, dy: -8, anchor: 'middle' },
};

const BASIN_METRICS_DATA = [
  { basin: 'Cholistan (Saraswati–Hakra)', early: 139, mature: 174, late: 50 },
  { basin: 'Haryana, East Punjab & Doab', early: 245, mature: 218, late: 853 },
  { basin: 'Gujarat (Kutch & Saurashtra)', early: 14, mature: 290, late: 184 },
  { basin: 'Sindh & Lower Indus', early: 58, mature: 86, late: 12 },
];

function resolveRouteSvg(route, sites) {
  if (route.path_d) {
    return { d: route.path_d, mid: route.label_pos || null, pts: [] };
  }
  const wps = route.waypoints || [];
  if (wps.length < 2) return null;
  const pts = wps.map(wp => {
    const key = String(wp.name || '').split('(')[0].trim().toLowerCase();
    const match = sites.find(s =>
      s.id === key ||
      s.name.toLowerCase() === key ||
      s.name.toLowerCase().startsWith(key)
    );
    const x = match ? (match.x !== undefined ? match.x : match.lon * 10) : wp.x;
    const y = match ? (match.y !== undefined ? match.y : -match.lat * 10) : wp.y;
    return { x, y, name: wp.name };
  });
  let d = `M ${pts[0].x.toFixed(1)} ${pts[0].y.toFixed(1)}`;
  for (let i = 1; i < pts.length; i++) {
    const prev = pts[i - 1];
    const curr = pts[i];
    const mx = ((prev.x + curr.x) / 2);
    const my = ((prev.y + curr.y) / 2) + (route.type === 'maritime' ? 6 : -3);
    d += ` Q ${mx.toFixed(1)} ${my.toFixed(1)} ${curr.x.toFixed(1)} ${curr.y.toFixed(1)}`;
  }
  const midPt = pts[Math.floor(pts.length / 2)];
  return {
    d,
    mid: {
      x: midPt.x,
      y: route.type === 'maritime' ? midPt.y + 16 : route.type === 'overland' ? midPt.y - 12 : midPt.y + 13,
    },
    pts,
  };
}

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
  { id: 'heartland', label: 'Indus-Saraswati Heartland', vb: { x: 590, y: -415, w: 195, h: 165 } },
  { id: 'haryana-punjab', label: 'Haryana–Saraswati Core', vb: { x: 705, y: -350, w: 82, h: 58 } },
  { id: 'gujarat', label: 'Gujarat & Kutch', vb: { x: 670, y: -260, w: 90, h: 80 } },
  { id: 'meso', label: 'Gulf & Mesopotamia', vb: { x: 420, y: -380, w: 170, h: 140 } },
];

export default function IndusValleyAtlas() {
  const themeId = useTheme();
  const isDarkMap = DARK_THEME_IDS.has(themeId);
  const [mapPaths, setMapPaths] = useState([]);
  const [selectedSiteId, setSelectedSiteId] = useState('rakhigarhi');
  const [selectedPeriodId, setSelectedPeriodId] = useState('all');
  const [dossierTab, setDossierTab] = useState('site'); // 'site' | 'periods' | 'metrics'
  const [activeDossierPeriodId, setActiveDossierPeriodId] = useState('mature');
  const [tierFilter, setTierFilter] = useState('all');
  const [countryFilter, setCountryFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showRoutes, setShowRoutes] = useState(true);
  const [showRivers, setShowRivers] = useState(true);
  const [showAllSitesInRail, setShowAllSitesInRail] = useState(false);
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
            onMouseLeave={() => { dragRef.current.active = false; setHoveredSiteId(null); setTooltip(null); }}
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
              <marker id="ivcMaritimeArrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
                <path d="M 1 1.5 L 8.5 5 L 1 8.5 z" fill={isDarkMap ? '#38bdf8' : '#0284c7'} opacity="0.85" />
              </marker>
              <marker id="ivcCaravanArrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
                <path d="M 1 1.5 L 8.5 5 L 1 8.5 z" fill={isDarkMap ? '#fbbf24' : '#b45309'} opacity="0.85" />
              </marker>
            </defs>

            {/* Geographical Background */}
            <rect
              x={viewBox.x - 200}
              y={viewBox.y - 200}
              width={viewBox.w + 400}
              height={viewBox.h + 400}
              fill={isDarkMap ? '#0d1117' : '#d6e4ee'}
            />

            {/* Geographic Seas, Gulfs & Relief Labels */}
            <g className="indus-geo-labels" fontFamily="Georgia, serif" fontStyle="italic" pointerEvents="none">
              <text x="615" y="-205" fill={isDarkMap ? '#38bdf8' : '#0369a1'} fontSize="7" opacity="0.38" letterSpacing="0.2em" textAnchor="middle">ARABIAN SEA</text>
              <text x="530" y="-256" fill={isDarkMap ? '#38bdf8' : '#0369a1'} fontSize="4.5" opacity="0.48" letterSpacing="0.14em" textAnchor="middle">PERSIAN GULF</text>
              <text x="665" y="-365" fill={isDarkMap ? '#94a3b8' : '#78716c'} fontSize="5" opacity="0.42" letterSpacing="0.14em" textAnchor="middle">HINDU KUSH</text>
              <text x="642" y="-248" fill={isDarkMap ? '#7dd3fc' : '#0369a1'} fontSize="4" opacity="0.5" textAnchor="middle">Makran Coast</text>
            </g>

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
                {/* Euphrates–Tigris Basin */}
                <path d="M 432 -372 Q 448 -350 461 -326 Q 475 -315 486 -302" stroke={isDarkMap ? '#0ea5e9' : '#0369a1'} strokeWidth="1.4" opacity="0.65" />
                {/* Narmada / Tapi */}
                <path d="M 730 -216 Q 765 -218 795 -220" stroke={isDarkMap ? '#0284c7' : '#0369a1'} strokeWidth="1.2" opacity="0.55" />
                {/* River Labels */}
                <text x="698" y="-266" fill={isDarkMap ? '#7dd3fc' : '#0369a1'} fontSize="4.2" fontStyle="italic" fontWeight="600" opacity="0.88">Indus (Sindhu)</text>
                <text x="724" y="-281" fill={isDarkMap ? '#7dd3fc' : '#0284c7'} fontSize="4" fontStyle="italic" fontWeight="600" opacity="0.88">Saraswati–Hakra</text>
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

            {/* Maritime & Caravan Trade Routes (resolved directly onto true site coordinates) */}
            {showRoutes && (
              <g className="indus-routes">
                {tradeRoutes.map(route => {
                  const geom = resolveRouteSvg(route, sites);
                  if (!geom || !geom.d) return null;
                  const strokeCol = route.type === 'maritime'
                    ? (isDarkMap ? '#38bdf8' : '#0284c7')
                    : route.type === 'riverine'
                      ? (isDarkMap ? '#34d399' : '#047857')
                      : (isDarkMap ? '#fbbf24' : '#b45309');
                  const textCol = route.type === 'maritime'
                    ? (isDarkMap ? '#7dd3fc' : '#0369a1')
                    : route.type === 'riverine'
                      ? (isDarkMap ? '#6ee7b7' : '#065f46')
                      : (isDarkMap ? '#fde68a' : '#92400e');
                  const shortTag = route.type === 'maritime'
                    ? 'Meluhha–Dilmun–Ur Sea Lane'
                    : route.type === 'overland'
                      ? 'Lapis Lazuli Caravan'
                      : 'Saraswati Axis';
                  return (
                    <g
                      key={route.id}
                      className="indus-route-group"
                      onMouseEnter={(e) => {
                        if (!mapStageRef.current) return;
                        const rect = mapStageRef.current.getBoundingClientRect();
                        setTooltip({
                          x: Math.max(10, Math.min(rect.width - 255, e.clientX - rect.left + 15)),
                          y: Math.max(10, Math.min(rect.height - 155, e.clientY - rect.top - 10)),
                          route,
                        });
                      }}
                      onMouseLeave={() => setTooltip(null)}
                      style={{ cursor: 'pointer' }}
                    >
                      <path
                        d={geom.d}
                        fill="none"
                        stroke={strokeCol}
                        strokeWidth={route.type === 'maritime' ? '2.1' : '1.6'}
                        strokeDasharray={route.type === 'maritime' ? '5,3' : '3,3'}
                        opacity={isDarkMap ? '0.86' : '0.92'}
                        markerMid={route.type === 'maritime' ? 'url(#ivcMaritimeArrow)' : 'url(#ivcCaravanArrow)'}
                        vectorEffect="non-scaling-stroke"
                      />
                      {geom.mid && (
                        <text
                          x={geom.mid.x}
                          y={geom.mid.y}
                          fill={textCol}
                          fontSize="4.4"
                          fontFamily="sans-serif"
                          fontWeight="700"
                          textAnchor="middle"
                          stroke={isDarkMap ? '#0d1117' : '#f4efe3'}
                          strokeWidth="2.2"
                          paintOrder="stroke"
                          opacity="0.95"
                        >
                          {shortTag}
                        </text>
                      )}
                    </g>
                  );
                })}
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
                const isForeignAnchor = FOREIGN_LABEL_IDS.has(site.id);
                const isForeign = site.category === 'foreign_trade';
                const color = CATEGORY_COLORS[site.category] || '#94a3b8';

                // Label major metropolises, key foreign trade anchors, hovered, and active site
                const shouldShowLabel = isMajor || isForeignAnchor || isSelected || isHovered || filteredSites.length <= 12;

                return (
                  <g
                    key={site.id}
                    className={`indus-site-pin ${isSelected ? 'selected' : ''} ${isHovered ? 'hovered' : ''}`}
                    onClick={() => { if (!dragRef.current.moved) setSelectedSiteId(site.id); }}
                    onMouseEnter={() => setHoveredSiteId(site.id)}
                    onMouseLeave={() => setHoveredSiteId(null)}
                    style={{ cursor: 'pointer' }}
                  >
                    {isMajor && (
                      <circle cx={sx} cy={sy} r="10" fill="url(#metropolisGlow)" />
                    )}

                    {/* High-contrast pulse ring in BOTH dark and light themes */}
                    {isSelected && (
                      <circle
                        cx={sx}
                        cy={sy}
                        r={isMajor ? 8.5 : 6.5}
                        fill="none"
                        stroke={isDarkMap ? '#fef08a' : '#b45309'}
                        strokeWidth="1.8"
                        strokeDasharray="2.5,2"
                        className="pin-pulse"
                      />
                    )}

                    <circle
                      cx={sx}
                      cy={sy}
                      r={isMajor ? 5 : isForeign ? 4 : 3}
                      fill={color}
                      stroke={isSelected ? (isDarkMap ? '#ffffff' : '#0b0f15') : (isDarkMap ? '#0b0f15' : '#ffffff')}
                      strokeWidth={isSelected ? '2' : '1.1'}
                      filter="url(#siteShadow)"
                    />

                    <circle
                      cx={sx}
                      cy={sy}
                      r={isMajor ? 2 : 1.2}
                      fill="#0b0f15"
                    />

                    {shouldShowLabel && (() => {
                      const off = METROPOLIS_LABEL_OFFSETS[site.id] || { dx: 0, dy: -(isMajor ? 8 : 6), anchor: 'middle' };
                      const labelFill = isSelected
                        ? (isDarkMap ? '#ffffff' : '#0b0f15')
                        : isMajor
                          ? (isDarkMap ? '#fef08a' : '#78350f')
                          : isForeignAnchor
                            ? (isDarkMap ? '#6ee7b7' : '#065f46')
                            : (isDarkMap ? '#cbd5e1' : '#1e293b');
                      const labelStroke = isDarkMap ? '#0b0f15' : '#fffdf8';
                      const shortLabel = site.id === 'qal-at-al-bahrain'
                        ? 'Dilmun (Bahrain)'
                        : site.id === 'ras-al-jinz'
                          ? 'Ras al-Jinz (Magan)'
                          : site.id === 'ur'
                            ? 'Ur (Mesopotamia)'
                            : site.name.split('(')[0].trim();
                      return (
                        <g className="site-label-wrap">
                          {off.leader && (
                            <line
                              x1={sx}
                              y1={sy}
                              x2={sx + off.dx * 0.78}
                              y2={sy + off.dy * 0.72}
                              stroke={labelFill}
                              strokeWidth="0.6"
                              opacity="0.7"
                            />
                          )}
                          <text
                            x={sx + off.dx}
                            y={sy + off.dy}
                            fill={labelFill}
                            fontSize={isMajor ? '5.3' : '4.0'}
                            fontWeight={isMajor ? '750' : '650'}
                            fontFamily="sans-serif"
                            textAnchor={off.anchor}
                            stroke={labelStroke}
                            strokeWidth="2.3"
                            paintOrder="stroke"
                            strokeLinejoin="round"
                          >
                            {shortLabel}
                          </text>
                        </g>
                      );
                    })()}
                  </g>
                );
              })}
            </g>

            {/* Cartographic Compass Rose & Approximate Scale Indicator (Fixed to viewBox corners) */}
            <g className="map-cartography-hud" transform={`translate(${viewBox.x + viewBox.w - 18}, ${viewBox.y + 18})`} pointerEvents="none" opacity="0.82">
              <circle r="7.5" fill={isDarkMap ? 'rgba(15,23,42,0.72)' : 'rgba(255,255,255,0.82)'} stroke={isDarkMap ? '#64748b' : '#94a3b8'} strokeWidth="0.6" />
              <polygon points="0,-5.8 1.6,0 0,-1.4 -1.6,0" fill="#d97706" />
              <polygon points="0,5.8 1.6,0 0,1.4 -1.6,0" fill={isDarkMap ? '#64748b' : '#94a3b8'} />
              <text y="-8.8" textAnchor="middle" fontSize="4.2" fontWeight="800" fill={isDarkMap ? '#f8fafc' : '#1e293b'}>N</text>
            </g>
            <g className="map-scale-bar" transform={`translate(${viewBox.x + 12}, ${viewBox.y + viewBox.h - 10})`} pointerEvents="none" opacity="0.85">
              <line x1="0" y1="0" x2="45" y2="0" stroke={isDarkMap ? '#cbd5e1' : '#334155'} strokeWidth="1.2" />
              <line x1="0" y1="-2.2" x2="0" y2="2.2" stroke={isDarkMap ? '#cbd5e1' : '#334155'} strokeWidth="1.2" />
              <line x1="45" y1="-2.2" x2="45" y2="2.2" stroke={isDarkMap ? '#cbd5e1' : '#334155'} strokeWidth="1.2" />
              <text x="22.5" y="-3.2" textAnchor="middle" fontSize="3.8" fontWeight="700" fill={isDarkMap ? '#cbd5e1' : '#1e293b'} stroke={isDarkMap ? '#0d1117' : '#d6e4ee'} strokeWidth="1.5" paintOrder="stroke">~500 km</text>
            </g>
          </svg>

          {filteredSites.length === 0 && (
            <div className="ivc-empty-overlay">
              <p>No Harappan excavations match the current filter criteria.</p>
              <button
                type="button"
                className="btn btn-primary btn-small"
                onClick={() => { setSearchQuery(''); setTierFilter('all'); setCountryFilter('all'); setSelectedPeriodId('all'); }}
              >
                Reset All Filters
              </button>
            </div>
          )}

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
                  <div className="ift-tag" style={{ color: tooltip.route.type === 'maritime' ? '#38bdf8' : tooltip.route.type === 'riverine' ? '#10b981' : '#fbbf24' }}>
                    {tooltip.route.type === 'maritime' ? '⚓ MARITIME SEA LANE' : tooltip.route.type === 'riverine' ? '🌊 RIVERINE CORRIDOR' : '🐪 OVERLAND CARAVAN CORRIDOR'}
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
            <div className={`isr-chips ${showAllSitesInRail ? 'expanded' : ''}`}>
              {(showAllSitesInRail ? filteredSites : filteredSites.slice(0, 18)).map(s => (
                <button
                  key={s.id}
                  type="button"
                  className={`isr-chip ${s.id === selectedSiteId ? 'active' : ''}`}
                  onClick={() => { focusSite(s); setDossierTab('site'); }}
                >
                  {MAJOR_METROPOLIS_IDS.has(s.id) ? '★ ' : ''}{s.name}
                </button>
              ))}
              {filteredSites.length > 18 && (
                <button
                  type="button"
                  className="isr-chip isr-more-btn"
                  onClick={() => setShowAllSitesInRail(v => !v)}
                >
                  {showAllSitesInRail ? 'Show Compact ↑' : `+ Show All ${filteredSites.length}`}
                </button>
              )}
            </div>
          </div>

          {/* Quick Legend at bottom of map */}
          <div className="indus-map-legend">
            <span className="iml-item"><span className="iml-dot" style={{ background: CATEGORY_COLORS.metropolis }} /> Great Metropolis (8)</span>
            <span className="iml-item"><span className="iml-dot" style={{ background: CATEGORY_COLORS.port }} /> Port &amp; Dockyard</span>
            <span className="iml-item"><span className="iml-dot" style={{ background: CATEGORY_COLORS.craft }} /> Craft / Bead Hub</span>
            <span className="iml-item"><span className="iml-dot" style={{ background: CATEGORY_COLORS.foreign_trade }} /> Mesopotamian / Gulf</span>
            <span className="iml-item"><span className="iml-line blue" /> Maritime Route</span>
            <span className="iml-item"><span className="iml-line gold" /> Lapis Caravan</span>
            <span className="iml-item"><span className="iml-line emerald" /> Saraswati Axis</span>
          </div>
          </>
        )}
        </div>

        {/* Polished Detailed Excavation Dossier Sidebar */}
        <aside className="indus-site-dossier" aria-labelledby="dossier-site-title">
          {/* Dossier Tabs: Site vs Periods vs Basin Charts */}
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
            <button
              type="button"
              role="tab"
              aria-selected={dossierTab === 'metrics'}
              className={`dossier-tab-btn ${dossierTab === 'metrics' ? 'active' : ''}`}
              onClick={() => setDossierTab('metrics')}
            >
              📊 Basin Charts
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

          {/* TAB 3: Interactive Urban Area & Basin Settlement Shifts */}
          {dossierTab === 'metrics' && (
            <div className="dossier-inner ivc-metrics-panel">
              <div className="dossier-box">
                <h4>Top Excavated Urban Footprints (Hectares)</h4>
                <p className="ivc-metrics-sub">Click any city below to jump to its excavation dossier on the map.</p>
                <div className="ivc-bars-list">
                  {sites
                    .filter(s => s.area_hectares > 0)
                    .sort((a, b) => (b.area_hectares || 0) - (a.area_hectares || 0))
                    .slice(0, 8)
                    .map(s => {
                      const pct = Math.max(4, Math.min(100, Math.round(((s.area_hectares || 0) / 350) * 100)));
                      const active = s.id === selectedSiteId;
                      return (
                        <button
                          key={s.id}
                          type="button"
                          className={`ivc-bar-row ${active ? 'active' : ''}`}
                          onClick={() => focusSite(s)}
                        >
                          <div className="ivc-bar-meta">
                            <span>{s.name}</span>
                            <strong>{s.area_hectares} ha</strong>
                          </div>
                          <div className="ivc-bar-track">
                            <div className="ivc-bar-fill" style={{ width: `${pct}%` }} />
                          </div>
                        </button>
                      );
                    })}
                </div>
              </div>

              <div className="dossier-box">
                <h4>River Basin Settlement Shifts Across Harappan Eras</h4>
                <p className="ivc-metrics-sub">Possehl (2002) &amp; Mughal (1997) survey counts across Early, Mature, and Late phases.</p>
                <div className="ivc-basin-cards">
                  {BASIN_METRICS_DATA.map(row => (
                    <div key={row.basin} className="ivc-basin-row">
                      <strong className="ivc-basin-name">{row.basin}</strong>
                      <div className="ivc-basin-pills">
                        <span className="ibp early">Early: {row.early}</span>
                        <span className="ibp mature">Mature: {row.mature}</span>
                        <span className="ibp late">Late: {row.late}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <button
                type="button"
                className="btn btn-primary btn-small"
                onClick={() => document.getElementById('subgroup-quant-heading')?.scrollIntoView({ behavior: 'smooth' })}
              >
                Explore All 9 Statistical Charts Below ↓
              </button>
            </div>
          )}
          </div>
        </aside>
      </div>
    </div>
  );
}
