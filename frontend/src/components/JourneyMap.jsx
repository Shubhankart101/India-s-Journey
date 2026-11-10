import { useEffect, useMemo, useRef, useState } from 'react';
import { formatInt, loadAtlasJson } from './atlasData.js';
import './JourneyMap.css';

// Keep behaviour identical to docs/journeys.js.
const VERSE_TRADITION = { Vedic: 'Hindu', Panchatantra: 'Hindu', Mahabharata: 'Hindu', Ramayana: 'Hindu', Buddhist: 'Buddhist', Jain: 'Jain', Sikh: 'Sikh' };
const project = (lon, lat, k) => [lon * k, -Math.log(Math.tan(Math.PI / 4 + (lat * Math.PI) / 360)) * (180 / Math.PI) * k];

function frameFor(points, k) {
  const xs = points.map(p => p[0]); const ys = points.map(p => p[1]);
  let w = Math.max(...xs) - Math.min(...xs); let h = Math.max(...ys) - Math.min(...ys);
  const cx = (Math.max(...xs) + Math.min(...xs)) / 2; const cy = (Math.max(...ys) + Math.min(...ys)) / 2;
  w = Math.max(w * 1.3, 16 * k); h = Math.max(h * 1.3, 12 * k);
  if (w / h > 4 / 3) h = (w * 3) / 4; else w = (h * 4) / 3;
  return { x: cx - w / 2, y: cy - h / 2, w, h };
}

function arc(a, b, bend) {
  const mx = (a[0] + b[0]) / 2; const my = (a[1] + b[1]) / 2;
  const dx = b[0] - a[0]; const dy = b[1] - a[1];
  return `M${a[0].toFixed(1)},${a[1].toFixed(1)}Q${(mx - dy * bend).toFixed(1)},${(my + dx * bend).toFixed(1)} ${b[0].toFixed(1)},${b[1].toFixed(1)}`;
}

function labelPositions(stops, points, frame, unit) {
  const baseRight = point => point[0] > frame.x + frame.w * 0.68;
  const baseTop = point => point[1] < frame.y + frame.h * 0.22;
  const directions = [
    { right: false, top: true }, { right: true, top: true },
    { right: false, top: false }, { right: true, top: false },
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
  const [playing, setPlaying] = useState(false);
  const alive = useRef(true);

  useEffect(() => {
    alive.current = true;
    Promise.all([loadAtlasJson('/data/faith-journeys.json'), loadAtlasJson('/maps/world-asia.json')])
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
    const timer = setInterval(() => setIdx(i => i + 1), 1900);
    return () => clearInterval(timer);
  }, [playing]);
  useEffect(() => {
    if (playing && idx >= last) { setPlaying(false); setIdx(last); }
  }, [playing, idx, last]);

  const land = useMemo(() => (basemap ? basemap.paths.map(p => <path key={p.i + p.n} d={p.d} className={p.i === 'IND' ? 'jm-india' : undefined}><title>{p.n}</title></path>) : null), [basemap]);
  const pts = useMemo(() => stops.map(stop => project(stop.lon, stop.lat, k)), [stops, k]);

  if (error) return <p className="jm-status">The journey map could not be loaded ({error}).</p>;
  if (!data || !basemap) return <p className="jm-status">Loading the journey map…</p>;
  if (!journey) return <p className="jm-status">Unknown journey “{id}”.</p>;

  const frame = frameFor(pts, k);
  const unit = frame.w / 100;
  const labels = labelPositions(stops, pts, frame, unit);
  const stop = stops[Math.min(idx, last)];
  const prev = stops[idx - 1];
  const legs = stops.slice(1);
  const maxLeg = Math.max(...legs.map(s => s.leg_km), 1);
  const totalKm = legs.reduce((sum, s) => sum + s.leg_km, 0);
  const slot = 560 / Math.max(legs.length, 1);
  const barW = Math.min(slot * 0.7, 44);

  const halt = () => setPlaying(false);
  const go = index => setIdx(Math.max(0, Math.min(last, index)));
  const pick = index => { halt(); go(index); };
  const onKey = index => event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); pick(index); } };

  return (
    <figure className={`journey${compact ? ' is-compact' : ''}`} aria-label={journey.title}>
      <p className="jm-intro">{journey.intro}</p>
      <div className="jm-bar">
        {journey.routes.length > 1 && (
          <div className="jm-routes" role="group" aria-label="Choose a route">
            {journey.routes.map((item, index) => (
              <button key={item.id} type="button" aria-pressed={index === routeIdx} onClick={() => { halt(); setRouteIdx(index); setIdx(0); }}>{item.label}</button>
            ))}
          </div>
        )}
        <button type="button" className="jm-play" aria-label={playing ? 'Pause' : 'Play the journey'} onClick={() => { if (playing) halt(); else { if (idx >= last) setIdx(0); setPlaying(true); } }}>{playing ? '❚❚' : '▶'}</button>
        <input type="range" min="0" max={last} value={idx} aria-label="Stop" onChange={event => pick(Number(event.target.value))} />
        <output className="jm-step" aria-live="polite">Stop {idx + 1} of {stops.length} · {stop.name}</output>
      </div>
      <div className="jm-main">
        <div className="jm-stage">
          <svg role="group" aria-label="Map of the journey" preserveAspectRatio="xMidYMid meet" viewBox={`${frame.x.toFixed(1)} ${frame.y.toFixed(1)} ${frame.w.toFixed(1)} ${frame.h.toFixed(1)}`} style={{ '--u': unit.toFixed(3) }}>
            <g className="jm-land">{land}</g>
            <g className="jm-legs">
              {pts.slice(1).map((pt, i) => <path key={`g${i}`} className="jm-ghost" d={arc(pts[i], pt, 0.12)} />)}
              {pts.slice(1).map((pt, i) => <path key={`l${i}`} className={`jm-leg${i + 1 <= idx ? ' is-done' : ''}${i + 1 === idx ? ' is-active' : ''}`} d={arc(pts[i], pt, 0.12)} pathLength="1" style={{ stroke: route.colour }} />)}
            </g>
            <g className="jm-stops">
              {stops.map((s, i) => (
                <g key={s.id || i} className={`jm-stop${s.approximate ? ' is-approx' : ''}${i === idx ? ' is-current' : ''}${i < idx ? ' is-visited' : ''}${i > idx ? ' is-future' : ''}`}
                  transform={`translate(${pts[i][0].toFixed(1)} ${pts[i][1].toFixed(1)})`} tabIndex={0} role="button" aria-label={`Stop ${i + 1}: ${s.name}`} aria-pressed={i === idx}
                  onClick={() => pick(i)} onKeyDown={onKey(i)}>
                  <title>{s.name}</title>
                  <circle r={(unit * 1.55).toFixed(2)} style={{ '--pin': route.colour }} />
                  <text y={(unit * 0.55).toFixed(2)} fontSize={(unit * 1.7).toFixed(2)}>{i + 1}</text>
                  <text className="jm-label" x={labels[i].x.toFixed(2)} y={labels[i].y.toFixed(2)} textAnchor={labels[i].anchor} fontSize={(unit * 1.9).toFixed(2)}>{s.name}</text>
                </g>
              ))}
            </g>
          </svg>
        </div>
        <aside className="jm-side">
          <div className="jm-detail" aria-live="polite">
            <h4>{idx + 1}. {stop.name} <small>{stop.when}</small></h4>
            <p className="jm-legline">{prev ? `${formatInt(stop.leg_km)} km (straight line) from ${prev.name}` : 'Where this route begins'}</p>
            <p>{stop.description}</p>
            {stop.approximate && <p className="jm-approx">Location is approximate (shown with a dashed ring).</p>}
            <Verse quote={stop.quote} tradition={journey.tradition} />
          </div>
          <div className="jm-nav">
            <button type="button" disabled={idx === 0} onClick={() => pick(idx - 1)}>← Previous stop</button>
            <button type="button" disabled={idx === last} onClick={() => pick(idx + 1)}>Next stop →</button>
          </div>
        </aside>
      </div>
      {legs.length > 0 && !compact && (
        <div className="jm-chart">
          <h5>Distance of each leg <small>straight line, km · total {formatInt(totalKm)} km over {legs.length} legs</small></h5>
          <svg viewBox="0 0 600 124" role="group" aria-label={`Bar chart of the distance of each leg of ${route.label}`}>
            {legs.map((s, i) => {
              const h = Math.max(2, (s.leg_km / maxLeg) * 92); const x = 20 + i * slot + (slot - barW) / 2;
              return (
                <g key={s.id || i} className={`jm-bar-item${idx === i + 1 ? ' is-current' : ''}${idx > i ? ' is-done' : ''}`} tabIndex={0} role="button"
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
