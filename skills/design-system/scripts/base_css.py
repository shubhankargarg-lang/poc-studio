#!/usr/bin/env python3
"""Design system · the base stylesheet, transformed onto the client's colour (Step 0 and Step 3).

usage:
  base_css.py inventory                      list every colour in the core and the kit, grouped by family, with counts
  base_css.py build <map.json> <out.css>     write core + kit, every colour moved to the client's hue at the SAME
                                             relative luminance, and print the before/after counts and each change
  base_css.py device                         print the device script to paste once at the end of <body>

map.json sets each family's new hue (degrees), saturation scale and cap (0..1); a family left out is unchanged:
  {"blue": {"hue": 176, "sat": 0.70, "cap": 0.62},
   "cerise": {"hue": 152, "sat": 0.62, "cap": 0.44},
   "positive": {"hue": 138}, "attention": {"hue": 28}, "negative": {"hue": 6},
   "fixed": {"#0033A1": "#0B4F4A"}}
"fixed" pins exact values (the sampled swatch, for example) and wins over the family rule.
Saturation is chosen; lightness is searched (SKILL.md Step 3). Colours under saturation .06 are left alone.
"""
import colorsys, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")
HEX = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
RGB = re.compile(r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})")
BARE = re.compile(r"(--aur-[abc]\s*:\s*)(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})")
FAMILIES = [("negative", 345, 15), ("attention", 15, 60), ("positive", 80, 175), ("blue", 175, 265), ("cerise", 265, 345)]


def _lin(c):
    c /= 255
    return c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4


def Y(rgb):
    r, g, b = rgb
    return .2126 * _lin(r) + .7152 * _lin(g) + .0722 * _lin(b)


def hsl_rgb(h, s, l):
    return tuple(round(v * 255) for v in colorsys.hls_to_rgb(h, l, s))


def reskin(rgb, hue, sat):
    target, lo, hi = Y(rgb), 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if Y(hsl_rgb(hue, sat, mid)) < target: lo = mid
        else: hi = mid
    return hsl_rgb(hue, sat, (lo + hi) / 2)


def family(rgb):
    h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in rgb))
    if s < .06 or l > .97 or l < .03: return "neutral"
    deg = h * 360
    for name, a, b in FAMILIES:
        if (a > b and (deg >= a or deg < b)) or (a <= deg < b): return name
    return "other"


def to_hex(rgb): return "#%02X%02X%02X" % rgb


def from_hex(h):
    h = h.lstrip("#")
    if len(h) == 3: h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def load():
    return open(os.path.join(ASSETS, "core.css")).read(), open(os.path.join(ASSETS, "kit.css")).read()


def colours(css):
    out = [from_hex(m.group(0)) for m in HEX.finditer(css)]
    out += [tuple(int(g) for g in m.groups()) for m in RGB.finditer(css)]
    out += [tuple(int(g) for g in m.groups()[1:]) for m in BARE.finditer(css)]
    return out


def counts(css):
    return {"hexes": len(set(m.group(0).upper() for m in HEX.finditer(css))),
            "rgb triples": len(set(m.groups() for m in RGB.finditer(css))),
            "bare --aur triples": len(BARE.findall(css))}


def inventory():
    core, kit = load()
    for name, css in (("core", core), ("kit", kit)):
        print(f"{name}: {counts(css)}")
    fam = {}
    for c in colours(core + kit): fam.setdefault(family(c), set()).add(to_hex(c))
    for k in sorted(fam):
        print(f"  {k:10} {len(fam[k]):3}  " + " ".join(sorted(fam[k])[:14]) + (" …" if len(fam[k]) > 14 else ""))


def build(map_path, out_path):
    m = json.load(open(map_path))
    fixed = {k.upper(): v for k, v in (m.get("fixed") or {}).items()}
    changes = {}

    def move(rgb):
        hx = to_hex(rgb)
        if hx in fixed: new = from_hex(fixed[hx])
        else:
            f = family(rgb); rule = m.get(f)
            if not rule: return rgb
            h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in rgb))
            sat = min(s * rule.get("sat", 1.0), rule.get("cap", 1.0))
            new = reskin(rgb, (rule["hue"] % 360) / 360, sat)
        if new != rgb: changes[hx] = (to_hex(new), round(Y(rgb), 4), round(Y(new), 4))
        return new

    core, kit = load()
    css = core + "\n" + kit
    before = counts(css)
    css = HEX.sub(lambda x: to_hex(move(from_hex(x.group(0)))), css)
    css = RGB.sub(lambda x: x.group(0).split("(")[0] + "(" + ",".join(str(v) for v in move(tuple(int(g) for g in x.groups()))), css)
    css = BARE.sub(lambda x: x.group(1) + ",".join(str(v) for v in move(tuple(int(g) for g in x.groups()[1:]))), css)
    open(out_path, "w").write(css)
    after = counts(css)
    print(f"before {before}\nafter  {after}")
    worst = max((abs(a - b) for _, a, b in changes.values()), default=0)
    print(f"{len(changes)} colours moved · max |ΔY| {worst:.4f} (put this in the port note)")
    for k, (v, a, b) in sorted(changes.items()): print(f"  {k} → {v}   Y {a} → {b}")
    if before != after: print("check: the colour counts changed; two colours merged into one value. Fine if intended, otherwise adjust the map")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["inventory"]: inventory()
    elif a[:1] == ["build"] and len(a) == 3: build(a[1], a[2])
    elif a[:1] == ["device"]: print(open(os.path.join(ASSETS, "device.js")).read())
    else: sys.exit(__doc__)
