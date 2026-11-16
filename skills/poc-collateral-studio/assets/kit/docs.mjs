// kit/docs.mjs: the demo script PDF and the walkthrough PDF, in the template theme (A4 landscape).
// usage: node kit/docs.mjs script | walkthrough | both
import fs from 'node:fs';
import path from 'node:path';
import { pdf, done, footer, md } from './render.mjs';
import { readJSON } from './lib.mjs';

const which = process.argv[2] ?? 'both';
const brief = readJSON('brief.json'), story = readJSON('story.json'), cov = readJSON('coverage.json', []);
const narr = readJSON('build/narration.json', {});
fs.mkdirSync('out', { recursive: true });
const img = (p) => (fs.existsSync(p) ? `file://${path.resolve(p)}` : null);
const esc = (s = '') => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
const secs = (s) => narr[s.id]?.dur ?? s.narration.split(/\s+/).length / 2.6;
const mmss = (x) => `${Math.floor(x / 60)}:${String(Math.round(x % 60)).padStart(2, '0')}`;
const date = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

const PAGE = `@page{size:297mm 210mm;margin:0}
.pg{width:297mm;height:210mm;position:relative;overflow:hidden;padding:16mm 18mm 20mm;page-break-after:always}
.pg:last-child{page-break-after:auto}
h1{font-size:34pt}h2{font-size:20pt;font-weight:400;color:var(--ink)}h2 em{font-style:italic;color:var(--em);font-weight:500}
.eyebrow{font-size:9pt;margin-bottom:3mm}
table{width:100%;border-collapse:separate;border-spacing:0;font-size:8.6pt;line-height:1.35}
th{font-weight:600;color:var(--em);text-transform:uppercase;font-size:7.5pt;letter-spacing:.05em;text-align:left;padding:2mm;border-bottom:1px solid var(--line)}
td{padding:2.2mm 2mm;vertical-align:top;border-bottom:1px solid var(--sand2);color:var(--body)}
td.n{color:var(--em);font-weight:600;white-space:nowrap}
.tag{display:inline-block;padding:.3mm 1.6mm;border-radius:9px;background:var(--disc);color:var(--em);font-size:7pt;margin:0 1mm 1mm 0}
.k{font-size:8pt;color:var(--em);font-weight:600;text-transform:uppercase;letter-spacing:.05em;margin:3mm 0 1mm}
.shot{width:100%;border-radius:8px;border:1px solid var(--line);display:block}`;

// Plain-English line for an action, used in the script's "On screen" column.
function says(a) {
  if (a.say) return a.say; // story can word any action for the script
  const t = a.target ?? a.to ?? {};
  const name = typeof t === 'string' ? '' : t.name ?? t.text ?? t.label ?? t.placeholder ?? '';
  const q = (n, fallback) => (n ? `“${n}”` : fallback);
  return { click: `Click ${q(name, 'the control')}`, hover: `Hover over ${q(name, 'the item')}`, type: `Type “${a.text}”`,
    press: `Press ${a.key}`, select: `Choose “${a.option}”`, scroll: a.to ? `Scroll to ${q(name, 'the section')}` : 'Scroll down',
    highlight: `Point out ${q(name, 'the section')}`, waitFor: '', settle: '', wait: '', goto: `Open ${a.url}`,
    custom: a.label ?? '' }[a.do] ?? '';
}

const cover = (title, sub) => `<div class="pg canvas" style="padding:34mm 26mm">
  <div class="eyebrow" style="font-size:11pt">${esc(brief.customer)} · ${esc(brief.poc)}</div>
  <h1 style="font-size:42pt;margin-top:6mm;max-width:220mm">${md(title)}</h1>
  <p style="font-size:14pt;margin-top:8mm;max-width:200mm;line-height:1.45">${md(sub)}</p>
  <p style="font-size:10pt;margin-top:14mm;color:var(--em)">Audience: ${esc(brief.persona_role ?? brief.persona)} (${esc(brief.persona)}) · Narration: US English, ${esc(brief.voice?.gender ?? 'female')} voice · ${date}</p>
  ${footer('', 1)}</div>`;

function covMatrix(firstPage) {
  const where = (id) => story.acts.flatMap((a) => a.scenes).filter((s) => (s.covers ?? []).includes(id)).map((s) => s.id);
  const PER = 9, pages = [];
  for (let i = 0; i < Math.max(cov.length, 1); i += PER) pages.push(cov.slice(i, i + PER));
  return pages.map((rows, k) => `<div class="pg canvas"><div class="eyebrow">Coverage${k ? ' (continued)' : ''}</div><h2>Every must-show feature, <em>and where it appears</em>.</h2>
  <table style="margin-top:6mm"><tr><th>ID</th><th>Screen</th><th>Feature</th><th>How to get there</th><th>Scenes</th><th>Shown in</th></tr>
  ${rows.map((c) => `<tr><td class="n">${c.id}</td><td>${esc(c.screen)}</td><td>${esc(c.feature)}</td><td>${esc((c.nav_path ?? []).join(' › '))}</td>
    <td>${where(c.id).join(', ') || '<b style="color:var(--atext)">none</b>'}</td><td>${(c.must_show_in ?? []).map((x) => `<span class="tag">${x}</span>`).join('')}</td></tr>`).join('')}
  </table>${footer(String(firstPage + k), 1)}</div>`).join('');
}

async function script() {
  let t = story.opening?.seconds ?? 4, pages = [], pg = 2;
  const rowH = (s) => Math.max(Math.ceil(s.narration.length / 95), (s.actions ?? []).map(says).filter(Boolean).length, 2) * 4.6 + 5; // mm
  for (const [i, a] of story.acts.entries()) {
    t += a.card_seconds ?? 3;
    const rows = a.scenes.map((s) => { const r = { h: rowH(s), html: `<tr><td class="n">${mmss(t)}</td><td><b style="color:var(--ink)">${esc(s.title)}</b><br><span style="color:var(--em)">${esc(s.lane ?? '')}</span></td>
      <td>${(s.actions ?? []).map(says).filter(Boolean).map(esc).join('<br>')}</td><td style="font-size:9.2pt">${esc(s.narration)}</td>
      <td>${(s.covers ?? []).map((c) => `<span class="tag">${c}</span>`).join('')}</td></tr>` }; t += secs(s) + 1.2; return r; });
    const chunks = [[]]; let used = 0;
    for (const r of rows) { if (used + r.h > 120 && chunks.at(-1).length) { chunks.push([]); used = 0; } chunks.at(-1).push(r); used += r.h; }
    chunks.forEach((c, k) => pages.push(`<div class="pg canvas"><div class="eyebrow">Act ${i + 1} of ${story.acts.length} · ${esc(brief.personas[a.persona]?.label ?? a.persona)}${k ? ' · continued' : ''}</div>
      <h2>${md(a.card ?? a.title)}</h2><p style="font-size:10pt;margin:2mm 0 5mm">${md(a.goal ?? '')}</p>
      <table><tr><th style="width:12mm">Time</th><th style="width:38mm">Scene</th><th style="width:58mm">On screen</th><th>Narration</th><th style="width:22mm">Covers</th></tr>${c.map((r) => r.html).join('')}</table>
      ${footer(String(pg++), 1)}</div>`));
  }
  const total = t + (story.closing?.seconds ?? 5);
  await pdf(`<style>${PAGE}</style>${cover(story.title, `Demo script for approval · ${story.acts.length} acts · about ${mmss(total)} minutes`)}${pages.join('')}${covMatrix(pg)}`,
    `out/${brief.slug}_Demo_Script.pdf`);
  console.log(`out/${brief.slug}_Demo_Script.pdf`);
}

async function walkthrough() {
  const lane = img('out/swimlane_with.png');
  const glance = `<div class="pg canvas"><div class="eyebrow">At a glance</div><h2>${md(story.title)}</h2>
    <div style="display:grid;grid-template-columns:${lane ? '1fr 1.25fr' : '1fr'};gap:8mm;margin-top:6mm">
    <div>${story.acts.map((a, i) => `<div class="card" style="padding:4mm 5mm;margin-bottom:3mm"><div class="k" style="margin:0">Act ${i + 1}</div>
      <div style="font-size:12pt;color:var(--ink);margin-top:1mm">${md(a.card ?? a.title)}</div><div style="font-size:9pt;margin-top:1mm">${md(a.goal ?? '')}</div></div>`).join('')}</div>
    ${lane ? `<div><img class="shot" src="${lane}"><div style="font-size:8pt;color:var(--em);margin-top:2mm">How the work flows with UnifyApps (full swimlanes in the companion PDF).</div></div>` : ''}
    </div>${footer('2', 1)}</div>`;
  let pg = 3; const pages = [];
  for (const [i, a] of story.acts.entries()) for (const s of a.scenes) {
    const w = s.walkthrough ?? {}, steps = (w.do ?? []);
    const stepHtml = steps.map((d, k) => { const sh = img(`build/shots/${s.id}_s${k + 1}.png`);
      return `<div style="display:grid;grid-template-columns:${sh ? '34mm 1fr' : '1fr'};gap:3mm;align-items:start;margin-bottom:2.5mm">
        ${sh ? `<img class="shot" src="${sh}">` : ''}<div style="font-size:9.2pt"><b style="color:var(--olive)">${k + 1}.</b> ${md(d)}</div></div>`; }).join('');
    const main = img(`build/shots/${s.id}.png`);
    pages.push(`<div class="pg canvas"><div class="eyebrow">Act ${i + 1} · ${esc(a.title)} · ${esc(s.lane ?? '')}</div><h2>${md(s.title)}</h2>
      <div style="display:grid;grid-template-columns:168mm 1fr;gap:7mm;margin-top:5mm">
        <div>${main ? `<img class="shot" src="${main}">` : '<div class="alert" style="padding:6mm">Screenshot missing: run capture</div>'}
          <div class="card" style="padding:3mm 4mm;margin-top:3mm;font-size:9pt"><span class="k">Why it matters</span><br>${md(w.why ?? '')}</div></div>
        <div><div class="k" style="margin-top:0">Do</div>${stepHtml}
          <div class="k">You'll see</div><div style="font-size:9.2pt">${md(w.expect ?? '')}</div>
          ${w.recover ? `<div class="k">If it doesn't</div><div style="font-size:9pt">${md(w.recover)}</div>` : ''}
          <div style="margin-top:3mm">${(s.covers ?? []).map((c) => `<span class="tag">${c} ${esc(cov.find((x) => x.id === c)?.feature ?? '')}</span>`).join('')}</div></div>
      </div>${footer(String(pg++), 1)}</div>`);
  }
  const internal = brief.share === 'internal';
  const live = [...new Set(cov.map((c) => c.screen.split(' · ')[0]))];
  const appx = `<div class="pg canvas"><div class="eyebrow">Appendix</div><h2>Running the demo <em>yourself</em>.</h2>
    <table style="margin-top:6mm"><tr><th>Role</th><th>Where</th><th>Sign in</th></tr>
    ${Object.values(brief.personas).map((p) => `<tr><td>${esc(p.label)}</td><td>${esc(internal ? p.url : p.public_url ?? 'Link provided with this guide')}</td>
      <td>${esc(internal ? p.username ?? 'no sign-in' : p.signin_note ?? 'Your account, provided separately')}</td></tr>`).join('')}</table>
    <div class="k" style="margin-top:6mm">Before you start</div><div style="font-size:9.5pt;line-height:1.5">${md(brief.reset ?? 'Use the demo data prepared for this POC.')}</div>
    <div class="k">Shown live in this guide</div><div style="font-size:9.5pt;line-height:1.5">${live.map(esc).join(' · ')}</div>
    <div class="k">Simulated in the POC, and connected at go-live</div><div style="font-size:9.5pt;line-height:1.5">${md(brief.limits ?? '')}</div>${footer(String(pg), 1)}</div>`;
  await pdf(`<style>${PAGE}</style>${cover(story.title, story.opening?.subtitle ?? 'Step-by-step walkthrough')}${glance}${pages.join('')}${appx}`,
    `out/${brief.slug}_Walkthrough.pdf`);
  console.log(`out/${brief.slug}_Walkthrough.pdf`);
}

if (which !== 'walkthrough') await script();
if (which !== 'script') await walkthrough();
await done();
