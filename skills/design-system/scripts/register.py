#!/usr/bin/env python3
"""Design system · the register of apps already made, so a new app never looks like an old one.

usage:
  register.py show ["$R"]                          list the entries, one line each
  register.py compare <design-system.html> ["$R"]  compare this file's #fingerprint with every entry
  register.py add <design-system.html> ["$R"]      append this file's fingerprint (after the checks pass)
  register.py extract <design-system.html>         print a fingerprint guessed from an older file with none

The fingerprint is the JSON in <script type="application/json" id="fingerprint"> (SKILL.md Step 7). The register is a
JSON list of fingerprints, each with "client", "app" and "date". It is shared by every run and lives outside the
plugin cache, which an update replaces: $R in SKILL.md ("Locate this skill"), by default
~/.local/poc-studio/design-register.json, the path used when the register argument is left out. A register path that
does not exist yet is seeded from this skill's register/register.json, which is never written to.

compare prints one line per past app with what matches, and a `check:` line (exit 1) when this app repeats a past
app's idea, signature form or home layout, or matches one past app on more than 3 of the 8 visual lines. Entries for the
same client are held only to the first test, and only when the team judged them weak: a client keeps its own look.
"""
import colorsys, datetime, json, os, re, shutil, sys
from collections import Counter

DEFAULT = os.path.join(os.path.expanduser("~"), ".local", "poc-studio", "design-register.json")
SEED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "register", "register.json")


def load(path=None):
    """Read the shared register; on first use, seed it from this skill's copy."""
    path = path or DEFAULT
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        shutil.copyfile(SEED, path)
        print(f"note: seeded the register {path} from {os.path.normpath(SEED)}", file=sys.stderr)
    return json.load(open(path, encoding="utf-8"))

VISUAL = ["nav", "surface", "shape", "font_display", "theme", "density", "imagery", "accent_family"]
STRUCT = ["idea", "signature_form", "home_layout"]
STOP = set("the a an of and to in on with for as its their is are by at from one each every".split())


def fingerprint(html):
    m = re.search(r'<script[^>]*id="fingerprint"[^>]*>(.*?)</script>', html, re.S)
    return json.loads(m.group(1)) if m else None


def words(s):
    return {w for w in re.findall(r"[a-z]+", (s or "").lower()) if w not in STOP and len(w) > 2}


def similar(a, b):
    """Two free-text answers say the same thing when most of their meaningful words are shared."""
    wa, wb = words(a), words(b)
    if not wa or not wb: return False
    return len(wa & wb) / min(len(wa), len(wb)) >= 0.6


def hue_family(h):
    if h is None or h == "": return ""
    try: h = float(h)
    except (TypeError, ValueError): return str(h)
    if h < 0: return "achromatic"
    for name, a, b in (("red", 345, 15), ("orange", 15, 45), ("yellow", 45, 70), ("green", 70, 165),
                       ("cyan", 165, 200), ("blue", 200, 255), ("purple", 255, 300), ("pink", 300, 345)):
        if (a > b and (h >= a or h < b)) or a <= h < b: return name
    return ""


def flat(fp):
    f = dict(fp)
    fonts = fp.get("fonts") or {}
    f["font_display"] = (fonts.get("display") or "").lower() if isinstance(fonts, dict) else ""
    f["accent_family"] = fp.get("accent_family") or hue_family(fp.get("accent_hue"))
    return f


def compare(fp, reg):
    me, errs, lines = flat(fp), [], []
    for e in reg:
        o = flat(e)
        own = (e.get("client") or "").split()[0:1] == (fp.get("client") or "").split()[0:1] and e.get("client")
        # the same client may keep its own brand's look; it must still move away from a run the team judged weak
        same = [] if own else [k for k in VISUAL if me.get(k) and o.get(k) and str(me[k]).lower() == str(o[k]).lower()]
        struct = [k for k in STRUCT if similar(me.get(k), o.get(k))] if (not own or e.get("verdict") == "weak") else []
        lines.append(f"{e.get('client', '?')} · {e.get('app', '?')}: {len(same)}/8 visual lines match ({', '.join(same) or 'none'})"
                     + (f"; repeats its {', '.join(struct)}" if struct else ""))
        if struct: errs.append(f"repeats {e.get('client')} ({e.get('app')}) on {', '.join(struct)}; Phase D must choose another direction")
        if len(same) > 3: errs.append(f"matches {e.get('client')} ({e.get('app')}) on {len(same)} of 8 visual lines ({', '.join(same)}); change at least {len(same) - 3}")
    return lines, errs


def extract(html):
    """A best guess for an older file with no #fingerprint: enough to seed the register. Fill idea and signature by hand."""
    fonts = Counter(f.strip().strip('"\'') for f in re.findall(r"font-family:\s*([^,;}\"']+|\"[^\"]+\"|'[^']+')", html)
                    if "mono" not in f.lower() and "inherit" not in f.lower() and "var(" not in f)
    root = re.search(r"<html([^>]*)>", html)
    attrs = dict(re.findall(r'data-([a-z-]+)="([^"]*)"', root.group(1))) if root else {}
    hexes = Counter(h.upper() for h in re.findall(r"#[0-9a-fA-F]{6}\b", html))
    hue = None
    for h, _ in hexes.most_common(60):
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
        hh, l, s = colorsys.rgb_to_hls(r, g, b)
        if s > .35 and .2 < l < .75: hue = round(hh * 360); break
    title = re.search(r"<title>(.*?)</title>", html, re.S)
    return {"client": "", "app": (title.group(1).strip() if title else ""), "date": "", "idea": "", "signature_form": "",
            "home_layout": "", "nav": "top bar" if attrs.get("shell") == "top" else ("left rail" if "app-rail" in html else ""),
            "surface": attrs.get("surface", "glass" if html.count("backdrop-filter") > 20 else ""),
            "shape": "", "fonts": {"display": fonts.most_common(1)[0][0] if fonts else ""}, "theme": attrs.get("theme", ""),
            "density": attrs.get("density", ""), "imagery": "", "accent_hue": hue, "chrome": attrs.get("chrome", "")}


def main(a):
    if not a: sys.exit(__doc__)
    if a[0] == "show":
        for e in load(a[1] if len(a) > 1 else None):
            print(f"{e.get('date', ''):10} {e.get('client', ''):28} {e.get('app', '')[:34]:34} idea: {e.get('idea', '')[:70]}")
        return
    if a[0] == "extract":
        print(json.dumps(extract(open(a[1], encoding="utf-8").read()), indent=2)); return
    if a[0] not in ("compare", "add") or len(a) < 2: sys.exit(__doc__)
    html = open(a[1], encoding="utf-8").read(); fp = fingerprint(html)
    if fp is None: sys.exit("check: no <script type=\"application/json\" id=\"fingerprint\"> in the file (SKILL.md Step 7)")
    path = a[2] if len(a) > 2 else DEFAULT
    reg = load(path)
    if a[0] == "compare":
        lines, errs = compare(fp, [e for e in reg if e.get("client") != fp.get("client") or e.get("app") != fp.get("app")])
        for l in lines: print(l)
        for e in errs: print("check:", e)
        sys.exit(1 if errs else 0)
    if a[0] == "add":
        if os.path.realpath(path) == os.path.realpath(SEED):
            sys.exit(f"check: {path} is the seed inside the plugin, which an update replaces; add to the shared register ($R, {DEFAULT})")
        fp.setdefault("date", datetime.date.today().isoformat())
        reg = [e for e in reg if not (e.get("client") == fp.get("client") and e.get("app") == fp.get("app"))] + [fp]
        json.dump(reg, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        print(f"added {fp.get('client')} · {fp.get('app')}; the register holds {len(reg)} apps")


if __name__ == "__main__":
    main(sys.argv[1:])
