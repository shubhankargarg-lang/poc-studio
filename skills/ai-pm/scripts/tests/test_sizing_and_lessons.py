#!/usr/bin/env python3
"""Tests for scope_metrics.py sizing (guide, not cap) and lessons.py init (seed refresh).

usage: python3 skills/ai-pm/scripts/tests/test_sizing_and_lessons.py      prints PASS/FAIL per case, exit 1 on a failure
Needs python-docx. Uses temporary folders only.
"""
import json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(SCRIPTS, "..", "..", ".."))
fails = []

def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail and not ok else ""))
    if not ok: fails.append(name)

# ---------- scope_metrics.py ----------
from docx import Document

def make_doc(path, pages, objs, wfs, ags, decision=None, ref203=False, l1=None):
    d = Document()
    d.add_heading("5. Scope and decisions", 1)
    d.add_heading("5.7 Decisions", 2)
    t = d.add_table(rows=1, cols=3); t.rows[0].cells[0].text, t.rows[0].cells[1].text, t.rows[0].cells[2].text = "ID", "Decision", "Why"
    r = t.add_row().cells; r[0].text, r[1].text, r[2].text = "D1", "Use one copilot", "Keeps the demo focused"
    if decision:
        r = t.add_row().cells; r[0].text, r[1].text, r[2].text = decision
    d.add_heading("10. Feature catalogue", 1)
    cat = d.add_table(rows=1, cols=4)
    for c, h in zip(cat.rows[0].cells, ["ID", "Sub-feature", "Description", "L1 reason"]): c.text = h
    for i, why in enumerate(l1 or ["Core flow (8.1)"] * 4, 1):
        r = cat.add_row().cells; r[0].text, r[1].text, r[2].text, r[3].text = f"F-{i}.1", "x", "x", why
    l2 = d.add_table(rows=1, cols=3)
    for c, h in zip(l2.rows[0].cells, ["ID", "Sub-feature", "Why it can wait"]): c.text = h
    for i in range(1, 9):
        r = l2.add_row().cells; r[0].text, r[1].text, r[2].text = f"F-9.{i}", "x", "later"
    d.add_heading("11. Pages", 1)
    for i in range(1, pages + 1): d.add_heading(f"PG-{i:02d} Page {i}", 2)
    d.add_heading("12. Objects", 1)
    for i in range(1, objs + 1): d.add_heading(f"OB-{i:02d} Object {i}", 2)
    d.add_heading("13. Agents", 1)
    for i in range(1, ags + 1): d.add_heading(f"AG-{i:02d} Agent {i}", 2)
    d.add_heading("14. Workflows", 1)
    for i in range(1, wfs + 1): d.add_heading(f"WF-{i:02d} Workflow {i}", 2)
    d.add_heading("20. Acceptance", 1)
    d.add_heading("20.3 Build scope vs future scope", 2)
    d.add_paragraph("The build has the counts below." + (" The larger workflow count is explained in D3." if ref203 else ""))
    d.save(path)

def metrics(path):
    j = path + ".json"
    r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "scope_metrics.py"), path, "--json", j], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr)
    return json.load(open(j))

def sizing(findings):
    return [f for f in findings if f["dimension"] == "R10" and f["where"] == "§20.3"]

tmp = tempfile.mkdtemp()
a = os.path.join(tmp, "a.docx"); make_doc(a, 8, 10, 6, 1)
check("sizing a: 8 PG, 10 OB, 6 WF, 1 AG → no sizing finding", sizing(metrics(a)["findings"]) == [])

b = os.path.join(tmp, "b.docx"); make_doc(b, 7, 10, 15, 1)
fb = sizing(metrics(b)["findings"])
check("sizing b: 15 WF, no D-ID in 20.3 → blocking R10", len(fb) == 1 and fb[0]["blocking"] and "Add a Decision" in fb[0]["fix"], str(fb))

c = os.path.join(tmp, "c.docx")
make_doc(c, 7, 10, 15, 1, decision=("D3", "15 workflows: needed by L1 features F-1.1, F-3.1", "Each L1 step has its own automation"), ref203=True)
mc = metrics(c); fc = sizing(mc["findings"])
check("sizing c: same plus D3 in 5.7 referenced in 20.3 → non-blocking R10 listing D3",
      len(fc) == 1 and not fc[0]["blocking"] and "D3" in fc[0]["evidence"] and mc["sizing"]["decisions"] == ["D3"], str(fc))

def share(findings):
    return [f for f in findings if f["dimension"] == "R10" and f["where"] == "§10 catalogue"]
d1 = os.path.join(tmp, "d1.docx"); make_doc(d1, 6, 10, 6, 1, l1=["Core flow (8.1)"] * 12)
f1 = share(metrics(d1)["findings"])
check("l1 share: 12 of 20 L1, none client-asked → blocking", len(f1) == 1 and f1[0]["blocking"], str(f1))
d2 = os.path.join(tmp, "d2.docx"); make_doc(d2, 6, 10, 6, 1, l1=["Client ask (E2)"] * 10 + ["Core flow (8.1)"] * 2)
f2 = share(metrics(d2)["findings"])
check("l1 share: 12 of 20 L1, mostly client asks → non-blocking", len(f2) == 1 and not f2[0]["blocking"], str(f2))

# ---------- lessons.py ----------
LESSONS = os.path.join(SCRIPTS, "lessons.py")
def run(home, *args, seed=None):
    env = dict(os.environ, POC_STUDIO_LESSONS=home)
    script = LESSONS
    if seed:   # run a copy of the script whose ../../../lessons is the given seed folder
        root = tempfile.mkdtemp(); sd = os.path.join(root, "skills", "ai-pm", "scripts"); os.makedirs(sd)
        shutil.copy(LESSONS, sd); shutil.copytree(seed, os.path.join(root, "lessons")); script = os.path.join(sd, "lessons.py")
    r = subprocess.run([sys.executable, script, *args], capture_output=True, text=True, env=env)
    return r.returncode, r.stdout + r.stderr

seed_dir = os.path.join(REPO, "lessons")

# (a) fresh home
home = tempfile.mkdtemp()
code, outp = run(home, "init")
check("lessons a: fresh home → init copies everything", code == 0 and open(os.path.join(home, "lessons.md")).read() == open(os.path.join(seed_dir, "lessons.md")).read(), outp)

# (b) old local copy + own L-020, seed also ships L-020
home = tempfile.mkdtemp()
seed_now = open(os.path.join(seed_dir, "lessons.md")).read()
old = re.sub(r"(?m)^- source: seed\n", "", seed_now)                     # legacy copy: no markers
old = old.replace("Over the guide with no Decision", "OLD TEXT. Over the guide with no Decision")
os.makedirs(os.path.join(home, "profiles"))
open(os.path.join(home, "lessons.md"), "w").write(old)
run(home, "add", "--stage", "scoping", "--area", "mine", "--check", "my own check", "--why", "w", "--origin", "o")
# force the person's lesson to be L-020 (as an old plugin version would have numbered it)
t = open(os.path.join(home, "lessons.md")).read(); t = re.sub(r"### L-5\d\d · scoping · mine", "### L-020 · scoping · mine", t)
open(os.path.join(home, "lessons.md"), "w").write(t)
open(os.path.join(home, "inbox.md"), "w").write("## inbox-1 · L-020 · scoping · POC-x · 2026-11-01\n\n> my feedback\n\n")
open(os.path.join(home, "profiles", "owner.md"), "w").write("Applies L-020 to every review.\n")
seed2 = tempfile.mkdtemp(); shutil.copytree(seed_dir, os.path.join(seed2, "lessons"))
open(os.path.join(seed2, "lessons", "lessons.md"), "a").write(
    "### L-020 · all · new seed\n- check: a new seed lesson\n- why: w\n- origin: o\n- added: 2026-11-16\n- source: seed\n\n")
code, outp = run(home, "init", seed=os.path.join(seed2, "lessons"))
txt = open(os.path.join(home, "lessons.md")).read()
check("lessons b: legacy L-001 replaced by the repo text", "OLD TEXT" not in txt and "updated L-001" in outp, outp)
check("lessons b: local L-020 renumbered to L-500", "### L-500 · scoping · mine" in txt and "renumbered local L-020 → L-500" in outp, outp)
check("lessons b: seed L-020 added", "### L-020 · all · new seed" in txt and "added L-020" in outp, outp)
check("lessons b: inbox and profile references updated",
      "L-500" in open(os.path.join(home, "inbox.md")).read() and "L-500" in open(os.path.join(home, "profiles", "owner.md")).read())
check("lessons b: backup written", any(f.startswith("lessons.md.bak-") for f in os.listdir(home)))
check("lessons b: seed lessons first, own lessons last", txt.index("### L-020 · all") < txt.index("### L-500"))

# (c) init twice → second run changes nothing
before = open(os.path.join(home, "lessons.md")).read()
code, outp = run(home, "init", seed=os.path.join(seed2, "lessons"))
check("lessons c: second init changes nothing", open(os.path.join(home, "lessons.md")).read() == before
      and not re.search(r"^(updated|added|renumbered)", outp, re.M), outp)

# (d) add after init → L-501
code, outp = run(home, "add", "--stage", "build", "--area", "mine2", "--check", "c", "--why", "w", "--origin", "o")
check("lessons d: add after init gets L-501", outp.startswith("L-501"), outp)

shutil.rmtree(tmp, ignore_errors=True)
print("\n" + ("ALL PASS" if not fails else f"{len(fails)} FAILED: {', '.join(fails)}"))
sys.exit(1 if fails else 0)
