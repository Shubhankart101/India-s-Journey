/* Shared chrome for every page: the sticky header, the mobile tab bar and scroll reveals. */
(() => {
  const page = document.body.dataset.page || 'home';
  const links = [
    { id: 'home', href: 'index.html', label: 'Home', icon: '⌂' },
    { id: 'explore', href: 'explore.html', label: 'Explore', icon: '◔' },
    { id: 'about', href: 'about.html', label: 'About', icon: 'ⓘ' },
    { id: 'sources', href: 'explore.html#references', label: 'Sources', icon: '❡', desktopOnly: true },
    { id: 'api', href: 'api.html', label: 'API', icon: '{ }' }
  ];
  const current = id => (id === page ? ' aria-current="page"' : '');

  const header = `
  <header class="masthead">
    <a class="brand-mark" href="index.html" aria-label="India's Journey home"><span class="brand-emblem">IJ</span><span>India's Journey<small>The public data atlas</small></span></a>
    <nav class="site-nav" aria-label="Main navigation">
      ${links.map(link => `<a href="${link.href}"${current(link.id)}>${link.label}</a>`).join('')}
    </nav>
    <a class="nav-cta" href="explore.html">Explore data</a>
  </header>`;
  const script = document.currentScript;
  if (script) script.insertAdjacentHTML('beforebegin', header);

  document.addEventListener('DOMContentLoaded', () => {
    const tabs = links.filter(link => !link.desktopOnly)
      .map(link => `<a href="${link.href}"${current(link.id)}><span class="tab-icon" aria-hidden="true">${link.icon}</span><span>${link.label}</span></a>`)
      .join('');
    document.body.insertAdjacentHTML('beforeend', `<nav class="tabbar" aria-label="Primary">${tabs}</nav>`);

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

    // Count up hero metrics whenever app.js fills them with a number.
    document.querySelectorAll('.hero-metrics strong').forEach(node => {
      const animate = () => {
        const text = node.textContent.trim();
        if (reduced || node.dataset.counting || !/^[\d,]+$/.test(text)) return;
        const target = Number(text.replace(/,/g, ''));
        if (!target) return;
        node.dataset.counting = '1';
        const start = performance.now();
        const step = now => {
          const t = Math.min((now - start) / 1400, 1);
          node.textContent = Math.round(target * (1 - (1 - t) ** 3)).toLocaleString('en-IN');
          if (t < 1) requestAnimationFrame(step);
          else delete node.dataset.counting;
        };
        requestAnimationFrame(step);
      };
      new MutationObserver(animate).observe(node, { childList: true, characterData: true, subtree: true });
      animate();
    });

    if (!reduced && window.matchMedia('(hover: hover)').matches) {
      document.addEventListener('pointermove', event => {
        const card = event.target.closest?.('.chart-card, .feature-card, .product-tile, .tile-card, .group-hero');
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
      document.querySelectorAll('.chart-card, .feature-card, .product-tile').forEach((node, index) => {
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
