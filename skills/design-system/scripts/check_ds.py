#!/usr/bin/env python3
"""Design system · the checks before hand-over (SKILL.md 0.0 rule 6, Step 6b and Step 7).

usage: check_ds.py <client>-design-system.html [wireframe-manifest.json] [--register "$R"] [--hero-picture "<name>"]

  --register      the shared register of apps already made (SKILL.md "Locate this skill": $R, normally
                  ~/.local/poc-studio/design-register.json); the fingerprint is compared with every entry
  --hero-picture  the hero object's name when the manifest has no hero_object but the scoping document's §21.1 says
                  it has a picture; the picture checks then run as if the manifest said so

A manifest from an older POC may lack fields this script reads (hero_object, journey, nav_options, pages, and per
component hero, does, views, cmp, states). Each check such a field turns off prints
"skipped (manifest has no <field>): <check>" instead of passing silently; do that check by hand (SKILL.md 0.0 rule 8).
Without a manifest every manifest check prints one skipped line.

Reads what the style guide marks on its parts:
  id="direction"               the chosen direction, with data-option="A|B|C" on each of the three and data-chosen on one
  id="thesis"                  an <ol> or <ul> of 3 to 5 rules that only fit this client
  id="showcase"                before the first component page: the three screens (data-screen="1|2|3") and
                               2 or 3 close-ups (data-moment)
  id="review"                  the creative director's scores: data-distinctiveness, data-wow, data-richness,
                               data-accuracy, data-ux, data-craft, data-journey (1 to 5) and data-rounds
  <script id="fingerprint">    the fingerprint JSON the register keeps (Step 7)
  data-component="<name>"      on every component page; data-signature on the signature's page
  data-added="true"            plus data-reason on every component the design system added
  data-states="…"              the states a component page draws
  data-part="anatomy|reference|…"  the parts of a component page
  data-media                   on every picture of the hero object (and other visual objects), with
  data-source="<page URL>|attached|drawn"   where it came from; at least 60 % real when the hero object has a picture
  data-variant="<code>"        on every variant specimen (the floor is 25 distinct)
  id="views", data-view="<component>:<view>", data-nav   the views of each hero data set, the navigation options
  id="expressive", data-gradient   the expressive layer and its brand gradients
  id="flows", data-flow="<CMP ids>" data-uses="<components>" data-journey="<steps>", data-principle
                               one flow panel per capability, three principle cards each
  data-form-change="…"         on a component whose form differs from its wireframe frame, with what and why
Prints one `check:` line per problem and exits 1 if there is any; `skipped` and `note:` lines do not change the exit
code.
"""
import json, re, sys
from html.parser import HTMLParser

WORDS_MAX, TABLES_MAX, VARIANTS_MIN = 12000, 24, 25
FP_KEYS = ["client", "app", "idea", "wow", "signature_form", "home_layout", "nav", "surface", "shape", "fonts", "theme",
           "density", "imagery", "accent_hue"]
SCORES = ["distinctiveness", "wow", "richness", "accuracy", "ux", "craft", "journey"]


class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.comps = {}; self.screens = []; self.moments = 0; self.media = 0; self.ids = {}
        self.pos = 0; self.first_comp = None; self.tables = 0; self.skip = 0; self.text = []; self.sig = None
        self.options = 0; self.chosen = 0; self.thesis_open = False; self.thesis_li = 0; self.depth_thesis = 0
        self.media_src = []; self.variants = set(); self.views = set(); self.navs = 0; self.gradients = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs); pos = self.getpos()
        if tag in ("script", "style", "pre", "code", "template"): self.skip += 1
        if tag == "table": self.tables += 1
        if a.get("id"): self.ids[a["id"]] = (pos, a)
        if a.get("id") == "thesis": self.thesis_open = True
        if self.thesis_open and tag == "li": self.thesis_li += 1
        if "data-option" in a: self.options += 1
        if "data-chosen" in a: self.chosen += 1
        c = a.get("data-component")
        if c and a.get("data-page") != "specimen" and tag == "section":
            if self.first_comp is None: self.first_comp = pos
            d = self.comps.setdefault(c, {"added": False, "reason": "", "states": set()})
            if a.get("data-added") == "true": d["added"] = True; d["reason"] = d["reason"] or a.get("data-reason", "")
            if a.get("data-states"): d["states"] |= {s.strip() for s in a["data-states"].split(",") if s.strip()}
            if "data-signature" in a: self.sig = c
        if a.get("data-screen"): self.screens.append((a["data-screen"], pos))
        if "data-moment" in a: self.moments += 1
        if "data-media" in a:
            self.media += 1; src = (a.get("data-source") or "").strip().lower()
            self.media_src.append(src)
        if a.get("data-variant"): self.variants.add(a["data-variant"])
        if a.get("data-view"): self.views.add(a["data-view"])
        if "data-nav" in a: self.navs += 1
        if "data-gradient" in a: self.gradients += 1
    def handle_endtag(self, tag):
        if tag in ("script", "style", "pre", "code", "template") and self.skip: self.skip -= 1
        if tag in ("ol", "ul") and self.thesis_open: self.thesis_open = False
    def handle_data(self, d):
        if not self.skip: self.text.append(d)


def before(a, b): return a[0] < b[0] or (a[0] == b[0] and a[1] < b[1])


def main(argv):
    reg = hero_pic = None
    if "--register" in argv: i = argv.index("--register"); reg = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    if "--hero-picture" in argv: i = argv.index("--hero-picture"); hero_pic = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    html_path = argv[0]; manifest_path = argv[1] if len(argv) > 1 else None
    raw = open(html_path, encoding="utf-8").read()
    p = P(); p.feed(raw)
    errs = []

    # --- the idea: direction, thesis, showcase, review (Phase D and Step 6b) ---
    if "direction" not in p.ids: errs.append("no #direction section (Phase D): the three directions and the chosen one")
    elif p.options < 3 or p.chosen != 1: errs.append(f"#direction shows {p.options} directions and {p.chosen} chosen; three (data-option), one data-chosen")
    if "thesis" not in p.ids: errs.append("no #thesis: 3 to 5 rules that only fit this client (Phase D)")
    elif not 3 <= p.thesis_li <= 5: errs.append(f"#thesis has {p.thesis_li} rules; 3 to 5")
    if "showcase" not in p.ids: errs.append("no #showcase section (0.6): the three screens and the close-ups, before the components")
    elif p.first_comp and not before(p.ids["showcase"][0], p.first_comp): errs.append("#showcase comes after the component pages; it opens the file, right after the direction and thesis")
    if len({s for s, _ in p.screens}) != 3: errs.append(f"{len({s for s, _ in p.screens})} full screens marked data-screen; exactly three (0.6)")
    if not 2 <= p.moments <= 3: errs.append(f"{p.moments} close-ups marked data-moment; two or three (0.6)")
    marks = [m.start() for m in re.finditer(r'data-screen="\d"', raw)]
    for k, pos in enumerate(marks):
        nxt_comp = raw.find("<section", pos + 20)
        while nxt_comp >= 0 and "data-component" not in raw[nxt_comp: raw.find(">", nxt_comp)]: nxt_comp = raw.find("<section", nxt_comp + 8)
        end = marks[k + 1] if k + 1 < len(marks) else (nxt_comp if nxt_comp > 0 else pos + 200000)
        seg = raw[pos: end]
        if re.search(r'class="[^"]*\bagent-launch\b', seg):
            errs.append(f"screen {raw[pos + 13]} has the floating agent launcher; leave it out of the three screens (the top-bar button is there)")
    # one way in to the agent (0.9): the entry the build plan names, and no second button
    root = re.search(r"<html[^>]*>", raw); entry = re.search(r'data-agent-entry="([a-z]+)"', root.group(0)) if root else None
    live = re.sub(r'<[^>]+data-active="false"[^>]*>.*?</(section|div|figure)>', "", raw, flags=re.S)  # reference variants do not count
    has_launch = bool(re.search(r'class="[^"]*\bagent-launch\b', live)); has_btn = "data-agent-button" in live
    if not entry: errs.append("no data-agent-entry on <html>: choose the app's one way in to the agent (topbar, launcher or command) (0.9)")
    elif entry.group(1) == "topbar" and has_launch: errs.append("the agent entry is the top-bar button, but a floating .agent-launch is on the page too; keep one (0.9)")
    elif entry.group(1) == "launcher" and has_btn: errs.append("the agent entry is the floating launcher, but a top-bar agent button (data-agent-button) is on the page too; keep one (0.9)")
    elif entry.group(1) == "command" and (has_launch or has_btn): errs.append("the agent opens from the command field, so neither a top-bar button nor a floating launcher belongs on the page (0.9)")
    if "review" not in p.ids: errs.append("no #review section (Step 6b): the creative director's scores")
    else:
        a = p.ids["review"][1]
        for k in SCORES:
            v = a.get(f"data-{k}")
            if not v or not v.isdigit(): errs.append(f"#review has no data-{k} score")
        low = [f"{k} {a.get('data-' + k)}" for k in SCORES if (a.get(f"data-{k}") or "").isdigit() and int(a.get(f"data-{k}")) < 4]
        rounds = int(a.get("data-rounds") or 0)
        if low and rounds < 2: errs.append(f"review scores under 4 ({', '.join(low)}) after {rounds} round(s); run the director's changes and judge again (Step 6b, at most two rounds)")
        elif low: print(f"note: after two rounds the review still scores {', '.join(low)}; name it as the weakest part in the hand-over")

    # --- the fingerprint, and the register ---
    m = re.search(r'<script[^>]*id="fingerprint"[^>]*>(.*?)</script>', raw, re.S)
    fp = None
    if not m: errs.append("no <script type=\"application/json\" id=\"fingerprint\"> (Step 7)")
    else:
        try: fp = json.loads(m.group(1))
        except Exception as e: errs.append(f"#fingerprint is not valid JSON: {e}")
        if fp:
            miss = [k for k in FP_KEYS if fp.get(k) in (None, "", {})]
            if miss: errs.append(f"#fingerprint is missing {', '.join(miss)}")
            fonts = fp.get("fonts") or {}
            for role in ("display", "body"):
                f = (fonts.get(role) or "") if isinstance(fonts, dict) else ""
                if re.fullmatch(r"\s*(inter|system-ui|-apple-system|arial|helvetica)\s*", f, re.I) and not fonts.get("reason"):
                    errs.append(f"the {role} font is {f}, a default; choose a face with the brand's character (Step 2b) or give fonts.reason from the brand evidence")

    # --- budgets: depth goes to the idea and the signature, everything else is compact (0.6) ---
    words = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’.-]*", " ".join(p.text)))
    if words > WORDS_MAX: errs.append(f"{words:,} words on the page; the budget is {WORDS_MAX:,} (0.6). Cut documentation: one line of rules beside the thing it governs")
    if p.tables > TABLES_MAX: errs.append(f"{p.tables} tables; the budget is {TABLES_MAX} (0.6). Draw it, or say it in a line")

    # --- the richness floor: draw more (0.6) ---
    if len(p.variants) < VARIANTS_MIN: errs.append(f"{len(p.variants)} distinct variants (data-variant); the floor is {VARIANTS_MIN}: give every hero, interactive and signature component 2 or 3 visibly different forms (0.6, Step 2c)")
    if "views" not in p.ids: errs.append("no #views section (0.6): the hero data sets in their views, the navigation options and the page types")
    if "expressive" not in p.ids: errs.append("no #expressive section (0.6): brand gradients, depth and hover, selection, an empty-state illustration, the chart palette")
    elif p.gradients < 2: errs.append(f"{p.gradients} brand gradients marked data-gradient in the expressive layer; at least two (0.6)")

    # --- the components (0.0) ---
    skipped = []
    def skip(field, what): skipped.append(f"skipped (manifest has no {field}): {what}")
    if p.sig is None: errs.append("no component page carries data-signature (0.8)")
    starts = [(mm.start(), mm.group(1)) for mm in re.finditer(r'<section[^>]*data-component="([^"]+)"', raw)]
    body = {}
    for i, (pos, name) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(raw)
        body[name] = body.get(name, "") + raw[pos:end]
    if p.sig and p.sig in body:
        b = body[p.sig]
        if 'data-part="anatomy"' not in b: errs.append(f"the signature '{p.sig}' has no anatomy (data-part=\"anatomy\")")
        k = b.find('data-part="reference"')
        if k < 0 or len(re.findall(r'href="https?://', b[k:])) < 2: errs.append(f"the signature '{p.sig}' needs a reference part with at least two links")
    for n, b in body.items():
        k = b.find('data-part="reference"')
        if k >= 0 and n != p.sig and len(re.findall(r'href="https?://', b[k:])) < 1: errs.append(f"'{n}' has a reference part with no link")
    if len(p.views) < 4: errs.append(f"{len(p.views)} views drawn (data-view); draw each hero data set at least two ways, four or more in all (0.6)")
    # flows at component level (0.6 part 6): each panel uses two or more components, three principles, says each thing once
    fl = [(mm.start(), dict(re.findall(r'(data-[a-z]+)="([^"]*)"', mm.group(0)))) for mm in re.finditer(r'<[a-z]+[^>]*data-flow="[^"]*"[^>]*>', raw)]
    if "flows" not in p.ids: errs.append("no #flows section (0.6 part 6): one flow panel per capability, components working together, three principle cards each")
    for k, (pos, a) in enumerate(fl):
        end = fl[k + 1][0] if k + 1 < len(fl) else raw.find("<section", pos + 10)
        seg = raw[pos: end if end > pos else pos + 200000]
        n_pr = len(re.findall(r"data-principle", seg))
        if len([u for u in a.get("data-uses", "").split(",") if u.strip()]) < 2: errs.append(f"flow '{a.get('data-flow')}' uses fewer than two components; a flow shows components working together")
        plain = [t.strip() for t in re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", seg, flags=re.S).split("<") if t.strip()]
        lines = [re.sub(r"^[^>]*>", "", t).strip() for t in plain]; lines = [l for l in lines if len(l) >= 40]
        dup = sorted({l for l in lines if lines.count(l) > 1})
        if dup: errs.append(f"flow '{a.get('data-flow')}' says the same thing twice ('{dup[0][:50]}…'); show each thing once per panel")
        if n_pr != 3: errs.append(f"flow '{a.get('data-flow')}' has {n_pr} principle cards; three, each a UX decision in a short title and two sentences")

    if not manifest_path:
        skipped.append("skipped (no manifest given): manifest components, states, build-plan pages, views, navigation options, "
                       "flow coverage of capabilities and journey steps, hero components, the hero object's pictures; "
                       "check them by hand against the scoping document (SKILL.md 0.0 rule 8)")
    else:
        mf = json.load(open(manifest_path))
        comps = mf.get("components") or []
        has = lambda key: any(key in c for c in comps)
        if not comps: skip("components", "every manifest component has a component page, with its states")
        names = {c["component"] for c in comps}
        for n in sorted(names - set(p.comps)): errs.append(f"manifest component '{n}' has no component page")
        for n, c in sorted(p.comps.items()):
            if n not in names and c["added"] and not c["reason"]: errs.append(f"added component '{n}' has no data-reason")
        added = [n for n, c in p.comps.items() if c["added"]]
        if not mf.get("pages"): skip("pages", "every frame's page ID is in #build-plan")
        for pg in mf.get("pages") or []:
            pid = re.sub(r"[a-z]$", "", pg["id"])
            if pid not in raw: errs.append(f"page {pid} is not in #build-plan")
        if comps and not has("states"): skip("states", "each component page draws the states the manifest lists")
        for c in comps:
            want = {s for s in c.get("states", []) if s in ("empty", "loading", "error", "disabled", "selected")}
            have = p.comps.get(c["component"], {}).get("states", set())
            if have and want - have: errs.append(f"'{c['component']}' is missing the manifest states {sorted(want - have)}")
        # views and navigation from the wireframes (v4.9)
        if comps and not has("views"): skip("views", "the #views section draws every view the wireframes list (choose two or more per hero data set yourself)")
        want_views = {f"{c['component']}:{v['name'] if isinstance(v, dict) else v}".lower() for c in comps for v in c.get("views", [])}
        have_views = {v.lower() for v in p.views}
        miss_v = sorted(want_views - have_views)
        if miss_v: errs.append(f"views the wireframes list but the #views section does not draw (data-view): {', '.join(miss_v[:6])}")
        if not mf.get("nav_options"): skip("nav_options", "the navigation options drawn (data-nav): draw the chosen one in full and two alternatives")
        nav = mf.get("nav_options") or []
        if nav and p.navs < min(3, len(nav)): errs.append(f"{p.navs} navigation options drawn (data-nav); draw the wireframes' {len(nav)} options, the chosen one in full")
        # hover and focus drawn on every interactive component
        if comps and not has("does"): skip("does", "hover and focus drawn on every interactive component (check each component that acts)")
        for c in comps:
            if c.get("does") and c["component"] in p.comps:
                st = {x.lower() for x in p.comps[c["component"]]["states"]}
                gaps = [x for x in ("hover", "focus") if not any(x in y for y in st)]
                if gaps: errs.append(f"'{c['component']}' is interactive but its states do not draw {' and '.join(gaps)} (data-states)")
        heroes = [c["component"] for c in comps if c.get("hero")]
        anat = sum(1 for n, b in body.items() if 'data-part="anatomy"' in b)
        if comps and not has("hero"):
            skip("hero", "hero components appear in a flow panel (take them from §21.1 and 0.8); full-depth floor taken as six pages, or every component when there are fewer")
            need = min(6, len(comps))
        else:
            need = min(6, 1 + len(heroes))
        if anat < need: errs.append(f"{anat} components drawn at full depth (data-part=\"anatomy\"); the signature and up to five key components, {need} in all (0.6)")
        # flows: one panel per capability, every journey step covered, every hero component used
        if comps and not has("cmp"): skip("cmp", "every capability has a flow panel (check against the scoping document's §23 CMP list)")
        caps = {x for c in comps for x in (c.get("cmp") or [])}
        have_caps = {x.strip() for _, a in fl for x in a.get("data-flow", "").split(",")}
        if caps - have_caps: errs.append(f"capabilities with no flow panel (data-flow): {', '.join(sorted(caps - have_caps))}")
        if not mf.get("journey"): skip("journey", "every journey step has a flow panel (check against the demo storyline §20.2)")
        steps = set(range(1, len(mf.get("journey") or []) + 1))
        have_steps = {int(x) for _, a in fl for x in re.findall(r"\d+", a.get("data-journey", ""))}
        if steps - have_steps: errs.append(f"journey steps no flow panel covers (data-journey): {', '.join(map(str, sorted(steps - have_steps)))}")
        used = {u.strip() for _, a in fl for u in a.get("data-uses", "").split(",")}
        if set(heroes) - used: errs.append(f"hero components that appear in no flow panel (data-uses): {', '.join(sorted(set(heroes) - used))}")
        ho = mf.get("hero_object")
        if not ho and hero_pic: ho = {"name": hero_pic, "picture": True}
        if not ho: skip("hero_object", "the hero object's pictures in every screen and the signature, real images and their sources "
                        "(take it from §21.1; run again with --hero-picture \"<name>\" when it has a picture)")
        ho = ho or {}
        if ho.get("picture"):
            if p.media < 12: errs.append(f"{p.media} pictures marked data-media; the hero object ({ho.get('name')}) has a picture, so show it wherever people meet it: at least 12, and in every screen")
            for s, pos in p.screens:
                seg_start = raw.find(f'data-screen="{s}"'); seg = raw[seg_start: seg_start + 300000]
                nxt = re.search(r'data-screen="\d"', seg[20:])
                seg = seg[: nxt.start() + 20] if nxt else seg
                if "data-media" not in seg: errs.append(f"screen {s} shows no picture of the {ho.get('name')} (data-media)")
            if p.sig and "data-media" not in body.get(p.sig, ""): errs.append(f"the signature '{p.sig}' shows no picture of the {ho.get('name')}")
            # real images, sourced and recorded (Phase D, "Real images, without being asked")
            nosrc = sum(1 for x in p.media_src if not x)
            if nosrc: errs.append(f"{nosrc} pictures marked data-media have no data-source (a page URL, attached, or drawn)")
            real = sum(1 for x in p.media_src if x and x != "drawn")
            if p.media and real / p.media < 0.6: errs.append(f"{real} of {p.media} pictures are real images; the hero object has a picture, so use the client's own images (at least 60 %), and say in the hand-over which sites refused")
            size = sum(len(mm) for mm in re.findall(r"data:image/[a-z+]+;base64,[A-Za-z0-9+/=]+", raw)) * 3 // 4
            if size > 8_000_000: errs.append(f"embedded images total {size / 1e6:.1f} MB; resize to 800 px WebP and keep them under 8 MB")
            if re.search(r'<img[^>]+src="https?://', raw): errs.append("an image is hotlinked (src=\"http…\"); embed it as a data URI so the file works on its own")
        print(f"{len(names)} manifest components · {len(added)} added by the design system · {len(p.comps)} component pages · "
              f"{p.media} pictures · {words:,} words · {p.tables} tables · {len(p.variants)} variants · {len(p.views)} views · {p.gradients} gradients")
        for n in added: print(f"  added: {n} — {p.comps[n]['reason']}")
        changed = re.findall(r'data-component="([^"]+)"[^>]*data-form-change="([^"]+)"', raw)
        for n, why in changed: print(f"  new form: {n} — {why}")
    for line in skipped: print(line)

    if reg and fp:
        sys.path.insert(0, __import__("os").path.dirname(__file__))
        import register
        lines, rerrs = register.compare(fp, [e for e in register.load(reg) if not (e.get("client") == fp.get("client") and e.get("app") == fp.get("app"))])
        errs += rerrs
    for e in errs: print("check:", e)
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(__doc__)
    main(sys.argv[1:])
