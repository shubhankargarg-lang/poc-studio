#!/usr/bin/env python3
"""wf_tool v2 — the wireframe HTML is the only deliverable; this tool embeds its fixed parts, checks it, writes the
internal manifest, and takes review screenshots. Standard library only, except `review` (a browser; Pillow optional).
usage: wf_tool.py embed    <wireframes.html>                fills <style id="wf-base"> and <script id="wf-runtime"> from the
                                                            skill's assets (never typed by hand)
       wf_tool.py manifest <wireframes.html> <out_dir>      writes wireframe-manifest.json and <slug>.wireframe.json (internal:
                                                            coverage.py, diff.py, the build plan; never uploaded or shown)
       wf_tool.py check    <wireframes.html>                prints error:/check: lines; exit 1 on any error
       wf_tool.py review   <wireframes.html> <qa_dir>       screenshots of every screen and frame, reading-order overlays and
                                                            contact sheets in <qa_dir> (02b-wireframes/_working/qa) for the
                                                            visual review only; no browser → says so and exits 0
"""
import hashlib, json, os, re, sys
from html.parser import HTMLParser

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
OVERLAY = {"drawer", "modal", "toast", "menu", "popover"}
TYPES = {"nav", "header", "tabs", "filter-bar", "table", "list", "card", "record-header", "form", "chart", "metric", "board", "calendar",
         "timeline", "stepper", "media", "document", "map", "chat", "ai-answer", "drawer", "modal", "toast", "banner", "menu", "popover",
         "empty-state", "diff", "tree", "graph", "compare", "upload", "rating"}

class Node:
    def __init__(s, tag, attrs, parent):
        s.tag, s.a, s.parent, s.kids = tag, dict(attrs), parent, []
    def walk(s):
        yield s
        for k in s.kids:
            if isinstance(k, Node): yield from k.walk()
    def text(s):
        if s.tag in ("script", "style", "template"): return ""
        return " ".join(" ".join((k if isinstance(k, str) else k.text()) for k in s.kids).split())
    def up(s, pred):
        p = s.parent
        while p is not None and not pred(p): p = p.parent
        return p

class Tree(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True); s.root = Node("#doc", {}, None); s.cur = s.root
    def handle_starttag(s, tag, attrs):
        n = Node(tag, [(k, v if v is not None else "") for k, v in attrs], s.cur); s.cur.kids.append(n)
        if tag not in VOID: s.cur = n
    def handle_startendtag(s, tag, attrs):
        s.cur.kids.append(Node(tag, [(k, v if v is not None else "") for k, v in attrs], s.cur))
    def handle_endtag(s, tag):
        n = s.cur
        while n is not None and n.tag != tag: n = n.parent
        if n is not None and n.parent is not None: s.cur = n.parent
    def handle_data(s, data):
        s.cur.kids.append(data)

def load(path):
    t = Tree(); t.feed(open(path, encoding="utf-8").read()); nodes = list(t.root.walk())
    meta_n = next((n for n in nodes if n.a.get("id") == "wf-meta"), None)
    if meta_n is None: sys.exit("error: no <script type=\"application/json\" id=\"wf-meta\">")
    raw = "".join(k for k in meta_n.kids if isinstance(k, str))
    try: meta = json.loads(raw)
    except Exception as e: sys.exit(f"error: wf-meta is not valid JSON: {e}")
    html = next((n for n in nodes if n.tag == "html"), t.root)
    return nodes, meta, html

def in_chrome(n): return n.up(lambda p: "data-wf-chrome" in p.a) is not None or "data-wf-chrome" in n.a
def screen_of(n): return n.up(lambda p: "data-screen-id" in p.a)
def toks(v): return [x for x in re.split(r"[\s,]+", v or "") if x]

def collect(path):
    nodes, meta, html = load(path)
    screens = [n for n in nodes if "data-screen-id" in n.a]
    insts = [n for n in nodes if "data-instance-id" in n.a and not in_chrome(n)]
    atoms = [n for n in nodes if "data-atom" in n.a and not in_chrome(n)]
    return nodes, meta, html, screens, insts, atoms

def manifest(path, out):
    nodes, meta, html, screens, insts, atoms = collect(path)
    reg = meta.get("components", {})
    sinfo = meta.get("screens", {})
    comps = {}
    for n in insts:
        cid, sc = n.a.get("data-component-id", ""), screen_of(n)
        sid = sc.a["data-screen-id"] if sc else "?"
        r = reg.get(cid, {})
        e = comps.setdefault(cid, {"component": cid, "name": r.get("name", cid), "type": n.a.get("data-component-type") or r.get("type", ""),
                                   "pages": [], "blocks": [], "instances": [], "variants": [], "features": [], "states": [], "cmp": []})
        if sid not in e["pages"]: e["pages"].append(sid)
        e["blocks"].append(f"{sid}/{n.a['data-instance-id']}")
        refs = toks(n.a.get("data-brd-ref"))
        e["instances"].append({"id": n.a["data-instance-id"], "screen": sid, "variant": n.a.get("data-variant") or None,
                               "states": toks(n.a.get("data-states")) or ["default"], "initial": n.a.get("data-state", "default"),
                               "brd_ref": refs, "interactions": sorted({c.a["data-interaction"] for c in n.walk() if "data-interaction" in c.a})})
        v = n.a.get("data-variant")
        if v and v not in e["variants"]: e["variants"].append(v)
        for s in toks(n.a.get("data-states")) or ["default"]:
            if s not in e["states"]: e["states"].append(s)
        for c in refs:
            if c.startswith("CMP-") and c not in e["cmp"]: e["cmp"].append(c)
    for cid, e in comps.items():
        r = reg.get(cid, {})
        for k in ("purpose", "shows", "does", "volume", "primary", "hero", "signature", "media", "views", "modes", "data_contract", "behaviour", "notes"):
            if k in r: e[k] = r[k] if k != "purpose" else ([r[k]] if isinstance(r[k], str) else r[k])
        e["variant_defs"] = r.get("variants", {})
        e["features"] = sorted(set(r.get("features", [])))
    at = {}
    for n in atoms:
        k = n.a["data-atom"]; e = at.setdefault(k, {"atom": k, "variants": [], "states": [], "screens": []})
        v = n.a.get("data-variant") or "default"
        if v not in e["variants"]: e["variants"].append(v)
        st = ["disabled"] if ("disabled" in n.a or n.a.get("aria-disabled") == "true") else []
        st += ["invalid"] if n.a.get("aria-invalid") == "true" else []
        for s in st:
            if s not in e["states"]: e["states"].append(s)
        sc = screen_of(n); sid = sc.a["data-screen-id"] if sc else "?"
        if sid not in e["screens"]: e["screens"].append(sid)
    pages = []
    for s in screens:
        sid = s.a["data-screen-id"]; si = sinfo.get(sid, {})
        body = s.text() + "|" + "|".join(f"{n.a.get('data-instance-id')}:{n.a.get('data-state','')}" for n in s.walk() if "data-instance-id" in n.a)
        pages.append({"id": sid, "title": s.a.get("data-screen-title", ""), "persona": s.a.get("data-persona"),
                      "width": int(s.a.get("data-width", "1280") or 1280), "brd_ref": s.a.get("data-brd-ref"),
                      "pattern": s.a.get("data-pattern"), "layout": "map" if s.a.get("data-pattern") == "map" else None,
                      "shape": si.get("shape"), "brief": si.get("brief"),
                      "content_hash": hashlib.sha1(body.encode()).hexdigest()[:12]})
    slug = html.a.get("data-slug") or meta.get("slug") or "app"
    app = dict(meta.get("app", {})); app.setdefault("shell", html.a.get("data-shell", "left"))
    m = {"format": "wireframe-manifest/html-1", "source": os.path.basename(path),
         "app": app.get("name"), "client": meta.get("client"), "use_case": meta.get("use_case"), "today": meta.get("today"),
         "shells": sorted({"phone" if p["width"] < 600 else "desktop" for p in pages}), "pages": pages,
         "frames": meta.get("frames", []), "signature": meta.get("signature"), "journey": meta.get("journey", []),
         "brd_overrides": meta.get("brd_overrides", []), "references": meta.get("references", []),
         "hero_object": meta.get("hero_object"), "shell": app["shell"], "nav_options": meta.get("nav_options", []),
         "agent_entry": html.a.get("data-agent-entry") or meta.get("agent_entry"), "payoff_frame": meta.get("payoff_frame"),
         "key_screens": meta.get("key_screens"),
         "alt_views": meta.get("alt_views", []), "open_questions": meta.get("open_questions", []),
         "assumptions": meta.get("assumptions", []), "components": list(comps.values()), "atoms": list(at.values()), "page_parts": []}
    os.makedirs(out, exist_ok=True)
    json.dump(m, open(os.path.join(out, "wireframe-manifest.json"), "w"), indent=2, ensure_ascii=False)
    idx = {"format": "wireframe-index/html-1", "source": os.path.basename(path), "client": meta.get("client"),
           "use_case": meta.get("use_case"), "slug": slug, "app": app, "today": meta.get("today"), "signature": meta.get("signature"),
           "nav_options": meta.get("nav_options", []), "hero_object": meta.get("hero_object"), "journey": meta.get("journey", []),
           "brd_overrides": meta.get("brd_overrides", []), "payoff_frame": meta.get("payoff_frame"), "frames": meta.get("frames", []),
           "pages": pages + [{"id": f["id"], "title": f.get("title", ""), "frame_of": f["of"], "set": f.get("set", {})} for f in meta.get("frames", [])]}
    json.dump(idx, open(os.path.join(out, f"{slug}.wireframe.json"), "w"), indent=2, ensure_ascii=False)
    print(f"{len(pages)} screens · {len(meta.get('frames', []))} frames · {len(comps)} components · {len(insts)} instances · {len(at)} atom kinds → {out}")

BANNED = r"\b(lorem|ipsum|tbd|placeholder|dummy|synthetic|demo|simulated?|sample data|john doe|jane doe|foo|bar baz)\b"
FILLER = r"\b(delve|landscape|pivotal|seamless(ly)?|robust|leverage|unlock|transformative|testament|empower|streamline|cutting-edge)\b"
GENERIC = {"overview", "insights", "quick actions", "recent activity", "at a glance", "key metrics", "welcome back", "dashboard", "details", "summary", "chart 1", "chart", "untitled", "title"}
# the team's "Dos and don'ts to reduce AI slop" (Writing, Screens, Charts), kept here for the review pass and not in the instructions
PRAISE = r"\b(powerful|effortless(ly)?|world-class|best-in-class|game-?changer|revolutionary|next-gen(eration)?|state-of-the-art|supercharge|elevate|unparalleled|holistic)\b"
TELLS = r"(\bnot just\b.*\bit'?s\b|\bin today's\b|\bin conclusion\b|\blet me know\b|\boops\b|\bmay potentially\b|\bsomething went wrong\b)"
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U0001F000-\U0001F2FF\U00002600-\U000026FF\U00002700-\U00002712\U00002718-\U000027BF]")   # ✓ ✔ ✕ ✖ ✗ stay: they are text marks
PATHS = r"(\b[\w-]+\.(py|json|js|md|yaml|yml|csv|html|docx?)\b|/Users/|~/|\brun[ _-]?id\b|\bstack trace\b|\bHTTP \d{3}\b)"
CODES = r"\b(PG|CMP|WF|AG|OB|AU)-\d+[a-z]?\b"
DOCS = r"\b(invoice|receipt|purchase order|certificate|statement|delivery note|lab(oratory)? (report|result)|contract|quotation|credit note|payslip|bill of lading)\b"

def check(path):
    nodes, meta, html, screens, insts, atoms = collect(path)
    err, chk = [], []
    E, C = err.append, chk.append
    reg = meta.get("components", {})
    for k in ("app", "client", "use_case", "today", "signature", "journey", "components", "screens"):
        if not meta.get(k): E(f"wf-meta has no '{k}'")
    allow = [w.lower() for w in meta.get("allow_words", [])]
    exact = {x.strip().lower() for x in meta.get("exact_copy", [])}
    sids = [s.a["data-screen-id"] for s in screens]
    for s in set(x for x in sids if sids.count(x) > 1): E(f"screen id {s} used twice")
    fids = [f["id"] for f in meta.get("frames", [])]
    targets = set(sids) | set(fids)
    for s in screens:
        sid = s.a["data-screen-id"]
        for k in ("data-screen-title", "data-persona", "data-width", "data-pattern"):
            if not s.a.get(k): E(f"{sid}: screen needs {k}")
        b = (meta.get("screens", {}).get(sid) or {}).get("brief") or {}
        for k in ("job", "decision", "next"):
            if not b.get(k): E(f"{sid}: brief has no '{k}' (wf-meta.screens)")
        def shown(n, who):
            p = n
            while p is not None and p is not s:
                if "data-for" in p.a and who not in toks(p.a["data-for"]): return False
                if "data-when" in p.a:
                    owner = p.up(lambda q: "data-instance-id" in q.a)
                    if owner is not None and owner.a.get("data-state", "default") not in toks(p.a["data-when"]): return False
                if p.a.get("data-component-type") in OVERLAY: return False
                p = p.parent
            return True
        for who in [s.a.get("data-persona")] + [f.get("persona") for f in meta.get("frames", []) if f.get("of") == sid and f.get("persona")]:
            prim = [n for n in s.walk() if n.a.get("data-atom") == "button" and n.a.get("data-variant") == "primary" and shown(n, who)]
            if len(prim) > 1: C(f"{sid} ({who}): {len(prim)} primary buttons visible at once; one per screen (the rest secondary)")
        personas = {s2.a.get("data-persona") for s2 in screens} | {f.get("persona") for f in meta.get("frames", []) if f.get("persona")}
        for n in s.walk():
            if "data-for" in n.a:
                if "data-when" in n.a: E(f"{sid}: an element has both data-for and data-when; nest one inside the other")
                for p in toks(n.a["data-for"]):
                    if p not in personas: E(f"{sid}: data-for '{p}' is not a persona of any screen or frame")
        nav = [n for n in s.walk() if n.a.get("data-component-type") == "nav"]
        for nv in nav:
            items = [n for n in nv.walk() if n.tag == "a"]
            if len(items) > 7: C(f"{sid}: navigation has {len(items)} items; seven or fewer")
        ro = (meta.get("screens", {}).get(sid) or {}).get("reading_order") or {}
        here = {n.a["data-instance-id"] for n in s.walk() if "data-instance-id" in n.a}
        for k in ("first", "next", "act"):
            if not ro.get(k): E(f"{sid}: reading_order has no '{k}' (wf-meta.screens.{sid}.reading_order)")
        for k, ids in ro.items():
            for x in ids if isinstance(ids, list) else [ids]:
                x = f"{sid}.{x[1:]}" if str(x).startswith("~") else x
                if x not in here: E(f"{sid}: reading_order.{k} names {x}, which is not an instance on this screen")
        for n in s.walk():
            if "wf-img" in n.a.get("class", "").split() and re.search(DOCS, n.text().lower()):
                E(f"{sid}: '{n.text()[:50]}' is a document drawn as a picture; draw the document (.wf-doc) with its real parts")
            if n.a.get("data-component-type") == "document" and not any(k.tag in ("table", "dl") for k in n.walk()):
                C(f"{n.a.get('data-instance-id')}: a document with no line items or fields; draw its anatomy (title and reference, parties, dates, lines, totals, status)")
    iids = [n.a["data-instance-id"] for n in insts]
    for i in set(x for x in iids if iids.count(x) > 1): E(f"instance id {i} used twice")
    used = set()
    states_of = {n.a["data-instance-id"]: (toks(n.a.get("data-states")) or ["default"]) for n in insts}
    on_screen = {}   # screen id -> {instance id: states}: interactions and frames resolve only inside their own screen
    for n in insts:
        sc_ = screen_of(n)
        if sc_ is not None: on_screen.setdefault(sc_.a["data-screen-id"], {})[n.a["data-instance-id"]] = states_of[n.a["data-instance-id"]]
    for n in insts:
        iid, cid = n.a["data-instance-id"], n.a.get("data-component-id", "")
        sc = screen_of(n)
        if not sc: E(f"{iid}: instance outside any screen")
        elif not iid.startswith(sc.a["data-screen-id"] + "."): E(f"{iid}: instance id must start with its screen id ({sc.a['data-screen-id']}.)")
        if cid not in reg: E(f"{iid}: component '{cid}' is not in wf-meta.components"); continue
        used.add(cid)
        if not n.a.get("data-component-type"): E(f"{iid}: no data-component-type")
        elif n.a["data-component-type"] not in TYPES: E(f"{iid}: type '{n.a['data-component-type']}' is not in the contract's list")
        elif reg[cid].get("type") and reg[cid]["type"] != n.a["data-component-type"]: E(f"{iid}: type {n.a['data-component-type']} but the registry says {reg[cid]['type']}")
        if not n.a.get("data-brd-ref"): E(f"{iid}: no data-brd-ref (trace it to the BRD, or to an override in brd_overrides)")
        v = n.a.get("data-variant")
        if v and v not in reg[cid].get("variants", {}): E(f"{iid}: variant '{v}' is not declared for {cid}")
        st = states_of[iid]
        if n.a.get("data-state", "default") not in st: E(f"{iid}: initial state '{n.a.get('data-state')}' not in data-states")
        for c in n.walk():
            if "data-when" in c.a and c.up(lambda p: "data-instance-id" in p.a) is n:
                for w in toks(c.a["data-when"]):
                    if w not in st: E(f"{iid}: data-when '{w}' is not one of its states {st}")
        if n.a.get("data-component-type") in OVERLAY and "closed" not in st: E(f"{iid}: an overlay needs a 'closed' state")
        if n.a.get("data-component-type") in ("drawer", "modal"):   # basic anatomy: header (title, close), body, footer (actions)
            kind = n.a["data-component-type"]
            mine = lambda k: k.up(lambda p: "data-instance-id" in p.a) is n
            heads = [k for k in n.walk() if k.tag == "header" and mine(k) and any(h.tag in ("h1", "h2", "h3", "h4") for h in k.walk())]
            if not heads: E(f"{iid}: the {kind} has no <header> holding its title")
            for k in n.walk():
                if k.tag != "button" or not mine(k): continue
                region = k.up(lambda p: p is n or (p.tag in ("header", "footer") and mine(p)))
                if (k.a.get("data-icon") == "close" or k.text().strip().lower() in ("close", "×", "✕")) and (region is None or region.tag != "header"):
                    C(f"{iid}: the close control sits outside the {kind}'s <header>")
                if k.a.get("data-variant") == "primary" and (region is None or region.tag != "footer"):
                    C(f"{iid}: '{k.text()[:30]}' sits in the {kind}'s body; put its actions in a <footer> after the content"); break
        txt = n.text()
        if len(re.sub(r"\W", "", txt)) < 3 and not any(k.tag in ("img", "svg", "input", "select", "textarea") or "wf-img" in k.a.get("class", "") for k in n.walk()):
            E(f"{iid}: the component shows no content")
        if n.a.get("data-component-type") == "card" and any(k is not n and k.a.get("data-component-type") == "card" for k in n.walk()):
            C(f"{iid}: a card inside a card; group with space and headings instead")
    for cid, r in reg.items():
        if cid not in used: E(f"component '{cid}' is in the registry but on no screen")
        for vname in r.get("variants", {}):
            if not any(n.a.get("data-component-id") == cid and n.a.get("data-variant") == vname for n in insts):
                C(f"{cid}: variant '{vname}' is declared but no instance uses it")
        for k in ("name", "type", "purpose"):
            if not r.get(k): E(f"component '{cid}' has no '{k}' in the registry")
    def target_ok(step, sid):
        """None when the step is valid on screen `sid`, else the reason. A target on another screen does not count."""
        verb, _, arg = step.partition(":"); arg = arg.strip()
        here = on_screen.get(sid, {})
        if verb in ("back", "wait", "submit") or (verb == "close" and not arg): return None
        if verb == "go": return None if arg in targets else f"'{arg}' is not a screen or frame"
        k, _, v = arg.partition("=") if verb == "state" else (arg, "", "")
        k, v = k.strip(), v.strip()
        if k.startswith("~"): k = f"{sid}.{k[1:]}"
        if verb not in ("open", "close", "toggle", "toast", "state"): return f"unknown step '{verb}'"
        if k not in here:
            where = [s for s, m in on_screen.items() if k in m]
            return f"missing target '{k}' on {sid}" + (f" (it exists only on {', '.join(where)}; interactions never reach another screen)" if where else "")
        if verb == "state": return None if v in here[k] else f"'{k}' has no state '{v}'"
        if verb != "close" and "open" not in here[k]: return f"'{k}' has no 'open' state"
        return None
    for n in nodes:
        if in_chrome(n): continue
        if "data-interaction" in n.a:
            sc_n = screen_of(n); sid_n = sc_n.a["data-screen-id"] if sc_n else ""
            for step in [x.strip() for x in n.a["data-interaction"].split(";") if x.strip()]:
                why = target_ok(step, sid_n)
                if why: E(f"{sid_n or '?'}: interaction '{step}' on <{n.tag}> '{(n.text() or n.a.get('aria-label', ''))[:30]}': {why}")
        if n.tag in ("button", "a") and screen_of(n):
            label = n.text() or n.a.get("aria-label", "")
            href = n.a.get("href", "")
            works = "data-interaction" in n.a or n.a.get("type") == "submit" or (href.startswith("#") and href[1:] in targets) or n.a.get("role") == "tab" and "data-interaction" in n.a
            off = "disabled" in n.a or n.a.get("aria-disabled") == "true"
            if off:
                rid = n.a.get("aria-describedby", "")
                if not rid or not any(m.a.get("id") == rid and m.text() for m in nodes): E(f"{screen_of(n).a['data-screen-id']}: disabled '{label}' has no visible reason (aria-describedby → the helper text)")
            elif not works: E(f"{screen_of(n).a['data-screen-id']}: '{label or n.tag}' does nothing (no data-interaction or #screen link)")
            if label.strip().lower() in ("submit", "ok", "click here", "go", "button", "yes", "no"): C(f"{screen_of(n).a['data-screen-id']}: vague label '{label}'; a verb and an object")
    for f in meta.get("frames", []):
        if f.get("of") not in sids: E(f"frame {f['id']}: 'of' {f.get('of')} is not a screen")
        if f.get("dir") not in (None, "rtl", "ltr"): E(f"frame {f['id']}: dir must be rtl or ltr")
        kinds = {(next((n for n in insts if n.a["data-instance-id"] == k), None) or Node("x", {}, None)).a.get("data-component-type") for k in (f.get("set") or {})}
        if kinds and kinds <= {"filter-bar", "tabs", "table", "list"} and kinds & {"filter-bar", "tabs"} and not f.get("persona") and not f.get("width"):
            C(f"frame {f['id']} only shows a filter or tab choice; that works in place on {f.get('of')}, so drop the frame")
        for k, v in (f.get("set") or {}).items():
            here = on_screen.get(f.get("of"), {})
            if k not in here: E(f"frame {f['id']}: sets {k}, which is not on its screen {f.get('of')}")
            elif v not in here[k]: E(f"frame {f['id']}: sets {k}={v}, a state it does not have")
    if len(fids) > 2 * len(sids) + 2: C(f"{len(fids)} frames for {len(sids)} screens; keep frames that change the layout, a persona's view or a workflow step")
    ids_all = targets | set(states_of)
    for r in meta.get("requirements", []):
        cov = r.get("covered_by") or []
        if not cov and r.get("status") not in ("open question", "out of scope", "not shown on screen"):
            E(f"requirement {r.get('ref')} ('{r.get('need', '')[:40]}') is covered by nothing and has no status")
        for x in cov:
            if x not in ids_all: E(f"requirement {r.get('ref')}: covered_by '{x}' is not a screen, frame or instance")
    if not meta.get("requirements"): E("wf-meta has no 'requirements' map (BRD requirement → screens, frames, instances)")
    for j in meta.get("journey", []):
        if j.get("frame") not in targets: E(f"journey step '{j.get('step', '')[:40]}' points at {j.get('frame')}, which is not a screen or frame")
    for k in ("payoff_frame",):
        if meta.get(k) and meta[k] not in targets: E(f"{k} {meta[k]} is not a screen or frame")
    ks = meta.get("key_screens") or {}
    for k in ("home", "main", "agent"):
        if not ks.get(k): E(f"wf-meta.key_screens has no '{k}' (the design system draws these three)")
        elif ks[k] not in targets: E(f"key_screens.{k} {ks[k]} is not a screen or frame")
    if len(screens) > 1 and ks.get("home") and ks.get("home") == ks.get("main"):
        E("key_screens.home and key_screens.main are the same screen; the design system draws three different views, so 'main' is the screen where the storyline's main work happens")
    fr_of = {f["id"]: f.get("of") for f in meta.get("frames", [])}
    if ks.get("agent") and ks.get("main") and fr_of.get(ks["agent"], ks["agent"]) != fr_of.get(ks["main"], ks["main"]):
        C(f"key_screens.agent {ks['agent']} is not a frame of the main screen {ks['main']}")
    sigc, home = (meta.get("signature") or {}).get("component"), ks.get("home")
    if sigc and home and len(screens) > 1:   # the home key screen shows the signature, as drawn in its frame's states
        hsid = fr_of.get(home, home); hset = next((f.get("set", {}) for f in meta.get("frames", []) if f["id"] == home), {})
        def seen(n):
            p = n
            while p is not None and p.a.get("data-screen-id") != hsid:
                if "hidden" in p.a and p.a.get("data-component-type") not in OVERLAY: return False
                if p.a.get("data-component-type") in OVERLAY and hset.get(p.a.get("data-instance-id"), p.a.get("data-state", "closed")) == "closed": return False
                if "data-when" in p.a:
                    o = p.up(lambda q: "data-instance-id" in q.a)
                    if o is not None and hset.get(o.a["data-instance-id"], o.a.get("data-state", "default")) not in toks(p.a["data-when"]): return False
                p = p.parent
            return True
        if not any(n.a.get("data-component-id") == sigc and (screen_of(n) or n).a.get("data-screen-id") == hsid and seen(n) for n in insts):
            C(f"the signature ({sigc}) is not visible on key_screens.home {home}; the home shows the signature, so point home at the screen or frame where it shows")
    own_cls = {}
    for s_ in screens:
        for n in s_.walk():
            for c in n.a.get("class", "").split():
                if not re.match(r"(wf-|l-|doc-)", c) and c not in ("num", "grand"): own_cls.setdefault(c, s_.a["data-screen-id"])
    if own_cls: C(f"classes outside the wf-, l- and doc- names: {', '.join(sorted(own_cls)[:10])}; name this app's own classes l-… so the design system's kit cannot restyle them")
    sig = meta.get("signature") or {}
    if sig and sig.get("frame") not in targets: E("signature.frame is not a screen or frame")
    if sig and sig.get("component") and sig["component"] not in reg: E("signature.component is not in the registry")
    comp_names = set(reg); sentences = {}
    for s in screens:
        sid = s.a["data-screen-id"]
        for n in s.walk():
            own = " ".join(k for k in n.kids if isinstance(k, str)).strip()
            if not own or n.tag in ("script", "style"): continue
            low = own.lower()
            if any(w in low for w in allow): continue
            if re.search(BANNED, low): E(f"{sid}: '{own[:50]}' uses a placeholder or demo word")
            if re.search(CODES, own): C(f"{sid}: '{own[:50]}' shows an internal BRD code; codes stay in metadata")
            if own.strip() in comp_names: E(f"{sid}: '{own}' is a component id shown as on-screen text")
            if re.search(FILLER, low): C(f"{sid}: filler word in '{own[:50]}'")
            if n.tag in ("h1", "h2", "h3", "h4") and low in GENERIC and low not in exact: C(f"{sid}: heading '{own}' says nothing; name what the block holds")
            if n.tag in ("p", "li", "span", "div", "td", "dd", "small"):
                for sen in re.split(r"(?<=[.!?])\s+", own):
                    w = len(sen.split())
                    if w > 25: C(f"{sid}: a {w}-word sentence ('{sen[:40]}…'); 25 words at most"); break
                if len(own.split()) >= 4: sentences.setdefault(sid, []).extend(len(x.split()) for x in re.split(r"(?<=[.!?])\s+", own) if x.strip())
            if own.count("·") >= 3: C(f"{sid}: '{own[:50]}' joins four or more facts with '·'; give them their own lines")
            if "!" in own and n.tag not in ("code", "pre"): C(f"{sid}: '{own[:50]}' has an exclamation mark; keep the tone calm and factual")
            if re.search(PRAISE, low): C(f"{sid}: praise word in '{own[:50]}'; use a concrete number or fact")
            if re.search(TELLS, low): C(f"{sid}: '{own[:50]}' uses a stock AI phrase (slogan, opener, closer, hedge or 'Oops')")
            if EMOJI.search(own): E(f"{sid}: emoji in '{own[:40]}'; use a labelled icon (data-icon) or words")
            if len(re.findall(r" [—–] ", own)) >= 2: C(f"{sid}: '{own[:50]}' has more than one dash aside; one per paragraph")
            if re.search(PATHS, own, re.I) and n.tag not in ("code", "pre"): C(f"{sid}: '{own[:50]}' shows how the output was made (a file name, path, run ID or error code)")
            if re.search(r"(?<![\d.])\d+\.\d{3,}(?![\d.])", own): C(f"{sid}: '{own[:50]}' shows false precision; round to what the decision needs")
    for sid, ws in sentences.items():
        if len(ws) >= 6 and sum(ws) / len(ws) > 20: C(f"{sid}: sentences average {sum(ws) / len(ws):.0f} words; aim for 15 to 20")
    # screens: the team's slop rules that a structure check can see
    taglines = {}
    for s in screens:
        sid = s.a["data-screen-id"]; ty = lambda n: n.a.get("data-component-type")
        metrics = [n for n in s.walk() if ty(n) == "metric"]
        if len(metrics) > 6: C(f"{sid}: {len(metrics)} metrics on one screen; six at most, each with a comparison and a time frame")
        for n in s.walk():
            if ty(n) in ("card", "record-header", "metric"):
                facts = [k for k in n.walk() if k.tag == "dt" and k.up(lambda q: "data-instance-id" in q.a) is n]
                if len(facts) > 4: C(f"{sid}: {n.a.get('data-instance-id')} shows {len(facts)} key facts; four at most, the rest behind Details")
                nums = re.findall(r"(?<![\w-])\d[\d,.]*%?(?![\w-])", n.text())
                if len(nums) > 8: C(f"{sid}: {n.a.get('data-instance-id')} packs {len(nums)} numbers onto one card; keep the few the decision needs")
            if ty(n) in ("card", "record-header", "metric") and n.up(lambda q: q.a.get("data-component-type") in ("card", "record-header", "metric") and q is not n) is not None:
                C(f"{sid}: {n.a.get('data-instance-id')} is a card inside a card; flatten it into its parent's sections")
            if ty(n) == "table":
                rows = [r for r in n.walk() if r.tag == "tr" and r.up(lambda q: q.tag == "tbody") is not None]
                tagged = [r for r in rows if any(k.a.get("data-atom") == "tag" for k in r.walk())]
                cols = {i for r in rows for i, c in enumerate([k for k in r.kids if not isinstance(k, str) and k.tag == "td"]) if any(x.a.get("data-atom") == "tag" for x in c.walk())}
                if len(cols) >= 3: C(f"{sid}: {n.a.get('data-instance-id')} has tags in {len(cols)} columns; colour only the exceptions")
                if len(rows) >= 4 and len(tagged) == len(rows) and len({" ".join(k.text() for k in r.walk() if k.a.get("data-atom") == "tag") for r in rows}) == 1:
                    C(f"{sid}: {n.a.get('data-instance-id')} puts the same tag on every row; colour only the exceptions")
                for i in range(12):
                    vals = [[k for k in r.kids if not isinstance(k, str) and k.tag == "td"] for r in rows]
                    vals = [v[i].text().strip() for v in vals if len(v) > i]
                    if len(vals) >= 4 and len(set(vals)) == 1 and vals[0] and not re.fullmatch(r"[-–—]|0|none|yes|no", vals[0], re.I):
                        C(f"{sid}: {n.a.get('data-instance-id')} repeats '{vals[0][:20]}' in every row of a column; use real, varied values"); break
            if n.a.get("data-icon") in ("sparkle", "sparkles", "ai", "magic"): taglines.setdefault(("ai", sid), []).append(n)
            if n.tag == "button" and n.a.get("data-icon") and not n.text().strip() and n.a.get("data-icon") not in ("close", "more"):
                C(f"{sid}: an icon button ({n.a['data-icon']}) has no text label; icons carry their word")
        if len(taglines.get(("ai", sid), [])) > 2: C(f"{sid}: {len(taglines[('ai', sid)])} AI sparkle marks; mark AI output once per panel")
        hdr = [n for n in s.walk() if ty(n) == "header" and any(k.tag == "h1" for k in n.walk())]   # the page header (the one with the title)
        sub = next((k.text().strip() for h in hdr for k in h.walk() if k.tag in ("p", "small") and k.text().strip()), "")
        if sub: taglines.setdefault(sub, []).append(sid)
        for h in hdr:
            acts = [k for k in h.walk() if k.a.get("data-atom") == "button" and k.a.get("data-variant") in ("primary", "secondary") and k.up(lambda q: "data-instance-id" in q.a) is h]
            if len(acts) > 3: C(f"{sid}: the page header holds {len(acts)} actions; one primary and at most two others, the rest in a menu")
    for k, v in taglines.items():
        if isinstance(k, str) and len(v) > 2: C(f"the same line '{k[:40]}' heads {len(v)} screens; give each screen its own")
    hs = fr_of.get(home, home) if home else None; inst_by = {n.a["data-instance-id"]: n for n in insts}
    first = ((meta.get("screens", {}).get(hs) or {}).get("reading_order") or {}).get("first") or []
    if first and all((inst_by.get(i) is not None and inst_by[i].a.get("data-component-type") == "metric") for i in first):
        C(f"key_screens.home {home} opens on number tiles; open on the person's next task")
    for x in err: print("error:", x)
    for x in chk: print("check:", x)
    print(f"{len(screens)} screens · {len(fids)} frames · {len(reg)} components · {len(insts)} instances · "
          f"{sum(1 for n in nodes if 'data-sample' in n.a)} sample-data marks · {len(err)} errors · {len(chk)} checks")
    sys.exit(1 if err else 0)

def browser(pw):
    import glob, shutil
    try: return pw.chromium.launch()
    except Exception as first:
        roots = [os.environ.get("PLAYWRIGHT_BROWSERS_PATH") or "", os.path.expanduser("~/Library/Caches/ms-playwright"), os.path.expanduser("~/.cache/ms-playwright")]
        cands = [os.environ.get("WF_CHROMIUM") or ""]
        for r in roots:
            if r and os.path.isdir(r):
                cands += sorted(glob.glob(os.path.join(r, "chromium*", "chrome-*", "Chromium.app", "Contents", "MacOS", "Chromium")) +
                                glob.glob(os.path.join(r, "chromium*", "chrome-linux*", "chrome")), reverse=True)
        cands += ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"] + [shutil.which(n) or "" for n in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable")]
        for exe in [c for c in cands if c and os.path.exists(c)]:
            try: return pw.chromium.launch(executable_path=exe)
            except Exception: continue
        raise RuntimeError(f"no Chromium could be started ({str(first).splitlines()[0]})")

def cli_shots(url, order, width, out):
    """No Python Playwright: drive an installed Chrome or Chromium from the command line (screenshots only)."""
    import shutil, subprocess
    exe = next((c for c in [os.environ.get("WF_CHROMIUM") or "", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Chromium.app/Contents/MacOS/Chromium"] + [shutil.which(n) or "" for n in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable")]
                if c and os.path.exists(c)), None)
    if not exe: return [], ["review screenshots skipped: no Python Playwright and no Chrome or Chromium on this machine; review each screen by eye in the browser"]
    shots = []
    for fid, sid, t, fw in order:
        w = fw or width[sid]; p = os.path.join(out, "png", f"{fid}.png")
        subprocess.run([exe, "--headless=new", "--hide-scrollbars", "--disable-gpu", f"--window-size={w},{812 if w < 600 else 900}",
                        "--virtual-time-budget=4000", f"--screenshot={os.path.abspath(p)}", f"{url}?export#{fid}"], capture_output=True, timeout=60)
        if not os.path.exists(p): return shots, [f"review: Chrome did not write {p}; review the rest by eye"]
        shots.append((fid, t, w, p))
    return shots, ["review used the Chrome command line: each frame is cut at the window height, and NAV-options/VIEWS sheets are not drawn"]

RO_JS = """({sid, ro}) => {
  const sc = document.querySelector(`.wf-screen[data-screen-id="${sid}"]`), dev = sc.querySelector('.wf-device').getBoundingClientRect(), out = {};
  for (const [k, ids] of Object.entries(ro)) {
    let r = null, font = 0;
    for (let id of [].concat(ids)) {
      if (id.startsWith('~')) id = sid + '.' + id.slice(1);
      const el = sc.querySelector(`[data-instance-id="${CSS.escape(id)}"]`); if (!el || el.closest('[hidden]')) continue;
      const b = el.getBoundingClientRect(); if (!b.width || !b.height) continue;
      r = r ? {l: Math.min(r.l, b.left), t: Math.min(r.t, b.top), r: Math.max(r.r, b.right), b: Math.max(r.b, b.bottom)} : {l: b.left, t: b.top, r: b.right, b: b.bottom};
      for (const x of [el, ...el.querySelectorAll('*')]) if (x.childNodes && [...x.childNodes].some(c => c.nodeType === 3 && c.nodeValue.trim())) font = Math.max(font, parseFloat(getComputedStyle(x).fontSize));
    }
    if (r) out[k] = {left: Math.round(r.l - dev.left), top: Math.round(r.t - dev.top), width: Math.round(r.r - r.l), height: Math.round(r.b - r.t), font};
  }
  return out;
}"""

OVERLAP_JS = r"""(sid) => {
  // text that overlaps other visible text on the rendered screen (map labels on markers, a label under a floating panel)
  const sc = document.querySelector(`.wf-screen[data-screen-id="${sid}"] .wf-device`), boxes = [], hits = [];
  const vis = el => { for (let n = el; n && n !== sc; n = n.parentElement) { if (n.hidden) return false; const cs = getComputedStyle(n); if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) return false; } return true; };
  const tw = document.createTreeWalker(sc, NodeFilter.SHOW_TEXT);
  for (let t; (t = tw.nextNode());) {
    if (!t.nodeValue.trim() || !vis(t.parentElement)) continue;
    const r = document.createRange(); r.selectNodeContents(t);
    for (const b of r.getClientRects()) if (b.width > 2 && b.height > 2) boxes.push({el: t.parentElement, txt: t.nodeValue.trim().slice(0, 28), l: b.left, t: b.top + scrollY, r: b.right, b: b.bottom + scrollY});
  }
  // a collision is two texts whose glyphs show through each other: the top element at the overlap is one of the two, and
  // nothing opaque sits between it and their common container (a drawer or a filled button over a label covers it instead)
  const opaque = (e, stop) => { for (let n = e; n && n !== stop; n = n.parentElement) { const m = getComputedStyle(n).backgroundColor.match(/rgba?\(([^)]+)\)/);
    if (m) { const p = m[1].split(',').map(Number); if (p.length < 4 || p[3] > .5) return true; } } return false; };
  const common = (x, y) => { let n = x; while (n && !n.contains(y)) n = n.parentElement; return n; };
  const top = (x, y, a, c) => { scrollTo(0, Math.max(0, y - innerHeight / 2)); const e = document.elementFromPoint(x, y - scrollY);
    if (!e || !(a.el.contains(e) || c.el.contains(e) || e.contains(a.el) || e.contains(c.el))) return false; return !opaque(e, common(a.el, c.el)); };
  for (let i = 0; i < boxes.length && hits.length < 6; i++) for (let j = i + 1; j < boxes.length && hits.length < 6; j++) {
    const a = boxes[i], c = boxes[j]; if (a.el === c.el || a.el.contains(c.el) || c.el.contains(a.el)) continue;
    const ox = Math.min(a.r, c.r) - Math.max(a.l, c.l), oy = Math.min(a.b, c.b) - Math.max(a.t, c.t);
    if (ox > 3 && oy > 3 && top((Math.max(a.l, c.l) + Math.min(a.r, c.r)) / 2, (Math.max(a.t, c.t) + Math.min(a.b, c.b)) / 2, a, c)) hits.push(`"${a.txt}" overlaps "${c.txt}"`);
  }
  scrollTo(0, 0); return hits;
}"""

def export(path, out):
    nodes, meta, html, screens, insts, atoms = collect(path)
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        Image = None
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sync_playwright = None
    slug = html.a.get("data-slug") or meta.get("slug") or "app"
    os.makedirs(os.path.join(out, "png"), exist_ok=True)
    width = {s.a["data-screen-id"]: int(s.a.get("data-width", "1280")) for s in screens}
    title = {s.a["data-screen-id"]: s.a.get("data-screen-title", "") for s in screens}
    order = []
    for sid in width:
        order.append((sid, sid, title[sid], None))
        order += [(f["id"], f["of"], f.get("title", ""), f.get("width")) for f in meta.get("frames", []) if f["of"] == sid]
    url = "file://" + os.path.abspath(path)
    shots, problems, ro_boxes = [], [], {}
    if sync_playwright is None:
        shots, problems = cli_shots(url, order, width, out)
    else:
     try:
      with sync_playwright() as pw:
          b = browser(pw)
          for fid, sid, t, fw in order:
              w = fw or width[sid]; pg = b.new_page(viewport={"width": w, "height": 812 if w < 600 else 800}, device_scale_factor=1)
              msgs = []; pg.on("pageerror", lambda e: msgs.append(str(e)))
              pg.goto(f"{url}?export#{fid}"); pg.wait_for_function("document.documentElement.dataset.ready==='1'", timeout=10000)
              if pg.evaluate("document.documentElement.dataset.current") != fid: problems.append(f"{fid}: the page did not open on this frame")
              el = pg.locator(f'.wf-screen[data-screen-id="{sid}"] .wf-device').first
              p = os.path.join(out, "png", f"{fid}.png"); el.screenshot(path=p)
              if fid == sid:
                  ro = (meta.get("screens", {}).get(sid) or {}).get("reading_order") or {}
                  boxes = pg.evaluate(RO_JS, {"sid": sid, "ro": ro})
                  vh = 812 if w < 600 else 800; ro_boxes[sid] = (p, boxes)
                  inside = lambda a, b: a and b and a["left"] >= b["left"] - 2 and a["top"] >= b["top"] - 2 and a["left"] + a["width"] <= b["left"] + b["width"] + 2 and a["top"] + a["height"] <= b["top"] + b["height"] + 2
                  f_, n_, a_, s_ = (boxes.get(k) for k in ("first", "next", "act", "support"))
                  if inside(f_, n_) or inside(n_, f_): n_ = None
                  if inside(f_, s_) or inside(s_, f_): s_ = None
                  if f_ and n_ and n_["top"] < f_["top"] - 8 and n_["left"] >= f_["left"]: problems.append(f"{sid}: 'next' sits above 'first'; the eye meets it first")
                  if f_ and f_["top"] > vh * 0.6: problems.append(f"{sid}: 'first' starts {f_['top']}px down; it should be the first thing in view")
                  if a_ and a_["top"] > vh: problems.append(f"{sid}: the action starts {a_['top']}px down, below the first view at {w}px")
                  if f_ and s_ and s_["top"] < f_["top"] - 8: problems.append(f"{sid}: supporting content sits above 'first'")
                  if f_ and s_ and s_["font"] > f_["font"]: problems.append(f"{sid}: supporting content uses larger type ({s_['font']}px) than 'first' ({f_['font']}px)")
                  for k in ("first", "next", "act"):
                      if ro.get(k) and not boxes.get(k): problems.append(f"{sid}: reading_order.{k} is not visible on the rendered screen")
              for h in pg.evaluate(OVERLAP_JS, sid): problems.append(f"{fid}: text overlaps on the rendered screen: {h}")
              hs = pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
              if hs > 2: problems.append(f"{fid}: {hs}px of sideways scroll at {w}px")
              problems += [f"{fid}: script error {m}" for m in msgs]; shots.append((fid, t, w, p)); pg.close()
          for sheet in ("NAV-options", "VIEWS"):
              if any(n.a.get("id") == sheet for n in nodes):
                  pg = b.new_page(viewport={"width": 1280, "height": 800}); pg.goto(f"{url}?export#{sid}")
                  pg.wait_for_function("document.documentElement.dataset.ready==='1'")
                  pg.evaluate(f"(()=>{{const s=document.getElementById('{sheet}');s.hidden=false;s.removeAttribute('data-wf-chrome');s.scrollIntoView()}})()")
                  pg.locator(f"#{sheet}").screenshot(path=os.path.join(out, "png", f"{sheet}.png")); pg.close()
          b.close()
     except Exception as e:
        shots, problems = cli_shots(url, order, width, out)
        problems.insert(0, f"Playwright could not run ({str(e).splitlines()[0][:120]}); used the Chrome command line")
    for x in problems: print("check:", x)
    if not shots or Image is None:
        print(f"{len(shots)} screens and frames captured in {out}/png" + ("" if Image else " (no Pillow: no overlays or contact sheets)"))
        return
    try: font = ImageFont.truetype("DejaVuSans.ttf", 12)
    except Exception: font = ImageFont.load_default()
    qa = out
    colours = {"first": "#d62728", "next": "#1f77b4", "act": "#2ca02c", "support": "#9467bd"}
    for sid, (p, boxes) in ro_boxes.items():
        im = Image.open(p).convert("RGB"); dr = ImageDraw.Draw(im)
        for i, k in enumerate(("first", "next", "act", "support"), 1):
            bx = boxes.get(k)
            if not bx: continue
            dr.rectangle([bx["left"], bx["top"], bx["left"] + bx["width"], bx["top"] + bx["height"]], outline=colours[k], width=3)
            dr.rectangle([bx["left"], bx["top"], bx["left"] + 74, bx["top"] + 18], fill=colours[k]); dr.text((bx["left"] + 4, bx["top"] + 3), f"{i} {k}", fill="white", font=font)
        im.save(os.path.join(qa, f"reading-order-{sid}.png"))
    thumbs = [(fid, t, Image.open(p).convert("RGB")) for fid, t, w, p in shots]
    for n in range(0, len(thumbs), 6):
        cells = []
        for fid, t, im in thumbs[n:n + 6]:
            s = 600 / max(im.width, 1); im2 = im.resize((600, max(1, int(im.height * s)))); im2 = im2.crop((0, 0, 600, min(520, im2.height)))
            cell = Image.new("RGB", (600, 548), "white"); cell.paste(im2, (0, 28)); ImageDraw.Draw(cell).text((8, 8), f"{fid} · {t}"[:90], fill="#222", font=font); cells.append(cell)
        sheet = Image.new("RGB", (3 * 610 + 10, ((len(cells) + 2) // 3) * 558 + 10), "#cfcfcf")
        for i, c in enumerate(cells): sheet.paste(c, (10 + (i % 3) * 610, 10 + (i // 3) * 558))
        sheet.save(os.path.join(qa, f"contact-sheet-{n // 6 + 1}.png"))
    if sync_playwright is None: print("check: reading order and overlapping text were not measured (no Playwright); check both by eye on each screen")
    print(f"{len(shots)} screens and frames → {out}/png, reading-order overlays and contact sheets in {out}")

def embed(path):
    """Put the skill's fixed stylesheet and runtime into the HTML, so they are never typed by hand."""
    a = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
    css, js = open(os.path.join(a, "wf-base.css")).read(), open(os.path.join(a, "wf-runtime.js")).read()
    s = open(path, encoding="utf-8").read()
    s, n1 = re.subn(r'(<style id="wf-base"[^>]*>).*?(</style>)', lambda m: m.group(1) + "\n" + css + m.group(2), s, flags=re.S)
    s, n2 = re.subn(r'(<script id="wf-runtime"[^>]*>).*?(</script>)', lambda m: m.group(1) + "\n" + js + m.group(2), s, flags=re.S)
    if not (n1 and n2):
        sys.exit('embed: the HTML needs <style id="wf-base"></style> in <head> and <script id="wf-runtime"></script> before </body>')
    open(path, "w", encoding="utf-8").write(s)
    print(f"embedded wf-base ({len(css)} chars) and wf-runtime ({len(js)} chars) into {path}")

if __name__ == "__main__":
    if len(sys.argv) < 3: sys.exit(__doc__)
    cmd, src = sys.argv[1], sys.argv[2]
    if cmd == "manifest" and len(sys.argv) == 4: manifest(src, sys.argv[3])
    elif cmd == "check": check(src)
    elif cmd in ("review", "export") and len(sys.argv) == 4: export(src, sys.argv[3])
    elif cmd == "embed": embed(src)
    else: sys.exit(__doc__)
