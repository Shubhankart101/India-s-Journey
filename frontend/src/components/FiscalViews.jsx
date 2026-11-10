import { useEffect, useMemo, useState } from 'react';
import DATA from '../data/fiscal-views.json';
import './FiscalViews.css';

const grp = new Intl.NumberFormat('en-IN');
const lakhCrore = value => `₹${(value / 1e5).toFixed(2)} lakh cr`;
const crore = value => `₹${grp.format(Math.round(value))} crore`;
export const slug = name => name.toLowerCase().replace(/&/g, 'and').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const NODE_W = 14;

const S = DATA.states;
const FUNCS = DATA.functions;
const UB = DATA.union_budget;
const metricByKey = Object.fromEntries(S.metrics.map(m => [m.key, m]));
const MATRIX_KEYS = ['gfd_gsdp', 'rd_gsdp', 'debt_gsdp', 'interest_rr', 'own_tax_rr', 'transfers_rr', 'committed_rr', 'capex_gsdp', 'gsdp_growth', 'gsdp', 'pcnsdp'];
const metricValue = (key, state, year) => S.values[key]?.[state]?.[year] ?? null;
const stateList = S.states.filter(state => state !== 'All States & UTs');
const YEARS = S.years.filter(year => MATRIX_KEYS.some(key => S.states.some(state => metricValue(key, state, year) !== null))).slice().reverse();
const DEFAULT_YEAR = YEARS.includes('2023-24') ? '2023-24' : YEARS[0];
const FUNC_YEARS = Object.keys(FUNCS.values);

export function fmtMetric(key, value) {
  if (value === null || value === undefined) return '–';
  if (key === 'pcnsdp') return `₹${grp.format(Math.round(value))}`;
  if (key === 'gsdp') return value.toFixed(2);
  return value.toFixed(1);
}

export function cellColour(value, min, max, better) {
  if (value === null || value === undefined || max === min) return 'transparent';
  if (better === null || better === undefined) return `rgba(88,166,255,${(0.08 + 0.5 * (value - min) / (max - min)).toFixed(2)})`;
  let t = (value - min) / (max - min);
  if (better === 'high') t = 1 - t;
  return `hsla(${(130 - 130 * t).toFixed(0)},62%,46%,${(0.22 + 0.3 * Math.abs(t - 0.5) * 2).toFixed(2)})`;
}

function Select({ label, value, onChange, items, name }) {
  return (
    <label>{label} <select aria-label={name || label} value={value} onChange={event => onChange(event.target.value)}>
      {items.map(([v, text]) => <option key={v} value={v}>{text}</option>)}
    </select></label>
  );
}

export function FiscalMatrix({ compact = false }) {
  const [year, setYear] = useState(DEFAULT_YEAR);
  const [sort, setSort] = useState({ key: 'gfd_gsdp', dir: -1 });
  const keys = compact ? MATRIX_KEYS.slice(0, 5) : MATRIX_KEYS;
  const { rows, ranges } = useMemo(() => {
    const list = stateList.filter(state => keys.some(key => metricValue(key, state, year) !== null));
    list.sort((a, b) => {
      const va = metricValue(sort.key, a, year);
      const vb = metricValue(sort.key, b, year);
      if (va === null && vb === null) return a.localeCompare(b);
      if (va === null) return 1;
      if (vb === null) return -1;
      return (va - vb) * sort.dir || a.localeCompare(b);
    });
    const span = Object.fromEntries(keys.map(key => {
      const values = list.map(state => metricValue(key, state, year)).filter(v => v !== null);
      return [key, [Math.min(...values), Math.max(...values)]];
    }));
    return { rows: compact ? list.slice(0, 8) : list, ranges: span };
  }, [year, sort, compact]);
  const toggle = key => setSort(prev => ({ key, dir: key === prev.key ? -prev.dir : -1 }));
  return (
    <div className="fv fv-matrix">
      {!compact && (
        <div className="fv-controls">
          <Select label="Year" value={year} onChange={setYear} items={YEARS.map(y => [y, y])} />
          <span className="fv-hint">Click a column heading to sort. Green = healthier, red = more stretched; blue = scale only. {YEARS.length} years of RBI data.</span>
        </div>
      )}
      <div className="fv-table-wrap">
        <table className="fv-table">
          <thead><tr>
            <th scope="col">State / UT</th>
            {keys.map(key => (
              <th key={key} scope="col" tabIndex={0} role="button" data-key={key} title={metricByKey[key].note}
                aria-sort={key === sort.key ? (sort.dir > 0 ? 'ascending' : 'descending') : 'none'}
                onClick={() => toggle(key)} onKeyDown={event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); toggle(key); } }}>
                {metricByKey[key].label}<small>{metricByKey[key].unit}</small>{key === sort.key ? (sort.dir > 0 ? ' ▲' : ' ▼') : ''}
              </th>
            ))}
          </tr></thead>
          <tbody>
            {rows.map(state => (
              <tr key={state}>
                <th scope="row">{state}</th>
                {keys.map(key => {
                  const value = metricValue(key, state, year);
                  return <td key={key} style={{ background: cellColour(value, ranges[key][0], ranges[key][1], metricByKey[key].better) }}>{fmtMetric(key, value)}</td>;
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {!compact && (
        <p className="fv-note">Source: <a href={S.metrics[0].source_url} target="_blank" rel="noopener noreferrer">RBI Handbook of Statistics on Indian States 2024-25</a> and <a href="https://www.rbi.org.in/Scripts/PublicationsView.aspx?id=23729" target="_blank" rel="noopener noreferrer">RBI State Finances: A Study of Budgets 2025-26</a>. Ratios are computed from RBI rupee data; {metricByKey.gfd_gsdp.note} Committed expenditure = interest + pensions.</p>
      )}
    </div>
  );
}

function parseHash() {
  if (typeof window === 'undefined') return null;
  const match = /^#(.+)-vs-(.+)$/.exec(window.location.hash || '');
  if (!match) return null;
  const a = stateList.find(state => slug(state) === match[1]);
  const b = stateList.find(state => slug(state) === match[2]);
  return a && b ? [a, b] : null;
}

export function FiscalHeadToHead({ compact = false }) {
  const [pair, setPair] = useState(() => (!compact && parseHash()) || ['Kerala', 'Tamil Nadu']);
  const [year, setYear] = useState(DEFAULT_YEAR);
  const [copied, setCopied] = useState(false);
  const [a, b] = pair;
  useEffect(() => {
    if (compact) return undefined;
    const onHash = () => { const next = parseHash(); if (next) setPair(next); };
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, [compact]);
  const choose = next => {
    setPair(next);
    setCopied(false);
    if (!compact) window.history.replaceState(window.history.state, '', `${window.location.pathname}${window.location.search}#${slug(next[0])}-vs-${slug(next[1])}`);
  };
  const fy = FUNC_YEARS.includes(year) ? year : FUNC_YEARS[0];
  const fiscal = MATRIX_KEYS.map(key => ({ label: metricByKey[key].label, unit: metricByKey[key].unit, a: metricValue(key, a, year), b: metricValue(key, b, year), key }));
  const func = FUNCS.categories.map(name => ({ label: name, unit: `% of revenue spending (${fy})`, a: FUNCS.values[fy]?.[a]?.[name] ?? null, b: FUNCS.values[fy]?.[b]?.[name] ?? null, key: 'fn' }));
  const line = row => {
    const max = Math.max(Math.abs(row.a ?? 0), Math.abs(row.b ?? 0));
    const fmt = value => (row.key === 'fn' ? (value === null ? '–' : value.toFixed(1)) : fmtMetric(row.key, value));
    const bar = (value, side) => (value === null ? null : <span className={`fv-bar ${side}`} style={{ width: `${max ? Math.max(2, Math.abs(value) / max * 100).toFixed(1) : 0}%` }} />);
    return (
      <div className="fv-h2h-row" key={`${row.key}-${row.label}`}>
        <span className="fv-h2h-val a">{fmt(row.a)}</span>
        <span className="fv-h2h-side a">{bar(row.a, 'a')}</span>
        <span className="fv-h2h-label">{row.label}<small>{row.unit}</small></span>
        <span className="fv-h2h-side b">{bar(row.b, 'b')}</span>
        <span className="fv-h2h-val b">{fmt(row.b)}</span>
      </div>
    );
  };
  const items = stateList.map(s => [s, s]);
  return (
    <div className="fv fv-compare">
      <div className="fv-controls">
        <Select label="" name="First State" value={a} onChange={v => choose([v, b])} items={items} />
        <button type="button" className="fv-swap" aria-label="Swap States" onClick={() => choose([b, a])}>⇄</button>
        <Select label="" name="Second State" value={b} onChange={v => choose([a, v])} items={items} />
        <Select label="Year" value={year} onChange={setYear} items={YEARS.map(y => [y, y])} />
        {!compact && (
          <button type="button" className="fv-copy" onClick={() => {
            const url = `${window.location.origin}${window.location.pathname}${window.location.search}#${slug(a)}-vs-${slug(b)}`;
            navigator.clipboard?.writeText(url).then(() => setCopied(true));
          }}>{copied ? 'Link copied' : 'Copy link'}</button>
        )}
      </div>
      <div className="fv-h2h-head"><strong className="a">{a}</strong><strong className="b">{b}</strong></div>
      <div className="fv-h2h">
        {(compact ? fiscal.slice(0, 5) : fiscal).map(line)}
        {!compact && <><h4 className="fv-h2h-title">Where revenue spending goes</h4>{func.map(line)}</>}
      </div>
      {!compact && (
        <p className="fv-note">Permalink: <code>#{slug(a)}-vs-{slug(b)}</code>. Sources: <a href={S.metrics[0].source_url} target="_blank" rel="noopener noreferrer">RBI Handbook of Statistics on Indian States</a>; <a href={FUNCS.source_url} target="_blank" rel="noopener noreferrer">RBI State Finances: A Study of Budgets (Appendix II)</a>. Spending shares are available for 2023-24, 2024-25 RE and 2025-26 BE.</p>
      )}
    </div>
  );
}

const FUNC_COLOURS = ['#ff9933', '#3fb950', '#58a6ff', '#bc8cff', '#ff7b72', '#f6c344', '#39c5bb', '#f778ba', '#a5d6ff', '#d2a8ff', '#ffa657', '#7ee787', '#e3b341', '#8b949e'];
const OTHER = 'Other revenue spending';
const funcColour = name => (name === OTHER ? 'rgba(128,128,128,.4)' : FUNC_COLOURS[(FUNCS.categories.indexOf(name) + FUNC_COLOURS.length) % FUNC_COLOURS.length]);
const yearLabel = value => ({ '2024-25': '2024-25 RE', '2025-26': '2025-26 BE', '2023-24': '2023-24 Accounts' }[value] || value);

function shares(year, state) {
  const base = FUNCS.values[year]?.[state];
  if (!base) return [];
  const entries = FUNCS.categories.map(name => [name, base[name] ?? 0]);
  return [...entries, [OTHER, Math.max(0, 100 - entries.reduce((sum, [, value]) => sum + value, 0))]];
}

export function squarify(items, x, y, w, h) {
  const out = [];
  let rest = items.filter(item => item[1] > 0).sort((p, q) => q[1] - p[1]);
  let total = rest.reduce((sum, item) => sum + item[1], 0);
  const worst = (row, side, scale) => {
    const area = row.reduce((sum, item) => sum + item[1], 0) * scale;
    const max = Math.max(...row.map(item => item[1] * scale));
    const min = Math.min(...row.map(item => item[1] * scale));
    return Math.max((side * side * max) / (area * area), (area * area) / (side * side * min));
  };
  while (rest.length) {
    const scale = (w * h) / total;
    const side = Math.min(w, h);
    const row = [rest[0]];
    let i = 1;
    while (i < rest.length && worst([...row, rest[i]], side, scale) <= worst(row, side, scale)) row.push(rest[i++]);
    const rowSum = row.reduce((sum, item) => sum + item[1], 0);
    const thick = (rowSum * scale) / side;
    let offset = 0;
    row.forEach(item => {
      const length = (item[1] * scale) / thick;
      out.push(w >= h ? { item, x, y: y + offset, w: thick, h: length } : { item, x: x + offset, y, w: length, h: thick });
      offset += length;
    });
    if (w >= h) { x += thick; w -= thick; } else { y += thick; h -= thick; }
    total -= rowSum;
    rest = rest.slice(row.length);
  }
  return out;
}

export function FiscalSpending({ compact = false }) {
  const [year, setYear] = useState(FUNC_YEARS[0]);
  const [view, setView] = useState('bars');
  const [state, setState] = useState('Kerala');
  const [sortBy, setSortBy] = useState('Education');
  const states = Object.keys(FUNCS.values[year] || {}).filter(name => name !== 'All States & UTs');
  const current = states.includes(state) ? state : states[0];
  const rank = states.map(name => [name, FUNCS.values[year][name][sortBy] ?? 0]).sort((p, q) => q[1] - p[1] || p[0].localeCompare(q[0])).map(item => item[0]);
  const W = 900;
  const H = 440;
  return (
    <div className="fv fv-spending">
      <div className="fv-controls">
        <Select label="Year" value={year} onChange={setYear} items={FUNC_YEARS.map(y => [y, yearLabel(y)])} />
        <div className="fv-toggle" role="group" aria-label="View">
          <button type="button" aria-pressed={view === 'bars'} onClick={() => setView('bars')}>Stacked bars</button>
          <button type="button" aria-pressed={view === 'tree'} onClick={() => setView('tree')}>Treemap</button>
        </div>
        {view === 'tree'
          ? <Select label="State" value={current} onChange={setState} items={states.map(s => [s, s])} />
          : <Select label="Sort by" value={sortBy} onChange={setSortBy} items={FUNCS.categories.map(f => [f, f])} />}
      </div>
      {view === 'bars' ? (
        <div className="fv-stack">
          {(compact ? rank.slice(0, 8) : rank).map(name => (
            <button type="button" key={name} className={`fv-stack-row${name === current ? ' selected' : ''}`} aria-label={`Show ${name} as treemap`} onClick={() => { setState(name); setView('tree'); }}>
              <span className="fv-stack-name">{name}</span>
              <span className="fv-stack-bar">{shares(year, name).map(([fn, value]) => <span key={fn} style={{ width: `${value}%`, background: funcColour(fn) }} title={`${fn}: ${value.toFixed(1)}%`} />)}</span>
            </button>
          ))}
        </div>
      ) : (
        <svg className="fv-treemap" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`${current} spending by function`}>
          {squarify(shares(year, current), 0, 0, W, H).map(c => {
            const [fn, value] = c.item;
            const fits = c.w > 90 && c.h > 40;
            return (
              <g key={fn}>
                <rect x={c.x} y={c.y} width={c.w} height={c.h} fill={funcColour(fn)} stroke="var(--bg, #111)" strokeWidth="2"><title>{`${fn}: ${value.toFixed(1)}% of revenue expenditure`}</title></rect>
                {fits && <><text x={c.x + 8} y={c.y + 20} className="fv-tm-label">{fn}</text><text x={c.x + 8} y={c.y + 38} className="fv-tm-val">{value.toFixed(1)}%</text></>}
              </g>
            );
          })}
        </svg>
      )}
      <div className="fv-legend">
        {FUNCS.categories.map(fn => <span key={fn}><i style={{ background: funcColour(fn) }} />{fn}</span>)}
        <span><i style={{ background: funcColour(OTHER) }} />{OTHER}</span>
      </div>
      {!compact && <p className="fv-note">Share of revenue expenditure by function. Source: <a href={FUNCS.source_url} target="_blank" rel="noopener noreferrer">RBI, State Finances: A Study of Budgets 2025-26, Appendix II</a>. {FUNCS.note}</p>}
    </div>
  );
}

export function BudgetAnatomy({ compact = false }) {
  const years = UB.years.map(item => item.year);
  const [year, setYear] = useState(years[years.length - 1]);
  const [selected, setSelected] = useState(null);
  const data = UB.by_year[year];
  const basisNote = data.basis === 'Actuals' ? 'Actuals' : data.basis === 'RE' ? 'Revised Estimates' : 'Budget Estimates';
  const W = 880;
  const H = compact ? 260 : 460;
  const gap = 8;
  const layout = (nodes, x) => {
    const usable = H - gap * (nodes.length - 1);
    let y = 0;
    const placed = nodes.map(node => { const h = Math.max(3, (node.value / data.total) * usable); const out = { ...node, x, y, h }; y += h + gap; return out; });
    const sum = placed.reduce((s, n) => s + n.h, 0);
    let offset = 0;
    placed.forEach(n => { n.cy = offset; n.ch = (n.h / sum) * H; offset += n.ch; });
    return placed;
  };
  const left = layout(data.sources, 0);
  const right = layout(data.uses, W - NODE_W);
  const midX = (W - NODE_W) / 2;
  const link = (node, side) => {
    const x0 = side === 'l' ? node.x + NODE_W : midX + NODE_W;
    const x1 = side === 'l' ? midX : node.x;
    const ya = side === 'l' ? node.y : node.cy;
    const yb = side === 'l' ? node.cy : node.y;
    const hA = side === 'l' ? node.h : node.ch;
    const hB = side === 'l' ? node.ch : node.h;
    const mx = (x0 + x1) / 2;
    return <path key={`${side}-${node.id}`} className="fv-link" fill={node.color} opacity={selected === node.id ? 0.7 : 0.32}
      d={`M${x0},${ya} C${mx},${ya} ${mx},${yb} ${x1},${yb} L${x1},${yb + hB} C${mx},${yb + hB} ${mx},${ya + hA} ${x0},${ya + hA} Z`} />;
  };
  const pick = id => setSelected(prev => (prev === id ? null : id));
  const onKey = (event, id) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); pick(id); } };
  const block = (node, side) => (
    <g key={node.id} className={`fv-san-node${selected === node.id ? ' selected' : ''}`} data-node={node.id} role="button" tabIndex={compact ? -1 : 0}
      aria-label={`${node.label}, ${node.pct}% of total`} onClick={compact ? undefined : () => pick(node.id)} onKeyDown={compact ? undefined : event => onKey(event, node.id)}>
      <rect x={node.x} y={node.y} width={NODE_W} height={node.h} fill={node.color} />
      {!compact && <text x={side === 'l' ? node.x + NODE_W + 6 : node.x - 6} y={node.y + node.h / 2 + 4} textAnchor={side === 'l' ? 'start' : 'end'} className="fv-san-label">{node.label} · {node.pct}%</text>}
    </g>
  );
  const rupeeBar = (title, nodes) => (
    <div className="fv-rupee" key={title}>
      <h4>{title}</h4>
      <div className="fv-rupee-bar">
        {nodes.map(node => <button type="button" key={node.id} className={selected === node.id ? 'selected' : ''} style={{ width: `${node.pct}%`, background: node.color }} title={`${node.label}: ${node.paise} paise`} aria-label={`${node.label}, ${node.paise} paise per rupee`} onClick={() => pick(node.id)}>{node.pct >= 6 ? node.paise : ''}</button>)}
      </div>
      <ul className="fv-rupee-list">{nodes.map(node => <li key={node.id}><i style={{ background: node.color }} />{node.label} <b>{node.paise}p</b></li>)}</ul>
    </div>
  );
  const h = data.headline;
  const node = [...data.sources, ...data.uses].find(item => item.id === selected);
  const isReceipt = node && data.sources.some(item => item.id === node.id);
  const deficit = (value, pct) => `${lakhCrore(value)}${pct != null ? ` · ${pct}% of GDP` : ''}`;
  return (
    <div className="fv fv-anatomy">
      {!compact && (
        <div className="fv-controls">
          <Select label="Budget year" value={year} onChange={v => { setYear(v); setSelected(null); }} items={UB.years.map(item => [item.year, item.label])} />
          <span className="fv-hint">{basisNote} · total {lakhCrore(data.total)}</span>
        </div>
      )}
      <div className="fv-anatomy-grid">
        <div>
          <svg className="fv-sankey" viewBox={`0 0 ${W} ${H}`} role="group" aria-label={`Receipts flowing into expenditure for ${data.label}`}>
            {left.map(n => link(n, 'l'))}{right.map(n => link(n, 'r'))}
            <rect x={midX} y="0" width={NODE_W} height={H} fill="rgba(128,128,128,.55)" />
            {left.map(n => block(n, 'l'))}{right.map(n => block(n, 'r'))}
          </svg>
        </div>
        {!compact && (node ? (
          <div className="fv-detail" data-testid="anatomy-detail">
            <h4><i style={{ background: node.color }} />{node.label}</h4>
            <dl>
              <div><dt>Amount ({data.label})</dt><dd>{lakhCrore(node.value)} <small>{crore(node.value)}</small></dd></div>
              <div><dt>Share of {isReceipt ? 'receipts' : 'spending'}</dt><dd>{node.pct}% · {node.paise} paise in the rupee</dd></div>
              {node.prev ? <div><dt>Change on previous year</dt><dd>{node.yoy > 0 ? '+' : ''}{node.yoy}% (from {lakhCrore(node.prev)})</dd></div> : null}
            </dl>
            <p>{node.desc}</p>
          </div>
        ) : (
          <div className="fv-detail" data-testid="anatomy-detail">
            <h4>{data.label} at a glance</h4>
            <dl>
              <div><dt>Total (receipts = spending + States' share)</dt><dd>{lakhCrore(data.total)}</dd></div>
              <div><dt>Total expenditure</dt><dd>{lakhCrore(h.total_expenditure)}</dd></div>
              <div><dt>Capital expenditure</dt><dd>{lakhCrore(h.capital_expenditure)}</dd></div>
              <div><dt>Fiscal deficit</dt><dd>{deficit(h.fiscal_deficit, h.fiscal_deficit_pct_gdp)}</dd></div>
              <div><dt>Revenue deficit</dt><dd>{deficit(h.revenue_deficit, h.revenue_deficit_pct_gdp)}</dd></div>
              <div><dt>Primary deficit</dt><dd>{deficit(h.primary_deficit, h.primary_deficit_pct_gdp)}</dd></div>
              <div><dt>Interest payments</dt><dd>{lakhCrore(h.interest_payments)} · {h.interest_share_of_revenue_receipts}% of revenue receipts</dd></div>
              {h.transfers_to_states ? <div><dt>Total transfers to States</dt><dd>{lakhCrore(h.transfers_to_states)}</dd></div> : null}
            </dl>
            <p className="fv-hint">Click any block to see its size, share and change on the previous year.</p>
          </div>
        ))}
      </div>
      {!compact && <>
        {rupeeBar('The rupee comes from', data.sources)}
        {rupeeBar('The rupee goes to', data.uses)}
        <p className="fv-note">{UB.note} Source: <a href={data.source_url} target="_blank" rel="noopener noreferrer">{UB.source}</a>.</p>
      </>}
    </div>
  );
}

export default function FiscalView({ type, compact = false }) {
  if (type === 'fiscal-matrix') return <FiscalMatrix compact={compact} />;
  if (type === 'fiscal-compare') return <FiscalHeadToHead compact={compact} />;
  if (type === 'fiscal-spending') return <FiscalSpending compact={compact} />;
  return <BudgetAnatomy compact={compact} />;
}

export const FISCAL_TYPES = ['fiscal-matrix', 'fiscal-compare', 'fiscal-spending', 'budget-anatomy'];
