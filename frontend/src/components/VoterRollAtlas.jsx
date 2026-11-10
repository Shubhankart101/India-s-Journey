import { useEffect, useMemo, useState } from 'react';
import { loadGeometry } from './IndiaMap.jsx';
import DATA from '../data/voter-roll.json';
import './VoterRollAtlas.css';
import SubgroupArticle from './SubgroupArticle.jsx';
import { pickVerse } from '../scripture.js';

const fmt = value => new Intl.NumberFormat('en-IN').format(value);
const crore = value => `${(value / 10000000).toFixed(2)} crore`;
const sourceAnchor = (href, label = 'Source ↗') => <a href={href} target="_blank" rel="noreferrer">{label}</a>;
const allStateData = new Map(DATA.sir.states.map(item => [item.state.toLowerCase(), item]));

function ElectionFigure() {
  const [selected, setSelected] = useState(DATA.elections.length - 1);
  const row = DATA.elections[selected];
  const maxElectors = 1000000000;
  const maxPopulation = 1500000000;
  const plot = { x: 54, y: 24, width: 900, height: 260 };
  const slot = plot.width / DATA.elections.length;
  const x = index => plot.x + (index + 0.5) * slot;
  const electorY = value => plot.y + plot.height - (value / maxElectors) * plot.height;
  const populationY = value => plot.y + plot.height - (value / maxPopulation) * plot.height;
  const turnoutY = value => plot.y + plot.height - (value / 80) * plot.height;
  const populationPath = DATA.elections.map((item, index) => `${index ? 'L' : 'M'}${x(index).toFixed(1)},${populationY(item.population).toFixed(1)}`).join(' ');
  const turnoutPath = DATA.elections.map((item, index) => `${index ? 'L' : 'M'}${x(index).toFixed(1)},${turnoutY(item.turnout_percent).toFixed(1)}`).join(' ');
  const markerX = x(DATA.elections.findIndex(item => item.year === 1989));

  return (
    <figure className="vra-figure">
      <div className="vra-chart-scroll">
        <svg className="vra-election-chart" viewBox="0 0 1000 330" role="img" aria-label="Bars show registered electors; lines show population and turnout at Lok Sabha elections from 1951–52 through 2024">
          {[0, 0.25, 0.5, 0.75, 1].map(fraction => (
            <line key={fraction} x1={plot.x} x2={plot.x + plot.width} y1={plot.y + plot.height * fraction} y2={plot.y + plot.height * fraction} className="vra-gridline" />
          ))}
          <line x1={markerX} x2={markerX} y1={plot.y} y2={plot.y + plot.height} className="vra-voting-marker" />
          <text x={markerX + 6} y="17" className="vra-marker-label">Age 18 from 1989 polls</text>
          {DATA.elections.map((item, index) => {
            const barHeight = plot.y + plot.height - electorY(item.electors);
            return (
              <rect
                key={item.label}
                x={x(index) - slot * 0.29}
                y={electorY(item.electors)}
                width={slot * 0.58}
                height={barHeight}
                rx="3"
                className={`vra-elector-bar${selected === index ? ' selected' : ''}`}
                role="button"
                tabIndex={0}
                aria-label={`${item.label}: ${fmt(item.electors)} registered electors, ${item.turnout_percent}% turnout`}
                aria-pressed={selected === index}
                onClick={() => setSelected(index)}
                onFocus={() => setSelected(index)}
                onMouseEnter={() => setSelected(index)}
                onKeyDown={event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); setSelected(index); } }}
              />
            );
          })}
          <path d={populationPath} className="vra-population-line" />
          <path d={turnoutPath} className="vra-turnout-line" />
          {DATA.elections.map((item, index) => <g key={`dots-${item.label}`}>
            <circle cx={x(index)} cy={populationY(item.population)} r="3.5" className="vra-population-dot" />
            <circle cx={x(index)} cy={turnoutY(item.turnout_percent)} r="3.5" className="vra-turnout-dot" />
          </g>)}
        </svg>
      </div>
      <div className="vra-legend" aria-label="Chart legend">
        <span><i className="vra-legend-electors" /> Registered electors</span>
        <span><i className="vra-legend-population" /> Population</span>
        <span><i className="vra-legend-turnout" /> Turnout %</span>
      </div>
      <div className="vra-year-picker" aria-label="Choose an election">
        {DATA.elections.map((item, index) => <button key={item.label} type="button" aria-pressed={selected === index} onClick={() => setSelected(index)}>{item.label}</button>)}
      </div>
      <output className="vra-selection" aria-live="polite">
        <strong>{row.label}</strong>: {fmt(row.electors)} electors · {row.turnout_percent}% turnout · population {crore(row.population)} ({row.population_year} source year)
        <span className="vra-sources">{sourceAnchor(row.sources.electors, 'ECI electors')} · {sourceAnchor(row.sources.turnout, 'ECI turnout')} · {sourceAnchor(row.sources.population, 'Population')}</span>
      </output>
      <figcaption className="vra-note">{DATA.figures.elections.population_note} {DATA.figures.elections.turnout_note} The population series is on a separate scale from electors and turnout.</figcaption>
      <p className="vra-source-row">Voting-age change: {sourceAnchor(DATA.sources.voting_age.url, DATA.sources.voting_age.label)}.</p>
    </figure>
  );
}

function changePercent(item) {
  return item.before && item.final ? ((item.final - item.before) / item.before) * 100 : null;
}

function sirFill(item) {
  const change = changePercent(item);
  if (change === null) return 'var(--map-empty, #78808a)';
  if (change <= -10) return '#9b1c1c';
  if (change <= -5) return '#df7128';
  if (change < 0) return '#f2b84b';
  return '#2f9d65';
}

function SirMap() {
  const [geometry, setGeometry] = useState(null);
  const [selected, setSelected] = useState('Bihar');
  const [error, setError] = useState('');
  const row = allStateData.get(selected.toLowerCase());
  useEffect(() => {
    let active = true;
    loadGeometry().then(value => { if (active) setGeometry(value); }, reason => { if (active) setError(reason.message); });
    return () => { active = false; };
  }, []);
  const activate = (name, event) => {
    if (event && event.type === 'keydown' && !['Enter', ' '].includes(event.key)) return;
    if (event && event.type === 'keydown') event.preventDefault();
    setSelected(name);
  };

  return (
    <figure className="vra-figure">
      {geometry ? <svg className="vra-sir-map" viewBox={geometry.viewBox} role="group" aria-label="India map; select a State or Union Territory for SIR information">
        {Object.entries(geometry.states).map(([name, path]) => {
          const info = allStateData.get(name.toLowerCase());
          return <path
            key={name}
            d={path}
            fill={sirFill(info || {})}
            className={`vra-state-shape${name === selected ? ' selected' : ''}`}
            tabIndex={0}
            role="button"
            data-state={name}
            aria-pressed={name === selected}
            aria-label={`${name}${changePercent(info || {}) === null ? ', no comparable roll totals in this dataset' : `, ${changePercent(info).toFixed(1)} percent change in electors`}`}
            onClick={event => activate(name, event)}
            onKeyDown={event => activate(name, event)}
          />;
        })}
      </svg> : <p className="vra-map-message" role={error ? 'alert' : 'status'}>{error || 'Loading State/UT outlines…'}</p>}
      <div className="vra-map-legend"><span><i className="vra-map-color" /> Bihar: before → final change</span><span><i className="vra-map-empty" /> Totals not verified here</span></div>
      <label className="vra-state-select">Choose a State/UT
        <select value={selected} onChange={event => setSelected(event.target.value)}>
          {DATA.sir.states.map(item => <option key={item.state} value={item.state}>{item.state}</option>)}
        </select>
      </label>
      <div className="vra-state-detail" aria-live="polite" data-testid="sir-state-detail">
        <p className="vra-eyebrow">{row?.phase ? `SIR phase ${row.phase}` : 'Roll data'}</p>
        <h3>{selected}</h3>
        <p>{row?.status}</p>
        {row?.before ? <dl className="vra-state-counts">
          <div><dt>Before SIR</dt><dd>≈ {crore(row.before)}</dd></div>
          <div><dt>Draft roll</dt><dd>≈ {crore(row.draft)}</dd></div>
          <div><dt>Final roll</dt><dd>≈ {crore(row.final)}</dd></div>
          <div><dt>Before → final</dt><dd>{changePercent(row).toFixed(1)}%</dd></div>
        </dl> : <p className="vra-note">Comparable before, draft and final counts were not available in the cited ECI material used for this view. The gray fill indicates missing comparable figures, not a claim that the state has not undergone revision.</p>}
        {row?.source && <p className="vra-source-row">{sourceAnchor(row.source, 'ECI state source ↗')}</p>}
      </div>
      <figcaption className="vra-note">{DATA.sir.note}</figcaption>
      <p className="vra-source-row">Phase references: {sourceAnchor(DATA.sources.sir_bihar.url, 'Bihar')} · {sourceAnchor(DATA.sources.sir_phase_ii.url, 'Phase II')} · {sourceAnchor(DATA.sources.sir_phase_iii.url, 'Phase III')}.</p>
    </figure>
  );
}

function RevisionCalendar() {
  const [active, setActive] = useState(0);
  const item = DATA.calendar[active];
  return <figure className="vra-figure">
    <div className="vra-calendar-steps" role="group" aria-label="SSR revision calendar">
      {DATA.calendar.map((step, index) => <button key={step.id} type="button" aria-pressed={index === active} onClick={() => setActive(index)}>
        <strong>{step.title}</strong><span>{step.label}</span>
      </button>)}
    </div>
    <div className="vra-step-detail" aria-live="polite"><p className="vra-eyebrow">{item.label}</p><h3>{item.title}</h3><p>{item.detail}</p>{sourceAnchor(item.source, 'Read the rule/source ↗')}</div>
    <figcaption className="vra-note">A qualifying date is the reference date for age eligibility; the draft, claims period and final publication are stages of the revision, not extra qualifying dates.</figcaption>
  </figure>;
}

function DeletionFigure() {
  const { reasons, total_reported: total, ratios, safeguards, note } = DATA.deletions;
  const reasonSum = reasons.reduce((sum, item) => sum + item.value, 0);
  return <figure className="vra-figure">
    <div className="vra-deletion-total"><strong>{(total / 10000000).toFixed(2)} crore</strong><span>deletions reported across the SSR before the 2024 general election</span></div>
    <div className="vra-segment-bar" role="img" aria-label={reasons.map(item => `${item.label}: ${fmt(item.value)}`).join('; ')}>
      {reasons.map((item, index) => <span key={item.label} className={`vra-segment segment-${index}`} style={{ flexGrow: item.value / reasonSum }} title={`${item.label}: ${fmt(item.value)}`} />)}
    </div>
    <ul className="vra-reason-list">{reasons.map((item, index) => <li key={item.label}><i className={`vra-reason-dot segment-${index}`} /><span>{item.label}</span><strong>{fmt(item.value)}</strong>{sourceAnchor(item.source, 'ECI/PIB ↗')}</li>)}</ul>
    <p className="vra-note">{note}</p>
    <div className="vra-ratio-grid">{ratios.map(item => <article key={item.label}><h3>{item.label}</h3><p><strong>{item.before}</strong> → <strong>{item.after}</strong></p>{sourceAnchor(item.source, 'ECI/PIB source ↗')}</article>)}</div>
    <h3>Checks before a name is removed</h3>
    <ul className="vra-safeguards">{safeguards.map(item => <li key={item.title}><strong>{item.title}</strong><p>{item.detail}</p>{sourceAnchor(item.source, 'Source ↗')}</li>)}</ul>
    <figcaption className="vra-note">The chart shows the three reason counts published by ECI/PIB; it does not invent a category for the unexplained difference.</figcaption>
  </figure>;
}

function FormsStepper() {
  const [scenarioId, setScenarioId] = useState(DATA.scenarios[0].id);
  const [stepIndex, setStepIndex] = useState(0);
  const scenario = useMemo(() => DATA.scenarios.find(item => item.id === scenarioId) || DATA.scenarios[0], [scenarioId]);
  const changeScenario = event => { setScenarioId(event.target.value); setStepIndex(0); };
  const step = Math.min(stepIndex, scenario.steps.length - 1);
  return <figure className="vra-figure">
    <label className="vra-scenario-select">What happened?
      <select aria-label="Choose a voter scenario" value={scenarioId} onChange={changeScenario}>
        {DATA.scenarios.map(item => <option key={item.id} value={item.id}>{item.title}</option>)}
      </select>
    </label>
    <div className="vra-form-answer" aria-live="polite">
      <p className="vra-eyebrow">Suggested route</p><h3>{scenario.form}</h3><p>{scenario.action}</p>
      <div className="vra-route-step"><span>Step {step + 1} of {scenario.steps.length}</span><p>{scenario.steps[step]}</p></div>
      <div className="vra-step-controls">
        <button type="button" onClick={() => setStepIndex(Math.max(0, step - 1))} disabled={step === 0}>Previous</button>
        <button type="button" onClick={() => setStepIndex(Math.min(scenario.steps.length - 1, step + 1))} disabled={step === scenario.steps.length - 1}>Next step</button>
      </div>
      <p className="vra-where">File online at {sourceAnchor(DATA.sources.forms.url, 'voters.eci.gov.in')}, through the Voter Helpline App, or with your BLO/ERO. For guidance, call <a href="tel:1950">1950</a> ({sourceAnchor(DATA.sources.sir_phase_ii.url, 'ECI guidance')}). Exact processing time depends on verification and the applicable revision schedule; this guide does not promise a fixed number of days.</p>
      {sourceAnchor(scenario.source, 'Form instructions/source ↗')}
    </div>
    <div className="vra-form-index"><strong>Form 6</strong> new enrolment · <strong>Form 7</strong> deletion/objection · <strong>Form 8</strong> shifting or correction · <strong>Form 6A</strong> overseas elector.</div>
    <figcaption className="vra-note">This is a route guide, not an application. Use the ECI portal for the current form and requirements.</figcaption>
  </figure>;
}

export default function VoterRollAtlas({ compact = false }) {
  if (compact) return <div className="vra-preview"><span lang="sa">मतदातृसूची</span><strong>SSR &amp; SIR interactive guide</strong><span>5 figures · 6 voter scenarios</span></div>;
  const latest = DATA.elections[DATA.elections.length - 1];
  const first = DATA.elections[0];
  const sections = [
    { title: 'The roll behind the ballot', text: 'Electoral rolls grow as eligible citizens are enrolled and change when people move, die or become ineligible. This election series puts those administrative counts beside population and turnout, while keeping their different scales visible.', content: <ElectionFigure /> },
    { title: 'SIR: a fresh enumeration', text: 'A Special Intensive Revision uses a fresh enumeration process rather than only updating an existing list. The map shows comparable counts only where the cited Election Commission material provides them; an unfilled state is a gap in this dataset, not a zero.', quote: 'A blank on this map means the figures were not verified here; it does not mean that no revision took place.', content: <SirMap /> },
    { title: 'SSR: the annual update', text: 'A Special Summary Revision updates the current roll through a published calendar. Select a milestone to see what happens at that stage and read the linked rule or notice.', content: <RevisionCalendar /> },
    { title: 'Deletions and safeguards', text: 'Deletion totals need careful reading: the published reason categories do not necessarily explain every change. The breakdown preserves that difference and pairs it with the checks required before a name is removed.', content: <DeletionFigure /> },
    { title: 'Find the right form', text: 'The form depends on whether someone is applying for a first enrolment, reporting a deletion, correcting or shifting an entry, or registering as an overseas elector. Use the official portal for current requirements.', content: <FormsStepper /> },
  ];
  const sources = Object.values(DATA.sources).map(source => ({ name: source.label, url: source.url }));
  return <SubgroupArticle
    headline="SIR, SSR and you: how India's voter list is revised"
    dek="India's electoral roll is a living record: it must add eligible voters, reflect changed circumstances and give people a clear route to correct an entry. This guide follows the evidence and the official process, from the first rolls to today's forms."
    kicker="Electoral rolls · an interactive guide"
    sections={sections}
    keyNumbers={[
      { label: 'Registered electors in 2024', value: `${(latest.electors / 10000000).toFixed(2)} crore` },
      { label: 'First general election', value: `${(first.electors / 10000000).toFixed(2)} crore` },
      { label: 'Reported pre-election deletions', value: `${(DATA.deletions.total_reported / 10000000).toFixed(2)} crore` },
    ]}
    verse={pickVerse('voter-list-sir-ssr', 'Elections & Democracy')}
    sources={sources}
    className="voter-roll-atlas"
    sectionClassName="vra-section"
  />;
}