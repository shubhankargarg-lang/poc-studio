#!/usr/bin/env python3
"""skill_run_row.py — build one valid orbit_studio_skill_run row (orbit-writeback Moment 7).

The object has schema validation on, so a wrong type, an unknown code or an empty value fails the whole write.
This script takes the row as loose JSON (whatever the session knows), fixes what it safely can, checks the rest
against the object's schema (copied below from orbit.uat.unifyapps.com, 2026-11-03), and prints the exact
apply_record_edits payload. Nothing is sent from here.

usage:
  skill_run_row.py <in.json> [--out <payload.json>] [--ledger DIR]
                                                        build and check; prints the payload (or writes it to --out)
  skill_run_row.py --start                              print a start time (epoch ms) to note before a skill runs
  skill_run_row.py --estimate <file or text>...         estimated tokens (characters / 4, rounded to 100)

The local ledger (every run's row, so nothing is lost and reviews are never logged ahead of the run they checked).
DIR is the run's .poc-studio folder (the folder holding the `observability` flag); when --ledger is not given it is
$CLAUDE_PROJECT_DIR/.poc-studio, or the nearest .poc-studio folder above the current one.
  skill_run_row.py note-change <skill> [--gate gN] [--ledger DIR]   the person asked for changes to this skill's output
  skill_run_row.py change-dropped <skill> [--ledger DIR]             the person dropped that change: no re-run is expected
  skill_run_row.py saved <run_id> <reply.json> [--ledger DIR]       check Orbit's reply; mark the row saved (exit 1: not saved)
  skill_run_row.py pending [--ledger DIR]                           rows not saved yet: one payload path per line, oldest first
  skill_run_row.py rework-check [--ledger DIR]                      a re-run since the last REVISE or change request with no row
  skill_run_row.py reconcile <orbit-reply.json> [--ledger DIR]      rows Orbit does not have go back to pending
  skill_run_row.py report [--ledger DIR] [--all]                    one line: runs logged and saved, or what is still pending

Input keys that are not fields (used, then dropped): files_read, files_written (paths, for the token estimate).

exit 0: payload is valid (warnings, if any, on stderr, one per line, prefixed "fixed:")
exit 2: the row cannot be made valid (each reason on stderr, prefixed "error:"); do not send it
exit 3: write another row first (the reason on stderr, prefixed "first:"): a review is never logged before the run it
        checked, and a re-run after a REVISE or a change request always has its own row
"""
import json, os, random, sys, time

SCHEMA = {
    "run_id": "string", "run_group": "string", "poc": "string", "origin": "string", "client_name": "string",
    "use_case": "string", "primary_document_id": "string", "phase": "string", "gate": "string",
    "sequence": "integer", "skill": "string", "label": "string", "reviews_run_id": "string", "verdict": "string",
    "round": "integer", "triggered_by": "string", "actor_name": "string", "actor_email": "string",
    "plugin_version": "string", "model": "string", "started_at": "integer", "ended_at": "integer",
    "duration_ms": "integer", "tokens_in": "integer", "tokens_out": "integer", "input_ask": "string",
    "input_documents": "docs", "reasoning": "strings", "output_summary": "string", "output_decisions": "strings",
    "output_documents": "docs", "created_at": "integer",
}
REQUIRED = ["run_id", "skill", "started_at"]
CODES = {
    "origin": ["poc", "one_off"],
    "phase": ["understand", "plan", "build", "deliver"],
    "gate": ["g1", "g2", "g3", "g4", "none"],
    "verdict": ["pass", "revise", "block", "ask_human"],
    "triggered_by": ["orchestrator", "person", "command", "iteration"],
}
ALIASES = {  # words a session may write instead of the code
    "origin": {"one-off": "one_off", "oneoff": "one_off", "standalone": "one_off", "pipeline": "poc", "full": "poc"},
    "verdict": {"askhuman": "ask_human", "ask-human": "ask_human", "approve": "pass", "passed": "pass"},
    "gate": {"": "none", "-": "none", "g2a": "g2", "g2b": "g2", "g2w": "g2"},
    "triggered_by": {"command": "command", "re-run": "iteration", "rerun": "iteration", "changes": "iteration"},
}
STAGE_PHASE = {  # used only when phase / gate are missing
    "requirement-gathering": ("understand", "g1"), "scoping-l1-first": ("plan", "g2"), "wireframes": ("plan", "g2"),
    "design-system": ("plan", "g2"), "platform-master": ("build", "g3"), "unifyapps-headless": ("build", "g3"),
    "poc-collateral-studio": ("deliver", "g4"), "poc-orchestrator": ("understand", "none"),
}
SKILL_ALIASES = {  # command or short names a session may write instead of the skill
    "requirements": "requirement-gathering", "rg": "requirement-gathering", "brd": "scoping-l1-first",
    "scoping": "scoping-l1-first", "design": "design-system", "collaterals": "poc-collateral-studio",
    "app": "unifyapps-headless", "build": "unifyapps-headless", "ua:plan": "unifyapps-headless",
    "orchestrator": "poc-orchestrator", "ai pm": "ai-pm", "aipm": "ai-pm",
}
DOC_KEYS = {"name": "string", "version": "integer", "document_id": "string", "link": "string"}

def now(): return int(time.time() * 1000)

def empty(v): return v is None or (isinstance(v, str) and not v.strip()) or (isinstance(v, (list, dict)) and not v)

def to_int(v):
    if isinstance(v, bool): return None
    if isinstance(v, int): return v
    if isinstance(v, float): return int(round(v))
    if isinstance(v, str):
        t = v.strip().lower().replace(",", "").lstrip("v")
        mult = 1
        if t.endswith("k"): t, mult = t[:-1], 1000
        elif t.endswith("m"): t, mult = t[:-1], 1000000
        try: return int(round(float(t) * mult))
        except ValueError: return None
    return None

def clean_docs(v, key, fixed, errors):
    if isinstance(v, dict): v = [v]
    if not isinstance(v, list): errors.append(f"{key} must be a list of {{name, version, document_id, link}}"); return None
    out = []
    for i, d in enumerate(v):
        if isinstance(d, str): d = {"name": d}
        if not isinstance(d, dict): fixed.append(f"{key}[{i}] dropped (not an object)"); continue
        doc = {}
        for k, t in DOC_KEYS.items():
            x = d.get(k if k != "link" else "link", d.get("file_link") if k == "link" else None)
            if empty(x): continue
            if t == "integer":
                n = to_int(x)
                if n is None: fixed.append(f"{key}[{i}].version {x!r} dropped (not a whole number)"); continue
                doc[k] = n
            else: doc[k] = str(x).strip()
        if doc: out.append(doc)
    return out or None

def clean_strings(v, key, fixed):
    if isinstance(v, str): v = [s for s in v.split("\n")]
    if not isinstance(v, list): v = [str(v)]
    out = [str(s).strip().lstrip("-•* ").strip() for s in v if not empty(s)]
    if key == "reasoning" and len(out) > 6: fixed.append("reasoning cut to 6 lines"); out = out[:6]
    return out or None

STAGE_SKILLS = {"requirement-gathering", "scoping-l1-first", "wireframes", "design-system", "poc-collateral-studio"}

def build(row):
    fixed, errors = [], []
    files_read, files_written = row.pop("files_read", None), row.pop("files_written", None)
    unknown = [k for k in row if k not in SCHEMA]
    for k in unknown: fixed.append(f"{k} dropped (not a field of orbit_studio_skill_run)")
    r = {k: v for k, v in row.items() if k in SCHEMA and not empty(v)}

    r.setdefault("run_id", f"RUN-{now()}-{random.randint(1000, 9999)}")
    if not str(r["run_id"]).startswith("RUN-"): fixed.append("run_id kept as given (does not start with RUN-)")
    if "created_at" not in r: r["created_at"] = r.get("ended_at", now())

    for key, codes in CODES.items():
        if key not in r: continue
        val = str(r[key]).strip().lower().replace(" ", "_")
        val = ALIASES.get(key, {}).get(val, val)
        if val not in codes:
            fixed.append(f"{key} {r[key]!r} dropped (allowed: {', '.join(codes)})"); r.pop(key); continue
        r[key] = val

    if "skill" in r:
        sk = str(r["skill"]).strip().lower()
        sk = sk.split(":", 1)[1] if sk.startswith("poc-studio:") else sk
        sk = SKILL_ALIASES.get(sk, sk)
        if sk != r["skill"]: fixed.append(f"skill {r['skill']!r} written as {sk!r}")
        r["skill"] = sk
    skill = str(r.get("skill", "")).strip()
    if skill in STAGE_PHASE:
        ph, gt = STAGE_PHASE[skill]
        if "phase" not in r: r["phase"] = ph
        if "gate" not in r and r.get("origin") != "one_off": r["gate"] = gt
    if r.get("origin") == "one_off":
        if "poc" in r: fixed.append("poc dropped (one-off rows never carry a POC)"); r.pop("poc")
        r.setdefault("gate", "none")
    if skill != "ai-pm":
        for k in ("verdict", "reviews_run_id"):
            if k in r: fixed.append(f"{k} dropped (only ai-pm review rows carry it)"); r.pop(k)

    for key, t in SCHEMA.items():
        if key not in r: continue
        v = r[key]
        if t == "integer":
            n = to_int(v)
            if n is None or n < 0: fixed.append(f"{key} {v!r} dropped (not a whole number ≥ 0)"); r.pop(key); continue
            if key in ("tokens_in", "tokens_out") and n != v: fixed.append(f"{key} rounded to {n}")
            r[key] = n
        elif t == "string":
            r[key] = v if isinstance(v, str) else json.dumps(v) if isinstance(v, (list, dict)) else str(v)
            r[key] = r[key].strip()
        elif t == "docs":
            d = clean_docs(v, key, fixed, errors)
            if d is None: r.pop(key, None)
            else: r[key] = d
        elif t == "strings":
            s = clean_strings(v, key, fixed)
            if s is None: r.pop(key, None)
            else: r[key] = s

    # Tokens are never left empty: estimate from the files the run read and wrote (and its own text) when not measured.
    def files(v): return [v] if isinstance(v, str) else list(v or [])
    if "tokens_in" not in r:
        n = estimate(files(files_read) + [r.get("input_ask", "")])
        r["tokens_in"] = max(n, 100); fixed.append(f"tokens_in estimated: {r['tokens_in']}")
    if "tokens_out" not in r:
        txt = [r.get("output_summary", "")] + list(r.get("output_decisions") or []) + list(r.get("reasoning") or [])
        n = estimate(files(files_written) + ["\n".join(map(str, txt))])
        r["tokens_out"] = max(n, 100); fixed.append(f"tokens_out estimated: {r['tokens_out']}")
    if "round" in r and r["round"] < 1: r["round"] = 1
    if "sequence" in r and r["sequence"] < 1: fixed.append("sequence dropped (must be 1 or more)"); r.pop("sequence")
    if "started_at" in r and "ended_at" in r:
        if r["ended_at"] < r["started_at"]: fixed.append("ended_at was before started_at: dropped"); r.pop("ended_at")
        else: r["duration_ms"] = r["ended_at"] - r["started_at"]
    for k in ("started_at", "ended_at", "created_at"):
        if k in r and r[k] < 10**12: fixed.append(f"{k} looked like seconds: converted to ms"); r[k] *= 1000
    for k in REQUIRED:
        if k not in r or empty(r[k]): errors.append(f"{k} is required")
    r = {k: r[k] for k in SCHEMA if k in r and not empty(r[k])}
    payload = {"host": "https://orbit.uat.unifyapps.com", "objectId": "orbit_studio_skill_run",
               "edits": [{"op": "create", "properties": r}]}
    return payload, fixed, errors

# ---------- the local ledger ----------
def ledger_dir(a):
    if "--ledger" in a: return a[a.index("--ledger") + 1]
    if os.environ.get("CLAUDE_PROJECT_DIR"):
        d = os.path.join(os.environ["CLAUDE_PROJECT_DIR"], ".poc-studio")
        if os.path.isdir(d): return d
    cur = os.getcwd()
    while True:
        d = os.path.join(cur, ".poc-studio")
        if os.path.isdir(d): return d
        if os.path.dirname(cur) == cur: return None
        cur = os.path.dirname(cur)

def L(d, *p): return os.path.join(d, "skill-runs", *p)

def read_ledger(d):
    f = L(d, "ledger.jsonl")
    if not d or not os.path.exists(f): return []
    out = []
    for ln in open(f):
        try: out.append(json.loads(ln))
        except ValueError: pass
    return out

def append(d, e):
    os.makedirs(L(d, "rows"), exist_ok=True)
    e.setdefault("t", now())
    with open(L(d, "ledger.jsonl"), "a") as f: f.write(json.dumps(e, ensure_ascii=False) + "\n")

def rows_state(d):
    """run_id -> the row's ledger entry with its latest status (built, saved, missing)."""
    rows = {}
    for e in read_ledger(d):
        if e.get("kind") == "row": rows[e["run_id"]] = dict(e, status="built")
        elif e.get("kind") in ("saved", "missing") and e.get("run_id") in rows: rows[e["run_id"]]["status"] = e["kind"]
    return rows

def current_group(d):
    f = os.path.join(d, "observability")
    return open(f).read().strip() if os.path.exists(f) else None

def rework_due(d):
    """Per skill: a REVISE verdict or a change request newer than that skill's latest row -> what to write."""
    led = read_ledger(d); rows = {e["run_id"]: e for e in led if e.get("kind") == "row"}
    last_row, trigger = {}, {}
    for e in led:
        if e.get("kind") == "row" and e.get("skill") in STAGE_SKILLS:
            last_row[e["skill"]] = e; trigger.pop(e["skill"], None)
        elif e.get("kind") == "row" and e.get("skill") == "ai-pm" and e.get("verdict") in ("revise", "block") \
                and (e.get("round") or 1) < 3:  # the third review is a ruling: the run goes to the gate, no re-run
            target = rows.get(e.get("reviews_run_id"), {}).get("skill")
            if target in STAGE_SKILLS: trigger[target] = ("revise", e)
        elif e.get("kind") == "change" and e.get("skill") in STAGE_SKILLS:
            trigger[e["skill"]] = ("change", e)
        elif e.get("kind") == "change_dropped":
            trigger.pop(e.get("skill"), None)
    return {sk: (why, e, last_row.get(sk)) for sk, (why, e) in trigger.items()}

def check_order(d, r):
    """A review is logged only after the run it checked, and only after the re-run that a REVISE or a change asked for."""
    if r.get("skill") != "ai-pm" or r.get("gate") == "g3" or r.get("phase") == "build":
        return None  # the build walk (4b) runs before the build's own row, which is written at publish
    rows = rows_state(d)
    rid = r.get("reviews_run_id")
    if not rid: return ("this review has no reviews_run_id: write the row of the run it checked first, then give its "
                        "run_id here (observability.runs)")
    if rid not in rows: return f"reviews_run_id {rid} is not a logged run: write the row of the run this review checked first"
    sk = rows[rid].get("skill")
    due = rework_due(d).get(sk)
    if due:
        why = "the AI PM's REVISE" if due[0] == "revise" else "the person's change request"
        return (f"{sk} re-ran after {why} and that re-run has no row: write it first (round +1, label '<doc> v<N> · "
                f"<k> fixes' or '· changes', triggered_by {'iteration' if due[0] == 'change' else 'orchestrator'}), "
                f"then use its run_id as reviews_run_id")
    return None

def reply_ok(reply):
    res = reply.get("results") if isinstance(reply, dict) else None
    if isinstance(res, list) and res: return all(isinstance(x, dict) and x.get("ok") is True for x in res)
    return isinstance(reply, dict) and reply.get("ok") is True

def estimate(args):
    total = 0
    for a in args:
        total += len(open(a, errors="ignore").read()) if os.path.isfile(a) else len(a)
    return int(round(total / 4 / 100.0)) * 100

if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    if a[0] == "--start": print(now()); sys.exit(0)
    if a[0] == "--estimate": print(estimate(a[1:])); sys.exit(0)
    if a[0] in ("note-change", "change-dropped", "saved", "pending", "rework-check", "reconcile", "report"):
        d = ledger_dir(a)
        if not d: print("error: no .poc-studio folder found (pass --ledger <dir>)", file=sys.stderr); sys.exit(2)
        cmd, args = a[0], [x for i, x in enumerate(a[1:], 1) if x not in ("--ledger", "--gate", "--all") and a[i - 1] not in ("--ledger", "--gate")]
        rows = rows_state(d)
        if cmd == "note-change":
            if not args: sys.exit("usage: note-change <skill> [--gate gN]")
            sk = SKILL_ALIASES.get(args[0].split(":")[-1], args[0].split(":")[-1])
            append(d, {"kind": "change", "skill": sk, "gate": a[a.index("--gate") + 1] if "--gate" in a else None})
            print(f"change noted for {sk}: its re-run gets its own row (triggered_by iteration) before the next review"); sys.exit(0)
        if cmd == "change-dropped":
            if not args: sys.exit("usage: change-dropped <skill>")
            sk = SKILL_ALIASES.get(args[0].split(":")[-1], args[0].split(":")[-1])
            append(d, {"kind": "change_dropped", "skill": sk}); print(f"change for {sk} dropped: no re-run row expected"); sys.exit(0)
        if cmd == "saved":
            if len(args) < 2: sys.exit("usage: saved <run_id> <reply.json>")
            rid, src = args[0], args[1]
            try: reply = json.load(sys.stdin if src == "-" else open(src))
            except Exception as e: print(f"error: cannot read the reply: {e}", file=sys.stderr); sys.exit(1)
            if rid not in rows: print(f"error: {rid} is not in the ledger", file=sys.stderr); sys.exit(1)
            if not reply_ok(reply):
                print(f"not saved: {json.dumps(reply)[:400]}", file=sys.stderr); print("the row stays pending; it is sent again at the next step", file=sys.stderr); sys.exit(1)
            append(d, {"kind": "saved", "run_id": rid}); print(f"saved {rid}"); sys.exit(0)
        if cmd == "pending":
            for rid, e in sorted(rows.items(), key=lambda kv: kv[1]["t"]):
                if e["status"] != "saved": print(L(d, "rows", f"{rid}.json"))
            sys.exit(0)
        if cmd == "rework-check":
            for sk, (why, e, last) in rework_due(d).items():
                print(f"{sk}: re-run after {'the AI PM REVISE' if why == 'revise' else 'the change request'} has no row yet")
            sys.exit(0)
        if cmd == "reconcile":
            if not args: sys.exit("usage: reconcile <orbit-reply.json>  (get_records on orbit_studio_skill_run for this POC or run_group)")
            import re as _re
            txt = open(args[0]).read(); in_orbit = set(_re.findall(r"RUN-\d+-\d+", txt))
            group = current_group(d); n = 0
            for rid, e in rows.items():
                if group and e.get("run_group") != group and "--all" not in a: continue
                if rid not in in_orbit and e["status"] == "saved": append(d, {"kind": "missing", "run_id": rid}); n += 1
            print(f"{n} saved row(s) not found in Orbit: back to pending" if n else "every saved row is in Orbit"); sys.exit(0)
        if cmd == "report":
            group = current_group(d)
            sel = [e for e in rows.values() if "--all" in a or not group or e.get("run_group") == group]
            left = [e for e in sel if e["status"] != "saved"]
            due = rework_due(d)
            if not left and not due: print(f"Observability: {len(sel)} runs logged, all saved in Orbit.")
            else:
                print(f"Observability: {len(sel)} runs logged, {len(sel) - len(left)} saved, {len(left)} not saved yet"
                      + (f", {len(due)} re-run(s) with no row" if due else "") + ".")
                for e in sorted(left, key=lambda e: e["t"]): print(f"  not saved: {e.get('skill')} · {e.get('label')} ({e['run_id']})")
                for sk in due: print(f"  no row: the latest re-run of {sk}")
            sys.exit(0)
    try: row = json.load(open(a[0]))
    except Exception as e: print(f"error: cannot read {a[0]} as JSON: {e}", file=sys.stderr); sys.exit(2)
    if not isinstance(row, dict):
        print("error: the input must be one JSON object (the row's fields)", file=sys.stderr); sys.exit(2)
    row = row.get("edits", [{}])[0].get("properties", row) if "edits" in row else row
    payload, fixed, errors = build(row)
    for f in fixed: print(f"fixed: {f}", file=sys.stderr)
    if errors:
        for e in errors: print(f"error: {e}", file=sys.stderr)
        sys.exit(2)
    props = payload["edits"][0]["properties"]
    d = ledger_dir(a)
    if d:
        first = check_order(d, props)
        if first: print(f"first: {first}", file=sys.stderr); sys.exit(3)
        rows = rows_state(d)
        if props["run_id"] in rows: print(f"error: run_id {props['run_id']} is already in the ledger (build without run_id)", file=sys.stderr); sys.exit(2)
        append(d, {"kind": "row", "run_id": props["run_id"], "skill": props.get("skill"), "label": props.get("label"),
                   "gate": props.get("gate"), "round": props.get("round"), "verdict": props.get("verdict"),
                   "reviews_run_id": props.get("reviews_run_id"), "run_group": props.get("run_group"), "poc": props.get("poc")})
        json.dump(payload, open(L(d, "rows", f"{props['run_id']}.json"), "w"), ensure_ascii=False, indent=1)
    else:
        print("fixed: no .poc-studio folder found: the row is not in the local ledger (pass --ledger <dir>)", file=sys.stderr)
    out = json.dumps(payload, ensure_ascii=False, indent=1)
    if "--out" in a: open(a[a.index("--out") + 1], "w").write(out + "\n"); print(props["run_id"])
    else: print(out)
