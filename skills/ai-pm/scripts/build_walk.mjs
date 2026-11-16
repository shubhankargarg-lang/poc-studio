// build_walk.mjs — the AI PM's independent walk of a built app (Stage 4b).
// Opens every page (and every tab on it, nested tabs included) at 1280x800 from the app's preview link, once per
// persona, and records what a PM would catch on first look: layout defects (the design-system render check, with
// screen-reader text, chart internals and angled labels left out), the scoping §4.1 visual acceptance block, raw
// values on screen, inert or unexplained disabled controls, coloured side stripes, console errors, failed requests,
// and every visible string for the copy review.
// It never submits forms or presses action buttons. It clicks only: tabs; the persona switch in the profile menu
// (or the steps in --personas); and, where routes.json asks with "open", one row or one named control to open a
// record or drawer. So it has no side effects on the app's data.
// Platform failures (HTTP 429/502/503/504, platform error pages) are retried and reported apart from app defects.
// Pages are opened under the app root (the preview link, or --app-base); a page that lands outside it is a walk
// problem (route_left_app), never an app defect, and two such routes in a row stop the walk. A page that says the
// signed-in user has no access (HTTP 401/403, or "you do not have access" and similar) is not reviewed: it is a walk
// problem, and on the start page it makes the report INCOMPLETE (never a clean pass).
// Exit code: 0 walk complete · 1 the script crashed · 2 bad arguments or Playwright missing · 3 report is INCOMPLETE.
//
// usage:
//   node build_walk.mjs --url <preview_url> [--storage <session.json>] [--routes routes.json] [--out dir]
//                       [--glossary glossary.json] [--max-row 64] [--min-rows 8]
//                       [--settle 30000] [--slow 8000] [--tab-depth 3] [--max-tabs 40]
//                       [--personas personas.json] [--storage-by-persona "Planner=planner.json,Manager=mgr.json"]
//                       [--app-base <url>]   (default: the --url preview link itself is the app root)
// routes.json: [{"name":"Home","route":"home","persona":"Planner","tabs":["Overview","Lines"],"open":"first-row"}, ...]
//   in scoping §11 nav order. route: relative to the app root, no leading "/" ("orders"); "/orders", "./orders" and a
//   path that already starts with the app root's path also work; a full https:// address is used as it is.
//   Only name and route are required.
//   persona: one name or a list (the page is walked once per persona). tabs: the tab names scoping §11 lists for the
//   page; any not found is reported. open: "first-row" (open the first list row, e.g. into a drawer or record page)
//   or a Playwright selector of one control that opens it; its tabs are walked too.
// Without --routes, it discovers links from the app's navigation (nav, aside, [role=navigation]), up to 15.
// Personas: with two or more personas in routes.json, each gets its own browser session. A persona with a session file
//   (--storage-by-persona, or "storage" in personas.json) uses it; otherwise the walk opens the profile menu and picks
//   the persona there ("View as"), or follows personas.json "switch" steps:
//   {"Planner": {"switch": [{"click": "[aria-label='Profile']"}, {"click": "text={persona}"}]}, "Manager": {"storage": "m.json"}}
//   If a persona cannot be switched to, its pages are not walked and the report says so (never walked as someone else).
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
const SETTLE = +arg('settle', 30000), SLOW = +arg('slow', 8000), TAB_DEPTH = +arg('tab-depth', 3), MAX_TABS = +arg('max-tabs', 40);
const STORAGE = arg('storage'), ROUTES = arg('routes'), GLOSSARY = arg('glossary');
const PERSONAS = arg('personas'), STORAGE_BY = arg('storage-by-persona');
const RENDER = fs.readFileSync(path.join(HERE, 'render_check.js'), 'utf8');
const SLOP = JSON.parse(fs.readFileSync(path.join(HERE, 'slop-phrases.json'), 'utf8'));
const PLATFORM = JSON.parse(fs.readFileSync(path.join(HERE, 'platform-errors.json'), 'utf8'));
const NO_ACCESS_TEXT = (PLATFORM.no_access_text || []).map((x) => x.toLowerCase());
const GLOSS = GLOSSARY && fs.existsSync(GLOSSARY) ? JSON.parse(fs.readFileSync(GLOSSARY, 'utf8')) : {};
fs.mkdirSync(path.join(OUT, 'shots'), { recursive: true });

// The app root: the preview link (code apps: …/agent-api/preview/b/<app id>/main) with a trailing "/", no query.
const ROOT = new URL(arg('app-base', URL0)); ROOT.search = ''; ROOT.hash = ''; ROOT.pathname = ROOT.pathname.replace(/\/*$/, '/');
const APP_PATH = ROOT.pathname.replace(/\/$/, '');          // '' when the app sits at the domain root
const extraRoots = [];                                        // where the preview link itself redirected to, if outside ROOT
function resolveRoute(route) {
  const r = String(route ?? '').trim();
  if (/^[a-z][a-z0-9+.-]*:\/\//i.test(r)) return r;                                   // a full address
  if (APP_PATH && (r === APP_PATH || /^[/?#]/.test(r.slice(APP_PATH.length)) && r.startsWith(APP_PATH))) return ROOT.origin + r;
  return new URL(r.replace(/^\.?\/+/, ''), ROOT.href).href;                           // "/orders", "./orders", "orders"
}
const under = (u, root) => { try { const x = new URL(u), b = new URL(root); const bp = b.pathname.replace(/\/$/, '');
  return x.origin === b.origin && (!bp || x.pathname === bp || x.pathname.startsWith(bp + '/')); } catch { return false; } };
const inApp = (u) => under(u, ROOT.href) || extraRoots.some((r) => under(u, r));
// A page that says the signed-in user (or persona) may not see it: the walk cannot review it (not an app pass).
const onSignIn = (u) => { try { return /\/(login|signin|sign-in|auth|sso|oauth)\b/i.test(new URL(u).pathname); } catch { return false; } };

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const firstLine = (e) => String(e).split('\n')[0].slice(0, 200);
const slugify = (s) => String(s || 'page').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 30);

// One deadline for the whole wait, counted from the navigation or click (t0). Network idle is only a short hint:
// apps that poll never reach it. Ready = no visible skeleton/spinner and some text on the page.
async function settle(page, t0 = Date.now(), budget = SETTLE) {
  const deadline = t0 + budget, left = () => Math.max(1, deadline - Date.now());
  await page.waitForLoadState('networkidle', { timeout: Math.min(5000, left()) }).catch(() => {});
  const ok = await page.waitForFunction(() => {
    const vis = (e) => { const b = e.getBoundingClientRect(); return b.height > 0 && b.width > 0 && b.bottom > 0 && b.top < innerHeight; };
    if (!document.body || !document.body.innerText.trim()) return false;
    return ![...document.querySelectorAll('[aria-busy="true"], [class*="skeleton" i], [class*="shimmer" i], [class*="spinner" i]')].some(vis);
  }, null, { timeout: left(), polling: 250 }).then(() => true, () => false);
  const ms = Date.now() - t0;
  await sleep(400); return { ok, ms };
}

// Everything the PM looks at on one screen, measured in the page.
const INSPECT = ({ maxRow, minRows }) => {
  const vis = (e) => { const cs = getComputedStyle(e); if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) return false;
    const b = e.getBoundingClientRect(); return b.width > 0 && b.height > 0; };
  const inView = (e) => { const b = e.getBoundingClientRect(); return b.bottom > 0 && b.top < innerHeight; };
  const label = (e) => (e.innerText || e.getAttribute('aria-label') || e.value || '').trim().replace(/\s+/g, ' ').slice(0, 80);
  const where = (e) => e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\s+/).slice(0, 2).join('.') : '');
  const isSvg = (e) => e instanceof SVGElement;                  // SVG has no innerText: icons and charts are skipped below
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
    .filter((e) => { if (isSvg(e) || !vis(e) || !(e.innerText || '').trim()) return false; const lh = parseFloat(getComputedStyle(e).lineHeight) || parseFloat(getComputedStyle(e).fontSize) * 1.3;
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

  // Numbers shown on badges and KPI tiles, for count reconciliation by the reviewer (never SVG: chart axis ticks are not badges).
  out.badges = [...document.querySelectorAll('nav *, aside *, [class*="badge" i], [class*="count" i], [class*="kpi" i], [class*="tile" i]')]
    .filter((e) => !isSvg(e) && vis(e) && /^\d[\d,]*$/.test((e.innerText || '').trim()) && e.children.length === 0)
    .map((e) => ({ value: e.innerText.trim(), near: label(e.parentElement).slice(0, 60) })).slice(0, 40);

  out.tabs = [...document.querySelectorAll('[role=tab]')].filter(vis).map((t) => ({ name: label(t), selected: t.getAttribute('aria-selected') === 'true' }));
  out.title = (document.querySelector('h1,[role=heading][aria-level="1"]')?.innerText || document.title || '').trim().slice(0, 100);
  return out;
};

// Layout-check noise on a live app: hide these from the render check only (visibility:hidden keeps the layout, and the
// render check skips hidden elements), then restore. render_check.js itself stays a verbatim copy.
//  - screen-reader-only text (1-2 px absolute boxes, clip rect(0 0 0 0), clip-path inset(50%), sr-only class names);
//  - everything inside an <svg> and inside a chart library's wrapper (the chart's own box is still checked);
//  - rotated or skewed text (angled axis labels).
const MARK_NOISE = () => {
  const CHART = /recharts|apexcharts|echarts|highcharts|chartjs|chart-js|nivo|vega|plotly|victory|visx|amcharts|nvd3|c3-chart/i;
  const cls = (e) => (typeof e.className === 'string' ? e.className : e.getAttribute('class')) || '';
  const marked = new Set(), rotated = [];
  for (const root of document.querySelectorAll('body *')) {
    if (!CHART.test(cls(root)) || [...ancestors(root)].some((a) => CHART.test(cls(a)))) continue;   // outermost chart wrapper only
    for (const d of root.querySelectorAll('*')) marked.add(d);
  }
  function* ancestors(e) { for (let n = e.parentElement; n && n !== document.body; n = n.parentElement) yield n; }
  for (const e of document.querySelectorAll('body *')) {
    if (marked.has(e)) continue;
    if (e.closest('svg') && e.tagName.toLowerCase() !== 'svg') { marked.add(e); continue; }
    const cs = getComputedStyle(e);
    if (cs.position === 'absolute' || cs.position === 'fixed') {
      const b = e.getBoundingClientRect();
      if ((b.width <= 2 && b.height <= 2) || /rect\(\s*0(px)?[\s,]+0(px)?[\s,]+0(px)?[\s,]+0(px)?\s*\)/.test(cs.clip) || /inset\(\s*(50|100)%/.test(cs.clipPath)) { marked.add(e); continue; }
    }
    if (/(^|[\s_-])(sr-only|visually-hidden|visuallyhidden|screen-reader)/i.test(cls(e))) { marked.add(e); continue; }
    if (cs.transform && cs.transform !== 'none') {
      const v = (cs.transform.match(/\(([^)]+)\)/) || [])[1]?.split(',').map(Number) || [];
      const [b, c] = cs.transform.startsWith('matrix3d') ? [v[1], v[4]] : [v[1], v[2]];
      if (Math.abs(b || 0) > 0.01 || Math.abs(c || 0) > 0.01) { marked.add(e); rotated.push(e); }
    }
  }
  // the box that holds only angled labels is clipped by design (the label overflows it when rotated)
  for (const e of rotated) {
    const p = e.parentElement; if (!p || p === document.body || marked.has(p)) continue;
    const ownText = [...p.childNodes].some((n) => n.nodeType === 3 && n.nodeValue.trim());
    if (!ownText && [...p.children].every((k) => marked.has(k) || !k.textContent.trim())) marked.add(p);
  }
  window.__bwIgnored = [...marked].map((e) => { const s = [e, e.style.getPropertyValue('visibility'), e.style.getPropertyPriority('visibility')];
    e.style.setProperty('visibility', 'hidden', 'important'); return s; });
  return marked.size;
};
const UNMARK_NOISE = () => {
  for (const [e, v, p] of window.__bwIgnored || []) { if (v) e.style.setProperty('visibility', v, p); else e.style.removeProperty('visibility'); }
  window.__bwIgnored = [];
};

// Every visible tab, grouped by its tab list; each tab is tagged so it can be clicked inside its own list.
const LIST_TABS = () => {
  const vis = (e) => { const cs = getComputedStyle(e); if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) return false;
    const b = e.getBoundingClientRect(); return b.width > 0 && b.height > 0; };
  const name = (t) => (t.innerText || t.getAttribute('aria-label') || t.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 80);
  const lists = new Map(); let n = +(document.body.dataset.bwTl || 0);
  for (const t of document.querySelectorAll('[role=tab]')) {
    if (!vis(t)) continue;
    const list = t.closest('[role=tablist]') || t.parentElement;
    if (!list.dataset.bwTl) list.dataset.bwTl = String(++n);
    if (!lists.has(list)) lists.set(list, []);
    const tabs = lists.get(list); t.dataset.bwTab = `${list.dataset.bwTl}:${tabs.length}`;
    tabs.push({ id: t.dataset.bwTab, name: name(t), selected: t.getAttribute('aria-selected') === 'true',
      disabled: t.getAttribute('aria-disabled') === 'true' || t.disabled === true });
  }
  document.body.dataset.bwTl = String(n);
  return [...lists.values()].map((tabs) => ({ sig: tabs.map((t) => t.name).join(' · '), tabs }));
};

// "open": "first-row" — tag a plain cell of the first list row (not a checkbox, button or input) to click.
const TAG_FIRST_ROW = () => {
  const vis = (e) => { const b = e.getBoundingClientRect(); return b.width > 0 && b.height > 0 && getComputedStyle(e).visibility !== 'hidden'; };
  const row = [...document.querySelectorAll('tbody tr, [role=row]')].find((r) => vis(r) && !r.closest('thead') && !r.querySelector('th,[role=columnheader]'));
  if (!row) return false;
  const cell = [...row.querySelectorAll('td,[role=cell],[role=gridcell]')].find((c) => vis(c) && c.innerText.trim()
    && !c.querySelector('button,input,select,textarea,[role=button],[role=checkbox],[role=switch]')) || row;
  cell.setAttribute('data-bw-open', ''); return true;
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

// ---- state shared by the whole walk ----
const pages = [], consoleErrors = [], failed = [];
const platform = [];      // platform/tenant failures: never app defects, never fix lines for the builder
const walkIssues = [];    // the walk itself could not do something (a check crashed, a persona switch failed)
const notWalked = [];     // pages the walk could not review
const sessions = [];      // per persona: how it was signed in or switched
let stopReason = null, signedOutAt = null;    // set when the walk stops early (routes do not match the preview link)
const early = { visits: 0, left: 0 };

const PERSONA_CFG = PERSONAS && fs.existsSync(PERSONAS) ? JSON.parse(fs.readFileSync(PERSONAS, 'utf8')) : {};
for (const part of (STORAGE_BY || '').split(',').map((x) => x.trim()).filter(Boolean)) {
  const i = part.indexOf('='); if (i > 0) (PERSONA_CFG[part.slice(0, i).trim()] ??= {}).storage = part.slice(i + 1).trim();
}

const launchOpts = { headless: true };
if (process.env.CHROME_PATH) launchOpts.executablePath = process.env.CHROME_PATH;
const browser = await chromium.launch(launchOpts);

async function newSession(persona, storageFile, listen = true) {
  const storage = storageFile && fs.existsSync(storageFile) ? storageFile : STORAGE && fs.existsSync(STORAGE) ? STORAGE : null;
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1, ...(storage ? { storageState: storage } : {}) });
  const page = await context.newPage();
  if (listen) page.on('console', (m) => { if (m.type() === 'error' && !/^Failed to load resource: the server responded with a status of \d+/.test(m.text())) consoleErrors.push({ persona, url: page.url(), text: m.text().slice(0, 200) }); });
  if (listen) page.on('pageerror', (e) => consoleErrors.push({ persona, url: page.url(), text: String(e).slice(0, 200) }));
  if (listen) page.on('response', (r) => { if (r.status() >= 400 && !/favicon|analytics|sentry|hotjar|segment/i.test(r.url())) failed.push({ persona, status: r.status(), url: r.url().slice(0, 160), on: page.url() }); });
  const t0 = Date.now();
  await page.goto(URL0, { waitUntil: 'domcontentloaded', timeout: 60000 }).catch((e) => walkIssues.push({ where: persona || 'start', issue: `preview link did not open: ${firstLine(e)}` }));
  await settle(page, t0);
  const signedOut = onSignIn(page.url());
  if (!signedOut && !inApp(page.url()) && /^https?:/.test(page.url())) {      // the preview link redirected elsewhere
    const u = new URL(page.url()); u.search = ''; u.hash = ''; extraRoots.push(u.href);
    walkIssues.push({ where: 'preview link', issue: `opened ${page.url()}, outside ${ROOT.href}; pages under it count as in the app. If pages leave the app, pass --app-base` });
  }
  const noAccess = signedOut ? null : await noAccessReason(page, null);
  if (noAccess) walkIssues.push({ where: persona ? `${persona} (start page)` : 'start page', blocking: true,
    issue: `no access: the signed-in Orbit user${persona ? ` as ${persona}` : ''} cannot see the app (${noAccess}). Link this user to the app (e.g. add them as a user, agency or partner in its data) or use a persona that has access, then re-run.` });
  return { persona, context, page, storage, signedOut, noAccess, at: page.url() };
}

async function clickVisible(locator, timeout = 4000) {
  const n = Math.min(await locator.count().catch(() => 0), 8);
  for (let i = 0; i < n; i++) { const l = locator.nth(i); if (await l.isVisible().catch(() => false)) { await l.click({ timeout }); return true; } }
  return false;
}

// Switch the signed-in user to a persona: personas.json steps if given, else the profile menu ("View as").
async function switchPersona(page, persona, steps) {
  if (Array.isArray(steps) && steps.length) {
    for (const st of steps) {
      const sel = (typeof st === 'string' ? st : st.click).replaceAll('{persona}', persona);
      await page.locator(sel).first().click({ timeout: 10000 }); await sleep(600);
    }
    await settle(page); return 'personas.json steps';
  }
  const menu = '[role=menu], [role=listbox], [role=dialog], [role=radiogroup], [class*="menu" i], [class*="popover" i], [class*="dropdown" i]';
  const pick = async () => {
    const m = page.locator(menu);
    const opt = m.getByRole('menuitemradio', { name: persona, exact: true }).or(m.getByRole('menuitem', { name: persona, exact: true }))
      .or(m.getByRole('option', { name: persona, exact: true })).or(m.getByRole('radio', { name: persona, exact: true }))
      .or(m.getByRole('button', { name: persona, exact: true })).or(m.getByText(persona, { exact: true }));
    return clickVisible(opt);
  };
  const openers = page.locator('[aria-label*="profile" i], [aria-label*="account" i], [aria-label*="user menu" i], [data-testid*="profile" i], [data-testid*="avatar" i], [class*="avatar" i], [class*="profile" i]');
  const count = Math.min(await openers.count().catch(() => 0), 6);
  for (let i = 0; i < count; i++) {
    const o = openers.nth(i);
    if (!(await o.isVisible().catch(() => false))) continue;
    await o.click({ timeout: 4000 }).catch(() => {}); await sleep(500);
    if (await pick().catch(() => false)) { await settle(page); return 'profile menu'; }
    // a "View as" / "Switch role" submenu first
    if (await clickVisible(page.locator(menu).getByText(/view as|switch (role|persona|user)|change role|^role$/i)).catch(() => false)) {
      await sleep(400); if (await pick().catch(() => false)) { await settle(page); return 'profile menu › view as'; }
    }
    await page.keyboard.press('Escape').catch(() => {}); await sleep(200);
  }
  throw new Error('no persona switch found in the profile menu');
}

// Does this page say the signed-in user (or persona) has no access? HTTP 401/403 on the page itself, or a short page
// (or its headings) saying so. Returns the reason, or null.
async function noAccessReason(page, resp) {
  if (resp && (resp.status() === 401 || resp.status() === 403)) return `the page returned HTTP ${resp.status()}`;
  const t = await page.evaluate(() => ({ body: (document.body?.innerText || '').slice(0, 3000),
    heads: [...document.querySelectorAll('h1,h2,h3,[role=heading],[role=alert]')].map((h) => h.innerText).join(' | ').slice(0, 1000) })).catch(() => ({ body: '', heads: '' }));
  const short = t.body.trim().length < 800, low = (x) => x.toLowerCase();
  const hit = NO_ACCESS_TEXT.find((m) => low(t.heads).includes(m) || (short && low(t.body).includes(m)));
  return hit ? `the page says "${hit}"` : null;
}

// Is the platform (not the app) failing on this attempt?
async function platformReasons(page, resp, navErr, sinceFailed) {
  const reasons = [];
  if (navErr) reasons.push(`page did not open: ${navErr}`);
  if (resp && resp.status() >= 500) reasons.push(`page returned HTTP ${resp.status()}`);
  else if (resp && PLATFORM.statuses.includes(resp.status())) reasons.push(`page returned HTTP ${resp.status()}`);
  if (!navErr) {
    const txt = await page.evaluate(() => ({ title: document.title || '', body: (document.body?.innerText || '').slice(0, 3000) })).catch(() => ({ title: '', body: '' }));
    const hit = PLATFORM.text.find((m) => txt.title.toLowerCase().includes(m) || (txt.body.trim().length < 600 && txt.body.toLowerCase().includes(m)));
    if (hit) reasons.push(`platform error page ("${hit}")`);
  }
  const sub = failed.slice(sinceFailed).filter((f) => PLATFORM.statuses.includes(f.status));
  if (sub.length) reasons.push(`${sub.length} request(s) got HTTP ${[...new Set(sub.map((f) => f.status))].join('/')}`);
  return reasons;
}

async function capture(s, name, slug, t0, settled) {
  const { page, persona } = s;
  const st = settled || await settle(page, t0);
  const shot = path.join('shots', `${slug}.png`);
  await page.screenshot({ path: path.join(OUT, shot) }).catch(() => {});
  let render, ins, checkError;
  try {
    const ignored = await page.evaluate(MARK_NOISE);
    try { render = await page.evaluate(RENDER); } finally { await page.evaluate(UNMARK_NOISE).catch(() => {}); }
    render = { ...render, ignored, fonts: undefined, unstyledClasses: undefined };
  } catch (e) { render = { error: firstLine(e) }; }
  try { ins = await page.evaluate(INSPECT, { maxRow: MAXROW, minRows: MINROWS }); } catch (e) { checkError = firstLine(e); }
  const rec = { persona, name, url: page.url(), shot, loadMs: st.ms, stillLoading: !st.ok, render, ...(ins || {}), checkError, slop: ins ? slopHits(ins.copy) : [] };
  pages.push(rec); return rec;
}

// Did the last navigation or click leave the app? Records it (sign-in page: session; elsewhere: route_left_app).
function leftApp(s, where, expected) {
  const u = s.page.url();
  if (onSignIn(u)) { signedOutAt ??= u; notWalked.push({ persona: s.persona, page: where, why: 'signed out' }); return true; }
  if (inApp(u)) return false;
  walkIssues.push({ where, issue: `route_left_app: expected a page under ${ROOT.href}${expected ? ` (${expected})` : ''}, opened ${u}` });
  notWalked.push({ persona: s.persona, page: where, why: 'route left the app' });
  return true;
}

// Open a page; retry up to 2 times while the platform is failing, dropping what the failed attempt logged.
async function visit(s, r, slug) {
  let attempt = 0, reasons = [], st = null, lastStatus = null, lastMark = null;
  for (;;) {
    const mark = { failed: failed.length, console: consoleErrors.length }; lastMark = mark;
    const t0 = Date.now(); let resp = null, navErr = null;
    const target = resolveRoute(r.route);
    try { resp = await s.page.goto(target, { waitUntil: 'domcontentloaded', timeout: 60000 }); } catch (e) { navErr = firstLine(e); }
    st = navErr ? null : await settle(s.page, t0);
    if (!navErr && attempt === 0) {
      const first = early.visits++ < 2, left = leftApp(s, r.name, target);
      if (left && first && !onSignIn(s.page.url()) && ++early.left >= 2) {
        stopReason = `routes.json does not match the preview link: the first two routes opened outside ${ROOT.href} (e.g. ${target} → ${s.page.url()}). Write routes relative to the preview link ("orders", no leading "/"), or pass --app-base`;
        walkIssues.push({ where: 'routes.json', blocking: true, issue: stopReason });
      }
      if (left) { failed.length = mark.failed; consoleErrors.length = mark.console; return null; }
    }
    reasons = await platformReasons(s.page, resp, navErr, mark.failed);
    lastStatus = resp ? resp.status() : null;
    if (!reasons.length || attempt >= 2) break;
    failed.length = mark.failed; consoleErrors.length = mark.console;
    attempt++; await sleep(5000 * attempt);
  }
  const who = r.name;
  if (reasons.length) {
    platform.push({ persona: s.persona, where: who, route: r.route, attempts: attempt + 1, reasons });
    notWalked.push({ persona: s.persona, page: who, why: 'platform unavailable' });
    if (st) { const rec = await capture(s, who, slug, 0, st); rec.platformDown = reasons; }
    return null;
  }
  const denied = (lastStatus === 401 || lastStatus === 403) ? `the page returned HTTP ${lastStatus}` : await noAccessReason(s.page, null);
  if (denied) {
    const rec = await capture(s, who, slug, 0, st); rec.noAccess = denied;
    failed.length = lastMark.failed; consoleErrors.length = lastMark.console;   // its 401/403 is not an app defect
    if (!(s.noAccess && rec.url === s.at)) walkIssues.push({ where: who, issue: `no access: ${denied}. If scoping §11 gives this ${s.persona ? `persona (${s.persona})` : 'user'} the page, confirm it on the screenshot as an app defect; otherwise fix the account or the route's persona`, shot: rec.shot });
    notWalked.push({ persona: s.persona, page: who, why: 'no access' });
    return null;
  }
  return capture(s, who, slug, 0, st);
}

async function walkTabs(s, base, slug, trail, depth, ancestors, seen, budget) {
  if (depth > TAB_DEPTH) return;
  const lists = (await s.page.evaluate(LIST_TABS).catch(() => [])).filter((l) => !ancestors.has(l.sig));
  const here = new Set([...ancestors, ...lists.map((l) => l.sig)]);
  for (const [li, L] of lists.entries()) {
    for (const [ti, t] of L.tabs.entries()) {
      if (t.name) seen.add(t.name.toLowerCase());
      if (t.selected || !t.name || t.disabled) continue;
      if (budget.left-- <= 0) {
        if (!budget.warned) { budget.warned = true; walkIssues.push({ where: base, issue: `stopped after ${MAX_TABS} tabs on this page (--max-tabs)` }); }
        return;
      }
      const label = `${base} › ${[...trail, t.name].join(' › ')}`, tslug = `${slug}-t${li + 1}-${ti + 1}`;
      try {
        const fresh = (await s.page.evaluate(LIST_TABS)).find((l) => l.sig === L.sig)?.tabs.find((x) => x.name === t.name);
        if (!fresh) throw new Error('the tab is no longer on the page');
        const t0 = Date.now();
        const back = s.page.url(), markF = failed.length, markC = consoleErrors.length;
        await s.page.locator(`[data-bw-tab="${fresh.id}"]`).first().click({ timeout: 5000 });
        await s.page.waitForLoadState('domcontentloaded', { timeout: 5000 }).catch(() => {});
        if (leftApp(s, label, `tab "${t.name}"`)) { failed.length = markF; consoleErrors.length = markC; await s.page.goto(back, { waitUntil: 'domcontentloaded', timeout: 60000 }).catch(() => {}); await settle(s.page); continue; }
        await capture(s, label, tslug, t0);
      } catch (e) { pages.push({ persona: s.persona, name: label, error: `tab did not respond to a click: ${firstLine(e)}` }); continue; }
      await walkTabs(s, base, tslug, [...trail, t.name], depth + 1, here, seen, budget);
    }
    const orig = L.tabs.find((x) => x.selected);              // leave the list as it was
    if (orig) {
      const fresh = (await s.page.evaluate(LIST_TABS).catch(() => [])).find((l) => l.sig === L.sig)?.tabs.find((x) => x.name === orig.name);
      if (fresh) { await s.page.locator(`[data-bw-tab="${fresh.id}"]`).first().click({ timeout: 5000 }).catch(() => {}); await settle(s.page, Date.now(), 8000); }
    }
  }
}

// ---- routes, personas ----
let routes = ROUTES && fs.existsSync(ROUTES) ? JSON.parse(fs.readFileSync(ROUTES, 'utf8')) : null;
let discovery = null;
if (!routes) {
  discovery = await newSession(null);
  routes = await discovery.page.evaluate(() => [...document.querySelectorAll('nav a[href], aside a[href], [role=navigation] a[href]')]
    .map((a) => ({ name: (a.innerText || a.getAttribute('aria-label') || '').trim().slice(0, 40), route: a.href }))
    .filter((r, i, all) => r.name && all.findIndex((x) => x.route === r.route) === i)).catch(() => []);
  if (!routes.length) routes = [{ name: 'Start', route: URL0 }];
  routes = routes.slice(0, 15);
}
const expanded = [];
for (const r of routes) for (const p of (Array.isArray(r.persona) ? r.persona : r.persona ? [r.persona] : [null])) expanded.push({ ...r, persona: p });
const personaOrder = [...new Set(expanded.map((r) => r.persona))];
const named = personaOrder.filter(Boolean);
const mustSwitch = named.length >= 2;          // one persona (or none): walk as the signed-in user
let switchedOnce = false;

for (const persona of personaOrder) {
  if (stopReason) { for (const r of expanded.filter((x) => x.persona === persona)) notWalked.push({ persona, page: persona && mustSwitch ? `[${persona}] ${r.name}` : r.name, why: 'walk stopped' }); continue; }
  const group = expanded.filter((r) => r.persona === persona);
  const cfg = (persona && PERSONA_CFG[persona]) || {};
  if (cfg.storage && !fs.existsSync(cfg.storage)) walkIssues.push({ where: persona, issue: `session file not found: ${cfg.storage}` });
  const s = persona === null && discovery ? discovery : await newSession(persona, cfg.storage);
  if (s.signedOut) signedOutAt ??= s.at;
  let how = cfg.storage && fs.existsSync(cfg.storage) ? `session file ${path.basename(cfg.storage)}` : 'signed-in user';
  if (persona && mustSwitch && !(cfg.storage && fs.existsSync(cfg.storage)) && !s.signedOut) {
    try { how = await switchPersona(s.page, persona, cfg.switch); switchedOnce = true; }
    catch (e) {
      sessions.push({ persona, how: 'switch failed', error: firstLine(e) });
      walkIssues.push({ where: persona, blocking: true, issue: `could not switch to ${persona} (${firstLine(e)}); its ${group.length} page(s) were not walked. Add "switch" steps for it in personas.json, or a session file with --storage-by-persona.` });
      for (const r of group) notWalked.push({ persona, page: `[${persona}] ${r.name}`, why: 'persona switch failed' });
      await s.context.close(); continue;
    }
  }
  sessions.push({ persona, how });
  const pre = persona ? `${slugify(persona)}--` : '';
  for (const [i, r] of group.entries()) {
    if (stopReason) { notWalked.push({ persona, page: persona && mustSwitch ? `[${persona}] ${r.name}` : r.name, why: 'walk stopped' }); continue; }
    const slug = `${pre}${String(routes.indexOf(routes.find((x) => x.name === r.name && x.route === r.route)) + 1).padStart(2, '0')}-${slugify(r.name)}`;
    const name = persona && mustSwitch ? `[${persona}] ${r.name}` : r.name;
    try {
      const rec = await visit(s, { ...r, name }, slug);
      if (!rec) continue;
      const seen = new Set(), budget = { left: MAX_TABS };
      await walkTabs(s, name, slug, [], 1, new Set(), seen, budget);
      if (r.open) {
        let leftOnOpen = false;
        const markF = failed.length, markC = consoleErrors.length;
        try {
          const t0 = Date.now();
          if (r.open === 'first-row') {
            if (!(await s.page.evaluate(TAG_FIRST_ROW))) throw new Error('no list row on the page');
            await s.page.locator('[data-bw-open]').first().click({ timeout: 5000 });
          } else await s.page.locator(r.open).first().click({ timeout: 5000 });
          const oname = `${name} › (opened)`;
          await s.page.waitForLoadState('domcontentloaded', { timeout: 5000 }).catch(() => {});
          if (leftApp(s, oname, `open "${r.open}"`)) { leftOnOpen = true; failed.length = markF; consoleErrors.length = markC; throw new Error('the click left the app'); }
          await capture(s, oname, `${slug}-open`, t0);
          await walkTabs(s, oname, `${slug}-open`, [], 1, new Set(), seen, budget);
        } catch (e) { if (!leftOnOpen) pages.push({ persona, name: `${name} › (opened)`, error: `could not open "${r.open}": ${firstLine(e)}` }); }
      }
      const want = (r.tabs || []).filter((t) => !seen.has(String(t).toLowerCase()));
      if (want.length) pages.push({ persona, name, missingTabs: want });
    } catch (e) { pages.push({ persona, name, url: r.route, error: firstLine(e) }); }
  }
  await s.context.close();
}
// Leave the app on the first persona when the walk switched personas in the app itself.
if (switchedOnce && named.length) {
  const cfg = PERSONA_CFG[named[0]] || {};
  if (!(cfg.storage && fs.existsSync(cfg.storage))) {
    const s = await newSession(named[0], null, false);
    await switchPersona(s.page, named[0], cfg.switch).catch((e) => walkIssues.push({ where: named[0], issue: `could not switch back to ${named[0]} at the end: ${firstLine(e)}` }));
    await s.context.close();
  }
}
await browser.close();

// ---- findings the reviewer starts from (candidates — it confirms each against the screenshot before keeping it) ----
const F = [];
const add = (dimension, blocking, where, evidence, fix) => F.push({ id: `W${F.length + 1}`, dimension, blocking, where, evidence, fix });
if (signedOutAt) add('R9', true, 'session', `the preview opened on ${signedOutAt}`, 'Sign in to Orbit (orbit_signin.mjs) and re-run the walk');
for (const p of pages) {
  if (p.missingTabs) { add('R2', true, p.name, `tabs in scoping §11 not found on the page: ${p.missingTabs.join(', ')}`, 'Build the listed tabs, or record the cut'); continue; }
  if (p.error) { add('R7', true, p.name, p.error, 'Make the page/tab open without error'); continue; }
  if (p.platformDown || p.noAccess) continue;                     // listed under Platform / Walk problems, not app defects
  const r = p.render || {};
  if (r.error) walkIssues.push({ where: p.name, issue: `render check failed: ${r.error}`, shot: p.shot });
  if (p.checkError) walkIssues.push({ where: p.name, issue: `page check failed: ${p.checkError}`, shot: p.shot });
  if (p.stillLoading) add('R7', true, p.name, `never finished loading within ${SETTLE / 1000} s (skeleton, spinner or blank page still showing)`, 'Make the page finish loading, or show a designed loading state that ends');
  else if (p.loadMs > SLOW) add('R7', false, p.name, `slow: loaded after ${(p.loadMs / 1000).toFixed(1)} s (over ${SLOW / 1000} s)`, 'Open it again warm; if it is still slow, lighten what the page loads first');
  for (const k of ['spills', 'clipped', 'vclipped', 'overlaps', 'squeezed', 'brokenImages']) if (r[k] > 0)
    add('R8', k !== 'squeezed' || r[k] > 3, p.name, `${r[k]} ${k}: ${(r.where || []).filter((w) => w.startsWith(k)).slice(0, 3).join(' | ')}`, `Fix the ${k} elements listed`);
  if (p.checkError) continue;                                     // no page measurements to judge
  if (p.hScroll > 2) add('R8', true, p.name, `horizontal page scroll of ${p.hScroll}px at 1280px`, 'Fit the page to 1280px; let wide tables scroll inside their own container');
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
const downUrls = new Set(pages.filter((p) => p.platformDown || p.noAccess).map((p) => p.url));
for (const e of consoleErrors.filter((x) => !downUrls.has(x.url))) (byPage[(e.persona && mustSwitch ? `[${e.persona}] ` : '') + e.url] ??= []).push(e.text);
for (const [u, errs] of Object.entries(byPage)) add('R7', false, u, `${errs.length} console errors, e.g. ${errs[0]}`, 'Fix the script errors');
const platformReq = failed.filter((f) => PLATFORM.statuses.includes(f.status)), appReq = failed.filter((f) => !PLATFORM.statuses.includes(f.status));
for (const f of appReq.slice(0, 15)) add('R7', f.status >= 500, f.on, `HTTP ${f.status} on ${f.url}`, 'Fix the failing request');
if (platformReq.length) platform.push({ where: 'requests', reasons: [...new Set(platformReq.map((f) => `HTTP ${f.status} on ${f.url}`))].slice(0, 15) });

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

// Incomplete: the report cannot carry an approve/reject (signed out, a persona not walked, or half the pages unreviewed).
const incomplete = !!stopReason || !!signedOutAt || walkIssues.some((w) => w.blocking) || notWalked.length * 2 >= Math.max(1, expanded.length);
fs.writeFileSync(path.join(OUT, 'copy.json'), JSON.stringify(pages.filter((p) => p.copy).map((p) => ({ persona: p.persona, page: p.name, copy: p.copy })), null, 2));
fs.writeFileSync(path.join(OUT, 'report.json'), JSON.stringify({ url: URL0, appRoot: ROOT.href, at: new Date().toISOString(), settleMs: SETTLE, incomplete, stopped: stopReason, sessions,
  pages: pages.map(({ copy, ...p }) => p), consoleErrors, failed: appReq, platform, walkIssues, notWalked, findings: F }, null, 2));
const cell = (p) => ['spills', 'clipped', 'vclipped', 'overlaps', 'squeezed'].map((k) => p.render?.[k] ?? '?').join('/');
const md = [`# Build walk — ${URL0}`, '',
  `App root: ${ROOT.href}`, '',
  ...(stopReason ? [`**STOPPED — ${stopReason}**`, ''] : []),
  ...(incomplete ? ['**INCOMPLETE — re-run the walk before approving or rejecting the build on this report** (see Not walked and Walk problems).', ''] : []),
  `${pages.length} screens · ${F.length} candidate findings (${F.filter((f) => f.blocking).length} blocking) · ${platform.length} platform failures · ${walkIssues.length} walk problems`, '',
  ...(sessions.length > 1 || sessions.some((x) => x.persona) ? ['Personas: ' + sessions.map((x) => `${x.persona ?? 'signed-in user'} (${x.how})`).join(' · '), ''] : []),
  '| # | Screen | Shot | Load | Render (spill/clip/vclip/overlap/squeeze) | Rows (tall/total) | Raw | Disabled w/o reason | Stripes | Slop |', '|---|---|---|---|---|---|---|---|---|---|',
  ...pages.filter((p) => !p.missingTabs).map((p, i) => p.error ? `| ${i + 1} | ${p.name} | — | | **error:** ${p.error} | | | | | |`
    : p.platformDown ? `| ${i + 1} | ${p.name} | ${p.shot} | | **platform unavailable** | | | | | |`
    : p.noAccess ? `| ${i + 1} | ${p.name} | ${p.shot} | | **no access** | | | | | |`
    : p.checkError ? `| ${i + 1} | ${p.name} | ${p.shot} | ${(p.loadMs / 1000).toFixed(1)} s | ${cell(p)} | **check failed** | | | | |`
    : `| ${i + 1} | ${p.name} | ${p.shot} | ${p.stillLoading ? 'never' : (p.loadMs / 1000).toFixed(1) + ' s'} | ${cell(p)} | ${p.tallRows}/${p.rows} | ${p.raw.length} | ${p.disabledNoReason.length} | ${p.sideStripes.length} | ${p.slop.length} |`),
  '', '## Candidate findings', '', ...F.map((f) => `- **${f.id}** ${f.blocking ? '[blocking] ' : ''}${f.dimension} · ${f.where} — ${f.evidence} → ${f.fix}`),
  '', '## Platform (tenant_unavailable)', '', 'Platform or tenant failures after retries. Not app defects: never send these to UnifyApps Headless as fix lines; re-run the walk later.', '',
  ...(platform.length ? platform.map((x) => `- ${x.where}${x.attempts ? ` (${x.attempts} tries)` : ''} — ${x.reasons.join('; ')}`) : ['- none']),
  '', '## Walk problems', '', 'Things the walk itself could not do. Not app defects.', '',
  ...(walkIssues.length ? walkIssues.map((w) => `- ${w.blocking ? '[blocking] ' : ''}${w.where} — ${w.issue}${w.shot ? ` (screenshot: ${w.shot})` : ''}`) : ['- none']),
  '', '## Not walked', '', ...(notWalked.length ? notWalked.map((n) => `- ${n.page} — ${n.why}`) : ['- none'])];
fs.writeFileSync(path.join(OUT, 'report.md'), md.join('\n') + '\n');
console.log(`${OUT}/report.md: ${incomplete ? 'INCOMPLETE, ' : ''}${pages.length} screens, ${F.length} candidate findings (${F.filter((f) => f.blocking).length} blocking), ${platform.length} platform failures, ${walkIssues.length} walk problems`);
process.exit(incomplete ? 3 : 0);
