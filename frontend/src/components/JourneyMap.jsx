import { useEffect, useMemo, useRef, useState } from 'react';
import { assetUrl } from '../config.js';
import { formatInt, loadAtlasJson, showTip } from './atlasData.js';
import './JourneyMap.css';

// Shared projection & verse tradition mapping across the journey datasets.
const VERSE_TRADITION = { Vedic: 'Hindu', Panchatantra: 'Hindu', Mahabharata: 'Hindu', Ramayana: 'Hindu', Buddhist: 'Buddhist', Jain: 'Jain', Sikh: 'Sikh' };
const project = (lon, lat, k) => [lon * k, -Math.log(Math.tan(Math.PI / 4 + (lat * Math.PI) / 360)) * (180 / Math.PI) * k];

function frameFor(points, k) {
  const xs = points.map(p => p[0]);
  const ys = points.map(p => p[1]);
  let w = Math.max(...xs) - Math.min(...xs);
  let h = Math.max(...ys) - Math.min(...ys);
  const cx = (Math.max(...xs) + Math.min(...xs)) / 2;
  const cy = (Math.max(...ys) + Math.min(...ys)) / 2;
  w = Math.max(w * 1.32, 16 * k);
  h = Math.max(h * 1.32, 12 * k);
  if (w / h > 4 / 3) h = (w * 3) / 4;
  else w = (h * 4) / 3;
  return { x: cx - w / 2, y: cy - h / 2, w, h };
}

function arcGeometry(a, b, bend) {
  const mx = (a[0] + b[0]) / 2;
  const my = (a[1] + b[1]) / 2;
  const dx = b[0] - a[0];
  const dy = b[1] - a[1];
  const cx = mx - dy * bend;
  const cy = my + dx * bend;
  const d = `M${a[0].toFixed(1)},${a[1].toFixed(1)}Q${cx.toFixed(1)},${cy.toFixed(1)} ${b[0].toFixed(1)},${b[1].toFixed(1)}`;
  const midX = 0.25 * a[0] + 0.5 * cx + 0.25 * b[0];
  const midY = 0.25 * a[1] + 0.5 * cy + 0.25 * b[1];
  const angle = (Math.atan2(dy, dx) * 180) / Math.PI;
  return { d, midX, midY, angle };
}

function labelPositions(stops, points, frame, unit) {
  const baseRight = point => point[0] > frame.x + frame.w * 0.68;
  const baseTop = point => point[1] < frame.y + frame.h * 0.22;
  const directions = [
    { right: false, top: true },
    { right: true, top: true },
    { right: false, top: false },
    { right: true, top: false },
  ];
  const placed = [];
  return stops.map((stop, index) => {
    const point = points[index];
    const duplicate = placed.find(prior => Math.hypot(point[0] - prior.point[0], point[1] - prior.point[1]) < unit * 0.4);
    const preferred = duplicate ? { right: !duplicate.right, top: duplicate.top } : { right: baseRight(point), top: baseTop(point) };
    const candidates = [preferred, ...directions.filter(item => item.right !== preferred.right || item.top !== preferred.top)];
    const fontSize = unit * 1.9;
    const width = Math.max(unit * 2, [...stop.name].length * fontSize * 0.56);
    const boxes = candidates.map(({ right, top }) => {
      const x = right ? -unit * 2.2 : unit * 2.2;
      const y = top ? unit * 3.2 : -unit * 2.2;
      const baselineX = point[0] + x;
      const baselineY = point[1] + y;
      const left = right ? baselineX - width : baselineX;
      const box = { left, right: left + width, top: baselineY - fontSize * 0.9, bottom: baselineY + fontSize * 0.3 };
      let cost = Math.max(0, frame.x - box.left, box.right - (frame.x + frame.w), frame.y - box.top, box.bottom - (frame.y + frame.h)) * 20;
      for (const prior of placed) {
        if (box.left < prior.right && box.right > prior.left && box.top < prior.bottom && box.bottom > prior.top) cost += unit * 20;
      }
      points.forEach((other, otherIndex) => {
        if (otherIndex === index) return;
        if (box.left < other[0] + unit * 1.8 && box.right > other[0] - unit * 1.8 && box.top < other[1] + unit * 1.8 && box.bottom > other[1] - unit * 1.8) cost += unit * 2;
      });
      return { right, x, y, box, cost };
    });
    boxes.sort((a, b) => a.cost - b.cost);
    const best = boxes[0];
    placed.push({ ...best.box, right: best.right, top: best.top, point });
    return { x: best.x, y: best.y, anchor: best.right ? 'end' : 'start' };
  });
}

function buildGraticule(viewFrame, k) {
  const stepDeg = viewFrame.w / k > 45 ? 15 : viewFrame.w / k > 18 ? 10 : 5;
  const minLon = Math.floor(viewFrame.x / k / stepDeg) * stepDeg;
  const maxLon = Math.ceil((viewFrame.x + viewFrame.w) / k / stepDeg) * stepDeg;
  const lons = [];
  for (let lon = minLon; lon <= maxLon; lon += stepDeg) {
    if (lon >= -40 && lon <= 160) lons.push({ lon, x: lon * k });
  }
  const lats = [];
  for (let lat = -15; lat <= 60; lat += stepDeg) {
    const [, py] = project(0, lat, k);
    if (py >= viewFrame.y && py <= viewFrame.y + viewFrame.h) lats.push({ lat, y: py });
  }
  return { lons, lats };
}

function formatCoords(lat, lon) {
  const ns = lat >= 0 ? 'N' : 'S';
  const ew = lon >= 0 ? 'E' : 'W';
  return `${Math.abs(lat).toFixed(2)}\u00b0${ns}, ${Math.abs(lon).toFixed(2)}\u00b0${ew}`;
}

function Verse({ quote, tradition }) {
  return (
    <figure className="scripture-verse jm-verse" data-tradition={VERSE_TRADITION[tradition] || 'Hindu'}>
      <blockquote lang={quote.lang}>{quote.text}</blockquote>
      <p className="scripture-english">{quote.translation}</p>
      <figcaption>
        <span className="scripture-badge"><i className="scripture-dot" aria-hidden="true" />{quote.work}</span>{' '}
        <cite>{quote.citation}</cite>{' '}
        <a href={quote.verified_from} target="_blank" rel="noreferrer">verified from the source</a>
        {quote.generic && <span className="jm-generic" title="No verse about this exact place could be checked online, so a verified verse of the same text is shown">{quote.label || 'From the text (general)'}</span>}
        {quote.note && <small className="jm-note">{quote.note}</small>}
      </figcaption>
    </figure>
  );
}

export default function JourneyMap({ id, compact = false }) {
  const [data, setData] = useState(null);
  const [basemap, setBasemap] = useState(null);
  const [error, setError] = useState('');
  const [routeIdx, setRouteIdx] = useState(0);
  const [idx, setIdx] = useState(0);
  const [hoverIdx, setHoverIdx] = useState(null);
  const [playing, setPlaying] = useState(false);
  const [speedMs, setSpeedMs] = useState(1900);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [followStop, setFollowStop] = useState(false);
  const [indiaRegion, setIndiaRegion] = useState(false);
  const [showLabels, setShowLabels] = useState(false);
  const [stopQuery, setStopQuery] = useState('');
  const [tip, setTip] = useState(null);
  const stageRef = useRef(null);
  const dragRef = useRef(null);
  const alive = useRef(true);

  useEffect(() => {
    alive.current = true;
    Promise.all([loadAtlasJson(assetUrl('data/faith-journeys.json')), loadAtlasJson(assetUrl('maps/world-asia.json'))])
      .then(([journeys, base]) => { if (alive.current) { setData(journeys); setBasemap(base); } })
      .catch(err => { if (alive.current) setError(err.message); });
    return () => { alive.current = false; };
  }, []);

  const journey = data?.journeys.find(item => item.id === id);
  const route = journey?.routes[routeIdx];
  const k = basemap?.k || 10;
  const stops = route?.stops || [];
  const last = Math.max(stops.length - 1, 0);

  useEffect(() => {
    if (!playing) return undefined;
    const timer = setInterval(() => setIdx(i => i + 1), speedMs);
    return () => clearInterval(timer);
  }, [playing, speedMs]);

  useEffect(() => {
    if (playing && idx >= last) {
      setPlaying(false);
      setIdx(last);
    }
  }, [playing, idx, last]);

  const land = useMemo(
    () => (basemap ? basemap.paths.map(p => <path key={p.i + p.n} d={p.d} className={p.i === 'IND' ? 'jm-india' : undefined}><title>{p.n}</title></path>) : null),
    [basemap],
  );
  const pts = useMemo(() => stops.map(stop => project(stop.lon, stop.lat, k)), [stops, k]);
  const indiaStops = useMemo(
    () => stops.map((s, i) => ({ s, pt: pts[i] })).filter(({ s }) => s.lon >= 66 && s.lon <= 99 && s.lat >= 5 && s.lat <= 39),
    [stops, pts],
  );

  if (error) return <p className="jm-status">The journey map could not be loaded ({error}).</p>;
  if (!data || !basemap) return <p className="jm-status">Loading the journey map…</p>;
  if (!journey) return <p className="jm-status">Unknown journey “{id}”.</p>;

  const fullFrame = frameFor(pts, k);
  const canFocusIndia = indiaStops.length >= 2 && (fullFrame.w / k > 38);
  const regionBaseFrame = (indiaRegion && canFocusIndia)
    ? frameFor(indiaStops.map(item => item.pt), k)
    : fullFrame;

  const activeZoom = followStop && zoom <= 1 ? 2.4 : zoom;
  const safeIdx = Math.min(idx, last);
  const activePt = pts[safeIdx] || [regionBaseFrame.x + regionBaseFrame.w / 2, regionBaseFrame.y + regionBaseFrame.h / 2];
  const viewW = regionBaseFrame.w / activeZoom;
  const viewH = regionBaseFrame.h / activeZoom;
  const defaultCx = followStop ? activePt[0] : regionBaseFrame.x + regionBaseFrame.w / 2 + pan.x;
  const defaultCy = followStop ? activePt[1] : regionBaseFrame.y + regionBaseFrame.h / 2 + pan.y;
  const maxPanX = regionBaseFrame.w * 0.55;
  const maxPanY = regionBaseFrame.h * 0.55;
  const baseCx = regionBaseFrame.x + regionBaseFrame.w / 2;
  const baseCy = regionBaseFrame.y + regionBaseFrame.h / 2;
  const cx = Math.max(baseCx - maxPanX, Math.min(baseCx + maxPanX, defaultCx));
  const cy = Math.max(baseCy - maxPanY, Math.min(baseCy + maxPanY, defaultCy));
  const viewFrame = { x: cx - viewW / 2, y: cy - viewH / 2, w: viewW, h: viewH };

  const unit = viewFrame.w / 100;
  const labels = labelPositions(stops, pts, viewFrame, unit);
  const graticule = !compact ? buildGraticule(viewFrame, k) : { lons: [], lats: [] };
  const arcCurves = pts.slice(1).map((pt, i) => arcGeometry(pts[i], pt, 0.12));

  const stop = stops[safeIdx];
  const prev = stops[safeIdx - 1];
  const legs = stops.slice(1);
  const maxLeg = Math.max(...legs.map(s => s.leg_km), 1);
  const totalKm = legs.reduce((sum, s) => sum + s.leg_km, 0);
  const cumulativeKm = stops.slice(0, safeIdx + 1).reduce((sum, s) => sum + (s.leg_km || 0), 0);
  const approxCount = stops.filter(s => s.approximate).length;
  const slot = 560 / Math.max(legs.length, 1);
  const barW = Math.min(slot * 0.72, 44);

  const halt = () => setPlaying(false);
  const go = index => setIdx(Math.max(0, Math.min(last, index)));
  const pick = index => { halt(); go(index); };
  const onKey = index => event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); pick(index); } };
  const resetCamera = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
    setFollowStop(false);
    setIndiaRegion(false);
  };
  const changeRoute = (index) => {
    halt();
    setRouteIdx(index);
    setIdx(0);
    setStopQuery('');
    setHoverIdx(null);
    resetCamera();
  };

  const onStagePointerDown = (event) => {
    if (compact || activeZoom <= 1 || event.target.closest('.jm-stop, .jm-map-controls')) return;
    dragRef.current = { x: event.clientX, y: event.clientY, startPan: { ...pan } };
  };
  const onStagePointerMove = (event) => {
    if (!dragRef.current || !stageRef.current) return;
    const rect = stageRef.current.getBoundingClientRect();
    const dx = ((event.clientX - dragRef.current.x) / rect.width) * viewFrame.w;
    const dy = ((event.clientY - dragRef.current.y) / rect.height) * viewFrame.h;
    if (Math.abs(event.clientX - dragRef.current.x) > 3 || Math.abs(event.clientY - dragRef.current.y) > 3) {
      setFollowStop(false);
      setPan({ x: dragRef.current.startPan.x - dx, y: dragRef.current.startPan.y - dy });
    }
  };
  const onStagePointerUp = () => { dragRef.current = null; };

  const queryLower = stopQuery.trim().toLowerCase();
  const visibleStops = stops
    .map((s, i) => ({ s, i }))
    .filter(({ s }) => !queryLower || `${s.name} ${s.when} ${s.description}`.toLowerCase().includes(queryLower));

  return (
    <figure className={`journey${compact ? ' is-compact' : ''}`} aria-label={journey.title}>
      <p className="jm-intro">{journey.intro}</p>
      {!compact && (
        <div className="jm-stats" aria-label="Journey route summary">
          <div><span>Plot points</span><strong>{stops.length} stops</strong></div>
          <div><span>Covered so far</span><strong>{formatInt(cumulativeKm)} km</strong> <small>/ {formatInt(totalKm)} km</small></div>
          <div><span>Approximate pins</span><strong>{approxCount}</strong> <small>dashed ring</small></div>
          <div><span>Origin → Terminus</span><strong>{stops[0]?.name.split('(')[0].trim()} → {stops[last]?.name.split('(')[0].trim()}</strong></div>
        </div>
      )}
      <div className="jm-bar">
        {journey.routes.length > 1 && (
          <div className="jm-routes" role="group" aria-label="Choose a route">
            {journey.routes.map((item, index) => (
              <button key={item.id} type="button" aria-pressed={index === routeIdx} onClick={() => changeRoute(index)}>{item.label} ({item.stops.length})</button>
            ))}
          </div>
        )}
        <button type="button" className="jm-play" aria-label={playing ? 'Pause' : 'Play the journey'} onClick={() => { if (playing) halt(); else { if (safeIdx >= last) setIdx(0); setPlaying(true); } }}>{playing ? '❚❚' : '▶'}</button>
        <button type="button" className="jm-speed" aria-label="Restart route" title="Back to Stop 1" onClick={() => pick(0)} disabled={safeIdx === 0 && !playing}>↺</button>
        <button type="button" className="jm-speed" aria-label={`Playback speed ${speedMs < 1500 ? '2x' : '1x'}`} onClick={() => setSpeedMs(ms => (ms < 1500 ? 1900 : 1000))}>{speedMs < 1500 ? '2×' : '1×'}</button>
        <input type="range" min="0" max={last} value={safeIdx} aria-label="Stop" onChange={event => pick(Number(event.target.value))} />
        <output className="jm-step" aria-live="polite">Stop {safeIdx + 1} of {stops.length} · {stop.name}</output>
      </div>
      <div className="jm-main">
        <div
          className={`jm-stage${activeZoom > 1 ? ' is-zoomed' : ''}`}
          ref={stageRef}
          onPointerDown={onStagePointerDown}
          onPointerMove={onStagePointerMove}
          onPointerUp={onStagePointerUp}
          onPointerLeave={() => { onStagePointerUp(); setTip(null); setHoverIdx(null); }}
        >
          {!compact && (
            <div className="jm-map-controls" role="toolbar" aria-label="Map camera and label controls">
              <button type="button" aria-label="Zoom in map" onClick={() => { setFollowStop(false); setZoom(z => Math.min(6, Number((z * 1.5).toFixed(2)))); }}>+</button>
              <button type="button" aria-label="Zoom out map" onClick={() => { setFollowStop(false); setZoom(z => { const nz = Math.max(1, Number((z / 1.5).toFixed(2))); if (nz <= 1.05) { setPan({ x: 0, y: 0 }); return 1; } return nz; }); }}>−</button>
              <button type="button" aria-label="Reset map zoom" onClick={resetCamera} disabled={activeZoom === 1 && !indiaRegion && !followStop}>Reset</button>
              <button type="button" aria-pressed={followStop} aria-label="Follow active stop" onClick={() => setFollowStop(f => { if (!f) setPan({ x: 0, y: 0 }); return !f; })}>◎ Follow</button>
              {canFocusIndia && (
                <button type="button" aria-pressed={indiaRegion} aria-label="Focus South Asia stops" onClick={() => { setPan({ x: 0, y: 0 }); setZoom(1); setFollowStop(false); setIndiaRegion(v => !v); }}>
                  {indiaRegion ? 'Full corridor' : 'Focus India'}
                </button>
              )}
              <button type="button" aria-pressed={showLabels} aria-label="Toggle all map stop labels" onClick={() => setShowLabels(s => !s)}>Labels</button>
            </div>
          )}
          <svg
            role="group"
            aria-label="Map of the journey"
            preserveAspectRatio="xMidYMid meet"
            viewBox={`${viewFrame.x.toFixed(1)} ${viewFrame.y.toFixed(1)} ${viewFrame.w.toFixed(1)} ${viewFrame.h.toFixed(1)}`}
            style={{ '--u': unit.toFixed(3) }}
          >
            {!compact && (
              <g className="jm-graticule" aria-hidden="true">
                {graticule.lons.map(g => (
                  <line key={`lon-${g.lon}`} x1={g.x.toFixed(1)} y1={viewFrame.y.toFixed(1)} x2={g.x.toFixed(1)} y2={(viewFrame.y + viewFrame.h).toFixed(1)} />
                ))}
                {graticule.lats.map(g => (
                  <line key={`lat-${g.lat}`} x1={viewFrame.x.toFixed(1)} y1={g.y.toFixed(1)} x2={(viewFrame.x + viewFrame.w).toFixed(1)} y2={g.y.toFixed(1)} />
                ))}
              </g>
            )}
            <g className="jm-land">{land}</g>
            <g className="jm-legs">
              {arcCurves.map((geom, i) => <path key={`g${i}`} className="jm-ghost" d={geom.d} />)}
              {arcCurves.map((geom, i) => (
                <path key={`l${i}`} className={`jm-leg${i + 1 <= safeIdx ? ' is-done' : ''}${i + 1 === safeIdx ? ' is-active' : ''}`} d={geom.d} pathLength="1" style={{ stroke: route.colour }} />
              ))}
              {!compact && arcCurves.map((geom, i) => (i + 1 <= safeIdx ? (
                <path
                  key={`c${i}`}
                  className="jm-chevron"
                  d={`M${(-unit * 0.9).toFixed(2)},${(-unit * 0.55).toFixed(2)} L${(unit * 0.6).toFixed(2)},0 L${(-unit * 0.9).toFixed(2)},${(unit * 0.55).toFixed(2)}`}
                  transform={`translate(${geom.midX.toFixed(1)} ${geom.midY.toFixed(1)}) rotate(${geom.angle.toFixed(1)})`}
                  style={{ stroke: route.colour }}
                />
              ) : null))}
            </g>
            <g className="jm-stops">
              {[...stops.map((s, i) => ({ s, i }))].sort((a, b) => {
                const aPri = a.i === safeIdx ? 2 : a.i === hoverIdx ? 1 : 0;
                const bPri = b.i === safeIdx ? 2 : b.i === hoverIdx ? 1 : 0;
                return aPri - bPri || a.i - b.i;
              }).map(({ s, i }) => {
                const isCurrent = i === safeIdx;
                const isHovered = i === hoverIdx;
                const isEndpoint = i === 0 || i === last;
                const showPinLabel = showLabels || isCurrent || isHovered;
                return (
                  <g
                    key={s.id || i}
                    className={`jm-stop${s.approximate ? ' is-approx' : ''}${isCurrent ? ' is-current' : ''}${i < safeIdx ? ' is-visited' : ''}${i > safeIdx ? ' is-future' : ''}${isHovered ? ' is-hovered' : ''}${isEndpoint ? ' is-endpoint' : ''}${showPinLabel ? ' show-label' : ''}`}
                    transform={`translate(${pts[i][0].toFixed(1)} ${pts[i][1].toFixed(1)})`}
                    tabIndex={0}
                    role="button"
                    aria-label={`Stop ${i + 1}: ${s.name}`}
                    aria-pressed={isCurrent}
                    onClick={() => pick(i)}
                    onKeyDown={onKey(i)}
                    onPointerEnter={event => {
                      if (!stageRef.current || compact) return;
                      setHoverIdx(i);
                      showTip(event, stageRef.current, setTip, [`${i + 1}. ${s.name}`, `${s.when}${i > 0 ? ` · +${formatInt(s.leg_km)} km` : ' · Origin'}`]);
                    }}
                    onFocus={event => {
                      if (!stageRef.current || compact) return;
                      setHoverIdx(i);
                      showTip(event, stageRef.current, setTip, [`${i + 1}. ${s.name}`, `${s.when}${i > 0 ? ` · +${formatInt(s.leg_km)} km` : ' · Origin'}`]);
                    }}
                    onPointerLeave={() => { setHoverIdx(null); setTip(null); }}
                    onBlur={() => { setHoverIdx(null); setTip(null); }}
                  >
                    <title>{s.name}</title>
                    {isCurrent && !compact && <circle className="jm-pulse" r={(unit * 2.5).toFixed(2)} style={{ stroke: route.colour }} />}
                    <circle r={(unit * (isCurrent ? 1.8 : 1.48)).toFixed(2)} style={{ '--pin': route.colour }} />
                    <text y={(unit * 0.54).toFixed(2)} fontSize={(unit * (stops.length > 15 ? 1.45 : 1.65)).toFixed(2)}>{i + 1}</text>
                    <text className="jm-label" x={labels[i].x.toFixed(2)} y={labels[i].y.toFixed(2)} textAnchor={labels[i].anchor} fontSize={(unit * 1.9).toFixed(2)}>{s.name}</text>
                  </g>
                );
              })}
            </g>
          </svg>
          {!compact && <div className="jm-compass" aria-hidden="true"><span>N</span><b>↑</b></div>}
          {!compact && tip && (
            <div className="jm-tip" role="tooltip" style={{ left: tip.left, top: tip.top }}>
              <b>{tip.content[0]}</b>
              <small>{tip.content[1]}</small>
            </div>
          )}
        </div>
        <aside className="jm-side">
          <div className="jm-detail" aria-live="polite">
            <div className="jm-detail-meta">
              <span>{stop.when}</span>
              <span>{formatCoords(stop.lat, stop.lon)}</span>
            </div>
            <h4>{safeIdx + 1}. {stop.name} <small>{stop.when}</small></h4>
            <p className="jm-legline">
              {prev
                ? `${formatInt(stop.leg_km)} km from ${prev.name} · ${formatInt(cumulativeKm)} of ${formatInt(totalKm)} km covered`
                : `Origin of ${route.label} (${formatInt(totalKm)} km across ${stops.length} plot points)`}
            </p>
            <p>{stop.description}</p>
            {stop.approximate && <p className="jm-approx">Location is approximate (shown with a dashed ring).</p>}
            <Verse quote={stop.quote} tradition={journey.tradition} />
          </div>
          <div className="jm-nav">
            <button type="button" disabled={safeIdx === 0} onClick={() => pick(safeIdx - 1)}>← Previous stop</button>
            <button type="button" disabled={safeIdx === last} onClick={() => pick(safeIdx + 1)}>Next stop →</button>
          </div>
        </aside>
      </div>
      {!compact && (
        <div className="jm-itinerary" aria-label="Chronological stops along this route">
          <div className="jm-itinerary-head">
            <h5>Route itinerary ({stops.length} plot points)</h5>
            {stops.length >= 6 && (
              <label className="jm-find">
                <span className="sr-only">Filter stops in this route</span>
                <input
                  type="search"
                  placeholder="Find a stop or event…"
                  value={stopQuery}
                  onChange={e => setStopQuery(e.target.value)}
                />
              </label>
            )}
          </div>
          <ol className="jm-stop-chips">
            {visibleStops.map(({ s, i }) => (
              <li key={s.id || i}>
                <button
                  type="button"
                  className={`jm-chip${i === safeIdx ? ' is-current' : ''}${i < safeIdx ? ' is-visited' : ''}`}
                  aria-pressed={i === safeIdx}
                  onClick={() => pick(i)}
                >
                  <span className="jm-chip-num" style={{ background: i <= safeIdx ? route.colour : undefined }}>{i + 1}</span>
                  <span className="jm-chip-name">{s.name}</span>
                  <small className="jm-chip-meta">{i > 0 ? `+${formatInt(s.leg_km)} km` : 'Start'}{s.approximate ? ' · ≈' : ''}</small>
                </button>
              </li>
            ))}
          </ol>
        </div>
      )}
      {legs.length > 0 && !compact && (
        <div className="jm-chart">
          <h5>Distance of each leg <small>straight line, km · total {formatInt(totalKm)} km over {legs.length} legs</small></h5>
          <svg viewBox="0 0 600 124" role="group" aria-label={`Bar chart of the distance of each leg of ${route.label}`}>
            {legs.map((s, i) => {
              const h = Math.max(2, (s.leg_km / maxLeg) * 92);
              const x = 20 + i * slot + (slot - barW) / 2;
              return (
                <g key={s.id || i} className={`jm-bar-item${safeIdx === i + 1 ? ' is-current' : ''}${safeIdx > i ? ' is-done' : ''}`} tabIndex={0} role="button"
                  aria-label={`Leg ${i + 1}: ${stops[i].name} to ${s.name}, ${formatInt(s.leg_km)} km`} onClick={() => pick(i + 1)} onKeyDown={onKey(i + 1)}>
                  <title>{stops[i].name} → {s.name}: {formatInt(s.leg_km)} km</title>
                  <rect x={x.toFixed(1)} y={(104 - h).toFixed(1)} width={barW.toFixed(1)} height={h.toFixed(1)} rx="3" style={{ fill: route.colour }} />
                  <text x={(x + barW / 2).toFixed(1)} y="118" textAnchor="middle">{i + 2}</text>
                  {legs.length <= 12 && <text className="jm-km" x={(x + barW / 2).toFixed(1)} y={(100 - h).toFixed(1)} textAnchor="middle">{formatInt(s.leg_km)}</text>}
                </g>
              );
            })}
          </svg>
        </div>
      )}
      <details className="jm-method">
        <summary>Methodology</summary>
        <ul>{(data.meta.methodology || []).map(line => <li key={line}>{line}</li>)}</ul>
      </details>
    </figure>
  );
}
