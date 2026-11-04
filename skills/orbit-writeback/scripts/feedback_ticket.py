#!/usr/bin/env python3
"""feedback_ticket.py — build the two writes for one POC Studio feedback ticket (orbit-writeback /feedback).

Builds the orbit_studio_feedback ticket and its orbit_studio_feedback_event "created" row in the one shape POC Build
Loop needs (ticket_key = ticket_no, status to_be_assigned, priority none, updated_at = created_at), checks them, and
prints them. Nothing is sent from here: the session sends each payload with apply_record_edits.

usage:
  feedback_ticket.py build <in.json> [--now <ms>] [--out-dir <dir>]
      in.json: {"title", "feedback", "given_by_name", "given_by_email", "skill", "poc", "client_name", "quote",
                "channel_ref", "priority", "attachments": [{"name", "link"}]}  (only title, feedback, given_by_name required)
      writes <out-dir>/ticket.json and <out-dir>/event.json (default: $TMPDIR or /tmp) and prints the ticket_no
  feedback_ticket.py retry <out-dir>      after a ticket_no clash: the same rows with now+1 (ticket, key, times, event id)
  feedback_ticket.py check <results.json> exit 0 only if every item in an apply_record_edits reply says "ok": true;
                                          otherwise print the platform's error and exit 3
  feedback_ticket.py --self-test          dry run: build sample tickets (with and without a POC), assert the shape, print one

exit 2: the input cannot make a valid ticket (reasons on stderr); do not send anything
"""
import json, os, random, re, sys, tempfile, time

HOST = "https://orbit.uat.unifyapps.com"
STATUSES = ["to_be_assigned", "research", "in_progress", "blocked", "in_qa", "qa_rejected", "done"]
STATUS_LABELS = {"to_be_assigned": "To be Assigned", "research": "Research", "in_progress": "In-Progress",
                 "blocked": "Blocked", "in_qa": "In QA", "qa_rejected": "QA Rejected", "done": "Done"}
PRIORITIES = ["urgent", "high", "medium", "low", "none"]
SKILLS = ["requirement-gathering", "connector-discovery", "scoping-l1-first", "wireframes", "design-system", "poc-orchestrator", "asset-run",
          "platform-master", "poc-collateral-studio", "orbit-writeback", "ai-pm", "general"]
IMAGE = re.compile(r"\.(png|jpe?g|gif|webp)$", re.I)
# the only keys a create may carry, in order
TICKET_KEYS = ["ticket_no", "ticket_key", "title", "feedback", "status", "priority", "channel", "skill", "poc",
               "client_name", "given_by_name", "given_by_email", "quote", "channel_ref", "created_at", "updated_at"]

def blank(v): return v is None or (isinstance(v, str) and not v.strip()) or (isinstance(v, (list, dict)) and not v)

def build(src, now):
    errors = []
    s = {k: (v.strip() if isinstance(v, str) else v) for k, v in src.items() if not blank(v)}
    for k in ("title", "feedback", "given_by_name"):
        if k not in s: errors.append(f"{k} is required")
    if errors: return None, None, errors
    title = " ".join(str(s["title"]).split())
    if len(title) > 90: title = title[:89].rstrip() + "…"
    text = str(s["feedback"]).rstrip()
    lines = []
    for a in s.get("attachments") or []:
        name, link = str(a.get("name", "")).strip(), str(a.get("link", "")).strip()
        if name and link: lines.append(f"{'!' if IMAGE.search(name) else ''}[{name}]({link})")
    if lines: text += "\n\n" + "\n".join(lines)
    skill = str(s.get("skill", "general")).lower()
    skill = skill if skill in SKILLS else "general"
    pr = str(s.get("priority", "none")).lower()
    pr = pr if pr in PRIORITIES else "none"
    key = f"FB-{now}"
    t = {"ticket_no": key, "ticket_key": key, "title": title, "feedback": text, "status": "to_be_assigned",
         "priority": pr, "channel": "claude", "skill": skill, "given_by_name": s["given_by_name"],
         "created_at": now, "updated_at": now}
    if s.get("poc"):
        t["poc"] = s["poc"]
        if s.get("client_name"): t["client_name"] = s["client_name"]
    for k in ("given_by_email", "quote", "channel_ref"):
        if s.get(k): t[k] = s[k]
    t = {k: t[k] for k in TICKET_KEYS if k in t}
    e = {"event_id": f"FEV-{now}-{random.randint(1000, 9999)}", "ticket": key, "ticket_key": key, "type": "created",
         "message": "Ticket created from Claude Code", "actor_name": t["given_by_name"], "actor_type": "person",
         "channel": "claude", "created_at": now}
    if t.get("given_by_email"): e["actor_email"] = t["given_by_email"]
    errors = assert_shape(t, e, has_poc=bool(s.get("poc")))
    return wrap("orbit_studio_feedback", t), wrap("orbit_studio_feedback_event", e), errors

def wrap(obj, props): return {"host": HOST, "objectId": obj, "edits": [{"op": "create", "properties": props}]}

def assert_shape(t, e, has_poc):
    errs = []
    def need(cond, msg):
        if not cond: errs.append(msg)
    need(re.fullmatch(r"FB-\d{13}", t.get("ticket_no", "")) is not None, "ticket_no must be FB-<13-digit ms>")
    need(t.get("ticket_key") == t.get("ticket_no"), "ticket_key must equal ticket_no")
    need(t.get("status") in STATUSES, f"status must be one of {STATUSES}")
    need(t.get("priority") in PRIORITIES, "priority missing or invalid")
    need(isinstance(t.get("created_at"), int) and t.get("updated_at") == t.get("created_at"), "created_at and updated_at must be the same ms")
    need(t.get("channel") == "claude", "channel must be claude")
    need(("poc" in t) == has_poc, "poc must be present only when there is a POC")
    need("client_name" not in t or "poc" in t, "client_name only with a POC")
    need(all(not blank(v) for v in t.values()) and all(not blank(v) for v in e.values()), "no empty values")
    need(set(t) <= set(TICKET_KEYS), f"unexpected keys: {sorted(set(t) - set(TICKET_KEYS))}")
    need(e.get("ticket") == t.get("ticket_no") and e.get("ticket_key") == t.get("ticket_key"), "event must point at the ticket")
    need(e.get("created_at") == t.get("created_at") and e.get("event_id", "").startswith(f"FEV-{t.get('created_at')}-"), "event must use the ticket's ms")
    return errs

def save(d, ticket, event):
    os.makedirs(d, exist_ok=True)
    for n, p in (("ticket.json", ticket), ("event.json", event)):
        json.dump(p, open(os.path.join(d, n), "w"), ensure_ascii=False, indent=1)

def retry(d):
    t = json.load(open(os.path.join(d, "ticket.json")))["edits"][0]["properties"]
    e = json.load(open(os.path.join(d, "event.json")))["edits"][0]["properties"]
    now = t["created_at"] + 1
    key = f"FB-{now}"
    t.update(ticket_no=key, ticket_key=key, created_at=now, updated_at=now)
    e.update(ticket=key, ticket_key=key, created_at=now, event_id=f"FEV-{now}-{random.randint(1000, 9999)}")
    errs = assert_shape(t, e, has_poc="poc" in t)
    if errs: [print(f"error: {x}", file=sys.stderr) for x in errs]; sys.exit(2)
    save(d, wrap("orbit_studio_feedback", t), wrap("orbit_studio_feedback_event", e)); print(key)

def check(path):
    try: r = json.load(open(path))
    except Exception as ex: print(f"error: reply is not JSON: {ex}", file=sys.stderr); sys.exit(3)
    items = r.get("results") if isinstance(r, dict) else r
    if not isinstance(items, list) or not items:
        print(f"error: no results in reply: {json.dumps(r)[:400]}", file=sys.stderr); sys.exit(3)
    bad = [i for i in items if not (isinstance(i, dict) and i.get("ok") is True)]
    if bad:
        for i in bad:
            msg = i.get("error") or i.get("message") or i.get("errors") if isinstance(i, dict) else i
            print(f"error: {json.dumps(msg, ensure_ascii=False)[:400]}", file=sys.stderr)
        sys.exit(3)
    print("ok")

def self_test():
    now = int(time.time() * 1000)
    base = {"title": "[Test] plugin intake check — safe to dismiss", "feedback": "Dry run only. Nothing is sent.",
            "given_by_name": "Test Person", "given_by_email": "test@example.com", "skill": "orbit-writeback",
            "quote": "safe to dismiss", "channel_ref": "test-client/test-use-case",
            "attachments": [{"name": "shot.png", "link": "https://orbit.uat.unifyapps.com/x/shot.png"},
                            {"name": "run.log", "link": "https://orbit.uat.unifyapps.com/x/run.log"}]}
    cases = [("no POC", dict(base)),
             ("with POC", dict(base, poc="POC-test-20261103", client_name="Test Client")),
             ("one-off with a client but no POC", dict(base, client_name="Test Client"))]
    failed = 0
    for name, src in cases:
        t, e, errs = build(src, now)
        p = t["edits"][0]["properties"] if t else {}
        extra = []
        if p and "poc" not in src and "poc" in p: extra.append("poc present without a POC")
        if p and not p["feedback"].endswith("[run.log](https://orbit.uat.unifyapps.com/x/run.log)"): extra.append("attachment lines missing")
        if p and "\n\n![shot.png](" not in p["feedback"]: extra.append("image line missing")
        ok = not errs and not extra
        failed += not ok
        print(f"{'PASS' if ok else 'FAIL'} {name}" + ("" if ok else f": {errs + extra}"))
    t, e, _ = build(cases[0][1], now)
    print("\nticket payload (no POC):\n" + json.dumps(t, ensure_ascii=False, indent=1))
    print("\nevent payload:\n" + json.dumps(e, ensure_ascii=False, indent=1))
    t2, e2, errs2 = build({"title": "x", "given_by_name": "y"}, now)
    print(f"\n{'PASS' if errs2 == ['feedback is required'] else 'FAIL'} missing feedback is refused")
    failed += errs2 != ["feedback is required"]
    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    if a[0] == "--self-test": self_test()
    elif a[0] == "build":
        try: src = json.load(open(a[1]))
        except Exception as ex: print(f"error: cannot read {a[1]}: {ex}", file=sys.stderr); sys.exit(2)
        now = int(a[a.index("--now") + 1]) if "--now" in a else int(time.time() * 1000)
        d = a[a.index("--out-dir") + 1] if "--out-dir" in a else os.environ.get("TMPDIR", tempfile.gettempdir())
        t, e, errs = build(src, now)
        if errs: [print(f"error: {x}", file=sys.stderr) for x in errs]; sys.exit(2)
        save(d, t, e); print(t["edits"][0]["properties"]["ticket_no"])
    elif a[0] == "retry": retry(a[1])
    elif a[0] == "check": check(a[1])
    else: sys.exit(__doc__)
