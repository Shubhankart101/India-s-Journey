import { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import packData from '../data/metro/delhi_metro_pack.json';
import './PolityPolicyMetroCanvas.css';

// Web Mercator projections matching politypolicy.com/DelhiMetro
const px = l => (l + 180) / 360;
const py = l => {
  const s = Math.sin((l * Math.PI) / 180);
  return 0.5 - Math.log((1 + s) / (1 - s)) / (4 * Math.PI);
};

const R2 = Math.PI / 180;
function kmDist(a, b) {
  const dx = (b.ll[0] - a.ll[0]) * Math.cos(((a.ll[1] + b.ll[1]) / 2) * R2) * 111.32;
  const dy = (b.ll[1] - a.ll[1]) * 110.57;
  return Math.hypot(dx, dy);
}

// Pre-project raw geometry once at module load
const projSegs = g => {
  const o = new Array(g.length);
  for (let i = 0; i < g.length; i++) o[i] = [px(g[i][0]), py(g[i][1])];
  return o;
};

// Deep prepare PACK geometry
const PACK = {
  ...packData,
  lines: packData.lines.map(l => ({ ...l, P: l.segs.map(projSegs) })),
  stations: packData.stations.map(s => ({
    ...s,
    P: [px(s.ll[0]), py(s.ll[1])],
    ix: s.l.length > 1 || !!(packData.branchIx && packData.branchIx[s.n]),
  })),
  future: (packData.future || []).map(f => ({
    ...f,
    PZ: projSegs(f.zone),
    st: f.st.map(s => ({ ...s, P: [px(s.ll[0]), py(s.ll[1])] })),
  })),
  base: {
    bd: (packData.base?.bd || []).map(b => ({ ...b, P: b.r.map(projSegs) })),
    water: (packData.base?.water || []).map(w => ({ ...w, P: projSegs(w.g) })),
    roads: (packData.base?.roads || []).map(r => ({ ...r, P: projSegs(r.g) })),
    rail: (packData.base?.rail || []).map(r => ({ ...r, P: projSegs(r.g) })),
    places: (packData.base?.places || []).map(p => ({ ...p, P: [px(p.ll[0]), py(p.ll[1])] })),
  },
};

const LMAP = Object.fromEntries(PACK.lines.map(l => [l.id, l]));
const SMAP = Object.fromEntries(PACK.stations.map(s => [s.n, s]));
const ADJ = {};

function addEdge(a, b, line) {
  if (!SMAP[a] || !SMAP[b] || a === b) return;
  const d = kmDist(SMAP[a], SMAP[b]);
  (ADJ[a] = ADJ[a] || []).push({ to: b, line, km: d });
  (ADJ[b] = ADJ[b] || []).push({ to: a, line, km: d });
}

for (const l of PACK.lines) {
  for (const br of [l.seq, l.branch]) {
    if (br) {
      for (let i = 1; i < br.length; i++) addEdge(br[i - 1], br[i], l.id);
    }
  }
}

const LINK = [
  ['Sarai Kale Khan', 'Sarai Kale Khan - Nizamuddin'],
  ['New Ashok Nagar RRTS', 'New Ashok Nagar'],
  ['Anand Vihar RRTS', 'Anand Vihar'],
  ['Noida Sector 51', 'Noida Sector 52'],
  ['New Delhi', 'New Delhi Airport Express Terminal'],
];
for (const p of LINK) addEdge(p[0], p[1], null);

export default function PolityPolicyMetroCanvas({ theme = 'light' }) {
  const canvasRef = useRef(null);
  const containerRef = useRef(null);

  // View state
  const viewRef = useRef({ cx: 0.7143, cy: 0.4172, z: 280000 });
  const [zoomLevel, setZoomLevel] = useState(280000);

  // Interaction & UI State
  const [cardOpen, setCardOpen] = useState(true);
  const [showFuture, setShowFuture] = useState(true);
  const [selectedLines, setSelectedLines] = useState(new Set());
  const [fromStation, setFromStation] = useState('Kashmere Gate');
  const [toStation, setToStation] = useState('New Delhi');
  const [routeResult, setRouteResult] = useState(null);
  const [selectedStation, setSelectedStation] = useState(null);
  const [hoverStation, setHoverStation] = useState(null);
  const [tooltip, setTooltip] = useState(null);

  // 1. Initial Home Bounds Fit
  useEffect(() => {
    let x0 = 1, y0 = 1, x1 = 0, y1 = 0;
    for (const l of PACK.lines) {
      if (l.sys !== 'dmrc') continue;
      for (const g of l.P) {
        for (const p of g) {
          if (p[0] < x0) x0 = p[0];
          if (p[0] > x1) x1 = p[0];
          if (p[1] < y0) y0 = p[1];
          if (p[1] > y1) y1 = p[1];
        }
      }
    }
    const mx = (x1 - x0) * 0.06, my = (y1 - y0) * 0.06;
    const b = { w: x0 - mx, e: x1 + mx, n: y0 - my, s: y1 + my };
    const cv = canvasRef.current;
    if (cv) {
      const W = cv.clientWidth || 900;
      const H = cv.clientHeight || 700;
      const z = Math.min((W * 0.88) / (b.e - b.w), (H * 0.88) / (b.s - b.n));
      viewRef.current = {
        cx: (b.w + b.e) / 2,
        cy: (b.n + b.s) / 2,
        z: Math.max(180000, z),
      };
      setZoomLevel(viewRef.current.z);
    }
  }, []);

  // 2. Dijkstra Route Solver
  const solveRoute = useCallback((from, to) => {
    if (!SMAP[from] || !SMAP[to] || from === to) return null;

    const key = (s, l) => s + '\u0001' + (l || '');
    const dist = {}, prev = {}, seen = {}, Q = [];
    const push = (k, d, p) => {
      if (dist[k] !== undefined && dist[k] <= d) return;
      dist[k] = d;
      prev[k] = p;
      Q.push([d, k]);
    };

    for (const e of ADJ[from] || []) push(key(from, e.line), 0, null);

    const CHANGE = 4.2;
    const WALK = 2.4;
    let endK = null;

    while (Q.length) {
      Q.sort((a, b) => a[0] - b[0]);
      const top = Q.shift(), d = top[0], k = top[1];
      if (seen[k] || d > dist[k]) continue;
      seen[k] = 1;
      const i = k.indexOf('\u0001'), s = k.slice(0, i), lid = k.slice(i + 1) || null;
      if (s === to) { endK = k; break; }

      for (const e of ADJ[s] || []) {
        const pen = e.line === lid ? 0 : (e.line === null || lid === null ? WALK : CHANGE);
        push(key(e.to, e.line), d + e.km + pen, k);
      }
    }

    if (!endK) return null;

    const path = [];
    for (let k = endK; k; k = prev[k]) {
      const i = k.indexOf('\u0001');
      path.push({ s: k.slice(0, i), l: k.slice(i + 1) || null });
    }
    path.reverse();

    const legs = [];
    let cur = null, dkm = 0;
    for (let i = 0; i < path.length; i++) {
      const p = path[i];
      if (i) dkm += kmDist(SMAP[path[i - 1].s], SMAP[p.s]);
      if (!cur || cur.line !== p.l) {
        cur = { line: p.l, lineName: p.l ? LMAP[p.l]?.nm : 'Walkway / Interchange Link', color: p.l ? LMAP[p.l]?.c : '#64748b', stops: [] };
        if (i) cur.stops.push(path[i - 1].s);
        legs.push(cur);
      }
      if (cur.stops[cur.stops.length - 1] !== p.s) cur.stops.push(p.s);
    }

    const clean = legs.filter(l => l.stops.length > 1);
    const stopsSet = new Set();
    for (const l of clean) for (const s of l.stops) stopsSet.add(s);
    const hops = clean.reduce((a, l) => a + (l.line ? l.stops.length - 1 : 0), 0);
    const interchanges = Math.max(0, clean.length - 1);
    const durationMin = Math.round(hops * 2.2 + interchanges * 5 + dkm * 0.4);

    let tokenFare = 10;
    if (dkm > 32) tokenFare = 60;
    else if (dkm > 21) tokenFare = 50;
    else if (dkm > 12) tokenFare = 40;
    else if (dkm > 5) tokenFare = 30;
    else if (dkm > 2) tokenFare = 20;

    const smartCardFare = Math.round(tokenFare * 0.9);

    return {
      from,
      to,
      legs: clean,
      stops: stopsSet,
      hops,
      changes: interchanges,
      km: dkm.toFixed(1),
      durationMin,
      tokenFare,
      smartCardFare,
      key: from + '>' + to,
    };
  }, []);

  // Compute route on initial load and when from/to change
  useEffect(() => {
    if (fromStation && toStation) {
      const r = solveRoute(fromStation, toStation);
      setRouteResult(r);
    }
  }, [fromStation, toStation, solveRoute]);

  // 3. Canvas Rendering
  useEffect(() => {
    if (!canvasRef.current) return;
    const cv = canvasRef.current;
    const ctx = cv.getContext?.('2d');
    if (!ctx) return;
    const DPR = Math.min(2, window.devicePixelRatio || 1);

    const W = cv.clientWidth || 900;
    const H = cv.clientHeight || 700;
    cv.width = Math.round(W * DPR);
    cv.height = Math.round(H * DPR);
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);

    const view = viewRef.current;
    const sx = x => (x - view.cx) * view.z + W / 2;
    const sy = y => (y - view.cy) * view.z + H / 2;

    const isDark = theme === 'dark';
    const C = isDark
      ? {
          bg: '#07050f',
          land: '#080a17',
          water: '#1b3f78',
          road: '#2a3054',
          road2: '#1d2242',
          rail: '#242a4a',
          bd: '#212648',
          ink: '#f7f0f6',
          mut: '#b3a5bd',
          dim: '#7a6e8c',
          ca: '#FC8EAC',
          ix: '#ffffff',
        }
      : {
          bg: '#fff1e5',
          land: '#fdf0df',
          water: '#cdb79c',
          road: '#ddcdb9',
          road2: '#e9dccb',
          rail: '#dfd0bd',
          bd: '#d9c6b0',
          ink: '#2b2622',
          mut: '#6b5d51',
          dim: '#93857a',
          ca: '#A81B52',
          ix: '#2b2622',
        };

    const z = view.z;
    const S = Math.max(0.5, Math.min(9, Math.pow(z / 470000, 0.42)));

    // Clear
    ctx.fillStyle = C.bg;
    ctx.fillRect(0, 0, W, H);

    const path1 = (c, g, close) => {
      if (g.length < 2) return;
      c.moveTo(sx(g[0][0]), sy(g[0][1]));
      for (let i = 1; i < g.length; i++) c.lineTo(sx(g[i][0]), sy(g[i][1]));
      if (close) c.closePath();
    };

    // 1. Boundaries
    if (PACK.base?.bd) {
      ctx.beginPath();
      for (const b of PACK.base.bd) {
        if (b.lvl === '4') for (const g of b.P) path1(ctx, g, true);
      }
      ctx.fillStyle = C.land;
      ctx.fill('evenodd');

      ctx.beginPath();
      for (const b of PACK.base.bd) {
        if (b.lvl === '4') for (const g of b.P) path1(ctx, g, true);
      }
      ctx.lineWidth = 1.15 * S;
      ctx.strokeStyle = C.bd;
      ctx.stroke();
    }

    // 2. Waterways (Yamuna, Hindon)
    if (PACK.base?.water) {
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.beginPath();
      for (const w of PACK.base.water) if (w.t === 'canal') path1(ctx, w.P, false);
      ctx.lineWidth = 0.75 * S;
      ctx.strokeStyle = C.water;
      ctx.globalAlpha = 0.55;
      ctx.stroke();
      ctx.globalAlpha = 1;

      ctx.beginPath();
      for (const w of PACK.base.water) if (w.t === 'river') path1(ctx, w.P, false);
      ctx.lineWidth = 2.4 * S;
      ctx.strokeStyle = C.water;
      ctx.stroke();
    }

    // 3. Roads & Railways
    if (PACK.base?.roads) {
      if (z > 330000) {
        ctx.beginPath();
        for (const r of PACK.base.roads) if (r.c === 2) path1(ctx, r.P, false);
        ctx.lineWidth = 0.6 * S;
        ctx.strokeStyle = C.road;
        ctx.stroke();
      }
      ctx.beginPath();
      for (const r of PACK.base.roads) if (r.c === 3) path1(ctx, r.P, false);
      ctx.lineWidth = 1.05 * S;
      ctx.strokeStyle = C.road;
      ctx.stroke();
    }

    if (PACK.base?.rail && z > 420000) {
      ctx.beginPath();
      for (const r of PACK.base.rail) path1(ctx, r.P, false);
      ctx.lineWidth = 0.5 * S;
      ctx.strokeStyle = C.rail;
      ctx.stroke();
    }

    // 4. Future Corridors (Phase 4 / 5)
    if (showFuture && PACK.future && !routeResult) {
      for (const f of PACK.future) {
        ctx.save();
        ctx.setLineDash([6 * S, 5 * S]);
        ctx.lineWidth = (f.ph === '4' ? 1.6 : 1.2) * S;
        ctx.strokeStyle = f.ph === '4' ? '#7C8AA0' : '#5A6678';
        ctx.globalAlpha = f.ph === '4' ? 0.8 : 0.55;
        ctx.beginPath();
        path1(ctx, f.PZ, true);
        ctx.stroke();
        ctx.restore();
      }
    }

    // 5. Metro Lines
    const lw = k => Math.max(1.4, Math.min(26, 2.9 * S * k));
    const isLineActive = id => selectedLines.size === 0 || selectedLines.has(id);

    for (const l of PACK.lines) {
      const active = isLineActive(l.id);
      const isRouteActive = !!routeResult;
      ctx.lineWidth = lw(1);
      ctx.strokeStyle = l.c;
      ctx.globalAlpha = active ? (isRouteActive ? 0.22 : 1) : 0.12;
      ctx.beginPath();
      for (const g of l.P) {
        if (g.length < 2) continue;
        path1(ctx, g, false);
      }
      ctx.stroke();
      ctx.globalAlpha = 1;
    }

    // 6. Active Journey Route
    if (routeResult) {
      for (const leg of routeResult.legs) {
        ctx.save();
        ctx.lineWidth = lw(1.8);
        ctx.strokeStyle = leg.color || C.ix;
        if (!leg.line) ctx.setLineDash([4 * S, 4 * S]);
        ctx.beginPath();
        for (let i = 0; i < leg.stops.length; i++) {
          const s = SMAP[leg.stops[i]];
          if (s) {
            const X = sx(s.P[0]), Y = sy(s.P[1]);
            if (i === 0) ctx.moveTo(X, Y);
            else ctx.lineTo(X, Y);
          }
        }
        ctx.stroke();
        ctx.restore();
      }
    }

    // 7. Stations
    const r = z > 9000000 ? 8.5 : z > 4500000 ? 7 : z > 2200000 ? 5.8 : z > 1100000 ? 4.8 : z > 620000 ? 4 : z > 330000 ? 3.2 : 2.4;
    const onlyIx = z < 320000 && selectedLines.size === 0 && !routeResult;

    for (const s of PACK.stations) {
      const X = sx(s.P[0]), Y = sy(s.P[1]);
      if (X < -20 || Y < -20 || X > W + 20 || Y > H + 20) continue;

      const inRoute = routeResult && routeResult.stops.has(s.n);
      if (routeResult && !inRoute && !s.ix) continue;
      if (onlyIx && !s.ix) continue;

      const isSel = selectedStation?.n === s.n;
      const isHov = hoverStation?.n === s.n;
      const radius = isSel ? r * 1.8 : isHov ? r * 1.4 : inRoute ? r * 1.3 : s.ix ? r * 1.25 : r * 0.9;

      if (s.ix) {
        ctx.beginPath();
        ctx.arc(X, Y, radius + 2, 0, 2 * Math.PI);
        ctx.fillStyle = C.bg;
        ctx.fill();
        ctx.lineWidth = 1.8;
        ctx.strokeStyle = inRoute ? C.ca : C.ix;
        ctx.stroke();
      }

      ctx.beginPath();
      ctx.arc(X, Y, radius, 0, 2 * Math.PI);
      ctx.fillStyle = inRoute ? C.ca : isSel ? '#f59e0b' : C.bg;
      ctx.fill();
      ctx.lineWidth = 1.4;
      ctx.strokeStyle = inRoute ? '#ffffff' : s.l[0] ? LMAP[s.l[0]]?.c : C.ink;
      ctx.stroke();
    }

    // 8. Labels
    const placed = [];
    ctx.textBaseline = 'middle';
    ctx.font = `600 ${Math.max(9, Math.min(13, 10.5 * S))}px 'Sora',system-ui,sans-serif`;

    if (PACK.base?.places) {
      ctx.textAlign = 'center';
      for (const p of PACK.base.places) {
        if (p.r < (z > 620000 ? 3 : 5)) continue;
        const X = sx(p.P[0]), Y = sy(p.P[1]);
        if (X < 50 || X > W - 50 || Y < 34 || Y > H - 34) continue;
        const w = ctx.measureText(p.n).width;
        placed.push([X - w / 2 - 4, Y - 7, X + w / 2 + 4, Y + 7]);
        ctx.lineWidth = 3;
        ctx.strokeStyle = C.bg;
        ctx.strokeText(p.n, X, Y);
        ctx.fillStyle = C.dim;
        ctx.fillText(p.n, X, Y);
      }
    }

    ctx.textAlign = 'left';
    const labelPool = PACK.stations
      .filter(s => (routeResult ? routeResult.stops.has(s.n) : s.ix || z > 480000))
      .sort((a, b) => b.ix - a.ix);

    for (const s of labelPool) {
      const X = sx(s.P[0]), Y = sy(s.P[1]);
      if (X < 30 || X > W - 30 || Y < 20 || Y > H - 20) continue;
      const w = ctx.measureText(s.n).width;
      const box = [X + 8, Y - 7, X + 12 + w, Y + 7];
      let clash = false;
      for (const b of placed) {
        if (box[0] < b[2] && box[2] > b[0] && box[1] < b[3] && box[3] > b[1]) {
          clash = true;
          break;
        }
      }
      if (clash && !s.ix && !routeResult) continue;
      placed.push(box);

      ctx.lineWidth = 3.2;
      ctx.strokeStyle = C.bg;
      ctx.strokeText(s.n, X + 9, Y);
      ctx.fillStyle = routeResult?.stops.has(s.n) ? C.ca : s.ix ? C.ink : C.mut;
      ctx.fillText(s.n, X + 9, Y);
    }
  }, [theme, zoomLevel, showFuture, selectedLines, routeResult, selectedStation, hoverStation]);

  // Pan & Zoom
  const dragRef = useRef({ dragging: false, startX: 0, startY: 0, moved: 0 });

  const handleMouseDown = e => {
    dragRef.current = { dragging: true, startX: e.clientX, startY: e.clientY, moved: 0 };
  };

  const handleMouseMove = e => {
    const cv = canvasRef.current;
    if (!cv) return;
    const rect = cv.getBoundingClientRect();
    const cX = e.clientX - rect.left;
    const cY = e.clientY - rect.top;

    if (dragRef.current.dragging) {
      const dx = e.clientX - dragRef.current.startX;
      const dy = e.clientY - dragRef.current.startY;
      dragRef.current.moved += Math.hypot(dx, dy);
      dragRef.current.startX = e.clientX;
      dragRef.current.startY = e.clientY;

      viewRef.current.cx -= dx / viewRef.current.z;
      viewRef.current.cy -= dy / viewRef.current.z;
      setZoomLevel(viewRef.current.z + Math.random() * 0.001);
      return;
    }

    const view = viewRef.current;
    const sx = x => (x - view.cx) * view.z + cv.clientWidth / 2;
    const sy = y => (y - view.cy) * view.z + cv.clientHeight / 2;

    let nearest = null, bd = 16;
    for (const s of PACK.stations) {
      const d = Math.hypot(sx(s.P[0]) - cX, sy(s.P[1]) - cY);
      if (d < bd) {
        bd = d;
        nearest = s;
      }
    }
    setHoverStation(nearest);
    if (nearest) {
      setTooltip({
        x: cX,
        y: cY,
        name: nearest.n,
        lines: nearest.l.map(id => LMAP[id]?.nm || id).join(' · '),
        interchange: nearest.ix,
      });
    } else {
      setTooltip(null);
    }
  };

  const handleMouseUp = () => {
    if (dragRef.current.moved < 6 && hoverStation) {
      setSelectedStation(hoverStation);
    }
    dragRef.current.dragging = false;
  };

  const handleWheel = e => {
    e.preventDefault();
    const cv = canvasRef.current;
    if (!cv) return;
    const rect = cv.getBoundingClientRect();
    const cX = e.clientX - rect.left;
    const cY = e.clientY - rect.top;

    const factor = e.deltaY < 0 ? 1.25 : 0.8;
    const oldZ = viewRef.current.z;
    const newZ = Math.max(90000, Math.min(12000000, oldZ * factor));

    const W = cv.clientWidth, H = cv.clientHeight;
    const pX = (cX - W / 2) / oldZ + viewRef.current.cx;
    const pY = (cY - H / 2) / oldZ + viewRef.current.cy;

    viewRef.current.z = newZ;
    viewRef.current.cx = pX - (cX - W / 2) / newZ;
    viewRef.current.cy = pY - (cY - H / 2) / newZ;
    setZoomLevel(newZ);
  };

  const handleZoom = delta => {
    const factor = delta > 0 ? 1.35 : 0.75;
    viewRef.current.z = Math.max(90000, Math.min(12000000, viewRef.current.z * factor));
    setZoomLevel(viewRef.current.z);
  };

  const handleReset = () => {
    viewRef.current = { cx: 0.7143, cy: 0.4172, z: 280000 };
    setZoomLevel(280000);
    setSelectedStation(null);
  };

  const allStations = useMemo(() => {
    return [...PACK.stations].sort((a, b) => a.n.localeCompare(b.n));
  }, []);

  return (
    <div className={`polity-metro-viewport theme-${theme}`} ref={containerRef}>
      {/* Top Left Layer Toggles */}
      <div className="polity-layer-toggles">
        <button
          type="button"
          className={`polity-layer-pill ${selectedLines.size === 0 ? 'active' : ''}`}
          onClick={() => setSelectedLines(new Set())}
        >
          Whole Network
        </button>
        <button
          type="button"
          className={`polity-layer-pill ${showFuture ? 'active future' : ''}`}
          onClick={() => setShowFuture(prev => !prev)}
        >
          --- Under Construction
        </button>
        <button
          type="button"
          className="polity-layer-pill"
          onClick={() => {
            const all = new Set(PACK.lines.map(l => l.id));
            setSelectedLines(all);
          }}
        >
          All Lines ({PACK.lines.length})
        </button>
      </div>

      {/* Main Canvas */}
      <canvas
        ref={canvasRef}
        className="polity-metro-canvas"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onWheel={handleWheel}
      />

      {/* Hover Tooltip */}
      {tooltip && (
        <div
          className="polity-metro-tooltip"
          style={{ left: `${tooltip.x + 12}px`, top: `${tooltip.y + 12}px` }}
        >
          <strong>{tooltip.name}</strong>
          <span className="tooltip-lines">{tooltip.lines}</span>
          {tooltip.interchange && <span className="tooltip-tag">Interchange</span>}
        </div>
      )}

      {/* Station Selected Callout */}
      {selectedStation && (
        <div className="polity-station-callout">
          <button
            type="button"
            className="callout-close"
            onClick={() => setSelectedStation(null)}
          >
            ✕
          </button>
          <div className="callout-type">
            {selectedStation.ix ? '⊚ Interchange Station' : '◯ Metro Station'}
          </div>
          <h4 className="callout-name">{selectedStation.n}</h4>
          <div className="callout-lines">
            {selectedStation.l.map(id => {
              const l = LMAP[id];
              return (
                <span key={id} className="callout-line-pill" style={{ borderColor: l?.c }}>
                  <span className="line-dot" style={{ background: l?.c }} />
                  {l?.nm || id}
                </span>
              );
            })}
          </div>
          <div className="callout-actions">
            <button
              type="button"
              className="callout-btn"
              onClick={() => {
                setFromStation(selectedStation.n);
                setCardOpen(true);
              }}
            >
              Set As From
            </button>
            <button
              type="button"
              className="callout-btn"
              onClick={() => {
                setToStation(selectedStation.n);
                setCardOpen(true);
              }}
            >
              Set As To
            </button>
          </div>
        </div>
      )}

      {/* Floating PLAN A JOURNEY Card (Collapsible) */}
      <div className={`polity-journey-card ${cardOpen ? 'open' : 'minimized'}`}>
        <div className="journey-header" onClick={() => setCardOpen(prev => !prev)}>
          <span className="journey-title">
            <span className="journey-toggle-arrow">{cardOpen ? '▾' : '‹'}</span>
            PLAN A JOURNEY
          </span>
          <button
            type="button"
            className="journey-minimize-btn"
            title={cardOpen ? 'Minimize Planner' : 'Expand Planner'}
            aria-label="Toggle Planner"
          >
            {cardOpen ? '−' : '+'}
          </button>
        </div>

        {cardOpen && (
          <div className="journey-body">
            <div className="journey-field">
              <label htmlFor="polity-from">FROM</label>
              <select
                id="polity-from"
                value={fromStation}
                onChange={e => setFromStation(e.target.value)}
              >
                {allStations.map(s => (
                  <option key={s.n} value={s.n}>
                    {s.n} {s.ix ? '★ (Interchange)' : ''}
                  </option>
                ))}
              </select>
            </div>

            <div className="journey-swap-row">
              <button
                type="button"
                className="journey-swap-btn"
                title="Swap From and To"
                onClick={() => {
                  const tmp = fromStation;
                  setFromStation(toStation);
                  setToStation(tmp);
                }}
              >
                ⇅
              </button>
            </div>

            <div className="journey-field">
              <label htmlFor="polity-to">TO</label>
              <select
                id="polity-to"
                value={toStation}
                onChange={e => setToStation(e.target.value)}
              >
                {allStations.map(s => (
                  <option key={s.n} value={s.n}>
                    {s.n} {s.ix ? '★ (Interchange)' : ''}
                  </option>
                ))}
              </select>
            </div>

            <button
              type="button"
              className="journey-find-btn"
              onClick={() => {
                const r = solveRoute(fromStation, toStation);
                setRouteResult(r);
              }}
            >
              Find The Route
            </button>

            {routeResult ? (
              <div className="journey-results">
                <div className="results-metrics">
                  <span>⏱ {routeResult.durationMin} min</span>
                  <span>📏 {routeResult.km} km</span>
                  <span>🔴 {routeResult.hops} stops</span>
                  <span>⇄ {routeResult.changes} xchg</span>
                </div>
                <div className="results-fares">
                  <span className="token-fare">Token: ₹{routeResult.tokenFare}</span>
                  <span className="smart-card-fare">Smart Card: ₹{routeResult.smartCardFare}</span>
                </div>
                <div className="results-legs">
                  {routeResult.legs.map((leg, idx) => (
                    <div key={idx} className="leg-item">
                      <div className="leg-badge" style={{ background: leg.color }}>
                        {leg.lineName}
                      </div>
                      <div className="leg-stops">
                        {leg.stops[0]} → {leg.stops[leg.stops.length - 1]} ({leg.stops.length - 1} stops)
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="journey-hint">
                Pick two stations, or click any station on the map and use{' '}
                <strong>Set As From</strong> / <strong>Set As To</strong>. The route is worked out
                over the real network — every line, every interchange, including the ones between
                operators.
              </div>
            )}
          </div>
        )}
      </div>

      {/* Bottom Controls */}
      <div className="polity-bottom-controls">
        <div className="polity-attribution">
          <div>Network and city geography: © OpenStreetMap contributors (ODbL)</div>
          <div>Corridors under construction: DMRC official KML (Phase 4 & 5)</div>
        </div>
        <div className="polity-zoom-btns">
          <button type="button" onClick={() => handleZoom(1)} title="Zoom In">+</button>
          <button type="button" onClick={() => handleZoom(-1)} title="Zoom Out">−</button>
          <button type="button" onClick={handleReset} title="Reset View">↺</button>
        </div>
      </div>
    </div>
  );
}
