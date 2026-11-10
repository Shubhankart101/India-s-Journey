import { createRequire } from 'node:module';
const require = createRequire(new URL('../frontend/package.json', import.meta.url));
const { chromium } = require('@playwright/test');

const SITES = { static: 'http://localhost:8772/', django: 'http://localhost:8765/' };
const THEMES = ['light', 'dark', 'newspaper', 'pamphlet'];
const only = process.argv[2];
const shots = process.argv[3] === 'shots';
const browser = await chromium.launch();
for (const [name, url] of Object.entries(SITES)) {
  if (only && only !== 'all' && only !== name) continue;
  for (const width of [1440, 390]) {
    for (const theme of THEMES) {
      const ctx = await browser.newContext({ viewport: { width, height: 900 } });
      await ctx.addInitScript(t => localStorage.setItem('ij-theme', t), theme);
      const page = await ctx.newPage();
      const errors = [];
      page.on('pageerror', e => errors.push('pageerror: ' + e.message));
      page.on('console', m => { if (m.type() === 'error' && !/fonts\.g|ERR_|favicon/.test(m.text())) errors.push(m.text().slice(0, 120)); });
      await page.goto(url, { waitUntil: 'load' });
      await page.waitForTimeout(1200);
      const info = await page.evaluate(() => {
        const vis = el => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el); return r.width > 4 && r.height > 4 && s.visibility !== 'hidden' && s.display !== 'none' && +s.opacity > 0.1; };
        const pill = [...document.querySelectorAll('.theme-select button')].map(b => `${b.value || b.textContent.trim()}:${vis(b) ? 'Y' : 'N'}`).join(' ');
        const chipMarquee = [...document.querySelectorAll('.marquee-item, #marquee-band .marquee')].filter(vis).length;
        const ticker = [...document.querySelectorAll('.vintage-ticker')].filter(vis).length;
        const tiles = [...document.querySelectorAll('#group-grid > *, .group-grid > *, .group-cards > *')];
        const text = document.body.innerText;
        const bad = text.match(/.{0,25}(\?\?\?|\uFFFD|Ã.|à¤|à¥|â€).{0,25}/);
        return { theme: document.documentElement.dataset.theme, pill, chipMarquee, ticker, tiles: tiles.length, tilesVis: tiles.filter(vis).length,
          tileCls: tiles[0]?.className, logo: document.querySelector('.brand-emblem, .brand-mark img, .brand img')?.outerHTML.slice(0, 80), dev: /[\u0900-\u097F]/.test(text), bad: bad && bad[0],
          overflowX: document.documentElement.scrollWidth - innerWidth };
      });
      console.log(name, width, theme, JSON.stringify(info), errors.length ? 'ERR ' + JSON.stringify(errors.slice(0, 3)) : '');
      if (shots) {
        await page.evaluate(() => (document.querySelector('#group-grid, .group-grid, .group-cards') || document.body).scrollIntoView());
        await page.waitForTimeout(800);
        await page.screenshot({ path: `qa/shots/${name}-${width}-${theme}-groups.png` });
      }
      await ctx.close();
    }
  }
}
await browser.close();
