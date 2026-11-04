#!/usr/bin/env python3
"""POC Studio · wireframes: compare two wireframe versions for a change request after the build.

usage: diff.py <previous_dir> <current_dir> <out_dir> [--request "<the person's words>"]
  previous_dir  the approved version moved aside before the update (e.g. 02b-wireframes/_previous/v1/),
                holding its <slug>.wireframe.json, png/ and wireframe-manifest.json
  current_dir   the updated 02b-wireframes/ (re-rendered)
  out_dir       where the change sheet goes (e.g. 02b-wireframes/changes/CR-<n>/)

writes: <out_dir>/change-summary.json  pages added / removed / changed / metadata only / unchanged, app-level
                                       changes (the app block's keys and the spec-level keys: today, signature,
                                       nav_options, journey, payoff_frame, hero_object, brd_overrides, ...),
                                       the NAV-options and VIEWS sheets that differ, components added / removed /
                                       changed (variants, states, pages, features, modes, views, purpose, hero)
        <out_dir>/png/<page-id>.png    one before | after sheet per added, removed or changed page, and per
                                       NAV-options / VIEWS sheet that differs (labelled as a sheet, not a page)
        <out_dir>/change-sheet.pdf     those sheets only, in the current nav order (removed pages, then the
                                       NAV-options and VIEWS sheets, last)
A page whose only changes are its brief, pattern or shape and whose PNG is identical is "metadata only": listed,
but given no before | after sheet.
prints one line per changed page and the component changes, then the totals.
Exit code 0 always; "NO_CHANGES" is printed when the two versions draw the same frames.
"""
import glob, hashlib, json, os, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
INK, MUTED, BG, LINE = "#2f2f2d", "#8a8a85", "#ffffff", "#c4c4bf"
ADD, DEL, CHG = "#2e7d32", "#c62828", "#b26a00"


def font(size, bold=False):
    names = ["Inter-SemiBold.otf"] if bold else ["Inter-Regular.otf"]
    for n in names + ["DejaVuSans.ttf"]:
        for p in (os.path.join(HERE, "..", "assets", n), f"/usr/share/fonts/truetype/dejavu/{n}"):
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default(size)


def load(d):
    specs = [p for p in glob.glob(os.path.join(d, "*.wireframe.json"))]
    if not specs:
        sys.exit(f"no *.wireframe.json in {d}")
    spec = json.load(open(specs[0]))
    man_p = os.path.join(d, "wireframe-manifest.json")
    man = json.load(open(man_p)) if os.path.exists(man_p) else {"components": []}
    return spec, man


def canon(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False)


def png_hash(d, pid):
    p = os.path.join(d, "png", f"{pid}.png")
    return hashlib.sha1(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None


def page_fields_changed(a, b):
    keys = sorted(set(a) | set(b))
    return [k for k in keys if canon(a.get(k)) != canon(b.get(k))]


META = {"brief", "pattern", "shape"}  # what the build reads but the frame does not draw
SHEETS = {"NAV-options": "Navigation options (sheet, not a page)", "VIEWS": "Views (sheet, not a page)"}


def sheet(prev_dir, cur_dir, pid, title, status, out_png, fields):
    before = os.path.join(prev_dir, "png", f"{pid}.png")
    after = os.path.join(cur_dir, "png", f"{pid}.png")
    ims = [Image.open(before).convert("RGB") if status != "added" and os.path.exists(before) else None,
           Image.open(after).convert("RGB") if status != "removed" and os.path.exists(after) else None]
    ref = next(i for i in ims if i is not None)
    w, h = ref.size
    scale = min(1.0, 900 / w)
    tw, th = int(w * scale), int(h * scale)
    gap, head = 24, 92
    canvas = Image.new("RGB", (tw * 2 + gap * 3, th + head + gap), BG)
    d = ImageDraw.Draw(canvas)
    colour = {"added": ADD, "removed": DEL, "changed": CHG}[status]
    d.text((gap, 18), f"{pid} · {title}", font=font(22, True), fill=INK)
    d.text((gap, 50), status.upper() + ("  ·  " + ", ".join(fields) if fields else ""), font=font(14, True), fill=colour)
    for i, (im, label) in enumerate(zip(ims, ("Before (approved)", "After (proposed)"))):
        x = gap + i * (tw + gap)
        d.text((x, head - 22), label, font=font(13), fill=MUTED)
        if im is None:
            d.rectangle([x, head, x + tw, head + th], outline=LINE, width=2)
            d.text((x + tw / 2, head + th / 2), "not in this version", font=font(16), fill=MUTED, anchor="mm")
        else:
            canvas.paste(im.resize((tw, th)), (x, head))
            d.rectangle([x, head, x + tw, head + th], outline=colour if i == 1 or status == "removed" else LINE, width=3)
    canvas.save(out_png)
    return canvas


def components_diff(m_old, m_new):
    old = {c["component"]: c for c in m_old.get("components", [])}
    new = {c["component"]: c for c in m_new.get("components", [])}
    changed = []
    def names(xs):  # views are names or {"name", "kind", "group_by"}; purpose, variants, states are lists of strings
        out = set()
        for x in ([xs] if isinstance(xs, str) else xs or []):
            if isinstance(x, dict):
                out.add(str(x.get("name", "")) + (f" ({x['kind']}" + (f", by {x['group_by']}" if x.get("group_by") else "") + ")" if x.get("kind") else ""))
            else:
                out.add(str(x))
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


def main(prev_dir, cur_dir, out_dir, request=None):
    s_old, m_old = load(prev_dir)
    s_new, m_new = load(cur_dir)
    old = {p["id"]: p for p in s_old["pages"]}
    new = {p["id"]: p for p in s_new["pages"]}
    # app-level: the app block's own keys (shell, nav, agent, ...) as before, then every spec-level key that differs
    # (today, signature, nav_options, journey, payoff_frame, hero_object, brd_overrides, references, ...)
    app_keys = page_fields_changed(s_old.get("app", {}), s_new.get("app", {}))
    spec_keys = [k for k in page_fields_changed({k: v for k, v in s_old.items() if k != "pages"},
                                                {k: v for k, v in s_new.items() if k != "pages"})]
    app_changed = app_keys + [k for k in spec_keys if k != "app"]

    rows, meta_only = [], []
    for p in s_new["pages"]:
        pid = p["id"]
        if pid not in old:
            rows.append((pid, p["title"], "added", []))
            continue
        fields = page_fields_changed(old[pid], p)
        h_old, h_new = png_hash(prev_dir, pid), png_hash(cur_dir, pid)
        if fields and set(fields) <= META and h_old is not None and h_old == h_new:
            meta_only.append({"id": pid, "fields": fields})  # the build reads it, the frame is the same: no sheet
            continue
        if (not fields or set(fields) <= META) and h_old != h_new:  # the frame changed though nothing it draws did
            fields = fields + (["drawing (app-level change)"] if app_changed else ["drawing"])
        if fields:
            rows.append((pid, p["title"], "changed", fields))
    for pid, p in old.items():
        if pid not in new:
            rows.append((pid, p["title"], "removed", []))
    unchanged = [pid for pid in new if pid in old and pid not in {r[0] for r in rows} and pid not in {m["id"] for m in meta_only}]
    # the sheets the renderer draws beside the pages: the navigation options and the other views
    sheet_rows = []
    for sid, label in SHEETS.items():
        h_old, h_new = png_hash(prev_dir, sid), png_hash(cur_dir, sid)
        if h_old == h_new:
            continue
        st = "added" if h_old is None else "removed" if h_new is None else "changed"
        sheet_rows.append((sid, label, st, ["sheet"]))
    c_add, c_del, c_chg = components_diff(m_old, m_new)

    os.makedirs(os.path.join(out_dir, "png"), exist_ok=True)
    sheets = [sheet(prev_dir, cur_dir, pid, t, st, os.path.join(out_dir, "png", f"{pid}.png"), f)
              for pid, t, st, f in rows + sheet_rows]
    if sheets:
        sheets[0].save(os.path.join(out_dir, "change-sheet.pdf"), save_all=True, append_images=sheets[1:], resolution=110)

    summary = {
        "request": request,
        "previous": os.path.abspath(prev_dir), "current": os.path.abspath(cur_dir),
        "app_level_changes": app_changed,
        "spec_level_changes": spec_keys,
        "pages": {"added": [r[0] for r in rows if r[2] == "added"],
                  "removed": [r[0] for r in rows if r[2] == "removed"],
                  "changed": [{"id": r[0], "fields": r[3]} for r in rows if r[2] == "changed"],
                  "metadata_only": meta_only,
                  "unchanged": unchanged},
        "sheets": {st: [r[0] for r in sheet_rows if r[2] == st] for st in ("added", "removed", "changed")},
        "components": {"added": c_add, "removed": c_del, "changed": c_chg},
        "sheet": os.path.join(os.path.abspath(out_dir), "change-sheet.pdf") if sheets else None,
    }
    json.dump(summary, open(os.path.join(out_dir, "change-summary.json"), "w"), indent=2, ensure_ascii=False)

    if not rows and not sheet_rows and not meta_only and not app_changed and not c_add and not c_del and not c_chg:
        print("NO_CHANGES")
        return
    if app_keys:
        print(f"app-level: app {', '.join(app_keys)} (nav or shell: every page may be affected)")
    if [k for k in spec_keys if k != "app"]:
        print(f"app-level: {', '.join(k for k in spec_keys if k != 'app')} (spec-level, not a page)")
    for pid, t, st, f in rows:
        print(f"{st:8} {pid} · {t}" + (f"  [{', '.join(f)}]" if f else ""))
    for m in meta_only:
        print(f"metadata {m['id']} · {new[m['id']]['title']}  [{', '.join(m['fields'])}] (frame unchanged: no sheet)")
    for sid, t, st, f in sheet_rows:
        print(f"{st:8} sheet {sid} · {t}")
    for n in c_add:
        print(f"component added   {n}  (not in the design system: styled from its kit and tokens)")
    for n in c_del:
        print(f"component removed {n}")
    for c in c_chg:
        print(f"component changed {c['component']}  " + "; ".join(
            f"{k} {v['from']} -> {v['to']}" if k == "hero" else f"{k} +{v['added']} -{v['removed']}" for k, v in c.items() if k != "component"))
    print(f"{len(rows)} page(s) differ, {len(meta_only)} metadata only, {len(sheet_rows)} sheet(s) differ, {len(unchanged)} unchanged"
          + (f" → {out_dir}/change-sheet.pdf" if sheets else " (no change sheet: nothing drawn differs)"))


if __name__ == "__main__":
    a = sys.argv[1:]
    req = None
    if "--request" in a:
        i = a.index("--request"); req = a[i + 1]; a = a[:i] + a[i + 2:]
    if len(a) != 3:
        sys.exit(__doc__)
    main(a[0], a[1], a[2], req)
