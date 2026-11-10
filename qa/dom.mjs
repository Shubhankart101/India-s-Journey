import { createRequire } from 'node:module';
const require = createRequire(new URL('../frontend/package.json', import.meta.url));
const { chromium } = require('@playwright/test');
const [url, theme = 'light', width = '1440'] = process.argv.slice(2);
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: +width, height: 900 } });
await ctx.addInitScript(t => localStorage.setItem('ij-theme', t), theme);
const page = await ctx.newPage();
await page.goto(url, { waitUntil: 'load' });
await page.waitForTimeout(2000);
const r = await page.evaluate(() => {
  const walk = (el, d) => {
    if (d > 3) return null;
    return { tag: el.tagName.toLowerCase(), id: el.id || undefined, cls: (el.className && el.className.baseVal === undefined ? el.className : '').toString().slice(0, 60) || undefined, kids: [...el.children].slice(0, 14).map(c => walk(c, d + 1)).filter(Boolean) };
  };
  return walk(document.querySelector('main') || document.body, 0);
});
const fmt = (n, i = 0) => ' '.repeat(i) + n.tag + (n.id ? '#' + n.id : '') + (n.cls ? '.' + n.cls.replace(/ /g, '.') : '') + '\n' + (n.kids || []).map(k => fmt(k, i + 1)).join('');
console.log(fmt(r));
await page.screenshot({ path: 'qa/shots/home-full.png', fullPage: true });
await browser.close();
