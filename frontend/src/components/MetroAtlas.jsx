import { useMemo, useState } from 'react';
import metroData from '../data/metro-networks.json';
import './MetroAtlas.css';

// Procedural vector layouts for city metro maps
const CITY_LAYOUTS = {
  'delhi-ncr': {
    width: 600,
    height: 520,
    lines: [
      { id: 'red', name: 'Red Line (Line 1)', color: '#dc2626', path: 'M 90,140 L 220,140 L 280,180 L 410,180 L 510,140' },
      { id: 'yellow', name: 'Yellow Line (Line 2)', color: '#eab308', path: 'M 280,40 L 280,180 L 280,260 L 260,330 L 210,430 L 160,490' },
      { id: 'blue', name: 'Blue Line (Line 3 & 4)', color: '#2563eb', path: 'M 70,390 L 170,330 L 280,260 L 390,260 L 490,290 L 550,290' },
      { id: 'green', name: 'Green Line (Line 5)', color: '#16a34a', path: 'M 50,210 L 160,210 L 220,240 L 240,260' },
      { id: 'violet', name: 'Violet Line (Line 6)', color: '#7c3aed', path: 'M 280,180 L 320,220 L 320,350 L 350,440 L 360,500' },
      { id: 'pink', name: 'Pink Line (Ring Line 7)', color: '#ec4899', path: 'M 190,90 L 360,90 L 450,180 L 450,330 L 370,410 L 220,410 L 140,310 L 140,160 Z' },
      { id: 'magenta', name: 'Magenta Line (Line 8)', color: '#d946ef', path: 'M 100,320 L 180,380 L 270,380 L 350,380 L 440,330 L 490,290' },
      { id: 'orange', name: 'Airport Express (Orange)', color: '#ea580c', path: 'M 280,240 L 230,290 L 160,380 L 120,410' },
      { id: 'rrts', name: 'Namo Bharat RRTS', color: '#991b1b', path: 'M 350,330 L 420,270 L 490,190 L 560,70' },
    ],
    stations: [
      { name: 'Kashmere Gate', x: 280, y: 180, lines: ['Red', 'Yellow', 'Violet'], interchange: true, footfall: '350,000' },
      { name: 'Rajiv Chowk (CP)', x: 280, y: 260, lines: ['Yellow', 'Blue'], interchange: true, footfall: '500,000' },
      { name: 'Hauz Khas', x: 270, y: 380, lines: ['Yellow', 'Magenta'], interchange: true, footfall: '280,000' },
      { name: 'Central Secretariat', x: 280, y: 290, lines: ['Yellow', 'Violet'], interchange: true, footfall: '210,000' },
      { name: 'IGI Airport T3', x: 160, y: 380, lines: ['Airport Express'], interchange: false, footfall: '75,000' },
      { name: 'Botanical Garden', x: 440, y: 330, lines: ['Blue', 'Magenta'], interchange: true, footfall: '220,000' },
      { name: 'Anand Vihar ISBT', x: 450, y: 240, lines: ['Blue', 'Pink', 'RRTS'], interchange: true, footfall: '260,000' },
      { name: 'Millennium City Centre', x: 160, y: 490, lines: ['Yellow'], interchange: false, footfall: '140,000' },
      { name: 'Noida Electronic City', x: 550, y: 290, lines: ['Blue'], interchange: false, footfall: '110,000' },
      { name: 'Rithala', x: 90, y: 140, lines: ['Red'], interchange: false, footfall: '90,000' },
    ],
  },
  'mumbai': {
    width: 600,
    height: 520,
    lines: [
      { id: 'line1', name: 'Line 1 (Blue)', color: '#0284c7', path: 'M 140,240 L 260,240 L 440,240' },
      { id: 'line2a', name: 'Line 2A (Yellow)', color: '#facc15', path: 'M 190,60 L 160,150 L 140,240 L 130,300' },
      { id: 'line7', name: 'Line 7 (Red)', color: '#ef4444', path: 'M 290,60 L 270,160 L 260,240 L 250,290' },
      { id: 'line3', name: 'Line 3 (Aqua Underground)', color: '#06b6d4', path: 'M 280,180 L 250,260 L 260,330 L 240,410 L 220,490' },
      { id: 'line4', name: 'Line 4 (Green Under Const.)', color: '#22c55e', path: 'M 470,80 L 450,170 L 440,240 L 420,350' },
    ],
    stations: [
      { name: 'Versova', x: 140, y: 240, lines: ['Line 1'], interchange: false, footfall: '65,000' },
      { name: 'Andheri / WEH', x: 260, y: 240, lines: ['Line 1', 'Line 7'], interchange: true, footfall: '220,000' },
      { name: 'Ghatkopar', x: 440, y: 240, lines: ['Line 1'], interchange: true, footfall: '180,000' },
      { name: 'Bandra-Kurla Complex (BKC)', x: 260, y: 330, lines: ['Line 3 (Aqua)'], interchange: true, footfall: '95,000' },
      { name: 'CSMIA Terminal 2', x: 270, y: 220, lines: ['Line 3 (Aqua)'], interchange: false, footfall: '60,000' },
      { name: 'Cuffe Parade', x: 220, y: 490, lines: ['Line 3 (Aqua)'], interchange: false, footfall: '45,000' },
      { name: 'Dahisar East', x: 240, y: 60, lines: ['Line 2A', 'Line 7'], interchange: true, footfall: '80,000' },
    ],
  },
  'bengaluru': {
    width: 600,
    height: 520,
    lines: [
      { id: 'purple', name: 'Purple Line', color: '#9333ea', path: 'M 60,360 L 160,300 L 270,250 L 390,250 L 540,190' },
      { id: 'green', name: 'Green Line', color: '#15803d', path: 'M 190,60 L 230,150 L 270,250 L 290,360 L 310,480' },
      { id: 'yellow', name: 'Yellow Line (Electronic City)', color: '#eab308', path: 'M 270,360 L 340,390 L 420,440 L 510,490' },
      { id: 'blue', name: 'Blue Line (Airport Under Const.)', color: '#2563eb', path: 'M 340,390 L 440,330 L 480,220 L 450,80' },
    ],
    stations: [
      { name: 'Kempegowda Majestic', x: 270, y: 250, lines: ['Purple', 'Green'], interchange: true, footfall: '240,000' },
      { name: 'Whitefield (Kadugodi)', x: 540, y: 190, lines: ['Purple'], interchange: false, footfall: '75,000' },
      { name: 'MG Road', x: 330, y: 250, lines: ['Purple'], interchange: false, footfall: '90,000' },
      { name: 'Indiranagar', x: 380, y: 250, lines: ['Purple'], interchange: false, footfall: '60,000' },
      { name: 'Silk Board', x: 340, y: 390, lines: ['Yellow', 'Blue'], interchange: true, footfall: '110,000' },
      { name: 'Electronic City', x: 470, y: 470, lines: ['Yellow'], interchange: false, footfall: '85,000' },
      { name: 'Challaghatta', x: 60, y: 360, lines: ['Purple'], interchange: false, footfall: '40,000' },
    ],
  },
  'kolkata': {
    width: 600,
    height: 520,
    lines: [
      { id: 'blue', name: 'Blue Line (Line 1)', color: '#2563eb', path: 'M 310,50 L 310,180 L 310,270 L 330,380 L 360,490' },
      { id: 'green', name: 'Green Line (Line 2 - Underwater)', color: '#16a34a', path: 'M 140,270 L 220,270 L 310,270 L 430,270 L 530,240' },
      { id: 'hooghly', name: 'River Hooghly Bed', color: '#0284c7', path: 'M 240,40 Q 250,150 260,270 T 230,490', isWater: true },
      { id: 'orange', name: 'Orange Line (Line 6)', color: '#ea580c', path: 'M 360,490 L 460,430 L 490,320 L 510,120' },
    ],
    stations: [
      { name: 'Howrah Maidan', x: 140, y: 270, lines: ['Green'], interchange: false, footfall: '90,000' },
      { name: 'Howrah Station (33m Deep)', x: 220, y: 270, lines: ['Green (Underwater)'], interchange: true, footfall: '220,000' },
      { name: 'Esplanade', x: 310, y: 270, lines: ['Blue', 'Green'], interchange: true, footfall: '260,000' },
      { name: 'Sealdah', x: 370, y: 270, lines: ['Green'], interchange: true, footfall: '190,000' },
      { name: 'Salt Lake Sector V', x: 530, y: 240, lines: ['Green'], interchange: false, footfall: '110,000' },
      { name: 'Dakshineswar', x: 310, y: 50, lines: ['Blue'], interchange: false, footfall: '70,000' },
      { name: 'Kavi Subhash', x: 360, y: 490, lines: ['Blue', 'Orange'], interchange: true, footfall: '85,000' },
    ],
  },
  'chennai': {
    width: 600,
    height: 520,
    lines: [
      { id: 'blue', name: 'Blue Line (Corridor 1)', color: '#1d4ed8', path: 'M 400,60 L 350,160 L 310,250 L 230,360 L 140,460' },
      { id: 'green', name: 'Green Line (Corridor 2)', color: '#15803d', path: 'M 350,160 L 260,200 L 200,270 L 210,370' },
    ],
    stations: [
      { name: 'Chennai Central (MGR)', x: 350, y: 160, lines: ['Blue', 'Green'], interchange: true, footfall: '110,000' },
      { name: 'Chennai Airport', x: 140, y: 460, lines: ['Blue'], interchange: false, footfall: '45,000' },
      { name: 'Alandur', x: 210, y: 370, lines: ['Blue', 'Green'], interchange: true, footfall: '50,000' },
      { name: 'Koyambedu', x: 200, y: 270, lines: ['Green'], interchange: false, footfall: '40,000' },
    ],
  },
  'hyderabad': {
    width: 600,
    height: 520,
    lines: [
      { id: 'red', name: 'Red Line (Corridor 1)', color: '#dc2626', path: 'M 100,80 L 250,220 L 330,320 L 480,440' },
      { id: 'blue', name: 'Blue Line (Corridor 3)', color: '#2563eb', path: 'M 80,310 L 250,220 L 400,190 L 520,230' },
      { id: 'green', name: 'Green Line (Corridor 2)', color: '#16a34a', path: 'M 340,110 L 340,240 L 330,320' },
    ],
    stations: [
      { name: 'Ameerpet Hub', x: 250, y: 220, lines: ['Red', 'Blue'], interchange: true, footfall: '120,000' },
      { name: 'Raidurg (HITEC City)', x: 80, y: 310, lines: ['Blue'], interchange: false, footfall: '85,000' },
      { name: 'MGBS', x: 330, y: 320, lines: ['Red', 'Green'], interchange: true, footfall: '70,000' },
      { name: 'Secunderabad / Parade Ground', x: 340, y: 110, lines: ['Blue', 'Green'], interchange: true, footfall: '65,000' },
    ],
  },
  'kochi': {
    width: 600,
    height: 520,
    lines: [
      { id: 'rail', name: 'Kochi Metro Rail', color: '#0284c7', path: 'M 380,60 L 340,180 L 320,300 L 370,440' },
      { id: 'water', name: 'Kochi Water Metro Routes', color: '#06b6d4', path: 'M 220,270 L 140,300 M 220,270 L 110,380 M 220,270 L 290,200', isWaterRoute: true },
    ],
    stations: [
      { name: 'High Court Terminal', x: 220, y: 270, lines: ['Water Metro Hub'], interchange: true, footfall: '22,000' },
      { name: 'Aluva', x: 380, y: 60, lines: ['Kochi Metro Rail'], interchange: false, footfall: '35,000' },
      { name: 'MG Road', x: 320, y: 300, lines: ['Kochi Metro Rail'], interchange: false, footfall: '28,000' },
      { name: 'Fort Kochi Terminal', x: 110, y: 380, lines: ['Water Metro'], interchange: false, footfall: '18,000' },
      { name: 'Vypin Island', x: 140, y: 300, lines: ['Water Metro'], interchange: false, footfall: '15,000' },
    ],
  },
};

export default function MetroAtlas({ onSelectCity }) {
  const [selectedCityId, setSelectedCityId] = useState('delhi-ncr');
  const [selectedLineId, setSelectedLineId] = useState(null);
  const [hoveredStation, setHoveredStation] = useState(null);
  const [zoom, setZoom] = useState(1);

  const city = useMemo(() => {
    return metroData.cities.find(c => c.id === selectedCityId) || metroData.cities[0];
  }, [selectedCityId]);

  const layout = useMemo(() => {
    return CITY_LAYOUTS[selectedCityId] || CITY_LAYOUTS['delhi-ncr'];
  }, [selectedCityId]);

  const handleCityChange = (id) => {
    setSelectedCityId(id);
    setSelectedLineId(null);
    setHoveredStation(null);
    if (onSelectCity) onSelectCity(id);
  };

  return (
    <div className="metro-atlas-root" aria-label="Interactive Metro Rail Workbench">
      {/* Top City Tabs */}
      <div className="metro-top-bar">
        <div className="metro-cities-nav" role="tablist" aria-label="Indian Metro Cities">
          {metroData.cities.map(c => (
            <button
              type="button"
              key={c.id}
              role="tab"
              aria-selected={selectedCityId === c.id}
              className={`metro-city-pill ${selectedCityId === c.id ? 'active' : ''}`}
              onClick={() => handleCityChange(c.id)}
            >
              <span className="metro-city-dot" />
              {c.name.split('(')[0].trim()}
            </button>
          ))}
        </div>
      </div>

      {/* Main Grid: Map on left, Dossier on right */}
      <div className="metro-workbench-grid">
        <div className="metro-map-canvas-container">
          {/* Zoom controls */}
          <div className="metro-map-controls">
            <button
              type="button"
              className="metro-map-btn"
              aria-label="Zoom in"
              onClick={() => setZoom(z => Math.min(1.8, z + 0.2))}
            >
              +
            </button>
            <button
              type="button"
              className="metro-map-btn"
              aria-label="Zoom out"
              onClick={() => setZoom(z => Math.max(0.8, z - 0.2))}
            >
              −
            </button>
            <button
              type="button"
              className="metro-map-btn"
              aria-label="Reset zoom"
              onClick={() => setZoom(1)}
            >
              ↺
            </button>
          </div>

          {/* SVG Canvas */}
          <svg
            className="metro-svg-canvas"
            viewBox={`0 0 ${layout.width} ${layout.height}`}
            style={{ transform: `scale(${zoom})`, transformOrigin: 'center center', transition: 'transform 0.2s ease' }}
          >
            {/* Background Grid Pattern */}
            <defs>
              <pattern id="metroGrid" width="30" height="30" patternUnits="userSpaceOnUse">
                <path d="M 30 0 L 0 0 0 30" fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="1" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#metroGrid)" />

            {/* Metro Lines */}
            {layout.lines.map(line => {
              const isSelected = !selectedLineId || selectedLineId === line.id;
              const strokeW = line.isWater ? 16 : line.isWaterRoute ? 5 : 8;
              const opacity = isSelected ? 1 : 0.2;
              return (
                <path
                  key={line.id}
                  d={line.path}
                  fill="none"
                  stroke={line.color}
                  strokeWidth={strokeW}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeDasharray={line.isWaterRoute ? '6,6' : 'none'}
                  opacity={opacity}
                  style={{ transition: 'opacity 0.2s ease' }}
                />
              );
            })}

            {/* Stations */}
            {layout.stations.map((st, idx) => {
              const isInterchange = st.interchange;
              const r = isInterchange ? 9 : 6;
              return (
                <g
                  key={idx}
                  transform={`translate(${st.x}, ${st.y})`}
                  style={{ cursor: 'pointer' }}
                  onMouseEnter={() => setHoveredStation(st)}
                  onMouseLeave={() => setHoveredStation(null)}
                >
                  {isInterchange && (
                    <circle
                      r={15}
                      fill="none"
                      stroke="#f59e0b"
                      strokeWidth="2"
                      opacity="0.6"
                      strokeDasharray="3,3"
                    />
                  )}
                  <circle
                    r={r}
                    fill={isInterchange ? '#ffffff' : '#0f172a'}
                    stroke={isInterchange ? '#f59e0b' : '#ffffff'}
                    strokeWidth="3"
                  />
                  <text
                    x={st.x > layout.width * 0.6 ? -12 : 12}
                    y={4}
                    textAnchor={st.x > layout.width * 0.6 ? 'end' : 'start'}
                    fill="#f8fafc"
                    fontSize={isInterchange ? '11px' : '9.5px'}
                    fontWeight={isInterchange ? '700' : '500'}
                    fontFamily="sans-serif"
                    style={{ textShadow: '0 2px 4px #000' }}
                  >
                    {st.name}
                  </text>
                </g>
              );
            })}
          </svg>

          {/* Hover Station Tooltip */}
          {hoveredStation && (
            <div
              className="metro-station-tooltip"
              style={{
                left: `${(hoveredStation.x / layout.width) * 100}%`,
                top: `${(hoveredStation.y / layout.height) * 100}%`,
              }}
            >
              <strong>{hoveredStation.name}</strong>
              <div>Lines: {hoveredStation.lines.join(' · ')}</div>
              {hoveredStation.footfall && <div>Daily Footfall: {hoveredStation.footfall}</div>}
            </div>
          )}

          {/* Line Filter Strip */}
          <div className="metro-line-filter-strip">
            <button
              type="button"
              className={`metro-line-pill ${!selectedLineId ? 'active' : ''}`}
              onClick={() => setSelectedLineId(null)}
            >
              All Lines ({city.lines.length})
            </button>
            {city.lines.map((l, i) => (
              <button
                type="button"
                key={i}
                className={`metro-line-pill ${selectedLineId === (layout.lines[i]?.id) ? 'active' : ''}`}
                style={{ '--line-color': l.color }}
                onClick={() => setSelectedLineId(selectedLineId === layout.lines[i]?.id ? null : layout.lines[i]?.id)}
              >
                <span className="metro-line-swatch" style={{ background: l.color }} />
                {l.name.split('(')[0].trim()}
              </button>
            ))}
          </div>
        </div>

        {/* Right Dossier Panel */}
        <div className="metro-dossier-panel">
          <div className="metro-dossier-header">
            <span className="metro-dossier-hindi">{city.hindi}</span>
            <h3 className="metro-dossier-title">{city.name}</h3>
            <div className="metro-dossier-meta">
              <span className="metro-meta-badge">Opened {city.opened_year}</span>
              <span className="metro-meta-badge">{city.length_km} km Active</span>
              <span className="metro-meta-badge">{city.stations_count} Stations</span>
              <span className="metro-meta-badge">{city.operator}</span>
            </div>
          </div>

          <p className="metro-dossier-lead">{city.description}</p>

          {/* Quoted Memoir */}
          {city.quote && (
            <blockquote className="metro-quote-card">
              “{city.quote.text}”
              <cite className="metro-quote-cite">
                — {city.quote.author}, {city.quote.title}
                <br />
                <em>{city.quote.source}</em>
              </cite>
            </blockquote>
          )}

          {/* Stats Grid */}
          <div className="metro-stats-grid">
            {city.stats.map((s, idx) => (
              <div key={idx} className="metro-stat-box">
                <span className="metro-stat-value">{s.value}</span>
                <span className="metro-stat-label">{s.label}</span>
                {s.note && <span className="metro-stat-note">{s.note}</span>}
              </div>
            ))}
          </div>

          {/* Engineering Feats */}
          {city.engineering_feats && (
            <div className="metro-feats-box">
              <h4>Civil Engineering Feats &amp; Innovation</h4>
              <ul>
                {city.engineering_feats.map((feat, idx) => (
                  <li key={idx}>{feat}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
