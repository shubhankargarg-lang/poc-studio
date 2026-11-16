#!/usr/bin/env python3
"""POC Studio · wireframes: compare two wireframe HTML versions for a change request after the build.

usage: diff.py <previous_dir> <current_dir> <out_dir> [--request "<the person's words>"]
  previous_dir  the approved version moved aside before the update (e.g. 02b-wireframes/_previous/v1/), holding its
                <slug>-wireframes.html
  current_dir   the updated 02b-wireframes/
  out_dir       where the change sheet goes (e.g. 02b-wireframes/changes/CR-<n>/)

writes: <out_dir>/change-summary.json  screens added / removed / changed / metadata only / unchanged, app-level changes
                                       (app block, today, signature, nav_options, journey, payoff_frame, hero_object,
                                       brd_overrides, frames, ...), components added / removed / changed
        <out_dir>/change-sheet.html    one self-contained, clickable page: the request, the summary, and for every added,
                                       removed or changed screen the version before and after side by side (each a live
                                       copy of that wireframe opened on that screen)
A screen whose only changes are its brief, pattern or shape and whose drawn content is identical is "metadata only":
listed, with no before | after.
Prints one line per changed screen and the component changes, then the totals. Exit 0 always; "NO_CHANGES" when the two
versions draw the same screens. A previous version with no HTML (made before wireframes were HTML) must be converted
first (wireframes SKILL.md, "Legacy wireframes"); then this compares the converted copy with the change.
"""
import glob, html, json, os, re, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wf_tool  # noqa: E402

META = {"brief", "pattern", "shape"}


def find_html(d):
    hs = sorted(glob.glob(os.path.join(d, "*-wireframes.html")))
    if not hs:
        sys.exit(f"no *-wireframes.html in {d}: a legacy (image) wireframe must be converted to HTML first "
                 f"(wireframes SKILL.md, 'Legacy wireframes')")
    return hs[0]


def load(d):
    h = find_html(d)
    t = tempfile.mkdtemp()
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()):
        wf_tool.manifest(h, t)
    man = json.load(open(os.path.join(t, "wireframe-manifest.json")))
    idx = json.load(open(glob.glob(os.path.join(t, "*.wireframe.json"))[0]))
    return h, idx, man


def canon(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False)


def fields_changed(a, b):
    keys = sorted(set(a) | set(b))
    return [k for k in keys if k not in ("content_hash",) and canon(a.get(k)) != canon(b.get(k))]


def components_diff(m_old, m_new):
    old = {c["component"]: c for c in m_old.get("components", [])}
    new = {c["component"]: c for c in m_new.get("components", [])}
    changed = []

    def names(xs):
        out = set()
        for x in ([xs] if isinstance(xs, str) else xs or []):
            out.add(json.dumps(x, sort_keys=True) if isinstance(x, dict) else str(x))
        return out
    for n in sorted(set(old) & set(new)):
        delta = {}
        for k in ("variants", "states", "pages", "features", "modes", "views", "purpose"):
            a, b = names(old[n].get(k)), names(new[n].get(k))
            if a != b:
                delta[k] = {"added": sorted(b - a), "removed": sorted(a - b)}
        if bool(old[n].get("hero")) != bool(new[n].get("hero")):
            delta["hero"] = {"from": bool(old[n].get("hero")), "to": bool(new[n].get("hero"))}
        if delta:
            changed.append({"component": n, **delta})
    return sorted(set(new) - set(old)), sorted(set(old) - set(new)), changed


def opened_on(doc, sid):
    """A copy of the wireframe that opens on screen sid, with the review bar hidden."""
    m = re.search(r'(<script[^>]*id="wf-meta"[^>]*>)(.*?)(</script>)', doc, re.S)
    if m:
        try:
            meta = json.loads(m.group(2)); meta["start"] = sid
            doc = doc[:m.start(2)] + json.dumps(meta, ensure_ascii=False) + doc[m.end(2):]
        except ValueError:
            pass
    return doc.replace("</head>", "<style>.wf-review{display:none!important}</style></head>", 1)


def main(prev_dir, cur_dir, out_dir, request=None):
    h_old, i_old, m_old = load(prev_dir)
    h_new, i_new, m_new = load(cur_dir)
    old = {p["id"]: p for p in i_old["pages"] if "frame_of" not in p}
    new = {p["id"]: p for p in i_new["pages"] if "frame_of" not in p}
    app_keys = fields_changed(i_old.get("app", {}), i_new.get("app", {}))
    spec_keys = fields_changed({k: v for k, v in i_old.items() if k not in ("pages", "source")},
                               {k: v for k, v in i_new.items() if k not in ("pages", "source")})
    app_changed = app_keys + [k for k in spec_keys if k != "app"]
    rows, meta_only = [], []
    for pid, p in new.items():
        if pid not in old:
            rows.append((pid, p["title"], "added", []))
            continue
        f = fields_changed(old[pid], p)
        drawn = old[pid].get("content_hash") != p.get("content_hash")
        if f and set(f) <= META and not drawn:
            meta_only.append({"id": pid, "fields": f})
            continue
        if drawn and "drawing" not in f:
            f = f + ["drawing"]
        if f:
            rows.append((pid, p["title"], "changed", f))
    for pid, p in old.items():
        if pid not in new:
            rows.append((pid, p["title"], "removed", []))
    done = {r[0] for r in rows} | {m["id"] for m in meta_only}
    unchanged = [pid for pid in new if pid in old and pid not in done]
    c_add, c_del, c_chg = components_diff(m_old, m_new)

    os.makedirs(out_dir, exist_ok=True)
    sheet = None
    if rows or app_changed or c_add or c_del or c_chg:
        d_old, d_new = open(h_old, encoding="utf-8").read(), open(h_new, encoding="utf-8").read()
        e = html.escape
        width = {**{k: v.get("width") or 1280 for k, v in old.items()}, **{k: v.get("width") or 1280 for k, v in new.items()}}
        def frame(doc, sid, label):
            w = int(width.get(sid) or 1280); sc = 1 if w <= 640 else round(640 / w, 3)
            return (f'<figure><figcaption>{e(label)} <small>({w}px, shown at {int(sc * 100)}%)</small></figcaption>'
                    f'<div class="vp" style="height:{int(900 * sc)}px"><iframe loading="lazy" style="width:{w}px;height:900px;transform:scale({sc})" '
                    f'srcdoc="{e(opened_on(doc, sid), quote=True)}"></iframe></div></figure>')
        parts = []
        for pid, t, st, f in rows:
            cols = ([frame(d_old, pid, "Before")] if st != "added" else ['<figure class="none"><figcaption>Before</figcaption><p>New screen</p></figure>']) + \
                   ([frame(d_new, pid, "After")] if st != "removed" else ['<figure class="none"><figcaption>After</figcaption><p>Removed</p></figure>'])
            parts.append(f'<section><h2><span class="st {st}">{st}</span> {e(pid)} · {e(t)}</h2>'
                         + (f'<p class="f">{e(", ".join(f))}</p>' if f else "") + f'<div class="pair">{"".join(cols)}</div></section>')
        li = lambda xs: "".join(f"<li>{e(str(x))}</li>" for x in xs) or "<li>none</li>"
        page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wireframe change sheet</title><style>
body{{font:14px/1.5 system-ui,-apple-system,Segoe UI,sans-serif;margin:0;padding:24px;background:#f3f3f1;color:#222}}
h1{{font-size:20px;margin:0 0 4px}} h2{{font-size:16px;margin:28px 0 6px}} .req{{background:#fff;border:1px solid #ccc;padding:10px 14px;border-radius:6px}}
.st{{font-size:12px;text-transform:uppercase;padding:2px 6px;border-radius:4px;color:#fff;margin-right:6px}} .added{{background:#2e7d32}} .removed{{background:#c62828}} .changed{{background:#b26a00}}
.f{{color:#666;margin:0 0 8px}} .pair{{display:grid;grid-template-columns:repeat(2,minmax(0,660px));gap:12px}} figure{{margin:0;background:#fff;border:1px solid #ccc;border-radius:6px;overflow:hidden}}
figcaption{{font-weight:600;padding:6px 10px;border-bottom:1px solid #ddd}} .vp{{overflow:hidden}} iframe{{border:0;display:block;transform-origin:0 0}} small{{font-weight:400;color:#777}} .none p{{padding:24px;color:#777}}
ul{{margin:4px 0 0}}</style></head><body>
<h1>Wireframe change sheet</h1><p class="req"><b>Request:</b> {e(request or "-")}</p>
<p>{len(rows)} screen(s) differ, {len(meta_only)} metadata only, {len(unchanged)} unchanged.</p>
<h2>App-level changes</h2><ul>{li(app_changed)}</ul>
<h2>Components</h2><ul>{li(["added: " + x for x in c_add] + ["removed: " + x for x in c_del] + ["changed: " + c["component"] for c in c_chg])}</ul>
{"".join(parts)}</body></html>"""
        sheet = os.path.join(out_dir, "change-sheet.html")
        open(sheet, "w", encoding="utf-8").write(page)

    summary = {
        "request": request, "previous": os.path.abspath(h_old), "current": os.path.abspath(h_new),
        "app_level_changes": app_changed, "spec_level_changes": spec_keys,
        "pages": {"added": [r[0] for r in rows if r[2] == "added"], "removed": [r[0] for r in rows if r[2] == "removed"],
                  "changed": [{"id": r[0], "fields": r[3]} for r in rows if r[2] == "changed"],
                  "metadata_only": meta_only, "unchanged": unchanged},
        "components": {"added": c_add, "removed": c_del, "changed": c_chg},
        "sheet": os.path.abspath(sheet) if sheet else None,
    }
    json.dump(summary, open(os.path.join(out_dir, "change-summary.json"), "w"), indent=2, ensure_ascii=False)
    if not rows and not meta_only and not app_changed and not c_add and not c_del and not c_chg:
        print("NO_CHANGES")
        return
    if app_changed:
        print(f"app-level: {', '.join(app_changed)}")
    for pid, t, st, f in rows:
        print(f"{st:8} {pid} · {t}" + (f"  [{', '.join(f)}]" if f else ""))
    for m in meta_only:
        print(f"metadata {m['id']} · {new[m['id']]['title']}  [{', '.join(m['fields'])}] (drawing unchanged)")
    for n in c_add:
        print(f"component added   {n}  (not in the design system: styled from its kit and tokens)")
    for n in c_del:
        print(f"component removed {n}")
    for c in c_chg:
        print(f"component changed {c['component']}  " + "; ".join(
            f"{k} {v['from']} -> {v['to']}" if k == "hero" else f"{k} +{v['added']} -{v['removed']}" for k, v in c.items() if k != "component"))
    print(f"{len(rows)} screen(s) differ, {len(meta_only)} metadata only, {len(unchanged)} unchanged"
          + (f" → {sheet}" if sheet else ""))


if __name__ == "__main__":
    a = sys.argv[1:]
    req = None
    if "--request" in a:
        i = a.index("--request"); req = a[i + 1]; a = a[:i] + a[i + 2:]
    if len(a) != 3:
        sys.exit(__doc__)
    main(a[0], a[1], a[2], req)
