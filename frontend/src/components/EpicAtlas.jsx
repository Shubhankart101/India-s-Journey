import { useEffect, useMemo, useRef, useState } from 'react';
import { assetUrl } from '../config.js';
import { formatInt, loadAtlas, showTip } from './atlasData.js';
import ScriptureVerse from './ScriptureVerse.jsx';
import './Atlas.css';

const DATA_URL = assetUrl('data/epic-kingdoms.json');

const REGION_PRESETS = [
  { id: 'all', label: 'All India', cx: 0.5, cy: 0.5, zoom: 1 },
  { id: 'north', label: 'North & Doab', cx: 0.42, cy: 0.30, zoom: 2.15 },
  { id: 'east', label: 'East & Magadha', cx: 0.67, cy: 0.37, zoom: 2.15 },
  { id: 'south', label: 'Deccan & Lanka', cx: 0.46, cy: 0.78, zoom: 2.05 },
];

export default function EpicAtlas({ compact = false, title = 'Epic kingdoms', epic: initialEpic = 'mahabharata' }) {
  const [loaded, setLoaded] = useState(null);
  const [error, setError] = useState('');
  const [epicKey, setEpicKey] = useState(initialEpic);
  const [pin, setPin] = useState(null);
  const [sideFilters, setSideFilters] = useState([]);
  const [view, setView] = useState('kingdoms');
  const [query, setQuery] = useState('');
  const [tip, setTip] = useState(null);
  const [stage, setStage] = useState(null);
  const [routeOn, setRouteOn] = useState(false);
  const [step, setStep] = useState(0);
  const [hoverStop, setHoverStop] = useState(null);
  const [playing, setPlaying] = useState(false);
  const [speedMs, setSpeedMs] = useState(1900);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [regionId, setRegionId] = useState('all');
  const [followRouteStop, setFollowRouteStop] = useState(false);
  const dragRef = useRef(null);

  useEffect(() => {
    if (!playing) return undefined;
    const timer = setInterval(() => setStep(s => s + 1), speedMs);
    return () => clearInterval(timer);
  }, [playing, speedMs]);

  useEffect(() => {
    let cancelled = false;
    loadAtlas(DATA_URL).then(([data, geometry]) => { if (!cancelled) setLoaded({ data, geometry }); }, err => { if (!cancelled) setError(err.message); });
    return () => { cancelled = true; };
  }, []);

  const data = loaded?.data;
  const geometry = loaded?.geometry;
  const epics = data ? Object.keys(data.epics) : [];
  const epic = data ? data.epics[epics.includes(epicKey) ? epicKey : epics[0]] : null;
  const rstops = epic?.route?.stops || [];
  const rlast = Math.max(rstops.length - 1, 0);

  useEffect(() => {
    if (playing && step >= rlast) {
      setPlaying(false);
      setStep(rlast);
    }
  }, [playing, step, rlast]);

  const outline = useMemo(
    () => (geometry ? Object.entries(geometry.states).map(([name, d]) => <path key={name} d={d} className="atlas-outline" />) : null),
    [geometry],
  );

  if (error) return <p className="atlas-status">The atlas could not be loaded ({error}).</p>;
  if (!loaded) return <p className="atlas-status">Loading the epic atlas…</p>;

  const colourOf = entry => epic.sides[entry.side]?.colour || '#8d8d8d';
  const matches = entry => !query || `${entry.name} ${entry.name_sa} ${entry.modern_location}`.toLowerCase().includes(query.toLowerCase());
  const shown = entry => matches(entry) && (!sideFilters.length || sideFilters.includes(entry.side));
  const visibleEntries = epic.entries.filter(shown);
  const selected = epic.entries.find(entry => entry.id === pin);
  const select = id => setPin(pin === id ? null : id);
  const rstep = Math.min(step, rlast);
  const rstop = rstops[rstep];
  const rprev = rstops[rstep - 1];
  const totalRouteKm = rstops.reduce((sum, s) => sum + (Number(s.leg_km) || 0), 0);
  const cumulativeRouteKm = rstops.slice(0, rstep + 1).reduce((sum, s) => sum + (Number(s.leg_km) || 0), 0);
  const battleStopsCount = rstops.filter(s => s.kind === 'battle').length;

  const halt = () => setPlaying(false);
  const goStep = index => { halt(); setStep(Math.max(0, Math.min(rlast, index))); };

  const [vbX, vbY, vbW, vbH] = (geometry.viewBox || '0 0 1000 1115').split(/\s+/).map(Number);
  const effectiveZoom = (view === 'route' && routeOn && followRouteStop && rstop && zoom <= 1) ? 2.15 : zoom;
  const targetW = vbW / effectiveZoom;
  const targetH = vbH / effectiveZoom;
  const baseCx = (view === 'route' && routeOn && followRouteStop && rstop) ? rstop.x : vbX + vbW / 2 + pan.x;
  const baseCy = (view === 'route' && routeOn && followRouteStop && rstop) ? rstop.y : vbY + vbH / 2 + pan.y;
  const clampedCx = Math.max(vbX + targetW * 0.25, Math.min(vbX + vbW - targetW * 0.25, baseCx));
  const clampedCy = Math.max(vbY + targetH * 0.25, Math.min(vbY + vbH - targetH * 0.25, baseCy));
  const activeViewBox = compact
    ? geometry.viewBox
    : `${(clampedCx - targetW / 2).toFixed(1)} ${(clampedCy - targetH / 2).toFixed(1)} ${targetW.toFixed(1)} ${targetH.toFixed(1)}`;
  const zoomScale = Math.pow(effectiveZoom, 0.45);

  const applyPreset = (preset) => {
    setRegionId(preset.id);
    setFollowRouteStop(false);
    setZoom(preset.zoom);
    setPan({
      x: (preset.cx - 0.5) * vbW,
      y: (preset.cy - 0.5) * vbH,
    });
  };
  const resetCamera = () => {
    setRegionId('all');
    setFollowRouteStop(false);
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  const onStagePointerDown = (event) => {
    if (compact || effectiveZoom <= 1 || event.target.closest('.atlas-pin, .atlas-stop, .atlas-zoom-bar')) return;
    dragRef.current = { x: event.clientX, y: event.clientY, startPan: { ...pan } };
  };
  const onStagePointerMove = (event) => {
    if (!dragRef.current || !stage) return;
    const rect = stage.getBoundingClientRect();
    const dx = ((event.clientX - dragRef.current.x) / rect.width) * targetW;
    const dy = ((event.clientY - dragRef.current.y) / rect.height) * targetH;
    if (Math.abs(event.clientX - dragRef.current.x) > 3 || Math.abs(event.clientY - dragRef.current.y) > 3) {
      setRegionId('custom');
      setFollowRouteStop(false);
      setPan({ x: dragRef.current.startPan.x - dx, y: dragRef.current.startPan.y - dy });
    }
  };
  const onStagePointerUp = () => { dragRef.current = null; };

  if (compact) {
    return (
      <figure className="atlas atlas-epic compact">
        <div className="atlas-stage">
          <svg viewBox={geometry.viewBox} role="img" aria-label={`${title}: ${epic.entries.length} places pinned on the map of India`} preserveAspectRatio="xMidYMid meet">
            <g className="atlas-base">{outline}</g>
            {epic.entries.map(entry => (
              <circle key={entry.id} cx={entry.x} cy={entry.y} r="12" className={`atlas-pin${entry.outside_india ? ' outside' : ''}`} style={{ '--pin': colourOf(entry) }} />
            ))}
          </svg>
        </div>
      </figure>
    );
  }

  return (
    <figure className="atlas atlas-epic" aria-label={title} onKeyDown={event => { if (event.key === 'Escape' && pin) setPin(null); }}>
      <div className="atlas-stats" aria-label="Epic atlas coverage summary">
        <div><span>Mapped sites</span><strong>{epic.entries.length} places</strong></div>
        <div><span>In current view</span><strong>{visibleEntries.length}</strong></div>
        <div><span>Narrative stops</span><strong>{rstops.length} stages</strong>{battleStopsCount > 0 && <small> · {battleStopsCount} battles</small>}</div>
        <div><span>Route distance</span><strong>{formatInt(totalRouteKm)} km</strong></div>
      </div>
      <div className="atlas-bar">
        <div className="atlas-switch" role="group" aria-label="Choose epic">
          {epics.map(key => (
            <button
              key={key}
              type="button"
              aria-pressed={key === (epics.includes(epicKey) ? epicKey : epics[0])}
              onClick={() => { halt(); setEpicKey(key); setPin(null); setSideFilters([]); setStep(0); setView('kingdoms'); setRouteOn(false); resetCamera(); }}
            >
              {data.epics[key].toggle_label}
            </button>
          ))}
        </div>
        <div className="atlas-view-switch" role="group" aria-label="Atlas view">
          {[['kingdoms', 'Kingdoms'], ['allegiance', 'Allegiance'], ['route', 'Route']].map(([key, label]) => (
            <button
              key={key}
              type="button"
              aria-label={key === 'route' ? 'Trace the route' : label}
              aria-pressed={view === key}
              onClick={() => { halt(); setView(key); setRouteOn(key === 'route'); setStep(0); }}
            >
              {label}
            </button>
          ))}
        </div>
        <label className="atlas-search"><span className="sr-only">Find a place</span>
          <input type="search" placeholder="Find a place…" autoComplete="off" value={query} onChange={event => setQuery(event.target.value)} />
        </label>
      </div>
      {view === 'route' && routeOn && rstop && (
        <div className="atlas-bar atlas-routebar">
          <button type="button" className="atlas-play" aria-label={playing ? 'Pause' : 'Play the route'} onClick={() => { if (playing) halt(); else { if (rstep >= rlast) setStep(0); setPlaying(true); } }}>{playing ? 'Pause' : 'Play'}</button>
          <button type="button" aria-label="Restart route" onClick={() => goStep(0)} disabled={rstep === 0 && !playing}>↺</button>
          <button type="button" aria-label={`Playback speed ${speedMs < 1500 ? '2x' : '1x'}`} onClick={() => setSpeedMs(ms => (ms < 1500 ? 1900 : 1000))}>{speedMs < 1500 ? '2×' : '1×'}</button>
          <button type="button" aria-pressed={followRouteStop} aria-label="Follow route stop" onClick={() => setFollowRouteStop(f => !f)}>◎ Follow</button>
          <input type="range" min="0" max={rlast} value={rstep} aria-label="Route stop" onChange={event => goStep(Number(event.target.value))} />
          <output className="atlas-year" aria-live="polite">Stop {rstep + 1} of {rstops.length} · {rstop.name}</output>
        </div>
      )}
      {view === 'allegiance' && epic.forces?.pandava && <div className="atlas-forces" aria-label="Army strengths: Pandava side 7 akshauhinis and Kaurava side 11 akshauhinis">
        <strong>Kurukshetra forces</strong><div className="atlas-forcebar" role="group" aria-label="Filter by army strength">
          <button type="button" className="atlas-force-pandava" style={{ flexGrow: epic.forces.pandava }} aria-pressed={sideFilters.includes('pandava')} onClick={() => setSideFilters(sideFilters.includes('pandava') ? sideFilters.filter(item => item !== 'pandava') : [...sideFilters, 'pandava'])} aria-label="Filter Pandava side: 7 akshauhinis">Pandava: 7</button>
          <button type="button" className="atlas-force-kaurava" style={{ flexGrow: epic.forces.kaurava }} aria-pressed={sideFilters.includes('kaurava')} onClick={() => setSideFilters(sideFilters.includes('kaurava') ? sideFilters.filter(item => item !== 'kaurava') : [...sideFilters, 'kaurava'])} aria-label="Filter Kaurava side: 11 akshauhinis">Kaurava: 11</button>
        </div><small>One akshauhini per the epic&apos;s stated army totals; individual kingdom contingents are not separately quantified.</small></div>}
      <div className={`atlas-legend${view === 'allegiance' ? ' is-allegiance' : ''}`} role="group" aria-label="Legend and side filters">
        {Object.entries(epic.sides).map(([key, info]) => view === 'allegiance' ? (
          <label key={key} className="atlas-side-filter"><input type="checkbox" checked={!sideFilters.length || sideFilters.includes(key)} onChange={() => setSideFilters(sideFilters.length === 0 ? Object.keys(epic.sides).filter(sideKey => sideKey !== key) : sideFilters.includes(key) ? sideFilters.filter(item => item !== key) : [...sideFilters, key])} />
            <span className={`atlas-dot${key === 'divided' ? ' divided' : ''}`} style={{ background: info.colour }} />{info.label} <b>{epic.entries.filter(entry => entry.side === key).length}</b></label>
        ) : <button key={key} type="button" aria-pressed={sideFilters.length === 1 && sideFilters[0] === key} onClick={() => setSideFilters(sideFilters.length === 1 && sideFilters[0] === key ? [] : [key])}>
            <span className={`atlas-dot${key === 'divided' ? ' divided' : ''}`} style={{ background: info.colour }} />{info.label} <b>{epic.entries.filter(entry => entry.side === key).length}</b>
          </button>)}
        <span className="atlas-hollow"><span className="atlas-dot hollow" />Outside present-day India</span>
      </div>
      <div className="atlas-main">
        <div
          className={`atlas-stage${effectiveZoom > 1 ? ' is-zoomed' : ''}`}
          ref={setStage}
          onPointerDown={onStagePointerDown}
          onPointerMove={onStagePointerMove}
          onPointerUp={onStagePointerUp}
          onPointerLeave={() => { onStagePointerUp(); setTip(null); setHoverStop(null); }}
        >
          <div className="atlas-zoom-bar" role="toolbar" aria-label="Map region and zoom controls">
            <button type="button" aria-label="Zoom in map" onClick={() => { setFollowRouteStop(false); setRegionId('custom'); setZoom(z => Math.min(5, Number((z * 1.45).toFixed(2)))); }}>+</button>
            <button type="button" aria-label="Zoom out map" onClick={() => { setFollowRouteStop(false); setZoom(z => { const nz = Math.max(1, Number((z / 1.45).toFixed(2))); if (nz <= 1.05) { resetCamera(); return 1; } return nz; }); }}>−</button>
            {REGION_PRESETS.map(preset => (
              <button key={preset.id} type="button" aria-pressed={regionId === preset.id && !followRouteStop} onClick={() => applyPreset(preset)}>{preset.label}</button>
            ))}
          </div>
          <svg viewBox={activeViewBox} role="group" aria-label="Map of India with epic places pinned at approximate modern locations" preserveAspectRatio="xMidYMid meet">
            <defs><linearGradient id="epic-divided" x1="0" y1="0" x2="1" y2="1"><stop offset="49%" stopColor="#1e88e5"/><stop offset="51%" stopColor="#c62828"/></linearGradient></defs>
            <g className="atlas-base">{outline}</g>
            <g className="atlas-pins">
              {epic.entries.map(entry => {
                const tipContent = [entry.name, entry.modern_location];
                const on = pin === entry.id;
                const radius = (on ? 17 : 12) / zoomScale;
                return (
                  <circle
                    key={entry.id}
                    cx={entry.x}
                    cy={entry.y}
                    r={radius.toFixed(1)}
                    data-id={entry.id}
                    className={`atlas-pin${entry.outside_india ? ' outside' : ''}${entry.side === 'divided' ? ' is-divided' : ''}${on ? ' is-pinned' : ''}${shown(entry) ? '' : ' is-dim'}`}
                    style={{ '--pin': colourOf(entry), strokeWidth: `${(on ? 4 : 2) / zoomScale}` }}
                    tabIndex={0}
                    role="button"
                    aria-pressed={on}
                    aria-label={`${entry.name}, ${entry.modern_location}`}
                    onPointerMove={event => showTip(event, stage, setTip, tipContent)}
                    onPointerLeave={() => setTip(null)}
                    onFocus={event => showTip(event, stage, setTip, tipContent)}
                    onBlur={() => setTip(null)}
                    onClick={() => select(entry.id)}
                    onKeyDown={event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); select(entry.id); } }}
                  />
                );
              })}
            </g>
            {view === 'route' && routeOn && rstop && (
              <g className="atlas-route">
                <polyline className="atlas-path-ghost" points={rstops.map(s => `${s.x},${s.y}`).join(' ')} style={{ strokeWidth: `${3 / zoomScale}` }} />
                <polyline className="atlas-path" points={rstops.slice(0, rstep + 1).map(s => `${s.x},${s.y}`).join(' ')} style={{ strokeWidth: `${5.5 / zoomScale}` }} />
                {rstops.slice(1, rstep + 1).map((s, idxLeg) => {
                  const prevStop = rstops[idxLeg];
                  const mx = (prevStop.x + s.x) / 2;
                  const my = (prevStop.y + s.y) / 2;
                  const deg = (Math.atan2(s.y - prevStop.y, s.x - prevStop.x) * 180) / Math.PI;
                  const chev = 9 / zoomScale;
                  return (
                    <path
                      key={`arr-${s.id}`}
                      className="atlas-chevron"
                      d={`M${(-chev).toFixed(1)},${(-chev * 0.65).toFixed(1)} L${(chev * 0.65).toFixed(1)},0 L${(-chev).toFixed(1)},${(chev * 0.65).toFixed(1)}`}
                      transform={`translate(${mx.toFixed(1)} ${my.toFixed(1)}) rotate(${deg.toFixed(1)})`}
                      style={{ strokeWidth: `${3 / zoomScale}` }}
                    />
                  );
                })}
                {[...rstops.map((s, i) => ({ s, i }))].sort((a, b) => {
                  const aPri = a.i === rstep ? 2 : a.i === hoverStop ? 1 : 0;
                  const bPri = b.i === rstep ? 2 : b.i === hoverStop ? 1 : 0;
                  return aPri - bPri || a.i - b.i;
                }).map(({ s, i }) => {
                  const isCurrent = i === rstep;
                  const isHovered = i === hoverStop;
                  const stopR = (isCurrent ? 17 : 12.5) / zoomScale;
                  const labelLeft = s.x > clampedCx + targetW * 0.14;
                  return (
                    <g
                      key={s.id}
                      className={`atlas-stop${isCurrent ? ' is-current' : ''}${i > rstep ? ' is-future' : ''}${s.kind === 'battle' ? ' is-battle' : ''}`}
                      data-step={i}
                      transform={`translate(${s.x} ${s.y})`}
                      tabIndex={0}
                      role="button"
                      aria-label={`Route stop ${i + 1}: ${s.name}`}
                      onClick={() => goStep(i)}
                      onKeyDown={event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); goStep(i); } }}
                      onPointerEnter={event => {
                        if (!stage) return;
                        setHoverStop(i);
                        showTip(event, stage, setTip, [`${i + 1}. ${s.name}`, `${s.kind === 'battle' ? 'Battle · ' : ''}${i > 0 ? `+${formatInt(s.leg_km)} km` : 'Origin'}`]);
                      }}
                      onPointerLeave={() => { setHoverStop(null); setTip(null); }}
                    >
                      <circle r={stopR.toFixed(1)} style={{ strokeWidth: `${(isCurrent ? 4 : 2) / zoomScale}` }} />
                      <text y={(5 / zoomScale).toFixed(1)} textAnchor="middle" style={{ fontSize: `${(14 / zoomScale).toFixed(1)}px` }}>{i + 1}</text>
                      {(isCurrent || isHovered) && (
                        <text
                          className="atlas-stop-label"
                          x={((labelLeft ? -20 : 20) / zoomScale).toFixed(1)}
                          y={(4 / zoomScale).toFixed(1)}
                          textAnchor={labelLeft ? 'end' : 'start'}
                          style={{ fontSize: `${(18 / zoomScale).toFixed(1)}px`, strokeWidth: `${(5 / zoomScale).toFixed(1)}px` }}
                        >
                          {s.name}
                        </text>
                      )}
                    </g>
                  );
                })}
              </g>
            )}
          </svg>
          {tip && (<div className="atlas-tip" role="tooltip" style={{ left: tip.left, top: tip.top }}><b>{tip.content[0]}</b><small>{tip.content[1]}</small></div>)}
        </div>
        <aside className="atlas-side">
          <div className="atlas-info-panel">
            <div className="atlas-detail" aria-live="polite">
              {view === 'route' && routeOn && rstop ? (
                <>
                  <h4>{rstep + 1}. {rstop.name} <small>{epic.route.title}</small></h4>
                  <p className="atlas-facts">
                    {rprev ? `${formatInt(rstop.leg_km)} km (straight line) from ${rprev.name}` : 'Where the route begins'}
                    {` · ${formatInt(cumulativeRouteKm)} of ${formatInt(totalRouteKm)} km covered`}
                    {rstop.kind === 'battle' ? ' · ⚔ Battle' : ''}
                  </p>
                  <p>{rstop.note}</p>
                  {rstop.approximate && <p className="atlas-note">Position approximate.</p>}
                  <div className="atlas-route-nav">
                    <button type="button" disabled={rstep === 0} onClick={() => goStep(rstep - 1)}>← Previous stop</button>
                    <button type="button" disabled={rstep === rlast} onClick={() => goStep(rstep + 1)}>Next stop →</button>
                  </div>
                  {rstop.shloka && (
                    <>
                      <ScriptureVerse className="atlas-verse" verse={{ tradition: epic.source_text, lang: 'sa', text: rstop.shloka.sa, english: rstop.shloka.translation, source: rstop.shloka.citation }} />
                      <small className="atlas-edition"><a href={rstop.shloka.verified_from} target="_blank" rel="noreferrer">verified from source</a>{rstop.shloka.generic ? <span className="atlas-generic">General verse of the epic</span> : null}</small>
                    </>
                  )}
                </>
              ) : selected ? (
                <>
                  <h4>{selected.name} <span lang="sa" className="atlas-sa">{selected.name_sa}</span></h4>
                  <p className="atlas-lead"><span className="atlas-dot" style={{ background: colourOf(selected) }} />{epic.sides[selected.side]?.label || selected.side}</p>
                  <dl>
                    <dt>Modern location</dt>
                    <dd>{selected.modern_location}{selected.outside_india ? <em> (outside present-day India: pinned at the nearest map edge)</em> : null}</dd>
                    <dt>{view === 'allegiance' ? 'Ruler / commander' : 'Ruler(s)'}</dt><dd>{selected.ruler}</dd>
                    {view === 'allegiance' && <><dt>Allegiance</dt><dd>{epic.sides[selected.side]?.label || selected.side}</dd><dt>Force size</dt><dd>{selected.akshauhinis || 'Not stated individually'}</dd><dt>Alliance role</dt><dd>{selected.allegiance_role || selected.role}</dd><dt>Allegiance citation</dt><dd>{selected.allegiance_citation || selected.citation}</dd></>}
                    <dt>Role in the epic</dt><dd>{selected.role}</dd>
                    <dt>{epic.location_field === 'kanda' ? 'Kanda' : 'Parva'}</dt><dd>{selected[epic.location_field]}</dd>
                  </dl>
                  <p>{selected.description}</p>
                  {selected.shloka ? (
                    <>
                      <ScriptureVerse className="atlas-verse" verse={{ tradition: epic.source_text, lang: 'sa', text: selected.shloka.sa, english: selected.shloka.translation, source: selected.shloka.citation }} />
                      <small className="atlas-edition"><a href={selected.shloka.verified_from} target="_blank" rel="noreferrer">verified from source</a>{selected.shloka.generic ? <span className="atlas-generic">General verse of the epic</span> : null}{selected.shloka.edition ? ` · ${selected.shloka.edition}` : ''}{selected.shloka.note ? ` · ${selected.shloka.note}` : ''}</small>
                    </>
                  ) : null}
                </>
              ) : (
                <>
                  <h4>{epic.title}</h4>
                  <p>Select any pin or place chip to inspect its ruler, role in the epic, narrative stage and verified Sanskrit verse, or click <strong>Trace the route</strong> to step through all {rstops.length} plot points.</p>
                </>
              )}
            </div>
            {view === 'route' && routeOn ? (
              <>
                <h5 className="atlas-places-heading">Chronological route stops ({rstops.length})</h5>
                <ul className="atlas-places atlas-route-list">
                  {rstops.map((s, i) => (
                    <li key={s.id}>
                      <button type="button" className={i === rstep ? 'is-current' : ''} aria-pressed={i === rstep} onClick={() => goStep(i)}>
                        <span className="atlas-step-num">{i + 1}</span>
                        <span>{s.name}{s.kind === 'battle' ? ' ⚔' : ''}</span>
                        <small>{i > 0 ? `+${formatInt(s.leg_km)} km` : 'Start'}</small>
                      </button>
                    </li>
                  ))}
                </ul>
              </>
            ) : (
              <>
                <h5 className="atlas-places-heading">Places in this view ({visibleEntries.length} of {epic.entries.length})</h5>
                <ul className="atlas-places">
                  {visibleEntries.map(entry => (
                    <li key={entry.id}><button type="button" aria-pressed={pin === entry.id} onClick={() => select(entry.id)}><span className="atlas-dot" style={{ background: colourOf(entry) }} />{entry.name}</button></li>
                  ))}
                </ul>
              </>
            )}
          </div>
        </aside>
      </div>
      <p className="atlas-note">{epic.edition_note}</p>
      <details className="atlas-method"><summary>Methodology</summary><ul>{(data.meta.methodology || []).map(line => <li key={line}>{line}</li>)}</ul></details>
    </figure>
  );
}
