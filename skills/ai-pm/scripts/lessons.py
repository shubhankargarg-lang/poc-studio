#!/usr/bin/env python3
"""lessons.py — the AI PM's memory across POCs.

Workspace logs (context-log.md, reviews/log.md) die with the POC. Lessons live outside any workspace so a mistake the
owner catches once is checked on every later POC.

Home: $POC_STUDIO_LESSONS or ~/.local/poc-studio/lessons/
  lessons.md          numbered rules (L-001 …), each with stage, the check, why, origin
  profiles/<owner>.md taste of one reviewer (owner), applied to every review they own
  inbox.md            gate feedback captured verbatim, waiting to become lessons
  recent-looks.md     the last design systems' look, for the logo-off test
  metrics.jsonl       one line per gate outcome, for first-try approval rate

usage:
  lessons.py init                                         refreshes seed lessons; never touches your own. Safe on every run:
                                                          seed lessons (`- source: seed`, L-001 … L-499) are added or
                                                          replaced from the plugin (repo wins); your own lessons (L-500 on)
                                                          are kept; one of yours that clashes with a new seed id is
                                                          renumbered (≥ L-500, references in inbox.md and profiles updated);
                                                          a backup lessons.md.bak-<date> is written before any change.
                                                          Other seed files are copied only when missing.
  lessons.py for <stage> [--owner <name>]                 print the checks a review of <stage> must run
  lessons.py capture <workspace> <stage> "<feedback>" [--work <id>]   store gate feedback verbatim in the inbox
                                                          (--work: count it under this id, e.g. a one-off run's SA-… id)
  lessons.py inbox                                        list pending inbox items
  lessons.py add --stage <s> --area <a> --check "<…>" --why "<…>" --origin "<…>" [--owner <name>] [--from-inbox <n>]
  lessons.py gate <workspace> <stage> [--since <n>]       gate summary for the person, from reviews/<stage>-review-<n>.yaml
                                                          (n >= since: a one-off run passes its first review number)
  lessons.py record <workspace> <stage> approved|changes|auto [--since <n>] [--work <id>]   log a gate outcome
                                                          (auto: approved by the AI PM in Sonic run mode; never a
                                                          first-try human approval, kept out of the approval stats)
  lessons.py miss <workspace> <stage> "<what was missed>" log a miss (the reviewer passed it, the owner caught it)
  lessons.py look <client> "<chrome · surface · shell · concept>"   record a design system's look
  lessons.py stats                                        first-try approval rate, rounds and misses per stage
"""
import json, os, re, sys, glob, shutil, datetime

HOME = os.path.expanduser(os.environ.get("POC_STUDIO_LESSONS", "~/.local/poc-studio/lessons"))
SEED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "lessons")
TODAY = datetime.date.today().isoformat()
STAGES = ["requirement-gathering", "scoping", "wireframes", "design-system", "build", "collaterals", "all"]

def p(*a): return os.path.join(HOME, *a)
def read(f): return open(f).read() if os.path.exists(f) else ""
def append(f, s):
    os.makedirs(os.path.dirname(f), exist_ok=True)
    with open(f, "a") as h: h.write(s)
def poc_id(ws):
    try: return json.load(open(os.path.join(ws, "state.json"))).get("poc_id", os.path.basename(ws))
    except Exception: return os.path.basename(os.path.abspath(ws))

def lessons():
    out = []
    for m in re.finditer(r"^### (L-\d+) · ([\w-]+) · (.+?)\n(.*?)(?=^### |\Z)", read(p("lessons.md")), re.S | re.M):
        out.append({"id": m.group(1), "stage": m.group(2), "area": m.group(3).strip(), "body": m.group(4).strip()})
    return out

OWN_FROM = 500                       # people's own lessons start here; seed lessons stay below
LEGACY_SEED = {f"L-{i:03d}" for i in range(1, 20)}   # shipped before the `- source: seed` marker existed

def split_blocks(text):
    """(preamble, [(id, stage, block text)]) — each block from its '### L-' line to the next."""
    parts = re.split(r"(?m)^(?=### L-\d+ · )", text)
    pre, out = parts[0], []
    for b in parts[1:]:
        m = re.match(r"### (L-\d+) · ([\w-]+) · ", b)
        out.append((m.group(1), m.group(2), b.strip() + "\n\n"))
    return pre, out

def is_seed(block, lid, stage, seed_stage):
    if re.search(r"(?m)^- source: seed\s*$", block): return True
    return lid in LEGACY_SEED and stage == seed_stage      # a legacy copy of a seed lesson

def write_atomic(path, text):
    tmp = path + ".tmp"
    with open(tmp, "w") as h: h.write(text)
    os.replace(tmp, path)

def cmd_init():
    os.makedirs(p("profiles"), exist_ok=True)
    seed = os.path.normpath(SEED)
    for f in glob.glob(os.path.join(seed, "**", "*.md"), recursive=True):
        rel = os.path.relpath(f, seed); dst = p(rel)
        if rel == "lessons.md": continue
        if not os.path.exists(dst):
            os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copy(f, dst); print("seeded", dst)
    seed_text, dst = read(os.path.join(seed, "lessons.md")), p("lessons.md")
    if not os.path.exists(dst):
        shutil.copy(os.path.join(seed, "lessons.md"), dst); print("seeded", dst)
    elif seed_text:
        refresh_seed(seed_text, dst)
    print("lessons home:", HOME, "·", len(lessons()), "lessons")

def refresh_seed(seed_text, dst):
    local_text = read(dst)
    spre, sblocks = split_blocks(seed_text)
    _, lblocks = split_blocks(local_text)
    seed_by = {i: (st, b) for i, st, b in sblocks}
    taken = {i for i, _, _ in lblocks} | set(seed_by)
    for f in glob.glob(p("profiles", "*.md")):
        taken |= set(re.findall(r"(?m)^### (L-\d+) · ", read(f)))
    changes, renames, own, kept_seed = [], {}, [], {}
    for i, st, b in lblocks:
        if i in seed_by and is_seed(b, i, st, seed_by[i][0]):
            kept_seed[i] = b                       # replaced by the repo text below
        elif i in seed_by:                         # a person's own lesson using a seed id: renumber it
            n = max([int(x[2:]) for x in taken] + [OWN_FROM - 1]) + 1
            new = f"L-{n:03d}"; taken.add(new); renames[i] = new
            own.append(re.sub(rf"^### {re.escape(i)} · ", f"### {new} · ", b))
            changes.append(f"renumbered local {i} → {new}")
        else:
            own.append(b)                          # never changed: not in the seed file
    for i, st, b in sblocks:
        if i not in kept_seed: changes.append(f"added {i}")
        elif kept_seed[i] != b: changes.append(f"updated {i}")
    lpre = split_blocks(local_text)[0]
    if not changes and lpre.strip() == spre.strip(): return     # nothing to refresh (whitespace aside)
    text = spre + "".join(b for _, _, b in sblocks) + "".join(own)
    if text == local_text: return
    bak = f"{dst}.bak-{TODAY}"
    if not os.path.exists(bak): shutil.copy(dst, bak); print("backup", bak)
    write_atomic(dst, text)
    if renames:                                    # keep references to renumbered lessons pointing at them
        for f in [p("inbox.md")] + glob.glob(p("profiles", "*.md")):
            t = read(f); t2 = t
            for old, new in renames.items(): t2 = re.sub(rf"\b{re.escape(old)}\b", new, t2)
            if t2 != t: write_atomic(f, t2)
    for c in changes: print(c)

def cmd_for(stage, owner=None):
    ls = [l for l in lessons() if l["stage"] in (stage, "all")]
    print(f"# Lessons for {stage} ({len(ls)})\n")
    for l in ls: print(f"### {l['id']} · {l['stage']} · {l['area']}\n{l['body']}\n")
    if owner:
        prof = read(p("profiles", f"{owner}.md"))
        print(f"# Owner profile: {owner}\n\n{prof or '(none yet)'}")
    if stage == "design-system":
        looks = read(p("recent-looks.md")).strip().splitlines()[-8:]
        print("\n# Recent looks (logo-off test)\n" + ("\n".join(looks) or "(none yet)"))

def cmd_capture(ws, stage, text, work=None):
    pid = work or poc_id(ws)
    n = len(re.findall(r"^## inbox-\d+", read(p("inbox.md")), re.M)) + 1
    append(p("inbox.md"), f"## inbox-{n} · pending · {stage} · {pid} · {TODAY}\n\n> " + text.strip().replace("\n", "\n> ") + "\n\n")
    append(p("metrics.jsonl"), json.dumps({"at": TODAY, "poc": pid, "stage": stage, "event": "feedback", "chars": len(text)}) + "\n")
    print(f"inbox-{n} captured")

def cmd_inbox():
    for m in re.finditer(r"^## (inbox-\d+) · pending · (.+?)\n\n(.*?)(?=^## |\Z)", read(p("inbox.md")), re.S | re.M):
        print(f"{m.group(1)} · {m.group(2)}\n{m.group(3).strip()}\n")

def cmd_add(a):
    stage = a["stage"]; assert stage in STAGES, f"stage must be one of {STAGES}"
    ids = [int(l["id"][2:]) for l in lessons()]
    for f in glob.glob(p("profiles", "*.md")): ids += [int(x) for x in re.findall(r"(?m)^### L-(\d+) · ", read(f))]
    nxt = max([i for i in ids if i >= OWN_FROM] + [OWN_FROM - 1]) + 1   # your own lessons start at L-500
    lid = f"L-{nxt:03d}"
    block = f"### {lid} · {stage} · {a['area']}\n- check: {a['check']}\n- why: {a['why']}\n- origin: {a['origin']}\n- added: {TODAY}\n\n"
    if a.get("owner"): append(p("profiles", f"{a['owner']}.md"), block)
    else: append(p("lessons.md"), block)
    if a.get("from-inbox"):
        s = read(p("inbox.md")).replace(f"## {a['from-inbox']} · pending ·", f"## {a['from-inbox']} · {lid} ·")
        open(p("inbox.md"), "w").write(s)
    print(lid, "added", "to profile " + a["owner"] if a.get("owner") else "")

def load_yaml(f):
    try:
        import yaml; return yaml.safe_load(open(f))
    except ImportError: sys.exit("pip install pyyaml (needed to read verdicts)")

def review_files(ws, stage, since=1):
    """Verdict files <stage>-review-<n>.yaml with n >= since, in numeric order (10 after 9)."""
    out = []
    for f in glob.glob(os.path.join(ws, "reviews", f"{stage}-review-*.yaml")):
        if f.endswith(".request.yaml"): continue
        m = re.search(r"-review-(\d+)\.yaml$", f)
        if m and int(m.group(1)) >= since: out.append((int(m.group(1)), f))
    return [f for _, f in sorted(out)]

def cmd_gate(ws, stage, since=1):
    vs = []
    for f in review_files(ws, stage, since):
        v = load_yaml(f) or {}; v["_file"] = os.path.basename(f); vs.append(v)
    if not vs: print(f"No review verdicts for {stage} in {ws}/reviews"); return
    last = vs[-1]
    fixed = disputed = ruled = 0; open_minor, check_this, ruling_lines = [], [], []
    for v in vs:
        for r in v.get("responses", []) or []:
            if r.get("status") == "fixed": fixed += 1
            elif r.get("status") == "disputed": disputed += 1
        for d in v.get("rulings", []) or []:
            ruled += 1; ruling_lines.append(f"- {d.get('finding')}: {d.get('ruling')} — {d.get('why', '')}")
        for d in v.get("decisions", []) or []:
            if d.get("check_this"): check_this.append(f"- {d.get('answer')} ({d.get('why', '')})")
    for f in last.get("findings", []) or []:
        if not f.get("blocking"): open_minor.append(f"- {f.get('where')}: {f.get('fix')}")
    print(f"**AI PM · {stage}** — {last.get('verdict')} at {last.get('score_pct')}% after {len(vs)} round(s); "
          f"{fixed} findings fixed, {disputed} disputed, {ruled} settled by ruling.\n")
    if ruling_lines: print("Rulings to check:\n" + "\n".join(ruling_lines) + "\n")
    if check_this: print("Assumptions to check:\n" + "\n".join(dict.fromkeys(check_this)) + "\n")
    blocking = [f for f in last.get("findings", []) or [] if f.get("blocking")]
    if blocking: print("Still open (blocking):\n" + "\n".join(f"- {f.get('id')} {f.get('where')}: {f.get('evidence')}" for f in blocking) + "\n")
    if open_minor: print(f"Minor, batched for later ({len(open_minor)}):\n" + "\n".join(open_minor[:8]) + "\n")
    w = last.get("weakest_part")
    if w: print(f"Weakest part (author's own): {w}")

def cmd_record(ws, stage, outcome, since=1, work=None):
    prior = [json.loads(l) for l in read(p("metrics.jsonl")).splitlines() if l.strip()]
    if outcome not in ("approved", "changes", "auto"): sys.exit("outcome must be approved, changes or auto")
    first = outcome == "approved" and not any(x["poc"] == (work or poc_id(ws)) and x["stage"] == stage and x["event"] in ("changes", "feedback") for x in prior)
    rounds = len(review_files(ws, stage, since))
    append(p("metrics.jsonl"), json.dumps({"at": TODAY, "poc": (work or poc_id(ws)), "stage": stage, "event": outcome, "first_try": first, "ai_pm_rounds": rounds}) + "\n")
    print(f"{stage}: {outcome}{' (first try)' if first else ''}")

def cmd_miss(ws, stage, what):
    append(p("metrics.jsonl"), json.dumps({"at": TODAY, "poc": poc_id(ws), "stage": stage, "event": "miss", "what": what[:300]}) + "\n")
    append(os.path.join(ws, "reviews", "log.md"), f"- {TODAY} MISS {stage}: {what}\n")
    print("miss logged; turn it into a lesson with `add --from-inbox` or `add`")

def cmd_look(client, look): append(p("recent-looks.md"), f"- {TODAY} · {client} · {look}\n"); print("look recorded")

def cmd_stats():
    rows = [json.loads(l) for l in read(p("metrics.jsonl")).splitlines() if l.strip()]
    print("| Stage | Gates | First-try approvals | Change requests | Misses | Avg AI PM rounds |\n|---|---|---|---|---|---|")
    for s in STAGES[:-1]:
        r = [x for x in rows if x["stage"] == s]
        appr = [x for x in r if x["event"] == "approved"]
        rr = [x.get("ai_pm_rounds", 0) for x in appr]
        print(f"| {s} | {len(appr)} | {sum(x.get('first_try', False) for x in appr)} | {sum(x['event'] == 'changes' for x in r)} | "
              f"{sum(x['event'] == 'miss' for x in r)} | {sum(rr) / len(rr):.1f} |" if rr else f"| {s} | 0 | – | – | – | – |")

def kv(args):
    d, i = {}, 0
    while i < len(args):
        if args[i].startswith("--"):
            if i + 1 < len(args) and not args[i + 1].startswith("--"): d[args[i][2:]] = args[i + 1]; i += 2
            else: i += 1

        else: i += 1
    return d

if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    c = a[0]
    if c == "init": cmd_init()
    elif c == "for": cmd_for(a[1], kv(a[2:]).get("owner"))
    elif c == "capture": cmd_capture(a[1], a[2], a[3], kv(a[4:]).get("work"))
    elif c == "inbox": cmd_inbox()
    elif c == "add": cmd_add(kv(a[1:]))
    elif c == "gate": cmd_gate(a[1], a[2], int(kv(a[3:]).get("since", 1)))
    elif c == "record": cmd_record(a[1], a[2], a[3], int(kv(a[4:]).get("since", 1)), kv(a[4:]).get("work"))
    elif c == "miss": cmd_miss(a[1], a[2], a[3])
    elif c == "look": cmd_look(a[1], a[2])
    elif c == "stats": cmd_stats()
    else: sys.exit(__doc__)
