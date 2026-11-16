// kit/lib.mjs: browser, visible cursor, human-paced actions. Shared by auth, run (capture/record).
import { chromium } from 'playwright';
import fs from 'node:fs';

export const W = 1920, H = 1080;
export const readJSON = (p, d) => (fs.existsSync(p) ? JSON.parse(fs.readFileSync(p, 'utf8')) : d);
export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export async function launch({ headless = true } = {}) {
  const opts = { headless, args: ['--hide-scrollbars', '--force-device-scale-factor=1'] };
  if (process.env.CHROME_PATH) opts.executablePath = process.env.CHROME_PATH;
  else if (process.env.CHROME_CHANNEL) opts.channel = process.env.CHROME_CHANNEL; // e.g. "chrome"
  return chromium.launch(opts);
}

// Drawn into every document: an arrow cursor that follows the real mouse, a ripple on click,
// a glow overlay for highlights, and the sync flash. None of it changes the page's scale.
// It also resets every scrolled pane to the top when the app changes route, so a new screen never
// opens half-way down because the app remembered the last page's scroll (set window.__keepScroll to opt out).
export const OVERLAY = `(() => {
  const css = \`#__cur{position:fixed;z-index:2147483647;pointer-events:none;width:26px;height:26px;left:0;top:0;
    transform:translate(-3px,-2px);filter:drop-shadow(0 2px 3px rgba(0,0,0,.35));transition:opacity .2s}
  .__rip{position:fixed;z-index:2147483646;pointer-events:none;width:14px;height:14px;margin:-7px 0 0 -7px;border-radius:50%;
    border:3px solid rgba(78,88,45,.85);animation:__r .55s ease-out forwards}
  @keyframes __r{to{transform:scale(3.2);opacity:0}}
  .__glow{position:fixed;z-index:2147483645;pointer-events:none;border-radius:10px;
    box-shadow:0 0 0 3px #847347,0 0 0 9px rgba(132,115,71,.28),0 0 28px 8px rgba(132,115,71,.35);opacity:0;transition:opacity .35s}\`;
  const add = () => {
    if (document.getElementById('__cur') || !document.body) return;
    const s = document.createElement('style'); s.textContent = css; document.head.appendChild(s);
    const c = document.createElement('div'); c.id = '__cur';
    c.innerHTML = '<svg viewBox="0 0 24 24" width="26" height="26"><path d="M3 2l7.5 19 2.6-7.6L21 10.8z" fill="#fff" stroke="#111" stroke-width="1.6" stroke-linejoin="round"/></svg>';
    document.body.appendChild(c);
    let p = null; try { p = JSON.parse(sessionStorage.getItem('__curpos')); } catch (e) {}
    if (p) c.style.left = p[0] + 'px', c.style.top = p[1] + 'px';
  };
  document.addEventListener('DOMContentLoaded', add); setInterval(add, 300);
  addEventListener('mousemove', (e) => { const c = document.getElementById('__cur'); if (!c) return;
    c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px';
    try { sessionStorage.setItem('__curpos', JSON.stringify([e.clientX, e.clientY])); } catch (x) {} }, true);
  addEventListener('mousedown', (e) => { const r = document.createElement('div'); r.className = '__rip';
    r.style.left = e.clientX + 'px'; r.style.top = e.clientY + 'px'; document.body.appendChild(r);
    setTimeout(() => r.remove(), 700); }, true);
  const top = () => { if (window.__keepScroll) return; scrollTo(0, 0);
    for (const e of document.querySelectorAll('*')) if (e.scrollTop > 0 && e.scrollHeight > e.clientHeight) e.scrollTop = 0; };
  const onNav = () => { [0, 60, 180, 400, 800].forEach((ms) => setTimeout(top, ms)); };
  for (const k of ['pushState', 'replaceState']) { const o = history[k];
    history[k] = function (...a) { const before = location.pathname + location.search; const r = o.apply(this, a);
      if (location.pathname + location.search !== before) onNav(); return r; }; }
  addEventListener('popstate', onNav); addEventListener('hashchange', onNav);
  window.__glow = (el, ms) => { const g = document.createElement('div'); g.className = '__glow'; document.body.appendChild(g);
    let on = true; const place = () => { if (!on) return; const b = el.getBoundingClientRect();
      Object.assign(g.style, { left: b.left - 6 + 'px', top: b.top - 6 + 'px', width: b.width + 12 + 'px', height: b.height + 12 + 'px' });
      requestAnimationFrame(place); };
    place(); requestAnimationFrame(() => (g.style.opacity = 1));
    setTimeout(() => { g.style.opacity = 0; setTimeout(() => { on = false; g.remove(); }, 400); }, ms); };
  window.__flash = (on) => { let f = document.getElementById('__flash');
    if (on) { f = document.createElement('div'); f.id = '__flash';
      f.style.cssText = 'position:fixed;inset:0;background:#FF00FF;z-index:2147483647'; document.documentElement.appendChild(f); }
    else if (f) f.remove(); };
})();`;

// target spec -> Locator. {role,name} | {text} | {label} | {placeholder} | {testid} | {css}; optional nth / within
export function loc(page, t) {
  if (typeof t === 'string') return page.locator(t).first();
  let root = t.within ? loc(page, t.within) : page;
  let l = t.role ? root.getByRole(t.role, { name: t.name, exact: t.exact ?? false })
    : t.text ? root.getByText(t.text, { exact: t.exact ?? false })
    : t.label ? root.getByLabel(t.label)
    : t.placeholder ? root.getByPlaceholder(t.placeholder)
    : t.testid ? root.getByTestId(t.testid)
    : root.locator(t.css);
  return t.nth != null ? l.nth(t.nth) : l.first();
}

// Wait until the screen has really painted: network quiet, and no loading skeleton / spinner left.
// Returns false (and the caller logs SLOW) if something still looks busy after `ms`.
export async function settled(page, ms = 6000) {
  await page.waitForLoadState('networkidle', { timeout: ms }).catch(() => {});
  const ok = await page.waitForFunction(() => {
    const vis = (e) => { const b = e.getBoundingClientRect(); return b.height > 0 && b.width > 0 && b.bottom > 0 && b.top < innerHeight; };
    return ![...document.querySelectorAll('[aria-busy="true"], [class*="skeleton" i], [class*="shimmer" i], [class*="spinner" i]')].some(vis);
  }, null, { timeout: ms }).then(() => true, () => false);
  await sleep(350);
  return ok;
}

export class Engine {
  constructor(page, log = console.log) { this.page = page; this.log = log; this.mx = W / 2; this.my = H / 2; this.marks = []; }

  mark(kind, b) { if (b) this.marks.push({ t: Date.now(), kind, y0: Math.round(b.y), y1: Math.round(b.y + b.height) }); }
  async moveTo(x, y) {
    const d = Math.hypot(x - this.mx, y - this.my);
    const steps = Math.max(12, Math.min(40, Math.round(d / 30)));
    await this.page.mouse.move(x, y, { steps });
    this.mx = x; this.my = y;
  }
  async centre(l) {
    // Bring the element to the middle with a real smooth scroll of whatever pane holds it.
    await l.waitFor({ state: 'visible', timeout: 15000 });
    const moved = await l.evaluate((el) => {
      const b = el.getBoundingClientRect();
      const off = b.top < 80 || b.bottom > innerHeight - 80;
      if (off) el.scrollIntoView({ block: 'center', behavior: 'smooth' });
      return off;
    });
    if (moved) await sleep(700);
    return l.boundingBox();
  }
  async point(l) { const b = await this.centre(l); await this.moveTo(b.x + b.width / 2, b.y + b.height / 2); return b; }
  // Move the cursor off the thing being read so it never sits on top of the words.
  async park(b) {
    const x = Math.min(W - 40, b.x + b.width + 36), y = Math.min(H - 60, b.y + b.height + 28);
    await this.moveTo(x, y);
  }

  async run(a) {
    try { await this.act(a); }
    catch (e) { throw new Error(`${a.do} ${JSON.stringify(a.target ?? a.to ?? a.text ?? a.url ?? '')}: ${e.message.split('\n')[0]}`); }
  }
  async act(a) {
    const p = this.page;
    switch (a.do) {
      case 'click': { const b = await this.point(loc(p, a.target)); this.mark('click', b); await sleep(220);
        await p.mouse.down(); await sleep(70); await p.mouse.up();
        if (a.nav && !(await settled(p))) this.log(`SLOW screen still loading after click ${JSON.stringify(a.target)}`); break; }
      case 'hover': { this.mark('hover', await this.point(loc(p, a.target))); break; }
      case 'type': { if (a.target) { await this.run({ do: 'click', target: a.target }); await sleep(250); }
        await p.keyboard.type(a.text, { delay: a.delay ?? 55 }); break; }
      case 'press': { await p.keyboard.press(a.key); break; }
      case 'select': { this.mark('select', await this.point(loc(p, a.target))); await sleep(200);
        await loc(p, a.target).selectOption(a.option); break; }
      case 'scroll': { // wheel the pane under the cursor; {to: target} or {by: px}
        if (a.pane) await this.point(loc(p, a.pane));
        let remaining = a.by ?? 0;
        if (a.to) { const l = loc(p, a.to); await l.waitFor({ state: 'attached' });
          const b = await l.boundingBox(); remaining = b ? b.y + b.height / 2 - H / 2 : 0; }
        const step = 110 * Math.sign(remaining);
        for (let n = Math.abs(Math.round(remaining / 110)); n > 0; n--) { await p.mouse.wheel(0, step); await sleep(45); }
        await sleep(350); break; }
      case 'highlight': { const l = loc(p, a.target); const b = await this.centre(l);
        if (a.point !== false) await this.point(l);
        this.mark('highlight', b);
        await l.evaluate((el, ms) => window.__glow(el, ms), a.ms ?? 2200);
        if (a.park !== false) { await sleep(250); await this.park(await l.boundingBox() ?? b); }
        await sleep(a.hold ?? 300); break; }
      case 'waitFor': { if (a.text) await p.getByText(a.text, { exact: false }).first().waitFor({ timeout: a.timeout ?? 30000 });
        else await loc(p, a.target).waitFor({ timeout: a.timeout ?? 30000 }); break; }
      case 'settle': { if (!(await settled(p, a.timeout ?? 6000))) this.log('SLOW screen still loading'); break; }
      case 'wait': { await sleep(a.ms); break; }
      case 'goto': { this.log(`GOTO ${a.url} (reason: ${a.reason})`); await p.goto(a.url, { waitUntil: 'networkidle' }); await settled(p); break; }
      case 'custom': { const mod = await import(new URL('../actions.mjs', import.meta.url)); await mod[a.fn]({ page: p, engine: this, ...a }); break; }
      default: throw new Error(`unknown action ${a.do}`);
    }
  }
}
