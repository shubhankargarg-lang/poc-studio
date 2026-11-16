// kit/lint.mjs: refuse a story that breaks the rules before anything is captured or recorded.
// usage: node kit/lint.mjs   (exit 1 on errors)
import { pathToFileURL } from 'node:url';
import { readJSON } from './lib.mjs';

const NAV_WORDS = /^(on|in|under|open|opening|next|finally|back|stepping|switch|go|moving|the \w+ tab)/i;

export function lint() {
  const story = readJSON('story.json'), cov = readJSON('coverage.json', []), brief = readJSON('brief.json');
  const errs = [], warns = [];
  const allowed = new Set(['click', 'hover', 'type', 'press', 'select', 'scroll', 'highlight', 'waitFor', 'settle', 'wait', 'goto', 'custom']);
  const ids = new Set(cov.map((c) => c.id)), covered = new Set();
  for (const [name, p] of Object.entries(brief.personas))
    if (/uat|staging|preview|localhost|127\.0\.0\.1|sandbox|dev\./i.test(p.url) && !p.public_url && brief.share !== 'internal')
      warns.push(`persona ${name}: ${p.url} looks internal; set "public_url" for the walkthrough, or "share": "internal"`);
  for (const act of story.acts) {
    if (!brief.personas[act.persona]) errs.push(`${act.id}: unknown persona ${act.persona}`);
    for (const [i, s] of act.scenes.entries()) {
      if (!s.narration?.trim()) errs.push(`${s.id}: no narration`);
      if (!s.covers?.length) warns.push(`${s.id}: covers no feature`);
      for (const f of s.covers ?? []) { if (!ids.has(f)) errs.push(`${s.id}: covers unknown feature ${f}`); covered.add(f); }
      const acts = s.actions ?? [];
      for (const a of acts) {
        if (!allowed.has(a.do)) errs.push(`${s.id}: action "${a.do}" not allowed (no fill, zoom, scale or screenshots-as-video)`);
        if (a.do === 'goto' && !a.reason) errs.push(`${s.id}: mid-act goto needs a "reason"; navigate by clicking instead`);
        if (a.at && !s.narration.includes(a.at)) errs.push(`${s.id}: cue "${a.at}" not found in narration`);
        if (a.pre && a.at) errs.push(`${s.id}: a "pre" action runs before the voice, so it cannot have an "at" cue`);
        if (JSON.stringify(a).match(/zoom|scale\(|setViewportSize/i)) errs.push(`${s.id}: zoom/scale is forbidden`);
        const t = a.target ?? a.to;
        if (t && typeof t === 'object' && t.css && !t.text && !t.name && !t.label && !a.say)
          warns.push(`${s.id}: ${a.do} on a CSS selector has no "say"; the script would print an empty name`);
      }
      // The screen must change BEFORE the voice talks about it (Pentland: narration ran 2-4 s ahead of the screen).
      const firstMain = acts.find((a) => !a.pre);
      const opensScreen = (a) => a && a.do === 'click' && (a.nav || /tab|menu|sidebar|link/i.test(JSON.stringify(a.target)));
      if (opensScreen(firstMain) && !s.under_voice && (!firstMain.at || s.narration.indexOf(firstMain.at) < 40))
        errs.push(`${s.id}: the first click opens a screen while the voice is already talking about it; mark it "pre": true (or set "under_voice": true if that is intended)`);
      if (i === 0 && NAV_WORDS.test(s.narration) && !acts.some((a) => a.pre) && act.start)
        warns.push(`${s.id}: first scene of act ${act.id} talks about a screen; make sure act "start" opens that screen (it opens ${act.start})`);
      const steps = acts.filter((a) => ['click', 'type', 'select'].includes(a.do)).length;
      if (s.walkthrough?.do && s.walkthrough.do.length !== steps) warns.push(`${s.id}: walkthrough has ${s.walkthrough.do.length} "do" lines for ${steps} click/type/select actions; they are paired with numbered step shots`);
      const words = s.narration.split(/\s+/).length, secs = words / 2.6;
      if (secs > 45) warns.push(`${s.id}: ~${secs.toFixed(0)} s of narration; split the scene`);
    }
  }
  for (const c of cov) if ((c.must_show_in ?? []).includes('video') && !covered.has(c.id)) errs.push(`coverage ${c.id} (${c.feature}) is in no scene`);
  return { errs, warns };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) { // works when the path has spaces
  const { errs, warns } = lint();
  warns.forEach((w) => console.log('WARN ', w));
  errs.forEach((e) => console.log('ERROR', e));
  console.log(errs.length ? `lint failed: ${errs.length} error(s)` : 'lint clean');
  process.exit(errs.length ? 1 : 0);
}
