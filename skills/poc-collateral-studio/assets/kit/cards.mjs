// kit/cards.mjs: opening, act and closing cards + the "Powered and built by UnifyApps" badge, in the theme.
// usage: node kit/cards.mjs   -> build/cards/*.png, build/cards/badge.png
import fs from 'node:fs';
import { png, done, footer, md } from './render.mjs';
import { readJSON as rj } from './lib.mjs';

const story = rj('story.json'), brief = rj('brief.json');
fs.mkdirSync('build/cards', { recursive: true });
const frame = (inner) => `<div class="canvas" style="width:1920px;height:1080px;position:relative;padding:150px 170px">${inner}${footer('', 2)}</div>`;

const o = story.opening ?? {};
await png(frame(`
  <div class="eyebrow" style="font-size:30px">${md(o.eyebrow ?? `${brief.customer} · Proof of concept`)}</div>
  <h1 style="font-size:104px;margin-top:34px;max-width:1500px">${md(o.title ?? story.title)}</h1>
  <p style="font-size:38px;margin-top:40px;max-width:1300px;line-height:1.4">${md(o.subtitle ?? '')}</p>`), 'build/cards/opening.png');

for (const [i, a] of story.acts.entries())
  await png(frame(`
    <div class="eyebrow" style="font-size:30px">Act ${i + 1} of ${story.acts.length}</div>
    <h1 style="font-size:96px;margin-top:34px;max-width:1500px">${md(a.card ?? a.title)}</h1>
    <p style="font-size:38px;margin-top:40px;max-width:1300px;line-height:1.4">${md(a.goal ?? '')}</p>`), `build/cards/act_${a.id}.png`);

const c = story.closing ?? {};
await png(frame(`
  <div class="eyebrow" style="font-size:30px">${md(c.eyebrow ?? 'What this means')}</div>
  <h1 style="font-size:96px;margin-top:34px;max-width:1500px">${md(c.title ?? 'Built on *UnifyApps*.')}</h1>
  <p style="font-size:38px;margin-top:40px;max-width:1300px;line-height:1.4">${md(c.subtitle ?? '')}</p>
  ${c.cta ? `<div style="display:inline-block;margin-top:56px;padding:22px 44px;border-radius:999px;background:var(--olive);color:#fff;font-size:34px;font-weight:600">${md(c.cta)}</div>` : ''}`), 'build/cards/closing.png');

await png(`<div style="display:inline-flex;align-items:center;gap:14px;padding:12px 24px;border-radius:999px;background:rgba(252,250,245,.94);
  border:1px solid var(--line);font-size:24px;color:var(--ink);font-weight:500">Powered and built by
  <span style="color:var(--em);font-weight:600;font-style:italic">UnifyApps</span></div>`, 'build/cards/badge.png', 420, 70, true);
await done();
console.log('cards written to build/cards/');
