// Layout audit: visits every route type in every theme at desktop and phone widths and flags
// overlapping text/controls, horizontal overflow, console errors and '?' mojibake.
// Usage: node scripts/layout-audit.mjs [--base http://127.0.0.1:8765] [--themes light,dark] [--widths 1440,390] [--only substring] [--max N]
import { chromium } from '@playwright/test';

const args = process.argv.slice(2);
const opt = (name, fallback) => { const i = args.indexOf(`--${name}`); return i >= 0 ? args[i + 1] : fallback; };
const BASE = opt('base', 'http://127.0.0.1:8765').replace(/\/$/, '');
const THEMES = opt('themes', 'light,dark,newspaper,pamphlet').split(',');
const WIDTHS = opt('widths', '1440,390').split(',').map(Number);
const ONLY = opt('only', '');
const MAX = Number(opt('max', '0'));

const SEEDS = ['/', '/explore', '/elections', '/voter-list-sir-ssr', '/compare', '/sources', '/about'];

function inPageAudit() {
  const issues = [];
  const doc = document.documentElement;
  if (doc.scrollWidth > window.innerWidth + 1) {
    const culprit = [...document.body.querySelectorAll('*')].find(el => !el.closest('svg, [aria-hidden="true"]') && el.getBoundingClientRect().right > window.innerWidth + 1 && el.getBoundingClientRect().width > 0 && getComputedStyle(el).position !== 'fixed');
    const tag = culprit ? culprit.tagName.toLowerCase() + '.' + String(culprit.className).trim().split(/\s+/).slice(0, 2).join('.') : '?';
    issues.push({ kind: 'h-overflow', detail: `scrollWidth ${doc.scrollWidth} > ${window.innerWidth} (${tag})` });
  }

  const visible = el => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || Number(cs.opacity) === 0) return false;
    if (cs.clip === 'rect(0px, 0px, 0px, 0px)' || (cs.position === 'absolute' && el.offsetWidth <= 1 && el.offsetHeight <= 1)) return false;
    for (let p = el.parentElement; p; p = p.parentElement) {
      const s = getComputedStyle(p);
      if (s.display === 'none' || s.visibility === 'hidden' || Number(s.opacity) === 0) return false;
      if (p.tagName === 'DETAILS' && !p.open) {
        let child = el; while (child.parentElement !== p) child = child.parentElement;
        if (child.tagName !== 'SUMMARY') return false;
      }
    }
    return true;
  };
  const clipRect = (el, self) => {
    let r = null;
    for (let p = self ? el : el.parentElement; p && p !== document.body; p = p.parentElement) {
      const s = getComputedStyle(p);
      if (s.overflowX !== 'visible' || s.overflowY !== 'visible') {
        const b = p.getBoundingClientRect();
        r = r ? { l: Math.max(r.l, b.left), t: Math.max(r.t, b.top), r: Math.min(r.r, b.right), b: Math.min(r.b, b.bottom) } : { l: b.left, t: b.top, r: b.right, b: b.bottom };
      }
    }
    return r;
  };
  const controls = new Set(['BUTTON', 'INPUT', 'SELECT', 'TEXTAREA', 'SUMMARY']);
  const items = [];
  const all = document.body.querySelectorAll('*');
  for (const el of all) {
    if (el.closest('svg') || el.closest('script,style,noscript,[aria-hidden="true"]') || el.closest('[role="tooltip"]')) continue;
    if (el.classList.contains('sr-only')) continue;
    let rects = [];
    if (controls.has(el.tagName)) {
      const b = el.getBoundingClientRect(); if (b.width && b.height) rects.push(b);
    } else {
      const range = document.createRange();
      for (const n of el.childNodes) {
        if (n.nodeType === 3 && n.textContent.trim()) { range.selectNodeContents(n); for (const r of range.getClientRects()) if (r.width > 1 && r.height > 1) rects.push(r); }
      }
    }
    if (!rects.length || !visible(el)) continue;
    const clip = clipRect(el, !controls.has(el.tagName));
    if (clip) rects = rects.filter(r => r.right > clip.l && r.left < clip.r && r.bottom > clip.t && r.top < clip.b);
    if (!rects.length) continue;
    const fixed = (() => { for (let p = el; p; p = p.parentElement) { const pos = getComputedStyle(p).position; if (pos === 'fixed' || pos === 'sticky') return true; } return false; })();
    if (fixed) continue;
    items.push({ el, rects });
  }
  const name = el => el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '') + ' "' + (el.textContent || el.value || '').trim().replace(/\s+/g, ' ').slice(0, 28) + '"';
  const seen = new Set();
  for (let i = 0; i < items.length; i++) {
    for (let j = i + 1; j < items.length; j++) {
      const a = items[i], b = items[j];
      if (a.el.contains(b.el) || b.el.contains(a.el)) continue;
      let hit = false;
      for (const ra of a.rects) {
        for (const rb of b.rects) {
          const w = Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left);
          const h = Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top);
          if (w > 2 && h > 3) { hit = true; break; }
        }
        if (hit) break;
      }
      if (!hit) continue;
      const key = name(a.el) + ' x ' + name(b.el);
      if (seen.has(key)) continue;
      seen.add(key);
      issues.push({ kind: 'overlap', detail: key });
    }
  }
  const text = document.body.innerText;
  const moji = text.match(/\S \? \S|\d\?\d|\uFFFD/);
  if (moji) issues.push({ kind: 'mojibake', detail: JSON.stringify(text.slice(Math.max(0, moji.index - 25), moji.index + 25)) });
  return issues;
}

async function discover(page) {
  const links = new Set();
  await page.goto(BASE + '/', { waitUntil: 'networkidle' });
  const categories = await page.evaluate(async () => {
    for (const url of ['/api/categories', '/api/categories.json']) {
      try { const r = await fetch(url); const j = await r.json(); if (Array.isArray(j)) return j; } catch { /* try next */ }
    }
    return [];
  });
  for (const c of categories) {
    links.add(`/explore?category=${c.slug}`);
    for (const s of c.subgroups || []) links.add(`/explore/${c.slug}/${s.slug}`);
  }
  // region pages (3) and indicator pages (2) are found by following links from list pages
  let regions = 0;
  const mapFirst = [...links].filter(l => l.startsWith('/explore/')).sort((a, b) => Number(b.includes('/india-in-maps/')) - Number(a.includes('/india-in-maps/')));
  for (const subgroup of mapFirst) {
    if (regions >= 3) break;
    await page.goto(BASE + subgroup, { waitUntil: 'networkidle' });
    const found = await page.$$eval('a[href]', as => as.map(a => a.getAttribute('href')));
    const region = found.find(h => h && h.startsWith(subgroup + '/') && !h.slice(subgroup.length + 1).includes('/'));
    if (region) { links.add(region); regions++; }
  }
  for (const state of ['maharashtra', 'kerala', 'uttar-pradesh']) links.add(`/elections/${state}`);
  for (const key of ['gdp_growth', 'cpi']) links.add(`/indicator/${key}`);
  return [...links];
}

const browser = await chromium.launch();
const probe = await browser.newPage();
let routes = [...SEEDS, ...(await discover(probe)).sort()];
await probe.close();
routes = [...new Set(routes)].filter(r => !ONLY || r.includes(ONLY));
if (MAX) routes = routes.slice(0, MAX);

const report = [];
let pages = 0;
const TOGGLES = '.atlas-switch button, .atlas-view-switch button';
for (const theme of THEMES) {
  for (const width of WIDTHS) {
    const ctx = await browser.newContext({ viewport: { width, height: width > 800 ? 900 : 800 } });
    await ctx.addInitScript(t => { try { localStorage.setItem('ij-theme', t); } catch { /* ignore */ } }, theme);
    const page = await ctx.newPage();
    const errors = [];
    page.on('console', m => { if (m.type() === 'error' && !/favicon|Failed to load resource/.test(m.text())) errors.push(m.text().slice(0, 160)); });
    page.on('pageerror', e => errors.push('pageerror: ' + e.message.slice(0, 160)));
    for (const route of routes) {
      errors.length = 0;
      try {
        await page.goto(BASE + route, { waitUntil: 'networkidle', timeout: 45000 });
        await page.waitForTimeout(700);
      } catch (e) { report.push({ route, theme, width, kind: 'load', detail: e.message.slice(0, 120) }); continue; }
      pages++;
      const seenIssues = new Set();
      const push = (label, issue) => {
        const key = route + label + issue.kind + issue.detail;
        if (seenIssues.has(key)) return;
        seenIssues.add(key);
        report.push({ route: route + label, theme, width, ...issue });
      };
      const here = async label => { for (const issue of await page.evaluate(inPageAudit)) push(label, issue); };
      // lazy charts mount near the viewport and unmount far away, so audit at each scroll position
      const run = async label => {
        const total = await page.evaluate(() => document.documentElement.scrollHeight);
        const step = width > 800 ? 800 : 700;
        for (let y = 0; y < total; y += step) {
          await page.evaluate(v => window.scrollTo(0, v), y);
          await page.waitForTimeout(250);
          await here(label);
        }
        await page.evaluate(() => window.scrollTo(0, 0));
      };
      await run('');
      // exercise every epic/view toggle so each atlas state is audited
      const count = await page.$$eval(TOGGLES, b => b.length).catch(() => 0);
      for (let i = 0; i < count; i++) {
        const btn = (await page.$$(TOGGLES))[i];
        if (!btn) continue;
        const label = (await btn.innerText()).trim();
        if (await btn.getAttribute('aria-pressed') === 'true') continue;
        await btn.click().catch(() => {});
        await page.waitForTimeout(400);
        await here(` [atlas:${label}]`);
      }
      for (const e of errors) report.push({ route, theme, width, kind: 'console', detail: e });
    }
    await ctx.close();
  }
}
await browser.close();

const byKind = {};
for (const r of report) byKind[r.kind] = (byKind[r.kind] || 0) + 1;
const grouped = new Map();
for (const r of report) {
  const k = `${r.kind} | ${r.route} | ${r.detail}`;
  if (!grouped.has(k)) grouped.set(k, new Set());
  grouped.get(k).add(`${r.theme}@${r.width}`);
}
for (const [k, v] of grouped) console.log(k, '  <', [...v].join(' '));
console.log(`\n${BASE}: ${routes.length} routes, ${pages} page-loads, ${report.length} issues`, JSON.stringify(byKind));
process.exit(report.length ? 1 : 0);
