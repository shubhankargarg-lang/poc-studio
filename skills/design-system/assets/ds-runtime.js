/* ds-runtime v1 — theme switch, component states, forced-state mirrors. Put in by ds_tool.py embed. */
(() => {
  const d = document, root = d.documentElement, $$ = (s, r = d) => [...r.querySelectorAll(s)];
  const OVERLAY = ['drawer', 'modal', 'toast', 'menu', 'popover'];
  const own = (el, c) => c.parentElement && c.parentElement.closest('[data-instance-id],[data-specimen-of],[data-wireframe-of]') === el;
  function paint(el) {
    const st = el.dataset.state || 'default';
    if (OVERLAY.includes(el.dataset.componentType) && !el.closest('[data-catalogue],.ds-compare')) el.hidden = st === 'closed';
    $$('[data-when]', el).forEach(c => { if (own(el, c)) c.hidden = !c.dataset.when.split(/\s+/).includes(st); });
    $$('[role="tab"][data-tab]', el).forEach(t => { if (own(el, t)) t.setAttribute('aria-selected', String(t.dataset.tab === st)); });
  }
  // styled screens 2 and 3 copy the same wireframe screen, so instance IDs repeat: always resolve inside the control's own screen
  const inst = (id, scope) => {
    if (id.startsWith('~') && scope && scope.dataset.dsScreen) id = scope.dataset.dsScreen + '.' + id.slice(1);
    return scope ? scope.querySelector(`[data-instance-id="${CSS.escape(id)}"]`) : null;
  };
  const set = (id, st, scope) => { const el = inst(id, scope); if (el) { el.dataset.state = st; paint(el); } };
  $$('[data-instance-id],[data-specimen-of],[data-wireframe-of]').forEach(paint);
  // persona-only parts (data-for) show only for the persona of their screen, stage or copy (data-persona on an ancestor)
  $$('[data-for]').forEach(e => { const p = e.closest('[data-persona]'); if (p) e.hidden = !e.dataset.for.split(/\s+/).includes(p.dataset.persona); });
  d.addEventListener('click', e => {
    const t = e.target.closest('[data-interaction]'), sc = t && t.closest('[data-ds-screen]');
    if (!t || t.disabled || !sc) return;
    e.preventDefault();
    for (const step of t.dataset.interaction.split(';').map(s => s.trim()).filter(Boolean)) {
      const [verb, arg = ''] = [step.split(':')[0], step.split(':').slice(1).join(':').trim()];
      const [k, v] = arg.split('=').map(s => s && s.trim());
      if (verb === 'state') set(k, v, sc); else if (verb === 'open') set(arg, 'open', sc);
      else if (verb === 'close') set(arg || t.closest('[data-instance-id]').dataset.instanceId, 'closed', sc);
      else if (verb === 'toggle') set(arg, inst(arg, sc) && inst(arg, sc).dataset.state === 'open' ? 'closed' : 'open', sc);
      else if (verb === 'toast') { set(arg, 'open', sc); setTimeout(() => set(arg, 'closed', sc), 4000); }
    }
  });
  // forced states for the catalogue: .is-hover / .is-focus / .is-pressed mirror the kit's own :hover / :focus-visible / :active rules
  const map = [[/:hover/g, '.is-hover'], [/:focus-visible/g, '.is-focus'], [/:focus-within/g, '.is-focus'], [/:active/g, '.is-pressed']];
  for (const sh of d.styleSheets) {
    let rules; try { rules = [...sh.cssRules]; } catch (e) { continue; }
    const walk = (list, target) => list.forEach(r => {
      if (r.cssRules && r.media) return walk([...r.cssRules], r);
      if (!r.selectorText || !/:(hover|focus-visible|focus-within|active)/.test(r.selectorText)) return;
      let s = r.selectorText; map.forEach(([re, cls]) => { s = s.replace(re, cls); });
      try { (target || sh).insertRule(`${s}{${r.style.cssText}}`, (target || sh).cssRules.length); } catch (e) {}
    });
    walk(rules, null);
  }
  // theme switch (document chrome only; the app itself ships one theme with the other's tokens live)
  const saved = (() => { try { return localStorage.getItem('ds-theme'); } catch (e) { return null; } })();
  if (saved) root.dataset.theme = saved;
  $$('[data-theme-set]').forEach(b => b.addEventListener('click', () => {
    const v = b.dataset.themeSet; if (v === 'os') root.removeAttribute('data-theme'); else root.dataset.theme = v;
    try { v === 'os' ? localStorage.removeItem('ds-theme') : localStorage.setItem('ds-theme', v); } catch (e) {}
    $$('[data-theme-set]').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
  }));
  // a styled screen keeps its wireframe width (--w) and is scaled down to fit where it is shown, so it keeps its real
  // layout and nothing is cut (the three screens, the light and dark comparison)
  const fit = () => $$('[data-ds-device]').forEach(dv => {
    dv.style.zoom = '';
    const w = parseFloat(getComputedStyle(dv).getPropertyValue('--w')) || dv.offsetWidth;
    const fr = dv.closest('.ds-frame'), host = (fr || dv).parentElement, cs = getComputedStyle(host);
    const avail = host.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
    if (avail > 0 && w > avail) dv.style.zoom = (avail / w).toFixed(4);
  });
  fit(); addEventListener('resize', fit);
  root.dataset.ready = '1';
})();
