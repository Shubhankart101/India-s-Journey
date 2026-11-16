import { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import { getCityPack, kmDist } from '../data/metro/all_city_packs.js';
import './PolityPolicyMetroCanvas.css';

export function getInitialView(pack, width = 900, height = 700) {
  if (!pack || !pack.stations || pack.stations.length === 0) {
    return { cx: 0.7143, cy: 0.4172, z: 280000 };
  }
  let x0 = 1, y0 = 1, x1 = 0, y1 = 0;
  for (const s of pack.stations) {
    if (s.P[0] < x0) x0 = s.P[0];
    if (s.P[0] > x1) x1 = s.P[0];
    if (s.P[1] < y0) y0 = s.P[1];
    if (s.P[1] > y1) y1 = s.P[1];
  }
  const mx = Math.max((x1 - x0) * 0.16, 0.0006);
  const my = Math.max((y1 - y0) * 0.16, 0.0006);
  const b = { w: x0 - mx, e: x1 + mx, n: y0 - my, s: y1 + my };
  const z = Math.min(
    (width * 0.82) / Math.max(1e-5, b.e - b.w),
    (height * 0.82) / Math.max(1e-5, b.s - b.n)
  );
  return {
    cx: (b.w + b.e) / 2,
    cy: (b.n + b.s) / 2,
    z: Math.max(30000, Math.min(8000000, z)),
  };
}

export default function PolityPolicyMetroCanvas({ cityId = 'delhi-ncr', theme = 'light' }) {
  const canvasRef = useRef(null);
  const containerRef = useRef(null);

  // Active City Pack & Lookups
  const PACK = useMemo(() => getCityPack(cityId), [cityId]);
  const LMAP = PACK.lmap || {};
  const SMAP = PACK.smap || {};
  const ADJ = PACK.adj || {};

  // View state initialized directly to the target city's exact geographic frame
  const viewRef = useRef(getInitialView(PACK));
  const [renderTrigger, setRenderTrigger] = useState(0);

  // Interaction & UI State
  const [cardOpen, setCardOpen] = useState(true);
  const [showFuture, setShowFuture] = useState(true);
  const [selectedLines, setSelectedLines] = useState(new Set());
  const [fromStation, setFromStation] = useState('');
  const [toStation, setToStation] = useState('');
  const [routeResult, setRouteResult] = useState(null);
  const [selectedStation, setSelectedStation] = useState(null);
  const [hoverStation, setHoverStation] = useState(null);
  const [tooltip, setTooltip] = useState(null);

  // Helper to fit bounding box of current city
  const fitCityBounds = useCallback((pack) => {
    const cv = canvasRef.current;
    const W = cv?.clientWidth || 900;
    const H = cv?.clientHeight || 700;
    viewRef.current = getInitialView(pack, W, H);
    setRenderTrigger(prev => prev + 1);
  }, []);

  // 1. Initial City Bounds Fit and Station Defaults
  useEffect(() => {
    fitCityBounds(PACK);
    if (PACK.stations && PACK.stations.length >= 2) {
      const startSt = PACK.stations[0].n;
      const endSt = PACK.stations[Math.min(PACK.stations.length - 1, 4)].n;
      setFromStation(startSt);
      setToStation(endSt);
      setSelectedStation(null);
      setSelectedLines(new Set());
      setRouteResult(null);
    }
  }, [cityId, PACK, fitCityBounds]);

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
  }, [ADJ, LMAP, SMAP]);

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

    // Clear background
    ctx.fillStyle = C.bg;
    ctx.fillRect(0, 0, W, H);

    const path1 = (c, g, close) => {
      if (!g || g.length < 2) return;
      c.moveTo(sx(g[0][0]), sy(g[0][1]));
      for (let i = 1; i < g.length; i++) c.lineTo(sx(g[i][0]), sy(g[i][1]));
      if (close) c.closePath();
    };

    // 1. Boundaries (ODbL municipal & metropolitan limits)
    if (PACK.base?.bd && PACK.base.bd.length) {
      ctx.beginPath();
      for (const b of PACK.base.bd) {
        if (b.lvl === '4' || !b.lvl) for (const g of b.P) path1(ctx, g, true);
      }
      ctx.fillStyle = C.land;
      ctx.fill('evenodd');

      ctx.beginPath();
      for (const b of PACK.base.bd) {
        if (b.lvl === '4' || !b.lvl) for (const g of b.P) path1(ctx, g, true);
      }
      ctx.lineWidth = 1.2 * S;
      ctx.strokeStyle = C.bd;
      ctx.stroke();
    }

    // 2. Waterways (Rivers, canals, coasts, lakes, bays)
    if (PACK.base?.water && PACK.base.water.length) {
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';

      // Canals and minor water streams
      ctx.beginPath();
      for (const w of PACK.base.water) {
        if (w.t === 'canal' || w.t === 'stream') path1(ctx, w.P, false);
      }
      ctx.lineWidth = 1.4 * S;
      ctx.strokeStyle = C.water;
      ctx.globalAlpha = 0.65;
      ctx.stroke();
      ctx.globalAlpha = 1;

      // Major rivers, coastlines, bays, and lakes
      ctx.beginPath();
      for (const w of PACK.base.water) {
        if (w.t !== 'canal' && w.t !== 'stream') path1(ctx, w.P, false);
      }
      ctx.lineWidth = 3.6 * S;
      ctx.strokeStyle = C.water;
      ctx.stroke();
    }

    // 3. Roads & Arterial Expressways
    if (PACK.base?.roads && PACK.base.roads.length) {
      // Secondary/arterial roads
      ctx.beginPath();
      for (const r of PACK.base.roads) if (r.c === 2) path1(ctx, r.P, false);
      ctx.lineWidth = 0.9 * S;
      ctx.strokeStyle = C.road;
      ctx.stroke();

      // Expressways & primary highways
      ctx.beginPath();
      for (const r of PACK.base.roads) if (r.c === 3 || !r.c) path1(ctx, r.P, false);
      ctx.lineWidth = 1.6 * S;
      ctx.strokeStyle = C.road;
      ctx.stroke();
    }

    // 3b. Railway Corridors (Base Indian Railways Trunk Lines)
    if (PACK.base?.rail && PACK.base.rail.length) {
      ctx.beginPath();
      for (const r of PACK.base.rail) path1(ctx, r.P, false);
      ctx.lineWidth = 1.1 * S;
      ctx.strokeStyle = C.rail;
      ctx.stroke();
    }

    // 4. Future Corridors (Phase 4 / 5 / Under Construction)
    if (showFuture && PACK.future && PACK.future.length && !routeResult) {
      for (const f of PACK.future) {
        ctx.save();
        ctx.setLineDash([8 * S, 6 * S]);
        ctx.lineWidth = Math.max(2.2, 3.2 * S);
        ctx.strokeStyle = f.c || (f.ph === '4' ? '#f59e0b' : '#0284c7');
        ctx.globalAlpha = 0.9;
        ctx.beginPath();
        if (f.segs && Array.isArray(f.segs)) {
          for (const seg of f.segs) path1(ctx, seg.map(p => [px(p[0]), py(p[1])]), false);
        } else if (f.PZ && f.PZ.length) {
          path1(ctx, f.PZ, false);
        }
        ctx.stroke();

        // Draw under-construction station rings (open hollow circles)
        if (f.st && f.st.length) {
          ctx.setLineDash([]);
          for (const ust of f.st) {
            const X = sx(ust.P[0]), Y = sy(ust.P[1]);
            if (X < -20 || Y < -20 || X > W + 20 || Y > H + 20) continue;
            ctx.beginPath();
            ctx.arc(X, Y, Math.max(3.2, 4.2 * S), 0, 2 * Math.PI);
            ctx.fillStyle = C.bg;
            ctx.fill();
            ctx.lineWidth = 2.0;
            ctx.strokeStyle = f.c || '#f59e0b';
            ctx.stroke();
          }
        }
        ctx.restore();
      }
    }

    // 5. Metro Lines
    const lw = k => Math.max(1.8, Math.min(28, 3.2 * S * k));
    const isLineActive = id => selectedLines.size === 0 || selectedLines.has(id);

    for (const l of PACK.lines || []) {
      const active = isLineActive(l.id);
      const isRouteActive = !!routeResult;
      ctx.lineWidth = lw(1);
      ctx.strokeStyle = l.c || '#2563eb';
      ctx.globalAlpha = active ? (isRouteActive ? 0.25 : 1) : 0.12;
      ctx.beginPath();
      for (const g of l.P || []) {
        if (!g || g.length < 2) continue;
        path1(ctx, g, false);
      }
      ctx.stroke();
      ctx.globalAlpha = 1;
    }

    // 6. Active Journey Route (Highlighted overlay)
    if (routeResult) {
      for (const leg of routeResult.legs) {
        ctx.save();
        ctx.lineWidth = lw(2.0);
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
    const r = z > 9000000 ? 8.5 : z > 4500000 ? 7 : z > 2200000 ? 5.8 : z > 1100000 ? 4.8 : z > 620000 ? 4 : z > 330000 ? 3.5 : 2.8;

    for (const s of PACK.stations || []) {
      const X = sx(s.P[0]), Y = sy(s.P[1]);
      if (X < -20 || Y < -20 || X > W + 20 || Y > H + 20) continue;

      const inRoute = routeResult && routeResult.stops.has(s.n);
      const isSel = selectedStation?.n === s.n;
      const isHov = hoverStation?.n === s.n;
      const radius = isSel ? r * 1.9 : isHov ? r * 1.5 : inRoute ? r * 1.35 : s.ix ? r * 1.3 : r * 1.0;

      if (s.ix) {
        ctx.beginPath();
        ctx.arc(X, Y, radius + 2.5, 0, 2 * Math.PI);
        ctx.fillStyle = C.bg;
        ctx.fill();
        ctx.lineWidth = 1.9;
        ctx.strokeStyle = inRoute ? C.ca : C.ix;
        ctx.stroke();
      }

      ctx.beginPath();
      ctx.arc(X, Y, radius, 0, 2 * Math.PI);
      ctx.fillStyle = inRoute ? C.ca : isSel ? '#f59e0b' : C.bg;
      ctx.fill();
      ctx.lineWidth = 1.6;
      ctx.strokeStyle = inRoute ? '#ffffff' : s.l && s.l[0] && LMAP[s.l[0]] ? LMAP[s.l[0]].c : C.ink;
      ctx.stroke();
    }

    // 8. Station Labels: NEVER visible by default; ONLY visible when scrolling/hovering over a station or selected
    ctx.textBaseline = 'middle';
    ctx.textAlign = 'left';
    ctx.font = `600 ${Math.max(10, Math.min(14, 12 * S))}px 'Sora',system-ui,sans-serif`;

    for (const s of PACK.stations || []) {
      const isSel = selectedStation?.n === s.n;
      const isHov = hoverStation?.n === s.n;

      // Absolutely zero names visible by default; strictly visible on scroll/hover/select
      if (!isHov && !isSel) continue;

      const X = sx(s.P[0]), Y = sy(s.P[1]);
      if (X < 15 || X > W - 140 || Y < 15 || Y > H - 15) continue;

      const lx = X + r * 1.6 + 6;
      const ly = Y;

      ctx.lineWidth = 4;
      ctx.strokeStyle = C.bg;
      ctx.strokeText(s.n, lx, ly);
      ctx.fillStyle = isSel ? '#d97706' : C.ink;
      ctx.fillText(s.n, lx, ly);
    }

    // Under-construction station names strictly visible on scroll/hover/select
    if (showFuture && PACK.future) {
      for (const f of PACK.future) {
        for (const s of f.st || []) {
          const isSel = selectedStation?.n === s.n;
          const isHov = hoverStation?.n === s.n;
          if (!isHov && !isSel) continue;

          const X = sx(s.P[0]), Y = sy(s.P[1]);
          if (X < 15 || X > W - 140 || Y < 15 || Y > H - 15) continue;

          const lx = X + r * 1.6 + 6;
          const ly = Y;

          ctx.lineWidth = 4;
          ctx.strokeStyle = C.bg;
          ctx.strokeText(`${s.n} (Under Construction)`, lx, ly);
          ctx.fillStyle = f.c || '#f59e0b';
          ctx.fillText(`${s.n} (Under Construction)`, lx, ly);
        }
      }
    }
  }, [theme, selectedLines, showFuture, routeResult, selectedStation, hoverStation, PACK, LMAP, SMAP, renderTrigger]);

  // Mouse Interaction handlers
  const dragRef = useRef({ dragging: false, startX: 0, startY: 0, moved: 0 });

  const handleMouseDown = e => {
    dragRef.current = {
      dragging: true,
      startX: e.clientX,
      startY: e.clientY,
      moved: 0,
    };
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
      setRenderTrigger(prev => prev + 1);
      return;
    }

    const view = viewRef.current;
    const sx = x => (x - view.cx) * view.z + cv.clientWidth / 2;
    const sy = y => (y - view.cy) * view.z + cv.clientHeight / 2;

    let nearest = null, bd = 24;
    for (const s of PACK.stations || []) {
      const d = Math.hypot(sx(s.P[0]) - cX, sy(s.P[1]) - cY);
      if (d < bd) {
        bd = d;
        nearest = s;
      }
    }
    if (showFuture && PACK.future) {
      for (const f of PACK.future) {
        for (const s of f.st || []) {
          const d = Math.hypot(sx(s.P[0]) - cX, sy(s.P[1]) - cY);
          if (d < bd) {
            bd = d;
            nearest = { ...s, l: [f.nm || f.lab || 'Under Construction Corridor'], isUnderConstruction: true, color: f.c || '#f59e0b' };
          }
        }
      }
    }
    setHoverStation(nearest);
    if (nearest) {
      setTooltip({
        x: cX,
        y: cY,
        name: nearest.n,
        hindi: nearest.hindi,
        lines: (nearest.l || []).map(id => LMAP[id]?.nm || id).join(' · '),
        interchange: nearest.ix,
        underConstruction: nearest.isUnderConstruction,
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
    const newZ = Math.max(30000, Math.min(14000000, oldZ * factor));

    const W = cv.clientWidth, H = cv.clientHeight;
    const pX = (cX - W / 2) / oldZ + viewRef.current.cx;
    const pY = (cY - H / 2) / oldZ + viewRef.current.cy;

    viewRef.current.z = newZ;
    viewRef.current.cx = pX - (cX - W / 2) / newZ;
    viewRef.current.cy = pY - (cY - H / 2) / newZ;

    const sx = x => (x - viewRef.current.cx) * newZ + W / 2;
    const sy = y => (y - viewRef.current.cy) * newZ + H / 2;
    let nearest = null, bd = 24;
    for (const s of PACK.stations || []) {
      const d = Math.hypot(sx(s.P[0]) - cX, sy(s.P[1]) - cY);
      if (d < bd) {
        bd = d;
        nearest = s;
      }
    }
    if (showFuture && PACK.future) {
      for (const f of PACK.future) {
        for (const s of f.st || []) {
          const d = Math.hypot(sx(s.P[0]) - cX, sy(s.P[1]) - cY);
          if (d < bd) {
            bd = d;
            nearest = { ...s, l: [f.nm || f.lab || 'Under Construction Corridor'], isUnderConstruction: true, color: f.c || '#f59e0b' };
          }
        }
      }
    }
    setHoverStation(nearest);
    if (nearest) {
      setTooltip({
        x: cX,
        y: cY,
        name: nearest.n,
        hindi: nearest.hindi,
        lines: (nearest.l || []).map(id => LMAP[id]?.nm || id).join(' · '),
        interchange: nearest.ix,
        underConstruction: nearest.isUnderConstruction,
      });
    } else {
      setTooltip(null);
    }

    setRenderTrigger(prev => prev + 1);
  };

  const handleZoom = delta => {
    const factor = delta > 0 ? 1.35 : 0.75;
    viewRef.current.z = Math.max(30000, Math.min(14000000, viewRef.current.z * factor));
    setRenderTrigger(prev => prev + 1);
  };

  const handleReset = () => {
    fitCityBounds(PACK);
    setSelectedStation(null);
  };

  const allStations = useMemo(() => {
    const list = [...(PACK.stations || [])];
    if (showFuture && PACK.future) {
      for (const f of PACK.future) {
        for (const s of f.st || []) {
          if (!list.some(x => x.n === s.n)) {
            list.push({ ...s, isUnderConstruction: true, l: [f.nm || f.lab || 'Under Construction'] });
          }
        }
      }
    }
    return list.sort((a, b) => a.n.localeCompare(b.n));
  }, [PACK, showFuture]);

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
        {PACK.future && PACK.future.length > 0 && (
          <button
            type="button"
            className={`polity-layer-pill ${showFuture ? 'active future' : ''}`}
            onClick={() => setShowFuture(prev => !prev)}
            title="Toggle under-construction and proposed corridors"
          >
            --- Under Construction ({PACK.future.length})
          </button>
        )}
        <button
          type="button"
          className="polity-layer-pill"
          onClick={() => {
            const all = new Set((PACK.lines || []).map(l => l.id));
            setSelectedLines(all);
          }}
        >
          All Lines ({PACK.lines?.length || 0})
        </button>
      </div>

      {/* Top Right Zoom Controls */}
      <div className="polity-top-zoom-controls" role="group" aria-label="Map Zoom and Fit Controls">
        <button
          type="button"
          className="polity-zoom-btn"
          onClick={() => handleZoom(1)}
          title="Zoom In (+)"
          aria-label="Zoom In"
        >
          + Zoom In
        </button>
        <button
          type="button"
          className="polity-zoom-btn"
          onClick={() => handleZoom(-1)}
          title="Zoom Out (−)"
          aria-label="Zoom Out"
        >
          − Zoom Out
        </button>
        <button
          type="button"
          className="polity-zoom-btn"
          onClick={handleReset}
          title="Reset Map View (↺)"
          aria-label="Reset View"
        >
          ↺ Fit View
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

      {/* Hover Tooltip (Appears when scrolling/hovering over any station) */}
      {tooltip && (
        <div
          className="polity-metro-tooltip"
          style={{ left: `${tooltip.x + 14}px`, top: `${tooltip.y + 14}px` }}
        >
          <div className="tooltip-title-row">
            <strong>{tooltip.name}</strong>
            {tooltip.hindi && <span className="tooltip-hindi">({tooltip.hindi})</span>}
          </div>
          <div className="tooltip-lines">{tooltip.lines}</div>
          {tooltip.underConstruction && <span className="tooltip-tag" style={{ color: '#f59e0b' }}>🚧 Under Construction / Proposed</span>}
          {tooltip.interchange && <span className="tooltip-tag">★ Interchange Junction</span>}
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
            {(selectedStation.l || []).map(id => {
              const l = LMAP[id];
              return (
                <span key={id} className="callout-line-pill" style={{ borderColor: l?.c || '#2563eb' }}>
                  <span className="line-dot" style={{ background: l?.c || '#2563eb' }} />
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
                  <span className="metric-pill">⏱ {routeResult.durationMin} min</span>
                  <span className="metric-pill">📏 {routeResult.km} km</span>
                  <span className="metric-pill">⬤ {routeResult.hops} stops</span>
                  <span className="metric-pill">⇄ {routeResult.changes} xchg</span>
                </div>

                <div className="results-fare">
                  <span className="fare-token">Token: ₹{routeResult.tokenFare}</span>
                  <span className="fare-smartcard">Smart Card: ₹{routeResult.smartCardFare}</span>
                </div>

                <div className="results-itinerary">
                  {routeResult.legs.map((leg, i) => (
                    <div key={i} className="itinerary-leg">
                      <div className="leg-indicator" style={{ background: leg.color }} />
                      <div className="leg-content">
                        <div className="leg-line-name" style={{ color: leg.color }}>
                          {leg.lineName}
                        </div>
                        <div className="leg-stations">
                          {leg.stops[0]} → {leg.stops[leg.stops.length - 1]}
                          <span className="leg-count"> ({leg.stops.length - 1} stops)</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="journey-hint">
                Pick origin and destination stations, or click any station circle directly on the terrain map.
              </div>
            )}
          </div>
        )}
      </div>

      {/* Bottom controls: Attribution on left, Zoom & Reset cluster on right */}
      <div className="polity-bottom-controls">
        <div className="polity-attribution">
          <span>Network and city geography: © OpenStreetMap contributors (ODbL). Corridors under construction: official city metro authority alignments.</span>
        </div>
        <div className="polity-zoom-btns" role="group" aria-label="Map Zoom and Fit Controls">
          <button
            type="button"
            onClick={() => handleZoom(1)}
            title="Zoom In (+)"
            aria-label="Zoom In"
          >
            +
          </button>
          <button
            type="button"
            onClick={() => handleZoom(-1)}
            title="Zoom Out (−)"
            aria-label="Zoom Out"
          >
            −
          </button>
          <button
            type="button"
            onClick={handleReset}
            title="Reset Map View (↺)"
            aria-label="Reset View"
          >
            ↺
          </button>
        </div>
      </div>
    </div>
  );
}
