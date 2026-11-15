import { useState, useMemo, useEffect, useRef } from 'react';
import empiresData from '../data/ancient-empires.json';
import { assetUrl } from '../config.js';
import './AncientEmpiresAtlas.css';

const PAN_INDIA_VIEWBOX = { x: 600, y: -380, w: 380, h: 330 };
const ALEX_VIEWBOX = { x: 160, y: -480, w: 600, h: 290 };

export default function AncientEmpiresAtlas({ initialEmpireId = null }) {
  const [mapPaths, setMapPaths] = useState([]);
  const [selectedEmpireId, setSelectedEmpireId] = useState(initialEmpireId || empiresData.empires[3].id); // default to Maurya
  const [selectedPhaseIndex, setSelectedPhaseIndex] = useState(0);
  const [selectedBattle, setSelectedBattle] = useState(null);
  const [hoveredCapital, setHoveredCapital] = useState(null);
  const [hoveredBattle, setHoveredBattle] = useState(null);
  const [tooltip, setTooltip] = useState(null);
  const mapStageRef = useRef(null);

  const empires = empiresData.empires || [];

  const currentEmpire = useMemo(() => {
    return empires.find(e => e.id === selectedEmpireId) || empires[0];
  }, [empires, selectedEmpireId]);

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
    setSelectedEmpireId(id);
    setSelectedPhaseIndex(0);
    setSelectedBattle(null);
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
    if (hoveredCapital || hoveredBattle) {
      setTooltip({
        x: Math.max(10, e.clientX - rect.left + 15),
        y: Math.max(10, e.clientY - rect.top - 10),
        data: hoveredCapital || hoveredBattle
      });
    } else {
      setTooltip(null);
    }
  };

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

      {/* Main Interactive Map & Dossier */}
      <div className="empires-workbench">
        {/* SVG Interactive Map */}
        <div
          className="empires-map-container"
          ref={mapStageRef}
          onMouseMove={handleMouseMove}
          onMouseLeave={() => { setHoveredCapital(null); setHoveredBattle(null); setTooltip(null); }}
        >
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
                  fillOpacity="0.35"
                  stroke={activePhase.color || '#a855f7'}
                  strokeWidth="2.5"
                  strokeLinejoin="round"
                  filter="url(#empShadow)"
                  vectorEffect="non-scaling-stroke"
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
                  strokeWidth="2.2"
                  strokeDasharray="5,3"
                  filter="url(#glowRoute)"
                  vectorEffect="non-scaling-stroke"
                />
              </g>
            )}

            {/* Neighboring Realms Labels */}
            {currentEmpire.neighboring_kingdoms && (
              <g className="neighboring-realms">
                {currentEmpire.neighboring_kingdoms.map((nb, idx) => (
                  <text
                    key={idx}
                    x={nb.pos.x}
                    y={nb.pos.y}
                    fill="#64748b"
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
                ))}
              </g>
            )}

            {/* Imperial Capitals */}
            {currentEmpire.capitals && (
              <g className="capitals-layer">
                {currentEmpire.capitals.map((cap, idx) => (
                  <g
                    key={idx}
                    className="capital-pin"
                    transform={`translate(${cap.x}, ${cap.y})`}
                    onMouseEnter={() => setHoveredCapital({ type: 'capital', title: cap.name, desc: cap.role })}
                    onMouseLeave={() => setHoveredCapital(null)}
                    style={{ cursor: 'pointer' }}
                  >
                    <circle r="4" fill="#facc15" stroke="#000" strokeWidth="1.2" />
                    <circle r="1.5" fill="#000" />
                    <text
                      y="-6"
                      fill="#fef08a"
                      fontSize="5"
                      fontWeight="750"
                      fontFamily="sans-serif"
                      textAnchor="middle"
                      stroke="#0b0f15"
                      strokeWidth="2"
                      paintOrder="stroke"
                    >
                      ★ {cap.name}
                    </text>
                  </g>
                ))}
              </g>
            )}

            {/* Battles Markers (Crossed Swords ⚔) */}
            {currentEmpire.battles && (
              <g className="battles-layer">
                {currentEmpire.battles.map((bt, idx) => {
                  const isSelected = selectedBattle?.name === bt.name;
                  return (
                    <g
                      key={idx}
                      className={`battle-pin ${isSelected ? 'active' : ''}`}
                      transform={`translate(${bt.coords.x}, ${bt.coords.y})`}
                      onClick={() => setSelectedBattle(bt)}
                      onMouseEnter={() => setHoveredBattle({ type: 'battle', title: bt.name, year: bt.year, parties: bt.parties, summary: bt.summary })}
                      onMouseLeave={() => setHoveredBattle(null)}
                      style={{ cursor: 'pointer' }}
                    >
                      <circle r={isSelected ? "8" : "6"} fill="#ef4444" fillOpacity={isSelected ? "0.95" : "0.8"} stroke="#fff" strokeWidth="1.2" />
                      <text
                        y="2"
                        fill="#fff"
                        fontSize="5"
                        fontWeight="900"
                        textAnchor="middle"
                      >
                        ⚔
                      </text>
                      <text
                        y="12"
                        fill={isSelected ? "#fca5a5" : "#e2e8f0"}
                        fontSize="4.5"
                        fontWeight="700"
                        fontFamily="sans-serif"
                        textAnchor="middle"
                        stroke="#0b0f15"
                        strokeWidth="1.8"
                        paintOrder="stroke"
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
              <div className="eft-tag">{tooltip.data.type === 'battle' ? '⚔ BATTLE' : '★ IMPERIAL CAPITAL'}</div>
              <strong className="eft-title">{tooltip.data.title}</strong>
              {tooltip.data.year && <span className="eft-year"> ({tooltip.data.year})</span>}
              {tooltip.data.parties && <p className="eft-parties"><strong>Forces:</strong> {tooltip.data.parties}</p>}
              <p className="eft-desc">{tooltip.data.summary || tooltip.data.desc}</p>
            </div>
          )}

          {/* Map Footer Legend */}
          <div className="empires-map-legend">
            <span><strong style={{ color: activePhase.color }}>■</strong> {currentEmpire.name} ({activePhase.year})</span>
            <span><strong style={{ color: '#facc15' }}>★</strong> Imperial Capital</span>
            <span><strong style={{ color: '#ef4444' }}>⚔</strong> Historic Battle</span>
            {currentEmpire.campaign_route && <span><strong style={{ color: '#38bdf8' }}>- -</strong> Macedonian March Route</span>}
            <span><strong style={{ color: '#64748b' }}>ABC</strong> Frontier Kingdoms</span>
          </div>
        </div>

        {/* Rich Empire Dossier Sidebar */}
        <aside className="empire-dossier" aria-label="Imperial details">
          {/* Battle Details Card */}
          {selectedBattle && (
            <div className="battle-alert-card">
              <div className="bac-header">
                <span className="bac-tag">⚔ DECISIVE HISTORICAL BATTLE</span>
                <button type="button" className="bac-close" onClick={() => setSelectedBattle(null)} aria-label="Close battle details">×</button>
              </div>
              <h4>{selectedBattle.name} ({selectedBattle.year})</h4>
              <p><strong>Parties:</strong> {selectedBattle.parties}</p>
              <p><strong>Tactical Summary:</strong> {selectedBattle.summary}</p>
              <p className="bac-source"><strong>Official Source:</strong> {selectedBattle.source}</p>
            </div>
          )}

          {/* Empire Header */}
          <div className="dossier-hero">
            <span className="dossier-era-badge">{currentEmpire.era_type}</span>
            <h3 className="dossier-emp-name">
              {currentEmpire.name}
              {currentEmpire.name_hi && <span className="dossier-emp-hi" lang="hi">({currentEmpire.name_hi})</span>}
            </h3>
            <p className="dossier-meta">
              <strong>Period:</strong> {currentEmpire.period} · <strong>Religion / Ideology:</strong> {currentEmpire.religion}
            </p>
          </div>

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

          {/* Key Battles */}
          {currentEmpire.battles && (
            <div className="dossier-section">
              <h4>Major Military Campaigns & Battles</h4>
              <div className="battles-list">
                {currentEmpire.battles.map((bt, idx) => (
                  <div
                    key={idx}
                    className={`battle-list-item ${selectedBattle?.name === bt.name ? 'selected' : ''}`}
                    onClick={() => setSelectedBattle(bt)}
                  >
                    <span className="bli-swords">⚔</span>
                    <div>
                      <strong>{bt.name} ({bt.year})</strong>
                      <p className="bli-desc">{bt.summary}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Historical Events Timeline */}
          {currentEmpire.events && (
            <div className="dossier-section">
              <h4>Key Historical Milestones</h4>
              <ul className="events-timeline">
                {currentEmpire.events.map((ev, idx) => (
                  <li key={idx}>
                    <span className="ev-year">{ev.year}</span>
                    <span className="ev-title">{ev.title}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Official Academic Sources */}
          {currentEmpire.sources && (
            <div className="dossier-section dossier-sources">
              <h4>Official Scholarly Research & Epigraphic Sources</h4>
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
        </aside>
      </div>
    </div>
  );
}
