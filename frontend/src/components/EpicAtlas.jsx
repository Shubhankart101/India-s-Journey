import { useEffect, useState } from 'react';
import { loadAtlas, showTip } from './atlasData.js';
import ScriptureVerse from './ScriptureVerse.jsx';
import './Atlas.css';

const DATA_URL = '/data/epic-kingdoms.json';

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
  const [playing, setPlaying] = useState(false);

  useEffect(() => {
    if (!playing) return undefined;
    const timer = setInterval(() => setStep(s => s + 1), 1900);
    return () => clearInterval(timer);
  }, [playing]);
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
  useEffect(() => { if (playing && step >= rlast) { setPlaying(false); setStep(rlast); } }, [playing, step, rlast]);

  if (error) return <p className="atlas-status">The atlas could not be loaded ({error}).</p>;
  if (!loaded) return <p className="atlas-status">Loading the epic atlas…</p>;

  const colourOf = entry => epic.sides[entry.side]?.colour || '#8d8d8d';
  const matches = entry => !query || `${entry.name} ${entry.name_sa} ${entry.modern_location}`.toLowerCase().includes(query.toLowerCase());
  const shown = entry => matches(entry) && (!sideFilters.length || sideFilters.includes(entry.side));
  const selected = epic.entries.find(entry => entry.id === pin);
  const select = id => setPin(pin === id ? null : id);
  const rstep = Math.min(step, rlast);
  const rstop = rstops[rstep];
  const rprev = rstops[rstep - 1];
  const halt = () => setPlaying(false);
  const goStep = index => { halt(); setStep(index); };
  const outline = Object.entries(geometry.states).map(([name, d]) => <path key={name} d={d} className="atlas-outline" />);

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
      <div className="atlas-bar">
        <div className="atlas-switch" role="group" aria-label="Choose epic">
          {epics.map(key => (
            <button key={key} type="button" aria-pressed={key === (epics.includes(epicKey) ? epicKey : epics[0])} onClick={() => { halt(); setEpicKey(key); setPin(null); setSideFilters([]); setStep(0); setView('kingdoms'); setRouteOn(false); }}>{data.epics[key].toggle_label}</button>
          ))}
        </div>
        <div className="atlas-view-switch" role="group" aria-label="Atlas view">
          {[['kingdoms', 'Kingdoms'], ['allegiance', 'Allegiance'], ['route', 'Route']].map(([key, label]) => (
            <button key={key} type="button" aria-label={key === 'route' ? 'Trace the route' : label} aria-pressed={view === key} onClick={() => { halt(); setView(key); setRouteOn(key === 'route'); setStep(0); }}>{label}</button>
          ))}
        </div>
        <label className="atlas-search"><span className="sr-only">Find a place</span>
          <input type="search" placeholder={`Find a place\u2026`} autoComplete="off" value={query} onChange={event => setQuery(event.target.value)} />
        </label>
      </div>
      {view === 'route' && routeOn && rstop && (
        <div className="atlas-bar atlas-routebar">
          <button type="button" className="atlas-play" aria-label={playing ? 'Pause' : 'Play the route'} onClick={() => { if (playing) halt(); else { if (rstep >= rlast) setStep(0); setPlaying(true); } }}>{playing ? 'Pause' : 'Play'}</button>
          <input type="range" min="0" max={rlast} value={rstep} aria-label="Route stop" onChange={event => goStep(Number(event.target.value))} />
          <output className="atlas-year" aria-live="polite">Stop {rstep + 1} of {rstops.length} {'\u00b7'} {rstop.name}</output>
        </div>
      )}
      {view === 'allegiance' && epic.forces?.pandava && <div className="atlas-forces" aria-label="Army strengths: Pandava side 7 akshauhinis and Kaurava side 11 akshauhinis">
        <strong>Kurukshetra forces</strong><div className="atlas-forcebar" role="group" aria-label="Filter by army strength">
          <button type="button" className="atlas-force-pandava" style={{ flexGrow: epic.forces.pandava }} aria-pressed={sideFilters.includes('pandava')} onClick={() => setSideFilters(sideFilters.includes('pandava') ? sideFilters.filter(item => item !== 'pandava') : [...sideFilters, 'pandava'])} aria-label="Filter Pandava side: 7 akshauhinis">Pandava: 7</button>
          <button type="button" className="atlas-force-kaurava" style={{ flexGrow: epic.forces.kaurava }} aria-pressed={sideFilters.includes('kaurava')} onClick={() => setSideFilters(sideFilters.includes('kaurava') ? sideFilters.filter(item => item !== 'kaurava') : [...sideFilters, 'kaurava'])} aria-label="Filter Kaurava side: 11 akshauhinis">Kaurava: 11</button>
        </div><small>One akshauhini per the epic's stated army totals; individual kingdom contingents are not separately quantified.</small></div>}
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
        <div className="atlas-stage" ref={setStage}>
          <svg viewBox={geometry.viewBox} role="group" aria-label="Map of India with epic places pinned at approximate modern locations" preserveAspectRatio="xMidYMid meet">
            <defs><linearGradient id="epic-divided" x1="0" y1="0" x2="1" y2="1"><stop offset="49%" stopColor="#1e88e5"/><stop offset="51%" stopColor="#c62828"/></linearGradient></defs>
            <g className="atlas-base">{outline}</g>
            <g className="atlas-pins">
              {epic.entries.map(entry => {
                const tipContent = [entry.name, entry.modern_location];
                const on = pin === entry.id;
                return (
                  <circle
                    key={entry.id}
                    cx={entry.x}
                    cy={entry.y}
                    r={on ? 17 : 12}
                    data-id={entry.id}
                    className={`atlas-pin${entry.outside_india ? ' outside' : ''}${entry.side === 'divided' ? ' is-divided' : ''}${on ? ' is-pinned' : ''}${shown(entry) ? '' : ' is-dim'}`}
                    style={{ '--pin': colourOf(entry) }}
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
                <polyline className="atlas-path-ghost" points={rstops.map(s => `${s.x},${s.y}`).join(' ')} />
                <polyline className="atlas-path" points={rstops.slice(0, rstep + 1).map(s => `${s.x},${s.y}`).join(' ')} />
                {rstops.map((s, i) => (
                  <g key={s.id} className={`atlas-stop${i === rstep ? ' is-current' : ''}${i > rstep ? ' is-future' : ''}`} data-step={i} transform={`translate(${s.x} ${s.y})`} tabIndex={0} role="button" aria-label={`Route stop ${i + 1}: ${s.name}`}
                    onClick={() => goStep(i)} onKeyDown={event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); goStep(i); } }}>
                    <circle r={i === rstep ? 17 : 13} /><text y="5" textAnchor="middle">{i + 1}</text>
                  </g>
                ))}
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
                <p className="atlas-facts">{rprev ? `${Number(rstop.leg_km).toLocaleString('en-IN')} km (straight line) from ${rprev.name}` : 'Where the route begins'}</p>
                <p>{rstop.note}</p>
                {rstop.approximate && <p className="atlas-note">Position approximate.</p>}
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
                    <small className="atlas-edition"><a href={selected.shloka.verified_from} target="_blank" rel="noreferrer">verified from source</a>                    {selected.shloka.generic ? <span className="atlas-generic">General verse of the epic</span> : null}{selected.shloka.edition ? ` · ${selected.shloka.edition}` : ''}{selected.shloka.note ? ` · ${selected.shloka.note}` : ''}</small>
                  </>
                                    ) : null}
              </>
            ) : (<><h4>{epic.title}</h4><p>Select a pin or a name to see the ruler, role in the epic, a short description and the Sanskrit verse.</p></>)}
          </div>
          <h5 className="atlas-places-heading">Places in this view</h5>
          <ul className="atlas-places">
            {epic.entries.filter(shown).map(entry => (
              <li key={entry.id}><button type="button" aria-pressed={pin === entry.id} onClick={() => select(entry.id)}><span className="atlas-dot" style={{ background: colourOf(entry) }} />{entry.name}</button></li>
            ))}
          </ul>
          </div>
        </aside>
      </div>
      <p className="atlas-note">{epic.edition_note}</p>
      <details className="atlas-method"><summary>Methodology</summary><ul>{(data.meta.methodology || []).map(line => <li key={line}>{line}</li>)}</ul></details>
    </figure>
  );
}
