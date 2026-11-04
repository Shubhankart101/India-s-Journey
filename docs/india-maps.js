/* "India in Maps": State/UT choropleths derived from every published series whose labels (or dataset names)
   are States/UTs. Shared by app.js and scripts/export_catalog.mjs so the static site and web app match. */
(root => {
  const GROUP = 'India in Maps';
  const MIN_STATES = 5;
  // Per-State breakdown categories are mapped only when enough States/UTs report them.
  const JURISDICTION_MIN_STATES = 10;
  const STATES = [
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana',
    'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya',
    'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
    'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Andaman & Nicobar Islands', 'Chandigarh',
    'Dadra & Nagar Haveli and Daman & Diu', 'Delhi', 'Jammu & Kashmir', 'Ladakh', 'Lakshadweep', 'Puducherry',
  ];
  // Mirrors canonical_state() in scripts/rbi_state_layer.py.
  const ALIASES = {
    'andaman & nicobar islands': 'Andaman & Nicobar Islands', 'andaman & nicobar': 'Andaman & Nicobar Islands',
    'a & n islands': 'Andaman & Nicobar Islands', delhi: 'Delhi', 'nct delhi': 'Delhi', 'nct of delhi': 'Delhi',
    'delhi ncr': 'Delhi', 'jammu & kashmir': 'Jammu & Kashmir', 'j & k': 'Jammu & Kashmir',
    'dadra & nagar haveli': 'Dadra & Nagar Haveli and Daman & Diu', 'dadar & nagar haveli': 'Dadra & Nagar Haveli and Daman & Diu',
    'dadra & nagar haveli & daman & diu': 'Dadra & Nagar Haveli and Daman & Diu', 'dnh & dd': 'Dadra & Nagar Haveli and Daman & Diu',
    orissa: 'Odisha', pondicherry: 'Puducherry', uttaranchal: 'Uttarakhand', chattisgarh: 'Chhattisgarh', tamilnadu: 'Tamil Nadu',
  };
  const CANONICAL = Object.fromEntries(STATES.map(name => [name.toLowerCase(), name]));

  const canonicalState = name => {
    let text = String(name ?? '').replace(/\(.*?\)/g, '');
    text = text.trim().replace(/^\d+\.?\s+/, '');
    text = text.replace(/&amp;/g, '&').replace(/\s+and\s+/gi, ' & ');
    text = text.replace(/^the\s+/i, '');
    text = text.trim().replace(/[*#@^$]+|\d+$/g, '');
    text = text.replace(/\s*&\s*/g, ' & ');
    const key = text.split(/\s+/).filter(Boolean).join(' ').replace(/^[ .:-]+|[ .:-]+$/g, '').toLowerCase();
    return CANONICAL[key] || ALIASES[key] || null;
  };
  const slug = name => String(name).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  const subgroupFor = group => `${group} on the map`;
  const artFor = group => `assets/maps-${slug(group)}.svg`;
  const finite = value => value !== null && value !== undefined && value !== '' && Number.isFinite(Number(value));

  const statePoints = (labels, values) => {
    const points = new Map();
    labels.forEach((label, index) => {
      const state = canonicalState(label);
      if (state && !points.has(state) && finite(values[index])) points.set(state, Number(values[index]));
    });
    return points;
  };

  // `lookup(key)` returns { group, subgroup, title, subtitle, frequency, color, suffix } for a source series.
  const deriveMapSeries = (series, lookup) => {
    const out = {};
    const add = (key, sourceKey, item, points, titleSuffix, extraNote, options = {}) => {
      if (points.size < MIN_STATES) return;
      const info = lookup(sourceKey) || {};
      const group = info.group;
      if (!group || group === GROUP) return;
      const theme = options.theme || group;
      const title = options.title || `${info.title || item.meta?.title || sourceKey}${titleSuffix}`;
      out[key] = {
        labels: [...points.keys()],
        values: [...points.values()],
        chartType: 'map',
        scope: 'state',
        scopeLabel: 'States/UTs mapped',
        source: item.source || '',
        unit: item.unit || '',
        note: [`Map view of "${title}" from ${group} › ${options.sourceSubgroup || info.subgroup || group}. ${points.size} of ${STATES.length} States/UTs have a value; unshaded areas are not reported by the source.`, extraNote, options.title ? '' : item.note].filter(Boolean).join(' '),
        meta: {
          title: `${title} — map`,
          subtitle: options.subtitle || info.subtitle || item.meta?.subtitle || `${group} on the map of India`,
          frequency: info.frequency || 'Cross-section',
          color: info.color || '#ff9933',
          suffix: info.suffix || '',
          category: GROUP,
          subgroup: subgroupFor(theme),
          sourceGroup: group,
          mapTheme: theme,
          sourceKey,
        },
      };
    };
    // Breakdowns published as one series per State/UT (e.g. NJDG lower courts, titled "<State>: <measure>").
    const jurisdictions = new Map();
    Object.entries(series || {}).forEach(([key, item]) => {
      if (!item || item.error || item.chartType === 'map' || key.startsWith('map__')) return;
      const scope = String(item.scope || '');
      if (scope.startsWith('jurisdiction:')) {
        const place = scope.slice('jurisdiction:'.length);
        const state = canonicalState(place);
        const title = String(item.meta?.title || '');
        if (state && item.values?.length && title.startsWith(`${place}: `)) {
          const measure = title.slice(place.length + 2);
          const id = `${item.meta?.category}|${item.meta?.subgroup}|${measure}`;
          if (!jurisdictions.has(id)) jurisdictions.set(id, { measure, subgroup: item.meta?.subgroup || '', rows: [] });
          jurisdictions.get(id).rows.push({ state, key, item });
        }
        return;
      }
      const labels = item.labels || [];
      const datasets = item.datasets || [];
      if (item.values?.length) {
        add(`map__${key}`, key, item, statePoints(labels, item.values), '', '');
        return;
      }
      datasets.forEach((dataset, index) => {
        const values = dataset.values || dataset.data || [];
        const suffix = datasets.length > 1 ? `: ${dataset.label || `Series ${index + 1}`}` : '';
        add(datasets.length > 1 ? `map__${key}__${index + 1}` : `map__${key}`, key, item, statePoints(labels, values), suffix, '');
      });
      // State-wise trend lines: one dataset per State/UT, so map each State/UT's latest reported value.
      const latest = new Map();
      let period = '';
      datasets.forEach(dataset => {
        const state = canonicalState(dataset.label);
        const values = dataset.values || dataset.data || [];
        for (let index = values.length - 1; index >= 0; index -= 1) {
          if (state && !latest.has(state) && finite(values[index])) {
            latest.set(state, Number(values[index]));
            period = period || String(labels[index] ?? '');
            break;
          }
        }
      });
      add(`map__${key}__latest`, key, item, latest, ' (latest reported)', period ? `Each State/UT shows its latest reported value (most recent period: ${period}).` : '');
    });
    const totals = new Set();
    jurisdictions.forEach(({ measure, subgroup, rows }) => {
      const heading = measure.charAt(0).toUpperCase() + measure.slice(1);
      const options = (title, subtitle) => ({ title, subtitle, theme: subgroup || undefined, sourceSubgroup: subgroup });
      const byLabel = new Map();
      const total = new Map();
      rows.forEach(({ state, item }) => {
        let sum = 0;
        (item.labels || []).forEach((label, index) => {
          const value = item.values[index];
          if (!finite(value) || /^\d{4}/.test(String(label)) || /^null$/i.test(String(label))) return;
          if (!byLabel.has(label)) byLabel.set(label, new Map());
          if (!byLabel.get(label).has(state)) byLabel.get(label).set(state, Number(value));
          sum += Number(value);
        });
        if (sum > 0 && !total.has(state)) total.set(state, sum);
      });
      const first = rows[0];
      const signature = JSON.stringify([...total.entries()]);
      if (!totals.has(signature)) {
        totals.add(signature);
        add(`map__jur__${slug(first.item.meta?.category)}__${slug(measure)}__total`, first.key, first.item, total, '', 'Each State/UT shows the sum of the categories it reports.',
          options(`${heading}: total by State/UT`, `${measure}, summed across categories for each State/UT`));
      }
      byLabel.forEach((points, label) => {
        if (points.size < JURISDICTION_MIN_STATES) return;
        add(`map__jur__${slug(first.item.meta?.category)}__${slug(measure)}__${slug(label)}`, first.key, first.item, points, '', '',
          options(`${heading}: ${label}`, `${label} — ${measure}, by State/UT`));
      });
    });
    return out;
  };

  // Adds hero text and artwork for the map group's subgroups (one per source group or theme).
  const decorate = ({ subgroupArtMap, subgroupHeroData }, themes) => {
    themes.forEach(theme => {
      const name = subgroupFor(theme);
      subgroupArtMap[name] = artFor(theme);
      subgroupHeroData[name] = {
        title: `🗺️ ${theme} on the map`,
        desc: `Every ${theme} statistic with State/UT values, drawn as a map of India. Darker shading means a higher value; hover or tap a State/UT for its figure.`,
        badge1: 'Choropleth',
        badge2: theme,
      };
    });
  };

  let geometryPromise = null;
  const loadGeometry = (url = 'assets/maps/india-states.json') => {
    geometryPromise = geometryPromise || fetch(url).then(response => {
      if (!response.ok) throw new Error(`Map outline unavailable (HTTP ${response.status})`);
      return response.json();
    });
    return geometryPromise;
  };

  const escape = value => String(value ?? '').replace(/[&<>"']/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));

  // Draws an SVG choropleth into `container`; colours come from the --map-* CSS variables so themes apply.
  const render = async (container, { labels = [], values = [], title = 'Map', suffix = '', format = value => String(value) }) => {
    const points = statePoints(labels, values);
    const numbers = [...points.values()];
    const min = Math.min(...numbers);
    const max = Math.max(...numbers);
    const share = value => (max === min ? 100 : Math.round(((value - min) / (max - min)) * 85 + 15));
    const ranked = [...points.entries()].sort((a, b) => b[1] - a[1]);
    const figure = document.createElement('figure');
    figure.className = 'india-map';
    figure.innerHTML = '<p class="india-map-status">Drawing map…</p>';
    container.append(figure);
    let geometry;
    try {
      geometry = await loadGeometry();
    } catch (error) {
      figure.innerHTML = `<p class="india-map-status">${escape(error.message)}</p>`;
      return figure;
    }
    const shapes = Object.entries(geometry.states).map(([name, d]) => {
      const has = points.has(name);
      const value = points.get(name);
      const label = has ? `${name}: ${format(value, suffix)} (rank ${ranked.findIndex(([state]) => state === name) + 1} of ${ranked.length})` : `${name}: not reported`;
      const fill = has ? `color-mix(in oklab, var(--map-high) ${share(value)}%, var(--map-low))` : 'var(--map-empty)';
      return `<path d="${d}" data-state="${escape(name)}" data-label="${escape(label)}" style="fill:${fill}" class="${has ? 'has-value' : 'no-value'}" tabindex="${has ? 0 : -1}"><title>${escape(label)}</title></path>`;
    }).join('');
    const top = ranked[0];
    const bottom = ranked[ranked.length - 1];
    const summary = `${title}: ${points.size} States/UTs shaded. Highest ${top[0]} (${format(top[1], suffix)}), lowest ${bottom[0]} (${format(bottom[1], suffix)}).`;
    figure.innerHTML = `<svg viewBox="${geometry.viewBox}" role="img" aria-label="${escape(summary)}" preserveAspectRatio="xMidYMid meet">${shapes}</svg>`
      + `<figcaption class="india-map-legend"><span class="india-map-readout" aria-live="polite">${escape(`Highest: ${top[0]} · ${format(top[1], suffix)}`)}</span>`
      + `<span class="india-map-scale"><span>${escape(format(min, suffix))}</span><i aria-hidden="true"></i><span>${escape(format(max, suffix))}</span></span>`
      + `<span class="india-map-credit">Boundaries: <a href="${escape(geometry.sourceUrl)}" target="_blank" rel="noreferrer">DataMeet</a> (${escape(geometry.license)})</span></figcaption>`;
    const readout = figure.querySelector('.india-map-readout');
    const show = event => {
      const path = event.target.closest?.('path[data-label]');
      if (path) readout.textContent = path.dataset.label;
    };
    figure.querySelector('svg').addEventListener('pointerover', show);
    figure.querySelector('svg').addEventListener('focusin', show);
    return figure;
  };

  root.IndiaMaps = { GROUP, MIN_STATES, STATES, canonicalState, slug, subgroupFor, artFor, deriveMapSeries, decorate, render, loadGeometry };
})(typeof window !== 'undefined' ? window : globalThis);
