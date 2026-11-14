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
  - very long strings (big tool outputs, whole files) trimmed to 20,000 characters with a note.
The session uploads the file (Moment 7) and puts its link and line range on the row. Nothing here uploads or blocks.

usage:
  session_log.py mark <skill> <transcript_path> [--ledger DIR]   note where <skill>'s run starts (called by the hook)
  session_log.py slice <skill> [--ledger DIR] [--out FILE]       write that run's log; prints {"file","lines","bytes"}
                                                                   or {"error": ...}; exit 0 either way
DIR is the run's .poc-studio folder (default $CLAUDE_PROJECT_DIR/.poc-studio).
"""
import glob, json, os, re, sys, time
from datetime import datetime

MAX_STR = 20000
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
    if len(s) > MAX_STR:
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


def slice_run(skill, d, out):
    mpath = os.path.join(d, "session-logs", "mark-%s.json" % skill)
    if not os.path.isfile(mpath):
        return {"error": "no start mark for %s (the observability hook was not active when it started)" % skill}
    m = json.load(open(mpath))
    tr, start = m["transcript"], int(m["start_line"])
    if not os.path.isfile(tr):
        return {"error": "session log not found: %s" % tr}
    index_path = os.path.join(d, "session-logs", "index.json")
    index = json.load(open(index_path)) if os.path.isfile(index_path) else []
    # nested runs already logged inside this range, from the same transcript
    nested = [r for r in index if r.get("transcript") == tr and int(r["start"]) >= start]
    end = count_lines(tr)
    used_agents = {p for r in index for p in r.get("agents", [])}
    agents = [p for p in subagent_files(tr, int(m["started_ms"])) if p not in used_agents]
    if not out:
        out = os.path.join(d, "session-logs", "%s-%d.jsonl" % (skill, int(time.time() * 1000)))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    w = 0
    with open(out, "w", encoding="utf-8") as fo:
        def put(obj):
            fo.write(json.dumps(obj, ensure_ascii=False) + "\n")
        put({"type": "poc_studio_session_log", "skill": skill, "session_lines": "%d-%d" % (start, end),
             "subagent_logs": len(agents), "nested_runs": len(nested), "secrets_removed": True,
             "written_at": int(time.time() * 1000)})
        with open(tr, encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f, 1):
                if i < start or i > end:
                    continue
                inner = next((r for r in nested if int(r["start"]) <= i <= int(r["end"])), None)
                if inner:
                    if i == int(inner["start"]):
                        put({"type": "poc_studio_nested_run", "skill": inner["skill"],
                             "session_lines": "%s-%s" % (inner["start"], inner["end"]),
                             "note": "this part has its own log on that run's Observability row"})
                    continue
                try:
                    put(clean(json.loads(line)))
                except Exception:
                    put({"type": "unparsed", "text": clean_str(line.rstrip("\n"))})
                w += 1
        for p in agents:
            put({"type": "poc_studio_subagent_log", "file": os.path.basename(p)})
            with open(p, encoding="utf-8", errors="replace") as f:
                for line in f:
                    try:
                        put(clean(json.loads(line)))
                    except Exception:
                        put({"type": "unparsed", "text": clean_str(line.rstrip("\n"))})
    index.append({"skill": skill, "transcript": tr, "start": start, "end": end, "file": out, "agents": agents})
    with open(index_path, "w") as f:
        json.dump(index, f)
    mime = "text/plain"
    if os.path.getsize(out) > MAX_UPLOAD:   # upload_public_file takes at most 20 MB: compress the rare big one
        import gzip, shutil
        with open(out, "rb") as fi, gzip.open(out + ".gz", "wb", compresslevel=9) as fz:
            shutil.copyfileobj(fi, fz)
        os.remove(out)
        out, mime = out + ".gz", "application/gzip"
        if os.path.getsize(out) > MAX_UPLOAD:
            return {"error": "log too big to upload even compressed (%d bytes)" % os.path.getsize(out), "file": out,
                    "lines": "%d-%d" % (start, end)}
    return {"file": out, "mime": mime, "lines": "%d-%d" % (start, end), "bytes": os.path.getsize(out),
            "subagent_logs": len(agents), "nested_runs": len(nested)}


def main():
    a = sys.argv[1:]
    try:
        if a[:1] == ["mark"] and len(a) >= 3:
            print(json.dumps(mark(a[1], a[2], ledger_dir(a))))
        elif a[:1] == ["slice"] and len(a) >= 2:
            out = a[a.index("--out") + 1] if "--out" in a else None
            print(json.dumps(slice_run(a[1], ledger_dir(a), out)))
        else:
            print(__doc__)
    except Exception as e:
        print(json.dumps({"error": str(e)[:300]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
