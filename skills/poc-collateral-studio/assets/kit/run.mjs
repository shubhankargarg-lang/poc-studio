// kit/run.mjs: capture (fast dry-run + screenshots + screen text) or record (real-time, narrated timing, video).
// usage: node kit/run.mjs capture|record      ACTS=B,C node kit/run.mjs record   (re-record only those acts)
//
// Each scene runs in two parts:
//   1. "pre" actions (navigation that opens the scene's screen) run BEFORE the voice starts, then the
//      recorder waits for the screen to finish loading. The film shows the click; the voice starts on the new screen.
//   2. the rest run under the narration, each on its `at` word.
import fs from 'node:fs';
import { launch, Engine, OVERLAY, readJSON, sleep, settled, loc, W, H } from './lib.mjs';
import { lint } from './lint.mjs';

const mode = process.argv[2];
if (!['capture', 'record'].includes(mode)) throw new Error('mode must be capture or record');
const story = readJSON('story.json'), brief = readJSON('brief.json');
const narr = readJSON('build/narration.json', {});
const only = process.env.ACTS ? process.env.ACTS.split(',') : null;
for (const d of ['build/shots', 'build/raw', 'build/text']) fs.mkdirSync(d, { recursive: true });
const logf = fs.createWriteStream(`build/${mode}.log`, { flags: only ? 'a' : 'w' }); // a full run starts a fresh log
const log = (...m) => { const s = m.join(' '); console.log(s); logf.write(s + '\n'); };

const { errs } = lint();
if (errs.length) { errs.forEach((e) => log('LINT', e)); process.exit(1); }
if (mode === 'record') {
  const missing = story.acts.flatMap((a) => a.scenes).filter((s) => !narr[s.id]);
  if (missing.length) throw new Error(`no narration for ${missing.map((s) => s.id)}; run kit/narrate.py first`);
}
let actions = {}; try { actions = await import(new URL('../actions.mjs', import.meta.url)); } catch {}

const browser = await launch();
const timeline = readJSON('build/timeline.json', {}), report = readJSON('build/capture.json', {});

async function context(persona, video) {
  const p = brief.personas[persona];
  const opts = { viewport: { width: W, height: H }, deviceScaleFactor: 1 };
  if (fs.existsSync(`auth/${persona}.json`)) opts.storageState = `auth/${persona}.json`;
  if (video) opts.recordVideo = { dir: 'build/raw/_tmp', size: { width: W, height: H } };
  const ctx = await browser.newContext(opts);
  if (brief.keepScrollOnNav) await ctx.addInitScript(() => { window.__keepScroll = true; });
  await ctx.addInitScript(OVERLAY);
  if (p.localStorage) await ctx.addInitScript((kv) => { for (const [k, v] of Object.entries(kv)) localStorage.setItem(k, v); }, p.localStorage);
  return ctx;
}

// What is on screen, as text, for the consistency check (check.py): visible text only, overlays excluded.
const screenText = (page) => page.evaluate(() => {
  const out = []; const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (walk.nextNode()) { const n = walk.currentNode, el = n.parentElement; const t = n.textContent.trim();
    if (!t || !el || el.closest('#__cur,.__glow,#__ring,script,style')) continue;
    const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    out.push(t); }
  return out.join('\n');
});

for (const act of story.acts) {
  if (only && !only.includes(act.id)) continue;
  log(`\n== ${mode} act ${act.id}: ${act.title}`);
  const base = brief.personas[act.persona].url;
  if (actions.prepare?.[act.id]) { // stage demo data off camera
    const c = await context(act.persona, false); await actions.prepare[act.id]({ page: await c.newPage(), base }); await c.close();
  }
  const ctx = await context(act.persona, mode === 'record');
  const page = await ctx.newPage();
  const t0 = Date.now(), eng = new Engine(page, log);
  await page.goto(new URL(act.start, base).href, { waitUntil: 'networkidle' }); // the only URL jump: before the clock
  if (!(await settled(page))) log(`SLOW act ${act.id} start screen still loading`);
  await sleep(act.settle ?? 1000);
  await page.mouse.move(W / 2, H / 2);
  let clock = 0; const scenes = [];
  if (mode === 'record') { // sync flash: build.py finds it and starts the act on the frame after it
    await page.evaluate(() => window.__flash(true)); await sleep(400);
    await page.evaluate(() => window.__flash(false)); clock = (Date.now() - t0) / 1000;
  }
  let failed = false;
  for (const s of act.scenes) {
    if (failed) { report[s.id] = { ok: false, error: 'skipped after earlier failure' }; continue; }
    const start = Date.now(), n = narr[s.id] ?? { dur: 0, cues: {} }; let step = 0, voice = start;
    eng.marks = [];
    const pre = (s.actions ?? []).filter((a) => a.pre), main = (s.actions ?? []).filter((a) => !a.pre);
    async function stepShot(a) { // walkthrough step shot with a numbered ring
      if (mode !== 'capture' || !['click', 'type', 'select'].includes(a.do) || !a.target) return;
      step += 1;
      try {
        const box = await eng.centre(loc(page, a.target));
        await page.evaluate(([b, n]) => { const r = document.createElement('div'); r.id = '__ring';
          r.style.cssText = `position:fixed;z-index:2147483647;pointer-events:none;left:${b.x - 8}px;top:${b.y - 8}px;width:${b.width + 16}px;height:${b.height + 16}px;border:4px solid #847347;border-radius:12px`;
          r.innerHTML = `<b style="position:absolute;left:-22px;top:-22px;width:40px;height:40px;border-radius:50%;background:#4E582D;color:#fff;font:600 22px Georgia;display:grid;place-items:center">${n}</b>`;
          document.body.appendChild(r); }, [box, step]);
        await page.screenshot({ path: `build/shots/${s.id}_s${step}.png` });
        await page.evaluate(() => document.getElementById('__ring')?.remove());
      } catch {}
    }
    try {
      for (const a of pre) { await stepShot(a); await eng.run(a); }
      if (pre.length && !(await settled(page))) log(`SLOW ${s.id}: screen still loading when the voice starts`);
      voice = Date.now();
      for (const a of main) {
        if (mode === 'record' && a.at) {
          const due = voice + (n.cues[a.at] ?? 0) * 1000 + (a.lead ?? -250);
          const wait = due - Date.now();
          if (wait > 0) await sleep(wait); else if (wait < -700) log(`LATE CUE ${s.id} "${a.at}" by ${(-wait / 1000).toFixed(1)} s`);
        }
        await stepShot(a);
        await eng.run(a);
      }
      if (mode === 'record') {
        const target = n.dur * 1000 + (s.pad ?? 700), used = Date.now() - voice;
        if (used > target) log(`OVERRUN ${s.id}: actions ${(used / 1000).toFixed(1)} s > line ${(target / 1000).toFixed(1)} s`);
        else await sleep(target - used);
      } else await sleep(s.settle ?? 600);
      await page.screenshot({ path: `build/shots/${s.id}.png` });
      if (mode === 'capture') fs.writeFileSync(`build/text/${s.id}.txt`, await screenText(page));
      report[s.id] = { ok: true }; log(`ok   ${s.id}`);
    } catch (e) {
      failed = true; report[s.id] = { ok: false, error: e.message.split('\n')[0] };
      fs.mkdirSync('build/fail', { recursive: true }); await page.screenshot({ path: `build/fail/${s.id}.png` }).catch(() => {});
      log(`FAIL ${s.id}: ${report[s.id].error}`);
    }
    const rel = (t) => (t - t0) / 1000;
    scenes.push({ id: s.id, start: rel(start), voice: rel(voice), end: rel(Date.now()),
      marks: eng.marks.map((m) => ({ ...m, t: rel(m.t) })) });
  }
  await sleep(900);
  const end = (Date.now() - t0) / 1000, video = page.video();
  await ctx.close();
  if (mode === 'record') {
    const out = `build/raw/${act.id}.webm`;
    await video.saveAs(out); await video.delete();
    timeline[act.id] = { video: out, clock, end, scenes, failed };
  }
}
await browser.close();
fs.writeFileSync('build/capture.json', JSON.stringify(report, null, 2));
if (mode === 'record') fs.writeFileSync('build/timeline.json', JSON.stringify(timeline, null, 2));
const bad = Object.entries(report).filter(([, r]) => !r.ok);
log(bad.length ? `\n${bad.length} scene(s) failing: ${bad.map(([k]) => k)}` : '\nall scenes green');
process.exit(bad.length ? 1 : 0);
