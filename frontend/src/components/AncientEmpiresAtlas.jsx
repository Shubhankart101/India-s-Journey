import { useState, useMemo, useEffect, useRef } from 'react';
import empiresData from '../data/ancient-empires.json';
import { assetUrl } from '../config.js';
import './AncientEmpiresAtlas.css';

const PAN_INDIA_VIEWBOX = { x: 600, y: -380, w: 380, h: 330 };
const ALEX_VIEWBOX = { x: 160, y: -480, w: 600, h: 290 };

const HISTORICAL_VARIANTS = {
  'classical-southern-dynasties': [
    { svg: 'maps/historical/sangam-age.svg', title: 'Tamilakam — Sangam Age (c. 300 BCE – 300 CE)' },
    { svg: 'maps/historical/pallava-empire.svg', title: 'Pallava Ascendancy (c. 300 – 900 CE)' },
    { svg: 'maps/historical/chola-empire.svg', title: 'Imperial Cholas (c. 985 – 1150 CE)' },
    { svg: 'maps/historical/chalukya-rashtrakuta.svg', title: 'Chālukyas & Rāṣṭrakūṭas (c. 543 – 982 CE)' },
  ],
  'mahajanapadas': [
    { svg: 'maps/historical/mahajanapadas.svg', title: 'Sixteen Mahājanapadas (c. 600–345 BCE)' },
    { svg: 'maps/historical/later-vedic.svg', title: 'Later Vedic Janapadas (c. 1100–600 BCE)' },
  ],
  'magadha-nanda': [
    { svg: 'maps/historical/mahajanapadas.svg', title: 'Sixteen Mahājanapadas & Magadha (c. 600–345 BCE)' },
    { svg: 'maps/historical/later-vedic.svg', title: 'Later Vedic Janapadas (c. 1100–600 BCE)' },
  ],
  'indo-greek-shunga': [
    { svg: 'maps/historical/post-mauryan-indo-greek.svg', title: 'Śuṅgas, Greeks & Śakas (c. 185 BCE – 50 CE)' },
    { svg: 'maps/historical/mauryan-empire.svg', title: 'Mauryan Age Context (c. 322–185 BCE)' },
  ],
};

export function HistoricalMapViewer({ svgUrl, title, onFallbackToInteractive }) {
  const [svgContent, setSvgContent] = useState('');
  const [error, setError] = useState(false);

  useEffect(() => {
    let active = true;
    setError(false);
    setSvgContent('');

    const cleanPath = String(svgUrl || '')
      .replace(/^\/+/, '')
      .replace(/^India-s-Journey\//i, '');
    const filename = cleanPath.split('/').pop();
    const candidateUrls = Array.from(new Set([
      svgUrl,
      `/India-s-Journey/${cleanPath}`,
      `/${cleanPath}`,
      `./${cleanPath}`,
      `/India-s-Journey/maps/historical/${filename}`,
      `/maps/historical/${filename}`,
      `./maps/historical/${filename}`,
    ].filter(Boolean)));

    async function tryFetch() {
      for (const u of candidateUrls) {
        try {
          const res = await fetch(u);
          if (res.ok) {
            const text = await res.text();
            if (active && text.includes('<svg')) {
              const clean = text.replace(/<\?xml[^>]*\?>/gi, '').trim();
              setSvgContent(clean);
              return;
            }
          }
        } catch {
          // continue
        }
      }
      if (active) setError(true);
    }

    tryFetch();
    return () => { active = false; };
  }, [svgUrl]);

  if (error) {
    return (
      <div className="ahm-error-fallback">
        <p className="ahm-error-msg">Historical atlas for <strong>{title}</strong> is currently unavailable in this view.</p>
        {onFallbackToInteractive && (
          <button type="button" className="btn btn-primary" onClick={onFallbackToInteractive}>
            Switch to Interactive Geospatial Workbench →
          </button>
        )}
      </div>
    );
  }

  if (!svgContent) {
    return <div className="ahm-loading">Loading authentic historical atlas…</div>;
  }

  return (
    <div
      className="ahm-svg-inline"
      dangerouslySetInnerHTML={{ __html: svgContent }}
    />
  );
}

export default function AncientEmpiresAtlas({
  initialEmpireId = null,
  selectedEmpireId: controlledEmpireId,
  onSelectEmpire: controlledOnSelectEmpire,
}) {
  const [mapPaths, setMapPaths] = useState([]);
  const [internalEmpireId, setInternalEmpireId] = useState(initialEmpireId || empiresData.empires[3].id); // default to Maurya
  const selectedEmpireId = controlledEmpireId !== undefined ? controlledEmpireId : internalEmpireId;
  const [selectedPhaseIndex, setSelectedPhaseIndex] = useState(0);
  const [selectedBattle, setSelectedBattle] = useState(null);
  const [selectedCapital, setSelectedCapital] = useState(null);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [hoveredCapital, setHoveredCapital] = useState(null);
  const [hoveredLocation, setHoveredLocation] = useState(null);
  const [hoveredBattle, setHoveredBattle] = useState(null);
  const [hoveredTerritory, setHoveredTerritory] = useState(null);
  const [hoveredNeighbor, setHoveredNeighbor] = useState(null);
  const [selectedVariantSvg, setSelectedVariantSvg] = useState(null);
  const [tooltip, setTooltip] = useState(null);
  const [mapViewMode, setMapViewMode] = useState('interactive'); // 'interactive' | 'historical'
  const [dossierTab, setDossierTab] = useState('overview'); // 'overview' | 'history' | 'battles' | 'locations' | 'milestones' | 'sources'
  const [mapLayerFilter, setMapLayerFilter] = useState('all'); // 'all' | 'battles' | 'locations'
  const [showAllLabels, setShowAllLabels] = useState(false);
  const [locationTypeFilter, setLocationTypeFilter] = useState('all');
  const mapStageRef = useRef(null);

  const empires = empiresData.empires || [];

  const currentEmpire = useMemo(() => {
    return empires.find(e => e.id === selectedEmpireId) || empires[0];
  }, [empires, selectedEmpireId]);

  const allLocations = useMemo(() => {
    return currentEmpire.locations || currentEmpire.capitals || [];
  }, [currentEmpire]);

  const allBattles = useMemo(() => {
    return currentEmpire.battles || [];
  }, [currentEmpire]);

  const filteredLocations = useMemo(() => {
    if (locationTypeFilter === 'all') return allLocations;
    return allLocations.filter(loc => (loc.type || 'capital') === locationTypeFilter);
  }, [allLocations, locationTypeFilter]);

  const activePhase = useMemo(() => {
    const phases = currentEmpire.boundary_phases || [];
    return phases[selectedPhaseIndex] || phases[0];
  }, [currentEmpire, selectedPhaseIndex]);

  const defaultViewBox = useMemo(() => {
    if (currentEmpire.viewbox) return currentEmpire.viewbox;
    return currentEmpire.id === 'alexander-campaign' ? ALEX_VIEWBOX : PAN_INDIA_VIEWBOX;
  }, [currentEmpire]);

  const [viewBox, setViewBox] = useState(defaultViewBox);

  // Switch viewbox when empire changes
  useEffect(() => {
    setViewBox(defaultViewBox);
  }, [defaultViewBox]);

  // Load vector basemap using assetUrl
  useEffect(() => {
    fetch(assetUrl('maps/world-asia.json'))
      .then(res => res.json())
      .then(data => {
        if (data && data.paths) {
          const targetIsos = new Set(['IND', 'PAK', 'AFG', 'IRQ', 'IRN', 'OMN', 'KWT', 'ARE', 'SAU', 'QAT', 'BHR', 'TKM', 'UZB', 'TJK', 'SYR', 'NPL', 'BTN', 'BGD', 'LKA', 'MMR', 'GRC', 'TUR', 'EGY']);
          const relevant = data.paths.filter(p => targetIsos.has(p.i));
          setMapPaths(relevant);
        }
      })
      .catch(() => {});
  }, []);

  const handleEmpireSelect = (id) => {
    if (controlledOnSelectEmpire) controlledOnSelectEmpire(id);
    setInternalEmpireId(id);
    setSelectedPhaseIndex(0);
    setSelectedBattle(null);
    setSelectedCapital(null);
    setSelectedLocation(null);
    setSelectedVariantSvg(null);
    setHoveredCapital(null);
    setHoveredLocation(null);
    setHoveredBattle(null);
    setHoveredTerritory(null);
    setHoveredNeighbor(null);
    setTooltip(null);
    setMapLayerFilter('all');
    setLocationTypeFilter('all');
  };

  const handleZoom = (factor) => {
    setViewBox(curr => {
      const nw = Math.max(100, Math.min(800, curr.w * factor));
      const nh = Math.max(70, Math.min(600, curr.h * factor));
      const nx = curr.x + (curr.w - nw) / 2;
      const ny = curr.y + (curr.h - nh) / 2;
      return { x: nx, y: ny, w: nw, h: nh };
    });
  };

  const handleMouseMove = (e) => {
    if (!mapStageRef.current) return;
    const rect = mapStageRef.current.getBoundingClientRect();
    const activeHover = hoveredLocation || hoveredCapital || hoveredBattle || hoveredTerritory || hoveredNeighbor;
    if (activeHover) {
      setTooltip({
        x: Math.max(10, Math.min(rect.width - 240, e.clientX - rect.left + 15)),
        y: Math.max(10, Math.min(rect.height - 150, e.clientY - rect.top - 10)),
        data: activeHover,
      });
    } else {
      setTooltip(null);
    }
  };

  const variants = HISTORICAL_VARIANTS[currentEmpire.id] || [];
  const currentHistoricalSvg = selectedVariantSvg || currentEmpire.historical_map_svg;

  return (
    <div className="empires-atlas">
      {/* Header */}
      <header className="empires-atlas-header">
        <div className="empires-title-group">
          <span className="empires-tag">OFFICIAL HISTORICAL & GEOSPATIAL ATLAS (600 BCE – 850 CE)</span>
          <h2>Empires of Ancient India: Dynastic Atlases, Battles & Inscriptions</h2>
          <p className="empires-lead">
            Explore 10 major imperial eras from the 16 Mahajanapadas to the Classical Golden Ages.
            Featuring authentic geospatial territory boundaries, Alexander the Great's trans-continental Macedonian campaign,
            decisive battlefield coordinates, and primary epigraphic charters in Ashokan Brahmi, Classical Sanskrit,
            Ancient Greek, and Sangam Old Tamil.
          </p>
        </div>
      </header>

      {/* Empire Chronology Selector Strip */}
      <nav className="empires-timeline-strip" aria-label="Imperial dynasties chronology">
        {empires.map(emp => {
          const isSelected = emp.id === selectedEmpireId;
          const isAlex = emp.id === 'alexander-campaign';
          return (
            <button
              key={emp.id}
              type="button"
              className={`timeline-chip ${isSelected ? 'active' : ''} ${isAlex ? 'chip-special' : ''}`}
              onClick={() => handleEmpireSelect(emp.id)}
            >
              {isAlex && <span className="chip-badge">SPECIAL MENTION</span>}
              <span className="chip-title">{emp.name}</span>
              <span className="chip-period">{emp.period}</span>
            </button>
          );
        })}
      </nav>

      {/* View Mode Switcher */}
      <div className="empires-mode-bar" role="tablist" aria-label="Atlas Display Mode">
        <button
          type="button"
          role="tab"
          aria-selected={mapViewMode === 'interactive'}
          className={`empires-mode-btn ${mapViewMode === 'interactive' ? 'active' : ''}`}
          onClick={() => setMapViewMode('interactive')}
        >
          🧭 Interactive Geospatial Workbench (Phases &amp; Battles)
        </button>
        {currentEmpire.historical_map_svg && (
          <button
            type="button"
            role="tab"
            aria-selected={mapViewMode === 'historical'}
            className={`empires-mode-btn ${mapViewMode === 'historical' ? 'active' : ''}`}
            onClick={() => setMapViewMode('historical')}
          >
            📜 Authentic Historical Atlas (Tapas Banerjee Cartography)
          </button>
        )}
      </div>

      {/* Main Interactive Map & Dossier */}
      <div className="empires-workbench">
        {/* Map Container */}
        <div
          className="empires-map-container"
          ref={mapStageRef}
          onMouseMove={handleMouseMove}
          onMouseLeave={() => { setHoveredCapital(null); setHoveredBattle(null); setHoveredTerritory(null); setHoveredNeighbor(null); setTooltip(null); }}
        >
          {mapViewMode === 'historical' && currentEmpire.historical_map_svg ? (
            <div className="authentic-historical-map-frame">
              <div className="ahm-toolbar">
                <span className="ahm-title">{currentEmpire.historical_map_title || currentEmpire.name}</span>
                <span className="ahm-credit">Open-source South Asian Historical Atlas · Tapas Banerjee</span>
              </div>
              {variants.length > 1 && (
                <div className="ahm-variant-selector" role="group" aria-label="Atlas Map Variations">
                  {variants.map(v => (
                    <button
                      key={v.svg}
                      type="button"
                      className={`ahm-var-btn ${currentHistoricalSvg === v.svg ? 'active' : ''}`}
                      onClick={() => setSelectedVariantSvg(v.svg)}
                    >
                      {v.title.split('—')[1] || v.title.split('(')[0] || v.title}
                    </button>
                  ))}
                </div>
              )}
              <HistoricalMapViewer
                svgUrl={assetUrl(currentHistoricalSvg)}
                title={currentEmpire.historical_map_title || currentEmpire.name}
                onFallbackToInteractive={() => setMapViewMode('interactive')}
              />
            </div>
          ) : (
            <>
              <div className="empires-map-toolbar">
                {/* Phase Selector for changing boundaries */}
                {currentEmpire.boundary_phases.length > 1 && (
                  <div className="phase-selector" role="group" aria-label="Territorial Phases">
                    <span className="ps-label">Phase:</span>
                    {currentEmpire.boundary_phases.map((ph, idx) => (
                      <button
                        key={idx}
                        type="button"
                        className={`ps-btn ${selectedPhaseIndex === idx ? 'active' : ''}`}
                        onClick={() => setSelectedPhaseIndex(idx)}
                      >
                        {ph.year}
                      </button>
                    ))}
                  </div>
                )}

                {/* Map Layer Selector Toolbar (All / Battles / Locations) */}
                <div className="map-layer-selector" role="group" aria-label="Map Layer Toggle">
                  <button
                    type="button"
                    className={`mls-btn ${mapLayerFilter === 'all' ? 'active' : ''}`}
                    onClick={() => setMapLayerFilter('all')}
                    title="Display all battles and historical locations on map"
                  >
                    🌐 All ({allBattles.length + allLocations.length})
                  </button>
                  <button
                    type="button"
                    className={`mls-btn ${mapLayerFilter === 'battles' ? 'active' : ''}`}
                    onClick={() => setMapLayerFilter('battles')}
                    title="Display only decisive military battles"
                  >
                    ⚔ Battles ({allBattles.length})
                  </button>
                  <button
                    type="button"
                    className={`mls-btn ${mapLayerFilter === 'locations' ? 'active' : ''}`}
                    onClick={() => setMapLayerFilter('locations')}
                    title="Display only imperial capitals, citadels, ports and academies"
                  >
                    🏛 Locations ({allLocations.length})
                  </button>
                  <button
                    type="button"
                    className={`mls-btn ${showAllLabels ? 'active' : ''}`}
                    onClick={() => setShowAllLabels(!showAllLabels)}
                    title="Toggle label density (Smart mode shows capitals and selected sites to avoid map clutter)"
                    aria-pressed={showAllLabels}
                  >
                    🏷️ {showAllLabels ? 'Labels: All' : 'Labels: Smart'}
                  </button>
                </div>

                {/* Zoom Controls */}
                <div className="map-zoom-btns">
                  <button type="button" onClick={() => handleZoom(0.8)} title="Zoom In" aria-label="Zoom in">+</button>
                  <button type="button" onClick={() => handleZoom(1.25)} title="Zoom Out" aria-label="Zoom out">−</button>
                  <button type="button" onClick={() => setViewBox(defaultViewBox)} title="Reset View" aria-label="Reset view">⟲</button>
                </div>
              </div>

              <svg
                className="empires-svg"
                viewBox={`${viewBox.x} ${viewBox.y} ${viewBox.w} ${viewBox.h}`}
                preserveAspectRatio="xMidYMid meet"
              >
                <defs>
                  <filter id="empShadow" x="-10%" y="-10%" width="120%" height="120%">
                    <feDropShadow dx="0" dy="2" stdDeviation="3" floodColor="#000" floodOpacity="0.7" />
                  </filter>
                  <filter id="glowRoute" x="-20%" y="-20%" width="140%" height="140%">
                    <feDropShadow dx="0" dy="0" stdDeviation="2" floodColor="#38bdf8" floodOpacity="0.8" />
                  </filter>
                </defs>

                {/* Ocean / Background */}
                <rect x={viewBox.x - 400} y={viewBox.y - 400} width={viewBox.w + 800} height={viewBox.h + 800} fill="#0a0d13" />

                {/* Basemap Countries */}
                <g className="empires-basemap">
                  {mapPaths.map((p, idx) => (
                    <path
                      key={idx}
                      d={p.d}
                      fill="#151b24"
                      stroke="#232e3d"
                      strokeWidth="0.75"
                      vectorEffect="non-scaling-stroke"
                    />
                  ))}
                </g>

                {/* Ancient River Courses (Ganges, Indus, Yamuna, Narmada, Godavari, Kaveri) */}
                <g className="empires-rivers" stroke="#1d4ed8" strokeWidth="1.2" fill="none" opacity="0.55" strokeLinecap="round" vectorEffect="non-scaling-stroke">
                  {/* Ganges */}
                  <path d="M 780 -300 Q 820 -275 850 -255 T 880 -235" />
                  {/* Indus */}
                  <path d="M 730 -340 Q 710 -310 685 -280 T 680 -250" />
                  {/* Narmada */}
                  <path d="M 730 -220 Q 770 -218 805 -215" strokeDasharray="3,2" />
                </g>

                {/* Imperial Boundary Polygon with Animation */}
                {activePhase && (
                  <g className="empire-territory-layer">
                    <path
                      d={activePhase.territory_path}
                      fill={activePhase.color || '#a855f7'}
                      fillOpacity="0.38"
                      stroke={activePhase.color || '#a855f7'}
                      strokeWidth="2.5"
                      strokeLinejoin="round"
                      filter="url(#empShadow)"
                      vectorEffect="non-scaling-stroke"
                      tabIndex={0}
                      role="button"
                      aria-label={`${currentEmpire.name} territory in ${activePhase.year}`}
                      onMouseEnter={() => setHoveredTerritory({
                        type: 'territory',
                        title: currentEmpire.name,
                        year: activePhase.year,
                        phase: activePhase.phase,
                        desc: activePhase.description,
                        color: activePhase.color,
                      })}
                      onMouseLeave={() => setHoveredTerritory(null)}
                      style={{ cursor: 'pointer', transition: 'fill-opacity 0.2s ease, stroke-width 0.2s ease' }}
                    />
                  </g>
                )}

                {/* Alexander's Campaign March Route (Special Mention) */}
                {currentEmpire.campaign_route && (
                  <g className="alexander-route-layer">
                    <path
                      d={currentEmpire.campaign_route}
                      fill="none"
                      stroke="#38bdf8"
                      strokeWidth="2.5"
                      strokeDasharray="5,3"
                      filter="url(#glowRoute)"
                      vectorEffect="non-scaling-stroke"
                      tabIndex={0}
                      role="button"
                      aria-label="Alexander the Great Macedonian Campaign Route"
                      onMouseEnter={() => setHoveredTerritory({
                        type: 'route',
                        title: "Alexander's Macedonian Campaign Route",
                        year: '334 – 323 BCE',
                        desc: '30,000+ km expedition from Pella across Anatolia, Egypt, Mesopotamia, Persepolis, Bactria, and the Hindu Kush into the Punjab/Indus basin.',
                        color: '#38bdf8',
                      })}
                      onMouseLeave={() => setHoveredTerritory(null)}
                      style={{ cursor: 'pointer' }}
                    />
                  </g>
                )}

                {/* Neighboring Realms Labels */}
                {currentEmpire.neighboring_kingdoms && (
                  <g className="neighboring-realms">
                    {currentEmpire.neighboring_kingdoms.map((nb, idx) => (
                      <g
                        key={idx}
                        className="neighbor-pin"
                        onMouseEnter={() => setHoveredNeighbor({ type: 'neighbor', title: nb.name, desc: nb.desc })}
                        onMouseLeave={() => setHoveredNeighbor(null)}
                        style={{ cursor: 'pointer' }}
                      >
                        {nb.pos && (
                          <text
                            x={nb.pos.x}
                            y={nb.pos.y}
                            fill="#94a3b8"
                            fontSize="6"
                            fontFamily="sans-serif"
                            fontWeight="700"
                            letterSpacing="0.08em"
                            textAnchor="middle"
                            stroke="#0b0f15"
                            strokeWidth="2"
                            paintOrder="stroke"
                          >
                            {nb.name.toUpperCase()}
                          </text>
                        )}
                      </g>
                    ))}
                  </g>
                )}

                {/* Historical Locations & Capitals Layer */}
                {(mapLayerFilter === 'all' || mapLayerFilter === 'locations') && (
                  <g className="locations-layer">
                    {filteredLocations.map((loc, idx) => {
                      const isLocSelected = selectedLocation?.name === loc.name || selectedCapital?.name === loc.name;
                      const locType = loc.type || 'capital';
                      
                      let markerColor = '#facc15';
                      if (locType === 'port') markerColor = '#38bdf8';
                      else if (locType === 'university') markerColor = '#c084fc';
                      else if (locType === 'citadel') markerColor = '#fb923c';
                      else if (locType === 'sacred_site') markerColor = '#34d399';
                      else if (locType === 'republic_assembly') markerColor = '#e879f9';
                      else if (locType === 'provincial_seat') markerColor = '#94a3b8';

                      return (
                        <g
                          key={`loc-${idx}`}
                          className={`location-pin loc-type-${locType} ${isLocSelected ? 'active-pin' : ''}`}
                          transform={`translate(${loc.x}, ${loc.y})`}
                          onClick={() => {
                            setSelectedLocation(loc);
                            setSelectedCapital(locType === 'capital' ? loc : null);
                            setSelectedBattle(null);
                            setDossierTab('locations');
                          }}
                          onMouseEnter={() => setHoveredLocation({
                            type: locType,
                            title: loc.name,
                            role: loc.role,
                            desc: loc.desc || loc.role
                          })}
                          onMouseLeave={() => setHoveredLocation(null)}
                          style={{ cursor: 'pointer' }}
                          tabIndex={0}
                          role="button"
                          aria-label={`${loc.name} (${locType}): ${loc.role || ''}`}
                        >
                          {isLocSelected && (
                            <circle r="9" fill="none" stroke={markerColor} strokeWidth="1.5" strokeDasharray="2,2" className="pin-pulse" />
                          )}
                          <circle r={locType === 'capital' ? "4.5" : "3.5"} fill={markerColor} stroke="#000" strokeWidth="1.2" />
                          {locType === 'capital' && <circle r="1.5" fill="#000" />}
                          <text
                            y={locType === 'capital' ? "-6" : "-5"}
                            fill={isLocSelected ? "#ffffff" : markerColor}
                            fontSize={locType === 'capital' ? "4.8" : "4.2"}
                            fontWeight={locType === 'capital' ? "800" : "700"}
                            fontFamily="sans-serif"
                            textAnchor="middle"
                            stroke="#0b0f15"
                            strokeWidth="1.8"
                            paintOrder="stroke"
                            opacity={(showAllLabels || locType === 'capital' || isLocSelected || hoveredLocation?.title === loc.name) ? 1 : 0}
                            pointerEvents={(showAllLabels || locType === 'capital' || isLocSelected || hoveredLocation?.title === loc.name) ? 'auto' : 'none'}
                          >
                            {locType === 'capital' ? `★ ${loc.name}` : loc.name}
                          </text>
                        </g>
                      );
                    })}
                  </g>
                )}

                {/* Battles Markers (Crossed Swords ⚔) */}
                {(mapLayerFilter === 'all' || mapLayerFilter === 'battles') && allBattles.length > 0 && (
                  <g className="battles-layer">
                    {allBattles.map((bt, idx) => {
                      const isSelected = selectedBattle?.name === bt.name;
                      return (
                        <g
                          key={`bt-${idx}`}
                          className={`battle-pin ${isSelected ? 'active' : ''}`}
                          transform={`translate(${bt.coords.x}, ${bt.coords.y})`}
                          onClick={() => { setSelectedBattle(bt); setSelectedLocation(null); setSelectedCapital(null); setDossierTab('battles'); }}
                          onMouseEnter={() => setHoveredBattle({ type: 'battle', title: bt.name, year: bt.year, parties: bt.parties, summary: bt.summary, source: bt.source })}
                          onMouseLeave={() => setHoveredBattle(null)}
                          style={{ cursor: 'pointer' }}
                          tabIndex={0}
                          role="button"
                          aria-label={`Historic battle: ${bt.name}`}
                        >
                          {isSelected && (
                            <circle r="11" fill="none" stroke="#ef4444" strokeWidth="1.5" strokeDasharray="3,2" className="pin-pulse" />
                          )}
                          <circle r={isSelected ? "8" : "6"} fill="#ef4444" fillOpacity={isSelected ? "0.95" : "0.85"} stroke="#ffffff" strokeWidth="1.2" />
                          <text
                            y="2"
                            fill="#ffffff"
                            fontSize="5"
                            fontWeight="900"
                            textAnchor="middle"
                          >
                            ⚔
                          </text>
                          <text
                            y="12"
                            fill={isSelected ? "#fca5a5" : "#f87171"}
                            fontSize="4.5"
                            fontWeight="750"
                            fontFamily="sans-serif"
                            textAnchor="middle"
                            stroke="#0b0f15"
                            strokeWidth="1.8"
                            paintOrder="stroke"
                            opacity={(showAllLabels || isSelected || hoveredBattle?.title === bt.name || allBattles.length <= 4) ? 1 : 0}
                            pointerEvents={(showAllLabels || isSelected || hoveredBattle?.title === bt.name || allBattles.length <= 4) ? 'auto' : 'none'}
                          >
                            {bt.name}
                          </text>
                        </g>
                      );
                    })}
                  </g>
                )}
              </svg>

              {/* Interactive Floating Tooltip */}
              {tooltip && (
                <div className="empires-floating-tooltip" style={{ left: tooltip.x, top: tooltip.y }}>
                  <div className="eft-tag">
                    {tooltip.data.type === 'battle' ? '⚔ DECISIVE HISTORIC BATTLE' :
                     tooltip.data.type === 'capital' ? '★ IMPERIAL CAPITAL' :
                     tooltip.data.type === 'port' ? '⚓ MARITIME PORT' :
                     tooltip.data.type === 'university' ? '📜 UNIVERSITY & MONASTERY' :
                     tooltip.data.type === 'citadel' ? '🏛 FORTIFIED CITADEL' :
                     tooltip.data.type === 'sacred_site' ? '☸ SACRED SANCTUARY' :
                     tooltip.data.type === 'republic_assembly' ? '⚖ GANA-SANGHA REPUBLIC ASSEMBLY' :
                     tooltip.data.type === 'provincial_seat' ? '📍 PROVINCIAL HEADQUARTERS' :
                     tooltip.data.type === 'territory' ? '🏛 EMPIRE REALM' :
                     tooltip.data.type === 'neighbor' ? '🌍 FRONTIER REALM' :
                     tooltip.data.type === 'route' ? '🧭 MARCH ROUTE' : 'INFO'}
                  </div>
                  <strong className="eft-title">{tooltip.data.title}</strong>
                  {tooltip.data.year && <span className="eft-year"> ({tooltip.data.year})</span>}
                  {tooltip.data.phase && <p className="eft-phase"><strong>Phase:</strong> {tooltip.data.phase}</p>}
                  {tooltip.data.parties && <p className="eft-parties"><strong>Forces:</strong> {tooltip.data.parties}</p>}
                  {tooltip.data.role && <p className="eft-role"><strong>Role:</strong> {tooltip.data.role}</p>}
                  <p className="eft-desc">{tooltip.data.summary || tooltip.data.desc}</p>
                </div>
              )}

              {/* Map Footer Legend */}
              <div className="empires-map-legend">
                <span><strong style={{ color: activePhase.color }}>■</strong> {currentEmpire.name} ({activePhase.year})</span>
                <span><strong style={{ color: '#facc15' }}>★</strong> Capital</span>
                <span><strong style={{ color: '#fb923c' }}>🏛</strong> Citadel</span>
                <span><strong style={{ color: '#38bdf8' }}>⚓</strong> Port</span>
                <span><strong style={{ color: '#c084fc' }}>📜</strong> Academy</span>
                <span><strong style={{ color: '#34d399' }}>☸</strong> Sacred</span>
                <span><strong style={{ color: '#ef4444' }}>⚔</strong> Battle</span>
                {currentEmpire.campaign_route && <span><strong style={{ color: '#38bdf8' }}>- -</strong> Macedonian Route</span>}
              </div>
            </>
          )}
        </div>

        {/* Rich Empire Dossier Sidebar with Tabbed Navigation (Zero Overflow) */}
        <aside className="empire-dossier" aria-label="Imperial details">
          {/* Pinned Top Bar: Hero + Tab Navigation (NEVER scrolls away or clips) */}
          <div className="empire-dossier-pinned-header">
            {/* Empire Header */}
            <div className="dossier-hero">
              <span className="dossier-era-badge">{currentEmpire.era_type}</span>
              <h3 className="dossier-emp-name">
                {currentEmpire.name}
                {currentEmpire.name_hi && <span className="dossier-emp-hi" lang="hi">({currentEmpire.name_hi})</span>}
              </h3>
              <p className="dossier-meta">
                <strong>Period:</strong> {currentEmpire.period} · <strong>Ideology / Faith:</strong> {currentEmpire.religion}
              </p>
            </div>

            {/* Dossier Tabs (Permanently pinned & clearly visible) */}
            <div className="dossier-tab-bar" role="tablist" aria-label="Imperial Dossier Sections">
              <button
                type="button"
                role="tab"
                aria-selected={dossierTab === 'overview'}
                className={`dossier-tab-btn ${dossierTab === 'overview' ? 'active' : ''}`}
                onClick={() => setDossierTab('overview')}
              >
                📜 Overview &amp; Epigraph
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={dossierTab === 'history'}
                className={`dossier-tab-btn ${dossierTab === 'history' ? 'active' : ''}`}
                onClick={() => setDossierTab('history')}
              >
                📖 History &amp; Quotes ({currentEmpire.detailed_history?.primary_sources?.length || 0})
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={dossierTab === 'battles'}
                className={`dossier-tab-btn ${dossierTab === 'battles' ? 'active' : ''}`}
                onClick={() => setDossierTab('battles')}
              >
                ⚔ Battles ({allBattles.length})
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={dossierTab === 'locations'}
                className={`dossier-tab-btn ${dossierTab === 'locations' ? 'active' : ''}`}
                onClick={() => setDossierTab('locations')}
              >
                🏛 Locations &amp; Cities ({allLocations.length})
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={dossierTab === 'milestones'}
                className={`dossier-tab-btn ${dossierTab === 'milestones' ? 'active' : ''}`}
                onClick={() => setDossierTab('milestones')}
              >
                ⏳ Milestones ({currentEmpire.events?.length || 0})
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={dossierTab === 'sources'}
                className={`dossier-tab-btn ${dossierTab === 'sources' ? 'active' : ''}`}
                onClick={() => setDossierTab('sources')}
              >
                📚 Sources
              </button>
            </div>
          </div>

          {/* Scrollable Tab Content Container */}
          <div className="empire-dossier-scroll-body">
            {/* TAB 1: Overview & Epigraph */}
            {dossierTab === 'overview' && (
              <div className="dossier-tab-content">
                {/* Capital Inspector Card if pinned */}
                {selectedCapital && (
                  <div className="capital-alert-card">
                    <div className="cac-header">
                      <span className="cac-tag">★ IMPERIAL CAPITAL INSPECTOR</span>
                      <button type="button" className="cac-close" onClick={() => setSelectedCapital(null)} aria-label="Close capital details">×</button>
                    </div>
                    <h4>{selectedCapital.name}</h4>
                    <p><strong>Administrative Role:</strong> {selectedCapital.role}</p>
                    {selectedCapital.desc && <p className="cac-desc">{selectedCapital.desc}</p>}
                  </div>
                )}

                {/* Streamlined Dynastic History Bridge */}
                {currentEmpire.detailed_history && (
                  <div className="empire-history-bridge">
                    <button
                      type="button"
                      className="empire-history-btn"
                      onClick={() => setDossierTab('history')}
                      title="Read complete dynastic history and primary epigraphic charters"
                    >
                      <span className="ehb-icon">📖</span>
                      <span className="ehb-text">
                        Read Full <strong>{currentEmpire.name}</strong> Chronicle &amp; Quoted Epigraphs ({currentEmpire.detailed_history.primary_sources?.length || 0})
                      </span>
                      <span className="ehb-arrow">→</span>
                    </button>
                  </div>
                )}

                {/* Territorial Phase Summary */}
              <div className="dossier-box">
                <h4>Territorial Phase: {activePhase.phase}</h4>
                <p>{activePhase.description}</p>
              </div>

              {/* Original Script & Language Shloka / Epigraph */}
              {currentEmpire.shloka_epigraph && (
                <div className="epigraph-card">
                  <div className="epigraph-header">
                    <span className="epigraph-badge">ORIGINAL EPIGRAPHIC TESTIMONY</span>
                    <span className="epigraph-lang">{currentEmpire.shloka_epigraph.lang} ({currentEmpire.shloka_epigraph.script})</span>
                  </div>

                  {/* Inscription in Original Script */}
                  <blockquote className="epigraph-original" lang="sa">
                    {currentEmpire.shloka_epigraph.text}
                  </blockquote>

                  {/* Transliteration if available */}
                  {currentEmpire.shloka_epigraph.transliteration && (
                    <p className="epigraph-translit">
                      <em>{currentEmpire.shloka_epigraph.transliteration}</em>
                    </p>
                  )}

                  {/* Translation */}
                  <p className="epigraph-translation">
                    <strong>Translation:</strong> {currentEmpire.shloka_epigraph.translation}
                  </p>

                  <div className="epigraph-cite-box">
                    <span className="epigraph-source">Citation: {currentEmpire.shloka_epigraph.citation}</span>
                    <span className="epigraph-verified">Verified from: {currentEmpire.shloka_epigraph.verified_from}</span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB: Detailed History & Quoted Primary Epigraphic Sources */}
          {dossierTab === 'history' && (
            <div className="dossier-tab-content">
              {currentEmpire.detailed_history ? (
                <>
                  {/* Detailed Overview */}
                  <div className="dossier-box history-overview-box">
                    <h4>Imperial Era &amp; Historical Trajectory</h4>
                    <p className="history-overview-text">{currentEmpire.detailed_history.overview}</p>
                  </div>

                  {/* Dynastic Chronicle */}
                  {currentEmpire.detailed_history.chronicle && (
                    <div className="dossier-section chronicle-section">
                      <h4>Dynastic Phases &amp; Historical Trajectory</h4>
                      <div className="chronicle-timeline">
                        {currentEmpire.detailed_history.chronicle.map((ch, idx) => (
                          <div key={idx} className="chronicle-card">
                            <span className="chronicle-era-badge">{ch.era}</span>
                            <p className="chronicle-narrative">{ch.narrative}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Primary Source Documentation Quoted Directly */}
                  {currentEmpire.detailed_history.primary_sources && (
                    <div className="dossier-section primary-sources-section">
                      <h4>Authentic Primary Epigraphic &amp; Classical Documentation</h4>
                      <div className="primary-sources-list">
                        {currentEmpire.detailed_history.primary_sources.map((ps, idx) => (
                          <div key={idx} className="primary-quote-card">
                            <div className="pqc-header">
                              <span className="pqc-badge">{ps.type || 'Epigraph'}</span>
                              <span className="pqc-script">{ps.script || 'Sanskrit / Brahmi'}</span>
                            </div>
                            <h5 className="pqc-title">{ps.source_title || ps.title}</h5>
                            <div className="pqc-meta">
                              {(ps.author || ps.ruler) && <span><strong>Author/Ruler:</strong> {ps.author || ps.ruler}</span>}
                              {ps.date && <span> · <strong>Date:</strong> {ps.date}</span>}
                            </div>

                            {/* Inscription in Original Script */}
                            {ps.original_text && (
                              <blockquote className="pqc-original">
                                {ps.original_text}
                              </blockquote>
                            )}

                            {/* Transliteration */}
                            {ps.transliteration && (
                              <div className="pqc-translit">
                                <span className="pqc-sublabel">Transliteration (IAST / Romanized):</span>
                                <p><em>{ps.transliteration}</em></p>
                              </div>
                            )}

                            {/* Translation */}
                            {ps.translation && (
                              <div className="pqc-translation">
                                <span className="pqc-sublabel">English Translation:</span>
                                <p>“{ps.translation}”</p>
                              </div>
                            )}

                            {/* Academic Citation & Significance */}
                            <div className="pqc-footer">
                              {ps.academic_citation && (
                                <p className="pqc-citation">
                                  <strong>Academic Citation:</strong> {ps.academic_citation}
                                </p>
                              )}
                              {(ps.historical_significance || ps.significance) && (
                                <p className="pqc-significance">
                                  <strong>Historical Significance:</strong> {ps.historical_significance || ps.significance}
                                </p>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div className="dossier-box">
                  <p>Detailed historical documentation is being compiled for this empire.</p>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: Major Military Campaigns & Battles */}
          {dossierTab === 'battles' && (
            <div className="dossier-tab-content">
              {/* Battle Details Card */}
              {selectedBattle && (
                <div className="battle-alert-card">
                  <div className="bac-header">
                    <span className="bac-tag">⚔ DECISIVE HISTORICAL BATTLE</span>
                    <button type="button" className="bac-close" onClick={() => setSelectedBattle(null)} aria-label="Close battle details">×</button>
                  </div>
                  <h4>{selectedBattle.name} ({selectedBattle.year})</h4>
                  <p><strong>Forces / Parties:</strong> {selectedBattle.parties}</p>
                  <p><strong>Tactical Summary:</strong> {selectedBattle.summary}</p>
                  <p className="bac-source"><strong>Official Source:</strong> {selectedBattle.source}</p>
                </div>
              )}

              {allBattles.length > 0 && (
                <div className="dossier-section">
                  <h4>Major Campaigns &amp; Clashes (Click to highlight on map)</h4>
                  <div className="battles-list">
                    {allBattles.map((bt, idx) => (
                      <div
                        key={idx}
                        className={`battle-list-item ${selectedBattle?.name === bt.name ? 'selected' : ''}`}
                        onClick={() => { setSelectedBattle(bt); setSelectedLocation(null); setSelectedCapital(null); }}
                      >
                        <span className="bli-swords">⚔</span>
                        <div className="bli-content">
                          <strong>{bt.name} ({bt.year})</strong>
                          <p className="bli-desc">{bt.summary}</p>
                          <span className="bli-parties"><strong>Opponents:</strong> {bt.parties}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB: Imperial Locations, Citadels & Seaports */}
          {dossierTab === 'locations' && (
            <div className="dossier-tab-content">
              {/* Location Details Card */}
              {selectedLocation && (
                <div className="capital-alert-card location-alert-card">
                  <div className="cac-header">
                    <span className="cac-tag">
                      {selectedLocation.type === 'capital' ? '★ IMPERIAL CAPITAL' :
                       selectedLocation.type === 'port' ? '⚓ MARITIME PORT' :
                       selectedLocation.type === 'university' ? '📜 UNIVERSITY & MONASTERY' :
                       selectedLocation.type === 'citadel' ? '🏛 FORTIFIED CITADEL' :
                       selectedLocation.type === 'sacred_site' ? '☸ SACRED SANCTUARY' :
                       selectedLocation.type === 'republic_assembly' ? '⚖ GANA-SANGHA REPUBLIC' :
                       selectedLocation.type === 'provincial_seat' ? '📍 PROVINCIAL HEADQUARTERS' : '🏛 HISTORICAL LOCATION'}
                    </span>
                    <button type="button" className="cac-close" onClick={() => setSelectedLocation(null)} aria-label="Close location details">×</button>
                  </div>
                  <h4>{selectedLocation.name}</h4>
                  <p><strong>Administrative Role:</strong> {selectedLocation.role}</p>
                  {selectedLocation.desc && <p className="cac-desc">{selectedLocation.desc}</p>}
                </div>
              )}

              {/* Type Filter Pills */}
              <div className="location-type-pills" role="group" aria-label="Filter locations by type">
                {[
                  { id: 'all', label: 'All Sites' },
                  { id: 'capital', label: '★ Capitals' },
                  { id: 'citadel', label: '🏛 Citadels' },
                  { id: 'port', label: '⚓ Ports' },
                  { id: 'university', label: '📜 Academies' },
                  { id: 'sacred_site', label: '☸ Sacred Sites' }
                ].map(t => (
                  <button
                    key={t.id}
                    type="button"
                    className={`lt-pill ${locationTypeFilter === t.id ? 'active' : ''}`}
                    onClick={() => setLocationTypeFilter(t.id)}
                  >
                    {t.label}
                  </button>
                ))}
              </div>

              {/* Locations List */}
              <div className="dossier-section">
                <h4>Imperial Cities, Citadels &amp; Emporia (Click to highlight on map)</h4>
                <div className="locations-list">
                  {filteredLocations.map((loc, idx) => {
                    const isLocSelected = selectedLocation?.name === loc.name;
                    return (
                      <div
                        key={idx}
                        className={`location-list-item ${isLocSelected ? 'selected' : ''}`}
                        onClick={() => {
                          setSelectedLocation(loc);
                          setSelectedCapital(loc.type === 'capital' ? loc : null);
                          setSelectedBattle(null);
                        }}
                      >
                        <span className="lli-icon">
                          {loc.type === 'capital' ? '★' :
                           loc.type === 'port' ? '⚓' :
                           loc.type === 'university' ? '📜' :
                           loc.type === 'citadel' ? '🏛' :
                           loc.type === 'sacred_site' ? '☸' :
                           loc.type === 'republic_assembly' ? '⚖' : '📍'}
                        </span>
                        <div className="lli-content">
                          <div className="lli-top">
                            <strong>{loc.name}</strong>
                            <span className="lli-type-tag">{loc.type || 'capital'}</span>
                          </div>
                          <p className="lli-role">{loc.role}</p>
                          {loc.desc && <p className="lli-desc">{loc.desc}</p>}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: Historical Events Timeline */}
          {dossierTab === 'milestones' && (
            <div className="dossier-tab-content">
              {currentEmpire.events && (
                <div className="dossier-section">
                  <h4>Dynastic Chronology &amp; Major Milestones</h4>
                  <ul className="events-timeline">
                    {currentEmpire.events.map((ev, idx) => (
                      <li key={idx}>
                        <span className="ev-year">{ev.year}</span>
                        <div className="ev-body">
                          <strong className="ev-title">{ev.title}</strong>
                          {ev.desc && <p className="ev-desc">{ev.desc}</p>}
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* TAB 4: Academic Sources */}
          {dossierTab === 'sources' && (
            <div className="dossier-tab-content">
              {currentEmpire.sources && (
                <div className="dossier-section dossier-sources">
                  <h4>Official Scholarly Research &amp; Epigraphic Sources</h4>
                  <div className="sources-list">
                    {currentEmpire.sources.map((src, idx) => (
                      <div key={idx} className="source-citation-card">
                        <span className="scc-year">{src.year}</span>
                        <h5 className="scc-title">{src.title}</h5>
                        <p className="scc-authors">{src.author || src.authors}</p>
                        <p className="scc-pub">{src.publisher}</p>
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
