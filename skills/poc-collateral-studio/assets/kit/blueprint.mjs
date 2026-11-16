// kit/blueprint.mjs: blueprint.json -> the technical blueprint slides for the deck, in the template theme.
//   build/blueprint/blueprint-1.png      architecture: what it is, the counts, and the high-level diagram
//                                        (users -> front doors -> automations and agents -> data and systems)
//   build/blueprint/blueprint-2..n.png   what was built: every automation and AI agent, one row each; as many
//                                        pages as the list needs (rows never split, a page never overflows)
// Each picture is content only (transparent, 1920 x 854): the deck slide gives the eyebrow, title and footer.
// usage: node kit/blueprint.mjs            (exit 1 when the diagram and the list disagree, or a page overflows)
import fs from 'node:fs';
import { page, done, md } from './render.mjs';
import { readJSON } from './lib.mjs';

const bp = readJSON('blueprint.json');
if (!bp) { console.error('MUST FIX\n  blueprint.json not found or not valid JSON'); process.exit(1); }
const W = 1920, H = 854, OUT = 'build/blueprint';
const esc = (s = '') => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
const STATUS = { live: 'Live', simulated: 'Simulated in POC', golive: 'Connected at go-live' };
const built = bp.built || [];
const autos = built.filter((b) => b.type !== 'agent'), agents = built.filter((b) => b.type === 'agent');
const byName = Object.fromEntries(built.map((b) => [b.name, b]));
const errors = [];
if (!built.length) errors.push('"built" is empty: list every automation and AI agent the build made');

// ---- the diagram and the list must name the same things ----
const inGroups = new Set((bp.groups || []).flatMap((g) => g.items));
for (const n of inGroups) if (!byName[n]) errors.push(`diagram names "${n}", which is not in "built"`);
for (const b of built) if (!inGroups.has(b.name) && !(bp.doors || []).some((d) => d.label === b.name))
  errors.push(`"${b.name}" is in "built" but not on the diagram (add it to a group, or as a door for a user-facing agent)`);
for (const b of built) if (!b.does) errors.push(`"${b.name}": say what it does ("does")`);
const doorIds = new Set((bp.doors || []).map((d) => d.id));
for (const u of bp.users || []) for (const t of u.to || []) if (!doorIds.has(t)) errors.push(`user "${u.label}" goes to unknown door "${t}"`);
// cross-check against the build summary when it is given: every built name should appear there
if (bp.source && !fs.existsSync(bp.source)) errors.push(`"source" ${bp.source} not found (the path is relative to the collateral folder, e.g. ../../04-build/build-summary.md)`);
else if (bp.source) {
  const txt = fs.readFileSync(bp.source, 'utf8').toLowerCase();
  for (const b of built) if (!txt.includes(b.name.toLowerCase())) console.warn(`WARN "${b.name}" does not appear in ${bp.source}: check it was built under this name`);
}

const counts = bp.counts || [
  [(bp.doors || []).filter((d) => d.kind === 'app').length, 'app'], [autos.length, 'automation'], [agents.length, 'AI agent'],
  [(bp.data || []).length, 'data object'], [(bp.systems || []).length, 'connected system'],
].filter(([n]) => n > 0).map(([n, label]) => ({ n, label: n === 1 ? label : label + 's' }));
const key = new Set(bp.key || []);

const STYLE = `
body{width:${W}px;height:${H}px;position:relative;overflow:hidden}
.wrap{position:absolute;inset:0;display:grid;grid-template-columns:400px 1fr;gap:28px;padding:6px 8px}
.side{display:flex;flex-direction:column;gap:16px;min-height:0}
.card{padding:20px 22px}
.h{font-size:22px;font-weight:500;color:var(--ink);margin-bottom:10px}
.lead{font-size:17px;line-height:1.45}
.tiles{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.tile{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--olive);border-radius:8px;padding:10px 14px}
.tile b{display:block;font-size:34px;font-weight:300;color:var(--ink);line-height:1.1}
.tile span{font-size:14px}
.pr li{font-size:15.5px;line-height:1.4;margin:0 0 6px 18px}
.pr b{color:var(--ink)}
.dia{position:relative;padding:18px 26px 16px;display:flex;flex-direction:column;justify-content:space-evenly;gap:26px;min-height:0}
.dia .h{margin:0}
.row{display:flex;flex-direction:column;gap:8px;position:relative}
.lab{position:relative;z-index:1;align-self:flex-start;background:var(--card);padding-right:8px;font-size:12.5px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--em)}
.items{display:flex;gap:16px;justify-content:center;flex-wrap:wrap}
.node{position:relative;z-index:1;background:#fff;border:1px solid var(--line);border-radius:8px;padding:9px 18px;text-align:center;min-width:170px}
.node b{display:block;font-size:17px;font-weight:600;color:var(--ink)}
.node i{display:block;font-style:normal;font-size:13.5px;margin-top:2px}
.door{border:1.5px solid var(--olive);background:var(--card)}
.door.agent{background:var(--olive)} .door.agent b,.door.agent i{color:#fff}
.engine{position:relative;z-index:1;background:#EEEDE6;border:2px solid var(--olive);border-radius:12px;padding:12px 16px;display:flex;gap:22px;flex-wrap:wrap;justify-content:center}
.grp{display:flex;flex-direction:column;gap:7px}
.grp .chips{display:flex;gap:7px;flex-wrap:wrap;max-width:520px}
.chip{background:#fff;border:1px solid var(--line);border-radius:6px;padding:5px 11px;font-size:14.5px;color:var(--ink);white-space:nowrap}
.chip.agent{background:var(--olive);color:#fff;border-color:var(--olive)}
.key{border:2px solid var(--olive);font-weight:600}
.sys{border-style:dashed}
.badge{display:inline-block;margin-top:4px;font-size:11.5px;padding:1px 8px;border-radius:9px;background:var(--disc);color:var(--em)}
.env{position:relative;z-index:1;align-self:center;background:var(--sand2);border:1px solid var(--line);border-radius:8px;padding:6px 18px;font-size:14px;margin-top:-8px}
svg.wires{position:absolute;inset:0;z-index:0;width:100%;height:100%;pointer-events:none;overflow:visible}
table{width:100%;border-collapse:collapse;font-size:15.5px}
th{background:var(--olive);color:#fff;font-weight:600;text-align:left;padding:9px 12px;font-size:13px;letter-spacing:.08em;text-transform:uppercase}
td{padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top;line-height:1.35}
td.n{color:var(--em);width:38px} td.nm{font-weight:600;color:var(--ink);width:260px}
td.ty{width:120px} td.tr{width:230px} td.ob{width:300px;font-size:14px}
.pill{display:inline-block;padding:1px 9px;border-radius:9px;font-size:12.5px;background:var(--disc);color:var(--em)}
.pill.agent{background:var(--olive);color:#fff}
.tbl{position:absolute;inset:0;padding:6px 8px;display:flex;flex-direction:column}
.tbl .card{padding:6px 10px;flex:1;overflow:hidden}
`;

function chip(name) {
  const b = byName[name] || {};
  return `<span class="chip ${b.type === 'agent' ? 'agent' : ''} ${key.has(name) ? 'key' : ''}">${esc(name)}</span>`;
}
function node(d, cls = '') {
  const status = d.status ? `<span class="badge">${STATUS[d.status] || esc(d.status)}</span>` : '';
  return `<div class="node ${cls} ${key.has(d.label) ? 'key' : ''}" ${d.id ? `data-id="${esc(d.id)}"` : ''}><b>${esc(d.label)}</b>${d.sub ? `<i>${esc(d.sub)}</i>` : ''}${status}</div>`;
}

function architecture(compact = false) {
  const side = `<div class="side">
    <div class="card"><div class="h">What it is</div><div class="lead">${md(bp.what || '')}</div></div>
    <div class="tiles">${counts.map((c) => `<div class="tile"><b>${c.n}</b><span>${esc(c.label)}</span></div>`).join('')}</div>
    ${(bp.principles || []).length ? `<div class="card pr"><div class="h">Design principles</div><ul>${bp.principles.map((p) => `<li>${md(p)}</li>`).join('')}</ul></div>` : ''}
  </div>`;
  // compact (a big build): each group shows its first three items and "+N more"; the list pages name them all
  const show = (g) => (compact && g.items.length > 4 ? [...g.items.slice(0, 3).map(chip), `<span class="chip">+${g.items.length - 3} more</span>`] : g.items.map(chip)).join('');
  const groups = (bp.groups || []).map((g) => `<div class="grp"><div class="lab">${esc(g.label)}</div><div class="chips">${show(g)}</div></div>`).join('');
  const bottom = [...(bp.data || []).map((d) => node(d, 'obj')), ...(bp.systems || []).map((d) => node(d, 'sys'))].join('');
  const dia = `<div class="card dia" id="dia">
    ${bp.headline ? `<div class="h">${md(bp.headline)}</div>` : ''}
    <div class="row" id="users"><div class="lab">Users</div><div class="items">${(bp.users || []).map((u) => node({ ...u, id: 'u:' + (u.id || u.label) })).join('')}</div></div>
    <div class="row" id="doors"><div class="lab">Front doors</div><div class="items">${(bp.doors || []).map((d) => node(d, `door ${d.kind === 'agent' ? 'agent' : ''}`)).join('')}</div></div>
    <div class="row"><div class="lab">${autos.length} automation${autos.length === 1 ? '' : 's'}${agents.length ? ` · ${agents.length} AI agent${agents.length === 1 ? '' : 's'}` : ''} · UnifyApps</div><div class="engine" id="engine">${groups}</div></div>
    <div class="row" id="bottom"><div class="lab">Data${(bp.systems || []).length ? ' and connected systems' : ''}</div><div class="items">${bottom}</div></div>
    ${bp.env ? `<div class="env">${esc(bp.env)}</div>` : ''}
    <svg class="wires" id="wires"></svg></div>`;
  return `<div class="wrap">${side}${dia}</div>`;
}

// Elbow connectors drawn after layout, from the real positions of the boxes.
const WIRE = (users) => `(() => {
  const dia = document.getElementById('dia'), R = dia.getBoundingClientRect(), svg = document.getElementById('wires');
  const box = (el) => { const r = el.getBoundingClientRect(); return { x: r.left - R.left + r.width / 2, t: r.top - R.top, b: r.bottom - R.top, l: r.left - R.left, r: r.right - R.left }; };
  const col = getComputedStyle(document.documentElement).getPropertyValue('--olive2').trim() || '#828750';
  let d = '';
  const elbow = (a, b) => { const m = (a.y + b.y) / 2; d += 'M' + a.x + ' ' + a.y + ' V' + m + ' H' + b.x + ' V' + (b.y - 6) + ' '; heads.push(b); };
  const heads = [];
  const users = ${JSON.stringify(users)};
  for (const u of users) { const ue = document.querySelector('[data-id="' + CSS.escape('u:' + u.id) + '"]'); if (!ue) continue;
    for (const t of u.to) { const de = document.querySelector('#doors [data-id="' + CSS.escape(t) + '"]'); if (!de) continue;
      const a = box(ue), b = box(de); elbow({ x: a.x, y: a.b }, { x: b.x, y: b.t }); } }
  const eng = box(document.getElementById('engine'));
  for (const de of document.querySelectorAll('#doors .node')) { const a = box(de); elbow({ x: a.x, y: a.b }, { x: Math.min(Math.max(a.x, eng.l + 20), eng.r - 20), y: eng.t }); }
  for (const be of document.querySelectorAll('#bottom .node')) { const b = box(be); elbow({ x: Math.min(Math.max(b.x, eng.l + 20), eng.r - 20), y: eng.b }, { x: b.x, y: b.t }); }
  svg.innerHTML = '<path d="' + d + '" fill="none" stroke="' + col + '" stroke-width="1.6"/>' +
    heads.map((h) => '<path d="M' + (h.x - 5) + ' ' + (h.y - 7) + ' L' + h.x + ' ' + (h.y - 1) + ' L' + (h.x + 5) + ' ' + (h.y - 7) + ' Z" fill="' + col + '"/>').join('');
  const over = dia.scrollHeight > dia.clientHeight + 2 || [...dia.querySelectorAll('.node,.engine')].some((e) => e.getBoundingClientRect().bottom > R.bottom)
    || [...document.querySelectorAll('.side > *')].some((e) => e.getBoundingClientRect().bottom > ${H});
  return over;
})()`;

function table(rows, start) {
  return `<div class="tbl"><div class="card" id="tc"><table><thead><tr><th></th><th>Name</th><th>Type</th><th>Runs when</th><th>What it does</th><th>Reads / writes · tools</th></tr></thead><tbody>
  ${rows.map((b, i) => `<tr><td class="n">${start + i + 1}</td><td class="nm">${esc(b.name)}</td>
    <td class="ty"><span class="pill ${b.type === 'agent' ? 'agent' : ''}">${b.type === 'agent' ? 'AI agent' : 'Automation'}</span></td>
    <td class="tr">${esc(b.trigger || '')}</td><td>${md(b.does || '')}</td>
    <td class="ob">${esc([...(b.objects || []), ...(b.tools || []).map((t) => 'tool: ' + t)].join(' · '))}</td></tr>`).join('')}
  </tbody></table></div></div>`;
}

fs.mkdirSync(OUT, { recursive: true });
for (const f of fs.readdirSync(OUT)) if (/^blueprint-\d+\.png$/.test(f)) fs.unlinkSync(`${OUT}/${f}`);  // our own previous render
const shots = [];
{
  const users = (bp.users || []).map((u) => ({ id: u.id || u.label, to: u.to || [] }));
  for (const compact of [false, true]) {
    const p = await page(`<style>${STYLE}</style>${architecture(compact)}`, W, H);
    const over = await p.evaluate(WIRE(users));
    if (over && !compact) { await p.close(); console.log('architecture: too many items for full chips; drawing groups compact (the list pages name every item)'); continue; }
    if (over) errors.push('architecture page overflows even compact: shorten "what", drop "principles", use fewer, wider groups, or list fewer data objects and systems');
    const f = `${OUT}/blueprint-1.png`; await p.screenshot({ path: f, omitBackground: true }); await p.close(); shots.push(f); break;
  }
}
// What was built: agents first, then automations, in the order given; as many pages as needed.
const list = [...agents, ...autos];
let i = 0, n = 2;
while (i < list.length) {
  const p = await page(`<style>${STYLE}</style>${table(list.slice(i), i)}`, W, H);
  const fit = await p.evaluate(() => {
    const c = document.getElementById('tc').getBoundingClientRect(); let k = 0;
    for (const tr of document.querySelectorAll('tbody tr')) { if (tr.getBoundingClientRect().bottom > c.bottom - 4) break; k++; }
    return k;
  });
  if (fit === 0) { errors.push(`row "${list[i].name}" is taller than a page: shorten its "does"`); await p.close(); break; }
  await p.evaluate((k) => { [...document.querySelectorAll('tbody tr')].slice(k).forEach((tr) => tr.remove()); }, fit);
  const f = `${OUT}/blueprint-${n++}.png`; await p.screenshot({ path: f, omitBackground: true }); await p.close(); shots.push(f);
  i += fit;
}
await done();
console.log(`${shots.length} blueprint page(s): ${shots.join(', ')}`);
console.log(`built: ${autos.length} automations, ${agents.length} AI agents, ${(bp.data || []).length} data objects`);
if (errors.length) { console.error('MUST FIX\n  ' + errors.join('\n  ')); process.exit(1); }
