/* Static Compare page: mirrors the web app's /compare (up to four indicators, optional rebase to 100). */
(() => {
  const store = window.IndiaCompare;
  const MAX = store?.MAX || 4;
  const PALETTE = store?.PALETTE || ['#ff9933', '#58a6ff', '#3fb950', '#bc8cff'];
  const $ = selector => document.querySelector(selector);
  const searchInput = $('#compare-search');
  const resultsList = $('#compare-results');
  const pills = $('#compare-pills');
  const missingNote = $('#compare-missing');
  const emptyNote = $('#compare-empty');
  const card = $('#compare-card');
  const normaliseInput = $('#compare-normalise');
  const unitsNote = $('#compare-units-note');
  const tableBody = $('#compare-table');
  const actions = $('#compare-actions');
  const countNote = $('#compare-count');
  const copyButton = $('#compare-copy');
  $('#compare-clear').addEventListener('click', () => store?.clear());
  copyButton.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      copyButton.textContent = '✓ Link copied';
      setTimeout(() => { copyButton.textContent = 'Copy link'; }, 1800);
    } catch {
      // Clipboard can be blocked (file:// or insecure context); the address bar still holds the URL.
    }
  });
  const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));

  const formatIndian = value => {
    const abs = Math.abs(value);
    if (abs >= 1e7) return `${(value / 1e7).toLocaleString('en-IN', { maximumFractionDigits: 2 })} crore`;
    if (abs >= 1e5) return `${(value / 1e5).toLocaleString('en-IN', { maximumFractionDigits: 2 })} lakh`;
    return value.toLocaleString('en-IN', { maximumFractionDigits: abs < 10 ? 2 : 1 });
  };
  const formatValue = (value, suffix = '') => {
    if (value === null || value === undefined || !Number.isFinite(Number(value))) return '—';
    const number = Number(value);
    const trimmed = String(suffix || '').trim();
    if (/US\$|USD|\$/.test(trimmed)) {
      const abs = Math.abs(number);
      const scaled = abs >= 1e12 ? `${(number / 1e12).toFixed(2)} trillion` : abs >= 1e9 ? `${(number / 1e9).toFixed(2)} billion` : abs >= 1e6 ? `${(number / 1e6).toFixed(2)} million` : number.toLocaleString('en-US', { maximumFractionDigits: 2 });
      return `${scaled} ${trimmed}`.trim();
    }
    if (trimmed === '%') return `${number.toLocaleString('en-IN', { maximumFractionDigits: 2 })}%`;
    return `${formatIndian(number)}${trimmed ? ` ${trimmed}` : ''}`;
  };
  // Rebases each series to 100 at its first available non-zero value so different units share one axis.
  const normalise = values => {
    const base = values.find(value => value !== null && value !== undefined && Number(value) !== 0);
    if (base === undefined) return values.map(() => null);
    return values.map(value => (value === null || value === undefined ? null : (Number(value) / Number(base)) * 100));
  };
  const labelSortKey = label => {
    const match = String(label).match(/(\d{4})(?:\D+(\d{1,2}))?/);
    return match ? Number(match[1]) * 100 + Number(match[2] || 0) : Number.POSITIVE_INFINITY;
  };

  let indicators = [];
  let byKey = new Map();
  let chart = null;
  const params = new URLSearchParams(window.location.search);
  let normalised = params.get('normalise') === '1';
  normaliseInput.checked = normalised;

  const currentKeys = () => (store ? store.items().map(item => item.key) : []);
  const writeUrl = keys => {
    const next = new URLSearchParams();
    if (keys.length) next.set('keys', keys.join(','));
    if (normalised) next.set('normalise', '1');
    const query = next.toString();
    history.replaceState(null, '', `${window.location.pathname}${query ? `?${query}` : ''}`);
  };

  const comparable = indicator => {
    const series = indicator.series || {};
    return !['state', 'category'].includes(series.scope) && Array.isArray(series.labels) && series.labels.length > 1
      && Array.isArray(series.datasets) && series.datasets.length > 0;
  };

  const render = () => {
    const keys = currentKeys();
    writeUrl(keys);
    const chosen = keys.map(key => byKey.get(key)).filter(Boolean);
    const missing = keys.filter(key => !byKey.has(key));
    missingNote.hidden = !missing.length;
    missingNote.textContent = missing.length ? `Not found: ${missing.join(', ')}` : '';
    pills.innerHTML = chosen.map((item, index) => `<li class="pill" style="--pill:${PALETTE[index % PALETTE.length]}"><a href="explore.html?chart=${encodeURIComponent(item.key)}">${escapeHtml(item.title)}</a><button type="button" data-remove="${escapeHtml(item.key)}" aria-label="Remove ${escapeHtml(item.title)}">×</button></li>`).join('');
    searchInput.disabled = keys.length >= MAX;
    searchInput.placeholder = keys.length >= MAX ? `Maximum of ${MAX} reached` : 'Add an indicator, e.g. inflation';
    actions.hidden = !keys.length;
    countNote.textContent = `${keys.length} of ${MAX} selected`;

    if (!chosen.length) {
      card.hidden = true;
      emptyNote.hidden = false;
      emptyNote.textContent = 'Nothing to compare yet. Search above, or use “+ Compare” on any chart in Explore.';
      chart?.destroy();
      chart = null;
      return;
    }
    emptyNote.hidden = true;
    card.hidden = false;

    const labelSet = new Set();
    chosen.forEach(item => item.series.labels.forEach(label => labelSet.add(String(label))));
    const labels = [...labelSet].sort((left, right) => labelSortKey(left) - labelSortKey(right) || left.localeCompare(right));
    const rows = chosen.map(item => {
      const lookup = new Map(item.series.labels.map((label, index) => [String(label), item.series.datasets[0].values[index]]));
      return { item, values: labels.map(label => (lookup.has(label) ? lookup.get(label) : null)) };
    });
    const mixedUnits = new Set(chosen.map(item => String(item.suffix || '').trim())).size > 1;
    unitsNote.hidden = !(mixedUnits && !normalised);
    const suffix = normalised || mixedUnits ? '' : chosen[0].suffix || '';

    tableBody.innerHTML = rows.map(({ item, values }) => {
      let last = values.length - 1;
      while (last >= 0 && (values[last] === null || values[last] === undefined)) last -= 1;
      const latest = last >= 0 ? `${formatValue(values[last], item.suffix)} (${escapeHtml(labels[last])})` : '—';
      return `<tr><th scope="row"><a href="explore.html?chart=${encodeURIComponent(item.key)}">${escapeHtml(item.title)}</a></th><td>${latest}</td><td>${escapeHtml(item.category)}</td></tr>`;
    }).join('');

    if (!window.Chart) return;
    const datasets = rows.map(({ item, values }, index) => {
      const color = PALETTE[index % PALETTE.length];
      return { label: item.title, data: normalised ? normalise(values) : values, borderColor: color, backgroundColor: `${color}33`, borderWidth: 2, pointRadius: 0, pointHoverRadius: 4, tension: 0.25, spanGaps: true };
    });
    chart?.destroy();
    const colors = window.IndiaTheme?.chartColors() || { legend: '#f5f5f7', muted: '#a1a1a6', grid: 'rgba(255,255,255,.06)' };
    chart = new window.Chart($('#compare-chart'), {
      type: 'line',
      data: { labels, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { labels: { color: colors.legend, boxWidth: 12 } },
          tooltip: { callbacks: { label: context => `${context.dataset.label}: ${normalised ? Number(context.parsed.y).toFixed(1) : formatValue(context.parsed.y, chosen[context.datasetIndex].suffix)}` } },
        },
        scales: {
          x: { ticks: { color: colors.muted, maxRotation: 0, autoSkip: true, maxTicksLimit: 10 }, grid: { color: colors.grid } },
          y: { ticks: { color: colors.muted, callback: value => (normalised ? value : formatValue(value, suffix)) }, grid: { color: colors.grid } },
        },
      },
    });
  };

  const renderResults = () => {
    const query = searchInput.value.trim().toLowerCase();
    if (query.length < 2 || searchInput.disabled) { resultsList.hidden = true; resultsList.innerHTML = ''; return; }
    const taken = new Set(currentKeys());
    const terms = query.split(/\s+/);
    const matches = indicators.filter(item => !taken.has(item.key) && terms.every(term => item.haystack.includes(term))).slice(0, 8);
    resultsList.hidden = false;
    resultsList.innerHTML = matches.length
      ? matches.map(item => `<li role="option" aria-selected="false"><button type="button" data-add="${escapeHtml(item.key)}"><strong>${escapeHtml(item.title)}</strong><small class="muted">${escapeHtml(item.category)} · ${escapeHtml(item.subgroup)}</small></button></li>`).join('')
      : '<li class="muted">No matches</li>';
  };

  searchInput.addEventListener('input', renderResults);
  resultsList.addEventListener('click', event => {
    const button = event.target.closest('[data-add]');
    if (!button) return;
    const item = byKey.get(button.dataset.add);
    if (item && store && !store.has(item.key) && !store.full()) store.toggle({ key: item.key, title: item.title });
    searchInput.value = '';
    renderResults();
  });
  pills.addEventListener('click', event => {
    const button = event.target.closest('[data-remove]');
    if (!button || !store) return;
    store.set(store.items().filter(item => item.key !== button.dataset.remove));
  });
  normaliseInput.addEventListener('change', () => { normalised = normaliseInput.checked; render(); });
  store?.subscribe(render);

  const loadCatalog = () => (Array.isArray(window.INDIA_COMPARE_DATA)
    ? Promise.resolve(window.INDIA_COMPARE_DATA)
    : Promise.reject(new Error('compare-data.js is missing')));
  loadCatalog()
    .then(rows => {
      indicators = rows.map(([key, title, category, subgroup, suffix, labels, values]) => ({
        key, title, category, subgroup, suffix,
        series: { labels, datasets: [{ values }] },
        haystack: `${title} ${category} ${subgroup}`.toLowerCase(),
      })).filter(comparable);
      byKey = new Map(indicators.map(item => [item.key, item]));
      const urlKeys = (params.get('keys') || '').split(',').map(key => key.trim()).filter(Boolean).slice(0, MAX);
      if (urlKeys.length && store) {
        const known = store.items();
        store.set(urlKeys.map(key => known.find(item => item.key === key) || { key, title: byKey.get(key)?.title || key }));
      } else {
        render();
      }
    })
    .catch(error => {
      emptyNote.hidden = false;
      emptyNote.textContent = `Indicators could not be loaded: ${error.message}`;
    });
})();
