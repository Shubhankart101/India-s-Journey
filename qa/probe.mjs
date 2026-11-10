import { createRequire } from 'node:module';
const require = createRequire(new URL('../frontend/package.json', import.meta.url));
const { chromium } = require('@playwright/test');

const SITES = { static: 'http://localhost:8772/', django: 'http://localhost:8765/' };
const THEMES = ['light', 'dark', 'newspaper', 'pamphlet'];
const widths = [1440, 390];
const only = process.argv[2];
const out = [];

const browser = await chromium.launch();
for (const [name, url] of Object.entries(SITES)) {
  if (only && only !== name) continue;
  for (const width of widths) {
    for (const theme of THEMES) {
      const ctx = await browser.newContext({ viewport: { width, height: 900 } });
      await ctx.addInitScript(t => localStorage.setItem('ij-theme', t), theme);
      const page = await ctx.newPage();
      const errors = [];
      page.on('pageerror', e => errors.push('pageerror: ' + e.message));
      page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text().slice(0, 160)); });
      const t0 = Date.now();
      await page.goto(url, { waitUntil: 'load' });
      await page.waitForTimeout(1500);
      const info = await page.evaluate(() => {
        const vis = el => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el); return r.width > 2 && r.height > 2 && s.visibility !== 'hidden' && s.display !== 'none' && s.opacity !== '0'; };
        const pill = document.querySelector('.theme-switch, .theme-pill, [data-theme-switch], .theme-selector, .theme-toggle');
        const pillButtons = pill ? [...pill.querySelectorAll('button')].map(b => ({ t: b.textContent.trim(), v: vis(b), a: b.getAttribute('aria-label') })) : null;
        const text = document.body.innerText;
        return {
          theme: document.documentElement.dataset.theme,
          marquee: !!document.querySelector('.marquee, .chip-marquee, .group-marquee, [class*=marquee], [class*=ticker]'),
          cards: document.querySelectorAll('.group-card, .gc-card, [class*=group-card]').length,
          pillFound: !!pill, pillButtons,
          logo: [...document.querySelectorAll('header img, .brand img, .logo img, header svg')].slice(0, 2).map(i => i.outerHTML.slice(0, 120)),
          badText: /\?\?\?|\uFFFD|Ã.|à¤|à¥|â€/.test(text) ? (text.match(/.{0,30}(\?\?\?|\uFFFD|Ã.|à¤|à¥|â€).{0,30}/) || [''])[0] : null,
          hasDevanagari: /[\u0900-\u097F]/.test(text),
          overflowX: document.documentElement.scrollWidth > innerWidth + 2,
        };
      });
      out.push({ site: name, width, theme, ms: Date.now() - t0, errors: errors.slice(0, 4), ...info });
      await page.screenshot({ path: `qa/shots/${name}-${width}-${theme}.png` });
      await ctx.close();
    }
  }
}
await browser.close();
console.log(JSON.stringify(out, null, 1));
