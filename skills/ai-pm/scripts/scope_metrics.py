#!/usr/bin/env python3
"""scope_metrics.py — the AI PM's numbers on a scoping document, beyond what check_docx.py enforces.

check_docx.py proves the document is well formed. This script measures whether the scope is the right size and the
writing is specific: L1 share, build-scope sizing against the POV budget, the executive summary's opening, slop and
unsourced numbers in Part A, the primary persona, and the demo storyline. Every result is a candidate finding for the
reviewer to confirm by reading the section it points at.

usage: python3 scope_metrics.py <scoping-document.docx> [--json out.json]
"""
import json, re, sys, collections, os
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

HERE = os.path.dirname(os.path.abspath(__file__))
SLOP = json.load(open(os.path.join(HERE, "slop-phrases.json")))
BUDGET = {"pages_per_app": (3, 6), "objects_per_app": (8, 12), "workflows_per_app": (3, 8), "agents": (1, 1), "l1_share": (0.30, 0.50)}

doc = Document(sys.argv[1])
blocks, h1, h2 = [], "", ""
for el in doc.element.body.iterchildren():
    if el.tag.endswith("}p"):
        p = Paragraph(el, doc); s = p.style.name if p.style is not None else ""
        if s == "Heading 1": h1, h2 = p.text.strip(), ""
        elif s == "Heading 2": h2 = p.text.strip()
        blocks.append(("p", p, h1, h2, s))
    elif el.tag.endswith("}tbl"):
        blocks.append(("t", Table(el, doc), h1, h2, ""))

def sec(n):  # section number of a Heading 1 like "5. Scope"
    m = re.match(r"(\d+)\.", n); return int(m.group(1)) if m else None
heads = [b[1].text.strip() for b in blocks if b[0] == "p" and b[4].startswith("Heading")]
part_a = [b for b in blocks if sec(b[2]) is not None and sec(b[2]) <= 9]
head = lambda t: [c.text.strip() for c in t.rows[0].cells]

out, F = {}, []
def find(dim, blocking, where, evidence, fix):
    F.append({"id": f"S{len(F)+1}", "dimension": dim, "blocking": blocking, "where": where, "evidence": evidence, "fix": fix})

# Catalogue: L1 and L2
l1, l2 = set(), set()
for b in blocks:
    if b[0] != "t": continue
    h = head(b[1])
    if h[:2] == ["ID", "Sub-feature"]:
        ids = {r.cells[0].text.strip() for r in b[1].rows[1:]}
        (l1 if "L1 reason" in h else l2 if "Why it can wait" in h else set()).update(ids)
total = len(l1 | l2); share = len(l1) / total if total else 0
out["features"] = {"L1": len(l1), "L2": len(l2), "total": total, "l1_share": round(share, 2)}
lo, hi = BUDGET["l1_share"]
if total and share > hi: find("R10", True, "§10 catalogue", f"L1 is {len(l1)} of {total} rows ({share:.0%}); the POV guide is 30–45%",
                             "Re-test every L1 row with the L1 rule (scoping step 5); move rows with no client ask, core-flow, agent or research-must-have reason to L2")
elif total and share < lo: find("R2", False, "§10 catalogue", f"L1 is only {share:.0%} of rows", "Check no client-asked item or journey stage lost its L1 row")

# Build-scope sizing per app (from PG-/OB-/WF-/AG- headings)
def ids(prefix):
    return sorted({h.split()[0] for h in heads if re.match(rf"{prefix}-[A-Z0-9-]*\d+\b", h)})
pages, objs, wfs, ags = ids("PG"), ids("OB"), ids("WF"), ids("AG")
apps = {re.sub(r"-?\d+$", "", p[3:]) or "app" for p in pages} or {"app"}
napps = len(apps)
out["sizing"] = {"apps": napps, "pages": len(pages), "objects": len(objs), "workflows": len(wfs), "agents": len(ags)}
for k, n, key in (("pages", len(pages), "pages_per_app"), ("objects", len(objs), "objects_per_app"), ("workflows", len(wfs), "workflows_per_app")):
    cap = BUDGET[key][1] * napps
    if n > cap: find("R10", True, "§20.3", f"{n} {k} for {napps} app(s); the POV budget is ≤ {cap}",
                     f"Merge {k} (fold stages into tabs, children into fields, per-action workflows into change-status) — or re-test L1; do not explain the overrun")
if len(ags) > 1:
    find("R10", False, "§13", f"{len(ags)} agents specified ({', '.join(ags)}); the POV default is one live copilot",
         "Keep one agent unless a Decision (D-ID) says why a second is needed; check 5.7")

# §1 opening
s1 = [b[1].text.strip() for b in blocks if b[0] == "p" and sec(b[2]) == 1 and not b[4].startswith("Heading") and b[1].text.strip()]
first = s1[0] if s1 else ""
out["exec_summary_opening"] = first[:300]
PAIN = re.compile(r"\b(lose|lost|loses|cost|costs|delay|delays|slip|slips|miss|misses|missed|error|errors|risk|manual|hours|days|weeks|rework|fail|fails|late|backlog|leak|leakage|churn|penalt)", re.I)
ASIS = re.compile(r"^(today|currently|at present|the client|[A-Z][\w&]+ (uses|runs|operates|manages|has))", re.I)
if first and (ASIS.search(first) and not PAIN.search(first.split(".")[0])):
    find("R3", True, "§1 first sentence", f'opens with the as-is process: "{first[:140]}…"',
         "Open §1 with the pain: who suffers, what goes wrong, what it costs (P1)")
elif first and not PAIN.search(first):
    find("R3", False, "§1 first paragraph", f'no pain or cost word in the opening: "{first[:140]}…"', "Lead with the cost of the problem")

# Slop and unsourced numbers in Part A
hits = collections.defaultdict(list)
for b in part_a:
    txt = b[1].text if b[0] == "p" else "\n".join(c.text for r in b[1].rows for c in r.cells)
    for group in ("filler", "overclaim"):
        for p in SLOP[group]:
            if re.search(rf"(^|\W){re.escape(p)}(\W|$)", txt, re.I): hits[(group, p)].append(b[2])
    if b[0] == "p":
        for m in re.finditer(r"(\d+(?:\.\d+)?)\s?%|\b(\d+(?:\.\d+)?)\s?(hours|hrs|days|weeks|minutes)\s+(saved|faster|less|reduction)", txt):
            if not re.search(r"\b[SAE]\d+\b|assum|industry|not .*client|source", txt, re.I):
                find("R10", True, b[2], f'unsourced figure "{m.group(0)}" in: "{txt.strip()[:120]}…"',
                     "Cite the source ID (S…), the assumption (A…), or label it 'industry, not <client>' — or remove it")
for (group, p), where in hits.items():
    find("R4" if group == "filler" else "R10", group == "overclaim", ", ".join(sorted(set(where)))[:80],
         f'{group}: "{p}" ×{len(where)}', "Replace with the specific record, number or step it stands for" if group == "filler"
         else "Name the products that already do part of it and say what we add (scoping §6)")
out["slop_hits"] = {f"{g}:{p}": len(w) for (g, p), w in hits.items()}

# Primary persona
for b in blocks:
    if b[0] == "t" and sec(b[2]) == 7:
        h = head(b[1])
        if any(x.startswith("Primary") for x in h):
            i = next(k for k, x in enumerate(h) if x.startswith("Primary"))
            ys = [r.cells[0].text.strip() for r in b[1].rows[1:] if r.cells[i].text.strip().upper().startswith("Y")]
            out["primary_personas"] = ys
            if len(ys) != 1: find("R1", True, "§7 personas", f"{len(ys)} personas marked Primary: {ys}", "Mark exactly one Primary persona (scoping step 6)")
            n = len(b[1].rows) - 1
            if n > 3: find("R1", False, "§7 personas", f"{n} app personas", "Keep two or three; recipients of notifications are not personas")

# Demo storyline (20.2)
story = []
for b in blocks:
    if sec(b[2]) == 20 and b[3].startswith("20.2"):
        if b[0] == "t": story += [" | ".join(c.text.strip() for c in r.cells)[:160] for r in b[1].rows[1:]]
        elif b[4].startswith("List") and b[1].text.strip(): story.append(b[1].text.strip()[:160])
out["storyline_steps"] = story
if story and not (6 <= len(story) <= 10): find("R3", False, "§20.2", f"{len(story)} storyline steps; the guide is 6–10 in 10–15 minutes", "Trim or merge steps so the core loop lands early")

# Assumptions
a = [b for b in blocks if b[0] == "t" and b[3].startswith("5.6")]
out["assumptions"] = sum(len(t[1].rows) - 1 for t in a)

out["findings"] = F
if "--json" in sys.argv: json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=2)
print(json.dumps({k: v for k, v in out.items() if k != "findings"}, indent=2))
print(f"\n{len(F)} candidate findings ({sum(f['blocking'] for f in F)} blocking)")
for f in F: print(f"- {f['id']} {'[blocking] ' if f['blocking'] else ''}{f['dimension']} · {f['where']} — {f['evidence']} → {f['fix']}")
