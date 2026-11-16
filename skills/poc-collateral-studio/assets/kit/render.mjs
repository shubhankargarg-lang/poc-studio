// kit/render.mjs: HTML in the template theme -> PNG or PDF. Used by cards, docs and swimlanes.
import fs from 'node:fs';
import path from 'node:path';
import { launch, readJSON } from './lib.mjs';

const T = readJSON('brand/tokens.json');
const F = path.resolve('fonts');
const face = (file, w, st = 'normal') => `@font-face{font-family:Spectral;src:url("file://${F}/${file}");font-weight:${w};font-style:${st}}`;
export const CSS = `
${face('Spectral-Light.ttf', 300)}${face('Spectral-Regular.ttf', 400)}${face('Spectral-Italic.ttf', 400, 'italic')}
${face('Spectral-Medium.ttf', 500)}${face('Spectral-MediumItalic.ttf', 500, 'italic')}${face('Spectral-SemiBold.ttf', 600)}
:root{--ink:${T.ink};--em:${T.emphasis};--body:${T.body};--olive:${T.olive};--olive2:${T.olive_2};--card:${T.card};
--line:${T.card_line};--disc:${T.disc};--sand:${T.sand};--sand2:${T.sand_2};--afill:${T.alert_fill};--aline:${T.alert_line};--atext:${T.alert_text}}
*{box-sizing:border-box;margin:0;padding:0}
html,body{font-family:Spectral,serif;color:var(--body);-webkit-print-color-adjust:exact;print-color-adjust:exact}
.canvas{background:radial-gradient(circle at 0% 0%, ${T.canvas_from} 0%, ${T.canvas_from} 41%, ${T.canvas_to} 100%)}
.eyebrow{font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:var(--em)}
h1,.h1{font-weight:300;color:var(--ink);line-height:1.08}
h1 em,.h1 em{font-weight:500;font-style:italic;color:var(--em)}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px}
.disc{border-radius:50%;background:var(--disc);display:grid;place-items:center;color:var(--em)}
.alert{background:var(--afill);border:1px solid var(--aline);color:var(--atext);border-radius:12px}
.footer{position:absolute;left:0;right:0;bottom:0;display:grid;grid-template-columns:1fr auto 1fr;align-items:center;color:var(--em)}
.footer span:last-child{text-align:right}
.footer img{height:1.2em;vertical-align:middle}
`;
export const logo = () => (fs.existsSync('brand/logo.png') ? `file://${path.resolve('brand/logo.png')}` : '');
export const footer = (page = '', scale = 1) => `<div class="footer" style="padding:0 ${40 * scale}px ${22 * scale}px;font-size:${11 * scale}px">
  <span><img src="${logo()}" style="height:${18 * scale}px"> &nbsp;·&nbsp; ${T.tagline}</span><span>${T.footer}</span><span>${page}</span></div>`;
// "Lead: *emphasis*." -> Lead: <em>emphasis</em>;  **bold** -> <b>bold</b>. Bold first, so ** never leaks as *.
export const md = (s = '') => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
  .replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>').replace(/\*([^*]+)\*/g, '<em>$1</em>');

let browser;
export async function page(html, w, h) {
  browser ??= await launch();
  const p = await browser.newPage({ viewport: { width: w, height: h } });
  fs.mkdirSync('build/html', { recursive: true });
  const f = path.resolve(`build/html/${Date.now()}_${Math.random().toString(36).slice(2)}.html`);
  fs.writeFileSync(f, `<!doctype html><meta charset="utf-8"><style>${CSS}</style>${html}`);
  await p.goto(`file://${f}`); await p.evaluate(() => document.fonts.ready);
  const missing = await p.evaluate(() => !document.fonts.check('16px Spectral'));
  if (missing) console.warn('WARN Spectral not loaded: run the font install step');
  return p;
}
export async function png(html, out, w = 1920, h = 1080, transparent = false) {
  const p = await page(html, w, h); await p.screenshot({ path: out, omitBackground: transparent }); await p.close();
}
export async function pdf(html, out, opts = {}) {
  const p = await page(html, 1600, 1000);
  await p.pdf({ path: out, printBackground: true, preferCSSPageSize: true, ...opts }); await p.close();
}
export async function done() { await browser?.close(); browser = null; }
