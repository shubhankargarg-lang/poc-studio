// kit/swimlanes.mjs: swimlanes.json -> out/swimlane_<view>.png (16:9, for the deck and walkthrough)
// and out/<Slug>_Swimlanes.pdf (one page per view), in the template theme.
// usage: node kit/swimlanes.mjs
import { png, pdf, done, footer, md } from './render.mjs';
import { readJSON } from './lib.mjs';

const brief = readJSON('brief.json'), sl = readJSON('swimlanes.json'), story = readJSON('story.json');
const scenes = new Set(story.acts.flatMap((a) => a.scenes.map((s) => s.id)));
const W = 1920, H = 1080, TOP = 210, BOT = 990, LH = 240, PADX = 50;
const esc = (s = '') => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
const STATUS = { live: 'Live', simulated: 'Simulated in POC', golive: 'Connected at go-live' };

function view(v, deck = false) {
  for (const s of v.steps) if (s.scene && !scenes.has(s.scene)) console.warn(`WARN ${v.id}/${s.id}: scene ${s.scene} not in story.json`);
  if (v.id !== 'today') for (const s of v.steps) if (!s.scene && s.kind !== 'system') console.warn(`WARN ${v.id}/${s.id}: no scene; every step must be shown in the demo or come from discovery`);
  const laneKind = Object.fromEntries(sl.lanes.map((l) => [l.id, l.kind]));
  for (const s of v.steps) s.kind ??= laneKind[s.lane] === 'unifyapps' ? 'auto' : laneKind[s.lane] === 'system' ? 'system' : 'manual';
  const lanes = sl.lanes.filter((l) => v.steps.some((s) => s.lane === l.id));
  const laneH = (BOT - TOP) / lanes.length, row = Object.fromEntries(lanes.map((l, i) => [l.id, i]));
  for (const [i, s] of v.steps.entries()) if (s.parallel && s.after) console.warn(`WARN ${v.id}/${s.id}: "parallel" with "after"; a step that needs another's output goes in a later column`);
  let c = -1; const col = {};
  for (const s of v.steps) col[s.id] = s.col ?? (s.parallel ? c : ++c);
  const ncol = Math.max(...Object.values(col)) + 1, colW = (W - PADX * 2 - LH) / ncol;
  const cw = Math.min(260, colW - 44), ch = Math.min(118, laneH - 54);
  const pos = {};
  for (const s of v.steps) pos[s.id] = { x: PADX + LH + col[s.id] * colW + (colW - cw) / 2, y: TOP + row[s.lane] * laneH + (laneH - ch) / 2 - (s.pain ? 14 : 0) };
  // Default flow: each main step -> the next main step. A "parallel" step shares the column of the main step
  // before it, takes the same input and feeds the same output. "next": [...] overrides any of this.
  const main = v.steps.filter((s) => !s.parallel), auto = {};
  main.forEach((s, i) => { auto[s.id] = main[i + 1] ? [main[i + 1].id] : []; });
  v.steps.forEach((s, i) => { if (!s.parallel) return;
    const q = [...v.steps.slice(0, i)].reverse().find((x) => !x.parallel); if (!q) return;
    const pred = main[main.indexOf(q) - 1]; if (pred) auto[pred.id].push(s.id);
    auto[s.id] = [...auto[q.id]]; });
  const edges = [], lanesUsed = {};
  v.steps.forEach((s) => {
    const nx = s.next ?? auto[s.id] ?? [];
    for (const t of nx) {
      const key = col[s.id]; lanesUsed[key] = (lanesUsed[key] ?? -1) + 1; const lane = lanesUsed[key];
      const a = pos[s.id], b = pos[t]; if (!b) continue;
      const handoff = s.lane !== v.steps.find((x) => x.id === t).lane;
      const auto = [s.kind, v.steps.find((x) => x.id === t).kind].some((k) => k === 'ai' || k === 'auto');
      const x1 = a.x + cw, y1 = a.y + ch / 2, x2 = b.x, y2 = b.y + ch / 2;
      const mx = Math.min(x2 - 16, x1 + 18 + lane * 12); // vertical run close to the source, offset per edge
      const d = Math.abs(y1 - y2) < 2 ? `M${x1},${y1} L${x2 - 10},${y2}` : `M${x1},${y1} L${mx},${y1} L${mx},${y2} L${x2 - 10},${y2}`;
      edges.push(`<path d="${d}" fill="none" stroke="${auto ? 'var(--olive)' : 'var(--sand)'}" stroke-width="${auto ? 3 : 2.5}"
        ${handoff && !auto ? 'stroke-dasharray="9 7"' : ''} marker-end="url(#${auto ? 'ah2' : 'ah'})"/>`);
    }
  });
  const card = (s) => {
    const p = pos[s.id], k = s.kind ?? 'manual';
    const st = k === 'ai' ? 'background:var(--olive);color:#fff;border-color:var(--olive)'
      : k === 'auto' ? 'background:#E9ECDD;color:var(--ink);border:1.5px solid var(--olive)'
      : k === 'system' ? 'background:var(--sand2);color:var(--ink);border-color:var(--sand)'
      : k === 'decision' ? 'border:2px dashed var(--em)' : '';
    return `<div class="card" style="position:absolute;left:${p.x}px;top:${p.y}px;width:${cw}px;height:${ch}px;padding:14px 16px;${st};
      display:flex;flex-direction:column;justify-content:center;font-size:${cw < 200 ? 17 : 19}px;line-height:1.25">
      ${k === 'ai' || k === 'auto' ? `<div style="font-size:13px;letter-spacing:.08em;font-weight:600;opacity:.8;margin-bottom:4px">${k === 'ai' ? 'AI' : 'AUTOMATED'} · UNIFYAPPS</div>` : ''}
      <div style="font-weight:${k === 'ai' ? 500 : 500};color:${k === 'ai' ? '#fff' : 'var(--ink)'}">${md(s.text)}</div>
      ${s.note ? `<div style="font-size:14px;margin-top:4px;opacity:.85">${md(s.note)}</div>` : ''}</div>
      ${s.pain ? `<div class="alert" style="position:absolute;left:${p.x}px;top:${p.y + ch + 8}px;width:${cw}px;padding:5px 10px;font-size:14px;line-height:1.2">● ${md(s.pain)}</div>` : ''}`;
  };
  const laneHtml = lanes.map((l, i) => `<div style="position:absolute;left:${PADX}px;top:${TOP + i * laneH}px;width:${W - PADX * 2}px;height:${laneH}px;
      border-top:1px solid var(--line);${i === lanes.length - 1 ? 'border-bottom:1px solid var(--line);' : ''}${l.kind === 'unifyapps' ? 'background:rgba(78,88,45,.05)' : ''}"></div>
    <div style="position:absolute;left:${PADX}px;top:${TOP + i * laneH + 8}px;width:${LH - 24}px;height:${laneH - 16}px;border-radius:12px;
      background:${l.kind === 'unifyapps' ? 'var(--olive)' : 'var(--disc)'};color:${l.kind === 'unifyapps' ? '#fff' : 'var(--ink)'};padding:0 18px;display:flex;flex-direction:column;justify-content:center">
      <div style="font-size:21px;font-weight:600">${esc(l.label)}</div>
      ${l.status ? `<div style="font-size:14px;margin-top:4px;color:${l.status === 'live' ? 'var(--olive)' : 'var(--em)'}">${STATUS[l.status] ?? esc(l.status)}</div>` : ''}</div>`).join('');
  return `<div class="${deck ? '' : 'canvas'}" style="width:${W}px;height:${H}px;position:relative">
    ${deck ? '' : `<div style="position:absolute;left:${PADX + 20}px;top:56px"><div class="eyebrow" style="font-size:20px">${esc(v.eyebrow ?? (v.id === 'today' ? 'How it works today' : 'How it works with UnifyApps'))}</div>
    <h1 style="font-size:54px;margin-top:10px">${md(v.title)}</h1></div>`}
    ${laneHtml}
    <svg width="${W}" height="${H}" style="position:absolute;left:0;top:0"><defs>
      <marker id="ah" markerWidth="10" markerHeight="10" refX="0" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="var(--sand)"/></marker>
      <marker id="ah2" markerWidth="10" markerHeight="10" refX="0" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="var(--olive)"/></marker></defs>${edges.join('')}</svg>
    ${v.steps.map(card).join('')}
    ${deck ? '' : footer('', 1.6)}</div>`;
}

const pages = [];
for (const v of sl.views) {
  const h = view(v); pages.push(h); await png(h, `out/swimlane_${v.id}.png`); console.log(`out/swimlane_${v.id}.png`);
  await png(view(v, true), `build/swimlane_${v.id}_deck.png`, W, H, true); // transparent, no footer: the slide supplies both
}
await pdf(`<style>@page{size:1920px 1080px;margin:0}.pg{page-break-after:always}.pg:last-child{page-break-after:auto}</style>${pages.map((p) => `<div class="pg">${p}</div>`).join('')}`,
  `out/${brief.slug}_Swimlanes.pdf`);
console.log(`out/${brief.slug}_Swimlanes.pdf`);
await done();
