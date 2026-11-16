/* wf-runtime v1 — screens, frames, states and interactions for a wireframe. Put in by wf_tool.py embed; do not edit per app. */
(() => {
  const d = document, root = d.documentElement;
  const meta = JSON.parse(d.getElementById('wf-meta').textContent);
  const $$ = (s, r = d) => [...r.querySelectorAll(s)];
  const OVERLAY = ['drawer', 'modal', 'toast', 'menu', 'popover'];
  // an instance resolves ONLY inside the control's own screen; '~name' means '<this screen>.name'. No document-wide fallback.
  const current = () => d.querySelector('.wf-screen:not([hidden])');
  const full = (id, scope) => id.startsWith('~') ? `${scope ? scope.dataset.screenId : ''}.${id.slice(1)}` : id;
  const inst = (id, scope) => scope ? scope.querySelector(`[data-instance-id="${CSS.escape(full(id, scope))}"]`) : null;
  function missing(id, scope, step) {   // fail safely: report, change nothing, stop the interaction
    const msg = `wf: missing target "${full(id, scope)}" on screen ${scope ? scope.dataset.screenId : '(none)'}${step ? ` in "${step}"` : ''}`;
    console.error(msg); (window.wfErrors = window.wfErrors || []).push(msg); root.dataset.wfError = msg;
  }
  const own = (el, c) => c.parentElement && c.parentElement.closest('[data-instance-id]') === el;
  function paint(el) {
    const st = el.dataset.state || 'default';
    if (OVERLAY.includes(el.dataset.componentType)) el.hidden = st === 'closed';
    $$('[data-when]', el).forEach(c => { if (own(el, c)) c.hidden = !c.dataset.when.split(/\s+/).includes(st); });
    $$('[role="tab"][data-tab]', el).forEach(t => { if (own(el, t)) t.setAttribute('aria-selected', String(t.dataset.tab === st)); });
  }
  function setState(id, st, scope) {
    const el = inst(id, scope);
    if (!el) { missing(id, scope); return false; }
    el.dataset.state = st; paint(el);
    if (OVERLAY.includes(el.dataset.componentType) && st === 'open' && el.dataset.componentType !== 'toast') {
      const f = el.querySelector('button,a[href],input,select,textarea,[tabindex]'); if (f) f.focus();
    }
  }
  $$('[data-instance-id]').forEach(el => { el.dataset.initial = el.dataset.state || 'default'; el.dataset.state = el.dataset.initial; });
  function show(id) {
    const fr = (meta.frames || []).find(f => f.id === id);
    const sid = fr ? fr.of : id;
    const screens = $$('.wf-screen');
    const sc = screens.find(s => s.dataset.screenId === sid) || screens[0];
    screens.forEach(s => { s.hidden = s !== sc; });
    $$('[data-instance-id]', sc).forEach(el => { el.dataset.state = el.dataset.initial; paint(el); });
    const dev = sc.querySelector('.wf-device'); if (dev) { if (!dev.dataset.w) dev.dataset.w = getComputedStyle(dev).getPropertyValue('--w'); dev.style.setProperty('--w', fr && fr.width ? fr.width + 'px' : dev.dataset.w); if (fr && fr.dir) dev.setAttribute('dir', fr.dir); else dev.removeAttribute('dir'); }
    if (fr) Object.entries(fr.set || {}).forEach(([k, v]) => setState(k, v, sc));
    const who = (fr && fr.persona) || sc.dataset.persona;
    $$('[data-for]', sc).forEach(e => { e.hidden = !e.dataset.for.split(/\s+/).includes(who); });
    root.dataset.persona = who;
    root.dataset.current = fr ? fr.id : sc.dataset.screenId;
    chrome(); scrollTo(0, 0); root.dataset.ready = '1';
  }
  async function run(spec, src) {
    const sc = src.closest('.wf-screen') || current(), S = (id, st) => setState(id, st, sc), I = id => inst(id, sc);
    for (const step of spec.split(';').map(s => s.trim()).filter(Boolean)) {
      const i = step.indexOf(':'), verb = i < 0 ? step : step.slice(0, i), arg = i < 0 ? '' : step.slice(i + 1).trim();
      const [k, v] = arg.split('=').map(s => s && s.trim());
      const target = verb === 'state' ? k : arg;
      if (['open', 'close', 'toggle', 'state', 'toast'].includes(verb) && target && !I(target)) { missing(target, sc, step); return; }
      if (verb === 'go') location.hash = arg;
      else if (verb === 'back') history.back();
      else if (verb === 'open') S(arg, 'open');
      else if (verb === 'close') S(arg || src.closest('[data-instance-id]').dataset.instanceId, 'closed');
      else if (verb === 'toggle') S(arg, I(arg) && I(arg).dataset.state === 'open' ? 'closed' : 'open');
      else if (verb === 'state') S(k, v);
      else if (verb === 'wait') await new Promise(r => setTimeout(r, +arg || 600));
      else if (verb === 'toast') { S(arg, 'open'); setTimeout(() => S(arg, 'closed'), 4000); }
      else if (verb === 'submit') { const f = src.closest('form'); if (f && !f.checkValidity()) { f.reportValidity(); return; } }
      else console.warn('wf: unknown step', step);
    }
  }
  d.addEventListener('click', e => {
    const t = e.target.closest('[data-interaction]');
    if (!t || t.disabled || t.getAttribute('aria-disabled') === 'true') return;
    e.preventDefault(); run(t.dataset.interaction, t);
  });
  d.addEventListener('submit', e => e.preventDefault());
  d.addEventListener('keydown', e => {
    if (e.key !== 'Escape') return;
    const open = $$('.wf-screen:not([hidden]) [data-instance-id][data-state="open"]').filter(el => OVERLAY.includes(el.dataset.componentType)).pop();
    if (open) setState(open.dataset.instanceId, 'closed', current());
  });
  function chrome() {
    const bar = d.querySelector('.wf-review'); if (!bar || root.classList.contains('wf-export')) return;
    const cur = root.dataset.current, sc = d.querySelector('.wf-screen:not([hidden])');
    const opts = $$('.wf-screen').map(s => [s.dataset.screenId, `${s.dataset.screenId} · ${s.dataset.screenTitle}`])
      .concat((meta.frames || []).map(f => [f.id, `${f.id} · ${f.title}`]));
    const states = $$('[data-instance-id][data-states]', sc).filter(el => el.dataset.states.trim().includes(' '));
    bar.innerHTML = `<strong>${meta.app.name} · wireframes</strong>
      <label>Screen <select id="wf-go">${opts.map(([v, t]) => `<option value="${v}"${v === cur ? ' selected' : ''}>${t}</option>`).join('')}</select></label>
      ${states.length ? `<label>State <select id="wf-st"><option value="">Component state…</option>${states.flatMap(el => el.dataset.states.split(/\s+/).map(s => `<option value="${el.dataset.instanceId}=${s}">${el.dataset.instanceId} → ${s}</option>`)).join('')}</select></label>` : ''}
      <button type="button" id="wf-an">${root.classList.contains('wf-annot') ? 'Hide' : 'Show'} annotations</button>
      <button type="button" id="wf-nt">Notes</button>`;
    bar.querySelector('#wf-go').onchange = e => { location.hash = e.target.value; };
    const st = bar.querySelector('#wf-st'); if (st) st.onchange = e => { const [k, v] = e.target.value.split('='); if (k) setState(k, v, current()); };
    bar.querySelector('#wf-an').onclick = () => { root.classList.toggle('wf-annot'); chrome(); };
    bar.querySelector('#wf-nt').onclick = () => { const n = d.querySelector('.wf-notes'); if (n) n.hidden = !n.hidden; };
  }
  const notes = d.querySelector('.wf-notes');
  if (notes) {
    const list = (t, xs, f) => xs && xs.length ? `<h3>${t}</h3><ul>${xs.map(f).join('')}</ul>` : '';
    notes.innerHTML = list('Open questions', meta.open_questions, q => `<li>${q.question} <small>(${q.brd_ref || ''}; assumed: ${q.assumption || 'nothing'})</small></li>`)
      + list('Changes to the BRD layout', meta.brd_overrides, o => `<li>${o.brd}: ${o.change} <small>(${o.why})</small></li>`)
      + list('Sample data used', $$('[data-sample]').map(e => e.textContent.trim()).filter((x, i, a) => x && a.indexOf(x) === i), x => `<li>${x}</li>`);
  }
  if (/export/.test(location.search)) root.classList.add('wf-export');
  addEventListener('hashchange', () => show(location.hash.slice(1)));
  show(location.hash.slice(1) || (meta.start || ''));
})();
