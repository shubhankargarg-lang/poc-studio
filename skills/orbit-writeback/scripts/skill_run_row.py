#!/usr/bin/env python3
"""skill_run_row.py — build one valid orbit_studio_skill_run row (orbit-writeback Moment 7).

The object has schema validation on, so a wrong type, an unknown code or an empty value fails the whole write.
This script takes the row as loose JSON (whatever the session knows), fixes what it safely can, checks the rest
against the object's schema (copied below from orbit.uat.unifyapps.com, 2026-11-03), and prints the exact
apply_record_edits payload. Nothing is sent from here.

usage:
  skill_run_row.py <in.json> [--out <payload.json>]     build and check; prints the payload (or writes it to --out)
  skill_run_row.py --start                              print a start time (epoch ms) to note before a skill runs
  skill_run_row.py --estimate <file or text>...         estimated tokens (characters / 4, rounded to 100)

exit 0: payload is valid (warnings, if any, on stderr, one per line, prefixed "fixed:")
exit 2: the row cannot be made valid (each reason on stderr, prefixed "error:"); do not send it
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

def build(row):
    fixed, errors = [], []
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
    out = json.dumps(payload, ensure_ascii=False, indent=1)
    if "--out" in a: open(a[a.index("--out") + 1], "w").write(out + "\n"); print(payload["edits"][0]["properties"]["run_id"])
    else: print(out)
