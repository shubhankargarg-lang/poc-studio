// kit/auth.mjs: one visible browser per persona; the USER signs in (Google SSO is fine). Saves auth/<persona>.json
// only once the app itself has opened, so an SSO hop (accounts.google.com, /auth/callback) never saves too early.
// usage: node kit/auth.mjs [persona ...]
import fs from 'node:fs';
import { launch, readJSON, W, H } from './lib.mjs';

const brief = readJSON('brief.json');
const want = process.argv.slice(2);
fs.mkdirSync('auth', { recursive: true });
for (const [name, p] of Object.entries(brief.personas)) {
  if (want.length && !want.includes(name)) continue;
  if (!p.login) continue; // public app, nothing to sign in to
  const app = new URL(p.url); const login = new URL(p.login, p.url);
  if (!login.searchParams.has('returnTo')) login.searchParams.set('returnTo', app.pathname);
  const browser = await launch({ headless: false });
  const ctx = await browser.newContext({ viewport: { width: W, height: H } });
  const page = await ctx.newPage();
  await page.goto(login.href);
  console.log(`>> Sign in${p.username ? ` as ${p.username}` : ''} for persona "${name}" in the open window. Waiting...`);
  // back on the app's own host, and past every sign-in / SSO callback path
  await page.waitForURL((u) => u.hostname === app.hostname && !u.pathname.startsWith(login.pathname)
    && !/^\/(auth|sso|oauth|callback)/.test(u.pathname), { timeout: 0 });
  await page.goto(app.href, { waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForFunction(() => document.body && document.body.innerText.trim().length > 50, null, { timeout: 90000 })
    .catch(() => {});
  if (new URL(page.url()).pathname.startsWith(login.pathname)) {
    console.error(`persona "${name}": still on the sign-in page, not saved; run again`); await browser.close(); process.exitCode = 1; continue;
  }
  await ctx.storageState({ path: `auth/${name}.json` });
  console.log(`saved auth/${name}.json (app opened)`);
  await browser.close();
}
