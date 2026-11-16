#!/usr/bin/env python3
"""gate_feedback.py — everything the person said at a gate, as context on Orbit · Iteration (orbit-writeback Moment 2c).

The original ask is still written the moment it is made (Moment 3: an Iteration with the person's exact words in
`reason`). When a gate is approved, this script reads every human turn typed since the last gate (typed messages,
messages typed while the agent was busy, AskUserQuestion answers with their "Other" text, pasted screenshots) from
this run's chats, drops what is not feedback (approvals, "go ahead", sign-in chatter, status pings, option picks), and
hands the rest to the session. The session decides, per ask: which existing iteration it belongs to (or a new one
from the chat), its context, quotes, times asked, the skill to improve, practice or app fix, the outcome and a
confidence. This script then checks every quote is word for word, builds the Orbit edits (updates touch ONLY the new
fields, never `title` or `reason`; new chat iterations carry the person's exact words), and keeps them in an outbox
until Orbit confirms them, so nothing is lost.

Turn rules adapted from the POC Studio feedback-capture skill (extract_human_inputs.py).

usage:
  gate_feedback.py turns --gate gN [--ledger DIR]
      -> <DIR>/gate-feedback/<gN>-<ms>/turns.json (candidate turns, each with an id, its text, time, the agent's line
         before it) and prints {"file", "candidates", "noise", "transcripts"}; exit 0 always
  gate_feedback.py build <items.json> --turns <turns.json> --existing <iterations.json> --poc <POC ID> --phase <phase>
                         --actor-name <name> --actor-email <email> [--ledger DIR]
      -> checks the items, writes the Orbit payload to <DIR>/gate-feedback/outbox/<gN>-<ms>.json, moves the gate cut
         forward, prints {"payload", "updates", "creates"} (exit 2 with error: lines when an item is wrong)
  gate_feedback.py saved <payload.json> <reply.json> [--ledger DIR]   Orbit's reply: mark saved (exit 1: not saved)
  gate_feedback.py pending [--ledger DIR]                             payloads not saved yet, one path per line

items.json: {"items": [{
   "iteration_id": "<existing IT-… this ask belongs to>"   (or omit for a new ask from the chat),
   "turn_ids": ["<turn id>", …],            the turns where the person asked it (every repeat)
   "quotes": ["<exact words>", …],         optional: parts of those turns, word for word; default = the whole turns
   "title": "<Artifact: short ask>",        new ones only
   "skill": "<skill that made the document>",  new ones only
   "related_document": "<document_id>",      new ones only, optional
   "context": "<what it means and the general rule behind it, plain words, at most 60 words>",
   "root_skill": "<skill key>", "kind": "practice|app_fix", "outcome": "done|not_done|regressed|unclear",
   "outcome_version": "v3", "confidence": 0-100 }],
 "not_feedback": ["<turn id>", …] }        candidates that turned out not to be feedback
Every candidate turn must be in one item or in not_feedback.
"""
import glob, hashlib, json, os, re, sys, time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sample_redact import Redactor  # noqa: E402
from session_log import clean_str, current_transcript  # noqa: E402

SKILLS = ["requirement-gathering", "connector-discovery", "scoping-l1-first", "wireframes", "design-system",
          "platform-master", "poc-collateral-setup", "poc-collateral-studio", "research", "poc-orchestrator",
          "asset-run", "orbit-writeback"]
KINDS, OUTCOMES = ("practice", "app_fix"), ("done", "not_done", "regressed", "unclear")
NEW_FIELDS = ("context", "times_asked", "quotes", "root_skill", "kind", "outcome", "outcome_version", "confidence",
              "context_added_at")

WRAPPERS = re.compile(r"(?s)<(system-reminder|user-prompt-submit-hook|hook[\w-]*)\b[^>]*>.*?</\1>")
NOT_HUMAN = ("<task-notification", "<agent-message", "<local-command-stdout", "<local-command-stderr",
             "<local-command-caveat", "Caveat: The messages below were generated", "Another Claude session sent",
             "This session is being continued from a previous conversation", "Base directory for this skill:",
             "<bash-stdout", "<bash-stderr", "[Request interrupted by user")
APPROVAL = re.compile(r"^(yes|y|yep|yeah|ok|okay|k|sure|fine|done|approve|approved|approve and continue.*|looks good|lgtm|"
                      r"good|great|perfect|go ahead|go on|continue|proceed|next|start|ship it|thanks|thank you|nice|"
                      r"all done|done now)( (please|thanks|now|it|go))*$")
APPROVAL_WORDS = set("""yes y yep yeah ok okay k sure fine done approve approved looks look good lgtm great perfect go
ahead on continue proceed next start ship it thanks thank you nice please now all set sounds right correct cool""".split())
SIGNIN = re.compile(r"\b(sign(ed)? ?in|log(ged)? ?in|password|otp|2fa|cookies?|authenticat\w*|session expired)\b")
STATUS = re.compile(r"^(status|eta|how long|faster|hurry|are you done|progress|update|any update|still)\b")
GATE_Q = re.compile(r"(?i)\b(approve|changes|gate|ready to|go ahead|sign off)\b")


def ledger_dir(a):
    if "--ledger" in a:
        return a[a.index("--ledger") + 1]
    return os.path.join(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd(), ".poc-studio")


def arg(a, k, default=None):
    return a[a.index(k) + 1] if k in a else default


def now():
    return int(time.time() * 1000)


def norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def key(s):
    return re.sub(r"[^a-z0-9 ]+", " ", norm(s).lower()).split()


def ts(e):
    t = e.get("timestamp")
    try:
        return int(datetime.fromisoformat(str(t).replace("Z", "+00:00")).timestamp() * 1000)
    except Exception:
        return 0


def text_of(content):
    if isinstance(content, str):
        return content, 0
    out, imgs = [], 0
    for b in content or []:
        if isinstance(b, dict) and b.get("type") == "text":
            out.append(b.get("text", ""))
        elif isinstance(b, dict) and b.get("type") == "image":
            imgs += 1
    return "\n".join(out), imgs


def transcripts(d):
    """Every chat of this run: the ones the hook recorded, and the current one."""
    out = []
    f = os.path.join(d, "session-logs", "transcripts.txt")
    if os.path.isfile(f):
        out += [l.strip() for l in open(f) if l.strip()]
    cur = current_transcript(d)
    if cur:
        out.append(cur)
    seen, res = set(), []
    for p in out:
        if p not in seen and os.path.isfile(p):
            seen.add(p)
            res.append(p)
    return res


def read_turns(path, start):
    """Human turns of one chat after line `start`."""
    last_asst, asks = "", {}
    with open(path, encoding="utf-8", errors="replace") as f:
        for ln, line in enumerate(f, 1):
            if ln <= start:
                if '"AskUserQuestion"' not in line:
                    continue
            try:
                e = json.loads(line)
            except Exception:
                continue
            if e.get("isSidechain"):
                continue
            t = e.get("type")
            if t == "assistant":
                c = (e.get("message") or {}).get("content")
                tx, _ = text_of(c)
                if tx.strip():
                    last_asst = tx
                for b in c if isinstance(c, list) else []:
                    if isinstance(b, dict) and b.get("type") == "tool_use" and str(b.get("name", "")).endswith("AskUserQuestion"):
                        asks[b.get("id")] = (b.get("input") or {}).get("questions") or []
                continue
            if ln <= start:
                continue
            base = {"at": ts(e), "chat": os.path.basename(path), "line": ln, "before": clean_str(norm(last_asst)[-300:])}
            if t == "attachment":
                att = e.get("attachment") or {}
                if att.get("type") == "queued_command":
                    tx, im = text_of(att.get("prompt"))
                    yield dict(base, id="%s:%d" % (os.path.basename(path)[:8], ln), kind="typed_while_busy", text=tx, images=im)
                continue
            if t != "user":
                continue
            c = (e.get("message") or {}).get("content")
            trs = [b for b in c if isinstance(b, dict) and b.get("type") == "tool_result"] if isinstance(c, list) else []
            if trs:
                for b in trs:
                    qs = asks.get(b.get("tool_use_id"))
                    if not qs:
                        continue
                    tur = e.get("toolUseResult") if isinstance(e.get("toolUseResult"), dict) else {}
                    answers = tur.get("answers") or {}
                    rt, _ = text_of(b.get("content"))
                    if not answers:
                        answers = dict(re.findall(r'"((?:[^"\\]|\\.)*)"="((?:[^"\\]|\\.)*)"', rt or ""))
                    for i, q in enumerate(qs):
                        opts = [o.get("label", "") for o in q.get("options", []) if isinstance(o, dict)]
                        ans = answers.get(q.get("question", ""), "")
                        ans = ", ".join(ans) if isinstance(ans, list) else str(ans or "")
                        parts = [p.strip() for p in (ans.split(", ") if q.get("multiSelect") else [ans]) if p.strip()]
                        other = [p for p in parts if p not in opts]
                        yield dict(base, id="%s:%d#q%d" % (os.path.basename(path)[:8], ln, i), kind="answer",
                                   question=q.get("question", ""), options=opts, text=ans, other_text="\n".join(other),
                                   gate_question=bool(GATE_Q.search(q.get("question", ""))), images=0)
                continue
            if e.get("isMeta") or e.get("isCompactSummary") or "toolUseResult" in e:
                continue
            o = e.get("origin")
            if isinstance(o, dict) and o.get("kind", "human") != "human":
                continue
            tx, im = text_of(c)
            yield dict(base, id="%s:%d" % (os.path.basename(path)[:8], ln), kind="typed", text=tx, images=im)


def clean(t):
    if t["kind"] == "answer":
        return t
    tx = WRAPPERS.sub("", t.get("text") or "").strip()
    if tx.startswith(NOT_HUMAN):
        return None
    m = re.search(r"<command-name>(.*?)</command-name>", tx, re.S)
    if m:
        a = re.search(r"<command-args>(.*?)</command-args>", tx, re.S)
        t["kind"], t["command"] = "command", m.group(1).strip()
        tx = a.group(1).strip() if a else ""
    if not tx and not t.get("images"):
        return None
    t["text"] = tx
    return t


def noise(t):
    if t["kind"] == "answer":
        if t["other_text"].strip():
            return None
        return "gate_answer" if t["gate_question"] else "option_pick"
    if t["kind"] == "command":
        return None if t.get("command", "").endswith("feedback") and t.get("text") else "command"
    k = " ".join(key(t["text"]))
    w = k.split()
    if not w:
        return None if t.get("images") else "empty"
    if APPROVAL.match(k) or (len(w) <= 6 and all(x in APPROVAL_WORDS for x in w)):
        return "approval"
    if len(w) <= 12 and SIGNIN.search(k):
        return "signin"
    if len(w) <= 6 and STATUS.match(k):
        return "status"
    return None


def cuts_file(d):
    return os.path.join(d, "gate-feedback", "cuts.json")


def cmd_turns(a):
    d, gate = ledger_dir(a), arg(a, "--gate", "g?")
    os.makedirs(os.path.join(d, "gate-feedback"), exist_ok=True)
    cuts = json.load(open(cuts_file(d))) if os.path.isfile(cuts_file(d)) else {}
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(os.path.abspath(d))
    red = Redactor().load(root, os.path.join(d, "session-logs", "sample-cache"))
    cands, nz, ends, trs = [], {}, {}, transcripts(d)
    for p in trs:
        start = int(cuts.get(p, 0))
        last = start
        for t in read_turns(p, start):
            last = max(last, t["line"])
            t = clean(t)
            if not t:
                continue
            why = noise(t)
            if why:
                nz[why] = nz.get(why, 0) + 1
                continue
            for k in ("text", "other_text", "before"):
                if t.get(k):
                    t[k] = red.redact(clean_str(t[k]))
            cands.append(t)
        with open(p, "rb") as f:
            ends[p] = sum(1 for _ in f)
    out = os.path.join(d, "gate-feedback", "%s-%d" % (gate, now()))
    os.makedirs(out, exist_ok=True)
    cands.sort(key=lambda t: (t["at"], t["id"]))
    json.dump({"gate": gate, "turns": cands, "noise": nz, "cuts_after": ends}, open(os.path.join(out, "turns.json"), "w"),
              indent=1, ensure_ascii=False)
    print(json.dumps({"file": os.path.join(out, "turns.json"), "candidates": len(cands), "noise": nz, "transcripts": len(trs)}))
    return 0


def quote_in(q, text):
    q, t = norm(q).lower(), norm(text).lower()
    parts = [p.strip(" .,;:") for p in re.split(r"\s*(?:…|\.{3,})\s*", q) if p.strip(" .,;:")]
    pos = 0
    for p in parts:
        i = t.find(p, pos)
        if i < 0:
            return False
        pos = i + len(p)
    return bool(parts)


def cmd_build(a):
    d = ledger_dir(a)
    items_p, turns_p, ex_p = a[1], arg(a, "--turns"), arg(a, "--existing")
    poc, phase = arg(a, "--poc"), arg(a, "--phase")
    errs = []
    if not (turns_p and ex_p and poc and phase):
        print("error: --turns, --existing, --poc and --phase are required", file=sys.stderr)
        return 2
    T = json.load(open(turns_p))
    turns = {t["id"]: t for t in T["turns"]}
    items = json.load(open(items_p))
    ex = json.load(open(ex_p))
    rows = ex.get("records") or ex.get("data") or ex.get("objects") or (ex if isinstance(ex, list) else [])
    recs = {}
    for r in rows:
        p = r.get("properties") or r
        if p.get("iteration_id"):
            recs[p["iteration_id"]] = {"id": r.get("id") or r.get("recordId"), "reason": p.get("reason") or "",
                                       "context": p.get("context"), "version": r.get("version")}
    used = set(items.get("not_feedback") or [])
    edits, n_up, n_new, stamp = [], 0, 0, now()
    for n, it in enumerate(items.get("items") or [], 1):
        tag = it.get("iteration_id") or "new %d" % n
        tids = it.get("turn_ids") or []
        if not tids:
            errs.append(f"{tag}: no turn_ids")
            continue
        miss = [x for x in tids if x not in turns]
        if miss:
            errs.append(f"{tag}: unknown turn ids {miss}")
            continue
        used.update(tids)
        src = [turns[x] for x in tids]
        full = [(t.get("other_text") or t.get("text") or "").strip() for t in src]
        quotes = it.get("quotes") or full
        for q in quotes:
            if not any(quote_in(q, f) for f in full):
                errs.append(f"{tag}: quote not word for word in its turns: {q[:80]!r}")
        if it.get("root_skill") not in SKILLS:
            errs.append(f"{tag}: root_skill must be one of {SKILLS}")
        if it.get("kind") not in KINDS:
            errs.append(f"{tag}: kind must be practice or app_fix")
        if it.get("outcome") not in OUTCOMES:
            errs.append(f"{tag}: outcome must be one of {OUTCOMES}")
        ctx = norm(it.get("context"))
        if not ctx or len(ctx.split()) > 80:
            errs.append(f"{tag}: context is required, at most 80 words")
        conf = it.get("confidence")
        if not isinstance(conf, int) or not 0 <= conf <= 100:
            errs.append(f"{tag}: confidence must be an integer 0-100")
        qlist = [{"text": q, "at": src[min(i, len(src) - 1)]["at"]} for i, q in enumerate(quotes)]
        props = {"context": ctx, "times_asked": max(1, len(set(tids))), "quotes": qlist, "root_skill": it.get("root_skill"), "kind": it.get("kind"),
                 "outcome": it.get("outcome"), "confidence": conf, "context_added_at": stamp}
        if it.get("outcome_version"):
            props["outcome_version"] = str(it["outcome_version"])
        if it.get("iteration_id"):
            r = recs.get(it["iteration_id"])
            if not r or not r["id"]:
                errs.append(f"{tag}: not in --existing (read this POC's iterations with get_records first)")
                continue
            e = {"op": "update", "recordId": r["id"], "properties": props}   # never title or reason
            if r.get("version") is not None:
                e["expectedVersion"] = r["version"]   # objects that need it refuse an update without it
            edits.append(e)
            n_up += 1
        else:
            if it.get("skill") not in SKILLS or not norm(it.get("title")):
                errs.append(f"{tag}: a new ask needs title and skill (one of the skill keys)")
                continue
            reason = "\n".join(dict.fromkeys(full))    # the person's own words, exactly as typed
            iid = "IT-%d-%d" % (stamp, n)
            props.update({"iteration_id": iid, "poc": poc, "phase": phase, "source": "chat",
                          "status": "open" if it.get("outcome") in ("not_done", "regressed") else "done",
                          "actor_name": arg(a, "--actor-name", ""), "actor_email": arg(a, "--actor-email", ""),
                          "title": norm(it["title"])[:140], "reason": reason, "skill": it["skill"], "created_at": stamp})
            if it.get("related_document"):
                props["related_document"] = it["related_document"]
            edits.append({"op": "create", "properties": props})
            n_new += 1
    left = [t for t in turns if t not in used]
    if left:
        errs.append(f"turns in no item and not in not_feedback: {left}")
    if errs:
        for e in errs:
            print("error:", e, file=sys.stderr)
        return 2
    ob = os.path.join(d, "gate-feedback", "outbox")
    os.makedirs(ob, exist_ok=True)
    pay = os.path.join(ob, "%s-%d.json" % (T.get("gate", "g"), stamp))
    if edits:
        json.dump({"host": "https://orbit.uat.unifyapps.com", "objectId": "orbit_studio_iteration", "edits": edits},
                  open(pay, "w"), indent=1, ensure_ascii=False)
    # the gate's turns are now held in the outbox: move the cut forward so the next gate starts after them
    cuts = json.load(open(cuts_file(d))) if os.path.isfile(cuts_file(d)) else {}
    cuts.update({k: int(v) for k, v in (T.get("cuts_after") or {}).items()})
    json.dump(cuts, open(cuts_file(d), "w"), indent=1)
    print(json.dumps({"payload": pay if edits else None, "updates": n_up, "creates": n_new}))
    return 0


def state_file(d):
    return os.path.join(d, "gate-feedback", "outbox-state.json")


def cmd_saved(a):
    d, pay, rep = ledger_dir(a), a[1], a[2]
    try:
        r = json.load(open(rep))
    except Exception as e:
        print(f"not saved: reply not read ({e})")
        return 1
    txt = json.dumps(r).lower()
    ok = r.get("ok") is True or (r.get("ok") is None and '"error' not in txt and "failed" not in txt)
    if not ok:
        print("not saved: " + json.dumps(r)[:300])
        return 1
    st = json.load(open(state_file(d))) if os.path.isfile(state_file(d)) else {}
    st[os.path.basename(pay)] = {"saved_at": now()}
    json.dump(st, open(state_file(d), "w"), indent=1)
    print("saved " + os.path.basename(pay))
    return 0


def cmd_pending(a):
    d = ledger_dir(a)
    st = json.load(open(state_file(d))) if os.path.isfile(state_file(d)) else {}
    for p in sorted(glob.glob(os.path.join(d, "gate-feedback", "outbox", "*.json"))):
        if os.path.basename(p) not in st:
            print(p)
    return 0


def main():
    a = sys.argv[1:]
    try:
        if a[:1] == ["turns"]:
            return cmd_turns(a)
        if a[:1] == ["build"] and len(a) > 1:
            return cmd_build(a)
        if a[:1] == ["saved"] and len(a) > 2:
            return cmd_saved(a)
        if a[:1] == ["pending"]:
            return cmd_pending(a)
        print(__doc__)
        return 0
    except Exception as e:
        print("error: " + str(e)[:300], file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
