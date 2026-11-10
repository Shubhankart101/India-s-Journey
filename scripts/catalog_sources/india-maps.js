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
  // Bump when scripts/build_india_maps.py output changes; earlier broken SVGs may sit in browser caches.
  const ART_VERSION = '4';
  const artFor = group => `assets/maps-${slug(group)}.svg?v=${ART_VERSION}`;
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
        note: [`${options.derived ? 'Derived map' : 'Map view'} of "${title}" from ${group} › ${options.sourceSubgroup || info.subgroup || group}. ${points.size} of ${STATES.length} States/UTs have a value; unshaded areas are not reported by the source.`, extraNote, options.title ? '' : item.note].filter(Boolean).join(' '),
        meta: {
          title: `${title} — map`,
          subtitle: options.subtitle || info.subtitle || item.meta?.subtitle || `${group} on the map of India`,
          frequency: options.frequency || info.frequency || 'Cross-section',
          color: info.color || '#ff9933',
          suffix: options.suffix ?? info.suffix ?? '',
          category: GROUP,
          subgroup: subgroupFor(theme),
          sourceGroup: group,
          mapTheme: theme,
          sourceKey,
        },
      };
      // Time-framed maps list one dataset per period (newest first) so the viewer can offer a year slider.
      if (options.frames?.length) {
        const labels = [...options.frames[0].points.keys()];
        options.frames.forEach(frame => frame.points.forEach((_, state) => { if (!labels.includes(state)) labels.push(state); }));
        out[key].labels = labels;
        out[key].datasets = options.frames.map(frame => ({ label: frame.label, values: labels.map(state => (frame.points.has(state) ? frame.points.get(state) : null)) }));
        out[key].values = out[key].datasets[0].values;
        out[key].note += ` Use the slider to step through ${options.frames.length} periods (${options.frames[options.frames.length - 1].label} to ${options.frames[0].label}).`;
      }
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
        if (state && (item.values?.length || item.datasets?.length) && title.startsWith(`${place}: `)) {
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
    const yearOf = label => (/^\d{4}$/.test(String(label)) ? Number(label) : null);
    const lowerBound = label => {
      const match = String(label).match(/^\s*(?:above|over|more than)?\s*(\d+)/i);
      return match ? Number(match[1]) : null;
    };
    // Per-State series whose labels are years/age buckets become year-slider maps and "older than N years" shares.
    const derivePerJurisdictionMaps = (_all, rows, measure, heading, subgroup, options) => {
      const first = rows[0];
      const stem = `map__jur__${slug(first.item.meta?.category)}__${slug(measure)}`;
      if (/by filing year/i.test(measure)) {
        const byYear = new Map();
        rows.forEach(({ state, item }) => (item.labels || []).forEach((label, index) => {
          const year = yearOf(label);
          if (year === null || !finite(item.values[index])) return;
          if (!byYear.has(year)) byYear.set(year, new Map());
          byYear.get(year).set(state, Number(item.values[index]));
        }));
        const newest = Math.max(...byYear.keys());
        const frames = [...byYear.entries()].filter(([year, points]) => year > newest - 15 && points.size >= MIN_STATES)
          .sort((left, right) => right[0] - left[0]).map(([year, points]) => ({ label: String(year), points }));
        if (frames.length > 1) {
          add(`${stem}__by_year`, first.key, first.item, frames[0].points, '', `Each period is the year the pending cases were filed; the latest year (${frames[0].label}) is partial.`,
            { ...options(`${heading} (year slider)`, `${measure}, by State/UT and year of filing`), frames, frequency: 'Snapshot by filing year' });
        }
      }
      if (/pending by age$/i.test(measure)) {
        [5, 10].forEach(years => {
          const shares = new Map();
          rows.forEach(({ state, item }) => {
            let all = 0;
            let older = 0;
            (item.labels || []).forEach((label, index) => {
              const bound = lowerBound(label);
              if (bound === null || !finite(item.values[index])) return;
              all += Number(item.values[index]);
              if (bound >= years) older += Number(item.values[index]);
            });
            if (all > 0 && !shares.has(state)) shares.set(state, Math.round((older / all) * 1000) / 10);
          });
          add(`${stem}__older_than_${years}`, first.key, first.item, shares, '', `Share of each State/UT's pending cases that are ${years} years old or more (buckets from NJDG's age profile).`,
            { ...options(`Pending cases older than ${years} years`, `Share of ${subgroup || 'court'} pending cases aged ${years}+ years, by State/UT`), suffix: '%', frequency: 'Snapshot' });
        });
      }
    };
    // Per-State series with one dataset per measure and years as labels (e.g. institutions vs disposals).
    const deriveJurisdictionFrames = (rows, measure, heading, subgroup, options) => {
      if (!/institutions and disposals/i.test(measure)) return;
      const first = rows[0];
      const stem = `map__jur__${slug(first.item.meta?.category)}__${slug(measure)}`;
      const byYear = new Map();
      rows.forEach(({ state, item }) => {
        const find = pattern => (item.datasets || []).find(dataset => pattern.test(String(dataset.label)));
        const instituted = find(/instit/i);
        const disposed = find(/dispos/i);
        if (!instituted || !disposed) return;
        (item.labels || []).forEach((label, index) => {
          const year = yearOf(label);
          if (year === null) return;
          const entry = byYear.get(year) || { instituted: new Map(), disposed: new Map(), rate: new Map(), net: new Map() };
          byYear.set(year, entry);
          const a = (instituted.values || instituted.data || [])[index];
          const b = (disposed.values || disposed.data || [])[index];
          if (finite(a)) entry.instituted.set(state, Number(a));
          if (finite(b)) entry.disposed.set(state, Number(b));
          if (finite(a) && finite(b)) {
            entry.net.set(state, Number(a) - Number(b));
            if (Number(a) > 0) entry.rate.set(state, Math.round((Number(b) / Number(a)) * 1000) / 10);
          }
        });
      });
      const years = [...byYear.keys()].sort((left, right) => right - left);
      const families = [
        ['instituted', 'Cases instituted each year', 'Cases instituted per year, by State/UT', undefined, 'Annual'],
        ['disposed', 'Cases disposed each year', 'Cases disposed per year, by State/UT', undefined, 'Annual'],
        ['rate', 'Disposal rate (disposed ÷ instituted)', 'Cases disposed as a share of cases instituted in the same year; above 100% means the backlog shrank', '%', 'Annual'],
        ['net', 'Net change in case backlog (instituted − disposed)', 'Cases instituted minus cases disposed each year; positive means the backlog grew', undefined, 'Annual'],
      ];
      families.forEach(([id, title, subtitle, suffix, frequency]) => {
        const frames = years.map(year => ({ label: String(year), points: byYear.get(year)[id] })).filter(frame => frame.points.size >= MIN_STATES);
        if (frames.length > 1) {
          add(`${stem}__${id}_by_year`, first.key, first.item, frames[0].points, '', `The latest year (${frames[0].label}) covers only the months published so far.`,
            { ...options(title, subtitle), frames, suffix, frequency });
        }
      });
    };

    const totals = new Set();
    jurisdictions.forEach(({ measure, subgroup, rows: allRows }) => {
      const heading = measure.charAt(0).toUpperCase() + measure.slice(1);
      const options = (title, subtitle) => ({ title, subtitle, theme: subgroup || undefined, sourceSubgroup: subgroup });
      const byLabel = new Map();
      const total = new Map();
      const rows = allRows.filter(({ item }) => item.values?.length);
      if (rows.length) {
        derivePerJurisdictionMaps(allRows, rows, measure, heading, subgroup, options);
      } else {
        deriveJurisdictionFrames(allRows, measure, heading, subgroup, options);
        return;
      }
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
    // Maps computed only from series already published on the dashboard (no new data sources are fetched).
    const pointsOf = (key, datasetIndex) => {
      const item = series?.[key];
      if (!item || item.error || item.chartType === 'map') return new Map();
      if (datasetIndex === undefined) return item.values?.length ? statePoints(item.labels || [], item.values) : new Map();
      const dataset = item.datasets?.[datasetIndex];
      return dataset ? statePoints(item.labels || [], dataset.values || dataset.data || []) : new Map();
    };
    const titleOf = key => lookup(key)?.title || series?.[key]?.meta?.title || key;
    const citation = keys => [...new Set(keys.map(key => series?.[key]?.source).filter(Boolean))].join('; ');
    const round = (value, digits = 1) => Math.round(value * 10 ** digits) / 10 ** digits;
    const addDerived = (id, keys, points, title, subtitle, how, options = {}) => add(`map__derived__${id}`, keys[0],
      { source: citation(keys), unit: '', note: '', meta: { title } }, points, '',
      `${how} Computed only from series already on this dashboard (${keys.map(titleOf).join('; ')}); no new data was fetched.`,
      { title, subtitle, derived: true, frequency: 'Derived cross-section', ...options });
    const combine = (left, right, fn) => {
      const points = new Map();
      left.forEach((a, state) => {
        if (!right.has(state)) return;
        const value = fn(a, right.get(state));
        if (Number.isFinite(value)) points.set(state, value);
      });
      return points;
    };
    // [id, numerator key, denominator key, scale, suffix, title, subtitle, how it is computed]
    [
      ['rrb-branch-share', 'rbi_state_rrb_branches', 'rbi_state_bank_offices', 100, '%', 'Regional Rural Bank branches as a share of all bank offices', 'RRB branches ÷ scheduled commercial bank offices, by State/UT', 'Regional Rural Bank branches divided by all scheduled commercial bank offices, times 100.'],
      ['agri-credit-share', 'rbi_state_agri_credit', 'rbi_state_bank_credit', 1, '%', 'Agricultural credit as a share of bank credit', 'Credit to agriculture ÷ total bank credit, by State/UT', 'Credit to agriculture (INR thousand crore) divided by total bank credit (INR lakh crore), converted to a percentage.'],
      ['industry-credit-share', 'rbi_state_industry_credit', 'rbi_state_bank_credit', 1, '%', 'Industrial credit as a share of bank credit', 'Credit to industry ÷ total bank credit, by State/UT', 'Credit to industry (INR thousand crore) divided by total bank credit (INR lakh crore), converted to a percentage.'],
      ['personal-loans-share', 'rbi_state_personal_loans', 'rbi_state_bank_credit', 1, '%', 'Personal loans as a share of bank credit', 'Personal loans ÷ total bank credit, by State/UT', 'Personal loans (INR thousand crore) divided by total bank credit (INR lakh crore), converted to a percentage.'],
      ['beds-per-hospital', 'rbi_state_government_beds', 'rbi_state_government_hospitals', 1, ' beds per hospital', 'Beds per government hospital', 'Government hospital beds ÷ government hospitals, by State/UT', 'Government hospital beds divided by the number of government hospitals.'],
      ['workers-per-factory', 'rbi_state_factory_workers', 'state_operating_factories', 100000, ' workers per factory', 'Workers per factory', 'ASI factory workers ÷ registered factories, by State/UT', 'Factory workers (lakh, converted to persons) divided by registered factories in the Annual Survey of Industries.'],
      ['intl-air-share', 'air_state_intl_passengers', 'air_state_passengers', 100, '%', 'International share of air passengers', 'International ÷ total airport passengers, by State', 'International passengers divided by total passengers at the State\'s airports, times 100.'],
    ].forEach(([id, num, den, scale, suffix, title, subtitle, how]) => {
      const points = combine(pointsOf(num), pointsOf(den), (a, b) => (b ? round((a / b) * scale, 2) : NaN));
      addDerived(id, [num, den], points, title, subtitle, how, { suffix });
    });
    // [id, key, dataset index of A, dataset index of B, suffix, title, subtitle, how] with value = B - A.
    [
      ['mpi-reduction', 'rbi_state_mpi_change', 1, 0, ' pts', 'Fall in multidimensional poverty, NFHS-4 to NFHS-5', 'Headcount ratio NFHS-4 minus NFHS-5 (percentage points), by State/UT', 'Multidimensional poverty headcount in NFHS-4 minus the headcount in NFHS-5; positive means poverty fell.'],
      ['life-expectancy-gap', 'rbi_state_life_expectancy_gender', 0, 1, ' years', 'Female life-expectancy advantage', 'Female minus male life expectancy (years), by State/UT', 'Female life expectancy minus male life expectancy.'],
      ['secondary-ger-gap', 'rbi_state_ger_secondary_gender', 0, 1, ' pts', 'Girls\' secondary enrolment gap', 'Girls\' minus boys\' secondary gross enrolment ratio (points), by State/UT', 'Girls\' gross enrolment ratio minus boys\' for secondary school; positive means girls enrol more.'],
    ].forEach(([id, key, indexA, indexB, suffix, title, subtitle, how]) => {
      const points = combine(pointsOf(key, indexA), pointsOf(key, indexB), (a, b) => round(b - a, 2));
      addDerived(id, [key], points, title, subtitle, how, { suffix });
    });
    {
      const key = 'rbi_state_mpi_change';
      const frames = (series?.[key]?.datasets || []).map((dataset, index) => ({ label: String(dataset.label || `Series ${index + 1}`), points: pointsOf(key, index) })).reverse();
      if (frames.length > 1) {
        addDerived('mpi-nfhs-periods', [key], frames[0].points, 'Multidimensional poverty headcount, NFHS-4 vs NFHS-5', 'Share of people multidimensionally poor, by State/UT and survey round',
          'Both survey rounds on one map.', { frames, frequency: 'Two survey rounds', suffix: '%' });
      }
    }
    // Equal-weight composite: each indicator becomes a 0-100 percentile among the States/UTs that report it
    // (direction -1 flips it so higher is always better), then the available percentiles are averaged.
    const composite = (parts, minParts) => {
      const ranked = parts.map(([key, direction]) => {
        const points = pointsOf(key);
        const sorted = [...points.values()].sort((a, b) => a - b);
        return { points, sorted, direction };
      }).filter(part => part.sorted.length >= MIN_STATES);
      const scores = new Map();
      STATES.forEach(state => {
        const percentiles = ranked.filter(part => part.points.has(state)).map(({ points, sorted, direction }) => {
          const value = points.get(state);
          const below = sorted.filter(other => other < value).length;
          const equal = sorted.filter(other => other === value).length;
          const share = sorted.length > 1 ? ((below + (equal - 1) / 2) / (sorted.length - 1)) * 100 : 50;
          return direction > 0 ? share : 100 - share;
        });
        if (percentiles.length >= minParts) scores.set(state, round(percentiles.reduce((sum, value) => sum + value, 0) / percentiles.length));
      });
      return scores;
    };
    // [id, title, subtitle, minimum indicators, [series key, direction]...]
    [
      ['health-outcomes-score', 'Health outcomes score', 'Equal-weight 0–100 rank score: infant mortality, life expectancy, maternal mortality, child anaemia', 3,
        [['state_infant_mortality_rate', -1], ['state_life_expectancy', 1], ['rbi_state_maternal_mortality', -1], ['rbi_state_child_anaemia', -1]]],
      ['development-score', 'Human development score', 'Equal-weight 0–100 rank score: poverty, per-capita NSDP, unemployment, secondary enrolment', 4,
        [['rbi_state_mpi_headcount', -1], ['rbi_state_per_capita_nsdp', 1], ['rbi_state_urban_unemployment', -1], ['rbi_state_rural_unemployment', -1], ['rbi_state_ger_secondary', 1]]],
      ['banking-depth-score', 'Banking depth score', 'Equal-weight 0–100 rank score: credit per office, deposits per office, credit-deposit ratio', 3,
        [['rbi_state_credit_per_office', 1], ['rbi_state_deposits_per_office', 1], ['rbi_state_credit_deposit_ratio', 1]]],
      ['fiscal-health-score', 'State fiscal health score', 'Equal-weight 0–100 rank score: own-tax revenue and fiscal deficit relative to GSDP, health share of spending', 3,
        [['rbi_state_own_tax_gsdp', 1], ['rbi_state_fiscal_deficit_gsdp', -1], ['rbi_state_health_spend_share', 1]]],
      ['education-access-score', 'Education access score', 'Equal-weight 0–100 rank score: middle, secondary and higher-education gross enrolment ratios', 3,
        [['rbi_state_ger_middle', 1], ['rbi_state_ger_secondary', 1], ['aishe_ger_states', 1]]],
    ].forEach(([id, title, subtitle, minParts, parts]) => {
      addDerived(id, parts.map(([key]) => key), composite(parts, minParts), title, subtitle,
        `Each indicator is turned into a 0–100 percentile among the States/UTs that report it (100 = best), and a State/UT's score is the average of at least ${minParts} available percentiles. Higher is better; it ranks States/UTs against each other and is not an official index.`,
        { suffix: ' / 100', frequency: 'Derived score' });
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
        desc: `Every ${theme} statistic with State/UT values, drawn as a map of India. Darker shading means a higher value; hover, tap or press Enter on a State/UT for its figure, rank and trend; play through years where the data has them.`,
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
  const NBINS = 5;
  const median = list => {
    const sorted = [...list].sort((a, b) => a - b);
    const mid = Math.floor(sorted.length / 2);
    return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
  };
  const binEdges = (values, scale) => {
    const sorted = [...values].sort((a, b) => a - b);
    const min = sorted[0];
    const max = sorted[sorted.length - 1];
    return Array.from({ length: NBINS - 1 }, (_, i) => (scale === 'linear'
      ? min + ((i + 1) * (max - min)) / NBINS
      : sorted[Math.min(sorted.length - 1, Math.floor(((i + 1) * sorted.length) / NBINS))]));
  };
  const binOf = (value, edges) => edges.reduce((count, edge) => count + (value >= edge ? 1 : 0), 0);
  const binFill = bin => `color-mix(in oklab, var(--map-high) ${Math.round(15 + (bin * 85) / (NBINS - 1))}%, var(--map-low))`;
  // Frames are the periods of a map: one per dataset. Year-labelled periods are ordered oldest to newest.
  const buildFrames = (labels, values, datasets) => {
    const sets = Array.isArray(datasets) && datasets.length > 1 ? datasets : [{ label: '', values }];
    let frames = sets.map(set => ({ label: String(set.label ?? ''), points: statePoints(labels, set.values || []) })).filter(frame => frame.points.size);
    const years = frames.map(frame => (frame.label.match(/\b(19|20)\d{2}\b/) || [])[0]);
    const timeline = frames.length > 1 && years.every(Boolean);
    if (timeline) frames = frames.map((frame, i) => ({ ...frame, year: Number(years[i]) })).sort((a, b) => a.year - b.year);
    return { frames, timeline };
  };
  const STYLE_ID = 'india-maps-style';
  const ensureStyles = () => {
    if (typeof document === 'undefined' || document.getElementById(STYLE_ID)) return;
    const script = document.currentScript || document.querySelector('script[src*="india-maps.js"]');
    const href = script?.src ? script.src.replace(/india-maps\.js[^/]*$/, 'india-maps.css') : 'india-maps.css';
    const link = document.createElement('link');
    link.id = STYLE_ID;
    link.rel = 'stylesheet';
    link.href = `${href.split('?')[0]}?v=${ART_VERSION}`;
    document.head.append(link);
  };
  ensureStyles();

  const readHash = () => new URLSearchParams(String(location.hash || '').replace(/^#/, ''));

  // Draws an interactive SVG choropleth into `container`; colours come from the --map-* CSS variables so themes apply.
  const render = async (container, { labels = [], values = [], datasets = null, id = '', title = 'Map', suffix = '', format = value => String(value) }) => {
    ensureStyles();
    const { frames, timeline } = buildFrames(labels, values, datasets);
    const figure = document.createElement('figure');
    figure.className = 'india-map';
    figure.innerHTML = '<p class="india-map-status">Drawing map…</p>';
    container.append(figure);
    if (!frames.length) {
      figure.innerHTML = '<p class="india-map-status">No State/UT values to draw.</p>';
      return figure;
    }
    let geometry;
    try {
      geometry = await loadGeometry();
    } catch (error) {
      figure.innerHTML = `<p class="india-map-status">${escape(error.message)}</p>`;
      return figure;
    }
    const mapId = id || slug(title);
    const pooled = frames.flatMap(frame => [...frame.points.values()]);
    const state = { f: timeline ? frames.length - 1 : 0, scale: 'quantile', sort: 'rank', pin: null, hover: null, q: '', bins: new Set(), timer: null };
    const hash = readHash();
    if (hash.get('map') === mapId) {
      const f = hash.has('f') ? Number(hash.get('f')) : NaN;
      if (Number.isInteger(f) && f >= 0 && f < frames.length) state.f = f;
      if (hash.get('s') === 'linear') state.scale = 'linear';
      if (['rank', 'asc', 'name'].includes(hash.get('o'))) state.sort = hash.get('o');
      if (geometry.states[hash.get('st')]) state.pin = hash.get('st');
      state.q = hash.get('q') || '';
      (hash.get('b') || '').split(',').forEach(b => { if (/^[0-4]$/.test(b)) state.bins.add(Number(b)); });
    }
    const names = Object.keys(geometry.states);
    const shapes = names.map(name => `<path d="${geometry.states[name]}" data-state="${escape(name)}" tabindex="-1" role="button" aria-pressed="false"></path>`).join('');
    const summary = `${title}: interactive map of India by State/UT. Use Tab or arrow keys to move between States/UTs, Enter to pin a detail panel.`;
    figure.innerHTML = `<div class="india-map-ui india-map-toolbar">`
      + `<label class="india-map-search"><span class="sr-only">Find a State or UT</span><input type="search" placeholder="Find a State/UT…" autocomplete="off" value="${escape(state.q)}"></label>`
      + `<div class="india-map-switch" role="group" aria-label="Colour scale"><button type="button" data-scale="quantile">Quantile</button><button type="button" data-scale="linear">Linear</button></div>`
      + `<button type="button" class="india-map-share">Copy link</button></div>`
      + `<div class="india-map-main"><div class="india-map-stage"><svg viewBox="${geometry.viewBox}" role="group" aria-label="${escape(summary)}" preserveAspectRatio="xMidYMid meet">${shapes}</svg><div class="india-map-tip" role="tooltip" hidden></div></div>`
      + `<aside class="india-map-ui india-map-side"><div class="india-map-detail" aria-live="polite"></div>`
      + `<div class="india-map-sortbar" role="group" aria-label="Sort ranking"><button type="button" data-sort="rank">High → low</button><button type="button" data-sort="asc">Low → high</button><button type="button" data-sort="name">A–Z</button></div>`
      + `<ol class="india-map-list"></ol></aside></div>`
      + `<div class="india-map-ui india-map-timebar" hidden><button type="button" class="india-map-play" aria-label="Play through periods">▶</button><input type="range" min="0" max="${frames.length - 1}" step="1" aria-label="Period"><output></output></div>`
      + `<figcaption class="india-map-legend"><span class="india-map-readout" aria-live="polite"></span><span class="india-map-bins india-map-ui" role="group" aria-label="Legend: click a band to highlight its States/UTs"></span>`
      + `<span class="india-map-credit">Boundaries: <a href="${escape(geometry.sourceUrl)}" target="_blank" rel="noreferrer">DataMeet</a> (${escape(geometry.license)})</span></figcaption>`;
    if (window.IJScripture) figure.insertAdjacentHTML('beforeend', window.IJScripture.verseHtml(window.IJScripture.pickVerse(`map:${id || title}`, 'India in Maps'), 'compact'));
    const $ = selector => figure.querySelector(selector);
    const paths = new Map([...figure.querySelectorAll('path[data-state]')].map(path => [path.dataset.state, path]));
    const tip = $('.india-map-tip');
    const stage = $('.india-map-stage');
    const readout = $('.india-map-readout');
    const slider = $('.india-map-timebar input');
    const timebar = $('.india-map-timebar');
    const playBtn = $('.india-map-play');
    if (frames.length > 1) timebar.hidden = false;
    const fmt = value => format(value, suffix);
    let cache = {};

    const compute = () => {
      const frame = frames[state.f];
      const entries = [...frame.points.entries()].sort((a, b) => b[1] - a[1]);
      const rank = new Map(entries.map(([name], i) => [name, i + 1]));
      const nums = entries.map(([, value]) => value);
      const edges = binEdges(pooled, state.scale);
      cache = { frame, entries, rank, edges, mean: nums.reduce((a, b) => a + b, 0) / nums.length, median: median(nums) };
    };
    const matches = name => !state.q || name.toLowerCase().includes(state.q.toLowerCase());
    const highlighting = () => state.bins.size > 0 || state.q !== '';
    const passes = (name, value) => value !== undefined && matches(name) && (!state.bins.size || state.bins.has(binOf(value, cache.edges)));

    const sparkline = name => {
      if (!timeline) return '';
      const series = frames.map(frame => frame.points.get(name));
      const known = series.filter(value => value !== undefined);
      if (known.length < 2) return '';
      const lo = Math.min(...known);
      const hi = Math.max(...known);
      const x = i => (i / (frames.length - 1)) * 120 + 4;
      const y = value => (hi === lo ? 15 : 30 - ((value - lo) / (hi - lo)) * 26 - 2);
      const pts = series.map((value, i) => (value === undefined ? null : `${x(i).toFixed(1)},${y(value).toFixed(1)}`)).filter(Boolean).join(' ');
      return `<svg class="india-map-spark" viewBox="0 0 128 32" role="img" aria-label="${escape(`${name} over ${frames[0].label} to ${frames[frames.length - 1].label}`)}"><polyline points="${pts}"/><circle cx="${x(state.f).toFixed(1)}" cy="${y(frames[state.f].points.get(name) ?? lo).toFixed(1)}" r="3"/></svg><small>${escape(frames[0].label)} – ${escape(frames[frames.length - 1].label)}</small>`;
    };
    const describe = name => {
      const value = cache.frame.points.get(name);
      return value === undefined ? `${name}: not reported` : `${name}: ${fmt(value)} · rank ${cache.rank.get(name)} of ${cache.entries.length}`;
    };

    const paintMap = () => {
      paths.forEach((path, name) => {
        const value = cache.frame.points.get(name);
        const has = value !== undefined;
        path.style.fill = has ? binFill(binOf(value, cache.edges)) : 'var(--map-empty)';
        path.classList.toggle('has-value', has);
        path.classList.toggle('no-value', !has);
        path.classList.toggle('is-dim', highlighting() && !passes(name, value));
        path.classList.toggle('is-pinned', state.pin === name);
        path.classList.toggle('is-hover', state.hover === name);
        path.setAttribute('aria-pressed', String(state.pin === name));
        path.setAttribute('aria-label', describe(name));
        path.tabIndex = has ? 0 : -1;
      });
      const pinned = paths.get(state.pin);
      if (pinned) pinned.parentNode.append(pinned);
    };
    const paintBins = () => {
      const bounds = [Math.min(...pooled), ...cache.edges, Math.max(...pooled)];
      $('.india-map-bins').innerHTML = Array.from({ length: NBINS }, (_, i) => {
        const count = cache.entries.filter(([, value]) => binOf(value, cache.edges) === i).length;
        return `<button type="button" data-bin="${i}" aria-pressed="${state.bins.has(i)}" title="${count} States/UTs"><i style="background:${binFill(i)}"></i>${escape(fmt(bounds[i]))} – ${escape(fmt(bounds[i + 1]))}</button>`;
      }).join('') + (state.bins.size ? '<button type="button" data-bin="clear" class="india-map-clear">Clear</button>' : '');
    };
    const paintList = () => {
      let rows = cache.entries.filter(([name]) => matches(name));
      if (state.sort === 'asc') rows = [...rows].reverse();
      if (state.sort === 'name') rows = [...rows].sort((a, b) => a[0].localeCompare(b[0]));
      const max = Math.max(...pooled.map(Math.abs)) || 1;
      $('.india-map-list').innerHTML = rows.map(([name, value]) => {
        const dim = state.bins.size && !passes(name, value);
        return `<li><button type="button" data-row="${escape(name)}" class="${dim ? 'is-dim' : ''}${state.pin === name ? ' is-pinned' : ''}" aria-pressed="${state.pin === name}"><span class="rk">${cache.rank.get(name)}</span><span class="nm">${escape(name)}</span><span class="bar" aria-hidden="true"><i style="width:${Math.max(2, (Math.abs(value) / max) * 100)}%;background:${binFill(binOf(value, cache.edges))}"></i></span><span class="vl">${escape(fmt(value))}</span></button></li>`;
      }).join('') || '<li class="india-map-empty">No State/UT matches.</li>';
      figure.querySelectorAll('.india-map-sortbar button').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.sort === state.sort)));
      figure.querySelectorAll('.india-map-switch button').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.scale === state.scale)));
    };
    const paintDetail = () => {
      const box = $('.india-map-detail');
      const name = state.pin;
      if (!name) {
        box.innerHTML = '<p class="india-map-hint">Hover for a quick look. Click a State/UT (or press Enter) to pin its details here.</p>';
        return;
      }
      const value = cache.frame.points.get(name);
      const diff = value === undefined ? '' : value - cache.median;
      box.innerHTML = `<div class="india-map-detail-head"><strong>${escape(name)}</strong><button type="button" class="india-map-unpin" aria-label="Unpin ${escape(name)}">×</button></div>`
        + (value === undefined ? '<p>Not reported by the source.</p>'
          : `<p class="big">${escape(fmt(value))}</p><dl><dt>Rank</dt><dd>${cache.rank.get(name)} of ${cache.entries.length}</dd><dt>National average</dt><dd>${escape(fmt(cache.mean))}</dd><dt>Median</dt><dd>${escape(fmt(cache.median))}</dd><dt>vs median</dt><dd>${diff >= 0 ? '+' : '−'}${escape(fmt(Math.abs(diff)))}</dd></dl>`)
        + sparkline(name)
        + (frames.length > 1 ? `<small class="india-map-period">${escape(cache.frame.label)}</small>` : '');
    };
    const paintTime = () => {
      slider.value = String(state.f);
      timebar.querySelector('output').textContent = cache.frame.label;
      slider.setAttribute('aria-valuetext', cache.frame.label);
      playBtn.textContent = state.timer ? '⏸' : '▶';
      playBtn.setAttribute('aria-label', state.timer ? 'Pause' : 'Play through periods');
    };
    const paintReadout = () => {
      const [topName, topValue] = cache.entries[0];
      readout.textContent = state.hover ? describe(state.hover) : `Highest: ${topName} · ${fmt(topValue)}`;
    };
    const persist = () => {
      if (figure.closest('#charts > .chart-card') || !figure.isConnected) return;
      const params = new URLSearchParams({ map: mapId, f: String(state.f), s: state.scale, o: state.sort });
      if (state.pin) params.set('st', state.pin);
      if (state.q) params.set('q', state.q);
      if (state.bins.size) params.set('b', [...state.bins].sort().join(','));
      history.replaceState(null, '', `#${params}`);
    };
    const paint = (save = true) => {
      compute();
      paintMap();
      paintBins();
      paintList();
      paintDetail();
      paintTime();
      paintReadout();
      if (save) persist();
    };
    const lightPaint = () => { paintMap(); paintList(); paintReadout(); };

    const showTip = (name, event) => {
      if (!name) { tip.hidden = true; return; }
      const value = cache.frame.points.get(name);
      tip.innerHTML = `<strong>${escape(name)}</strong>` + (value === undefined ? '<span>Not reported</span>'
        : `<span>${escape(fmt(value))}</span><small>Rank ${cache.rank.get(name)} of ${cache.entries.length} · ${value >= cache.median ? 'above' : 'below'} median</small>`);
      tip.hidden = false;
      const box = stage.getBoundingClientRect();
      let x;
      let y;
      if (event && event.clientX !== undefined && (event.clientX || event.clientY)) {
        x = event.clientX - box.left;
        y = event.clientY - box.top;
      } else {
        const rect = paths.get(name).getBoundingClientRect();
        x = rect.left + rect.width / 2 - box.left;
        y = rect.top + rect.height / 2 - box.top;
      }
      tip.style.left = `${Math.min(Math.max(x + 12, 0), Math.max(0, box.width - tip.offsetWidth - 4))}px`;
      tip.style.top = `${Math.min(Math.max(y + 12, 0), Math.max(0, box.height - tip.offsetHeight - 4))}px`;
    };
    const setHover = (name, event) => {
      if (state.hover !== name) {
        state.hover = name;
        figure.querySelectorAll('.india-map-list button.is-hover').forEach(button => button.classList.remove('is-hover'));
        paths.forEach((path, key) => path.classList.toggle('is-hover', key === name));
        const row = name && [...figure.querySelectorAll('.india-map-list button')].find(button => button.dataset.row === name);
        if (row) row.classList.add('is-hover');
        paintReadout();
      }
      showTip(name, event);
    };
    const pin = name => {
      state.pin = state.pin === name ? null : name;
      paint();
    };
    const stop = () => {
      if (state.timer) clearInterval(state.timer);
      state.timer = null;
    };
    const setFrame = f => {
      state.f = f;
      paint();
    };

    const svg = $('svg');
    svg.addEventListener('pointermove', event => {
      const path = event.target.closest('path[data-state]');
      setHover(path ? path.dataset.state : null, event);
    });
    svg.addEventListener('pointerleave', () => setHover(null));
    svg.addEventListener('focusin', event => {
      const path = event.target.closest('path[data-state]');
      if (path) setHover(path.dataset.state);
    });
    svg.addEventListener('focusout', () => setHover(null));
    svg.addEventListener('click', event => {
      const path = event.target.closest('path[data-state]');
      if (path && path.classList.contains('has-value')) pin(path.dataset.state);
    });
    svg.addEventListener('keydown', event => {
      const path = event.target.closest('path[data-state]');
      if (!path) return;
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        if (path.classList.contains('has-value')) pin(path.dataset.state);
        return;
      }
      const dir = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] }[event.key];
      if (!dir) return;
      event.preventDefault();
      const centre = node => { const b = node.getBBox(); return [b.x + b.width / 2, b.y + b.height / 2]; };
      const [cx, cy] = centre(path);
      let best = null;
      let bestScore = Infinity;
      paths.forEach((other, name) => {
        if (other === path || !other.classList.contains('has-value')) return;
        const [ox, oy] = centre(other);
        const dx = ox - cx;
        const dy = oy - cy;
        const along = dx * dir[0] + dy * dir[1];
        if (along <= 0) return;
        const score = Math.hypot(dx, dy) + Math.abs(dir[0] ? dy : dx);
        if (score < bestScore) { best = other; bestScore = score; }
      });
      if (best) best.focus();
    });
    const list = $('.india-map-list');
    list.addEventListener('pointerover', event => {
      const row = event.target.closest('button[data-row]');
      setHover(row ? row.dataset.row : null);
    });
    list.addEventListener('pointerleave', () => setHover(null));
    list.addEventListener('focusin', event => {
      const row = event.target.closest('button[data-row]');
      if (row) setHover(row.dataset.row);
    });
    list.addEventListener('click', event => {
      const row = event.target.closest('button[data-row]');
      if (row) pin(row.dataset.row);
    });
    figure.addEventListener('click', event => {
      const button = event.target.closest('button');
      if (!button || !figure.contains(button)) return;
      if (button.dataset.sort) { state.sort = button.dataset.sort; paint(); }
      else if (button.dataset.scale) { state.scale = button.dataset.scale; paint(); }
      else if (button.dataset.bin !== undefined) {
        if (button.dataset.bin === 'clear') state.bins.clear();
        else {
          const bin = Number(button.dataset.bin);
          if (state.bins.has(bin)) state.bins.delete(bin); else state.bins.add(bin);
        }
        paint();
      } else if (button.classList.contains('india-map-unpin')) { state.pin = null; paint(); }
      else if (button.classList.contains('india-map-play')) {
        if (state.timer) { stop(); paintTime(); return; }
        if (state.f >= frames.length - 1) state.f = 0;
        state.timer = setInterval(() => {
          if (!figure.isConnected) { stop(); return; }
          if (state.f >= frames.length - 1) { stop(); paint(); return; }
          setFrame(state.f + 1);
        }, 1100);
        paint();
      } else if (button.classList.contains('india-map-share')) {
        persist();
        const url = location.href;
        const done = () => { button.textContent = 'Link copied'; setTimeout(() => { button.textContent = 'Copy link'; }, 1600); };
        (navigator.clipboard ? navigator.clipboard.writeText(url) : Promise.reject(new Error('no clipboard'))).then(done, () => { window.prompt('Copy this link', url); });
      }
    });
    slider.addEventListener('input', () => { stop(); setFrame(Number(slider.value)); });
    const input = $('.india-map-search input');
    input.addEventListener('input', () => { state.q = input.value.trim(); paint(); });
    input.addEventListener('keydown', event => {
      if (event.key === 'Enter') {
        const first = cache.entries.find(([name]) => matches(name));
        if (first) { state.pin = first[0]; paint(); }
      }
    });
    figure.addEventListener('keydown', event => {
      if (event.key === 'Escape' && state.pin) { state.pin = null; paint(); event.stopPropagation(); }
    });

    paint(false);
    return figure;
  };

  // Opens the card for a shared `#map=<id>` link so permalinks land on the right chart.
  const openFromHash = scope => {
    const id = readHash().get('map');
    const card = id && [...(scope || document).querySelectorAll('.chart-card[data-key]')].find(node => node.dataset.key === id);
    const button = card && card.querySelector('.expand-chart-btn');
    if (button) button.click();
  };

  root.IndiaMaps = { GROUP, MIN_STATES, STATES, canonicalState, slug, subgroupFor, artFor, deriveMapSeries, decorate, render, loadGeometry, openFromHash };
})(typeof window !== 'undefined' ? window : globalThis);
