#!/usr/bin/env python3
"""Design system · the render scan and the screenshots the creative director judges (Step 6 and Step 6b).

usage: scan.py <client>-design-system.html <out_dir>

Opens the file in Chromium at 1,440 × 900 in light and dark and:
  - measures the page height (budget: 70,000 px),
  - finds text that overlaps other text, text clipped by its box, text under 4.5:1 on its own background
    (3:1 for 18 px and up), click targets under 24 × 24 px, and a run of four or more identical rows,
  - flags text cut short inside flow panels,
  - saves the screenshots for the director in <out_dir>: 01-first-view, 02-direction, 02-thesis, 03-showcase-<n>,
    04-moment-<n>, 05-signature, 06-component-<name> (four at random), 07-views, 08-expressive, 09-flow-<n>, each in
    -light and -dark, and scan.json with the height, the findings and the screenshot paths.
Prints one `check:` line per finding (at most 12 of each kind) and exits 1 if there is any.

Needs Python Playwright (`pip install playwright --break-system-packages` where `python3 -I -c "import playwright"`
fails). It reuses a Chromium that is already installed: Playwright's own (under PLAYWRIGHT_BROWSERS_PATH or
~/.cache/ms-playwright), or one named in SCAN_CHROMIUM, or chromium / google-chrome on the PATH. Run
`playwright install chromium` only when none exists.
"""
import glob, json, os, random, shutil, sys

JS_FINDINGS = r"""
() => {
  const out = {overlap: [], clip: [], contrast: [], target: [], repeat: []};
  const scope = [...document.querySelectorAll('[data-screen],[data-moment],[data-component]')];
  const inScope = el => scope.some(s => s.contains(el));
  const vis = el => { const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
    return r.width > 1 && r.height > 1 && cs.visibility !== 'hidden' && cs.display !== 'none' && +cs.opacity > 0.05; };
  const leaves = [...document.querySelectorAll('body *')].filter(el => inScope(el) && vis(el) &&
    [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 1));
  const name = el => (el.closest('[data-component]')?.dataset.component || el.closest('[data-screen]') && ('screen ' + el.closest('[data-screen]').dataset.screen) || el.closest('[data-moment]') && 'moment') + ' · "' + el.textContent.trim().slice(0, 40) + '"';
  // text over text
  // the text's own box, cut to what its clipping ancestors actually show (an ellipsis hides the rest)
  const clipTo = (el, r) => { let x0 = r.left, y0 = r.top, x1 = r.right, y1 = r.bottom, n = el;
    while (n && n !== document.body) { const cs = getComputedStyle(n);
      if (cs.overflowX !== 'visible' || cs.overflowY !== 'visible' || cs.textOverflow === 'ellipsis') {
        const c = n.getBoundingClientRect(); x0 = Math.max(x0, c.left); y0 = Math.max(y0, c.top); x1 = Math.min(x1, c.right); y1 = Math.min(y1, c.bottom); }
      n = n.parentElement; }
    return {left: x0, top: y0, right: x1, bottom: y1, width: x1 - x0, height: y1 - y0}; };
  const boxes = leaves.map(el => { const range = document.createRange(); range.selectNodeContents(el);
    const r = clipTo(el, range.getBoundingClientRect()); return {el, r}; }).filter(b => b.r.width > 2 && b.r.height > 2);
  boxes.sort((a, b) => a.r.top - b.r.top);
  for (let i = 0; i < boxes.length && out.overlap.length < 40; i++) {
    const a = boxes[i];
    for (let j = i + 1; j < boxes.length && boxes[j].r.top < a.r.bottom; j++) {
      const b = boxes[j]; if (a.el.contains(b.el) || b.el.contains(a.el)) continue;
      const w = Math.min(a.r.right, b.r.right) - Math.max(a.r.left, b.r.left);
      const h = Math.min(a.r.bottom, b.r.bottom) - Math.max(a.r.top, b.r.top);
      if (w > 4 && h > 4) out.overlap.push(name(a.el) + ' overlaps ' + name(b.el));
    }
  }
  for (const el of leaves) {
    const cs = getComputedStyle(el);
    if ((el.scrollWidth > el.clientWidth + 2 && cs.overflowX !== 'visible' && cs.textOverflow !== 'ellipsis') ||
        (el.scrollHeight > el.clientHeight + 3 && cs.overflowY === 'hidden' && !cs.webkitLineClamp && cs.webkitLineClamp !== 'none'))
      out.clip.push(name(el));
    // contrast against the first opaque background behind it
    const fg = cs.color.match(/[\d.]+/g).map(Number); let bg = null, n = el;
    while (n && n !== document.documentElement) { const b = getComputedStyle(n);
      if (b.backgroundImage && b.backgroundImage !== 'none') { bg = null; break; }
      const c = b.backgroundColor.match(/[\d.]+/g); if (c && (c[3] === undefined || +c[3] > 0.9)) { bg = c.map(Number); break; } n = n.parentElement; }
    if (bg) {
      const L = c => { c = c.slice(0, 3).map(v => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; }); return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]; };
      const a = fg[3] === undefined ? 1 : fg[3]; const mix = fg.slice(0, 3).map((v, k) => v * a + bg[k] * (1 - a));
      const l1 = L(mix), l2 = L(bg); const ratio = (Math.max(l1, l2) + .05) / (Math.min(l1, l2) + .05);
      const big = parseFloat(cs.fontSize) >= 18 || (parseFloat(cs.fontSize) >= 14 && +cs.fontWeight >= 700);
      if (ratio < (big ? 3 : 4.5) && !el.closest('[aria-disabled="true"],[disabled],.is-disabled')) out.contrast.push(name(el) + ' ' + ratio.toFixed(2) + ':1');
    }
  }
  // v12.6 · text cut short inside flow panels: a squeezed panel reads as sloppy
  out.squeezed = [];
  for (const el of document.querySelectorAll('[data-flow] *')) {
    if (!vis(el) || !el.childNodes.length || ![...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 3)) continue;
    const cs = getComputedStyle(el);
    if (el.scrollWidth > el.clientWidth + 2 && (cs.textOverflow === 'ellipsis' || cs.overflowX === 'hidden')) out.squeezed.push(name(el));
  }
  for (const el of document.querySelectorAll('[data-screen] button,[data-screen] a,[data-screen] [role=button],[data-screen] input,[data-moment] button')) {
    if (!vis(el)) continue; const r = el.getBoundingClientRect();
    if (r.width < 24 || r.height < 24) out.target.push((el.getAttribute('aria-label') || el.textContent.trim() || el.tagName).slice(0, 30) + ' ' + Math.round(r.width) + '×' + Math.round(r.height));
  }
  for (const parent of document.querySelectorAll('[data-component] *')) {
    const kids = [...parent.children].filter(vis); let run = 1;
    for (let k = 1; k < kids.length; k++) {
      run = kids[k].innerText && kids[k].innerText === kids[k - 1].innerText && kids[k].innerText.length > 12 ? run + 1 : 1;
      if (run === 4) out.repeat.push(name(kids[k]));
    }
  }
  return out;
}
"""


def shoot(page, sel, path, full=False, el=None):
    """Screenshot one element; an empty or hidden one is skipped (and reported by the caller), never a crash."""
    el = el or page.query_selector(sel)
    if not el: return False
    try:
        el.scroll_into_view_if_needed(timeout=3000); page.wait_for_timeout(150)
        box = el.bounding_box()
        if not box or box["width"] < 2 or box["height"] < 2: return False
        if box["height"] > 2600: page.screenshot(path=path, clip={"x": box["x"], "y": box["y"], "width": box["width"], "height": 2600})
        else: el.screenshot(path=path, timeout=10000)
        return True
    except Exception as e:
        print(f"note: no screenshot of {sel} ({str(e).splitlines()[0]})", file=sys.stderr)
        return False


def launch(pw):
    """Playwright's own Chromium first; otherwise any Chromium already on the machine, so no second browser is fetched."""
    try:
        return pw.chromium.launch()
    except Exception as first:
        roots = [os.environ.get("PLAYWRIGHT_BROWSERS_PATH") or "", os.path.expanduser("~/.cache/ms-playwright"),
                 os.path.expanduser("~/Library/Caches/ms-playwright"), "/ms-playwright"]
        cands = [os.environ.get("SCAN_CHROMIUM") or ""]
        for r in roots:
            if r and os.path.isdir(r):
                cands += sorted(glob.glob(os.path.join(r, "chromium*", "chrome-linux*", "chrome")) +
                                glob.glob(os.path.join(r, "chromium_headless_shell*", "chrome-linux*", "headless_shell")) +
                                glob.glob(os.path.join(r, "chromium*", "chrome-mac*", "Chromium.app", "Contents", "MacOS", "Chromium")) +
                                glob.glob(os.path.join(r, "chromium_headless_shell*", "chrome-mac*", "headless_shell")), reverse=True)
        cands += [shutil.which(n) or "" for n in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable")]
        for exe in [c for c in cands if c and os.path.exists(c)]:
            try:
                return pw.chromium.launch(executable_path=exe)
            except Exception:
                continue
        sys.exit(f"check: no Chromium could be started ({str(first).splitlines()[0]}); set SCAN_CHROMIUM to an installed "
                 "Chromium, or run `playwright install chromium` if none exists")


def main(html, out):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("check: Python Playwright is missing; pip install playwright --break-system-packages, then run again "
                 "(an installed Chromium is reused)")
    os.makedirs(out, exist_ok=True); findings = {}; shots = []
    with sync_playwright() as pw:
        b = launch(pw); page = b.new_page(viewport={"width": 1440, "height": 900})
        page.goto("file://" + os.path.abspath(html)); page.wait_for_timeout(1200)
        height = page.evaluate("document.documentElement.scrollHeight")
        comps = page.evaluate("[...document.querySelectorAll('section[data-component]')].map(s => s.dataset.component)")
        sig = page.evaluate("(document.querySelector('section[data-signature]')||{dataset:{}}).dataset.component || null")
        random.seed(len(comps)); pick = random.sample([c for c in comps if c != sig], min(4, max(0, len(comps) - 1)))
        for theme in ("light", "dark"):
            page.evaluate(f"document.documentElement.setAttribute('data-theme','{theme}')"); page.wait_for_timeout(300)
            page.evaluate("window.scrollTo(0,0)"); page.wait_for_timeout(150)
            p = os.path.join(out, f"01-first-view-{theme}.png"); page.screenshot(path=p); shots.append(p)
            for sel, nm in (("#direction", "02-direction"), ("#thesis", "02-thesis"), ("#views", "07-views"), ("#expressive", "08-expressive")):
                p = os.path.join(out, f"{nm}-{theme}.png")
                if shoot(page, sel, p): shots.append(p)
            for k in range(1, 4):
                p = os.path.join(out, f"03-showcase-{k}-{theme}.png")
                if shoot(page, f'[data-screen="{k}"]', p): shots.append(p)
            for k, h in enumerate(page.query_selector_all("[data-moment]")[:3], 1):
                p = os.path.join(out, f"04-moment-{k}-{theme}.png")
                if shoot(page, f"data-moment {k}", p, el=h): shots.append(p)
            if sig:
                p = os.path.join(out, f"05-signature-{theme}.png")
                if shoot(page, f'section[data-component="{sig}"]', p): shots.append(p)
            for k, fl in enumerate(page.query_selector_all("[data-flow]")[:4], 1):
                p = os.path.join(out, f"09-flow-{k}-{theme}.png")
                if shoot(page, f"data-flow {k}", p, el=fl): shots.append(p)
            for c in pick:
                p = os.path.join(out, f"06-component-{c}-{theme}.png")
                if shoot(page, f'section[data-component="{c}"]', p): shots.append(p)
            f = page.evaluate(JS_FINDINGS)
            for k, v in f.items():
                findings.setdefault(k, []); findings[k] += [f"{theme}: {x}" for x in v if x not in findings[k]]
        b.close()
    errs = []
    if height > 70000: errs.append(f"the page is {height:,} px tall at 1,440 wide; the budget is 70,000 (SKILL.md 0.6): cut documentation, keep the drawings")
    sq = findings.pop("squeezed", [])
    if len(sq) > 6: errs.append(f"{len(sq)} texts cut short inside flow panels (e.g. {sq[0]}); give the panel's components their real width")
    label = {"overlap": "text overlaps text", "clip": "text clipped by its box", "contrast": "text under its contrast floor",
             "target": "click target under 24 × 24", "repeat": "the same row four times or more (draw each state once)"}
    for k, v in findings.items():
        for x in v[:12]: errs.append(f"{label[k]}: {x}")
        if len(v) > 12: errs.append(f"{label[k]}: … and {len(v) - 12} more")
    json.dump({"height": height, "findings": findings, "screenshots": shots}, open(os.path.join(out, "scan.json"), "w"), indent=1)
    print(f"page height {height:,} px · {len(comps)} component pages · {len(shots)} screenshots in {out}")
    for e in errs: print("check:", e)
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    if len(sys.argv) < 3: sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
