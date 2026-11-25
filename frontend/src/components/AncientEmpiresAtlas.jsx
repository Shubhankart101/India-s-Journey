import { useState, useMemo, useEffect, useRef } from 'react';
import empiresData from '../data/ancient-empires.json';
import { assetUrl } from '../config.js';
import { useTheme } from '../theme.js';
import './AncientEmpiresAtlas.css';

const PAN_INDIA_VIEWBOX = { x: 600, y: -380, w: 380, h: 330 };
const ALEX_VIEWBOX = { x: 185, y: -450, w: 635, h: 245 };
const DARK_THEME_IDS = new Set(['dark', 'military', 'parliamentary', 'airforce']);

const EMPIRE_BENCHMARKS = [
  { id: 'mahajanapadas', label: '16 Mahajanapadas', area: 1.1, reign: 255, army: 90 },
  { id: 'magadha-nanda', label: 'Magadha & Nanda', area: 1.8, reign: 222, army: 200 },
  { id: 'alexander-campaign', label: 'Alexander (Macedon)', area: 5.2, reign: 11, army: 47 },
  { id: 'maurya-empire', label: 'Mauryan Empire', area: 5.0, reign: 137, army: 600 },
  { id: 'indo-greek-shunga', label: 'Indo-Greeks & Shungas', area: 1.2, reign: 175, army: 85 },
  { id: 'satavahana-empire', label: 'Satavahana Empire', area: 2.2, reign: 450, army: 100 },
  { id: 'kushan-empire', label: 'Kushan Empire', area: 3.0, reign: 345, army: 140 },
  { id: 'gupta-empire', label: 'Gupta Golden Age', area: 3.5, reign: 231, army: 180 },
  { id: 'harsha-empire', label: 'Harsha Empire', area: 2.5, reign: 41, army: 100 },
  { id: 'classical-southern-dynasties', label: 'Southern Dynasties', area: 1.5, reign: 400, army: 120 },
];

// Deterministic radial de-collision when multiple events fall on the same city coordinate
function computeDeCollidedEvents(events) {
  const buckets = new Map();
  for (let i = 0; i < events.length; i++) {
    const ev = events[i];
    if (!ev?.coords) continue;
    const key = `${Math.round(ev.coords.x)},${Math.round(ev.coords.y)}`;
    if (!buckets.has(key)) buckets.set(key, []);
    buckets.get(key).push(i);
  }
  return events.map((ev, i) => {
    if (!ev?.coords) return { ev, idx: i, dx: 0, dy: 0, colliding: false };
    const key = `${Math.round(ev.coords.x)},${Math.round(ev.coords.y)}`;
    const group = buckets.get(key) || [i];
    if (group.length <= 1) return { ev, idx: i, dx: 0, dy: 0, colliding: false };
    const pos = group.indexOf(i);
    const angle = (2 * Math.PI * pos) / group.length - Math.PI / 4;
    const radius = group.length > 3 ? 6.2 : 4.5;
    return {
      ev,
      idx: i,
      dx: Math.cos(angle) * radius,
      dy: Math.sin(angle) * radius,
      colliding: true,
    };
  });
}

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
  const [plateZoom, setPlateZoom] = useState(1);
  const [platePan, setPlatePan] = useState({ x: 0, y: 0 });
  const plateDragRef = useRef({ active: false, startX: 0, startY: 0, origPan: { x: 0, y: 0 } });

  useEffect(() => {
    let active = true;
    setError(false);
    setSvgContent('');
    setPlateZoom(1);
    setPlatePan({ x: 0, y: 0 });

    const cleanPath = String(svgUrl || '')
      .replace(/^\/+/, '')
      .replace(/^India-s-Journey\//i, '');
    const filename = cleanPath.split('/').pop();
    const candidateUrls = Array.from(new Set([
      assetUrl(`maps/historical/${filename}`),
      assetUrl(cleanPath),
      svgUrl,
      `/${cleanPath}`,
      `/India-s-Journey/${cleanPath}`,
      `/maps/historical/${filename}`,
      `/India-s-Journey/maps/historical/${filename}`,
      `./maps/historical/${filename}`,
      `./${cleanPath}`,
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
    <div className="ahm-viewer-shell">
      <div className="ahm-viewer-controls">
        <span className="ahm-zoom-readout">Scale: {Math.round(plateZoom * 100)}% · Drag plate to inspect detail</span>
        <div className="map-zoom-btns ahm-zoom-group">
          <button type="button" onClick={() => setPlateZoom(z => Math.min(2.6, +(z * 1.25).toFixed(2)))} title="Zoom In Historical Plate" aria-label="Zoom in historical map">+</button>
          <button type="button" onClick={() => setPlateZoom(z => Math.max(1, +(z / 1.25).toFixed(2)))} title="Zoom Out Historical Plate" aria-label="Zoom out historical map">−</button>
          <button type="button" onClick={() => { setPlateZoom(1); setPlatePan({ x: 0, y: 0 }); }} title="Reset Historical Plate" aria-label="Reset historical map">⟲</button>
        </div>
      </div>
      <div
        className="ahm-svg-inline"
        onPointerDown={(e) => {
          if (plateZoom <= 1) return;
          plateDragRef.current = { active: true, startX: e.clientX, startY: e.clientY, origPan: platePan };
        }}
        onPointerMove={(e) => {
          if (!plateDragRef.current.active) return;
          setPlatePan({
            x: plateDragRef.current.origPan.x + (e.clientX - plateDragRef.current.startX),
            y: plateDragRef.current.origPan.y + (e.clientY - plateDragRef.current.startY),
          });
        }}
        onPointerUp={() => { plateDragRef.current.active = false; }}
        onPointerLeave={() => { plateDragRef.current.active = false; }}
        style={{ cursor: plateZoom > 1 ? 'grab' : 'default' }}
      >
        <div
          className="ahm-svg-transform"
          style={{ transform: `translate(${platePan.x}px, ${platePan.y}px) scale(${plateZoom})`, transformOrigin: 'center center', transition: plateDragRef.current.active ? 'none' : 'transform 0.18s ease' }}
          dangerouslySetInnerHTML={{ __html: svgContent }}
        />
      </div>
    </div>
  );
}

export default function AncientEmpiresAtlas({
  initialEmpireId = null,
  selectedEmpireId: controlledEmpireId,
  onSelectEmpire: controlledOnSelectEmpire,
}) {
  const themeId = useTheme();
  const isDarkMap = DARK_THEME_IDS.has(themeId);
  const [mapPaths, setMapPaths] = useState([]);
  const [internalEmpireId, setInternalEmpireId] = useState(initialEmpireId || empiresData.empires[3].id); // default to Maurya
  const selectedEmpireId = controlledEmpireId !== undefined ? controlledEmpireId : internalEmpireId;
  const [selectedPhaseIndex, setSelectedPhaseIndex] = useState(0);
  const [selectedBattle, setSelectedBattle] = useState(null);
  const [selectedCapital, setSelectedCapital] = useState(null);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [activeEventIdx, setActiveEventIdx] = useState(0);
  const [hoveredCapital, setHoveredCapital] = useState(null);
  const [hoveredLocation, setHoveredLocation] = useState(null);
  const [hoveredBattle, setHoveredBattle] = useState(null);
  const [hoveredEvent, setHoveredEvent] = useState(null);
  const [hoveredTerritory, setHoveredTerritory] = useState(null);
  const [hoveredNeighbor, setHoveredNeighbor] = useState(null);
  const [selectedVariantSvg, setSelectedVariantSvg] = useState(null);
  const [tooltip, setTooltip] = useState(null);
  const [mapViewMode, setMapViewMode] = useState('interactive'); // 'interactive' | 'historical'
  const [dossierTab, setDossierTab] = useState('overview'); // 'overview' | 'history' | 'battles' | 'locations' | 'milestones' | 'sources'
  const [mapLayerFilter, setMapLayerFilter] = useState('all'); // 'all' | 'battles' | 'locations' | 'events'
  const [showAllLabels, setShowAllLabels] = useState(false);
  const [locationTypeFilter, setLocationTypeFilter] = useState('all');
  const mapStageRef = useRef(null);
  const dragRef = useRef({ active: false, moved: false, startX: 0, startY: 0, startVb: null });

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

  const allEvents = useMemo(() => {
    return currentEmpire.events || [];
  }, [currentEmpire]);

  const placedEvents = useMemo(() => {
    return computeDeCollidedEvents(allEvents);
  }, [allEvents]);

  const currentEvent = useMemo(() => {
    return allEvents[activeEventIdx] || allEvents[0] || null;
  }, [allEvents, activeEventIdx]);

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

  // Switch viewbox and reset active event when empire changes
  useEffect(() => {
    setViewBox(defaultViewBox);
    setActiveEventIdx(0);
  }, [defaultViewBox, selectedEmpireId]);

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
    setActiveEventIdx(0);
    setSelectedVariantSvg(null);
    setHoveredCapital(null);
    setHoveredLocation(null);
    setHoveredBattle(null);
    setHoveredEvent(null);
    setHoveredTerritory(null);
    setHoveredNeighbor(null);
    setTooltip(null);
    setMapLayerFilter('all');
    setLocationTypeFilter('all');
  };

  const focusCoords = (coords) => {
    if (!coords) return;
    setViewBox(curr => {
      const targetW = Math.min(curr.w, Math.max(150, defaultViewBox.w * 0.58));
      const targetH = Math.min(curr.h, Math.max(120, defaultViewBox.h * 0.58));
      return {
        x: coords.x - targetW / 2,
        y: coords.y - targetH / 2,
        w: targetW,
        h: targetH,
      };
    });
  };

  const handleZoom = (factor) => {
    setViewBox(curr => {
      const nw = Math.max(85, Math.min(800, curr.w * factor));
      const nh = Math.max(60, Math.min(600, curr.h * factor));
      const nx = curr.x + (curr.w - nw) / 2;
      const ny = curr.y + (curr.h - nh) / 2;
      return { x: nx, y: ny, w: nw, h: nh };
    });
  };

  const handleSvgPointerDown = (e) => {
    if (e.button !== 0 || e.target.closest('.location-pin, .battle-pin, .event-pin')) return;
    dragRef.current = { active: true, moved: false, startX: e.clientX, startY: e.clientY, startVb: viewBox };
  };

  const handleSvgPointerUp = () => {
    dragRef.current.active = false;
  };

  const handleMouseMove = (e) => {
    if (dragRef.current.active && mapStageRef.current && dragRef.current.startVb) {
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
      return;
    }
    if (!mapStageRef.current) return;
    const rect = mapStageRef.current.getBoundingClientRect();
    const activeHover = hoveredEvent || hoveredLocation || hoveredCapital || hoveredBattle || hoveredTerritory || hoveredNeighbor;
    if (activeHover) {
      setTooltip({
        x: Math.max(10, Math.min(rect.width - 285, e.clientX - rect.left + 15)),
        y: Math.max(10, Math.min(rect.height - 170, e.clientY - rect.top - 10)),
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
          onMouseLeave={() => {
            dragRef.current.active = false;
            setHoveredCapital(null);
            setHoveredLocation(null);
            setHoveredBattle(null);
            setHoveredEvent(null);
            setHoveredTerritory(null);
            setHoveredNeighbor(null);
            setTooltip(null);
          }}
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

                {/* Map Layer Selector Toolbar (All / Battles / Locations / Events) */}
                <div className="map-layer-selector" role="group" aria-label="Map Layer Toggle">
                  <button
                    type="button"
                    className={`mls-btn ${mapLayerFilter === 'all' ? 'active' : ''}`}
                    onClick={() => setMapLayerFilter('all')}
                    title="Display all battles, locations, and shloka event pins on map"
                  >
                    🌐 All ({allBattles.length + allLocations.length + allEvents.length})
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
                    className={`mls-btn ${mapLayerFilter === 'events' ? 'active' : ''}`}
                    onClick={() => { setMapLayerFilter('events'); setDossierTab('milestones'); }}
                    title="Display chronological events and classical shloka pins"
                  >
                    📜 Shloka Events ({allEvents.length})
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
                onPointerDown={handleSvgPointerDown}
                onPointerUp={handleSvgPointerUp}
                onPointerLeave={handleSvgPointerUp}
                style={{ cursor: dragRef.current.active ? 'grabbing' : 'grab' }}
              >
                <defs>
                  <filter id="empShadow" x="-10%" y="-10%" width="120%" height="120%">
                    <feDropShadow dx="0" dy="2" stdDeviation="3" floodColor="#000" floodOpacity="0.65" />
                  </filter>
                  <filter id="glowRoute" x="-20%" y="-20%" width="140%" height="140%">
                    <feDropShadow dx="0" dy="0" stdDeviation="2" floodColor="#38bdf8" floodOpacity="0.8" />
                  </filter>
                </defs>

                {/* Ocean / Background */}
                <rect x={viewBox.x - 400} y={viewBox.y - 400} width={viewBox.w + 800} height={viewBox.h + 800} fill={isDarkMap ? '#0a0d13' : '#d6e4ee'} />

                {/* Geographic Ocean & Range Watermarks */}
                <g className="empires-geo-labels" fontFamily="Georgia, serif" fontStyle="italic" pointerEvents="none">
                  <text x="675" y="-145" fill={isDarkMap ? '#38bdf8' : '#0369a1'} fontSize="6.5" opacity="0.34" letterSpacing="0.18em" textAnchor="middle">ARABIAN SEA</text>
                  <text x="865" y="-155" fill={isDarkMap ? '#38bdf8' : '#0369a1'} fontSize="6.5" opacity="0.34" letterSpacing="0.18em" textAnchor="middle">BAY OF BENGAL</text>
                  <text x="815" y="-315" fill={isDarkMap ? '#94a3b8' : '#78716c'} fontSize="5.4" opacity="0.38" letterSpacing="0.2em" textAnchor="middle" transform="rotate(14, 815, -315)">HIMALAYAS</text>
                </g>

                {/* Basemap Countries */}
                <g className="empires-basemap">
                  {mapPaths.map((p, idx) => (
                    <path
                      key={idx}
                      d={p.d}
                      fill={isDarkMap ? '#151b24' : '#f4efe3'}
                      stroke={isDarkMap ? '#232e3d' : '#c0b297'}
                      strokeWidth="0.75"
                      vectorEffect="non-scaling-stroke"
                    />
                  ))}
                </g>

                {/* Ancient River Courses (Ganges, Yamuna, Indus, Narmada, Godavari, Krishna, Kaveri) */}
                <g className="empires-rivers" stroke={isDarkMap ? '#2563eb' : '#0284c7'} strokeWidth="1.2" fill="none" opacity={isDarkMap ? '0.62' : '0.72'} strokeLinecap="round" vectorEffect="non-scaling-stroke">
                  {/* Ganga */}
                  <path d="M 780 -300 Q 820 -275 850 -255 T 885 -232" />
                  {/* Yamuna */}
                  <path d="M 772 -300 Q 778 -275 814 -253" strokeWidth="1" opacity="0.8" />
                  {/* Indus */}
                  <path d="M 745 -350 Q 716 -318 688 -276 T 678 -244" />
                  {/* Narmada */}
                  <path d="M 730 -218 Q 770 -220 808 -226" strokeDasharray="3,2" />
                  {/* Godavari */}
                  <path d="M 737 -198 Q 775 -190 818 -168" opacity="0.75" />
                  {/* Kaveri */}
                  <path d="M 762 -122 Q 782 -114 798 -111" opacity="0.75" />
                </g>
                <g className="empires-river-labels" fontSize="3.8" fontStyle="italic" fontWeight="600" fill={isDarkMap ? '#60a5fa' : '#0369a1'} opacity="0.8">
                  <text x="835" y="-263">Ganga</text>
                  <text x="698" y="-290">Indus</text>
                  <text x="765" y="-213">Narmada</text>
                  <text x="778" y="-176">Godavari</text>
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
                            fill={isDarkMap ? '#94a3b8' : '#475569'}
                            fontSize="5.4"
                            fontFamily="sans-serif"
                            fontWeight="700"
                            letterSpacing="0.06em"
                            textAnchor="middle"
                            stroke={isDarkMap ? '#0b0f15' : '#fffdf8'}
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
                      
                      let markerColor = isDarkMap ? '#facc15' : '#ca8a04';
                      let labelColor = isDarkMap ? '#facc15' : '#78350f';
                      if (locType === 'port') { markerColor = isDarkMap ? '#38bdf8' : '#0284c7'; labelColor = isDarkMap ? '#7dd3fc' : '#0369a1'; }
                      else if (locType === 'university') { markerColor = isDarkMap ? '#c084fc' : '#7e22ce'; labelColor = isDarkMap ? '#d8b4fe' : '#6b21a8'; }
                      else if (locType === 'citadel') { markerColor = isDarkMap ? '#fb923c' : '#c2410c'; labelColor = isDarkMap ? '#fdba74' : '#9a3412'; }
                      else if (locType === 'sacred_site') { markerColor = isDarkMap ? '#34d399' : '#047857'; labelColor = isDarkMap ? '#6ee7b7' : '#065f46'; }
                      else if (locType === 'republic_assembly') { markerColor = isDarkMap ? '#e879f9' : '#a21caf'; labelColor = isDarkMap ? '#f0abfc' : '#86198f'; }
                      else if (locType === 'provincial_seat') { markerColor = isDarkMap ? '#94a3b8' : '#475569'; labelColor = isDarkMap ? '#cbd5e1' : '#334155'; }

                      return (
                        <g
                          key={`loc-${idx}`}
                          className={`location-pin loc-type-${locType} ${isLocSelected ? 'active-pin' : ''}`}
                          transform={`translate(${loc.x}, ${loc.y})`}
                          onClick={() => {
                            if (dragRef.current.moved) return;
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
                          <circle r={locType === 'capital' ? "4.5" : "3.5"} fill={markerColor} stroke={isDarkMap ? "#000" : "#fff"} strokeWidth="1.2" />
                          {locType === 'capital' && <circle r="1.5" fill={isDarkMap ? "#000" : "#fff"} />}
                          <text
                            y={locType === 'capital' ? "-8.5" : "-5.5"}
                            fill={isLocSelected ? (isDarkMap ? "#ffffff" : "#0b0f15") : labelColor}
                            fontSize={locType === 'capital' ? "4.8" : "4.2"}
                            fontWeight={locType === 'capital' ? "800" : "700"}
                            fontFamily="sans-serif"
                            textAnchor="middle"
                            stroke={isDarkMap ? "#0b0f15" : "#fffdf8"}
                            strokeWidth="2"
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

                {/* Events & Shloka Storyboard Layer (with radial de-collision for same-city events) */}
                {(mapLayerFilter === 'all' || mapLayerFilter === 'events') && (
                  <g className="events-layer">
                    {placedEvents.map(({ ev, idx, dx, dy, colliding }) => {
                      if (!ev?.coords) return null;
                      const px = ev.coords.x + dx;
                      const py = ev.coords.y + dy;
                      const isEvSelected = idx === activeEventIdx;
                      const isEvHovered = hoveredEvent?.title === ev.title;
                      const nearCapital = mapLayerFilter === 'all' && allLocations.some(loc => loc.type === 'capital' && Math.hypot(loc.x - px, loc.y - py) < 10);
                      const showLabel = (mapLayerFilter === 'events' && (showAllLabels || isEvSelected || isEvHovered))
                        || (mapLayerFilter === 'all' && (isEvHovered || (isEvSelected && !nearCapital)));
                      return (
                        <g
                          key={`ev-${idx}-${ev.year}`}
                          className={`event-pin ${isEvSelected ? 'active' : ''}`}
                          transform={`translate(${px.toFixed(2)}, ${py.toFixed(2)})`}
                          onClick={() => {
                            if (dragRef.current.moved) return;
                            setActiveEventIdx(idx);
                            setDossierTab('milestones');
                          }}
                          onMouseEnter={() => setHoveredEvent({
                            type: 'event',
                            title: ev.title,
                            year: ev.year,
                            desc: ev.desc,
                            shlokaText: ev.shloka?.text,
                          })}
                          onMouseLeave={() => setHoveredEvent(null)}
                          style={{ cursor: 'pointer' }}
                          tabIndex={0}
                          role="button"
                          aria-label={`Event milestone: ${ev.title} (${ev.year})`}
                        >
                          {colliding && (
                            <line
                              x1={-dx}
                              y1={-dy}
                              x2="0"
                              y2="0"
                              stroke={isDarkMap ? '#fbbf24' : '#b45309'}
                              strokeWidth="0.65"
                              opacity="0.55"
                            />
                          )}
                          {isEvSelected && (
                            <circle r="10" fill="none" stroke={isDarkMap ? '#fbbf24' : '#b45309'} strokeWidth="1.6" strokeDasharray="3,2" className="pin-pulse" />
                          )}
                          <polygon
                            points={isEvSelected ? '0,-5.5 5.5,0 0,5.5 -5.5,0' : '0,-4.2 4.2,0 0,4.2 -4.2,0'}
                            fill={isEvSelected ? '#f59e0b' : '#fbbf24'}
                            stroke={isDarkMap ? '#0b0f15' : '#ffffff'}
                            strokeWidth="1.1"
                            opacity={mapLayerFilter === 'events' || isEvSelected ? 1 : 0.85}
                          />
                          {showLabel && (
                            <text
                              y="12.5"
                              fill={isDarkMap ? '#fde68a' : '#78350f'}
                              fontSize="4.2"
                              fontWeight="800"
                              fontFamily="sans-serif"
                              textAnchor="middle"
                              stroke={isDarkMap ? '#0b0f15' : '#fffdf8'}
                              strokeWidth="2.1"
                              paintOrder="stroke"
                            >
                              {ev.year}: {ev.place || ev.title.split(' ').slice(0, 3).join(' ')}
                            </text>
                          )}
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
                          onClick={() => { if (!dragRef.current.moved) { setSelectedBattle(bt); setSelectedLocation(null); setSelectedCapital(null); setDossierTab('battles'); } }}
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
                            fill={isDarkMap ? (isSelected ? "#fca5a5" : "#f87171") : (isSelected ? "#991b1b" : "#b91c1c")}
                            fontSize="4.5"
                            fontWeight="750"
                            fontFamily="sans-serif"
                            textAnchor="middle"
                            stroke={isDarkMap ? "#0b0f15" : "#fffdf8"}
                            strokeWidth="2"
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

                {/* Compass Rose & Scale Bar HUD */}
                <g className="emp-cartography-hud" transform={`translate(${viewBox.x + viewBox.w - 18}, ${viewBox.y + 18})`} pointerEvents="none" opacity="0.82">
                  <circle r="7.5" fill={isDarkMap ? 'rgba(15,23,42,0.72)' : 'rgba(255,255,255,0.82)'} stroke={isDarkMap ? '#64748b' : '#94a3b8'} strokeWidth="0.6" />
                  <polygon points="0,-5.8 1.6,0 0,-1.4 -1.6,0" fill="#d97706" />
                  <polygon points="0,5.8 1.6,0 0,1.4 -1.6,0" fill={isDarkMap ? '#64748b' : '#94a3b8'} />
                  <text y="-8.8" textAnchor="middle" fontSize="4.2" fontWeight="800" fill={isDarkMap ? '#f8fafc' : '#1e293b'}>N</text>
                </g>
                <g className="emp-scale-bar" transform={`translate(${viewBox.x + 12}, ${viewBox.y + viewBox.h - 10})`} pointerEvents="none" opacity="0.85">
                  <line x1="0" y1="0" x2="36" y2="0" stroke={isDarkMap ? '#cbd5e1' : '#334155'} strokeWidth="1.2" />
                  <line x1="0" y1="-2.2" x2="0" y2="2.2" stroke={isDarkMap ? '#cbd5e1' : '#334155'} strokeWidth="1.2" />
                  <line x1="36" y1="-2.2" x2="36" y2="2.2" stroke={isDarkMap ? '#cbd5e1' : '#334155'} strokeWidth="1.2" />
                  <text x="18" y="-3.2" textAnchor="middle" fontSize="3.8" fontWeight="700" fill={isDarkMap ? '#cbd5e1' : '#1e293b'} stroke={isDarkMap ? '#0a0d13' : '#d6e4ee'} strokeWidth="1.5" paintOrder="stroke">~400 km</text>
                </g>
              </svg>

              {/* Interactive Floating Tooltip */}
              {tooltip && (
                <div className="empires-floating-tooltip" style={{ left: tooltip.x, top: tooltip.y }}>
                  <div className="eft-tag">
                    {tooltip.data.type === 'battle' ? '⚔ DECISIVE HISTORIC BATTLE' :
                     tooltip.data.type === 'event' ? '📜 CHRONOLOGICAL MILESTONE & SHLOKA' :
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
                  {tooltip.data.shlokaText && <p className="eft-shloka" lang="sa">{tooltip.data.shlokaText}</p>}
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
                <span><strong style={{ color: '#f59e0b' }}>◆</strong> Shloka Event</span>
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
                aria-selected={dossierTab === 'metrics'}
                className={`dossier-tab-btn ${dossierTab === 'metrics' ? 'active' : ''}`}
                onClick={() => setDossierTab('metrics')}
              >
                📊 Metrics
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
                {filteredLocations.length === 0 ? (
                  <div className="locations-empty-box">
                    <p>No documented locations match the "{locationTypeFilter}" category for {currentEmpire.name}.</p>
                    <button type="button" className="btn btn-primary btn-small" onClick={() => setLocationTypeFilter('all')}>
                      Show All {allLocations.length} Sites
                    </button>
                  </div>
                ) : (
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
                )}
              </div>
            </div>
          )}

          {/* TAB: Imperial Comparative Metrics */}
          {dossierTab === 'metrics' && (
            <div className="dossier-tab-content empires-metrics-panel">
              <div className="dossier-box">
                <h4>Peak Territorial Extent Across 10 Imperial Eras (M km²)</h4>
                <p style={{ margin: '0 0 6px', fontSize: '0.74rem', color: 'var(--muted)' }}>
                  Click any dynasty row below to focus the interactive atlas and shloka milestones on that era.
                </p>
                <div className="emp-bench-list">
                  {EMPIRE_BENCHMARKS.map(b => {
                    const pct = Math.max(8, Math.round((b.area / 5.2) * 100));
                    const isCurrent = b.id === selectedEmpireId;
                    return (
                      <button
                        key={b.id}
                        type="button"
                        className={`emp-bench-row ${isCurrent ? 'active' : ''}`}
                        onClick={() => handleEmpireSelect(b.id)}
                      >
                        <div className="emp-bench-head">
                          <strong>{b.label}</strong>
                          <span className="emp-bench-vals">{b.area} M km² · {b.reign} yrs · {(b.army / 10).toFixed(0)}k+ inf</span>
                        </div>
                        <div className="emp-bench-track">
                          <div className="emp-bench-fill" style={{ width: `${pct}%` }} />
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
              <button
                type="button"
                className="btn btn-primary btn-small"
                onClick={() => document.getElementById('subgroup-quant-heading')?.scrollIntoView({ behavior: 'smooth' })}
              >
                Explore All 14 Interactive Charts &amp; Epigraphic Data Below ↓
              </button>
            </div>
          )}

          {/* TAB 3: Historical Events Timeline with Shlokas */}
          {dossierTab === 'milestones' && (
            <div className="dossier-tab-content">
              {allEvents.length > 0 && currentEvent && (
                <div className="event-shloka-spotlight">
                  <div className="ess-nav-bar">
                    <button
                      type="button"
                      className="ess-step-btn"
                      onClick={() => setActiveEventIdx(i => Math.max(0, i - 1))}
                      disabled={activeEventIdx === 0}
                    >
                      ← Prev Event
                    </button>
                    <span className="ess-counter">Event {activeEventIdx + 1} of {allEvents.length} · {currentEvent.year}</span>
                    <button
                      type="button"
                      className="ess-step-btn"
                      onClick={() => setActiveEventIdx(i => Math.min(allEvents.length - 1, i + 1))}
                      disabled={activeEventIdx >= allEvents.length - 1}
                    >
                      Next Event →
                    </button>
                  </div>
                  <div className="ess-body">
                    <div className="ess-meta-row">
                      {currentEvent.category && <span className="ess-cat">{currentEvent.category}</span>}
                      {currentEvent.place && <span className="ess-place">📍 {currentEvent.place}</span>}
                      {currentEvent.coords && (
                        <button
                          type="button"
                          className="ess-focus-btn"
                          onClick={() => focusCoords(currentEvent.coords)}
                        >
                          Focus Map →
                        </button>
                      )}
                    </div>
                    <h4 className="ess-title">{currentEvent.title}</h4>
                    <p className="ess-desc">{currentEvent.desc}</p>
                    {currentEvent.shloka && (
                      <div className="ess-shloka-card">
                        <span className="ess-shloka-lang">{currentEvent.shloka.lang || 'Classical Verse'}</span>
                        <blockquote className="ess-shloka-text" lang="sa">{currentEvent.shloka.text}</blockquote>
                        {currentEvent.shloka.transliteration && (
                          <p className="ess-shloka-translit"><em>{currentEvent.shloka.transliteration}</em></p>
                        )}
                        <p className="ess-shloka-translation">“{currentEvent.shloka.translation}”</p>
                        <span className="ess-shloka-cite">Source: {currentEvent.shloka.citation || currentEvent.shloka.source}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {currentEmpire.events && (
                <div className="dossier-section">
                  <h4>Dynastic Chronology &amp; Shloka-Defined Events ({allEvents.length})</h4>
                  <ul className="events-timeline">
                    {currentEmpire.events.map((ev, idx) => {
                      const isActive = idx === activeEventIdx;
                      return (
                        <li
                          key={idx}
                          className={isActive ? 'active-event-row' : ''}
                          onClick={() => {
                            setActiveEventIdx(idx);
                            if (ev.coords) focusCoords(ev.coords);
                          }}
                          style={{ cursor: 'pointer' }}
                        >
                          <span className="ev-year">{ev.year}</span>
                          <div className="ev-body">
                            <div className="ev-head-row">
                              <strong className="ev-title">{ev.title}</strong>
                              {ev.place && <span className="ev-place-chip">📍 {ev.place}</span>}
                            </div>
                            {ev.desc && <p className="ev-desc">{ev.desc}</p>}
                            {ev.shloka && (
                              <div className="ev-inline-shloka">
                                <span className="ev-shloka-verse" lang="sa">{ev.shloka.text}</span>
                                <span className="ev-shloka-meaning">— “{ev.shloka.translation}” <em>({ev.shloka.citation || ev.shloka.source})</em></span>
                              </div>
                            )}
                          </div>
                        </li>
                      );
                    })}
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
