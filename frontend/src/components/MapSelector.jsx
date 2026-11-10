import { useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { binEdges, binOf, stateKey } from './IndiaMap.jsx';
import './MapSelector.css';

export const binFill = (bin, bins = 5) => `color-mix(in oklab, var(--map-high) ${Math.round(15 + (bin * 85) / (bins - 1))}%, var(--map-low))`;

// Quintile choropleth fills for a Map of region name -> value.
export function choropleth(points, scale = 'quantile') {
  const values = [...points.values()];
  if (!values.length) return { edges: [], fillOf: () => undefined };
  const edges = binEdges(values, scale);
  return { edges, fillOf: value => (value === undefined ? undefined : binFill(binOf(value, edges))) };
}

/**
 * Large clickable India map plus a region list. `regions` maps stateKey(name) to
 * { fill, summary, detail, to }; shapes without an entry stay neutral. Used by the Elections atlas and the map subgroups.
 */
export default function MapSelector({
  geometry, regions, ariaLabel, legend, controls, heading, intro, listLabel = 'Choose a State or Union Territory', onSelect, emptyLabel = 'No data',
}) {
  const stage = useRef(null);
  const [tip, setTip] = useState(null);
  const names = Object.keys(geometry.states);
  const moveTip = (name, event) => {
    const rect = stage.current?.getBoundingClientRect();
    const region = regions.get(stateKey(name));
    if (!rect) return;
    setTip({ name, text: region?.summary || emptyLabel, left: Math.max(8, event.clientX - rect.left + 12), top: Math.max(8, event.clientY - rect.top + 10) });
  };
  const open = name => {
    const region = regions.get(stateKey(name));
    if (region?.to) onSelect(region.to, name);
  };
  return (
    <section className="map-selector" aria-label={heading || ariaLabel}>
      {(heading || intro) && <div className="map-selector-heading">
        {heading && <h2>{heading}</h2>}
        {intro && <p>{intro}</p>}
      </div>}
      {controls && <div className="map-selector-controls">{controls}</div>}
      <div className="map-selector-stage" ref={stage} onPointerLeave={() => setTip(null)}>
        <svg viewBox={geometry.viewBox} role="group" aria-label={ariaLabel} preserveAspectRatio="xMidYMid meet">
          {names.map(name => {
            const region = regions.get(stateKey(name));
            const label = region?.summary || emptyLabel;
            return (
              <path
                key={name}
                d={geometry.states[name]}
                className={`map-selector-shape${region?.fill ? '' : ' is-empty'}`}
                style={region?.fill ? { fill: region.fill } : undefined}
                tabIndex={region?.to ? 0 : -1}
                role="button"
                aria-label={`${name}. ${label}.${region?.to ? ' Open its page.' : ''}`}
                onPointerMove={event => moveTip(name, event)}
                onFocus={event => moveTip(name, event)}
                onBlur={() => setTip(null)}
                onClick={() => open(name)}
                onKeyDown={event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); open(name); } }}
              >
                <title>{`${name} · ${label}`}</title>
              </path>
            );
          })}
        </svg>
        {tip && <div className="map-selector-tip" role="tooltip" style={{ left: tip.left, top: tip.top }}><strong>{tip.name}</strong><span>{tip.text}</span></div>}
      </div>
      {legend && <div className="map-selector-legend">{legend}</div>}
      <nav className="map-selector-list" aria-label={listLabel}>
        {names.map(name => {
          const region = regions.get(stateKey(name));
          const body = <><strong>{name}</strong><span>{region?.detail || region?.summary || emptyLabel}</span></>;
          return region?.to
            ? <Link key={name} to={region.to}>{body}</Link>
            : <div key={name} className="is-static">{body}</div>;
        })}
      </nav>
    </section>
  );
}

export function QuintileLegend({ edges, format, label }) {
  if (!edges.length) return null;
  return (
    <>
      <span className="map-selector-legend-label">{label}</span>
      <span>≤ {format(edges[0])}</span>
      <span className="map-selector-scale" role="img" aria-label={`Colour scale from low to high; breaks at ${edges.map(format).join(', ')}`}>
        {[0, 1, 2, 3, 4].map(bin => <i key={bin} style={{ background: binFill(bin) }} />)}
      </span>
      <span>&gt; {format(edges[edges.length - 1])}</span>
    </>
  );
}
