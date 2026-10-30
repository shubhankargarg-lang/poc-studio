// build_walk.mjs — the AI PM's independent walk of a built app (Stage 4b).
// Opens every page (and every tab on it) at 1280x800 from the app's preview link with a saved session, and records
// what a PM would catch on first look: layout defects (the design-system render check), the scoping §4.1 visual
// acceptance block, raw values on screen, inert or unexplained disabled controls, coloured side stripes, console
// errors, failed requests, and every visible string for the copy review. It never submits forms or clicks anything
// except tabs, so it has no side effects on the app's data.
//
// usage:
//   node build_walk.mjs --url <preview_url> [--storage <session.json>] [--routes routes.json] [--out dir]
//                       [--glossary glossary.json] [--max-row 64] [--min-rows 8]
// routes.json: [{"name":"Home","route":"/home"}, ...] in scoping §11 nav order (relative to --url, or absolute).
// Without --routes, it discovers links from the app's navigation (nav, aside, [role=navigation]), up to 15.
// glossary.json (optional): {"Visit": ["Audit", "Inspection"]} — preferred term -> words that must not appear.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
// Find Playwright wherever POC Studio installed it: the shared collateral tools, a local node_modules, or NODE_PATH.
function loadPlaywright() {
  const roots = [path.join(os.homedir(), '.local/poc-collateral/node'), process.cwd(), HERE,
    ...(process.env.NODE_PATH || '').split(path.delimiter).filter(Boolean).map((p) => path.dirname(p))];
  for (const r of roots) { try { return createRequire(path.join(r, 'noop.js'))('playwright'); } catch {} }
  console.error('Playwright not found. Run the poc-collateral-setup skill, or `npm i playwright@1.56.1` here.'); process.exit(2);
}
const { chromium } = loadPlaywright();
const arg = (k, d) => { const i = process.argv.indexOf(`--${k}`); return i > 0 ? process.argv[i + 1] : d; };
const URL0 = arg('url'); if (!URL0) { console.error('--url is required'); process.exit(2); }
const OUT = arg('out', 'build-walk'), MAXROW = +arg('max-row', 64), MINROWS = +arg('min-rows', 8);
const STORAGE = arg('storage'), ROUTES = arg('routes'), GLOSSARY = arg('glossary');
const RENDER = fs.readFileSync(path.join(HERE, 'render_check.js'), 'utf8');
const SLOP = JSON.parse(fs.readFileSync(path.join(HERE, 'slop-phrases.json'), 'utf8'));
const GLOSS = GLOSSARY && fs.existsSync(GLOSSARY) ? JSON.parse(fs.readFileSync(GLOSSARY, 'utf8')) : {};
fs.mkdirSync(path.join(OUT, 'shots'), { recursive: true });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function settle(page, ms = 8000) {
  await page.waitForLoadState('networkidle', { timeout: ms }).catch(() => {});
  const ok = await page.waitForFunction(() => {
    const vis = (e) => { const b = e.getBoundingClientRect(); return b.height > 0 && b.width > 0 && b.bottom > 0 && b.top < innerHeight; };
    return ![...document.querySelectorAll('[aria-busy="true"], [class*="skeleton" i], [class*="shimmer" i], [class*="spinner" i]')].some(vis);
  }, null, { timeout: ms }).then(() => true, () => false);
  await sleep(400); return ok;
}

// Everything the PM looks at on one screen, measured in the page.
const INSPECT = ({ maxRow, minRows }) => {
  const vis = (e) => { const cs = getComputedStyle(e); if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) return false;
    const b = e.getBoundingClientRect(); return b.width > 0 && b.height > 0; };
  const inView = (e) => { const b = e.getBoundingClientRect(); return b.bottom > 0 && b.top < innerHeight; };
  const label = (e) => (e.innerText || e.getAttribute('aria-label') || e.value || '').trim().replace(/\s+/g, ' ').slice(0, 80);
  const where = (e) => e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\s+/).slice(0, 2).join('.') : '');
  const out = { hScroll: document.documentElement.scrollWidth - document.documentElement.clientWidth };

  // Copy: every visible text node, with the kind of element it sits in.
  const copy = [];
  const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (walk.nextNode()) {
    const n = walk.currentNode, t = n.textContent.trim(), el = n.parentElement;
    if (!t || !el || !vis(el) || el.closest('script,style,noscript')) continue;
    const kind = el.closest('button,[role=button]') ? 'button' : el.closest('h1,h2,h3,h4,[role=heading]') ? 'heading'
      : el.closest('label,th') ? 'label' : el.closest('td,[role=cell],[role=gridcell]') ? 'cell'
      : el.closest('[role=tab]') ? 'tab' : el.closest('nav,aside,[role=navigation]') ? 'nav' : 'text';
    copy.push({ kind, text: t.slice(0, 300) });
  }
  for (const e of document.querySelectorAll('input[placeholder],textarea[placeholder]')) if (vis(e)) copy.push({ kind: 'placeholder', text: e.placeholder });
  out.copy = copy;

  // Raw values that should never reach a user.
  const RAW = /(^|\s)(null|undefined|NaN|\[object Object\]|Invalid Date|\{\{[^}]*\}\})(?=\s|$)/;
  const FRACTION = /^(0\.\d{1,4}|1\.0+)$/;                       // a ratio shown as a fraction, not a %
  const SNAKE = /\b[a-z]+(?:_[a-z0-9]+){1,}\b/;                  // field_name leaking into copy
  const QUERY = /\b[a-z_]+\s*(=|>|<|!=|>=|<=)\s*['"\w]+/;         // "status = open"
  out.raw = copy.filter((c) => RAW.test(c.text) || FRACTION.test(c.text) || (c.kind !== 'text' || c.text.length < 60) && (SNAKE.test(c.text) || QUERY.test(c.text)))
    .map((c) => c.text).slice(0, 40);

  // Visual acceptance (scoping §4.1).
  const rows = [...document.querySelectorAll('tbody tr, [role=row]')].filter((r) => vis(r) && !r.closest('thead') && !r.querySelector('th'));
  out.rows = rows.length;
  out.tallRows = rows.filter((r) => r.getBoundingClientRect().height > maxRow).length;
  out.rowsInView = rows.filter(inView).length;
  out.fewRowsVisible = rows.length >= minRows && out.rowsInView < minRows;
  out.wrappedPills = [...document.querySelectorAll('[class*="tag" i],[class*="pill" i],[class*="badge" i],[class*="chip" i]')]
    .filter((e) => { if (!vis(e) || !e.innerText.trim()) return false; const lh = parseFloat(getComputedStyle(e).lineHeight) || parseFloat(getComputedStyle(e).fontSize) * 1.3;
      return e.getBoundingClientRect().height > lh * 1.7; }).map(label).slice(0, 20);

  // Controls: disabled without a reason, and buttons with no name.
  const buttons = [...document.querySelectorAll('button,[role=button],a[href]')].filter(vis);
  out.buttons = buttons.filter((b) => b.tagName !== 'A').map(label).filter(Boolean);
  out.disabledNoReason = buttons.filter((b) => (b.disabled || b.getAttribute('aria-disabled') === 'true')
      && !b.title && !b.getAttribute('aria-describedby') && !b.closest('[title]') && !b.getAttribute('data-tooltip'))
    .map(label).slice(0, 20);
  out.unnamedButtons = buttons.filter((b) => b.tagName !== 'A' && !label(b) && !b.title).length;

  // Coloured side stripes on cards, rows, bubbles and fields (owner profile rule).
  const neutral = (rgb) => { const m = rgb.match(/\d+/g); if (!m) return true; const [r, g, b] = m.map(Number); return Math.max(r, g, b) - Math.min(r, g, b) < 18; };
  out.sideStripes = [...document.querySelectorAll('body *')].filter((e) => {
    if (!vis(e)) return false; const cs = getComputedStyle(e), b = e.getBoundingClientRect();
    if (b.width < 120 || b.height < 28) return false;
    const w = parseFloat(cs.borderLeftWidth); const solidLeft = w >= 2 && cs.borderLeftStyle !== 'none' && !neutral(cs.borderLeftColor)
      && parseFloat(cs.borderRightWidth) < 1;
    const pseudo = getComputedStyle(e, '::before'); const pw = parseFloat(pseudo.width);
    const pseudoStripe = pseudo.content !== 'none' && pw >= 2 && pw <= 6 && parseFloat(pseudo.height) > 20 && !neutral(pseudo.backgroundColor)
      && !e.closest('nav,aside,[role=navigation]');
    return solidLeft || pseudoStripe;
  }).map(where).slice(0, 15);

  // Numbers shown on badges and KPI tiles, for count reconciliation by the reviewer.
  out.badges = [...document.querySelectorAll('nav *, aside *, [class*="badge" i], [class*="count" i], [class*="kpi" i], [class*="tile" i]')]
    .filter((e) => vis(e) && /^\d[\d,]*$/.test(e.innerText.trim()) && e.children.length === 0)
    .map((e) => ({ value: e.innerText.trim(), near: label(e.parentElement).slice(0, 60) })).slice(0, 40);

  out.tabs = [...document.querySelectorAll('[role=tab]')].filter(vis).map((t) => ({ name: label(t), selected: t.getAttribute('aria-selected') === 'true' }));
  out.title = (document.querySelector('h1,[role=heading][aria-level="1"]')?.innerText || document.title || '').trim().slice(0, 100);
  return out;
};

function slopHits(copy) {
  const hits = [];
  for (const [group, list] of Object.entries(SLOP)) {
    if (group.startsWith('_')) continue;
    for (const c of copy) {
      const low = c.text.toLowerCase();
      for (const p of list) {
        const pl = p.toLowerCase();
        const match = group === 'vague_buttons' ? (c.kind === 'button' && low === pl) : new RegExp(`(^|\\W)${pl.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(\\W|$)`, 'i').test(c.text);
        if (match) hits.push({ group, phrase: p, text: c.text.slice(0, 120), kind: c.kind });
      }
    }
  }
  for (const [pref, avoid] of Object.entries(GLOSS))
    for (const w of avoid) for (const c of copy) if (new RegExp(`\\b${w}\\b`, 'i').test(c.text)) hits.push({ group: 'glossary', phrase: `${w} → ${pref}`, text: c.text.slice(0, 120), kind: c.kind });
  return hits;
}

const launchOpts = { headless: true };
if (process.env.CHROME_PATH) launchOpts.executablePath = process.env.CHROME_PATH;
const browser = await chromium.launch(launchOpts);
const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1,
  ...(STORAGE && fs.existsSync(STORAGE) ? { storageState: STORAGE } : {}) });
const page = await ctx.newPage();
const consoleErrors = [], failed = [];
page.on('console', (m) => { if (m.type() === 'error') consoleErrors.push({ url: page.url(), text: m.text().slice(0, 200) }); });
page.on('pageerror', (e) => consoleErrors.push({ url: page.url(), text: String(e).slice(0, 200) }));
page.on('response', (r) => { if (r.status() >= 400 && !/favicon|analytics|sentry|hotjar|segment/i.test(r.url())) failed.push({ status: r.status(), url: r.url().slice(0, 160), on: page.url() }); });

let routes = ROUTES && fs.existsSync(ROUTES) ? JSON.parse(fs.readFileSync(ROUTES, 'utf8')) : null;
await page.goto(URL0, { waitUntil: 'domcontentloaded', timeout: 60000 });
await settle(page);
const signedOut = /\/login|\/signin|\/auth\b/i.test(new URL(page.url()).pathname);
if (!routes) {
  routes = await page.evaluate(() => [...document.querySelectorAll('nav a[href], aside a[href], [role=navigation] a[href]')]
    .map((a) => ({ name: (a.innerText || a.getAttribute('aria-label') || '').trim().slice(0, 40), route: a.href }))
    .filter((r, i, all) => r.name && all.findIndex((x) => x.route === r.route) === i)).catch(() => []);
  if (!routes.length) routes = [{ name: 'Start', route: URL0 }];
  routes = routes.slice(0, 15);
}

const pages = [];
async function capture(name, slug) {
  const ok = await settle(page);
  const shot = path.join('shots', `${slug}.png`);
  await page.screenshot({ path: path.join(OUT, shot) });
  const render = await page.evaluate(RENDER).catch((e) => ({ error: String(e).slice(0, 200) }));
  const ins = await page.evaluate(INSPECT, { maxRow: MAXROW, minRows: MINROWS });
  const rec = { name, url: page.url(), shot, stillLoading: !ok, render: { ...render, fonts: undefined, unstyledClasses: undefined }, ...ins, slop: slopHits(ins.copy) };
  pages.push(rec); return rec;
}

for (const [i, r] of routes.entries()) {
  const slug = `${String(i + 1).padStart(2, '0')}-${(r.name || 'page').toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 30)}`;
  try {
    await page.goto(new URL(r.route, URL0).href, { waitUntil: 'domcontentloaded', timeout: 60000 });
    const rec = await capture(r.name, slug);
    for (const [k, t] of rec.tabs.entries()) {                    // open every other tab: safe, no data changes
      if (t.selected || !t.name) continue;
      try {
        await page.getByRole('tab', { name: t.name, exact: true }).first().click({ timeout: 5000 });
        await capture(`${r.name} › ${t.name}`, `${slug}-tab${k + 1}`);
      } catch (e) { pages.push({ name: `${r.name} › ${t.name}`, error: `tab did not open: ${String(e).split('\n')[0]}` }); }
    }
  } catch (e) { pages.push({ name: r.name, url: r.route, error: String(e).split('\n')[0] }); }
}
await browser.close();

// Findings the reviewer starts from (candidates — it confirms each against the screenshot before keeping it).
const F = [];
const add = (dimension, blocking, where, evidence, fix) => F.push({ id: `W${F.length + 1}`, dimension, blocking, where, evidence, fix });
if (signedOut) add('R9', true, 'session', `the preview opened on ${page.url?.() ?? 'a sign-in page'}`, 'Sign in to Orbit (orbit_signin.mjs) and re-run the walk');
for (const p of pages) {
  if (p.error) { add('R7', true, p.name, p.error, 'Make the page/tab open without error'); continue; }
  const r = p.render || {};
  if (p.stillLoading) add('R7', true, p.name, 'still loading after 8 s (skeleton/spinner visible)', 'Make the page load within 8 s or show a designed loading state');
  if (p.hScroll > 2) add('R8', true, p.name, `horizontal page scroll of ${p.hScroll}px at 1280px`, 'Fit the page to 1280px; let wide tables scroll inside their own container');
  for (const k of ['spills', 'clipped', 'vclipped', 'overlaps', 'squeezed', 'brokenImages']) if (r[k] > 0)
    add('R8', k !== 'squeezed' || r[k] > 3, p.name, `${r[k]} ${k}: ${(r.where || []).filter((w) => w.startsWith(k)).slice(0, 3).join(' | ')}`, `Fix the ${k} elements listed`);
  if (p.tallRows) add('R8', true, p.name, `${p.tallRows} of ${p.rows} list rows taller than ${MAXROW}px`, `One line per cell (two in the first column); move detail to an expanded row or drawer`);
  if (p.fewRowsVisible) add('R8', false, p.name, `only ${p.rowsInView} rows in the first viewport (needs ${MINROWS})`, 'Reduce the space above the list or the row height');
  if (p.wrappedPills.length) add('R8', true, p.name, `wrapped pills: ${p.wrappedPills.join(', ')}`, 'Shorten the pill text or widen the column; pills never wrap');
  if (p.raw.length) add('R6', true, p.name, `raw values on screen: ${p.raw.slice(0, 6).map((x) => `"${x}"`).join(', ')}`, 'Format values (percentages, dates, display names); never show field names, nulls or query syntax');
  if (p.disabledNoReason.length) add('R7', true, p.name, `disabled with no reason: ${p.disabledNoReason.join(', ')}`, 'Give each disabled button a tooltip or helper line naming what is missing (scoping §11 prerequisites)');
  if (p.unnamedButtons) add('R7', false, p.name, `${p.unnamedButtons} buttons with no text or accessible name`, 'Add an aria-label or visible label');
  if (p.sideStripes.length) add('R8', true, p.name, `coloured side stripe on: ${p.sideStripes.slice(0, 4).join(', ')}`, 'Remove the side stripe; show status with the tag (owner profile)');
  const slop = [...new Map(p.slop.map((s) => [s.group + s.phrase, s])).values()];
  if (slop.length) add('R5', slop.some((s) => s.group === 'ui_jargon' || s.group === 'glossary'), p.name,
    slop.slice(0, 6).map((s) => `${s.group}: "${s.phrase}" in "${s.text}"`).join(' | '), 'Rewrite in the client\'s vocabulary (scoping Appendix B); see references/slop.md section 3');
}
const byPage = {};
for (const e of consoleErrors) (byPage[e.url] ??= []).push(e.text);
for (const [u, errs] of Object.entries(byPage)) add('R7', false, u, `${errs.length} console errors, e.g. ${errs[0]}`, 'Fix the script errors');
for (const f of failed.slice(0, 15)) add('R7', f.status >= 500, f.on, `HTTP ${f.status} on ${f.url}`, 'Fix the failing request');

// A shared component repeats its defect on every screen: report it once, listing the screens.
{
  const groups = new Map();
  for (const f of F) {
    const key = `${f.dimension}|${f.fix}|${f.evidence.replace(/^\d+ of \d+/, 'N')}`;
    if (groups.has(key)) groups.get(key).screens.push(f.where); else groups.set(key, { ...f, screens: [f.where] });
  }
  F.length = 0;
  for (const g of groups.values()) F.push({ ...g, id: `W${F.length + 1}`, where: g.screens.length > 3 ? `${g.screens.length} screens: ${g.screens.slice(0, 3).join(', ')} …` : g.screens.join(', ') });
  F.sort((a, b) => (b.blocking - a.blocking));
}
fs.writeFileSync(path.join(OUT, 'copy.json'), JSON.stringify(pages.filter((p) => p.copy).map((p) => ({ page: p.name, copy: p.copy })), null, 2));
fs.writeFileSync(path.join(OUT, 'report.json'), JSON.stringify({ url: URL0, at: new Date().toISOString(), pages: pages.map(({ copy, ...p }) => p), consoleErrors, failed, findings: F }, null, 2));
const md = [`# Build walk — ${URL0}`, '', `${pages.length} screens · ${F.length} candidate findings (${F.filter((f) => f.blocking).length} blocking)`, '',
  '| # | Screen | Shot | Render (spill/clip/vclip/overlap/squeeze) | Rows (tall/total) | Raw | Disabled w/o reason | Stripes | Slop |', '|---|---|---|---|---|---|---|---|---|',
  ...pages.map((p, i) => p.error ? `| ${i + 1} | ${p.name} | — | **error:** ${p.error} | | | | | |`
    : `| ${i + 1} | ${p.name} | ${p.shot} | ${['spills', 'clipped', 'vclipped', 'overlaps', 'squeezed'].map((k) => p.render?.[k] ?? '?').join('/')} | ${p.tallRows}/${p.rows} | ${p.raw.length} | ${p.disabledNoReason.length} | ${p.sideStripes.length} | ${p.slop.length} |`),
  '', '## Candidate findings', '', ...F.map((f) => `- **${f.id}** ${f.blocking ? '[blocking] ' : ''}${f.dimension} · ${f.where} — ${f.evidence} → ${f.fix}`)];
fs.writeFileSync(path.join(OUT, 'report.md'), md.join('\n') + '\n');
console.log(`${OUT}/report.md: ${pages.length} screens, ${F.length} candidate findings (${F.filter((f) => f.blocking).length} blocking)`);
