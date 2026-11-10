import { useEffect, useMemo, useState } from 'react';
import ScriptureVerse from './ScriptureVerse.jsx';
import './Atlas.css';
import { formatInt } from './atlasData.js';

// Mirrors docs/state-elections.js: keep markup and class names in sync.
const BASE = '/data/state-elections/';
const HOUSES = { GE: 'Lok Sabha', AE: 'Vidhan Sabha (Assembly)' };
const cache = {};
const getJSON = url => (cache[url] = cache[url] || fetch(url).then(r => {
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}).catch(err => { delete cache[url]; throw err; }));
const slugOf = name => String(name).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

export function readStateHash() {
  const params = new URLSearchParams(String(window.location.hash || '').replace(/^#/, ''));
  const house = params.get('house');
  return { state: params.get('state') || '', house: house === 'AE' ? 'AE' : 'GE', year: params.get('year') || '' };
}

function writeHash(value) {
  const params = new URLSearchParams(String(window.location.hash || '').replace(/^#/, ''));
  ['state', 'house', 'year'].forEach(key => params.delete(key));
  if (value) { params.set('state', value.state); params.set('house', value.house); if (value.year) params.set('year', value.year); }
  const text = params.toString();
  window.history.replaceState(null, '', `${window.location.pathname}${window.location.search}${text ? `#${text}` : ''}`);
}

function lokHouse(atlas, state) {
  const records = atlas.states[state] || {};
  const labels = Object.fromEntries(atlas.years.map(item => [String(item.year), item.label]));
  const years = Object.keys(records).sort((a, b) => a - b).map(id => ({ id, year: Number(id), label: labels[id] || id, ...records[id] }));
  return {
    house: 'GE', name: `${state} Lok Sabha seats`, years, lists: Object.fromEntries(years.map(item => [item.id, item.list || []])), parties: atlas.parties,
    note: years.some(item => item.from) ? 'Some earlier seats were mapped from older states (see the atlas methodology).' : '',
    sources: atlas.meta.sources || [], methodology: atlas.meta.methodology || [],
  };
}

function assemblyHouse(file, index) {
  return {
    house: 'AE', name: file.house_name, years: file.years, lists: Object.fromEntries(Object.entries(file.elections).map(([id, item]) => [id, item.list])),
    parties: file.parties, note: file.note, sources: file.sources, methodology: index?.meta?.methodology || [], seatsNow: file.seats_now,
  };
}

function LineChart({ house, colour }) {
  const years = house.years;
  const peak = {};
  years.forEach(item => Object.entries(item.vote_share || {}).forEach(([code, share]) => { peak[code] = Math.max(peak[code] || 0, share); }));
  const counts = Object.fromEntries(Object.keys(peak).map(code => [code, years.filter(item => item.vote_share?.[code] != null).length]));
  const codes = Object.keys(peak).filter(code => counts[code] >= 2 && code !== 'IND' && code !== 'OTH').sort((a, b) => peak[b] - peak[a]).slice(0, 6);
  if (years.length < 2 || !codes.length) return null;
  const W = 640; const H = 230; const L = 38; const R = 10; const T = 10; const B = 26;
  const top = Math.max(10, Math.ceil(Math.max(...codes.map(code => peak[code])) / 10) * 10);
  const x = i => L + (i / (years.length - 1)) * (W - L - R);
  const y = value => T + (1 - value / top) * (H - T - B);
  const step = Math.ceil(years.length / 7);
  const summary = codes.map(code => { const last = [...years].reverse().find(item => item.vote_share?.[code] != null); return `${code} ${last.vote_share[code]}% in ${last.label}`; }).join(', ');
  return (
    <figure className="sv-lines">
      <figcaption>Vote share by party (% of votes polled)</figcaption>
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`Vote share lines. Latest: ${summary}`}>
        {[0, 1, 2, 3, 4].map(k => { const value = (top / 4) * k; return (<g key={k}><line x1={L} x2={W - R} y1={y(value)} y2={y(value)} className="sv-grid" /><text x={L - 5} y={y(value) + 4} textAnchor="end">{Math.round(value)}%</text></g>); })}
        {years.map((item, i) => (i % step === 0 || i === years.length - 1 ? <text key={item.id} x={x(i)} y={H - 8} textAnchor="middle">{item.label}</text> : null))}
        {codes.map(code => {
          const points = years.map((item, i) => (item.vote_share?.[code] != null ? { i, value: item.vote_share[code], label: item.label } : null)).filter(Boolean);
          const segments = []; let run = [];
          points.forEach(point => { if (run.length && point.i !== run[run.length - 1].i + 1) { segments.push(run); run = []; } run.push(point); });
          if (run.length) segments.push(run);
          return (
            <g key={code} style={{ color: colour(code) }}>
              {segments.map((seg, n) => <polyline key={n} points={seg.map(p => `${x(p.i).toFixed(1)},${y(p.value).toFixed(1)}`).join(' ')} className="sv-line" />)}
              {points.map(p => <circle key={p.i} cx={x(p.i).toFixed(1)} cy={y(p.value).toFixed(1)} r="3"><title>{`${code} ${p.label}: ${p.value}%`}</title></circle>)}
            </g>
          );
        })}
      </svg>
      <ul className="sv-legend">{codes.map(code => <li key={code}><span className="atlas-dot" style={{ background: colour(code) }} />{code}</li>)}</ul>
    </figure>
  );
}

function Panel({ house, yearId, q, party, setYear, setQ, setParty }) {
  const years = house.years;
  const colour = code => house.parties[code]?.colour || '#8d8d8d';
  const id = house.years.some(item => item.id === yearId) ? yearId : house.years[house.years.length - 1].id;
  const yearIndex = house.years.findIndex(entry => entry.id === id);
  const item = house.years.find(entry => entry.id === id);
  const list = house.lists[id] || [];
  const first = house.years[0]; const last = house.years[house.years.length - 1];
  const majority = Math.floor(item.total / 2) + 1;
  const shares = Object.entries(item.vote_share || {}).slice(0, 6).map(([code, share]) => `${code} ${share}%`).join(' · ');
  const needle = q.trim().toLowerCase();
  const shown = list.filter(row => (!party || row[2] === party) && (!needle || `${row[0]} ${row[1]} ${row[2]}`.toLowerCase().includes(needle)));
  const seatEntries = Object.entries(item.seats).sort((a, b) => b[1] - a[1]);
  const strip = [...list].sort((a, b) => (item.seats[b[2]] - item.seats[a[2]]) || String(a[2]).localeCompare(b[2]) || a[0].localeCompare(b[0]));
  return (
    <>
      <p className="sv-meta">{house.name} · {house.years.length} elections, {first.label}–{last.label}{house.seatsNow ? ` · ${house.seatsNow} seats today` : ''}</p>
      {house.note && <p className="sv-note">{house.note}</p>}
      <label className="sv-year-slider"><span>Election year</span><input type="range" min="0" max={years.length - 1} step="1" value={yearIndex} aria-label="Election year" aria-valuetext={item.label} disabled={years.length < 2} onChange={event => setYear(years[Number(event.target.value)].id)} /><output aria-live="polite">{item.label}</output></label>
      <ol className="sv-timeline" aria-label="Elections, oldest first. Choose one to see its seat-by-seat results">
        {house.years.map(entry => {
          const label = `${entry.label}: ${entry.lead} won the most seats, ${entry.seats[entry.lead]} of ${entry.total}${entry.turnout != null ? `; turnout ${entry.turnout}%` : ''}`;
          return (
            <li key={entry.id}>
              <button type="button" className="sv-row" data-id={entry.id} aria-pressed={entry.id === id} aria-label={label} onClick={() => setYear(entry.id)}>
                <span className="sv-yr">{entry.label}</span>
                <span className="sv-bar" aria-hidden="true">{Object.entries(entry.seats).map(([code, count]) => <i key={code} style={{ width: `${count / entry.total * 100}%`, background: colour(code) }} title={`${code} ${count}`} />)}</span>
                <span className="sv-lead"><span className="atlas-dot" style={{ background: colour(entry.lead) }} />{entry.lead} {entry.seats[entry.lead]}/{entry.total}</span>
                <span className="sv-turn">{entry.turnout != null ? `${entry.turnout}%` : '—'}</span>
              </button>
            </li>
          );
        })}
      </ol>
      <LineChart house={house} colour={colour} />
      <div className="sv-year" aria-live="polite">
        <h4>{item.label} election <small>{item.total} seats</small></h4>
        <p className="atlas-lead"><span className="atlas-dot" style={{ background: colour(item.lead) }} />Most seats: <b>{house.parties[item.lead]?.name || item.lead}</b> ({item.seats[item.lead]} of {item.total}{item.seats[item.lead] >= majority ? ', a majority' : `; majority is ${majority}`})</p>
        <p className="atlas-facts">{item.turnout != null ? `Turnout ${item.turnout}%. ` : ''}{shares ? `Vote share: ${shares}.` : ''}</p>
        <div className="sv-strip" role="img" aria-label={`Seat strip, one tile per seat: ${seatEntries.slice(0, 6).map(([code, count]) => `${code} ${count}`).join(', ')}`}>
          {strip.map((row, n) => <i key={n} style={{ background: colour(row[2]) }} title={`${row[0]}: ${row[1]} (${row[2]})`} />)}
        </div>
        <ul className="sv-tally" aria-label="Seats by party; choose a party to filter the list">
          {seatEntries.map(([code, count]) => (
            <li key={code}><button type="button" className="sv-party" data-party={code} aria-pressed={party === code} onClick={() => setParty(party === code ? '' : code)}>
              <span className="atlas-dot" style={{ background: colour(code) }} /><b>{code}</b> {count}<span className="atlas-meter"><i style={{ width: `${count / item.total * 100}%`, background: colour(code) }} /></span>
            </button></li>
          ))}
        </ul>
        <label className="sv-search"><span className="sr-only">Filter constituencies</span><input type="search" placeholder="Filter constituency, winner or party…" value={q} autoComplete="off" onChange={event => setQ(event.target.value)} /></label>
        <div className="atlas-tablewrap sv-table">
          <table>
            <caption>Seat-by-seat winners, {item.label}</caption>
            <thead><tr><th>Constituency</th><th>Winner</th><th>Party</th><th className="num">Margin</th></tr></thead>
            <tbody>
              {shown.length ? shown.map(([constituency, winner, code, margin], n) => (
                <tr key={`${constituency}-${n}`}><td>{constituency}</td><td>{winner}</td><td><span className="atlas-dot" style={{ background: colour(code) }} />{code}</td><td className="num">{margin ? formatInt(margin) : '—'}</td></tr>
              )) : <tr><td colSpan="4">No matching seats.</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
      <details className="atlas-method sv-sources">
        <summary>Sources and method</summary>
        <ul>{house.sources.map(source => <li key={source.url || source.name}><a href={source.url} target="_blank" rel="noreferrer">{source.name}</a>{source.licence ? <small> {source.licence}</small> : null}</li>)}</ul>
        <ul>{house.methodology.map(line => <li key={line}>{line}</li>)}</ul>
      </details>
    </>
  );
}

export default function StateElections({ atlas, states, initial, onClose, includeVerse = true, showTitle = true }) {
  const [name, setName] = useState(initial.state);
  const [houseKey, setHouseKey] = useState(initial.house || 'GE');
  const [yearId, setYear] = useState(initial.year || '');
  const [q, setQ] = useState('');
  const [party, setParty] = useState('');
  const [assembly, setAssembly] = useState(undefined);

  useEffect(() => {
    if (houseKey !== 'AE') return undefined;
    let cancelled = false;
    setAssembly(undefined);
    (async () => {
      try {
        const index = await getJSON(`${BASE}index.json`).catch(() => null);
        if (index && !index.states[name]) { if (!cancelled) setAssembly({ none: index.no_assembly?.[name] || '' }); return; }
        const file = await getJSON(`${BASE}${slugOf(name)}.json`);
        if (!cancelled) setAssembly(assemblyHouse(file, index));
      } catch (err) { if (!cancelled) setAssembly({ error: err.message }); }
    })();
    return () => { cancelled = true; };
  }, [name, houseKey]);

  const house = useMemo(() => (houseKey === 'GE' ? lokHouse(atlas, name) : assembly), [atlas, name, houseKey, assembly]);
  const resolvedYear = house?.years?.length ? (house.years.some(item => item.id === yearId) ? yearId : house.years[house.years.length - 1].id) : '';

  useEffect(() => { writeHash({ state: name, house: houseKey, year: resolvedYear }); }, [name, houseKey, resolvedYear]);

  useEffect(() => {
    const onHash = () => {
      const next = readStateHash();
      if (!next.state) return;
      setName(prev => (states.includes(next.state) ? next.state : prev));
      setHouseKey(next.house);
      setYear(next.year);
    };
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, [states]);

  const close = () => { writeHash(null); onClose(name); };
  const reset = () => { setYear(''); setQ(''); setParty(''); };
  const switchHouse = key => { setHouseKey(key); reset(); };

  let body;
  if (house === undefined) body = <p className="atlas-status">Loading…</p>;
  else if (house.none !== undefined) body = <p className="atlas-status">{house.none ? `${name}: ${house.none}` : `No Vidhan Sabha election data is available for ${name}.`}</p>;
  else if (house.error) body = <p className="atlas-status">Could not load {name} ({house.error}).</p>;
  else if (!house.years.length) body = <p className="atlas-status">{name} has no {HOUSES[houseKey]} seats in this dataset.</p>;
  else body = <Panel house={house} yearId={yearId} q={q} party={party} setYear={id => { setYear(id); setQ(''); setParty(''); }} setQ={setQ} setParty={setParty} />;

  return (
    <section className="sv" onKeyDown={event => {
      if (event.key === 'Escape') { event.stopPropagation(); close(); return; }
      if (event.target.closest?.('[role="tab"]') && (event.key === 'ArrowLeft' || event.key === 'ArrowRight')) { event.preventDefault(); switchHouse(houseKey === 'GE' ? 'AE' : 'GE'); }
    }}>
      <div className="sv-head">
        <button type="button" className="sv-back" onClick={close}>← All India map</button>
        <label className="sv-picker">State <select aria-label="State or UT" value={name} onChange={event => { setName(event.target.value); reset(); }}>
          {states.map(option => <option key={option}>{option}</option>)}
        </select></label>
      </div>
      {showTitle && <h3 className="sv-title">How {name} voted</h3>}
      <div className="sv-tabs" role="tablist" aria-label="Legislature">
        {Object.entries(HOUSES).map(([key, label]) => (
          <button key={key} type="button" role="tab" id={`sv-tab-${key}`} aria-selected={houseKey === key} aria-controls="sv-panel" tabIndex={houseKey === key ? 0 : -1} data-house={key} onClick={() => switchHouse(key)}>{label}</button>
        ))}
      </div>
      <div id="sv-panel" role="tabpanel" aria-labelledby={`sv-tab-${houseKey}`} className="sv-panel">{body}</div>
      {includeVerse && <ScriptureVerse verseKey={`state-elections:${name}`} group="India in Maps" className="compact" />}
    </section>
  );
}
