// orbit_signin.mjs — one Orbit sign-in per run, reused by the AI PM's build walk and the collateral recording.
// Opens a visible browser on the Orbit login page; the PERSON signs in (Google SSO is fine). The session is saved
// only once Orbit itself has opened, never typed or stored as a password.
//
// usage: node orbit_signin.mjs [--base https://orbit.uat.unifyapps.com] [--out ~/.local/poc-studio/auth/orbit.json] [--check]
//   --check  open the saved session headless and exit 0 if it is still signed in, 1 if not (no browser shown).
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const arg = (k, d) => { const i = process.argv.indexOf(`--${k}`); return i > 0 ? process.argv[i + 1] : d; };
const BASE = arg('base', 'https://orbit.uat.unifyapps.com');
const OUT = (arg('out', '~/.local/poc-studio/auth/orbit.json')).replace(/^~/, os.homedir());
const roots = [path.join(os.homedir(), '.local/poc-collateral/node'), process.cwd(), HERE];
let pw; for (const r of roots) { try { pw = createRequire(path.join(r, 'noop.js'))('playwright'); break; } catch {} }
if (!pw) { console.error('Playwright not found: run the poc-collateral-setup skill first.'); process.exit(2); }

const onLogin = (u) => /\/(login|signin|auth|sso|oauth|callback)\b/i.test(new URL(u).pathname) || !new URL(u).hostname.endsWith(new URL(BASE).hostname);

if (process.argv.includes('--check')) {
  if (!fs.existsSync(OUT)) { console.log('no saved Orbit session'); process.exit(1); }
  const b = await pw.chromium.launch({ headless: true });
  const p = await (await b.newContext({ storageState: OUT })).newPage();
  await p.goto(BASE, { waitUntil: 'domcontentloaded', timeout: 60000 }).catch(() => {});
  await p.waitForTimeout(2500);
  const ok = !onLogin(p.url()); await b.close();
  console.log(ok ? 'Orbit session valid' : 'Orbit session expired'); process.exit(ok ? 0 : 1);
}

const browser = await pw.chromium.launch({ headless: false });
const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
const page = await ctx.newPage();
await page.goto(new URL('/login', BASE).href);
console.log('>> Sign in to Orbit in the open window. Waiting…');
await page.waitForURL((u) => !onLogin(u.href), { timeout: 0 });
await page.waitForFunction(() => document.body && document.body.innerText.trim().length > 50, null, { timeout: 90000 }).catch(() => {});
fs.mkdirSync(path.dirname(OUT), { recursive: true });
await ctx.storageState({ path: OUT });
fs.chmodSync(OUT, 0o600);
console.log(`saved ${OUT}`);
await browser.close();
