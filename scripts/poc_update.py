#!/usr/bin/env python3
"""POC Studio version check and self-update.

Every network call goes through curl (first) or Node (fallback, including the Node runtime that
UnifyApps Headless ships). Python is used only for local file work, never for HTTPS, because
Python's own certificate store is what failed on some Macs ("SSL: CERTIFICATE_VERIFY_FAILED").

usage:
  poc_update.py check [--max-age SECONDS]   compare this copy with plugin.json on GitHub main
  poc_update.py install                     download main, verify it, install it beside this copy
  poc_update.py session-start               SessionStart hook: check, install when newer, tell the session
  poc_update.py gate                        PreToolUse hook (Skill): block a new stage unless this copy is latest

check and install print one JSON line on stdout and always exit 0.
The hooks print the JSON Claude Code expects and always exit 0.

State lives in ~/.local/poc-studio/update/ :
  state.json     the last check (installed, latest, status, checked_at, error)
  plugin_root    the folder of the copy the last hook ran from (used by /poc-studio:update)
  install.lock   held while an install runs
"""
import json, os, re, shutil, subprocess, sys, tempfile, time, zipfile

REPO = "shubhankargarg-lang/poc-studio"
RAW_URL = "https://raw.githubusercontent.com/%s/main/.claude-plugin/plugin.json" % REPO
ZIP_URL = "https://codeload.github.com/%s/zip/refs/heads/main" % REPO
PLUGIN_NAME = "poc-studio"
STATE_DIR = os.path.join(os.path.expanduser("~"), ".local", "poc-studio", "update")
STATE = os.path.join(STATE_DIR, "state.json")
ROOT_FILE = os.path.join(STATE_DIR, "plugin_root")
LOCK = os.path.join(STATE_DIR, "install.lock")
FETCH_TIMEOUT = 20          # seconds per network attempt
MAX_ZIP = 200 * 1024 * 1024  # refuse anything bigger

# Skills that start a stage (or a whole run). The gate checks the version only here, so a stage
# that is already running is never interrupted: reviews, research, write-backs and the platform
# expert inside a stage are not gated.
STAGE_SKILLS = {
    "poc-orchestrator", "asset-run", "requirement-gathering", "connector-discovery",
    "scoping-l1-first", "wireframes", "design-system", "poc-collateral-studio",
}
# The build stage starts with UnifyApps Headless's planner; gate it only inside a POC Studio run.
HEADLESS_STAGE_SKILLS = {"ua:plan", "ua:setup"}

UPDATE_HELP = ("Type /poc-studio:update to install it. If that also fails, ask in the POC Studio channel "
               "and share the error above.")


# ---------------------------------------------------------------- small helpers
def now():
    return int(time.time())


def vtuple(v):
    m = re.match(r"^\s*v?(\d+)\.(\d+)\.(\d+)", str(v or ""))
    return tuple(int(x) for x in m.groups()) if m else None


def read_json(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp-%d" % os.getpid()
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def plugin_root():
    """The folder of the copy that is running: CLAUDE_PLUGIN_ROOT in hooks, else this script's parent."""
    env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env and os.path.isfile(os.path.join(env, ".claude-plugin", "plugin.json")):
        return os.path.realpath(env)
    return os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def installed_version(root):
    return str((read_json(os.path.join(root, ".claude-plugin", "plugin.json"), {}) or {}).get("version", ""))


def remember_root(root):
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(ROOT_FILE, "w") as f:
            f.write(root + "\n")
    except Exception:
        pass


# ---------------------------------------------------------------- network (curl, then Node)
def _node_candidates():
    out = []
    if shutil.which("node"):
        out.append(["node"])
    # UnifyApps Headless's pinned runtime: scripts/run-node.sh execs node with the given args.
    base = os.path.expanduser("~/.claude/plugins/cache")
    try:
        for mkt in sorted(os.listdir(base)):
            ua = os.path.join(base, mkt, "ua")
            if not os.path.isdir(ua):
                continue
            for ver in sorted(os.listdir(ua), key=lambda s: vtuple(s) or (0, 0, 0), reverse=True):
                sh = os.path.join(ua, ver, "scripts", "run-node.sh")
                if os.path.isfile(sh):
                    out.append(["bash", sh])
                    break
    except Exception:
        pass
    return out


NODE_FETCH = r"""
const [url, out] = process.argv.slice(-2);
const https = require('https'), fs = require('fs');
function get(u, hops) {
  https.get(u, {headers: {'User-Agent': 'poc-studio-update'}, timeout: %d}, res => {
    if ([301,302,303,307,308].includes(res.statusCode) && res.headers.location && hops < 5) {
      res.resume(); return get(new URL(res.headers.location, u).toString(), hops + 1);
    }
    if (res.statusCode !== 200) { console.error('HTTP ' + res.statusCode); process.exit(3); }
    const f = fs.createWriteStream(out); res.pipe(f); f.on('finish', () => f.close(() => process.exit(0)));
  }).on('timeout', function () { this.destroy(new Error('timed out')); })
    .on('error', e => { console.error(e.code || e.message); process.exit(4); });
}
get(url, 0);
""" % (FETCH_TIMEOUT * 1000)


def fetch(url, dest):
    """Download url to dest. Returns (ok, method, error_text)."""
    errors = []
    curl = shutil.which("curl")
    if curl:
        base = [curl, "-fsSL", "--retry", "2", "--retry-delay", "1", "--connect-timeout", "10",
                "--max-time", str(FETCH_TIMEOUT * 3), "-A", "poc-studio-update", "-o", dest, url]
        attempts = [base]
        # Some company networks re-sign HTTPS traffic with their own certificate, which is trusted by
        # macOS but not always by curl's bundle. --ca-native makes curl use the system store.
        attempts.append(base[:1] + ["--ca-native"] + base[1:])
        for cmd in attempts:
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=FETCH_TIMEOUT * 4)
            except Exception as e:
                errors.append("curl: %s" % e)
                break
            if r.returncode == 0 and os.path.isfile(dest) and os.path.getsize(dest) > 0:
                return True, "curl", ""
            msg = (r.stderr or "").strip().splitlines()[-1:] or ["exit %d" % r.returncode]
            errors.append(msg[0] if msg[0].startswith("curl") else "curl: %s" % msg[0])
            # Retry with --ca-native only for TLS/certificate failures (35, 60, 77, 83).
            if r.returncode not in (35, 60, 77, 83):
                break
    for node in _node_candidates():
        # --use-system-ca (Node 22.15+/23.8+) trusts the macOS keychain; older Node rejects the flag,
        # so try without it next.
        for extra in (["--use-system-ca"], []):
            cmd = node + extra + ["-e", NODE_FETCH, url, dest]
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=FETCH_TIMEOUT * 4)
            except Exception as e:
                errors.append("node: %s" % e)
                break
            if r.returncode == 0 and os.path.isfile(dest) and os.path.getsize(dest) > 0:
                return True, "node", ""
            err = (r.stderr or "").strip().splitlines()[-1:] or ["exit %d" % r.returncode]
            errors.append("node: %s" % err[0])
            if "bad option" not in (r.stderr or "") and "--use-system-ca" not in (r.stderr or ""):
                break
    if not curl and not _node_candidates():
        errors.append("neither curl nor node is available")
    return False, "", "; ".join(errors)[:600]


# ---------------------------------------------------------------- check
def latest_version():
    """(version, error). Adds a changing query so a stale CDN copy is less likely."""
    fd, tmp = tempfile.mkstemp(prefix="poc-studio-ver-")
    os.close(fd)
    try:
        ok, _, err = fetch("%s?t=%d" % (RAW_URL, now()), tmp)
        if not ok:
            return "", err or "could not download plugin.json"
        data = read_json(tmp)
        if not isinstance(data, dict) or not vtuple(data.get("version")):
            return "", "plugin.json on GitHub has no version"
        return str(data["version"]), ""
    finally:
        try:
            os.remove(tmp)
        except Exception:
            pass


def check(max_age=0):
    root = plugin_root()
    inst = installed_version(root)
    prev = read_json(STATE, {}) or {}
    if (max_age and prev.get("status") in ("current", "outdated") and prev.get("installed") == inst
            and now() - int(prev.get("checked_at", 0)) <= max_age):
        return prev
    latest, err = latest_version()
    if not latest:
        res = {"status": "unreachable", "installed": inst, "latest": prev.get("latest", ""),
               "checked_at": now(), "error": err}
    else:
        newer = (vtuple(latest) or (0, 0, 0)) > (vtuple(inst) or (0, 0, 0))
        res = {"status": "outdated" if newer else "current", "installed": inst, "latest": latest,
               "checked_at": now(), "error": ""}
    res["plugin_root"] = root
    res["pending_restart"] = prev.get("pending_restart", "")
    if res["status"] == "current":
        res["pending_restart"] = ""
    try:
        write_json(STATE, res)
    except Exception:
        pass
    return res


# ---------------------------------------------------------------- install
def _take_lock():
    os.makedirs(STATE_DIR, exist_ok=True)
    for _ in range(2):
        try:
            fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, json.dumps({"pid": os.getpid(), "at": now()}).encode())
            os.close(fd)
            return True
        except FileExistsError:
            info = read_json(LOCK, {}) or {}
            stale = now() - int(info.get("at", 0)) > 600
            try:
                os.kill(int(info.get("pid", 0)), 0)
                alive = True
            except Exception:
                alive = False
            if stale or not alive:
                try:
                    os.remove(LOCK)
                except Exception:
                    pass
                continue
            return False
    return False


def _drop_lock():
    try:
        os.remove(LOCK)
    except Exception:
        pass


def _safe_extract(zpath, dest):
    with zipfile.ZipFile(zpath) as z:
        for info in z.infolist():
            name = info.filename
            if name.startswith("/") or ".." in name.replace("\\", "/").split("/"):
                raise ValueError("unsafe path in the download: %s" % name)
            # Refuse symlinks (unix mode in the high 16 bits).
            if (info.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError("symlink in the download: %s" % name)
        z.extractall(dest)
    tops = [d for d in os.listdir(dest) if os.path.isdir(os.path.join(dest, d))]
    if len(tops) != 1:
        raise ValueError("unexpected archive layout")
    top = os.path.join(dest, tops[0])
    pj = read_json(os.path.join(top, ".claude-plugin", "plugin.json"), {}) or {}
    if pj.get("name") != PLUGIN_NAME or not vtuple(pj.get("version")):
        raise ValueError("the download is not a POC Studio plugin")
    for need in ("hooks/hooks.json", "skills", "commands"):
        if not os.path.exists(os.path.join(top, need)):
            raise ValueError("the download is missing %s" % need)
    return top, str(pj["version"])


def _installed_entries():
    """(path, data, [(key, entry)]) for poc-studio entries in Claude Code's installed_plugins.json."""
    path = os.path.expanduser("~/.claude/plugins/installed_plugins.json")
    data = read_json(path)
    found = []
    if isinstance(data, dict):
        plugins = data.get("plugins", data)
        if isinstance(plugins, dict):
            for key, val in plugins.items():
                if str(key).split("@")[0] != PLUGIN_NAME:
                    continue
                for entry in (val if isinstance(val, list) else [val]):
                    if isinstance(entry, dict) and entry.get("installPath"):
                        found.append((key, entry))
    return path, data, found


def install():
    root = plugin_root()
    before = installed_version(root)
    if not _take_lock():
        return {"status": "error", "error": "another POC Studio update is running; try again in a minute"}
    work = tempfile.mkdtemp(prefix="poc-studio-update-")
    try:
        latest, err = latest_version()
        zpath = os.path.join(work, "main.zip")
        ok, method, ferr = fetch(ZIP_URL, zpath)
        if not ok:
            return {"status": "error", "error": "could not download POC Studio from GitHub: " + ferr}
        if os.path.getsize(zpath) > MAX_ZIP:
            return {"status": "error", "error": "the download is larger than expected"}
        top, new = _safe_extract(zpath, os.path.join(work, "x"))
        if latest and vtuple(new) < vtuple(latest):
            return {"status": "error", "error": "GitHub served an older copy (%s) than its version file (%s); "
                                                 "try again in a few minutes" % (new, latest)}
        if vtuple(new) <= (vtuple(before) or (0, 0, 0)):
            return {"status": "current", "installed": before, "latest": new}

        ip_path, ip_data, entries = _installed_entries()
        # Prefer the entry this copy was loaded from, then the user-scope one.
        entries.sort(key=lambda kv: (os.path.realpath(kv[1]["installPath"]) != root,
                                     kv[1].get("scope") != "user"))
        target_note = ""
        if entries:
            # Claude Code layout: .../cache/<marketplace>/poc-studio/<version>/ . Install the new
            # version as a sibling folder and point every poc-studio entry at it, so sessions still
            # running keep their own files until they restart.
            cur = entries[0][1]["installPath"]
            parent = os.path.dirname(os.path.realpath(cur))
            dest = os.path.join(parent, new)
            staging = dest + ".incoming-%d" % os.getpid()
            shutil.rmtree(staging, ignore_errors=True)
            shutil.copytree(top, staging, symlinks=False)
            if os.path.exists(dest):
                old = dest + ".old-%d" % now()
                os.replace(dest, old)
                shutil.rmtree(old, ignore_errors=True)
            os.replace(staging, dest)
            backup = ip_path + ".bak"
            try:
                shutil.copy2(ip_path, backup)
            except Exception:
                pass
            for _, entry in entries:
                entry["installPath"] = dest
                if "version" in entry:
                    entry["version"] = new
                if "lastUpdated" in entry:
                    entry["lastUpdated"] = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
                if "gitCommitSha" in entry:
                    entry.pop("gitCommitSha", None)
            write_json(ip_path, ip_data)
            target = dest
        else:
            # No Claude Code record found (for example a copy loaded with --plugin-dir): replace this
            # copy's files in place, keeping a backup beside it.
            staging = root + ".incoming-%d" % os.getpid()
            shutil.rmtree(staging, ignore_errors=True)
            shutil.copytree(top, staging, symlinks=False)
            backup = root + ".previous"
            shutil.rmtree(backup, ignore_errors=True)
            os.replace(root, backup)
            os.replace(staging, root)
            target = root
            target_note = "replaced in place"

        _refresh_marketplace_clone()
        st = read_json(STATE, {}) or {}
        st.update({"status": "outdated", "installed": before, "latest": new, "pending_restart": new,
                   "checked_at": now(), "error": ""})
        write_json(STATE, st)
        res = {"status": "installed", "from": before, "to": new, "path": target, "via": method}
        if target_note:
            res["note"] = target_note
        return res
    except Exception as e:
        return {"status": "error", "error": str(e)[:400]}
    finally:
        shutil.rmtree(work, ignore_errors=True)
        _drop_lock()


def _refresh_marketplace_clone():
    """Best effort: bring Claude Code's git copy of the marketplace up to date, so its own update
    logic sees the same version. Failure here is harmless and ignored."""
    git = shutil.which("git")
    base = os.path.expanduser("~/.claude/plugins/marketplaces")
    if not git or not os.path.isdir(base):
        return
    for name in os.listdir(base):
        d = os.path.join(base, name)
        mj = read_json(os.path.join(d, ".claude-plugin", "marketplace.json"), {}) or {}
        if not any(isinstance(p, dict) and p.get("name") == PLUGIN_NAME for p in mj.get("plugins", [])):
            continue
        try:
            subprocess.run([git, "-C", d, "pull", "--ff-only", "-q"], capture_output=True, timeout=30,
                           env=dict(os.environ, GIT_TERMINAL_PROMPT="0"))
        except Exception:
            pass


# ---------------------------------------------------------------- hooks
def _hook_input():
    try:
        return json.loads(sys.stdin.read() or "{}")
    except Exception:
        return {}


def session_start():
    _hook_input()
    root = plugin_root()
    remember_root(root)
    res = check()
    ctx, msg = "", ""
    if res["status"] == "outdated":
        if res.get("pending_restart") and vtuple(res["pending_restart"]) >= vtuple(res["latest"]):
            inst = {"status": "installed", "from": res["installed"], "to": res["pending_restart"]}
        else:
            inst = install()
        if inst.get("status") == "installed":
            msg = ("POC Studio %s was installed (this session runs %s). Restart Claude Code before POC work: "
                   "type /exit, then open it again." % (inst["to"], inst["from"]))
            ctx = ("POC_STUDIO_UPDATE: a newer POC Studio (%s) was installed; this session still runs %s. "
                   "Open your first reply with this line, in bold: **%s** POC Studio stages are blocked in this "
                   "session until the restart." % (inst["to"], inst["from"], msg))
        else:
            msg = ("POC Studio %s is out of date (latest %s) and could not update itself: %s. %s"
                   % (res["installed"], res["latest"], inst.get("error", "unknown error"), UPDATE_HELP))
            ctx = ("POC_STUDIO_UPDATE: open your first reply with this line, in bold: **%s** POC Studio "
                   "stages are blocked until it is updated." % msg)
    elif res["status"] == "unreachable":
        ctx = ("POC_STUDIO_UPDATE: the POC Studio version check could not reach GitHub (%s). If the person "
               "asks for POC Studio work, say in one line that the check will run again when a stage starts, "
               "and that a stage cannot start until GitHub is reachable (check the internet connection or VPN)."
               % res.get("error", ""))
    out = {}
    if ctx:
        out["hookSpecificOutput"] = {"hookEventName": "SessionStart", "additionalContext": ctx}
    if msg:
        out["systemMessage"] = msg
    if out:
        print(json.dumps(out))


def _deny(reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": reason}}))


def gate():
    h = _hook_input()
    if h.get("tool_name") != "Skill":
        return
    skill = str((h.get("tool_input") or {}).get("skill", "")).strip()
    short = skill.split(":")[-1]
    in_run = os.path.isdir(os.path.join(h.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd(),
                                        ".poc-studio"))
    is_ours = skill.startswith(PLUGIN_NAME + ":") or (":" not in skill and short in STAGE_SKILLS)
    if not ((is_ours and short in STAGE_SKILLS) or (skill in HEADLESS_STAGE_SKILLS and in_run)):
        return
    root = plugin_root()
    remember_root(root)
    res = check(max_age=120)
    if res["status"] == "current":
        return
    if res["status"] == "outdated":
        pending = res.get("pending_restart")
        if pending and vtuple(pending) >= vtuple(res["latest"]):
            how = ("POC Studio %s is already installed, but this session still runs %s. Restart Claude Code "
                   "(type /exit, then open it again) and run the same command; the run resumes from this stage."
                   % (pending, res["installed"]))
        else:
            how = ("A newer POC Studio (%s) is available and this session runs %s. Type /poc-studio:update, "
                   "then restart Claude Code (type /exit, then open it again) and run the same command; the run "
                   "resumes from this stage." % (res["latest"], res["installed"]))
        _deny("POC_STUDIO_UPDATE: do not start this stage. Tell the person, in these words: \"%s\" Then stop; "
              "do not try to work around this check." % how)
        return
    _deny("POC_STUDIO_UPDATE: do not start this stage. Tell the person, in these words: \"POC Studio could not "
          "check for updates because GitHub could not be reached (%s). Check the internet connection or VPN, "
          "then run the same command again; the run resumes from this stage.\" Then stop; do not try to work "
          "around this check." % (res.get("error") or "no response"))


# ---------------------------------------------------------------- main
def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    try:
        if cmd == "check":
            age = int(sys.argv[sys.argv.index("--max-age") + 1]) if "--max-age" in sys.argv else 0
            print(json.dumps(check(age)))
        elif cmd == "install":
            remember_root(plugin_root())
            res = check()
            if res["status"] == "current":
                print(json.dumps({"status": "current", "installed": res["installed"], "latest": res["latest"]}))
            elif res["status"] == "unreachable":
                print(json.dumps({"status": "error", "error": "GitHub could not be reached: " + res["error"]}))
            else:
                print(json.dumps(install()))
        elif cmd == "session-start":
            session_start()
        elif cmd == "gate":
            gate()
        else:
            print(json.dumps({"status": "error", "error": "unknown command " + cmd}))
    except Exception as e:  # a hook must never crash the session
        if cmd == "gate":
            _deny("POC_STUDIO_UPDATE: the POC Studio version check failed (%s). Tell the person and stop." % e)
        elif cmd != "session-start":
            print(json.dumps({"status": "error", "error": str(e)[:400]}))


if __name__ == "__main__":
    main()
