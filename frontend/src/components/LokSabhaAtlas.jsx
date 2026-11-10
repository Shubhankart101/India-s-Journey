import { useEffect, useMemo, useRef, useState } from 'react';
import { formatInt, loadAtlas, showTip } from './atlasData.js';
import StateElections, { readStateHash } from './StateElections.jsx';
import './Atlas.css';

const DATA_URL = import.meta.env.BASE_URL + 'data/lok-sabha-atlas.json';

export default function LokSabhaAtlas({ compact = false, title = 'Lok Sabha elections by state' }) {
  const [loaded, setLoaded] = useState(null);
  const [error, setError] = useState('');
  const [yi, setYi] = useState(null);
  const [pin, setPin] = useState(null);
  const [party, setParty] = useState(null);
  const [playing, setPlaying] = useState(false);
  const [tip, setTip] = useState(null);
  const [view, setView] = useState(() => {
    if (compact) return null;
    const hash = readStateHash();
    return hash.state ? hash : null;
  });
  const stageRef = useRef(null);

  useEffect(() => {
    let cancelled = false;
    loadAtlas(DATA_URL).then(([data, geometry]) => { if (!cancelled) setLoaded({ data, geometry }); }, err => { if (!cancelled) setError(err.message); });
    return () => { cancelled = true; };
  }, []);

  const years = loaded?.data.years || [];
  const index = yi === null ? years.length - 1 : Math.min(yi, years.length - 1);

  useEffect(() => {
    if (!playing) return undefined;
    const timer = setInterval(() => {
      setYi(value => {
        const next = (value === null ? years.length - 1 : value) + 1;
        if (next >= years.length) { setPlaying(false); return years.length - 1; }
        return next;
      });
    }, 1200);
    return () => clearInterval(timer);
  }, [playing, years.length]);

  const national = useMemo(() => {
    const year = years[index];
    if (!year) return [];
    return Object.entries(year.national).sort((a, b) => b[1] - a[1]);
  }, [years, index]);

  if (error) return <p className="atlas-status">The atlas could not be loaded ({error}).</p>;
  if (!loaded) return <p className="atlas-status">Loading the Lok Sabha atlas…</p>;

  const { data, geometry } = loaded;
  const year = years[index];
  const colourOf = code => data.parties[code]?.colour || '#8d8d8d';
  const nameOf = code => data.parties[code]?.name || code;
  const recordOf = name => data.states[name]?.[String(year.year)];
  const names = Object.keys(geometry.states);
  const total = national.reduce((sum, [, count]) => sum + count, 0) || 1;
  const toggle = name => { if (recordOf(name)) setPin(pin === name ? null : name); };

  const paths = names.map(name => {
    const rec = recordOf(name);
    const classes = [rec ? '' : 'no-value', party && rec?.lead !== party ? 'is-dim' : '', pin === name ? 'is-pinned' : ''].filter(Boolean).join(' ');
    const label = rec ? `${name}, ${year.label}: ${nameOf(rec.lead)} won most seats, ${rec.seats[rec.lead]} of ${rec.total}` : `${name}, ${year.label}: no seats`;
    const tipContent = rec ? [name, `${year.label} · ${nameOf(rec.lead)} ${rec.seats[rec.lead]} of ${rec.total} seats`] : [name, `No seats in ${year.label}`];
    return (
      <path
        key={name}
        d={geometry.states[name]}
        data-state={name}
        className={classes}
        style={{ fill: rec ? colourOf(rec.lead) : 'var(--map-empty)' }}
        tabIndex={compact ? -1 : 0}
        role={compact ? undefined : 'button'}
        aria-pressed={compact ? undefined : pin === name}
        aria-label={compact ? undefined : label}
        onPointerMove={compact ? undefined : event => showTip(event, stageRef.current, setTip, tipContent)}
        onPointerLeave={compact ? undefined : () => setTip(null)}
        onFocus={compact ? undefined : event => showTip(event, stageRef.current, setTip, tipContent)}
        onBlur={compact ? undefined : () => setTip(null)}
        onClick={compact ? undefined : () => toggle(name)}
        onKeyDown={compact ? undefined : event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); toggle(name); } }}
      />
    );
  });

  if (compact) {
    return (
      <figure className="atlas atlas-ls compact">
        <div className="atlas-stage">
          <svg viewBox={geometry.viewBox} role="img" aria-label={`${title}: ${year.label} winners by State/UT`} preserveAspectRatio="xMidYMid meet">{paths}</svg>
        </div>
      </figure>
    );
  }

  const pinned = pin ? recordOf(pin) : null;
  const detail = pin && pinned ? (
    <>
      <h4>{pin} <small>{year.label}</small></h4>
      <p className="atlas-lead"><span className="atlas-dot" style={{ background: colourOf(pinned.lead) }} />Most seats: <b>{nameOf(pinned.lead)}</b> ({pinned.seats[pinned.lead]} of {pinned.total})</p>
      <ul className="atlas-seatlist">
        {Object.entries(pinned.seats).sort((a, b) => b[1] - a[1]).map(([code, count]) => (
          <li key={code}><span className="atlas-dot" style={{ background: colourOf(code) }} /><span><b>{code}</b> {count}</span>
            <span className="atlas-meter"><i style={{ width: `${(count / pinned.total) * 100}%`, background: colourOf(code) }} /></span></li>
        ))}
      </ul>
      <p className="atlas-facts">
        {pinned.turnout != null ? `Turnout ${pinned.turnout}%. ` : ''}
        {pinned.vote_share ? `Vote share: ${Object.entries(pinned.vote_share).slice(0, 5).map(([code, share]) => `${code} ${share}%`).join(' · ')}.` : ''}
        {pinned.from ? ` Includes seats mapped from ${pinned.from}.` : ''}
      </p>
      <div className="atlas-tablewrap">
        <table>
          <caption>Seat-by-seat winners, {year.label}</caption>
          <thead><tr><th>Constituency</th><th>Winner</th><th>Party</th><th className="num">Margin</th></tr></thead>
          <tbody>
            {(pinned.list || []).map(([constituency, winner, code, margin], row) => (
              <tr key={`${constituency}-${row}`}><td>{constituency}</td><td>{winner}</td><td><span className="atlas-dot" style={{ background: colourOf(code) }} />{code}</td><td className="num">{margin ? formatInt(margin) : '—'}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
      <p><button type="button" className="sv-open" onClick={() => setView({ state: pin, house: 'GE', year: String(year.year) })}>How {pin} voted: every election →</button></p>
    </>
  ) : pin ? (
    <><h4>{pin}</h4><p>No Lok Sabha seat in this State/UT in {year.label}.</p></>
  ) : (
    <><h4>{year.label} general election</h4><p>{year.note || 'Select a State or UT on the map to see seats won by each party and the seat-by-seat winners.'}</p></>
  );

  const step = delta => { setPlaying(false); setYi(Math.min(years.length - 1, Math.max(0, index + delta))); };

  return (
    <figure
      className={`atlas atlas-ls${view ? ' is-state-view' : ''}`}
      aria-label={title}
      onKeyDown={event => {
        if (event.key === 'Escape' && pin && !view) setPin(null);
        if (event.altKey && event.key === 'ArrowLeft') step(-1);
        if (event.altKey && event.key === 'ArrowRight') step(1);
      }}
    >
      <div className="atlas-bar">
        <button type="button" className="atlas-play" aria-label={playing ? 'Pause' : 'Play through elections'} onClick={() => { if (!playing && index >= years.length - 1) setYi(0); setPlaying(!playing); }}>{playing ? '❚❚' : '▶'}</button>
        <input type="range" min="0" max={years.length - 1} step="1" value={index} aria-label="Election year" aria-valuetext={year.label} onChange={event => { setPlaying(false); setYi(Number(event.target.value)); }} />
        <output className="atlas-year" aria-live="polite">{year.label} · {formatInt(year.seats_counted)} seats counted</output>
      </div>
      <div className="atlas-main">
        <div className="atlas-stage" ref={stageRef}>
          <svg viewBox={geometry.viewBox} role="group" aria-label="Map of India: each State or UT shaded by the party that won most Lok Sabha seats. Tab to a State or UT and press Enter for seat-by-seat winners." preserveAspectRatio="xMidYMid meet">{paths}</svg>
          {tip && (<div className="atlas-tip" role="tooltip" style={{ left: tip.left, top: tip.top }}><b>{tip.content[0]}</b><small>{tip.content[1]}</small></div>)}
        </div>
        <aside className="atlas-side"><div className="atlas-detail" aria-live="polite">{detail}</div></aside>
      </div>
      <div className="atlas-tally">
        <div className="atlas-tally-bar" role="img" aria-label={`National seats ${year.label}: ${national.slice(0, 6).map(([code, count]) => `${code} ${count}`).join(', ')}`}>
          {national.map(([code, count]) => (<i key={code} style={{ width: `${(count / total) * 100}%`, background: colourOf(code) }} title={`${nameOf(code)}: ${count}`} />))}
        </div>
        <div className="atlas-legend" role="group" aria-label="Party legend: choose a party to highlight the States it leads">
          {national.map(([code, count]) => (
            <button key={code} type="button" aria-pressed={party === code} onClick={() => setParty(party === code ? null : code)}>
              <span className="atlas-dot" style={{ background: colourOf(code) }} />{code} <b>{count}</b>
            </button>
          ))}
        </div>
      </div>
      <details className="atlas-method">
        <summary>Methodology and coverage</summary>
        <ul>{(data.meta.methodology || []).map(line => <li key={line}>{line}</li>)}</ul>
        <p>Years available: {(data.meta.years_available || []).join(', ')}.{data.meta.missing_years?.length ? ` Not available: ${data.meta.missing_years.join(', ')}.` : ''}</p>
      </details>
      {view && (
        <StateElections
          atlas={data}
          states={Object.keys(data.states).sort()}
          initial={view}
          onClose={closed => { if (recordOf(closed)) setPin(closed); setView(null); }}
        />
      )}
    </figure>
  );
}
