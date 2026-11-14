import { useState, useMemo, useEffect } from 'react';
import empiresData from '../data/ancient-empires.json';
import './AncientEmpiresAtlas.css';

// Projected bounding box for world-asia.json (covers Greece/Mesopotamia to Bengal/South India)
const BASE_VIEWBOX = { x: 440, y: -480, w: 420, h: 360 };

export default function AncientEmpiresAtlas({ initialEmpireId = null }) {
  const [mapPaths, setMapPaths] = useState([]);
  const [selectedEmpireId, setSelectedEmpireId] = useState(initialEmpireId || empiresData.empires[3].id); // default to Maurya
  const [selectedPhaseIndex, setSelectedPhaseIndex] = useState(0);
  const [selectedBattle, setSelectedBattle] = useState(null);
  const [viewBox, setViewBox] = useState(BASE_VIEWBOX);

  const empires = empiresData.empires || [];

  const currentEmpire = useMemo(() => {
    return empires.find(e => e.id === selectedEmpireId) || empires[0];
  }, [empires, selectedEmpireId]);

  const activePhase = useMemo(() => {
    const phases = currentEmpire.boundary_phases || [];
    return phases[selectedPhaseIndex] || phases[0];
  }, [currentEmpire, selectedPhaseIndex]);

  // Load vector basemap
  useEffect(() => {
    fetch('/maps/world-asia.json')
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
      const nw = Math.max(120, Math.min(600, curr.w * factor));
      const nh = Math.max(90, Math.min(450, curr.h * factor));
      const nx = curr.x + (curr.w - nw) / 2;
      const ny = curr.y + (curr.h - nh) / 2;
      return { x: nx, y: ny, w: nw, h: nh };
    });
  };

  return (
    <div className="empires-atlas">
      {/* Header */}
      <header className="empires-atlas-header">
        <div className="empires-title-group">
          <span className="empires-tag">OFFICIAL HISTORICAL & GEOSPATIAL ATLAS (600 BCE – 850 CE)</span>
          <h2>Empires of Ancient India: Geospatial Borders, Battles & Epigraphy</h2>
          <p className="empires-lead">
            Explore 10 major empires and eras following the Later Vedic period, including the 16 Mahajanapadas,
            the Mauryan pan-Indian state, Alexander the Great's Macedonian frontier campaign, the Gupta Golden Age,
            and the Classical Southern Dynasties. Track interactive changing borders, decisive battles, and original
            epigraphic inscriptions in Sanskrit, Ashokan Brahmi, Ancient Greek, and Sangam Tamil.
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
              {isAlex && <span className="chip-badge">SPECIAL</span>}
              <span className="chip-title">{emp.name}</span>
              <span className="chip-period">{emp.period}</span>
            </button>
          );
        })}
      </nav>

      {/* Main Interactive Map & Dossier */}
      <div className="empires-workbench">
        {/* SVG Interactive Map */}
        <div className="empires-map-container">
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
              <button type="button" onClick={() => handleZoom(0.8)} title="Zoom In">+</button>
              <button type="button" onClick={() => handleZoom(1.25)} title="Zoom Out">−</button>
              <button type="button" onClick={() => setViewBox(BASE_VIEWBOX)} title="Reset View">⟲</button>
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
            </defs>

            {/* Ocean / Background */}
            <rect x={viewBox.x - 300} y={viewBox.y - 300} width={viewBox.w + 600} height={viewBox.h + 600} fill="#0a0d13" />

            {/* Basemap Countries */}
            <g className="empires-basemap">
              {mapPaths.map((p, idx) => (
                <path
                  key={idx}
                  d={p.d}
                  fill="#151b24"
                  stroke="#232e3d"
                  strokeWidth="0.7"
                  vectorEffect="non-scaling-stroke"
                />
              ))}
            </g>

            {/* Major Sacred Rivers (Ganges, Indus, Yamuna, Narmada, Godavari, Kaveri) */}
            <g className="empires-rivers" stroke="#1d4ed8" strokeWidth="1.2" fill="none" opacity="0.5" strokeLinecap="round" vectorEffect="non-scaling-stroke">
              {/* Ganges */}
              <path d="M 680 -380 Q 720 -355 770 -335 T 805 -315" />
              {/* Indus */}
              <path d="M 650 -420 Q 630 -380 615 -345 T 605 -300" />
              {/* Narmada */}
              <path d="M 640 -300 Q 680 -295 725 -290" strokeDasharray="3,2" />
            </g>

            {/* Imperial Boundary Polygon with Animation */}
            {activePhase && (
              <g className="empire-territory-layer">
                <path
                  d={activePhase.territory_path}
                  fill={activePhase.color || '#a855f7'}
                  fillOpacity="0.32"
                  stroke={activePhase.color || '#a855f7'}
                  strokeWidth="2.5"
                  strokeLinejoin="round"
                  filter="url(#empShadow)"
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
                    fontSize="7"
                    fontFamily="sans-serif"
                    fontWeight="700"
                    letterSpacing="0.08em"
                    textAnchor="middle"
                    stroke="#0b0f15"
                    strokeWidth="2.5"
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
                  <g key={idx} className="capital-pin" transform={`translate(${cap.x}, ${cap.y})`}>
                    <circle r="4.5" fill="#facc15" stroke="#000" strokeWidth="1.5" />
                    <circle r="1.8" fill="#000" />
                    <text
                      y="-7"
                      fill="#fef08a"
                      fontSize="6"
                      fontWeight="750"
                      fontFamily="sans-serif"
                      textAnchor="middle"
                      stroke="#0b0f15"
                      strokeWidth="2.5"
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
                      style={{ cursor: 'pointer' }}
                    >
                      <circle r={isSelected ? "9" : "7"} fill="#ef4444" fillOpacity={isSelected ? "0.9" : "0.75"} stroke="#fff" strokeWidth="1.5" />
                      <text
                        y="2.5"
                        fill="#fff"
                        fontSize="6"
                        fontWeight="900"
                        textAnchor="middle"
                      >
                        ⚔
                      </text>
                      <text
                        y="14"
                        fill={isSelected ? "#fca5a5" : "#e2e8f0"}
                        fontSize="5"
                        fontWeight="700"
                        fontFamily="sans-serif"
                        textAnchor="middle"
                        stroke="#0b0f15"
                        strokeWidth="2"
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

          {/* Map Footer Legend */}
          <div className="empires-map-legend">
            <span><strong style={{ color: activePhase.color }}>■</strong> {currentEmpire.name} ({activePhase.year})</span>
            <span><strong style={{ color: '#facc15' }}>★</strong> Imperial Capital</span>
            <span><strong style={{ color: '#ef4444' }}>⚔</strong> Major Battle Site</span>
            <span><strong style={{ color: '#64748b' }}>ABC</strong> Neighboring Realms</span>
          </div>
        </div>

        {/* Rich Empire Dossier Sidebar */}
        <aside className="empire-dossier" aria-label="Imperial details">
          {/* Battle Popup if clicked */}
          {selectedBattle && (
            <div className="battle-alert-card">
              <div className="bac-header">
                <span className="bac-tag">⚔ DECISIVE HISTORICAL BATTLE</span>
                <button type="button" className="bac-close" onClick={() => setSelectedBattle(null)}>×</button>
              </div>
              <h4>{selectedBattle.name} ({selectedBattle.year})</h4>
              <p><strong>Location:</strong> {selectedBattle.location}</p>
              <p><strong>Commanders:</strong> {selectedBattle.commanders}</p>
              <p><strong>Outcome:</strong> {selectedBattle.outcome}</p>
              {selectedBattle.significance && <p><strong>Significance:</strong> {selectedBattle.significance}</p>}
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
            <p>{activePhase.notes}</p>
          </div>

          {/* Original Script & Language Shloka / Epigraph */}
          {currentEmpire.shloka_epigraph && (
            <div className="epigraph-card">
              <div className="epigraph-header">
                <span className="epigraph-badge">ORIGINAL EPIGRAPHIC TESTIMONY</span>
                <span className="epigraph-lang">{currentEmpire.shloka_epigraph.language} ({currentEmpire.shloka_epigraph.script})</span>
              </div>

              {/* Inscription in Original Script */}
              <blockquote className="epigraph-original" lang="sa">
                {currentEmpire.shloka_epigraph.original}
              </blockquote>

              {/* Transliteration */}
              {currentEmpire.shloka_epigraph.transliteration && (
                <p className="epigraph-translit">
                  <em>{currentEmpire.shloka_epigraph.transliteration}</em>
                </p>
              )}

              {/* Translation */}
              <p className="epigraph-translation">
                <strong>Translation:</strong> {currentEmpire.shloka_epigraph.translation}
              </p>

              <span className="epigraph-source">
                Source: {currentEmpire.shloka_epigraph.source_text}
              </span>
            </div>
          )}

          {/* Key Battles */}
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
                    <p className="bli-desc">{bt.outcome}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

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
          <div className="dossier-section dossier-sources">
            <h4>Official Scholarly Research & Epigraphic Sources</h4>
            <div className="sources-list">
              {currentEmpire.sources.map((src, idx) => (
                <div key={idx} className="source-citation-card">
                  <span className="scc-year">{src.year}</span>
                  <h5 className="scc-title">{src.title}</h5>
                  <p className="scc-authors">{src.authors}</p>
                  <p className="scc-pub">{src.publisher}</p>
                </div>
              ))}
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
