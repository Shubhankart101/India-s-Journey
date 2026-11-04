/* Shared chrome for every page: the sticky header, the mobile tab bar and scroll reveals. */
/* Compare selection shared with the web app's behaviour: up to four indicators kept in localStorage. */
window.IndiaCompare = (() => {
  const MAX = 4;
  const KEY = 'ij-compare';
  const listeners = new Set();
  const read = () => {
    try {
      const parsed = JSON.parse(localStorage.getItem(KEY) || '[]');
      return Array.isArray(parsed) ? parsed.filter(item => item && item.key).slice(0, MAX) : [];
    } catch { return []; }
  };
  let items = read();
  const save = () => {
    try { localStorage.setItem(KEY, JSON.stringify(items)); } catch { /* private mode: keep for this visit */ }
    listeners.forEach(listener => listener(items));
  };
  return {
    MAX,
    PALETTE: ['#ff9933', '#58a6ff', '#3fb950', '#bc8cff'],
    items: () => items.slice(),
    slot: key => items.findIndex(item => item.key === key),
    has: key => items.some(item => item.key === key),
    full: () => items.length >= MAX,
    toggle: indicator => {
      if (items.some(item => item.key === indicator.key)) items = items.filter(item => item.key !== indicator.key);
      else if (items.length < MAX) items = [...items, { key: indicator.key, title: indicator.title }];
      save();
    },
    set: next => { items = next.filter(item => item && item.key).slice(0, MAX); save(); },
    clear: () => { items = []; save(); },
    subscribe: listener => { listeners.add(listener); return () => listeners.delete(listener); },
  };
})();

/* Display theme shared with the web app (same localStorage key): dark, light, newspaper or pamphlet. */
window.IndiaTheme = (() => {
  const KEY = 'ij-theme';
  const THEMES = [
    { id: 'dark', label: 'Dark', meta: '#000000' },
    { id: 'light', label: 'Light', meta: '#f5f5f7' },
    { id: 'newspaper', label: 'Newspaper', meta: '#f4f0e6' },
    { id: 'pamphlet', label: 'Pamphlet', meta: '#fff1c1' }
  ];
  const CHART_COLORS = {
    dark: { ink: '#f5f5f7', muted: '#a1a1a6', grid: 'rgba(255, 255, 255, 0.08)', legend: '#d2d2d7', sliceBorder: '#1c1c1e' },
    light: { ink: '#1d1d1f', muted: '#515154', grid: 'rgba(0, 0, 0, 0.08)', legend: '#3a3a3c', sliceBorder: '#ffffff' },
    newspaper: { ink: '#111111', muted: '#3b3b3b', grid: 'rgba(0, 0, 0, 0.12)', legend: '#222222', sliceBorder: '#fbf8f1' },
    pamphlet: { ink: '#1b1b1b', muted: '#2f2f2f', grid: 'rgba(27, 27, 27, 0.14)', legend: '#1b1b1b', sliceBorder: '#1b1b1b' }
  };
  const valid = value => THEMES.some(theme => theme.id === value);
  const read = () => {
    try { const saved = localStorage.getItem(KEY); return valid(saved) ? saved : 'dark'; } catch { return 'dark'; }
  };
  let current = read();
  const apply = () => {
    document.documentElement.dataset.theme = current;
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content', THEMES.find(theme => theme.id === current).meta);
  };
  const chartColors = () => CHART_COLORS[current];
  const restyleCharts = () => {
    if (!window.Chart?.instances) return;
    const colors = chartColors();
    Object.values(window.Chart.instances).forEach(chart => {
      Object.values(chart.options.scales || {}).forEach(scale => {
        if (scale.ticks) scale.ticks.color = colors.muted;
        if (scale.grid && scale.grid.display !== false) scale.grid.color = colors.grid;
      });
      const legendLabels = chart.options.plugins?.legend?.labels;
      if (legendLabels) legendLabels.color = colors.legend;
      chart.update('none');
    });
  };
  apply();
  return {
    THEMES,
    get: () => current,
    chartColors,
    set: theme => {
      if (!valid(theme) || theme === current) return;
      current = theme;
      apply();
      try { localStorage.setItem(KEY, theme); } catch { /* private mode: keep for this visit */ }
      restyleCharts();
    }
  };
})();

(() => {
  const page = document.body.dataset.page || 'home';
  const links = [
    { id: 'home', href: 'index.html', label: 'Home', icon: '⌂' },
    { id: 'explore', href: 'explore.html', label: 'Explore', icon: '◎' },
    { id: 'sources', href: 'sources.html', label: 'Sources', icon: '❡' },
    { id: 'compare', href: 'compare.html', label: 'Compare', icon: '⇄' },
    { id: 'about', href: 'about.html', label: 'About', icon: 'ⓘ' },
    { id: 'api', href: 'api.html', label: 'API', icon: '{ }' }
  ];
  const current = id => (id === page ? ' aria-current="page"' : '');
  const compareCount = () => window.IndiaCompare.items().length;
  const badge = id => (id === 'compare' && compareCount() ? `<span class="nav-badge">${compareCount()}</span>` : '');

  const header = `
  <header class="masthead">
    <a class="brand-mark" href="index.html" aria-label="India's Journey home"><span class="brand-emblem">IJ</span><span>India's Journey<small>The public data atlas</small></span></a>
    <nav class="site-nav" aria-label="Main navigation">
      ${links.map(link => `<a href="${link.href}"${current(link.id)} data-nav="${link.id}">${link.label}${badge(link.id)}</a>`).join('')}
    </nav>
    <a class="nav-cta" href="explore.html">Explore data</a>
    <select class="theme-select" aria-label="Display theme">
      ${window.IndiaTheme.THEMES.map(theme => `<option value="${theme.id}"${theme.id === window.IndiaTheme.get() ? ' selected' : ''}>${theme.label}</option>`).join('')}
    </select>
  </header>`;
  const script = document.currentScript;
  if (script) script.insertAdjacentHTML('beforebegin', header);
  document.querySelector('.masthead .theme-select')?.addEventListener('change', event => window.IndiaTheme.set(event.target.value));

  const renderCompareChrome = () => {
    const count = compareCount();
    document.querySelectorAll('[data-nav="compare"]').forEach(link => {
      link.querySelector('.nav-badge')?.remove();
      if (count) link.insertAdjacentHTML('beforeend', `<span class="nav-badge">${count}</span>`);
    });
    let tray = document.querySelector('.compare-tray');
    if (!count || page === 'compare') { tray?.remove(); return; }
    if (!tray) {
      tray = document.createElement('aside');
      tray.className = 'compare-tray';
      tray.setAttribute('aria-label', 'Compare tray');
      document.body.append(tray);
    }
    const items = window.IndiaCompare.items();
    const keys = items.map(item => encodeURIComponent(item.key)).join(',');
    const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
    const chips = items.map((item, index) => `<li class="tray-chip" style="--slot:${window.IndiaCompare.PALETTE[index % window.IndiaCompare.PALETTE.length]}"><span class="tray-chip-title" title="${esc(item.title)}">${esc(item.title)}</span><button type="button" data-remove="${esc(item.key)}" aria-label="Remove ${esc(item.title)} from compare">×</button></li>`).join('');
    tray.setAttribute('aria-live', 'polite');
    tray.innerHTML = `<span class="tray-count"><span aria-hidden="true">⇄ </span>${count} selected<small> / ${window.IndiaCompare.MAX}</small></span><ul class="tray-chips" aria-label="Selected for comparison">${chips}</ul><a class="tray-btn tray-primary" href="compare.html?keys=${keys}">Compare<span aria-hidden="true"> →</span></a><button type="button" class="tray-btn" data-clear>Clear</button>`;
    tray.querySelector('[data-clear]').addEventListener('click', () => window.IndiaCompare.clear());
    tray.querySelectorAll('[data-remove]').forEach(button => button.addEventListener('click', () => {
      window.IndiaCompare.set(window.IndiaCompare.items().filter(item => item.key !== button.dataset.remove));
    }));
  };
  window.IndiaCompare.subscribe(renderCompareChrome);

  document.addEventListener('DOMContentLoaded', () => {
    const tabs = links.filter(link => !link.desktopOnly)
      .map(link => `<a href="${link.href}"${current(link.id)} data-nav="${link.id}"><span class="tab-icon" aria-hidden="true">${link.icon}</span><span>${link.label}</span></a>`)
      .join('');
    document.body.insertAdjacentHTML('beforeend', `<nav class="tabbar" aria-label="Primary">${tabs}</nav>`);
    renderCompareChrome();

    const targets = document.querySelectorAll('[data-reveal]');
    if (!('IntersectionObserver' in window)) {
      targets.forEach(element => element.classList.add('is-revealed'));
      return;
    }
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-revealed');
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.12 });
    targets.forEach(element => observer.observe(element));
  });
})();

/* Background art controller: paints a scene with a soft swap, and rotates an ambient playlist of
   animated landmark scenes on pages that are not showing a specific group's artwork. */
window.IndiaArt = (() => {
  const ambient = ['red-fort', 'himalaya', 'backwaters', 'isro-launch', 'konark-sun-temple', 'varanasi-ghats',
    'sea-link', 'renewables', 'monsoon-fields', 'toy-train-hills', 'sports', 'trophy', 'athletics', 'multi-sport-games',
    'racket-sports', 'chess-kabaddi', 'cricket-batting', 'football-players', 'hockey-players'].map(name => `assets/${name}.svg`);
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const layer = () => document.querySelector('#era-bg-layer');
  let timer = 0;
  let index = 0;

  const paint = url => {
    const bgLayer = layer();
    if (!bgLayer || !url) return;
    const next = `url("${url}")`;
    if (bgLayer.style.backgroundImage === next) return;
    if (!bgLayer.style.backgroundImage) {
      bgLayer.style.backgroundImage = next;
      return;
    }
    bgLayer.classList.add('is-swapping');
    clearTimeout(bgLayer.swapTimer);
    bgLayer.swapTimer = setTimeout(() => {
      bgLayer.style.backgroundImage = next;
      bgLayer.classList.remove('is-swapping');
    }, 380);
  };
  const stop = () => { clearInterval(timer); timer = 0; };
  const start = () => {
    stop();
    paint(ambient[index]);
    if (reduced) return;
    timer = setInterval(() => {
      if (document.hidden) return;
      index = (index + 1) % ambient.length;
      paint(ambient[index]);
      new Image().src = ambient[(index + 1) % ambient.length];
    }, 9000);
  };
  const isAmbientPage = ['explore', 'about', 'sources', '404'].includes(document.body.dataset.page);
  if (isAmbientPage && layer()) start();
  return { ambient, paint, start, stop, resume: start, isAmbientPage, isRunning: () => Boolean(timer) };
})();

/* Pointer and scroll parallax for the illustrated full-page backdrop. */
(() => {
  const layer = document.querySelector('#era-bg-layer');
  if (!layer || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  let frame = 0;
  let px = 0;
  let py = 0;
  const paint = () => {
    frame = 0;
    layer.style.setProperty('--px', px.toFixed(3));
    layer.style.setProperty('--py', py.toFixed(3));
    layer.style.setProperty('--sy', String(Math.min(window.scrollY, 1500)));
  };
  const schedule = () => { if (!frame) frame = requestAnimationFrame(paint); };
  window.addEventListener('pointermove', event => {
    px = event.clientX / window.innerWidth - 0.5;
    py = event.clientY / window.innerHeight - 0.5;
    schedule();
  }, { passive: true });
  window.addEventListener('scroll', schedule, { passive: true });
})();

/* Interactive layer: scroll progress, glassy header on scroll, typewriter, count-up metrics,
   cursor spotlight on cards, scroll-in reveals for rendered cards, and a back-to-top button. */
(() => {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const ready = fn => (document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', fn) : fn());

  ready(() => {
    const bar = document.createElement('div');
    bar.className = 'scroll-progress';
    bar.setAttribute('aria-hidden', 'true');
    document.body.prepend(bar);
    const top = document.createElement('button');
    top.type = 'button';
    top.className = 'scroll-top';
    top.setAttribute('aria-label', 'Back to top');
    top.tabIndex = -1;
    top.textContent = '\u2191';
    top.addEventListener('click', () => window.scrollTo({ top: 0, behavior: reduced ? 'auto' : 'smooth' }));
    document.body.append(top);
    const masthead = document.querySelector('.masthead');

    let frame = 0;
    const paint = () => {
      frame = 0;
      const max = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.setProperty('--progress', String(max > 0 ? Math.min(window.scrollY / max, 1) : 0));
      masthead?.classList.toggle('is-scrolled', window.scrollY > 12);
      const show = window.scrollY > 500;
      top.classList.toggle('visible', show);
      top.tabIndex = show ? 0 : -1;
    };
    const schedule = () => { if (!frame) frame = requestAnimationFrame(paint); };
    paint();
    window.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('resize', schedule);

    const heroTitle = document.querySelector('.product-hero h1');
    if (heroTitle) {
      const topics = ['GDP and inflation', 'UPI payments', 'coal and iron ore', 'Lok Sabha results', 'public health', 'defence and security', 'tourism and heritage'];
      heroTitle.insertAdjacentHTML('afterend', `<p class="hero-typed">Track <span class="visually-hidden">${topics.join(', ')}</span><span aria-hidden="true"><span class="typewriter-text">${topics[0]}</span><span class="caret"></span></span></p>`);
      const out = heroTitle.nextElementSibling.querySelector('.typewriter-text');
      if (!reduced) {
        let index = 0;
        let length = topics[0].length;
        let deleting = true;
        const tick = () => {
          const phrase = topics[index];
          let delay = deleting ? 35 : 70;
          if (!deleting && length === phrase.length) { deleting = true; delay = 1800; }
          else if (deleting && length === 0) { deleting = false; index = (index + 1) % topics.length; }
          else length += deleting ? -1 : 1;
          out.textContent = topics[index].slice(0, length);
          setTimeout(tick, delay);
        };
        setTimeout(tick, 1800);
      }
    }

    // Count up hero metrics whenever app.js fills them with a number; a new value mid-animation retargets it.
    document.querySelectorAll('.hero-metrics strong').forEach(node => {
      let written = null;
      let target = 0;
      let frame = 0;
      const animate = () => {
        const text = node.textContent.trim();
        if (reduced || text === written || !/^[\d,]+$/.test(text)) return;
        const next = Number(text.replace(/,/g, ''));
        if (!next) return;
        target = next;
        if (frame) return;
        const start = performance.now();
        const step = now => {
          const t = Math.min((now - start) / 1400, 1);
          written = Math.round(target * (1 - (1 - t) ** 3)).toLocaleString('en-IN');
          node.textContent = written;
          frame = t < 1 ? requestAnimationFrame(step) : 0;
        };
        frame = requestAnimationFrame(step);
      };
      new MutationObserver(animate).observe(node, { childList: true, characterData: true, subtree: true });
      animate();
    });

    if (!reduced && window.matchMedia('(hover: hover)').matches) {
      document.addEventListener('pointermove', event => {
        const card = event.target.closest?.('.chart-card, .feature-card, .group-tile, .mini-index, .tile-card, .group-hero');
        if (!card) return;
        const box = card.getBoundingClientRect();
        card.style.setProperty('--mx', `${event.clientX - box.left}px`);
        card.style.setProperty('--my', `${event.clientY - box.top}px`);
      }, { passive: true });
    }

    if (reduced || !('IntersectionObserver' in window)) return;
    const io = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-in');
        io.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -6% 0px', threshold: 0.06 });
    const tag = () => {
      document.querySelectorAll('.chart-card, .feature-card, .group-tile, .article-list li').forEach((node, index) => {
        if (node.dataset.rise || node.hasAttribute('data-reveal')) return;
        node.dataset.rise = '1';
        if (node.getBoundingClientRect().top < window.innerHeight) return;
        node.style.setProperty('--rise-delay', `${(index % 3) * 80}ms`);
        node.classList.add('rise');
        io.observe(node);
      });
    };
    tag();
    new MutationObserver(tag).observe(document.querySelector('main') || document.body, { childList: true, subtree: true });
  });
})();

/* Latest publisher articles are shown only in the Sources page acknowledgement. */
(() => {
  const feeds = [['#thanks-pp-articles', 'substack-latest.json'], ['#thanks-im-articles', 'indian-matrix-latest.json']];
  const render = (container, articles) => {
    container.replaceChildren();
    if (!articles.length) {
      container.innerHTML = '<p class="article-loading">No public article snapshot available yet.</p>';
      return;
    }
    articles.slice(0, 3).forEach(article => {
      const link = document.createElement('a');
      link.className = 'article-button';
      link.href = article.link;
      link.target = '_blank';
      link.rel = 'noreferrer';
      const title = document.createElement('strong');
      title.textContent = article.title || 'Untitled public article';
      const date = document.createElement('span');
      date.textContent = `${article.published || 'Public article'} ↗`;
      link.append(title, date);
      container.append(link);
    });
  };
  const load = () => feeds.forEach(([selector, file]) => {
    const container = document.querySelector(selector);
    if (!container) return;
    const bundled = window.INDIA_OVERLAY_DATA?.[file];
    const source = bundled && location.protocol === 'file:'
      ? Promise.resolve(bundled)
      : fetch(`data/${file}`)
        .then(response => (response.ok ? response.json() : Promise.reject(new Error(response.statusText))))
        .catch(error => bundled || Promise.reject(error));
    source
      .then(payload => render(container, (payload.articles || []).filter(article => article && article.link)))
      .catch(() => { container.innerHTML = '<p class="article-loading">Articles are temporarily unavailable.</p>'; });
  });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load); else load();
})();
