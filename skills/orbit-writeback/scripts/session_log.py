#!/usr/bin/env python3
"""session_log.py — the session log of one skill run, for its Observability row (orbit-writeback Moment 7).

Claude Code keeps every session as a JSONL file (the hook input's `transcript_path`). When a logged skill starts, the
skill-run-log hook calls `mark`, which notes that file and how many lines it has. When the skill returns, `slice` writes
one JSONL file with exactly that run's part of the session:
  - the main session's lines from the mark to now;
  - the full logs of helper agents (subagents) that started during the run (AI PM, research helpers, builders);
  - a marker line in place of each nested logged run that already has its own log (research or an AI PM review
    inside a stage), so nothing is stored twice;
  - sign-in secrets removed (cookies such as Orbit's `_at`, bearer tokens, JWTs, API keys, passwords);
  - real client samples removed (sample_redact.py): every piece of text from files/samples/ is replaced with
    "[REDACTED: real sample <file>]", tool calls that read a sample have their result replaced, base64 payloads are
    replaced; a final check confirms no sample text is left ("sample_text_left": false) — only then is the file
    uploadable. Everything else is kept;
  - everything else kept in full. Only when the file is over the 20 MB upload limit is it compressed (gzip); only if
    it is still over 20 MB compressed are very long strings (big tool outputs, whole files) cut, with a note, at the
    largest length that fits.
The session uploads the file (Moment 7) and puts its link and line range on the row. Nothing here uploads or blocks.

usage:
  session_log.py mark <skill> <transcript_path> [--ledger DIR]   note where <skill>'s run starts (called by the hook)
  session_log.py mark-start <skill> [--ledger DIR]               the same, for a run the hook cannot see: call it before
                                                                   every re-run done inline (a REVISE or a change request)
  session_log.py slice <skill> [--ledger DIR] [--out FILE]       write that run's log; prints {"file","mime","lines",
                                                                   "bytes","usage"} or {"error": ...}; exit 0 either way
  session_log.py slice poc-orchestrator [--transcript FILE]      the orchestrator's own part: every line of this chat since
                                                                   its last cut that no skill run claimed (Setup, gates,
                                                                   write-backs, moving between stages)
  session_log.py slice <skill> --lines A-B [--transcript FILE]   repair: a redacted log of a given range, for a row
                                                                   written earlier without one (no token bookkeeping)
  session_log.py usage <file.jsonl>...                           real usage of whole log files (each call once)

"usage" is the real token use of the run, from the AI calls in its part of the log and its helper agents' logs, each
call counted once (Claude Code writes one call over several lines; a call already counted for another row is skipped):
  tokens_new_in      new text read     (input_tokens + cache_creation_input_tokens)
  tokens_cache_read  history re-read   (cache_read_input_tokens)
  tokens_out         text written      (output_tokens)
  tokens_total       the sum of the three: the real usage
DIR is the run's .poc-studio folder (default $CLAUDE_PROJECT_DIR/.poc-studio).
"""
import glob, json, os, re, sys, time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sample_redact import Redactor, blank_results, drop_binary, results_for, sample_tool_ids, strings  # noqa: E402

MAX_STR = None            # no cut by default: the whole log is kept
TRIM_STEPS = (200000, 50000, 20000, 5000)   # only for a log still over 20 MB after compressing
MAX_UPLOAD = 19 * 1024 * 1024

SECRET_PATTERNS = [
    # JWTs and similar three-part tokens
    (re.compile(r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{4,}"), "[REDACTED-TOKEN]"),
    # well-known key formats
    (re.compile(r"\b(sk-ant-[A-Za-z0-9_\-]{10,}|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|gho_[A-Za-z0-9]{20,}|"
                r"github_pat_[A-Za-z0-9_]{20,}|xox[abprs]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_\-]{30,})"),
     "[REDACTED-KEY]"),
    # Bearer / Basic authorization values
    (re.compile(r"(?i)\b(bearer|basic)\s+[A-Za-z0-9._~+/=\-]{16,}"), r"\1 [REDACTED]"),
    # cookies: _at=..., "_at": "...", cf_clearance=..., sessionKey=...
    (re.compile(r"(?i)\b(_at|cf_clearance|__cf_bm|sessionkey|session[_-]?id|sid)(\"?\s*[:=]\s*\"?)[^\s\"';,}]{12,}"),
     r"\1\2[REDACTED]"),
    # key = value / "key": "value" for secret-looking keys
    (re.compile(r"(?i)\b(api[_-]?key|x-api-key|secret|client[_-]?secret|password|passwd|access[_-]?token|"
                r"refresh[_-]?token|auth[_-]?token|id[_-]?token|authorization|set-cookie|cookie)"
                r"(\"?\s*[:=]\s*\"?)[^\s\"',}]{8,}"), r"\1\2[REDACTED]"),
]


def clean_str(s):
    for rx, rep in SECRET_PATTERNS:
        s = rx.sub(rep, s)
    if MAX_STR and len(s) > MAX_STR:
        s = s[:MAX_STR] + "\n[… trimmed by POC Studio: %d more characters]" % (len(s) - MAX_STR)
    return s


def clean(o):
    if isinstance(o, str):
        return clean_str(o)
    if isinstance(o, list):
        return [clean(x) for x in o]
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    return o


USAGE_FIELDS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")


class Usage:
    """Adds up AI calls, each once: by message id (or request id), keeping the largest figure seen for each field."""
    def __init__(self, counted):
        self.counted, self.calls = counted, {}

    def add(self, e):
        if not isinstance(e, dict) or e.get("type") != "assistant":
            return
        m = e.get("message") or {}
        u = m.get("usage") if isinstance(m, dict) else None
        if not isinstance(u, dict):
            return
        cid = (m.get("id") or e.get("requestId") or e.get("uuid"))
        if not cid or cid in self.counted:
            return
        cur = self.calls.setdefault(cid, {f: 0 for f in USAGE_FIELDS})
        for f in USAGE_FIELDS:
            v = u.get(f)
            if isinstance(v, int) and v > cur[f]:
                cur[f] = v

    def totals(self):
        t = {f: sum(c[f] for c in self.calls.values()) for f in USAGE_FIELDS}
        new_in = t["input_tokens"] + t["cache_creation_input_tokens"]
        return {"tokens_new_in": new_in, "tokens_cache_read": t["cache_read_input_tokens"], "tokens_out": t["output_tokens"],
                "tokens_total": new_in + t["cache_read_input_tokens"] + t["output_tokens"], "calls": len(self.calls)}


def read_counted(d):
    f = os.path.join(d, "session-logs", "counted.txt")
    return set(open(f).read().split()) if os.path.isfile(f) else set()


def save_counted(d, ids):
    if ids:
        with open(os.path.join(d, "session-logs", "counted.txt"), "a") as f:
            f.write("\n".join(ids) + "\n")


def current_transcript(d, given=None):
    """This chat's log: the one given, else the newest top-level .jsonl among the one the hook recorded and this
    project's Claude Code folder (the chat being written right now is the newest)."""
    if given:
        return given
    c = []
    rec = os.path.join(d, "session-logs", "transcript")
    if os.path.isfile(rec):
        c.append(open(rec).read().strip())
    proj = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(os.path.abspath(d))
    base = os.path.join(os.path.expanduser("~"), ".claude", "projects")
    c += glob.glob(os.path.join(base, re.sub(r"[^A-Za-z0-9]", "-", proj), "*.jsonl"))
    c = [p for p in c if p and os.path.isfile(p)]
    return max(c, key=os.path.getmtime) if c else None


def ledger_dir(argv):
    if "--ledger" in argv:
        return argv[argv.index("--ledger") + 1]
    return os.path.join(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd(), ".poc-studio")


def count_lines(path):
    n = 0
    with open(path, "rb") as f:
        for _ in f:
            n += 1
    return n


def ts_ms(entry):
    t = entry.get("timestamp") if isinstance(entry, dict) else None
    if not t:
        return None
    try:
        return int(datetime.fromisoformat(str(t).replace("Z", "+00:00")).timestamp() * 1000)
    except Exception:
        return None


def mark(skill, transcript, d):
    os.makedirs(os.path.join(d, "session-logs"), exist_ok=True)
    m = {"skill": skill, "transcript": transcript, "start_line": count_lines(transcript) + 1 if os.path.isfile(transcript) else 1,
         "started_ms": int(time.time() * 1000)}
    with open(os.path.join(d, "session-logs", "mark-%s.json" % skill), "w") as f:
        json.dump(m, f)
    return m


def subagent_files(transcript, started_ms):
    """Helper-agent logs of this session that started at or after started_ms."""
    base = os.path.dirname(transcript)
    sid = os.path.splitext(os.path.basename(transcript))[0]
    cands = set(glob.glob(os.path.join(base, sid, "**", "*.jsonl"), recursive=True))
    cands |= set(glob.glob(os.path.join(base, "agent-*.jsonl")))
    out = []
    for p in sorted(cands):
        if os.path.abspath(p) == os.path.abspath(transcript):
            continue
        try:
            if os.path.getmtime(p) * 1000 < started_ms - 1000:
                continue
            with open(p, encoding="utf-8", errors="replace") as f:
                first = json.loads(f.readline() or "{}")
        except Exception:
            continue
        if first.get("sessionId") and first.get("sessionId") != sid and os.path.dirname(p) == base:
            continue
        t = ts_ms(first)
        if t is not None and t < started_ms - 1000:
            continue
        out.append(p)
    return out


def _load_index(d):
    p = os.path.join(d, "session-logs", "index.json")
    return json.load(open(p)) if os.path.isfile(p) else []


def _save_index(d, index):
    with open(os.path.join(d, "session-logs", "index.json"), "w") as f:
        json.dump(index, f)


def _uncount(d, ids):
    f = os.path.join(d, "session-logs", "counted.txt")
    if ids and os.path.isfile(f):
        keep = [x for x in open(f).read().split() if x not in set(ids)]
        open(f, "w").write("\n".join(keep) + ("\n" if keep else ""))


def _used(d, tr, r):
    """True when a row was already built from this slice (the builder records each row's log range)."""
    f = os.path.join(d, "skill-runs", "ledger.jsonl")
    want = {"t": os.path.basename(tr), "lines": "%s-%s" % (r["start"], r["end"])}
    if not os.path.isfile(f):
        return False
    for ln in open(f):
        try:
            e = json.loads(ln)
        except ValueError:
            continue
        lg = e.get("log") or {}
        if lg.get("t") == want["t"] and lg.get("lines") == want["lines"]:
            return True
    return False


def _in_progress(d, index, tr):
    """start lines (in tr) of skill runs that started and were not cut yet."""
    out = []
    for mp in glob.glob(os.path.join(d, "session-logs", "mark-*.json")):
        try:
            m = json.load(open(mp))
        except Exception:
            continue
        if m.get("transcript") != tr:
            continue
        done = any(r.get("skill") == m.get("skill") and int(r.get("cut_ms", 0)) >= int(m["started_ms"]) for r in index)
        if not done:
            out.append(int(m["start_line"]))
    return out


def slice_run(skill, d, out, transcript=None, lines=None):
    global MAX_STR
    MAX_STR = None
    os.makedirs(os.path.join(d, "session-logs"), exist_ok=True)
    index = _load_index(d)
    now = int(time.time() * 1000)
    started_ms, repair = None, bool(lines)
    if lines:
        # Repair: a given range (for a row written earlier without its log). No index or token bookkeeping.
        tr = current_transcript(d, transcript)
        start, end = [int(x) for x in lines.split("-")]
        since_ms = None
    elif skill == "poc-orchestrator":
        # The orchestrator's own work: this chat's lines since its last cut (or the chat's start), minus every skill
        # run that has its own row; it stops before any skill run that started and has not been cut yet.
        tr = current_transcript(d, transcript)
        if not tr:
            return {"error": "this chat's session log was not found"}
        prev = [r for r in index if r.get("transcript") == tr and r.get("skill") == "poc-orchestrator"]
        start = max(int(r["end"]) for r in prev) + 1 if prev else 1
        since_ms = max(int(r.get("cut_ms", 0)) for r in prev) if prev else 0
    else:
        mpath = os.path.join(d, "session-logs", "mark-%s.json" % skill)
        if not os.path.isfile(mpath):
            # no start mark (the hook was not active): take everything since the last claimed line of this chat
            tr = current_transcript(d, transcript)
            if not tr:
                return {"error": "no start mark for %s and this chat's session log was not found" % skill}
            mine = [r for r in index if r.get("transcript") == tr]
            start = max([int(r["end"]) for r in mine] or [0]) + 1
            since_ms = max([int(r.get("cut_ms", 0)) for r in mine] or [0])
        else:
            m = json.load(open(mpath))
            tr, start, since_ms = m["transcript"], int(m["start_line"]), int(m["started_ms"])
            started_ms = since_ms
            mine = [r for r in index if r.get("transcript") == tr]
            # a retry of the same slice (nothing cut since, and no row built from it yet): replace it
            if mine and mine[-1].get("skill") == skill and mine[-1].get("mark_ms") == since_ms \
                    and not _used(d, tr, mine[-1]):
                _uncount(d, mine[-1].get("ids", []))
                index.remove(mine[-1])
                mine = mine[:-1]
            # this skill was already cut after its mark: an inline re-run with no new mark -> start after every claimed line
            if any(r.get("skill") == skill and int(r.get("cut_ms", 0)) >= since_ms for r in mine):
                start = max(int(r["end"]) for r in mine) + 1
                since_ms = max(int(r.get("cut_ms", 0)) for r in mine)
                started_ms = since_ms
            # never overlap a run that began before this one
            before = [int(r["end"]) for r in mine if int(r["start"]) < start]
            if before:
                start = max(start, max(before) + 1)
    if not tr or not os.path.isfile(tr):
        return {"error": "session log not found: %s" % tr}
    total = count_lines(tr)
    if not repair:
        end = total
        if skill == "poc-orchestrator":
            running = [x for x in _in_progress(d, index, tr) if x > start]
            if running:
                end = min(running) - 1
    end = min(end, total)
    if end < start:
        return {"error": "nothing new in the session log since the last cut (line %d)" % (start - 1)}
    # runs already logged inside this range, from the same chat: a marker instead of their lines
    nested = [] if repair else [r for r in index if r.get("transcript") == tr and int(r["start"]) >= start and int(r["end"]) <= end]
    used_agents = {p for r in index for p in r.get("agents", [])}
    agents = [] if repair else [p for p in subagent_files(tr, since_ms) if p not in used_agents]
    if not out:
        out = os.path.join(d, "session-logs", "%s-%d.jsonl" % (skill, now))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)

    # Real samples: never in a log. Load their text, and find tool calls that read them.
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(os.path.abspath(d))
    red = Redactor().load(root, os.path.join(d, "session-logs", "sample-cache"))

    def entries():
        with open(tr, encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f, 1):
                if i < start or i > end:
                    continue
                inner = next((r for r in nested if int(r["start"]) <= i <= int(r["end"])), None)
                yield ("main", i, line, inner)
        for p in agents:
            yield ("agent", p, None, None)
            with open(p, encoding="utf-8", errors="replace") as f:
                for line in f:
                    yield ("agentline", p, line, None)

    sample_ids = set()
    if red.samples:
        for kind, i, line, inner in entries():   # pass 1: tool calls that read a sample, and what they returned
            if line is None or inner:
                continue
            try:
                e = json.loads(line)
            except Exception:
                continue
            sample_ids.update(sample_tool_ids(e))
            for _, txt in results_for(e, sample_ids):
                red.add_text(txt, "read from files/samples")

    def safe(e):
        if sample_ids:
            blank_results(e, sample_ids)
        e = drop_binary(clean(e))
        return _walk(e, red.redact) if red.runs else e

    def write(path, use):
        with open(path, "w", encoding="utf-8") as fo:
            def put(obj):
                fo.write(json.dumps(obj, ensure_ascii=False) + "\n")
            put({"type": "poc_studio_session_log", "skill": skill, "session_lines": "%d-%d" % (start, end),
                 "subagent_logs": len(agents), "nested_runs": len(nested), "secrets_removed": True,
                 "samples_redacted": red.samples, "long_text_cut_at": MAX_STR, "written_at": now})
            for kind, i, line, inner in entries():
                if kind == "agent":
                    put({"type": "poc_studio_subagent_log", "file": os.path.basename(i)})
                    continue
                if inner:
                    if i == int(inner["start"]):
                        put({"type": "poc_studio_nested_run", "skill": inner["skill"],
                             "session_lines": "%s-%s" % (inner["start"], inner["end"]),
                             "note": "this part has its own log on that run's Observability row"})
                    continue
                try:
                    e = json.loads(line)
                except Exception:
                    put({"type": "unparsed", "text": red.redact(clean_str(line.rstrip("\n")))})
                    continue
                if use is not None:
                    use.add(e)
                put(safe(e))

    use = Usage(set() if repair else read_counted(d))
    write(out, use)
    usage = use.totals()
    # final check: no sample text left anywhere in the file
    left = False
    if red.runs:
        with open(out, encoding="utf-8") as f:
            for line in f:
                if any(red.left(x) for x in strings(json.loads(line))):
                    left = True
                    break
    if not repair:
        save_counted(d, list(use.calls))
        index.append({"skill": skill, "transcript": tr, "start": start, "end": end, "file": out, "agents": agents,
                      "cut_ms": now, "mark_ms": started_ms, "ids": list(use.calls), "usage": usage})
        _save_index(d, index)
    res = {"file": out, "mime": "text/plain", "lines": "%d-%d" % (start, end), "transcript": os.path.basename(tr),
           "usage": usage, "subagent_logs": len(agents), "nested_runs": len(nested), "cut_ms": now,
           "samples": red.samples, "redacted": red.counts, "samples_not_extracted": red.not_extracted,
           "sample_text_left": left}
    if started_ms:
        res["started_ms"] = started_ms
    if repair:
        res["repair"] = True
    if left:
        os.remove(out)
        res["file"] = None
        res["upload"] = False
        res["upload_note"] = "sample text was still found after redaction: not uploadable (the row keeps its tokens)"
        return res
    if os.path.getsize(out) > MAX_UPLOAD:   # upload_public_file takes at most 20 MB: compress only then
        import gzip, shutil

        def gz():
            with open(out, "rb") as fi, gzip.open(out + ".gz", "wb", compresslevel=9) as fz:
                shutil.copyfileobj(fi, fz)
            return os.path.getsize(out + ".gz")
        size = gz()
        for cut in TRIM_STEPS:      # still too big compressed: cut only the longest texts, as little as fits
            if size <= MAX_UPLOAD:
                break
            MAX_STR = cut
            write(out, None)
            size = gz()
            res["long_text_cut_at"] = cut
        os.remove(out)
        res["file"], res["mime"] = out + ".gz", "application/gzip"
        if size > MAX_UPLOAD:
            res["upload"] = False   # too big even cut and compressed: no link, but the usage still goes on the row
            res["upload_note"] = "log too big to upload even compressed (%d bytes)" % size
    res["bytes"] = os.path.getsize(res["file"])
    return res


def _walk(o, fn):
    if isinstance(o, str):
        return fn(o)
    if isinstance(o, list):
        return [_walk(x, fn) for x in o]
    if isinstance(o, dict):
        return {k: _walk(v, fn) for k, v in o.items()}
    return o


def usage_files(paths):
    u = Usage(set())
    for p in paths:
        with open(p, encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    u.add(json.loads(line))
                except Exception:
                    pass
    return u.totals()


def main():
    a = sys.argv[1:]
    try:
        if a[:1] == ["mark"] and len(a) >= 3:
            print(json.dumps(mark(a[1], a[2], ledger_dir(a))))
        elif a[:1] == ["slice"] and len(a) >= 2:
            out = a[a.index("--out") + 1] if "--out" in a else None
            tr = a[a.index("--transcript") + 1] if "--transcript" in a else None
            ln = a[a.index("--lines") + 1] if "--lines" in a else None
            print(json.dumps(slice_run(a[1], ledger_dir(a), out, tr, ln)))
        elif a[:1] == ["mark-start"] and len(a) >= 2:
            d = ledger_dir(a)
            tr = current_transcript(d, a[a.index("--transcript") + 1] if "--transcript" in a else None)
            print(json.dumps(mark(a[1], tr, d) if tr else {"error": "this chat's session log was not found"}))
        elif a[:1] == ["usage"] and len(a) >= 2:
            print(json.dumps(usage_files(a[1:])))
        else:
            print(__doc__)
    except Exception as e:
        print(json.dumps({"error": str(e)[:300]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
