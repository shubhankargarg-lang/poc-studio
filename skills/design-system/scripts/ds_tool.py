#!/usr/bin/env python3
"""ds_tool v1 — checks a design-system HTML against the wireframe HTML it styles.
usage: ds_tool.py inventory <wireframes.html> <out.json>          the component index, target widths and the starting #ds-manifest,
                                                                    #build-plan and #style-sets (no browser)
       ds_tool.py fidelity <wireframes.html> <design-system.html>   structure, content, metadata, traceability, anatomy corrections and
                                                                    data-bound visuals (no browser)
       ds_tool.py embed    <design-system.html>                   fills <script id="ds-runtime"> from assets/ds-runtime.js
       ds_tool.py audit    <design-system.html> [out_dir]           light + dark at the BRD's target width (plus 1,024 px for robustness
                                                                    when desktop only, 375 px when a page is phone): contrast, overflow,
                                                                    blank and clipped specimens, surface hierarchy, names, focus, targets,
                                                                    fonts; component anatomy (overlay header, body and footer), components
                                                                    that blend into their surface, field and button edges, empty overlay
                                                                    space; rendered consistency (type, colour, radius, gaps, borders,
                                                                    gradients, icons, one component treated two ways); screenshots of
                                                                    every catalogue entry, contact sheets and consistency.json
Prints error:/check: lines; exits 1 on any error.
"""
import json, os, re, sys
from html.parser import HTMLParser

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

class Node:
    def __init__(s, tag, attrs, parent): s.tag, s.a, s.parent, s.kids = tag, dict(attrs), parent, []
    def walk(s, skip=lambda n: False):
        yield s
        for k in s.kids:
            if isinstance(k, Node) and not skip(k): yield from k.walk(skip)
    def text(s, skip=lambda n: False):
        if s.tag in ("script", "style", "template") or skip(s): return ""
        return " ".join(" ".join((k if isinstance(k, str) else k.text(skip)) for k in s.kids).split())
    def up(s, pred):
        p = s.parent
        while p is not None and not pred(p): p = p.parent
        return p

class Tree(HTMLParser):
    def __init__(s): super().__init__(convert_charrefs=True); s.root = Node("#doc", {}, None); s.cur = s.root
    def handle_starttag(s, tag, attrs):
        n = Node(tag, [(k, v or "") for k, v in attrs], s.cur); s.cur.kids.append(n)
        if tag not in VOID: s.cur = n
    def handle_startendtag(s, tag, attrs): s.cur.kids.append(Node(tag, [(k, v or "") for k, v in attrs], s.cur))
    def handle_endtag(s, tag):
        n = s.cur
        while n is not None and n.tag != tag: n = n.parent
        if n is not None and n.parent is not None: s.cur = n.parent
    def handle_data(s, data): s.cur.kids.append(data)

def parse(path):
    t = Tree(); t.feed(open(path, encoding="utf-8").read()); return t.root, list(t.root.walk())
def jblock(nodes, i):
    n = next((x for x in nodes if x.a.get("id") == i), None)
    return None if n is None else json.loads("".join(k for k in n.kids if isinstance(k, str)))
DECOR = lambda n: "data-ds-decor" in n.a
LOGO = lambda n: "data-logo" in n.a
VIZ = lambda n: "data-ds-viz" in n.a        # a supporting visual drawn from a number the component already shows
WRAP = lambda n: "data-ds-wrap" in n.a      # a region wrapper (header, body, footer, group, label, sr): structure only, no content
SKIP = lambda n: DECOR(n) or LOGO(n) or VIZ(n)
WRAPS = {"header", "body", "footer", "group", "label", "sr"}
KEYS = ("data-component-id", "data-component-type", "data-for", "data-sample", "data-icon", "data-logo", "data-variant", "data-states", "data-state", "data-brd-ref", "data-interaction",
        "data-when", "data-atom", "href", "disabled", "aria-describedby", "role", "data-tab")
def shape(n):
    """What must not change: the element tree (tags and the metadata attributes) and the text, ignoring decor, logo content,
    data-bound visuals and region wrappers (a wrapper's children count as its parent's)."""
    # an id reference may be renamed so a copy stays unique on the page (aria-describedby="why-open" → "why-open-c2")
    return [(x.tag, tuple((k, True if k == "aria-describedby" else x.a.get(k)) for k in KEYS if k in x.a and k != "data-state")) for x in n.walk(SKIP) if x is n or not WRAP(x)]

def numbers(t):
    """The values a data-bound visual may show, read from its source text: '35%' → 35; '6 of 7' → 85.7."""
    t = t.replace(",", "")
    m = re.search(r"(-?\d+(?:\.\d+)?)\s*%", t)
    if m: return float(m.group(1))
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:of|/)\s*(\d+(?:\.\d+)?)", t)
    if m and float(m.group(2)): return 100 * float(m.group(1)) / float(m.group(2))
    return None

def corrections(root, where, E, C):
    """Region wrappers and data-bound visuals: the only structure the design system may add. Returns True if any is used."""
    used = False
    owner_text = root.text(SKIP)
    for x in root.walk():
        if WRAP(x):
            used = True
            if x.a["data-ds-wrap"] not in WRAPS: E(f"{where}: data-ds-wrap=\"{x.a['data-ds-wrap']}\" is not one of {', '.join(sorted(WRAPS))}")
            if x.tag not in ("div", "header", "footer", "section", "span"): E(f"{where}: a <{x.tag}> wrapper; wrappers are div, header, footer, section or span")
            if any(k in x.a for k in KEYS): E(f"{where}: a wrapper carries wireframe metadata ({', '.join(k for k in KEYS if k in x.a)}); it must be structure only")
            if x.a["data-ds-wrap"] != "sr" and any(isinstance(k, str) and k.strip() for k in x.kids): E(f"{where}: a wrapper adds text of its own ('{' '.join(k for k in x.kids if isinstance(k, str)).strip()[:40]}')")
        if VIZ(x):
            used = True
            src = x.a.get("data-ds-from", "").strip()
            if x.text(): E(f"{where}: a data-bound visual carries text '{x.text()[:40]}'; its numbers stay in the component's own text")
            if x.a.get("aria-hidden") != "true": E(f"{where}: a data-bound visual needs aria-hidden=\"true\" (the text already says it)")
            if not src: E(f"{where}: a data-bound visual has no data-ds-from (the text it draws)")
            elif " ".join(src.split()) not in owner_text: E(f"{where}: a visual draws '{src[:40]}', which the component does not show; draw only numbers it already shows")
            else:
                want = numbers(src)
                for y in x.walk():
                    m = re.search(r"--v:\s*(-?[\d.]+)%", y.a.get("style", ""))
                    if m and want is not None and abs(float(m.group(1)) - want) > 1.5: E(f"{where}: a visual is drawn at {m.group(1)}% but '{src}' says {want:.1f}%")
                    if m and want is None: E(f"{where}: a visual is drawn at {m.group(1)}% from '{src}', which states no proportion")
    return used

def fidelity(wf_path, ds_path):
    err, chk = [], []
    E, C = err.append, chk.append
    _, wn = parse(wf_path); _, dn = parse(ds_path)
    wf_inst = {n.a["data-instance-id"]: n for n in wn if "data-instance-id" in n.a and n.up(lambda p: "data-wf-chrome" in p.a) is None}
    wf_screens = {n.a["data-screen-id"]: n for n in wn if "data-screen-id" in n.a}
    wmeta = jblock(wn, "wf-meta") or {}
    reg = wmeta.get("components", {})
    frames = {f["id"]: f for f in wmeta.get("frames", [])}
    wf_atoms = {}
    for n in wn:
        if "data-atom" in n.a and n.up(lambda p: "data-wf-chrome" in p.a) is None:
            wf_atoms.setdefault(n.a["data-atom"], set()).add(n.a.get("data-variant") or "default")
    corrected = set()
    # 1 · the styled screens
    screens = [n for n in dn if "data-ds-screen" in n.a]
    if len(screens) != 3: E(f"{len(screens)} styled screens (data-ds-screen); exactly three")
    ks = wmeta.get("key_screens") or {}
    for n, key in (("1", "home"), ("2", "main"), ("3", "agent")):
        want_id = ks.get(key)
        if not want_id: continue
        s = next((x for x in screens if x.a.get("data-screen") == n), None)
        got = (s.a.get("data-ds-frame") or s.a.get("data-ds-screen")) if s is not None else None
        if got != want_id: E(f"styled screen {n} should be the wireframe's key_screens.{key} ({want_id}), found {got}")
    for s in screens:
        sid, fid = s.a["data-ds-screen"], s.a.get("data-ds-frame")
        if sid not in wf_screens: E(f"styled screen {sid} is not a wireframe screen"); continue
        if fid and (fid not in frames or frames[fid]["of"] != sid): E(f"styled screen {sid}: frame {fid} is not a frame of it in the wireframe")
        want = [n.a["data-instance-id"] for n in wf_screens[sid].walk() if "data-instance-id" in n.a]
        have = [n.a["data-instance-id"] for n in s.walk() if "data-instance-id" in n.a]
        if want != have:
            miss, extra = [x for x in want if x not in have], [x for x in have if x not in want]
            E(f"{sid}: instances differ from the wireframe" + (f"; missing {miss[:5]}" if miss else "") + (f"; added {extra[:5]}" if extra else "") + ("; order changed" if not miss and not extra else ""))
        root_w = next((n for n in wf_screens[sid].walk() if "wf-device" in n.a.get("class", "").split()), wf_screens[sid])
        root_d = next((n for n in s.walk() if "data-ds-device" in n.a), None)
        if root_d is None: E(f"{sid}: no element marked data-ds-device (the copy of the wireframe's .wf-device)")
        else:
            if root_w.text(SKIP) != root_d.text(SKIP): E(f"{sid}: the screen's text differs from the wireframe (near: '{first_diff(root_w.text(SKIP), root_d.text(SKIP))}')")
            if shape(root_w)[1:] != shape(root_d)[1:]: E(f"{sid}: the element tree differs from the wireframe (an element or a metadata attribute was added, removed or changed)")
            for n in root_d.walk():
                if "data-instance-id" in n.a and corrections(n, f"{sid} {n.a['data-instance-id']}", E, C): corrected.add(n.a.get("data-component-id"))
        st = (frames.get(fid) or {}).get("set", {}) if fid else {}
        for n in s.walk():
            iid = n.a.get("data-instance-id")
            if iid and iid in wf_inst:
                expect = st.get(iid, wf_inst[iid].a.get("data-state", "default"))
                if n.a.get("data-state", "default") != expect: E(f"{sid}: {iid} is in state '{n.a.get('data-state', 'default')}', the wireframe frame has '{expect}'")
        for n in s.walk():
            if DECOR(n) and n.tag not in ("svg", "img", "span", "i") : E(f"{sid}: decor element <{n.tag}> (decor is icons and picture art only)")
            if DECOR(n) and n.text(): E(f"{sid}: decor element carries text '{n.text()[:40]}'")
            if DECOR(n) and n.parent is not None and not ("data-icon" in n.parent.a or "data-media" in n.parent.a or "wf-img" in n.parent.a.get("class", "")):
                C(f"{sid}: decor added where the wireframe asked for no icon or picture (parent <{n.parent.tag}>)")
    html_d = next((n for n in dn if n.tag == "html"), None)
    # 2 · the catalogue
    cat = {n.a["data-component"]: n for n in dn if "data-catalogue" in n.a and "data-component" in n.a}
    for cid in reg:
        if cid not in cat: E(f"component '{cid}' (wireframe) has no catalogue entry")
    for cid in cat:
        if cid not in reg: E(f"catalogue entry '{cid}' is not a wireframe component")
    atoms = {n.a["data-catalogue-atom"] for n in dn if "data-catalogue-atom" in n.a}
    for a in wf_atoms:
        if a not in atoms: E(f"atom '{a}' is used in the wireframe but not in the catalogue")
    for a in atoms - set(wf_atoms): E(f"catalogue atom '{a}' is not used in the wireframe")
    for cid, c in cat.items():
        specs = [n for n in c.walk() if "data-specimen-of" in n.a]
        if not specs: E(f"'{cid}': the catalogue entry renders no specimen (data-specimen-of)")
        for sp in specs:
            if sp.a.get("data-active") != "true": E(f"'{cid}': specimen of {sp.a['data-specimen-of']} is not marked data-active=\"true\"")
        for sp in specs:
            src = wf_inst.get(sp.a["data-specimen-of"])
            if src is None: E(f"'{cid}': specimen of unknown instance {sp.a['data-specimen-of']}"); continue
            if src.a.get("data-component-id") != cid: E(f"'{cid}': specimen copies {sp.a['data-specimen-of']}, a {src.a.get('data-component-id')}")
            if src.text(SKIP) != sp.text(SKIP): E(f"'{cid}': specimen text differs from {sp.a['data-specimen-of']} (near: '{first_diff(src.text(SKIP), sp.text(SKIP))}')")
            if sp.a.get("data-state") and sp.a["data-state"] not in (src.a.get("data-states") or "default").split(): E(f"'{cid}': specimen state '{sp.a['data-state']}' is not one of the instance's states")
            if shape(src)[1:] != shape(sp)[1:]: E(f"'{cid}': specimen of {sp.a['data-specimen-of']} has a different element tree from its instance (only region wrappers and data-bound visuals may be added)")
            if corrections(sp, f"'{cid}' specimen", E, C): corrected.add(cid)
        insts = [i for i, n in wf_inst.items() if n.a.get("data-component-id") == cid]
        want = {"data-source-instances": set(insts),
                "data-source-screens": {i.split(".")[0] for i in insts},
                "data-component-type": {wf_inst[insts[0]].a.get("data-component-type")} if insts else set(),
                "data-variants": {wf_inst[i].a["data-variant"] for i in insts if wf_inst[i].a.get("data-variant")},
                "data-states": {st for i in insts for st in (wf_inst[i].a.get("data-states") or "default").split()}}
        for k, v in want.items():
            if k not in c.a: E(f"'{cid}': the entry has no {k} (traceability to the wireframe without a copy of it)")
            elif set(c.a[k].split()) != v: E(f"'{cid}': {k}=\"{c.a[k]}\" but the wireframe has \"{' '.join(sorted(v))}\"")
        for k in ("anatomy", "tokens", "states", "behaviour", "a11y", "responsive"):
            if not any(n.a.get("data-part") == k for n in c.walk()): C(f"'{cid}': no {k} part (data-part=\"{k}\")")
    # 3 · the document: order, navigation, overview, index, brand status, traceability
    order = ["overview", "index", "brand", "foundations", "color", "type", "space", "icons", "components", "screens", "themes", "qa"]
    found = [n.a["id"] for n in dn if n.tag == "section" and n.a.get("id") in order]
    if found != order: E(f"sections out of order or missing: have {found}, need {order}")
    nav = next((n for n in dn if "ds-nav" in n.a.get("class", "").split()), None)
    if nav is None: E("no .ds-nav with links to the sections")
    else:
        hrefs = {n.a.get("href") for n in nav.walk() if n.tag == "a"}
        for sec in order:
            if f"#{sec}" not in hrefs: E(f".ds-nav has no link to #{sec}")
    ov = next((n for n in dn if n.a.get("id") == "overview"), None)
    if ov is not None:
        st = ov.a.get("data-brand-status")
        if st not in ("complete", "incomplete"): E("#overview needs data-brand-status=\"complete\" or \"incomplete\"")
        placeholder = any(n.a.get("data-logo-status") in ("placeholder", "stand-in") for n in dn)
        if placeholder and st != "incomplete": E("a logo is a placeholder or stand-in, so #overview must say the brand is incomplete")
        for k in ("data-source-brd", "data-source-wireframe"):
            if not (html_d is not None and html_d.a.get(k)): E(f"<html> has no {k} (the overview names the BRD and wireframe used)")
    brand = next((n for n in dn if n.a.get("id") == "brand"), None)
    VARIANTS = {"primary", "horizontal", "stacked", "mark", "reversed", "one-colour", "app"}
    if brand is not None:
        kit = next((n for n in brand.walk() if "data-logo-kit" in n.a), None)
        if kit is None: E("#brand has no logo section (data-logo-kit); it is drawn whether or not the logo file was obtained")
        else:
            got = {n.a.get("data-logo-variant") for n in kit.walk() if "data-logo-variant" in n.a}
            if VARIANTS - got: E(f"the logo section has no slot for {', '.join(sorted(VARIANTS - got))} (data-logo-variant)")
            for n in kit.walk():
                if "data-logo-variant" in n.a and not any(k.tag in ("img", "svg") for k in n.walk()) and not any(k.a.get("data-logo-status") in ("placeholder", "stand-in") for k in n.walk()):
                    E(f"logo variant '{n.a['data-logo-variant']}' shows neither the logo nor a marked placeholder")
    idx = next((n for n in dn if n.a.get("id") == "index"), None)
    if idx is not None:
        rows = {n.a.get("href", "")[5:] for n in idx.walk() if n.tag == "a" and n.a.get("href", "").startswith("#cmp-")}
        for cid in reg:
            if cid not in rows: E(f"#index has no row linking to #cmp-{cid}")
        for r in rows - set(reg): E(f"#index links to #cmp-{r}, which is not a wireframe component")
    for cid, c in cat.items():
        if c.a.get("id") != f"cmp-{cid}": E(f"catalogue entry '{cid}' needs id=\"cmp-{cid}\"")
        if not any("ds-stage" in n.a.get("class", "").split() for n in c.walk()): E(f"'{cid}': the specimen is not in a .ds-stage")
        if any("data-ds-part" in n.a for n in c.walk()): E(f"'{cid}': numbered part markers (data-ds-part); name the parts in words in the anatomy part, so no number reads as content")
        if any("data-wireframe-of" in n.a or "ds-wf" in n.a.get("class", "").split() for n in c.walk()):
            E(f"'{cid}': the entry repeats the low-fidelity wireframe component; the catalogue stands alone and traces it with data-source-* and a link")
        if not any(n.tag == "a" and re.search(r"wireframes\.html#", n.a.get("href", "")) for n in c.walk()): C(f"'{cid}': no link to its wireframe screen")
    css_all = " ".join("".join(k for k in n.kids if isinstance(k, str)) for n in dn if n.tag == "style")
    kit_cls = set(re.findall(r"\.([a-zA-Z][\w-]*)", css_all)) - {x for x in re.findall(r"\.([a-zA-Z][\w-]*)", css_all) if x.startswith(("wf-", "ds-"))}
    for cid, c in cat.items():
        for sp in [n for n in c.walk() if "data-specimen-of" in n.a][:1]:
            used = {x for n in sp.walk() for x in n.a.get("class", "").split()}
            if not used & kit_cls: E(f"'{cid}': the specimen uses no kit class, so it renders unstyled")
    parts = {}
    for cid, c in cat.items():
        for n in c.walk():
            if n.a.get("data-part") in ("anatomy", "a11y", "responsive", "behaviour"):
                parts.setdefault((n.a["data-part"], n.text()), []).append(cid)
    for (p, txt), cids in parts.items():
        if len(cids) >= 3 and txt: C(f"the same {p} notes appear in {len(cids)} entries ({', '.join(cids[:3])}…); write them for each component")
    fixes = {n.a.get("data-component") for n in dn if n.tag == "li" and n.up(lambda p: p.a.get("id") == "corrections") is not None}
    for cid in sorted(x for x in corrected if x):
        if cid not in fixes: E(f"'{cid}' has anatomy corrections or data-bound visuals, but #corrections in the QA report does not list it (data-component=\"{cid}\")")
    # 4 · machine-readable blocks
    man = jblock(dn, "ds-manifest")
    if man is None: E("no #ds-manifest block")
    else:
        mc = man.get("components", {})
        for cid in reg:
            if cid not in mc: E(f"#ds-manifest has no '{cid}'"); continue
            inst = sorted(mc[cid].get("instances", []))
            want = sorted(i for i, n in wf_inst.items() if n.a.get("data-component-id") == cid)
            if inst != want: E(f"#ds-manifest '{cid}' instances differ from the wireframe")
        for cid in mc:
            if cid not in reg: E(f"#ds-manifest lists '{cid}', which the wireframe does not have")
        css = " ".join("".join(k for k in n.kids if isinstance(k, str)) for n in dn if n.tag == "style")
        declared = set(re.findall(r"(--[a-z0-9-]+)\s*:", css))
        for cid, e in mc.items():
            for t in e.get("tokens", []):
                if t not in declared: E(f"#ds-manifest '{cid}' names token {t}, which the stylesheet does not declare")
    bp = jblock(dn, "build-plan")
    if bp is None: E("no #build-plan block")
    else:
        pages = {p.get("id") for p in bp.get("pages", [])}
        for sid in wf_screens:
            if sid not in pages: E(f"page {sid} is not in #build-plan")
    if jblock(dn, "style-sets") is None: E("no #style-sets block")
    html_d = next((n for n in dn if n.tag == "html"), None); html_w = next((n for n in wn if n.tag == "html"), None)
    if html_d is not None and html_w is not None and html_d.a.get("data-agent-entry") != html_w.a.get("data-agent-entry"):
        E(f"data-agent-entry is '{html_d.a.get('data-agent-entry')}', the wireframe has '{html_w.a.get('data-agent-entry')}'")
    if any(n.tag == "img" and n.a.get("src", "").startswith("data:image/svg") and "data-logo" in (n.parent.a if n.parent else {}) and "trace" in n.a.get("alt", "").lower() for n in dn):
        E("a logo looks traced")
    for x in err: print("error:", x)
    for x in chk: print("check:", x)
    print(f"{len(screens)} styled screens · {len(cat)} catalogue entries for {len(reg)} wireframe components · {len(atoms)} atoms · {len(err)} errors · {len(chk)} checks")
    sys.exit(1 if err else 0)

def inventory(wf_path, out_path):
    """Read the wireframe and write the starting #ds-manifest, #build-plan and #style-sets blocks (JSON) for this run."""
    root, wn = parse(wf_path)
    meta = jblock(wn, "wf-meta")
    if meta is None: sys.exit("error: the wireframe has no wf-meta block; it was not made by the wireframes skill (HTML contract v1)")
    html = next((n for n in wn if n.tag == "html"), root)
    chrome = lambda n: n.up(lambda p: "data-wf-chrome" in p.a) is not None
    reg = meta.get("components", {})
    comps, atoms, pages = {}, {}, []
    for s in [n for n in wn if "data-screen-id" in n.a]:
        sid = s.a["data-screen-id"]; regions = []
        for n in s.walk():
            if "data-instance-id" in n.a:
                cid = n.a.get("data-component-id")
                e = comps.setdefault(cid, {"name": reg.get(cid, {}).get("name", cid), "type": n.a.get("data-component-type"),
                                           "instances": [], "screens": [], "variants": [], "states": [], "tokens": []})
                e["instances"].append(n.a["data-instance-id"])
                if sid not in e["screens"]: e["screens"].append(sid)
                v = n.a.get("data-variant")
                if v and v not in e["variants"]: e["variants"].append(v)
                for st in (n.a.get("data-states") or "default").split():
                    if st not in e["states"]: e["states"].append(st)
                if n.up(lambda p: "data-instance-id" in p.a) is None: regions.append(cid)
            if "data-atom" in n.a and not chrome(n):
                a = atoms.setdefault(n.a["data-atom"], {"variants": [], "states": [], "screens": []})
                v = n.a.get("data-variant") or "default"
                if v not in a["variants"]: a["variants"].append(v)
                for st, ok in (("disabled", "disabled" in n.a or n.a.get("aria-disabled") == "true"), ("invalid", n.a.get("aria-invalid") == "true")):
                    if ok and st not in a["states"]: a["states"].append(st)
                if sid not in a["screens"]: a["screens"].append(sid)
        pages.append({"id": sid, "title": s.a.get("data-screen-title"), "persona": s.a.get("data-persona"), "width": s.a.get("data-width"),
                      "pattern": s.a.get("data-pattern"), "regions": list(dict.fromkeys(regions)),
                      "frame": f"02b-wireframes/{os.path.basename(wf_path)}#{sid}"})
    titles = {p["id"]: p["title"] for p in pages}
    index = [{"component": cid, "name": e["name"], "type": e["type"], "screens": [f"{x} {titles.get(x, '')}" for x in e["screens"]],
              "instances": e["instances"], "variants": len(e["variants"]), "states": len(e["states"]), "link": f"#cmp-{cid}"} for cid, e in comps.items()]
    widths = sorted({int(p["width"] or 1280) for p in pages} | {int(f["width"]) for f in meta.get("frames", []) if f.get("width")})
    out = {"index": index, "targets": {"widths": widths, "desktop_only": all(w >= 1024 for w in widths)},
           "ds-manifest": {"format": "ds-manifest/1", "wireframe": os.path.basename(wf_path), "components": comps, "atoms": atoms,
                           "screens": [p["id"] for p in pages], "frames": [f["id"] for f in meta.get("frames", [])],
                           "key_screens": meta.get("key_screens"), "tokens": {}},
           "build-plan": {"app": {"shell": html.a.get("data-shell") or meta.get("app", {}).get("shell"), "agent_entry": html.a.get("data-agent-entry"),
                                  "theme": "", "surface": "", "fill": "", "density": ""},
                          "concept": (meta.get("signature") or {}).get("name"), "pages": pages,
                          "rules": [{"when": "any page", "use": "its wireframe screen: regions, order, components, content and interactions as drawn"}]},
           "style-sets": {"active": "S1", "sets": {"S1": {cid: (e["variants"] or ["default"]) for cid, e in comps.items()}},
                          "variants": {f"{cid}:{v}": d for cid, r in reg.items() for v, d in (r.get("variants") or {}).items()}}}
    json.dump(out, open(out_path, "w"), indent=2, ensure_ascii=False)
    gaps = [r for r in meta.get("requirements", []) if not r.get("covered_by")]
    print(f"{len(pages)} screens · {len(meta.get('frames', []))} frames · {len(comps)} components · {sum(len(e['instances']) for e in comps.values())} instances · "
          f"{len(atoms)} atom kinds · signature: {(meta.get('signature') or {}).get('component')} · agent entry: {html.a.get('data-agent-entry')} · "
          f"key screens: {meta.get('key_screens')} → {out_path}")
    for r in gaps: print(f"note: requirement {r.get('ref')} has no screen ({r.get('status')}): {r.get('need', '')[:70]}")
    for q in meta.get("open_questions", []): print(f"note: open question {q.get('id')}: {q.get('question', '')[:80]}")

def first_diff(a, b):
    i = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
    return (a[max(0, i - 20):i + 20] + " ≠ " + b[max(0, i - 20):i + 20]).replace("\n", " ")

AUDIT_JS = r"""() => {
  const out = {contrast: [], names: [], targets: [], hScroll: 0, fonts: {}, focus: []};
  const num = s => s.match(/[\d.]+%?/g).map(x => x.endsWith('%') ? parseFloat(x) / 100 : +x);
  const col = s => { if (!s) return null; let m = s.match(/^rgba?\(([^)]+)\)/); if (m) { const p = num(m[1]); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; }
    m = s.match(/^color\(srgb ([^)]+)\)/); if (m) { const p = num(m[1]); return [p[0] * 255, p[1] * 255, p[2] * 255, p.length > 3 ? p[3] : 1]; } return null; };
  const over = (t, b) => [t[0] * t[3] + b[0] * (1 - t[3]), t[1] * t[3] + b[1] * (1 - t[3]), t[2] * t[3] + b[2] * (1 - t[3]), 1];
  const lin = c => { c /= 255; return c <= .04045 ? c / 12.92 : ((c + .055) / 1.055) ** 2.4; };
  const Y = c => .2126 * lin(c[0]) + .7152 * lin(c[1]) + .0722 * lin(c[2]);
  const ratio = (a, b) => { const x = Y(a), y = Y(b); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05); };
  const stops = img => (img.match(/(rgba?\([^)]+\)|color\(srgb [^)]+\))/g) || []).map(col).filter(Boolean);
  function grounds(el) {               // every colour the text may sit on: each gradient stop, composited down to an opaque ground
    const chain = []; for (let n = el; n; n = n.parentElement) chain.push(n);
    let base = [[255, 255, 255, 1]];
    for (let i = chain.length - 1; i >= 0; i--) {
      const cs = getComputedStyle(chain[i]); const bc = col(cs.backgroundColor); const g = cs.backgroundImage !== 'none' ? stops(cs.backgroundImage) : [];
      if (bc && bc[3] > 0) base = base.map(b => over(bc, b));
      if (g.length && !/url\(/.test(cs.backgroundImage)) base = g.flatMap(s => base.map(b => over(s, b)));
      if (cs.opacity !== '1') { /* opacity dims the text and its ground together; measured as drawn */ }
    }
    return base;
  }
  const dim = el => el.closest(':disabled,[aria-disabled="true"],.off,[data-dim]');
  for (const el of document.querySelectorAll('body *')) {
    const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden' || el.closest('[hidden],[data-doc-chrome],.amb')) continue;
    const r = el.getBoundingClientRect(); if (!r.width || !r.height) continue;
    const own = [...el.childNodes].some(n => n.nodeType === 3 && n.nodeValue.trim());
    if (own && !dim(el)) {
      const fs = parseFloat(cs.fontSize), large = fs >= 24 || (fs >= 18.66 && +cs.fontWeight >= 700);
      const tc = col(cs.color); if (tc) { const worst = Math.min(...grounds(el).map(g => ratio(over(tc, g), g)));
        const need = large ? 3 : 4.5; if (worst < need - 0.005) out.contrast.push(`${worst.toFixed(2)} < ${need}: ${el.tagName.toLowerCase()}.${[...el.classList].join('.')} "${el.textContent.trim().slice(0, 40)}"`); }
    }
    if (el.matches('a[href],button,input:not([type=hidden]),select,textarea,[role=button],[role=tab],[tabindex]:not([tabindex="-1"])') && !el.closest('[data-doc-chrome]')) {
      const name = (el.getAttribute('aria-label') || el.textContent || el.value || el.title || (el.labels && el.labels[0] && el.labels[0].textContent) || '').trim();
      if (!name) out.names.push(`${el.tagName.toLowerCase()}.${[...el.classList].join('.')}`);
      const tr = el.closest('.ctl') ? el.closest('.ctl').getBoundingClientRect() : r;
      if ((tr.width < 24 || tr.height < 24) && !el.matches('input[type=checkbox],input[type=radio]') && cs.display !== 'inline') out.targets.push(`${Math.round(tr.width)}×${Math.round(tr.height)} ${el.tagName.toLowerCase()} "${name.slice(0, 30)}"`);
      el.focus({preventScroll: true});
      if (document.activeElement === el) { const f = getComputedStyle(el); if (f.outlineStyle === 'none' && f.boxShadow === 'none' && !el.closest('.ctl')) out.focus.push(`${el.tagName.toLowerCase()}.${[...el.classList].join('.')} "${name.slice(0, 30)}"`); }
      el.blur && el.blur();
    }
  }
  out.hScroll = document.documentElement.scrollWidth - document.documentElement.clientWidth;
  document.fonts.forEach(f => { out.fonts[f.family.replace(/["']/g, '')] = f.status; });
  return out;
}"""

SPEC_JS = r"""() => {
  const out = {blank: [], clipped: [], scroll: [], ladder: {}};
  const col = s => { const m = s && s.match(/rgba?\(([^)]+)\)|color\(srgb ([^)]+)\)/); if (!m) return null; const p = (m[1] || m[2]).split(/[ ,\/]+/).filter(Boolean).map(Number);
    return m[2] ? [p[0] * 255, p[1] * 255, p[2] * 255, p.length > 3 ? p[3] : 1] : [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; };
  const ground = el => { let c = [255, 255, 255]; const chain = []; for (let n = el; n; n = n.parentElement) chain.push(n);
    for (const n of chain.reverse()) { const b = col(getComputedStyle(n).backgroundColor); if (b && b[3] > 0) c = c.map((v, i) => b[i] * b[3] + v * (1 - b[3])); } return c; };
  const L = c => { const f = v => { v /= 255; v = v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; return v; }; const y = .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2]);
    return 116 * (y > 216 / 24389 ? Math.cbrt(y) : (24389 / 27 * y + 16) / 116) - 16; };
  for (const st of document.querySelectorAll('[data-catalogue] .ds-stage')) {
    const cat = st.closest('[data-catalogue]'), id = cat.dataset.component || cat.dataset.catalogueAtom, r = st.getBoundingClientRect();
    if (!r.width || !r.height || st.closest('[hidden]')) continue;
    let u = null;
    for (const el of st.querySelectorAll('*')) {
      const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden' || el.closest('[hidden],.sr')) continue;
      const b = el.getBoundingClientRect(); if (!b.width || !b.height) continue;
      const own = [...el.childNodes].some(n => n.nodeType === 3 && n.nodeValue.trim());
      const painted = (col(cs.backgroundColor) || [0, 0, 0, 0])[3] > 0 || cs.boxShadow !== 'none' || /^(IMG|SVG|INPUT|SELECT|TEXTAREA|CANVAS)$/i.test(el.tagName);
      if (/auto|scroll|hidden/.test(cs.overflowX) && el.scrollWidth > el.clientWidth + 2 && !el.dataset.seen) { el.dataset.seen = 1; out.clipped.push(`${id}: <${el.tagName.toLowerCase()}.${[...el.classList].join('.')}> hides ${el.scrollWidth - el.clientWidth}px of its content at this width; give the component its real width (a wide state row)`); }
      if (!own && !painted) continue;
      u = u ? {l: Math.min(u.l, b.left), t: Math.min(u.t, b.top), r: Math.max(u.r, b.right), b: Math.max(u.b, b.bottom)} : {l: b.left, t: b.top, r: b.right, b: b.bottom};
      if (own && cs.overflow !== 'visible' && el.scrollWidth > el.clientWidth + 1 && cs.textOverflow !== 'ellipsis') out.clipped.push(`${id}: text cut in <${el.tagName.toLowerCase()}> "${el.textContent.trim().slice(0, 30)}"`);
      if (getComputedStyle(st).overflow === 'hidden' && (b.right > r.right + 1 || b.bottom > r.bottom + 1) && own) out.clipped.push(`${id}: "${el.textContent.trim().slice(0, 30)}" runs outside its stage`);
    }
    const area = u ? Math.max(0, Math.min(u.r, r.right) - Math.max(u.l, r.left)) * Math.max(0, Math.min(u.b, r.bottom) - Math.max(u.t, r.top)) : 0;
    const ratio = area / (r.width * r.height), ov = st.classList.contains('ov');
    if (!u) out.blank.push(`${id}: the stage is empty`);
    else if (r.height > 160 && ratio < (ov ? .10 : .35)) out.blank.push(`${id}: ${Math.round(ratio * 100)}% of a ${Math.round(r.width)}×${Math.round(r.height)} stage is used`);
    if (!ov && st.scrollWidth > st.clientWidth + 2) out.scroll.push(`${id}: the specimen is ${st.scrollWidth - st.clientWidth}px wider than its stage`);
  }
  for (const cat of document.querySelectorAll('[data-catalogue]')) {
    const cr = cat.getBoundingClientRect(), id = cat.dataset.component || cat.dataset.catalogueAtom;
    for (const el of cat.querySelectorAll('*')) {
      const cs = getComputedStyle(el); if (!/absolute|fixed/.test(cs.position) || cs.display === 'none' || el.closest('[hidden]')) continue;
      const b = el.getBoundingClientRect(); if (!b.width || !b.height) continue;
      if (b.left < cr.left - 2 || b.right > cr.right + 2 || b.top < cr.top - 2 || b.bottom > cr.bottom + 2) { out.blank.push(`${id}: <${el.tagName.toLowerCase()}.${[...el.classList].join('.')}> escapes its catalogue entry`); break; }
    }
  }
  const main = document.querySelector('[data-screen="2"] [data-ds-device]'), agent = document.querySelector('[data-screen="3"] [data-ds-device]');
  if (main) {
    const nav = main.querySelector('[data-component-type="nav"]');
    let best = null, bestA = 0;   // the largest content surface: a card, a table ground, a tile, a document
    for (const el of main.querySelectorAll('.g1,.g2,.g3,.solid,.tblwrap,.tile,.wf-card,.wf-doc,[data-component-type="card"],[data-component-type="table"]')) {
      if ((nav && nav.contains(el)) || el.closest('[hidden]')) continue;
      const r = el.getBoundingClientRect(), a = r.width * r.height; if (a > bestA) { best = el; bestA = a; }
    }
    out.ladder.app = L(ground(main)); if (nav) out.ladder.nav = L(ground(nav)); if (best) out.ladder.surface = L(ground(best));
    if (best) out.ladder.lifted = getComputedStyle(best).boxShadow.split(/,(?![^(]*\))/).some(p => !/inset/.test(p) && p !== 'none') ? 1 : 0;
    const ov = agent && agent.querySelector('[data-component-type="drawer"]:not([hidden]),[data-component-type="modal"]:not([hidden])');
    if (ov) out.ladder.overlay = L(ground(ov));
  }
  return out;
}"""

ANAT_JS = r"""() => {
  // what a finished component needs and a coloured wireframe fragment lacks: an overlay with a header, body and footer; a
  // container that separates from the surface behind it; fields and buttons with a visible edge; no empty panel.
  const out = {anatomy: [], blend: [], edges: [], space: [], cut: [], touch: []};
  const col = s => { const m = s && s.match(/rgba?\(([^)]+)\)|color\(srgb ([^)]+)\)/); if (!m) return null; const p = (m[1] || m[2]).split(/[ ,\/]+/).filter(Boolean).map(Number);
    return m[2] ? [p[0] * 255, p[1] * 255, p[2] * 255, p.length > 3 ? p[3] : 1] : [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; };
  const over = (t, b) => [0, 1, 2].map(i => t[i] * t[3] + b[i] * (1 - t[3]));
  const lin = c => { c /= 255; return c <= .04045 ? c / 12.92 : ((c + .055) / 1.055) ** 2.4; };
  const Y = c => .2126 * lin(c[0]) + .7152 * lin(c[1]) + .0722 * lin(c[2]);
  const ratio = (a, b) => { const x = Y(a), y = Y(b); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05); };
  const Lab = c => { const y = Y(c); return 116 * (y > 216 / 24389 ? Math.cbrt(y) : (24389 / 27 * y + 16) / 116) - 16; };
  const ground = el => { let c = [255, 255, 255]; const chain = []; for (let n = el; n; n = n.parentElement) chain.push(n);
    for (const n of chain.reverse()) { const b = col(getComputedStyle(n).backgroundColor); if (b && b[3] > 0) c = over(b, c); } return c; };
  const edgeCols = el => { const cs = getComputedStyle(el), cols = [];
    for (const d of ['Top', 'Right', 'Bottom', 'Left']) if (parseFloat(cs['border' + d + 'Width']) >= 1 && cs['border' + d + 'Style'] !== 'none') cols.push(col(cs['border' + d + 'Color']));
    for (const part of (cs.boxShadow === 'none' ? [] : cs.boxShadow.split(/,(?![^(]*\))/))) {
      if (!/inset/.test(part)) continue; const c = col((part.match(/rgba?\([^)]+\)|color\(srgb [^)]+\)/) || [])[0]);
      const n = (part.replace(/rgba?\([^)]+\)|color\(srgb [^)]+\)/, '').match(/-?[\d.]+px/g) || []).map(parseFloat);
      if (c && (n[2] || 0) <= 1 && ((n[3] || 0) >= .5 || Math.abs(n[0] || 0) >= 1 || Math.abs(n[1] || 0) >= 1)) cols.push(c); }
    return cols.filter(Boolean); };
  const edge = el => { const g = ground(el.parentElement || el); return Math.max(1, ...edgeCols(el).map(c => ratio(over(c, g), g))); };
  const lifted = el => { const bs = getComputedStyle(el).boxShadow; return bs !== 'none' && bs.split(/,(?![^(]*\))/).some(p => !/inset/.test(p) && ((p.replace(/rgba?\([^)]+\)|color\(srgb [^)]+\)/, '').match(/-?[\d.]+px/g) || []).map(parseFloat)[2] || 0) >= 2); };
  const vis = el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0 && !el.closest('[hidden]') && getComputedStyle(el).visibility !== 'hidden'; };
  const name = el => (el.getAttribute('aria-label') || el.textContent || '').trim().replace(/\s+/g, ' ');
  const where = el => { const c = el.closest('[data-catalogue]'); return c ? `${c.dataset.component || c.dataset.catalogueAtom}` : el.closest('.ds-compare') ? 'light and dark comparison' : `screen ${(el.closest('[data-screen]') || {dataset: {}}).dataset.screen}`; };
  const id = el => el.dataset.specimenOf || el.dataset.instanceId;
  const scopes = [...document.querySelectorAll('[data-ds-device], .ds-stage')].filter(s => !s.closest('.ds-dark,.ds-compare'));
  const roots = new Set(); for (const sc of scopes) for (const el of sc.querySelectorAll('[data-specimen-of],[data-instance-id]')) if (vis(el)) roots.add(el);
  const CONTAINER = ['card', 'metric', 'record-header', 'document', 'drawer', 'modal', 'menu', 'popover', 'toast'];
  for (const el of roots) {
    const type = el.dataset.componentType, w = `${where(el)} · ${id(el)}`;
    if (type === 'drawer' || type === 'modal') {
      const mine = n => n.closest('[data-specimen-of],[data-instance-id]') === el;
      const heads = [...el.querySelectorAll('.pane-head,[data-ds-wrap="header"],header')].filter(h => vis(h) && mine(h) && h.querySelector('h1,h2,h3,h4'));
      const head = heads[0], foots = [...el.querySelectorAll('.pane-foot,[data-ds-wrap="footer"],footer')].filter(f => vis(f) && mine(f));
      const btns = [...el.querySelectorAll('button,[role=button]')].filter(b => vis(b) && mine(b));
      const close = btns.find(b => b.dataset.icon === 'close' || /^(close|×|✕)$/i.test(name(b)));
      if (!head) out.anatomy.push(`${w}: the ${type} has no header holding its title`);
      if (close && head && !head.contains(close)) out.anatomy.push(`${w}: the close control sits outside the ${type}'s header`);
      if (close && head && head.contains(close)) { const h = head.getBoundingClientRect(), b = close.getBoundingClientRect(); if (h.right - b.right > 40 || b.top - h.top > 40) out.anatomy.push(`check ${w}: the close control is not at the header's top end`); }
      const acts = btns.filter(b => b !== close && (b.matches('.btn-p') || b.dataset.variant === 'primary'));
      for (const a of acts) if (!foots.some(f => f.contains(a))) { out.anatomy.push(`${w}: "${name(a).slice(0, 30)}" sits in the body; a ${type}'s actions go in its footer`); break; }
      if (foots.length && head && el.closest('.ds-stage')) {
        const r = el.getBoundingClientRect(), f = foots[foots.length - 1].getBoundingClientRect();
        if (r.bottom - f.bottom > 24) out.anatomy.push(`check ${w}: the footer stops ${Math.round(r.bottom - f.bottom)}px above the ${type}'s bottom edge`);
      }
      if (el.closest('.ds-stage')) {   // empty panel: content ends far above the bottom (or the footer)
        let last = 0; for (const n of el.querySelectorAll('*')) { if (!vis(n) || foots.some(f => f.contains(n))) continue;
          if ([...n.childNodes].some(c => c.nodeType === 3 && c.nodeValue.trim()) || /^(INPUT|SELECT|TEXTAREA|IMG|svg|TABLE)$/i.test(n.tagName)) last = Math.max(last, n.getBoundingClientRect().bottom); }
        const r = el.getBoundingClientRect(), stop = foots.length ? foots[foots.length - 1].getBoundingClientRect().top : r.bottom, gap = stop - last;
        if (last && gap > 120 && gap > .25 * r.height) out.space.push(`${w}: ${Math.round(gap)}px of empty ${type} below its content; size the stage to the content`);
      }
    }
    const stage = el.closest('.ds-stage');
    if (stage && CONTAINER.includes(type) && el.dataset.specimenOf) {   // a raised surface needs stage around it on every side, or it merges with the entry
      const s = stage.getBoundingClientRect(), r = el.getBoundingClientRect(), gap = Math.min(r.top - s.top, s.right - r.right, s.bottom - r.bottom, r.left - s.left);
      if (gap < 8) out.blend.push(`${w}: the ${type} runs to the edge of its stage (${Math.round(gap)}px), so its edge merges with the entry around it`);
    }
    if (CONTAINER.includes(type) && el.parentElement) {
      const g = ground(el), p = ground(el.parentElement), dl = Math.abs(Lab(g) - Lab(p));
      if (dl < 2.5 && !lifted(el) && edge(el) < 1.3) out.blend.push(`${w}: the ${type} blends into the surface behind it (ΔL* ${dl.toFixed(1)}, no elevation, no visible edge)`);
    }
  }
  for (const sc of scopes) {
    for (const f of sc.querySelectorAll('input:not([type=hidden]):not([type=checkbox]):not([type=radio]):not([type=file]):not([type=range]),select,textarea')) {
      if (!vis(f) || f.disabled || f.closest('.ds-dark,.ds-compare')) continue;
      const host = f.closest('.ctl') || f, g = ground(host), p = ground(host.parentElement), b = Math.max(ratio(g, p), edge(host));
      if (b < 3) out.edges.push(`${where(f)} · ${f.id || f.name || f.tagName.toLowerCase()}: the field's edge is ${b.toFixed(2)}:1 against its surface (3:1 needed, WCAG 1.4.11)`);
    }
    for (const bt of sc.querySelectorAll('.btn:not(.btn-p):not(.btn-t):not(.btn-i)')) {
      if (!vis(bt) || bt.disabled || bt.closest('.ds-dark,.ds-compare')) continue;
      const g = ground(bt), p = ground(bt.parentElement), b = Math.max(ratio(g, p), edge(bt));
      if (b < 1.5) out.edges.push(`${where(bt)} · "${name(bt).slice(0, 30)}": the secondary button has no visible edge (${b.toFixed(2)}:1); it reads as loose text`);
    }
  }
  // a whole styled screen wider than the frame or column that shows it (the comparison included) is cut at its edge
  for (const dv of document.querySelectorAll('[data-ds-device]')) {
    if (!vis(dv)) continue; const r = dv.getBoundingClientRect();
    for (let p = dv.parentElement; p && p !== document.body; p = p.parentElement) {
      if (getComputedStyle(p).overflowX === 'visible') continue; const c = p.getBoundingClientRect();
      if (r.right > c.right + 1.5) out.cut.push(`${dv.closest('.ds-compare') ? 'light and dark comparison' : 'screen ' + ((dv.closest('[data-screen]') || {dataset: {}}).dataset.screen || '')}: the styled screen runs ${Math.round(r.right - c.right)}px past its frame and is cut; it keeps its wireframe width and is scaled to fit (ds-runtime)`);
      break;
    }
  }
  // cut: content that runs past an edge that hides overflow (the screen frame, a top bar, a card); scrolling regions are fine
  const OVL = '[data-component-type="drawer"],[data-component-type="modal"],[data-component-type="menu"],[data-component-type="popover"],[data-component-type="toast"]';
  for (const sc of document.querySelectorAll('[data-ds-device], .ds-stage')) {
    for (const el of sc.querySelectorAll('*')) {
      if (!vis(el) || el.closest('.sr') || (el.closest(OVL) && !el.closest(OVL).contains(sc))) continue;
      const own = [...el.childNodes].some(n => n.nodeType === 3 && n.nodeValue.trim()) || /^(INPUT|SELECT|TEXTAREA|BUTTON|IMG)$/i.test(el.tagName);
      if (!own) continue;
      let clip = null; for (let p = el.parentElement; p; p = p.parentElement) { const o = getComputedStyle(p).overflowX; if (o !== 'visible') { clip = /auto|scroll/.test(o) ? null : p; break; } if (p === sc) { clip = sc.matches('[data-ds-device]') ? sc : null; break; } }
      if (!clip) continue;
      const r = el.getBoundingClientRect(), c = clip.getBoundingClientRect();
      if (r.right > c.right + 1.5 || r.left < c.left - 1.5) out.cut.push(`${where(el)}: <${el.tagName.toLowerCase()}> "${name(el).slice(0, 30)}" runs ${Math.round(Math.max(r.right - c.right, c.left - r.left))}px past the edge of <${clip.tagName.toLowerCase()}.${[...clip.classList].slice(0, 2).join('.')}> and is cut`);
    }
    // touching: a button pressed against the text or control next to it. Inline text is measured line by line, and a
    // borderless text button by its words, so a link that follows a sentence on the same line is not a collision
    const boxed = el => { const cs = getComputedStyle(el); return (col(cs.backgroundColor) || [0, 0, 0, 0])[3] > .05 || cs.boxShadow !== 'none' || parseFloat(cs.borderTopWidth) > 0; };
    const textRects = el => { const r = document.createRange(); r.selectNodeContents(el); return [...r.getClientRects()].filter(x => x.width > 1 && x.height > 1); };
        for (const b of sc.querySelectorAll('.btn,button')) {
      if (!vis(b) || b.closest('.sr,.ds-dark,.ds-compare') || /absolute|fixed/.test(getComputedStyle(b).position)) continue;
      const bR = boxed(b) ? [b.getBoundingClientRect()] : textRects(b);
      let hit = null;
      for (const s of b.parentElement ? b.parentElement.children : []) {
        if (hit || s === b || !vis(s) || s.contains(b) || /absolute|fixed/.test(getComputedStyle(s).position) || !(s.textContent.trim() || s.matches('input,select,textarea,.btn,button'))) continue;
        const sR = /inline/.test(getComputedStyle(s).display) ? textRects(s) : (boxed(s) || s.matches('input,select,textarea') ? [s.getBoundingClientRect()] : textRects(s));
        for (const p of bR) for (const r of sR) {
          const hx = Math.min(p.right, r.right) - Math.max(p.left, r.left), vy = Math.min(p.bottom, r.bottom) - Math.max(p.top, r.top);
          const gap = hx > 0 && vy > 0 ? -1 : hx > 0 ? -vy : vy > 0 ? -hx : 99;
          if (gap < (hx > 0 ? 4 : 2) && !hit) hit = [s, gap];
        }
      }
      if (hit) out.touch.push(`${where(b)}: "${name(b).slice(0, 26)}" ${hit[1] < 0 ? 'overlaps' : 'touches'} "${name(hit[0]).slice(0, 26)}" (${Math.max(0, Math.round(hit[1]))}px); give them a gap from the spacing scale`);
    }
    // a select whose arrow sits on its edge: the native arrow with no room for it
    for (const s of sc.querySelectorAll('select')) {
      if (!vis(s) || s.closest('.ds-dark,.ds-compare')) continue;
      const cs = getComputedStyle(s), host = s.closest('.ctl') || s;
      if (cs.appearance !== 'none' && parseFloat(getComputedStyle(host).paddingRight) + parseFloat(cs.paddingRight) < 16) out.touch.push(`${where(s)}: the select's arrow sits against its edge; use the kit's select (its own chevron with room on the right)`);
    }
  }
  for (const k of Object.keys(out)) out[k] = [...new Set(out[k])];
  return out;
}"""

CONSIST_JS = r"""() => {
  const root = document.documentElement, cs0 = getComputedStyle(root), tok = n => cs0.getPropertyValue(n).trim();
  const probe = document.createElement('div'); document.body.appendChild(probe);
  const resolve = (prop, v) => { probe.style[prop] = ''; probe.style[prop] = v; return getComputedStyle(probe)[prop]; };
  const px = v => Math.round(parseFloat(v) * 10) / 10;
  const sizes = new Set(['--fs-page', '--fs-section', '--fs-body', '--fs-support', '--fs-meta', '--glyph-xs'].map(t => px(tok(t))));
  const fam = v => v.split(',')[0].replace(/["']/g, '').trim().toLowerCase();
  const fams = new Set([fam(tok('--font-ui')), fam(tok('--font-mono'))]);
  const spaces = new Set([0, ...[1, 2, 3, 4, 5, 6, 7, 8].map(i => px(tok('--sp-' + i)))]);
  const radii = new Set([0, px(tok('--r')), px(tok('--r-sm')), 12, 16, 22, 28]);
  const colours = new Set(['rgba(0, 0, 0, 0)', 'rgb(255, 255, 255)', 'rgb(0, 0, 0)']);
  const walk = rules => { for (const r of rules) { if (r.cssRules) walk([...r.cssRules]); if (!r.style) continue;
      for (const p of r.style) if (p.startsWith('--')) { const v = r.style.getPropertyValue(p).trim(); if (/^(#|rgb|hsl|color)/.test(v)) colours.add(resolve('color', v)); } } };
  for (const sh of document.styleSheets) { try { walk([...sh.cssRules]); } catch (e) {} }
  probe.remove();
  const out = {size: {}, family: {}, weight: {}, radius: {}, gap: {}, colour: {}, borders: [], gradients: [], icons: {}, drift: []};
  const add = (bag, k, ex) => { (bag[k] = bag[k] || {n: 0, ex: ex}).n++; };
  const label = el => `${el.tagName.toLowerCase()}${[...el.classList].filter(c => !c.startsWith('wf-')).slice(0, 2).map(c => '.' + c).join('')}`;
  const scope = [...document.querySelectorAll('[data-ds-device], .ds-stage')].filter(s => !s.closest('.ds-wf,.ds-dark,.ds-compare'));
  const seen = new Set();
  for (const sc of scope) for (const el of [sc, ...sc.querySelectorAll('*')]) {
    if (seen.has(el) || el.closest('.ds-wf,[hidden]')) continue; seen.add(el);
    const cs = getComputedStyle(el); if (cs.display === 'none') continue;
    const own = [...el.childNodes].some(n => n.nodeType === 3 && n.nodeValue.trim());
    if (own) {
      const f = px(cs.fontSize); if (!sizes.has(f)) add(out.size, f + 'px', label(el));
      if (!fams.has(fam(cs.fontFamily))) add(out.family, fam(cs.fontFamily), label(el));
      if (!['400', '500', '600'].includes(cs.fontWeight)) add(out.weight, cs.fontWeight, label(el));
      if (!colours.has(cs.color)) add(out.colour, 'text ' + cs.color, label(el));
    }
    const bg = cs.backgroundColor; if (bg !== 'rgba(0, 0, 0, 0)' && !colours.has(bg)) add(out.colour, 'surface ' + bg, label(el));
    const r = px(cs.borderTopLeftRadius); if (r && r < 900 && !radii.has(r) && !(el.offsetHeight && Math.abs(r - el.offsetHeight / 2) < 2)) add(out.radius, r + 'px', label(el));
    const layout = [...el.classList].some(c => /^(wf-(row|stack|main|inline|split|header|app)|stack|row|grid|app-body)$/.test(c));
    if (layout) for (const g of [cs.rowGap, cs.columnGap]) if (g && g !== 'normal' && /flex|grid/.test(cs.display) && !spaces.has(px(g))) add(out.gap, px(g) + 'px', label(el));
    if (el.matches('.g1,.g2,.g3,.tile,.drawer,.modal,.doc,[data-component-type="card"]') && ['Top', 'Right', 'Bottom', 'Left'].some(d => parseFloat(cs['border' + d + 'Width']) > 0 && cs['border' + d + 'Style'] !== 'none'))
      out.borders.push(label(el));
    const sheen = /gradient/.test(cs.backgroundImage) && (cs.backgroundImage.match(/rgba?\([^)]+\)/g) || []).every(c => /^rgba?\(255, 255, 255(, (0|0?\.[0-3]\d*))?\)$/.test(c) && /,\s*(0|0?\.[0-3]\d*)\)$/.test(c));
    if (/gradient/.test(cs.backgroundImage) && !sheen && !el.matches('.app-rail,.app-top,.wash,[data-ds-device]')) { const b = el.getBoundingClientRect(); if (b.width * b.height > 24000) out.gradients.push(`${label(el)} ${Math.round(b.width)}×${Math.round(b.height)}`); }
    if (el.tagName.toLowerCase() === 'svg' && el.closest('[data-icon]')) add(out.icons, `${Math.round(el.getBoundingClientRect().width)}px stroke ${el.getAttribute('stroke-width') || cs.strokeWidth}`, label(el.closest('[data-icon]')));
  }
  const sig = {};
  for (const el of document.querySelectorAll('[data-ds-device] [data-component-id], .ds-stage [data-component-id]')) {
    if (el.closest('.ds-wf,.ds-dark,.ds-compare,[hidden]') || ['drawer', 'modal', 'toast', 'menu', 'popover'].includes(el.dataset.componentType)) continue;
    const cs = getComputedStyle(el), key = el.dataset.componentId + (el.dataset.variant ? ':' + el.dataset.variant : '');
    const s = [cs.fontSize, cs.fontWeight, cs.paddingTop, cs.paddingLeft, cs.borderTopLeftRadius, cs.backgroundColor, cs.boxShadow === 'none' ? 'flat' : 'raised', /gradient/.test(cs.backgroundImage) ? 'gradient' : 'no gradient'].join(' | ');
    (sig[key] = sig[key] || {}); (sig[key][s] = sig[key][s] || []).push(el.dataset.instanceId || el.dataset.specimenOf);
  }
  for (const [k, v] of Object.entries(sig)) if (Object.keys(v).length > 1) out.drift.push(`${k}: ${Object.entries(v).map(([s, ids]) => `[${s}] on ${ids.slice(0, 2).join(', ')}`).join(' vs ')}`);
  return out;
}"""

def audit(ds_path, out_dir=None):
    from playwright.sync_api import sync_playwright
    from PIL import Image, ImageDraw
    url = "file://" + os.path.abspath(ds_path); err, chk = [], []
    out_dir = out_dir or os.path.join(os.path.dirname(os.path.abspath(ds_path)), "_working", "qa")
    os.makedirs(os.path.join(out_dir, "catalogue"), exist_ok=True)
    _, dn = parse(ds_path)
    widths = sorted({int(p.get("width") or 1280) for p in ((jblock(dn, "build-plan") or {}).get("pages") or [])} or {1280})
    desktop_only = all(w >= 1024 for w in widths)
    # the document is read at 1,440 px; each styled screen and specimen keeps its own wireframe width inside it.
    # 1,024 px is a robustness pass only: findings there are checks, never failures, and nothing is designed for it.
    checks = [(1440, False), (1024, True)]
    with sync_playwright() as pw:
        try: b = pw.chromium.launch()
        except Exception:
            import shutil
            exe = next((c for c in ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"] + [shutil.which(n) or "" for n in ("chromium", "google-chrome", "google-chrome-stable")] if c and os.path.exists(c)), None)
            if not exe: sys.exit("audit: no Chromium could be started")
            b = pw.chromium.launch(executable_path=exe)
        ladders, consist, lifts = {}, {}, {}
        for theme in ("light", "dark"):
            for w, robust in checks:
                pg = b.new_page(viewport={"width": w, "height": 900}, color_scheme=theme); errs = []
                pg.on("pageerror", lambda e: errs.append(str(e)))
                pg.goto(url); pg.evaluate(f"document.documentElement.dataset.theme='{theme}'")
                pg.wait_for_function("document.documentElement.dataset.ready==='1'", timeout=10000); pg.wait_for_timeout(400)
                tag = f"{theme} {w}px" + (" (robustness only)" if robust else "")
                r = pg.evaluate(AUDIT_JS); bad = chk.append if robust else err.append
                for x in errs: err.append(f"{tag}: script error {x}")
                if r["hScroll"] > 2: bad(f"{tag}: {r['hScroll']}px of sideways page scroll")
                if not robust:
                    for x in r["contrast"][:12]: err.append(f"{tag}: contrast {x}")
                    if len(r["contrast"]) > 12: err.append(f"{tag}: … and {len(r['contrast']) - 12} more contrast failures")
                    for x in r["names"][:6]: err.append(f"{tag}: control with no accessible name: {x}")
                    for x in r["focus"][:6]: err.append(f"{tag}: no visible focus on {x}")
                    for x in sorted(set(r["targets"]))[:6]: chk.append(f"{tag}: target under 24 px: {x}")
                    for f, st in r["fonts"].items():
                        if st != "loaded": chk.append(f"{tag}: font {f} is {st} (not embedded or not used)")
                    s = pg.evaluate(SPEC_JS)
                    for x in s["blank"]: err.append(f"{tag}: blank specimen · {x}")
                    for x in s["clipped"][:12]: err.append(f"{tag}: clipped · {x}")
                    for x in s["scroll"]: err.append(f"{tag}: overflowing specimen · {x}")
                    lifts[theme] = s["ladder"].pop("lifted", 0); ladders[theme] = s["ladder"]
                    a = pg.evaluate(ANAT_JS)
                    for x in a["anatomy"]: (chk.append(f"{tag}: anatomy · {x[6:]}") if x.startswith("check ") else err.append(f"{tag}: anatomy · {x}"))
                    for x in a["blend"][:10]: err.append(f"{tag}: surface · {x}")
                    for x in a["edges"][:10]: err.append(f"{tag}: edge · {x}")
                    for x in a["space"]: err.append(f"{tag}: empty space · {x}")
                    for x in a["cut"][:10]: err.append(f"{tag}: cut · {x}")
                    for x in a["touch"][:10]: err.append(f"{tag}: spacing · {x}")
                    c = pg.evaluate(CONSIST_JS); consist[theme] = c
                    top = lambda bag: ", ".join(f"{k} ×{v['n']} (e.g. {v['ex']})" for k, v in sorted(bag.items(), key=lambda x: -x[1]["n"])[:5])
                    if c["size"]: err.append(f"{tag}: polish · font sizes off the five roles: {top(c['size'])}")
                    if c["family"]: err.append(f"{tag}: polish · font families other than --font-ui and --font-mono: {top(c['family'])}")
                    if c["weight"]: err.append(f"{tag}: polish · font weights other than 400, 500, 600: {top(c['weight'])}")
                    if c["colour"]: err.append(f"{tag}: polish · colours that are no token: {top(c['colour'])}")
                    for x in c["drift"][:8]: err.append(f"{tag}: polish · one component, different treatments: {x}")
                    if c["radius"]: chk.append(f"{tag}: polish · radii off the scale: {top(c['radius'])}")
                    if c["gap"]: chk.append(f"{tag}: polish · gaps off the spacing scale: {top(c['gap'])}")
                    if c["borders"]: chk.append(f"{tag}: polish · bordered cards or panels (separate by tone and elevation): {', '.join(sorted(set(c['borders']))[:6])}")
                    if len(c["icons"]) > 2: chk.append(f"{tag}: polish · {len(c['icons'])} icon size/stroke combinations: {top(c['icons'])}")
                    if c["gradients"]: chk.append(f"{tag}: polish · {len(c['gradients'])} large gradient surfaces outside the rail; confirm each is a deliberate brand moment and not behind dense data: {', '.join(c['gradients'][:5])}")
                    pg.screenshot(path=os.path.join(out_dir, f"page-{theme}-{w}.png"), full_page=True)
                    for i, el in enumerate(pg.locator("[data-catalogue]").all()):
                        cid = el.get_attribute("data-component") or ("atom-" + (el.get_attribute("data-catalogue-atom") or str(i)))
                        el.screenshot(path=os.path.join(out_dir, "catalogue", f"{cid}-{theme}.png"))
                    for i, el in enumerate(pg.locator("[data-ds-screen]").all()):
                        el.screenshot(path=os.path.join(out_dir, f"screen-{el.get_attribute('data-screen')}-{theme}.png"))
                pg.close()
        b.close()
    for theme, ld in ladders.items():
        app, nav, srf, ovl = (ld.get(k) for k in ("app", "nav", "surface", "overlay"))
        if srf is None: chk.append(f"{theme}: no card, table ground or document on styled screen 2 to measure the surface hierarchy; judge it by eye")
        if app is not None and srf is not None and abs(app - srf) < 2:
            if lifts.get(theme): chk.append(f"{theme}: content surfaces (L* {srf:.0f}) share the app background's tone (L* {app:.0f}) and separate by elevation alone; confirm every card's edge shows")
            else: err.append(f"{theme}: content surfaces (L* {srf:.0f}) are not distinguishable from the app background (L* {app:.0f}), and they have no elevation; the page reads flat")
        if nav is not None and srf is not None and abs(nav - srf) < 3: chk.append(f"{theme}: the navigation (L* {nav:.0f}) barely separates from content (L* {srf:.0f})")
        if theme == "dark" and ovl is not None and srf is not None and ovl < srf: err.append(f"dark: the drawer or modal (L* {ovl:.0f}) is darker than the content surface (L* {srf:.0f}); raised surfaces get lighter in dark")
    cats = sorted(f for f in os.listdir(os.path.join(out_dir, "catalogue")) if f.endswith(".png"))
    for theme in ("light", "dark"):
        files = [f for f in cats if f.endswith(f"-{theme}.png")]
        for n in range(0, len(files), 8):
            cells = []
            for f in files[n:n + 8]:
                im = Image.open(os.path.join(out_dir, "catalogue", f)).convert("RGB"); sc = 640 / im.width
                im = im.resize((640, max(1, int(im.height * sc)))); im = im.crop((0, 0, 640, min(im.height, 760)))
                cell = Image.new("RGB", (640, 790), "white"); cell.paste(im, (0, 30)); ImageDraw.Draw(cell).text((8, 8), f[:-4], fill="#222"); cells.append(cell)
            sheet = Image.new("RGB", (4 * 650 + 10, ((len(cells) + 3) // 4) * 800 + 10), "#bdbdbd")
            for i, c in enumerate(cells): sheet.paste(c, (10 + (i % 4) * 650, 10 + (i // 4) * 800))
            sheet.save(os.path.join(out_dir, f"contact-{theme}-{n // 8 + 1}.png"))
    json.dump({"surface_lightness": ladders, "consistency": consist}, open(os.path.join(out_dir, "consistency.json"), "w"), indent=1)
    for x in dict.fromkeys(err): print("error:", x)
    for x in dict.fromkeys(chk): print("check:", x)
    print(f"audit at {', '.join(str(w) + 'px' + (' (robustness)' if r else '') for w, r in checks)} · screens at {', '.join(map(str, widths))}px ({'desktop only' if desktop_only else 'includes phone'}) · "
          f"surface L* {json.dumps({t: {k: round(v) for k, v in l.items()} for t, l in ladders.items()})} · {len(set(err))} errors · {len(set(chk))} checks · screenshots and contact sheets in {out_dir}")
    sys.exit(1 if err else 0)

def embed(path):
    """Put the skill's fixed runtime into the page, so it is never typed by hand."""
    js = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "ds-runtime.js")).read()
    t = open(path, encoding="utf-8").read()
    t, n = re.subn(r'(<script id="ds-runtime"[^>]*>).*?(</script>)', lambda m: m.group(1) + "\n" + js + m.group(2), t, flags=re.S)
    if not n:
        sys.exit('embed: the page needs <script id="ds-runtime"></script> before </body>')
    open(path, "w", encoding="utf-8").write(t)
    print(f"embedded ds-runtime ({len(js)} chars) into {path}")

if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "embed": embed(sys.argv[2]); sys.exit(0)
    if len(sys.argv) >= 4 and sys.argv[1] == "fidelity": fidelity(sys.argv[2], sys.argv[3])
    elif len(sys.argv) >= 4 and sys.argv[1] == "inventory": inventory(sys.argv[2], sys.argv[3])
    elif len(sys.argv) >= 3 and sys.argv[1] == "audit": audit(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    else: sys.exit(__doc__)
