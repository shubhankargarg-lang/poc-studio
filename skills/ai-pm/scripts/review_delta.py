#!/usr/bin/env python3
"""review_delta.py — what changed since the AI PM's last review of a stage, so a later review reads only that.

The first review of a stage reads everything. Every later review (round 2 and 3 after a REVISE, the review after a
change the person asked for at a gate, the review after a change after the build) reads only what changed since the
last review, plus what depends on it. This script works that out.

usage:
  review_delta.py snapshot <workspace> <stage> <round> <artifact> [<artifact> ...]
      run at the end of every review: records each artifact split into sections (text and hashes) in
      <workspace>/reviews/_snapshots/<stage>-latest.json (and a copy as <stage>-r<round>-<time>.json)
  review_delta.py diff <workspace> <stage> <round> <artifact> [<artifact> ...]
      run at the start of every later review: compares the artifacts with <stage>-latest.json and writes
      <workspace>/reviews/<stage>-delta-<round>.json   the changed / added / removed sections per file, the share changed,
                                                       CSS custom properties that changed, and the recommendation
      <workspace>/reviews/<stage>-delta-<round>.md     a short before/after of each changed section (what to read)
      prints the summary and a last line: SCOPE delta | SCOPE full (<reason>)

Artifacts can be files (.docx .md .txt .html .json .pptx .pdf, images, anything else) or folders (each file inside is
one section, compared by hash). URLs are skipped (the build walk decides its own scope from the fix lines).
Full review is recommended when there is no earlier snapshot, when more than FULL_SHARE of the text changed, or when
a file's sections cannot be matched (it was rebuilt rather than fixed).
"""
import datetime, difflib, glob, hashlib, json, os, re, sys
from html.parser import HTMLParser

FULL_SHARE = 0.40       # above this share of changed text, read the whole artifact again
DIFF_LINES = 60         # cap of before/after lines shown per changed section in the .md report


def h(b):
    return hashlib.sha1(b if isinstance(b, bytes) else b.encode("utf-8", "replace")).hexdigest()[:16]


def norm(t):
    return re.sub(r"[ \t]+", " ", re.sub(r"\n\s*\n+", "\n", t or "")).strip()


# ---------- splitting each kind of file into named sections: [(name, text)] ----------
def split_md(path):
    out, name, buf = [], "(top)", []
    for line in open(path, encoding="utf-8", errors="replace"):
        m = re.match(r"^(#{1,3})\s+(.*)", line)
        if m:
            out.append((name, "".join(buf))); name, buf = m.group(2).strip(), []
        buf.append(line)
    out.append((name, "".join(buf)))
    return out


def split_docx(path):
    from docx import Document
    from docx.table import Table
    from docx.text.paragraph import Paragraph
    doc = Document(path)
    out, h1, name, buf = [], "", "(top)", []
    for el in doc.element.body.iterchildren():
        if el.tag.endswith("}p"):
            p = Paragraph(el, doc)
            s = p.style.name if p.style is not None else ""
            if s in ("Heading 1", "Heading 2", "Title"):
                out.append((name, "\n".join(buf)))
                if s == "Heading 1":
                    h1 = p.text.strip(); name = h1
                elif s == "Heading 2":
                    name = f"{h1} › {p.text.strip()}"
                else:
                    name = p.text.strip()
                buf = []
            buf.append(p.text)
        elif el.tag.endswith("}tbl"):
            t = Table(el, doc)
            buf.extend(" | ".join(c.text.strip() for c in r.cells) for r in t.rows)
    out.append((name, "\n".join(buf)))
    return out


class _HTML(HTMLParser):
    """Sections start at h1-h3 and at any <section>/<article> with an id. <style> and <script> are their own sections;
    CSS custom properties are collected so a token change can be traced to the sections that use it."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.name, self.buf, self.stack = [], "(top)", [], []
        self.in_head, self.head_txt, self.mode, self.style, self.script = None, "", None, [], []
        self.var_use = {}      # section name -> set of var(--x) used inline

    def _cut(self, name):
        self.out.append((self.name, "".join(self.buf))); self.name, self.buf = name, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("style", "script"):
            self.mode = tag; return
        if tag in ("h1", "h2", "h3"):
            self.in_head, self.head_txt = tag, ""
        elif tag in ("section", "article") and a.get("id"):
            self._cut(f"#{a['id']}")
        for k, v in a.items():
            if v and "var(--" in v:
                self.var_use.setdefault(self.name, set()).update(re.findall(r"var\((--[\w-]+)", v))
            if k == "class" and v:
                self.buf.append(f"[.{v}]")

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self.mode = None; return
        if self.in_head == tag:
            t = self.head_txt.strip()[:90] or tag
            self._cut(t); self.buf.append(t + "\n"); self.in_head = None

    def handle_data(self, d):
        if self.mode == "style":
            self.style.append(d); return
        if self.mode == "script":
            self.script.append(d); return
        if self.in_head:
            self.head_txt += d
        self.buf.append(d)


def css_vars(css):
    return {m.group(1): m.group(2).strip() for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;}{]+)", css)}


def split_html(path):
    p = _HTML(); p.feed(open(path, encoding="utf-8", errors="replace").read()); p._cut("(end)")
    secs = [(n, t) for n, t in p.out if norm(t)]
    css = "".join(p.style)
    secs.append(("<style>", css)); secs.append(("<script>", "".join(p.script)))
    # which section uses which var, from classes is unknowable without a renderer; inline uses are recorded
    extra = {"css_vars": css_vars(css), "var_use": {k: sorted(v) for k, v in p.var_use.items()}}
    return secs, extra


def split_pptx(path):
    from pptx import Presentation
    out = []
    for i, s in enumerate(Presentation(path).slides, 1):
        txt, pics = [], []
        for sh in s.shapes:
            if sh.has_text_frame:
                txt.append(sh.text_frame.text)
            if sh.shape_type == 13:
                try: pics.append(h(sh.image.blob))
                except Exception: pass
        title = next((t for t in txt if t.strip()), "")[:60]
        out.append((f"slide {i}: {title}", "\n".join(txt) + ("\n[images " + ",".join(pics) + "]" if pics else "")))
    return out


def split_pdf(path):
    try:
        from pypdf import PdfReader
        return [(f"page {i}", p.extract_text() or "") for i, p in enumerate(PdfReader(path).pages, 1)]
    except Exception:
        return [("(file)", h(open(path, "rb").read()))]


def split_json(path):
    d = json.load(open(path, encoding="utf-8"))
    out = []
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, list) and v and all(isinstance(x, dict) and ("id" in x or "name" in x) for x in v):
                for x in v:
                    out.append((f"{k}[{x.get('id', x.get('name'))}]", json.dumps(x, indent=1, sort_keys=True, ensure_ascii=False)))
            else:
                out.append((k, json.dumps(v, indent=1, sort_keys=True, ensure_ascii=False)))
    else:
        out.append(("(root)", json.dumps(d, indent=1, sort_keys=True, ensure_ascii=False)))
    return out


def split_dir(path):
    out = []
    for f in sorted(glob.glob(os.path.join(path, "**", "*"), recursive=True)):
        if os.path.isfile(f) and "/_previous/" not in f:
            out.append((os.path.relpath(f, path), "hash " + h(open(f, "rb").read())))
    return out


def sections(path):
    """-> (kind, [(name, text)], extra)"""
    if os.path.isdir(path):
        return "folder", split_dir(path), {}
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext in (".md", ".txt", ".yaml", ".yml"):
            return "text", split_md(path), {}
        if ext == ".docx":
            return "docx", split_docx(path), {}
        if ext in (".html", ".htm"):
            s, extra = split_html(path); return "html", s, extra
        if ext == ".pptx":
            return "pptx", split_pptx(path), {}
        if ext == ".pdf":
            return "pdf", split_pdf(path), {}
        if ext == ".json":
            return "json", split_json(path), {}
    except Exception as e:  # unreadable as its kind: compare the whole file
        return "file", [("(file)", "hash " + h(open(path, "rb").read()))], {"error": str(e)}
    return "file", [("(file)", "hash " + h(open(path, "rb").read()))], {}


def unique(secs):
    seen, out = {}, []
    for n, t in secs:
        seen[n] = seen.get(n, 0) + 1
        out.append((n if seen[n] == 1 else f"{n} ({seen[n]})", t))
    return out


def record(path, ws):
    kind, secs, extra = sections(path)
    secs = unique(secs)
    rel = os.path.relpath(os.path.abspath(path), os.path.abspath(ws))
    return rel, {"kind": kind, "file_hash": None if os.path.isdir(path) else h(open(path, "rb").read()),
                 "sections": [{"name": n, "hash": h(norm(t)), "len": len(norm(t)), "text": t[:20000]} for n, t in secs],
                 **extra}


def artifacts(ws, items):
    out = []
    for a in items:
        if re.match(r"https?://", a):
            continue
        p = a if os.path.isabs(a) else os.path.join(ws, a)
        if os.path.exists(p):
            out.append(p)
        else:
            print(f"skip (not found): {a}")
    return out


def snapshot(ws, stage, rnd, items):
    d = os.path.join(ws, "reviews", "_snapshots"); os.makedirs(d, exist_ok=True)
    snap = {"stage": stage, "round": rnd, "at": datetime.datetime.now().isoformat(timespec="seconds"),
            "files": dict(record(p, ws) for p in artifacts(ws, items))}
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    for name in (f"{stage}-latest.json", f"{stage}-r{rnd}-{stamp}.json"):
        json.dump(snap, open(os.path.join(d, name), "w"), ensure_ascii=False)
    n = sum(len(f["sections"]) for f in snap["files"].values())
    print(f"snapshot {stage} r{rnd}: {len(snap['files'])} file(s), {n} section(s) → reviews/_snapshots/{stage}-latest.json")


def diff(ws, stage, rnd, items):
    base_p = os.path.join(ws, "reviews", "_snapshots", f"{stage}-latest.json")
    os.makedirs(os.path.join(ws, "reviews"), exist_ok=True)
    out_json = os.path.join(ws, "reviews", f"{stage}-delta-{rnd}.json")
    out_md = os.path.join(ws, "reviews", f"{stage}-delta-{rnd}.md")
    if not os.path.exists(base_p):
        rep = {"stage": stage, "round": rnd, "scope": "full", "reason": "no earlier snapshot of this stage"}
        json.dump(rep, open(out_json, "w"), indent=2)
        print("SCOPE full (no earlier snapshot of this stage)"); return
    base = json.load(open(base_p))
    files, md = [], [f"# What changed since the last review — {stage}, round {rnd}", "",
                     f"Compared with the review of {base['at']} (round {base['round']}).", ""]
    tot_len = chg_len = 0
    full_reasons = []
    cur = dict(record(p, ws) for p in artifacts(ws, items))
    for rel in sorted(set(cur) | set(base["files"])):
        a, b = base["files"].get(rel), cur.get(rel)
        if b is None:
            files.append({"path": rel, "status": "removed"}); md.append(f"## {rel} — removed\n"); continue
        if a is None:
            files.append({"path": rel, "status": "added"}); md.append(f"## {rel} — new file: read it whole\n")
            tot_len += sum(s["len"] for s in b["sections"]); chg_len += sum(s["len"] for s in b["sections"]); continue
        if a.get("file_hash") and a["file_hash"] == b.get("file_hash"):
            files.append({"path": rel, "status": "unchanged"}); tot_len += sum(s["len"] for s in b["sections"]); continue
        old = {s["name"]: s for s in a["sections"]}; new = {s["name"]: s for s in b["sections"]}
        changed = [n for n in new if n in old and old[n]["hash"] != new[n]["hash"]]
        added = [n for n in new if n not in old]; removed = [n for n in old if n not in new]
        flen = sum(s["len"] for s in b["sections"]) or 1
        clen = sum(new[n]["len"] for n in changed + added) + sum(old[n]["len"] for n in removed)
        tot_len += flen; chg_len += clen
        matched = len([n for n in new if n in old]) / max(len(new), 1)
        entry = {"path": rel, "status": "changed", "kind": b["kind"], "changed": changed, "added": added,
                 "removed": removed, "unchanged": len(new) - len(changed) - len(added), "share": round(clen / flen, 3)}
        if b["kind"] == "html":
            ov, nv = a.get("css_vars", {}), b.get("css_vars", {})
            vchg = sorted(k for k in set(ov) | set(nv) if ov.get(k) != nv.get(k))
            entry["css_vars_changed"] = vchg
            if vchg:
                users = sorted(n for n, vs in b.get("var_use", {}).items() if set(vs) & set(vchg))
                entry["sections_using_changed_vars"] = users
        if matched < 0.5 and len(new) > 3:
            full_reasons.append(f"{rel}: most sections renamed or rebuilt")
        files.append(entry)
        md.append(f"## {rel} — {len(changed)} changed, {len(added)} added, {len(removed)} removed, "
                  f"{entry['unchanged']} unchanged ({entry['share']:.0%} of its text)")
        if entry.get("css_vars_changed"):
            md.append(f"CSS custom properties changed: {', '.join(entry['css_vars_changed'])}. Check every section that uses "
                      f"them (search the file for each name); inline uses found in: "
                      f"{', '.join(entry.get('sections_using_changed_vars') or ['none inline'])}.")
        md.append("")
        for n in changed:
            dl = list(difflib.unified_diff(old[n]["text"].splitlines(), new[n]["text"].splitlines(), "before", "after", n=1, lineterm=""))[2:]
            md.append(f"### {n} (changed)"); md.append("```diff")
            md.extend(l if len(l) <= 400 else l[:400] + " …" for l in dl[:DIFF_LINES]); md.append("... (more; read this section in the file)" if len(dl) > DIFF_LINES else "")
            md.append("```")
        for n in added:
            md.append(f"### {n} (added: read it whole)")
        for n in removed:
            md.append(f"### {n} (removed)")
        md.append("")
    share = chg_len / tot_len if tot_len else 0
    if share > FULL_SHARE:
        full_reasons.append(f"{share:.0%} of the text changed (over {FULL_SHARE:.0%})")
    scope = "full" if full_reasons else "delta"
    rep = {"stage": stage, "round": rnd, "base": base_p, "base_round": base["round"], "share_changed": round(share, 3),
           "scope": scope, "reason": "; ".join(full_reasons) or "changes are local", "files": files}
    json.dump(rep, open(out_json, "w"), indent=2, ensure_ascii=False)
    open(out_md, "w").write("\n".join(md))
    for f in files:
        if f["status"] == "changed":
            print(f"{f['path']}: {len(f['changed'])} changed, {len(f['added'])} added, {len(f['removed'])} removed, {f['unchanged']} unchanged")
        else:
            print(f"{f['path']}: {f['status']}")
    print(f"share changed {share:.0%} → reviews/{stage}-delta-{rnd}.md")
    print("SCOPE " + (f"full ({rep['reason']})" if scope == "full" else "delta"))


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) < 5 or a[0] not in ("snapshot", "diff"):
        sys.exit(__doc__)
    (snapshot if a[0] == "snapshot" else diff)(a[1], a[2], a[3], a[4:])
