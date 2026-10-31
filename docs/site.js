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
