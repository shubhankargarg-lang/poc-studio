#!/usr/bin/env python3
# check_docx.py: the scoping document's structural and count checks (SKILL.md section 8, "What it enforces").
import re, sys, hashlib, collections
from docx import Document
from docx.text.paragraph import Paragraph
from docx.table import Table
doc = Document(sys.argv[1])
errs = []

# --- walk the body in order, tracking the current Heading 1 / Heading 2 ---
blocks = []                                   # (kind, obj, h1, h2)
h1 = h2 = ""
for el in doc.element.body.iterchildren():
    if el.tag.endswith("}p"):
        p = Paragraph(el, doc); s = p.style.name if p.style is not None else ""
        if s == "Heading 1": h1, h2 = p.text.strip(), ""
        elif s == "Heading 2": h2 = p.text.strip()
        blocks.append(("p", p, h1, h2))
    elif el.tag.endswith("}tbl"):
        blocks.append(("t", Table(el, doc), h1, h2))
paras = [b[1] for b in blocks if b[0] == "p"]
tables = [b[1] for b in blocks if b[0] == "t"]
def head(t): return [c.text.strip() for c in t.rows[0].cells]
def cells(t): return [c.text for r in t.rows for c in r.cells]
def heading(p, lvl): return p.style is not None and p.style.name == f"Heading {lvl}"
h1s = [p.text.strip() for p in paras if heading(p, 1)]
allh = [p.text.strip() for p in paras if p.style is not None and p.style.name.startswith("Heading")]
text = "\n".join(p.text for p in paras)
alltext = text + "\n" + "\n".join(x for t in tables for x in cells(t))

# --- structure: sections, parts, required and forbidden headings ---
for i in range(24):
    if not any(h.startswith(f"{i}.") for h in h1s): errs.append(f"missing section {i}")
if not any(h.startswith("Appendix") for h in h1s): errs.append("missing Appendix")
def pos(pred):
    return next((i for i, h in enumerate(h1s) if pred(h)), None)
pa, pb = pos(lambda h: h.startswith("Part A")), pos(lambda h: h.startswith("Part B"))
s0, s10 = pos(lambda h: h.startswith("0.")), pos(lambda h: h.startswith("10."))
if pa is None or pb is None: errs.append("missing 'Part A' / 'Part B' Heading 1 dividers")
elif not (s0 is not None and s10 is not None and pa < s0 and s0 < pb < s10):
    errs.append("Part A must come before section 0, Part B between sections 9 and 10")
for req in ["How to read this document", "5.5 Must-have vs future scope", "10.2 Must-have catalogue",
            "10.3 Future scope", "20.1 Acceptance checklist", "20.3 Build scope vs future scope",
            "20.4 Known limits of the build", "21.1 Hero object", "21.2 Reference products",
            "E. Feature build mapping", "F. Feature research mapping"]:
    if not any(h.startswith(req) for h in allh): errs.append(f"missing heading: {req}")
for bad in [r"Full catalogue", r"^5\.5 Phases\b", r"Build slice", r"Known limits of Phase 1", r"^C\. Assumptions log"]:
    for h in allh:
        if re.search(bad, h): errs.append(f"old-layout heading: '{h}'")

# --- placeholders and code ---
for bad in ["TBD", "TODO", "{{", "```"]:
    if bad in alltext: errs.append(f"placeholder or code block: {bad}")
if re.search(r'^\s*[\{\[]\s*"', alltext, re.M): errs.append("JSON-like block found")

# --- readability: table width, Phase 1 columns, duplicates ---
wide, ph_col, ph_row = [], [], []
for n, t in enumerate(tables, 1):
    h = head(t)
    if len(h) > 10: wide.append(f"{n} ({len(h)} cols, '{h[0]} | {h[1]}…')")
    if any(x == "Phase 1" for x in h): ph_col.append(n)
    if h and h[0] in ("Item", "Convention", "Count", "Topic", "Block"):
        keys = [r.cells[0].text.strip() for r in t.rows[1:]]
        if "Phase 1" in keys: ph_row.append(n)
        for k, c in collections.Counter(keys).items():
            if c > 1 and k not in ("", "—"): errs.append(f"table {n} repeats row '{k}'")
def few(xs): return ", ".join(map(str, xs[:6])) + (f" … (+{len(xs)-6})" if len(xs) > 6 else "")
if wide: errs.append(f"{len(wide)} tables wider than 10 columns: {few(wide)}")
if ph_col: errs.append(f"{len(ph_col)} tables have a 'Phase 1' column: tables {few(ph_col)}")
if ph_row: errs.append(f"{len(ph_row)} spec tables have a 'Phase 1' row: tables {few(ph_row)}")
seen = {}
for n, t in enumerate(tables, 1):
    if len(t.rows) < 4: continue
    key = hashlib.md5("|".join(cells(t)).encode()).hexdigest()
    if key in seen: errs.append(f"table {n} duplicates table {seen[key]}; state it once and reference it")
    seen.setdefault(key, n)
runs, cur = [], []
for p in paras:
    if p.style is not None and "List" in p.style.name and p.text.strip(): cur.append(p.text.strip())
    else:
        if len(cur) >= 3: runs.append(tuple(cur))
        cur = []
if len(cur) >= 3: runs.append(tuple(cur))
for r, c in collections.Counter(runs).items():
    if c > 1: errs.append(f"list repeated {c} times (starts '{r[0][:50]}'); state it once and reference it")

# --- "Phase 2/3" only in section 5, 10.3 and the Appendix ---
def allowed(h1, h2): return h1.startswith("5.") or h2.startswith("10.3") or h1.startswith("Appendix")
stray = collections.Counter()
for kind, obj, b1, b2 in blocks:
    if allowed(b1, b2): continue
    txt = obj.text if kind == "p" else "\n".join(cells(obj))
    n = len(re.findall(r"\b(Phase [23]|later phase)\b", txt, re.I))
    if n: stray[b1] += n
for sec, n in stray.items(): errs.append(f"'Phase 2/3' mentioned {n}× in {sec}; use the page's 'Future scope' line or 10.3")

# --- diagrams ---
if len(doc.inline_shapes) < 5: errs.append(f"{len(doc.inline_shapes)} diagram images (need ≥ 5: journey, app map, AI/data flow, lifecycle, ER)")
caps = [p.text for p in paras if re.match(r"Figure \d+\.", p.text.strip())]
if len(caps) < len(doc.inline_shapes): errs.append("every diagram image needs a 'Figure N.' caption")
if not any(s.orientation == 1 for s in doc.sections): errs.append("no landscape section for wide tables")

# --- catalogue: L1 tables, L2 tables, appendix mappings ---
l1, l2, comp_ids, mapE, mapF = set(), set(), set(), set(), set()
for t in tables:
    h = head(t)
    if h[:2] == ["ID", "Sub-feature"]:
        ids = [r.cells[0].text.strip() for r in t.rows[1:]]
        if "L1 reason" in h:
            rsn = h.index("L1 reason")
            for r in t.rows[1:]:
                fid = r.cells[0].text.strip(); l1.add(fid)
                if r.cells[rsn].text.strip() in ("", "—"): errs.append(f"L1 row without L1 reason: {fid}")
        elif "Why it can wait" in h: l2 |= set(ids)
        else: errs.append(f"catalogue table (ID | Sub-feature …) with neither 'L1 reason' nor 'Why it can wait': {h[:5]}")
    if h[:2] == ["ID", "Process stage"]: mapE |= {r.cells[0].text.strip() for r in t.rows[1:]}
    if h[:2] == ["ID", "Market coverage"]: mapF |= {r.cells[0].text.strip() for r in t.rows[1:]}
    if h[:2] in (["CMP ID", "Capability"], ["CMP ID", "Component"]): comp_ids |= {r.cells[0].text.strip() for r in t.rows[1:]}
feat = l1 | l2
if not l1: errs.append("no L1 (build scope) catalogue rows")
if l1 & l2: errs.append(f"IDs in both L1 and L2: {sorted(l1 & l2)[:5]}")
if mapE != l1: errs.append(f"Appendix E build mapping does not match L1 (missing {len(l1-mapE)}, extra {len(mapE-l1)})")
if not l1 <= mapF: errs.append(f"Appendix F research mapping misses {len(l1-mapF)} L1 rows")

# --- every stated count agrees with the tables ---
for label, val in (("Grand total", len(feat)), ("L1 must-have", len(l1)), ("L2 future scope", len(l2))):
    found = re.findall(rf"{label}: (\d+)", alltext)
    if not found: errs.append(f"'{label}: N' not stated")
    for f in set(found):
        if int(f) != val: errs.append(f"'{label}: {f}' but tables have {val}")
if feat:
    for a, b in re.findall(r"\b(\d+) of (\d+)\b", alltext):
        if int(b) == len(feat) and int(a) not in (len(l1), len(l2)): errs.append(f"'{a} of {b}' matches neither L1 ({len(l1)}) nor L2 ({len(l2)})")
spec = {k: len({h.split()[0] for h in allh if re.match(rf"{p}\d+\b", h)})
        for k, p in (("Pages", r"PG-[A-Z]*"), ("Objects", r"OB-"), ("Agents", r"AG-"), ("Workflows", r"WF-"))}
spec["Components"] = len(comp_ids)
for t in tables:
    if head(t)[:2] == ["Count", "Value"]:
        for r in t.rows[1:]:
            k, v = r.cells[0].text.strip(), r.cells[1].text.strip()
            for name, n in spec.items():
                m = re.match(r"(\d+)", v)
                if k.startswith(name) and m and int(m.group(1)) != n: errs.append(f"Document control says {k} = {m.group(1)} but the specs have {n}")

# --- components and L2 leakage into build specs ---
if not comp_ids: errs.append("no capability inventory table (CMP ID | Capability …)")
for cid in set(re.findall(r"\bCMP-[A-Z]*-?\d+\b", alltext)) - comp_ids: errs.append(f"unknown component {cid}")
def expand(txt):                                         # "FC-001–FC-004" -> each ID
    out = set(re.findall(r"\b[A-Z]{2,4}-\d{3}\b", txt))
    for a, p, x, y in re.findall(r"\b(([A-Z]{2,4})-(\d{3}))\s*[–-]\s*\2-(\d{3})\b", txt):
        out |= {f"{p}-{i:03d}" for i in range(int(x), int(y) + 1)}
    return out
build_refs = set()
for p in paras:
    if p.text.startswith("Features covered"): build_refs |= expand(p.text)
for t in tables:
    h = head(t)
    for col in ("L1 feature IDs", "Features powered", "Feature IDs"):
        if col in h and h[:2] != ["ID", "Sub-feature"]:
            i = h.index(col); build_refs |= {x for r in t.rows[1:] for x in expand(r.cells[i].text)}
    if h and h[0] == "Item":
        for r in t.rows[1:]:
            if r.cells[0].text.strip() in ("Features powered", "Components and features", "Features covered"):
                build_refs |= expand(r.cells[1].text)
leak = sorted(build_refs & l2)
if leak: errs.append(f"{len(leak)} L2 feature IDs referenced in build specs, e.g. {leak[:5]}")

print("\n".join(errs) or "ok")
print("features:", len(feat), "L1:", len(l1), "L2:", len(l2), "components:", len(comp_ids),
      "pages/objects/agents/workflows:", spec["Pages"], spec["Objects"], spec["Agents"], spec["Workflows"])
