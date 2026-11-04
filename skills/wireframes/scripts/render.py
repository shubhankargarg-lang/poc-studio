#!/usr/bin/env python3
"""POC Studio · wireframes: render low-fidelity wireframes from a JSON layout spec straight to PNG (no browser, no HTML).

usage: render.py <spec.json> <out_dir>
writes: <out_dir>/png/<page-id>.png (one per page), <out_dir>/<slug>-wireframes.pdf (all pages),
        <out_dir>/wireframe-manifest.json (the closed component list the design system builds from)
"""
import json, os, random, re, sys
from collections import OrderedDict
from PIL import Image, ImageDraw, ImageFont

# ---------- look: greys only, one font, fixed sizes ----------
BG, PANEL, LINE, FILL, FILL2, INK, MUTED, DARK = "#f3f3f1", "#ffffff", "#c4c4bf", "#e7e7e3", "#d6d6d1", "#2f2f2d", "#8a8a85", "#4a4a47"
HERE = os.path.dirname(os.path.abspath(__file__))
def _font(names, size):
    for n in names:
        for p in (os.path.join(HERE, "..", "assets", n), f"/usr/share/fonts/opentype/inter/{n}",
                  f"/usr/share/fonts/truetype/dejavu/{n}", f"/Library/Fonts/{n}", os.path.expanduser(f"~/Library/Fonts/{n}")):
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default(size)
REG = lambda s: _font(["Inter-Regular.otf", "Inter-Regular.ttf"], s)
BOLD = lambda s: _font(["Inter-SemiBold.otf", "Inter-SemiBold.ttf"], s)
MONO = lambda s: _font(["IBMPlexMono-Regular.ttf", "DejaVuSansMono.ttf", "Menlo.ttc"], s)

GAP, PAD = 16, 24
AGENT = ["AI"]  # the agent's short name, from app.agent (set in main)

RENDER_ISSUES = []
class Canvas:
    def __init__(self, w, h):
        self.im = Image.new("RGB", (w, h), BG); self.d = ImageDraw.Draw(self.im, "RGBA"); self.cur = None; self.texts = []; self.blocks = {}
    def box(self, x, y, w, h, fill=PANEL, line=LINE, r=8, width=1):
        self.d.rounded_rectangle([x, y, x + w, y + h], r, fill=fill, outline=line, width=width)
    def text(self, x, y, s, f=None, fill=INK, anchor="la"):
        self.d.text((x, y), str(s), font=f or REG(13), fill=fill, anchor=anchor)
        if self.cur and str(s).strip():  # v4.10 · remember where each text landed, for the sloppiness check
            self.texts.append((self.d.textbbox((x, y), str(s), font=f or REG(13), anchor=anchor), self.cur, str(s)[:40]))
    def sloppy(self, page_id):
        """Text that spills out of its block, or sits on other text: the first thing a reviewer calls sloppy."""
        out, seen = [], set()
        for (bx0, by0, bx1, by1), (x, y, w, h, bid), s in self.texts:
            if bx1 > x + w + 2 or by1 > y + h + 2 or bx0 < x - 2:
                k = (bid, "spill")
                if k not in seen: seen.add(k); out.append(f"{page_id}/{bid}: '{s}' runs outside its block; shorten it, wrap it or give the block room")
        T = sorted(self.texts, key=lambda t: t[0][1])
        for i, (a, ab, sa) in enumerate(T):
            for (b_, bb, sb) in T[i + 1:]:
                if b_[1] >= a[3]: break
                if min(a[2], b_[2]) - max(a[0], b_[0]) > 3 and min(a[3], b_[3]) - max(a[1], b_[1]) > 3:
                    k = (ab[4], bb[4], "overlap")
                    if k not in seen: seen.add(k); out.append(f"{page_id}/{ab[4]}: '{sa}' overlaps '{sb}'; move or shorten one")
        # a big block mostly empty: wasted space reads as unfinished
        bottoms = {}
        for (bx0, by0, bx1, by1), (x, y, w, h, bid), s in self.texts: bottoms[bid] = max(bottoms.get(bid, 0), by1)
        for bid, (x, y, w, h, typ) in self.blocks.items():
            if typ in ("slot", "media", "chart", "board", "calendar", "graph", "map", "stack") or h < 300 or bid not in bottoms: continue
            if bottoms[bid] - y < 0.5 * h: out.append(f"{page_id}/{bid}: the block is {int(h)} px tall but its content ends after {int(bottoms[bid] - y)} px; size it to its content or give it the content it needs")
        return out
    def tw(self, s, f): return self.d.textlength(str(s), font=f)
    def bar(self, x, y, w, h=8, fill=FILL): self.d.rounded_rectangle([x, y, x + w, y + h], h // 2, fill=fill)
    def pill(self, x, y, s, solid=False, f=None):
        f = f or REG(11); w = self.tw(s, f) + 16
        self.d.rounded_rectangle([x, y, x + w, y + 20], 10, fill=DARK if solid else PANEL, outline=DARK if solid else LINE)
        self.text(x + 8, y + 10, s, f, PANEL if solid else DARK, "lm"); return w
    def button(self, x, y, s, primary=False, disabled=False):
        f = BOLD(12); w = self.tw(s, f) + 28
        if disabled:  # v4.10 · a blocked action looks blocked
            self.d.rounded_rectangle([x, y, x + w, y + 32], 6, fill=FILL, outline=LINE); self.text(x + w / 2, y + 16, s, f, MUTED, "mm"); return w
        self.d.rounded_rectangle([x, y, x + w, y + 32], 6, fill=DARK if primary else PANEL, outline=DARK if primary else LINE)
        self.text(x + w / 2, y + 16, s, f, PANEL if primary else INK, "mm"); return w
    def tag(self, x, y, w, h, b):
        s = f"{b.get('id', '')} · {b['type'] if not b.get('component') else b['component']}".strip(" ·")
        f = MONO(9); tw = self.tw(s, f)
        self.d.rectangle([x + w - tw - 12, y + h - 18, x + w - 4, y + h - 4], fill=(255, 255, 255, 230))
        self.text(x + w - 8, y + h - 11, s, f, MUTED, "rm")

def wrap(c, s, f, width):
    words, lines, cur = str(s).split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if c.tw(t, f) <= width: cur = t
        else: lines.append(cur); cur = wd
    return lines + ([cur] if cur else [])

def pic(c, x, y, w, h):
    """A picture: the hero object's image (a product, a shot, a scan, a site photo). Grey box with a mountain glyph."""
    c.box(x, y, w, h, FILL2, None, 4)
    c.d.line([(x + 3, y + h - 3), (x + w * .4, y + h * .45), (x + w * .6, y + h * .7), (x + w - 3, y + h * .3)], fill=MUTED, width=1)
def title(c, x, y, b):
    if b.get("title"): c.text(x + 16, y + 16, b["title"], BOLD(13))
    if b.get("views") and b.get("_w"):  # v4.9 · the ways to look at the same items, as a switch on the block's title row
        names = [v["name"] if isinstance(v, dict) else v for v in b["views"]]
        f = MONO(10); ws = [c.tw(v.upper(), f) + 20 for v in names]; tw = sum(ws) + 6; vx = x + b["_w"] - tw - 14; act = b.get("view", names[0])
        c.box(vx, y + 4, tw, 24, FILL, None, 12); cx = vx + 3
        for v, wv in zip(names, ws):
            if v == act: c.box(cx, y + 6, wv, 20, PANEL, LINE, 10)
            c.text(cx + wv / 2, y + 16, v.upper(), f, INK if v == act else MUTED, "mm"); cx += wv
    return 44 if b.get("title") or b.get("views") else 16

# ---------- blocks ----------
def b_header(c, x, y, w, h, b):
    if b.get("breadcrumb"): c.text(x, y + 2, " / ".join(b["breadcrumb"]), REG(12), MUTED)
    c.text(x, y + (22 if b.get("breadcrumb") else 6), b["title"], BOLD(22))
    if b.get("subtitle"): c.text(x, y + (52 if b.get("breadcrumb") else 38), b["subtitle"], REG(13), MUTED)
    bx = x + w
    for i, a in enumerate(reversed(b.get("actions", []))):
        f = BOLD(12); bw = c.tw(a, f) + 28; bx -= bw; c.button(bx, y + 8, a, primary=(i == 0)); bx -= 8
def b_filters(c, x, y, w, h, b):
    if b.get("search", True):
        c.box(x, y + 4, 260, 34, PANEL, LINE, 6); c.text(x + 30, y + 21, b.get("search_label", "Search"), REG(12), MUTED, "lm")
        c.d.ellipse([x + 11, y + 15, x + 21, y + 25], outline=MUTED, width=2); fx = x + 272
    else: fx = x
    for chip in b.get("chips", []):
        f = REG(12); cw = c.tw(chip, f) + 34
        c.box(fx, y + 4, cw, 34, PANEL, LINE, 17); c.text(fx + 14, y + 21, chip, f, INK, "lm")
        c.d.polygon([(fx + cw - 16, y + 18), (fx + cw - 10, y + 18), (fx + cw - 13, y + 23)], fill=MUTED); fx += cw + 8
def b_kpi(c, x, y, w, h, b):
    c.box(x, y, w, h); c.text(x + 16, y + 16, b["label"], REG(12), MUTED)
    c.text(x + 16, y + 38, b["value"], BOLD(26))
    if b.get("delta"): c.text(x + 16, y + h - 26, b["delta"], REG(11), MUTED)
    c.d.line([(x + w - 90, y + h - 26), (x + w - 70, y + h - 34), (x + w - 50, y + h - 30), (x + w - 30, y + h - 42), (x + w - 16, y + h - 38)], fill=FILL2, width=2)
def b_chart(c, x, y, w, h, b):
    c.box(x, y, w, h); t = title(c, x, y, b); ix, iy, iw, ih = x + 16, y + t + 4, w - 32, h - t - 40
    c.d.line([(ix, iy), (ix, iy + ih), (ix + iw, iy + ih)], fill=LINE)
    rnd = random.Random(b.get("id", "c")); kind = b.get("kind", "line")
    if kind == "bar":
        n = 8; bw = iw / n * .55
        for i in range(n):
            bh = ih * rnd.uniform(.25, .95); bx = ix + iw / n * i + 10
            c.d.rectangle([bx, iy + ih - bh, bx + bw, iy + ih], fill=FILL2)
    elif kind == "donut":
        r = min(iw, ih) / 2 - 4; cx, cy = ix + iw / 2, iy + ih / 2; a = -90
        for frac, col in ((.55, DARK), (.3, FILL2), (.15, FILL)):
            c.d.pieslice([cx - r, cy - r, cx + r, cy + r], a, a + 360 * frac, fill=col); a += 360 * frac
        c.d.ellipse([cx - r * .6, cy - r * .6, cx + r * .6, cy + r * .6], fill=PANEL)
    else:
        for k, col in ((0, DARK), (1, FILL2)):
            pts = [(ix + iw / 9 * i, iy + ih * rnd.uniform(.15 + .2 * k, .8)) for i in range(10)]
            c.d.line(pts, fill=col, width=2)
    if b.get("caption"): c.text(x + 16, y + h - 20, b["caption"], REG(11), MUTED)
def b_table(c, x, y, w, h, b):
    c.box(x, y, w, h); t = title(c, x, y, b)
    if b.get("bulk"):
        bx = x + w - 16
        for a in reversed(b["bulk"]):
            f = BOLD(12); bw = c.tw(a, f) + 28; bx -= bw; c.button(bx, y + 8, a, a == b["bulk"][-1]); bx -= 8
    th_ = 34 if b.get("thumb") else 0
    cols = b["columns"]; cx0 = x + 16 + (28 if b.get("select") else 0) + th_; cw = (w - 32 - (28 if b.get("select") else 0) - th_) / len(cols)
    hy = y + t + 2; c.d.rectangle([x + 1, hy, x + w - 1, hy + 30], fill=FILL)
    for i, col in enumerate(cols): c.text(cx0 + cw * i, hy + 15, col, BOLD(11), DARK, "lm")
    rnd = random.Random(b.get("id", "t")); ry = hy + 30; rh = 36
    statuses = b.get("statuses", ["Critical", "Low", "OK"])
    for k, row in enumerate(b.get("rows") or []):  # real rows first, in the person's words
        if ry + rh > y + h - 8: break
        if k == b.get("selected"): c.d.rectangle([x + 1, ry, x + w - 1, ry + rh], fill=FILL)
        c.d.line([(x + 1, ry + rh), (x + w - 1, ry + rh)], fill=FILL)
        if b.get("select"):
            ticked = b.get("checked") == "all" or k in (b.get("checked") or [])
            c.box(x + 16, ry + 11, 14, 14, DARK if ticked else PANEL, DARK if ticked else LINE, 3)
            if ticked: c.d.line([(x + 19, ry + 18), (x + 22, ry + 21), (x + 27, ry + 14)], fill=PANEL, width=2)
        if th_: pic(c, cx0 - th_, ry + 4, 28, rh - 8)
        for i, col in enumerate(cols):
            v = str(row[i]) if i < len(row) else ""
            px = cx0 + cw * i
            if col == b.get("status_col") and v: c.pill(px, ry + 8, v, solid=False)
            elif col == b.get("action_col"): c.text(px, ry + rh / 2, v or "Open  ›", REG(12), DARK, "lm")
            else:
                f = BOLD(12) if i == 0 else REG(12)
                while v and c.tw(v, f) > cw - 12: v = v[:-2].rstrip() + "…" if not v.endswith("…") else v[:-2] + "…"
                c.text(px, ry + rh / 2, v, f, INK if i == 0 else DARK, "lm")
        ry += rh
    while ry + rh <= y + h - 8:
        c.d.line([(x + 1, ry + rh), (x + w - 1, ry + rh)], fill=FILL)
        if b.get("select"): c.box(x + 16, ry + 11, 14, 14, PANEL, LINE, 3)
        for i, col in enumerate(cols):
            px = cx0 + cw * i
            if col == b.get("status_col"): c.pill(px, ry + 8, rnd.choice(statuses), solid=False)
            elif col == b.get("action_col"): c.text(px, ry + rh / 2, "Open  ›", REG(12), DARK, "lm")
            else: c.bar(px, ry + 14, min(cw - 20, rnd.uniform(.35, .8) * cw))
        ry += rh
    if b.get("paging", True) and h > 160: c.text(x + w - 16, y + h - 4, "", REG(1))
def b_list(c, x, y, w, h, b):
    c.box(x, y, w, h); t = title(c, x, y, b); iy = y + t
    for it in b.get("items", []):
        if iy + 56 > y + h - 8: break
        lx = x + 16
        if b.get("thumb"): pic(c, lx, iy + 4, 44, 44); lx += 54
        c.text(lx, iy + 10, it["title"], BOLD(12)); c.text(lx, iy + 30, it.get("meta", ""), REG(11), MUTED)
        if it.get("status"):
            f = REG(11); c.pill(x + w - 16 - c.tw(it["status"], f) - 16, iy + 12, it["status"])
        c.d.line([(x + 16, iy + 54), (x + w - 16, iy + 54)], fill=FILL); iy += 58
def b_tabs(c, x, y, w, h, b):
    tx = x
    for i, t in enumerate(b["items"]):
        f = BOLD(13) if i == b.get("active", 0) else REG(13); tw = c.tw(t, f)
        c.text(tx, y + 14, t, f, INK if i == b.get("active", 0) else MUTED)
        if i == b.get("active", 0): c.d.rectangle([tx, y + 36, tx + tw, y + 38], fill=DARK)
        tx += tw + 28
    c.d.line([(x, y + 38), (x + w, y + 38)], fill=LINE)
def b_form(c, x, y, w, h, b):
    c.box(x, y, w, h); iy = y + title(c, x, y, b)
    for fd in b.get("fields", []):
        c.text(x + 16, iy, fd["label"], BOLD(11), DARK); kind = fd.get("kind", "text"); fh = 64 if kind in ("textarea", "photo") else 36
        if kind == "photo":
            c.d.rounded_rectangle([x + 16, iy + 18, x + w - 16, iy + 18 + fh], 6, outline=MUTED, width=2, fill=FILL)
            cx3, cy3 = x + w / 2 - 50, iy + 18 + fh / 2; c.d.rounded_rectangle([cx3 - 12, cy3 - 8, cx3 + 12, cy3 + 9], 3, outline=DARK, width=2); c.d.ellipse([cx3 - 5, cy3 - 4, cx3 + 5, cy3 + 6], outline=DARK, width=2); c.text(cx3 + 22, cy3, "Take photo", BOLD(12), DARK, "lm")
        else:
            c.box(x + 16, iy + 18, w - 32, fh, PANEL, LINE, 6)
            if fd.get("value"): c.text(x + 28, iy + 36, fd["value"], REG(12), INK, "lm")
            else: c.bar(x + 28, iy + 32, (w - 32) * .35)
            if kind == "select": c.d.polygon([(x + w - 38, iy + 32), (x + w - 28, iy + 32), (x + w - 33, iy + 39)], fill=MUTED)
            if kind == "number": c.text(x + w - 30, iy + 36, "−   +", BOLD(13), DARK, "rm")
        iy += fh + 34
    if b.get("submit"):
        if b.get("submit_full"): c.d.rounded_rectangle([x + 16, y + h - 70, x + w - 16, y + h - 26], 8, fill=DARK); c.text(x + w / 2, y + h - 48, b["submit"], BOLD(14), PANEL, "mm")
        else: c.button(x + 16, y + h - 48, b["submit"], True)
def b_card(c, x, y, w, h, b):
    c.box(x, y, w, h); iy = y + title(c, x, y, b)
    for l in b.get("lines", []):
        for ln in wrap(c, l, REG(12), w - 32): c.text(x + 16, iy, ln, REG(12), DARK); iy += 18
        iy += 6
    if b.get("action"): c.button(x + 16, y + h - 48, b["action"], True)
def b_timeline(c, x, y, w, h, b):
    c.box(x, y, w, h); iy = y + title(c, x, y, b)
    for i, it in enumerate(b.get("items", [])):
        if iy + 44 > y + h: break
        c.d.ellipse([x + 18, iy + 4, x + 28, iy + 14], fill=DARK if i == 0 else PANEL, outline=DARK, width=2)
        c.text(x + 40, iy + 2, it, REG(12), INK); c.text(x + 40, iy + 20, "", REG(10)); iy += 40
BLOCKS = dict(header=b_header, filters=b_filters, kpi=b_kpi, chart=b_chart, table=b_table, list=b_list,
              tabs=b_tabs, form=b_form, card=b_card, timeline=b_timeline)
NO_TAG = {"header", "filters", "tabs"}

# ---------- overlays ----------
def o_drawer(c, W, H, top, b):
    c.d.rectangle([0, 0, W, H], fill=(30, 30, 28, 60)); w = b.get("width", 400); x = W - w
    c.d.rectangle([x, top, W, H], fill=PANEL, outline=DARK); c.text(x + 20, top + 22, b["title"], BOLD(15))
    c.d.line([(W - 34, top + 22), (W - 24, top + 32)], fill=MUTED, width=2); c.d.line([(W - 34, top + 32), (W - 24, top + 22)], fill=MUTED, width=2); iy = top + 64
    for m in b.get("messages", []):
        f = REG(12); lines = wrap(c, m["text"], f, w - 90); bh = 18 * len(lines) + 20
        user = m.get("from") == "user"; bw = min(w - 60, max(c.tw(l, f) for l in lines) + 28)
        bx = W - 20 - bw if user else x + 20
        c.box(bx, iy, bw, bh, FILL if user else PANEL, LINE if not user else FILL, 10)
        for i, l in enumerate(lines): c.text(bx + 14, iy + 10 + i * 18, l, f, INK)
        iy += bh + 10
        cx = x + 20
        for ch in m.get("chips", []): cx += c.pill(cx, iy, ch) + 6
        if m.get("chips"): iy += 30
        if m.get("card"):
            c.box(x + 20, iy, w - 40, 76, PANEL, DARK, 8, 2); c.text(x + 34, iy + 14, m["card"], BOLD(12))
            c.button(x + 34, iy + 36, "Approve", True); c.button(x + 140, iy + 36, "Edit"); iy += 88
    if b.get("blocks"): iy = stack(c, x + 20, iy, w - 40, b["blocks"])
    if b.get("messages") or b.get("input"):
        c.box(x + 16, H - 64, w - 32, 44, PANEL, LINE, 22); c.text(x + 34, H - 42, b.get("input", "Ask a question…"), REG(12), MUTED, "lm")
    elif b.get("actions"):
        bx = W - 20
        for i, a in enumerate(reversed(b["actions"])):
            bw = c.tw(a, BOLD(12)) + 28; bx -= bw; c.button(bx, H - 56, a, i == 0); bx -= 8
    c.tag(x, top, w, H - top - 70, b)
def o_modal(c, W, H, top, b):
    c.d.rectangle([0, 0, W, H], fill=(30, 30, 28, 70)); w = b.get("width", 460)
    body = wrap(c, b.get("body", ""), REG(13), w - 48)
    inner = sum(k.get("h", 100) + k.get("gap", 12) for k in b.get("blocks", []))
    h = b.get("height") or (60 + 20 * len(body) + (inner + 12 if inner else 0) + 80)
    h = min(h, H - top - 24); x, y = (W - w) / 2, max(top + 12, (H - h) / 2); c.box(x, y, w, h, PANEL, DARK, 10, 2)
    c.text(x + 24, y + 24, b["title"], BOLD(16)); iy = y + 60
    for ln in body: c.text(x + 24, iy, ln, REG(13), DARK); iy += 20
    if b.get("blocks"): stack(c, x + 24, iy + 8, w - 48, b["blocks"])
    bx = x + w - 24
    for i, a in enumerate(reversed(b.get("actions", ["Cancel", "Confirm"]))):
        f = BOLD(12); bw = c.tw(a, f) + 28; bx -= bw; c.button(bx, y + h - 56, a, i == 0); bx -= 8
    c.tag(x, y, w, h, b)
OVERLAYS = dict(drawer=o_drawer, modal=o_modal)

# ---------- shells ----------
def shell_desktop(c, W, H, app, page):
    nav_w = 220; c.d.rectangle([0, 0, nav_w, H], fill=PANEL); c.d.line([(nav_w, 0), (nav_w, H)], fill=LINE)
    c.box(20, 18, 28, 28, FILL2, None, 6); c.text(58, 32, app["name"], BOLD(14), INK, "lm")
    for i, item in enumerate(app["nav"]):
        y = 84 + i * 40; active = item == page.get("nav_active")
        if active: c.d.rounded_rectangle([12, y - 4, nav_w - 12, y + 30], 6, fill=FILL)
        c.d.rounded_rectangle([24, y + 5, 40, y + 21], 4, fill=DARK if active else FILL2)
        c.text(52, y + 13, item, BOLD(13) if active else REG(13), INK if active else DARK, "lm")
    c.d.rectangle([nav_w + 1, 0, W, 56], fill=PANEL); c.d.line([(nav_w, 56), (W, 56)], fill=LINE)
    c.box(nav_w + 24, 12, 320, 32, BG, LINE, 6); c.text(nav_w + 40, 28, app.get("search_label", "Search"), REG(12), MUTED, "lm")
    c.d.ellipse([W - 52, 12, W - 20, 44], fill=FILL2); c.d.ellipse([W - 96, 18, W - 76, 38], outline=MUTED, width=2)
    return nav_w + PAD, 56 + PAD, W - nav_w - 2 * PAD, 56
def shell_phone(c, W, H, app, page):
    c.d.rectangle([0, 0, W, 56], fill=PANEL); c.d.line([(0, 56), (W, 56)], fill=LINE)
    c.text(16, 28, "‹", BOLD(20), INK, "lm"); c.text(W / 2, 28, page["title"], BOLD(15), INK, "mm")
    tabs = app.get("phone_tabs", app["nav"][:4]); tw = W / len(tabs)
    c.d.rectangle([0, H - 64, W, H], fill=PANEL); c.d.line([(0, H - 64), (W, H - 64)], fill=LINE)
    for i, t in enumerate(tabs):
        active = t == page.get("nav_active"); cx = tw * i + tw / 2
        c.d.rounded_rectangle([cx - 10, H - 52, cx + 10, H - 32], 5, fill=DARK if active else FILL2)
        c.text(cx, H - 18, t, BOLD(10) if active else REG(10), INK if active else MUTED, "mm")
    return 16, 56 + 16, W - 32, 56


# ---------- more blocks (map-console apps) ----------
def b_label(c, x, y, w, h, b):
    c.text(x, y + h / 2, b["text"].upper(), MONO(11), MUTED, "lm")
def b_insight(c, x, y, w, h, b):
    c.box(x, y, w, h, PANEL, DARK if b.get("active") else LINE, 8, 2 if b.get("active") else 1)
    lx = x + 16
    if b.get("warn"): c.d.polygon([(lx, y + 26), (lx + 6, y + 15), (lx + 12, y + 26)], outline=DARK, width=2); lx += 20
    if b.get("ai"): c.box(lx, y + 13, 16, 16, FILL2, None, 3); c.text(lx + 8, y + 21, AGENT[0][:2].upper(), BOLD(7), INK, "mm"); lx += 22
    for ln in wrap(c, b["label"].upper(), MONO(11), w - (lx - x) - 40)[:2]: c.text(lx, y + 20, ln, MONO(11), DARK, "lm"); y += 15
    y -= 15 * min(2, len(wrap(c, b["label"].upper(), MONO(11), w - (lx - x) - 40)))
    c.text(x + w - 18, y + 20, "↗", BOLD(13), MUTED, "mm")
    nl = len(wrap(c, b["label"].upper(), MONO(11), w - (lx - x) - 40)[:2]); vy = y + 22 + 15 * nl + 8
    vf = BOLD(26); c.text(x + 16, vy, b["value"], vf, INK, "lt")
    if b.get("of"): c.text(x + 22 + c.tw(b["value"], vf), vy + 9, b["of"], REG(14), MUTED, "lt")
    if b.get("badge"): c.pill(x + w - 16 - c.tw(b["badge"], REG(11)) - 16, vy + 5, b["badge"])
    by = vy + 40
    if b.get("progress") is not None:
        c.bar(x + 16, by, w - 32, 4, FILL); c.bar(x + 16, by, max(4, (w - 32) * b["progress"]), 4, DARK); by += 12
    if b.get("sub"): c.text(x + 16, by + 6, b["sub"].upper(), MONO(10), MUTED, "lm")
def b_stat(c, x, y, w, h, b):
    c.box(x, y, w, h); lx = x + 22
    if b.get("warn"): c.d.polygon([(lx, y + 32), (lx + 6, y + 21), (lx + 12, y + 32)], outline=DARK, width=2); lx += 20
    c.text(lx, y + 27, b["label"].upper(), MONO(11), DARK, "lm"); c.d.ellipse([lx + c.tw(b["label"].upper(), MONO(11)) + 8, y + 21, lx + c.tw(b["label"].upper(), MONO(11)) + 20, y + 33], outline=MUTED)
    vf = BOLD(34); c.text(x + 22, y + 52, b["value"], vf, INK, "lt")
    if b.get("unit"): c.text(x + 30 + c.tw(b["value"], vf), y + 66, b["unit"], REG(16), DARK, "lt")
    if b.get("delta"): c.pill(x + w - 22 - c.tw(b["delta"], REG(11)) - 16, y + 18, b["delta"])
def b_segmented(c, x, y, w, h, b):
    f = MONO(11); widths = [c.tw(t.upper(), f) + 28 for t in b["items"]]; tw = sum(widths) + 8
    c.box(x, y, tw, h, FILL, None, h // 2); cx = x + 4
    for i, t in enumerate(b["items"]):
        if i == b.get("active", 0): c.box(cx, y + 4, widths[i], h - 8, PANEL, LINE, (h - 8) // 2)
        c.text(cx + widths[i] / 2, y + h / 2, t.upper(), f, INK if i == b.get("active", 0) else MUTED, "mm"); cx += widths[i]
def b_select(c, x, y, w, h, b):
    if b.get("label"): c.text(x, y + 6, b["label"].upper(), MONO(10), DARK, "lm"); y += 18; h -= 18
    c.box(x, y, w, h, FILL if b.get("filled") else PANEL, None if b.get("filled") else LINE, 6)
    c.text(x + 12, y + h / 2, b["value"], REG(13), INK if b.get("strong", True) else MUTED, "lm")
    if b.get("kind", "select") == "select": c.d.polygon([(x + w - 22, y + h / 2 - 3), (x + w - 12, y + h / 2 - 3), (x + w - 17, y + h / 2 + 3)], fill=DARK)
def b_stepper(c, x, y, w, h, b):
    if b.get("label"): c.text(x, y + 6, b["label"].upper(), MONO(10), DARK, "lm"); y += 18; h -= 18
    c.box(x, y, 144, h, PANEL, LINE, 6); c.text(x + 20, y + h / 2, "−", BOLD(14), DARK, "mm"); c.text(x + 72, y + h / 2, b.get("value", "1"), REG(13), INK, "mm"); c.text(x + 124, y + h / 2, "+", BOLD(14), DARK, "mm")
def b_slider(c, x, y, w, h, b):
    c.text(x, y + 6, b["label"].upper(), MONO(10), DARK, "lm"); c.text(x + w, y + 6, b["value"], BOLD(12), INK, "rm")
    c.bar(x, y + 28, w, 6, FILL2); k = b.get("at", .15); c.bar(x, y + 28, w * k, 6, DARK); c.d.ellipse([x + w * k - 8, y + 23, x + w * k + 8, y + 39], fill=PANEL, outline=DARK, width=2)
def b_text(c, x, y, w, h, b):
    f = BOLD(b.get("size", 13)) if b.get("bold") else REG(b.get("size", 13))
    for ln in wrap(c, b["text"], f, w): c.text(x, y, ln, f, INK if b.get("bold") else DARK); y += b.get("size", 13) + 7
def b_button(c, x, y, w, h, b):
    if b.get("full"):
        c.d.rounded_rectangle([x, y, x + w, y + h], 8, fill=FILL if b.get("disabled") else DARK)
        c.text(x + w / 2, y + h / 2, b["text"], BOLD(13), MUTED if b.get("disabled") else PANEL, "mm")
    else: c.button(x, y, b["text"], b.get("primary", True), disabled=bool(b.get("disabled")))
def b_tiles(c, x, y, w, h, b):
    n = len(b["items"]); tw = (w - 8 * (n - 1)) / n
    for i, it in enumerate(b["items"]):
        tx = x + i * (tw + 8); act = i == b.get("active", 0)
        c.box(tx, y, tw, h, PANEL if act else FILL, LINE if act else None, 6)
        lf = REG(10 if n > 3 else 11); lab = it[0]
        while c.tw(lab, lf) > tw - 14 and len(lab) > 3: lab = lab[:-2] + "…"
        c.text(tx + 8, y + 14, lab, lf, DARK); c.text(tx + 8, y + 34, it[1], BOLD(14 if n > 3 else 15), INK)
def b_move(c, x, y, w, h, b):
    c.box(x, y, w, h); c.text(x + 16, y + 20, b.get("kind", "Branch request"), BOLD(12), DARK, "lm")
    c.d.ellipse([x + 16, y + 44, x + 26, y + 54], outline=DARK, width=2); c.d.line([(x + 21, y + 56), (x + 21, y + 80)], fill=MUTED, width=2); c.d.ellipse([x + 16, y + 82, x + 26, y + 92], fill=DARK)
    c.text(x + 36, y + 49, b["from"], BOLD(14), INK, "lm"); c.text(x + 36, y + 68, b.get("miles", ""), REG(11), MUTED, "lm"); c.text(x + 36, y + 87, b["to"], BOLD(14), INK, "lm")
    c.text(x + w - 16, y + 50, b.get("value", ""), BOLD(18), INK, "rm"); c.text(x + w - 16, y + 72, b.get("value_label", ""), REG(11), MUTED, "rm")
    c.text(x + 16, y + 116, b.get("detail", "").upper(), MONO(10), DARK, "lm")
    bw = (w - 44) / 2; c.box(x + 16, y + h - 50, bw, 36, PANEL, LINE, 6); c.text(x + 16 + bw / 2, y + h - 32, "Reject", BOLD(13), INK, "mm")
    c.d.rounded_rectangle([x + 28 + bw, y + h - 50, x + w - 16, y + h - 14], 6, fill=DARK); c.text(x + 28 + bw + bw / 2, y + h - 32, "Approve", BOLD(13), PANEL, "mm")
def b_slot(c, x, y, w, h, b):
    """An empty region that names the component the design system will design for it."""
    c.d.rounded_rectangle([x, y, x + w, y + h], 8, fill="#f7f7f5")
    for (x1, y1, x2, y2) in ((x, y, x + w, y), (x, y + h, x + w, y + h), (x, y, x, y + h), (x + w, y, x + w, y + h)):
        n = int(max(abs(x2 - x1), abs(y2 - y1)) // 10)
        for k in range(0, n, 2):
            a, bb = k / n, min(1, (k + 1) / n)
            c.d.line([(x1 + (x2 - x1) * a, y1 + (y2 - y1) * a), (x1 + (x2 - x1) * bb, y1 + (y2 - y1) * bb)], fill=MUTED, width=1)
    name = b.get("component", "component") + (f"  ×{b['count']}" if b.get("count") else "")
    lines = [b["note"]] if b.get("note") else []
    if b.get("variants"): lines.append("variants: " + " · ".join(b["variants"]))
    if b.get("states"): lines.append("states: " + " · ".join(b["states"]))
    th = 22 + 18 * sum(len(wrap(c, l, REG(11), w - 32)) for l in lines); ty = y + max(14, (h - th) / 2)
    if b.get("title"): c.text(x + 14, y + 16, b["title"], BOLD(12), DARK); ty = max(ty, y + 34)
    c.text(x + w / 2, ty + 8, name, MONO(13), INK, "mm"); ty += 26
    for l in lines:
        for ln in wrap(c, l, REG(11), w - 32): c.text(x + w / 2, ty, ln, REG(11), MUTED, "mm"); ty += 18
BLOCKS["slot"] = b_slot
BLOCKS.update(label=b_label, insight=b_insight, stat=b_stat, segmented=b_segmented, select=b_select, stepper=b_stepper,
              slider=b_slider, text=b_text, button=b_button, tiles=b_tiles, move=b_move)
NO_TAG.update({"label", "segmented", "select", "stepper", "slider", "text", "button"})

# ---------- blocks for how the work flows (guided steps, decisions, boards, graphs, the working behind a number) ----------
def b_next(c, x, y, w, h, b):
    """The page's one next step: a banner with one primary action (kind "decision" = the fixed approve bar)."""
    c.box(x, y, w, h, FILL if b.get("kind") != "decision" else PANEL, LINE, 8)
    bx = x + w - 16
    btns = ([b["secondary"]] if b.get("secondary") else []) + ([b["action"]] if b.get("action") else [])
    widths = [c.tw(s, BOLD(12)) + 28 for s in btns]; tx_max = w - 48 - sum(widths) - 8 * len(widths)
    if b.get("kind") == "decision":
        c.text(x + 16, y + h / 2 - (9 if b.get("sub") else 0), b.get("text", ""), BOLD(13), INK, "lm")
        if b.get("sub"): c.text(x + 16, y + h / 2 + 11, b["sub"], REG(11), MUTED, "lm")
    else:
        lx = x + 16; c.text(lx, y + 18, b.get("label", "Next").upper(), MONO(10), DARK, "lm")
        if b.get("ai"): c.pill(lx + c.tw(b.get("label", "Next").upper(), MONO(10)) + 8, y + 8, AGENT[0], f=REG(10))
        iy = y + 34
        for ln in wrap(c, b.get("text", ""), REG(12), tx_max)[:3]: c.text(lx, iy, ln, REG(12), INK); iy += 18
    for i, s in enumerate(reversed(btns)):
        bw = c.tw(s, BOLD(12)) + 28; bx -= bw; c.button(bx, y + h / 2 - 16, s, primary=(i == 0), disabled=(i == 0 and bool(b.get("disabled")))); bx -= 8
def b_steps(c, x, y, w, h, b):
    """Where the person is in the job: numbered steps, done ones ticked."""
    items, act = b["items"], b.get("active", 0); f = REG(12); cx = x; cy = y + h / 2
    for i, t in enumerate(items):
        done, cur = i < act, i == act
        c.d.ellipse([cx, cy - 11, cx + 22, cy + 11], fill=DARK if (done or cur) else PANEL, outline=DARK if (done or cur) else LINE, width=2)
        c.text(cx + 11, cy, "✓" if done else str(i + 1), BOLD(11), PANEL if (done or cur) else MUTED, "mm")
        c.text(cx + 30, cy, t, BOLD(12) if cur else f, INK if (cur or done) else MUTED, "lm"); cx += 30 + c.tw(t, BOLD(12)) + 12
        if i < len(items) - 1: c.d.line([(cx, cy), (cx + 28, cy)], fill=DARK if done else LINE, width=2); cx += 40
def b_chips(c, x, y, w, h, b):
    """Split the work by who has to act (Needs you · In hand · Already done) with counts; the active chip is solid."""
    cx = x
    for i, it in enumerate(b["items"]):
        s = it if isinstance(it, str) else f"{it[0]}  {it[1]}"; f = REG(12); cw = c.tw(s, f) + 28; act = i == b.get("active", 0)
        c.d.rounded_rectangle([cx, y + h / 2 - 15, cx + cw, y + h / 2 + 15], 15, fill=DARK if act else PANEL, outline=DARK if act else LINE)
        c.text(cx + 14, y + h / 2, s, f, PANEL if act else INK, "lm"); cx += cw + 8
    if b.get("right"):
        f = REG(12); rw = c.tw(b["right"], f) + 40; c.box(x + w - rw, y + h / 2 - 16, rw, 32, PANEL, LINE, 6)
        c.text(x + w - rw + 12, y + h / 2, b["right"], f, INK, "lm"); c.d.polygon([(x + w - 22, y + h / 2 - 3), (x + w - 12, y + h / 2 - 3), (x + w - 17, y + h / 2 + 3)], fill=DARK)
def b_options(c, x, y, w, h, b):
    """Options side by side; the recommended one marked; a blocked option shows why and has no choose button."""
    items = b["items"]; n = len(items); cw = (w - 12 * (n - 1)) / n
    for i, it in enumerate(items):
        cx = x + i * (cw + 12); rec, blocked = it.get("state") == "recommended", it.get("state") == "blocked"
        c.box(cx, y, cw, h, PANEL, DARK if rec else LINE, 10, 2 if rec else 1)
        c.text(cx + 16, y + 20, it.get("name", ""), REG(11), MUTED, "lm")
        if it.get("badge"): f = REG(10); c.pill(cx + cw - 16 - c.tw(it["badge"], f) - 16, y + 10, it["badge"], solid=rec, f=f)
        c.text(cx + 16, y + 36, it.get("head", ""), BOLD(24), MUTED if blocked else INK, "lt")
        if it.get("sub"): c.text(cx + 16, y + 70, it["sub"], REG(11), MUTED)
        fy = y + 96; facts = it.get("facts", []); colw = (cw - 32) / 2
        c.box(cx + 12, fy - 6, cw - 24, 34 * ((len(facts) + 1) // 2) + 6, FILL, None, 6)
        for k, (lab, val) in enumerate(facts):
            fx = cx + 20 + (k % 2) * colw; fyy = fy + (k // 2) * 34
            c.text(fx, fyy + 1, lab, REG(10), MUTED); c.text(fx, fyy + 14, val, BOLD(12), INK)
        ny = fy + 34 * ((len(facts) + 1) // 2) + 12
        for ln in wrap(c, it.get("note", ""), REG(11), cw - 32)[:3]: c.text(cx + 16, ny, ln, REG(11), DARK); ny += 16
        if not blocked and b.get("choose"): c.button(cx + 16, y + h - 46, b["choose"], primary=rec)
def b_compare(c, x, y, w, h, b):
    """Options compared row by row; a row given as a string is a section label; `best` marks the recommended column."""
    c.box(x, y, w, h); t = title(c, x, y, b); cols = b["columns"]; lw = w * .3; cw = (w - lw - 16) / len(cols); best = b.get("best")
    hy = y + t
    if best is not None: c.d.rectangle([x + lw + cw * best, hy, x + lw + cw * (best + 1), hy + 28], fill=FILL)
    for i, col in enumerate(cols): c.text(x + lw + cw * i + cw - 12, hy + 14, col, BOLD(12), INK, "rm")
    ry = hy + 32; c.d.line([(x + 1, ry - 4), (x + w - 1, ry - 4)], fill=LINE)
    for r in b.get("rows", []):
        if ry + 24 > y + h - 8: break
        if isinstance(r, str): c.text(x + 16, ry + 10, r.upper(), MONO(10), MUTED, "lm"); ry += 24; continue
        if best is not None: c.d.rectangle([x + lw + cw * best, ry - 3, x + lw + cw * (best + 1), ry + 23], fill=FILL)
        c.text(x + 16, ry + 11, r[0], REG(12), DARK, "lm")
        for i, v in enumerate(r[1:]): c.text(x + lw + cw * i + cw - 12, ry + 11, v, BOLD(12) if i == best else REG(12), INK, "rm")
        c.d.line([(x + 16, ry + 23), (x + w - 16, ry + 23)], fill=FILL); ry += 26
def b_board(c, x, y, w, h, b):
    """Columns of cards that move left to right as the work progresses."""
    cols = b["columns"]; n = len(cols); cw = (w - 12 * (n - 1)) / n
    for i, col in enumerate(cols):
        cx = x + i * (cw + 12); c.box(cx, y, cw, h, FILL, None, 10)
        c.text(cx + 14, y + 20, col["title"], BOLD(12), INK, "lm"); cnt = str(col.get("count", len(col.get("cards", []))))
        c.pill(cx + cw - 14 - c.tw(cnt, REG(11)) - 16, y + 10, cnt)
        cy = y + 40
        if not col.get("cards"):
            c.d.rounded_rectangle([cx + 10, cy, cx + cw - 10, cy + 56], 8, outline=LINE); c.text(cx + cw / 2, cy + 28, col.get("empty", "Nothing here"), REG(11), MUTED, "mm")
        for cd in col.get("cards", []):
            lines = wrap(c, cd["title"], BOLD(12), cw - 40)[:2]; chh = 22 + 17 * len(lines) + (26 if cd.get("tag") else 0) + (20 if cd.get("meta") else 0) + (42 if cd.get("action") else 0)
            if cy + chh > y + h - 8: break
            c.box(cx + 10, cy, cw - 20, chh, PANEL, LINE, 8); iy = cy + 10
            if cd.get("tag"): c.pill(cx + 20, iy, cd["tag"], f=REG(10)); iy += 26
            for ln in lines: c.text(cx + 20, iy, ln, BOLD(12), INK); iy += 17
            if cd.get("meta"): c.text(cx + 20, iy + 2, cd["meta"], REG(11), MUTED); iy += 20
            if cd.get("action"): c.button(cx + 20, iy + 4, cd["action"], True)
            cy += chh + 8
def b_graph(c, x, y, w, h, b):
    """A centre item and the items linked to it on each side, each link labelled with its weight (dashed = weak)."""
    c.box(x, y, w, h); t = title(c, x, y, b); cx, cy = x + w / 2, y + t + (h - t) / 2 - 10; r = 34
    for side, key, tkey in ((-1, "left", "left_title"), (1, "right", "right_title")):
        nodes = b.get(key, []); nx = cx + side * w * .2
        if b.get(tkey): c.text(nx + side * 26, y + t + 4, b[tkey], BOLD(12), DARK, "rm" if side < 0 else "lm")
        for i, nd in enumerate(nodes):
            ny = y + t + 34 + (h - t - 74) * (i + .5) / max(1, len(nodes))
            pts = [(nx - side * 18, ny), (cx - side * r, cy)]
            if nd.get("weak"):
                n = 14
                for k in range(0, n, 2): c.d.line([(pts[0][0] + (pts[1][0] - pts[0][0]) * k / n, pts[0][1] + (pts[1][1] - pts[0][1]) * k / n), (pts[0][0] + (pts[1][0] - pts[0][0]) * (k + 1) / n, pts[0][1] + (pts[1][1] - pts[0][1]) * (k + 1) / n)], fill=MUTED, width=2)
            else: c.d.line(pts, fill=DARK, width=2)
            if nd.get("value"): mx, my = pts[0][0] + (pts[1][0] - pts[0][0]) * .3, pts[0][1] + (pts[1][1] - pts[0][1]) * .3; c.pill(mx - (c.tw(nd["value"], REG(11)) + 16) / 2, my - 10, nd["value"])
            c.d.ellipse([nx - 17, ny - 17, nx + 17, ny + 17], fill=PANEL, outline=DARK, width=2)
            c.text(nx + side * 26, ny, nd["label"], REG(12), INK, "rm" if side < 0 else "lm")
    c.d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=FILL, outline=DARK, width=3)
    lab = b.get("center", ""); lw_ = c.tw(lab, BOLD(12)) + 16; c.box(cx - lw_ / 2, y + h - 52, lw_, 22, PANEL, None, 4); c.text(cx, y + h - 41, lab, BOLD(12), INK, "mm")
    if b.get("caption"): c.text(x + 16, y + h - 18, b["caption"], REG(11), MUTED)
def b_chat(c, x, y, w, h, b):
    """The agent leading the person through a job step by step on the page: progress, messages, quick-reply choices, input."""
    c.box(x, y, w, h); c.text(x + 16, y + 22, b.get("title", AGENT[0]), BOLD(14), INK, "lm")
    if b.get("status"): c.pill(x + w - 16 - c.tw(b["status"], REG(11)) - 16, y + 12, b["status"])
    iy = y + 44
    if b.get("progress"):
        p = b["progress"]; c.text(x + 16, iy + 6, p.get("label", ""), REG(11), DARK, "lm"); n = p.get("of", 6); sx = x + 16 + c.tw(p.get("label", ""), REG(11)) + 12; sw = (x + w - 16 - sx - 4 * (n - 1)) / n
        for k in range(n): c.bar(sx + k * (sw + 4), iy + 3, sw, 5, DARK if k < p.get("at", 1) else FILL2)
        iy += 24
    c.d.line([(x + 1, iy), (x + w - 1, iy)], fill=FILL); iy += 12
    for m in b.get("messages", []):
        f = REG(12); user = m.get("from") == "user"; lines = wrap(c, m["text"], f, w - 80)
        if iy + 18 * len(lines) + 20 > y + h - 70: break
        bw = min(w - 48, max(c.tw(l, f) for l in lines) + 28); bh = 18 * len(lines) + 18 + (26 if m.get("done") else 0)
        bx = x + w - 16 - bw if user else x + 16
        c.box(bx, iy, bw, bh, DARK if user else PANEL, DARK if user else LINE, 10)
        for i, l in enumerate(lines): c.text(bx + 14, iy + 9 + i * 18, l, f, PANEL if user else INK)
        if m.get("done"): c.pill(bx + 14, iy + bh - 28, "✓ " + m["done"], f=REG(10))
        iy += bh + 8; cx = x + 16
        for k, ch in enumerate(m.get("chips", [])):
            cw = c.tw(ch, REG(11)) + 16
            if cx + cw > x + w - 16: cx = x + 16; iy += 26
            c.pill(cx, iy, ch, solid=(k == 0 and m.get("pick")), f=REG(11)); cx += cw + 6
        if m.get("chips"): iy += 30
    c.box(x + 12, y + h - 52, w - 24, 40, PANEL, LINE, 20); c.text(x + 30, y + h - 32, b.get("input", "Ask or change the plan…"), REG(12), MUTED, "lm")
def b_decomp(c, x, y, w, h, b):
    """The working behind the number the person acts on, one line per step, each with a plain explanation."""
    c.box(x, y, w, h); iy = y + title(c, x, y, b)
    for r in b.get("rows", []):
        lab, help_, val = (r + [""] * 3)[:3]; tot = r[-1] == "total" if len(r) > 3 else False
        if iy + 40 > y + h: break
        if tot: c.d.line([(x + 16, iy - 4), (x + w - 16, iy - 4)], fill=DARK, width=2)
        c.text(x + 16, iy + 8, lab, BOLD(12) if tot else REG(12), INK, "lm"); c.text(x + w - 16, iy + 8, val, BOLD(13) if tot else REG(12), INK, "rm")
        if help_: c.text(x + 16, iy + 24, help_, REG(10), MUTED, "lm")
        iy += 40
def b_work(c, x, y, w, h, b):
    """Work items, one card each: what, why, the number to act on, and the actions; done items show no buttons."""
    c.box(x, y, w, h); iy = y + title(c, x, y, b)
    for it in b.get("items", []):
        ih = 70 + (18 if it.get("why") else 0) + (22 if it.get("progress") is not None else 0) + (42 if it.get("actions") else 0)
        if iy + ih > y + h - 6: break
        c.box(x + 16, iy + 4, 36, 36, FILL2, None, 6)
        vw = c.tw(it.get("value", ""), BOLD(18)) + 24 if it.get("value") else 0; ttl = it["title"]
        while c.tw(ttl, BOLD(13)) > w - 78 - vw and len(ttl) > 4: ttl = ttl[:-2].rstrip() + "…"
        c.text(x + 62, iy + 12, ttl, BOLD(13), INK, "lm"); tx = x + 62
        for tg in it.get("tags", []): tx += c.pill(tx, iy + 26, tg, f=REG(10)) + 6
        if it.get("value"): c.text(x + w - 16, iy + 12, it["value"], BOLD(18), INK, "rm"); c.text(x + w - 16, iy + 32, it.get("value_label", ""), REG(10), MUTED, "rm")
        yy = iy + 56
        if it.get("why"): c.text(x + 62, yy, (AGENT[0] + ": " if it.get("ai") else "") + it["why"], REG(11), DARK, "lm"); yy += 18
        if it.get("progress") is not None:
            pw = w - 94 - c.tw(it.get("progress_label", ""), REG(10)) - 16; c.bar(x + 62, yy - 2, pw, 6, FILL); c.bar(x + 62, yy - 2, max(6, pw * it["progress"]), 6, DARK); c.text(x + w - 16, yy + 1, it.get("progress_label", ""), REG(10), MUTED, "rm"); yy += 22
        if it.get("actions"):
            bx = x + 62
            for k, a in enumerate(it["actions"]): bx += c.button(bx, yy, a, primary=(k == 0)) + 8
            c.text(x + w - 16, yy + 16, "Details  ›", REG(12), DARK, "rm")
        c.d.line([(x + 16, iy + ih), (x + w - 16, iy + ih)], fill=FILL); iy += ih + 8
def b_facts(c, x, y, w, h, b):
    """What the agent or the page used, as tiles: label, value, one line, and where it comes from; 'Waiting' until read."""
    c.box(x, y, w, h); t = title(c, x, y, b); items = b.get("items", []); n = b.get("cols", 3); rows_ = (len(items) + n - 1) // n
    tw = (w - 32 - 12 * (n - 1)) / n; th = (h - t - 16 - 12 * (rows_ - 1)) / max(1, rows_)
    for i, it in enumerate(items):
        tx, ty = x + 16 + (i % n) * (tw + 12), y + t + (i // n) * (th + 12); wait = it.get("value") in (None, "", "Waiting")
        c.box(tx, ty, tw, th, FILL if wait else PANEL, None if wait else LINE, 8)
        c.text(tx + 12, ty + 16, it["label"], REG(11), DARK, "lm"); c.text(tx + 12, ty + 40, "Waiting" if wait else it["value"], REG(12) if wait else BOLD(18), MUTED if wait else INK, "lm")
        if it.get("sub") and not wait:
            for k, ln in enumerate(wrap(c, it["sub"], REG(10), tw - 24)[:2]): c.text(tx + 12, ty + 60 + k * 14, ln, REG(10), MUTED, "lm")
        if it.get("source") and not wait: c.text(tx + 12, ty + th - 14, "↗ " + it["source"], REG(10), DARK, "lm")
def b_stack(c, x, y, w, h, b):
    """Blocks one under the other inside one span (an agent column beside a canvas of tabs, tiles and a graph)."""
    outer = c.cur
    for k in b.get("blocks", []):
        kh = k.get("h", 100); k["_w"] = w
        if outer: c.cur = (x, y, w, kh, k.get("id") or k.get("component") or k["type"])
        BLOCKS[k["type"]](c, x, y, w, kh, k); c.cur = outer; k.pop("_w", None)
        if k["type"] not in NO_TAG: c.tag(x, y, w, kh, k)
        y += kh + k.get("gap", 12)
def b_document(c, x, y, w, h, b):
    """A page of a document (invoice, contract, form, scan) with the regions the system read outlined and labelled;
    optional page thumbnails down the left. Regions: at = [x, y, w, h] as fractions of the page."""
    c.box(x, y, w, h); t = title(c, x, y, b); pages = b.get("pages", 0); tx = x + 12
    if pages:
        for i in range(min(pages, 5)):
            c.box(tx, y + t + i * 70, 44, 60, FILL if i else PANEL, DARK if i == b.get("page", 0) else LINE, 3, 2 if i == b.get("page", 0) else 1)
        tx += 56
    px, py, pw, ph = tx + 4, y + t, x + w - tx - 16, h - t - 12; c.box(px, py, pw, ph, "#fbfbf9", LINE, 2)
    rnd = random.Random(b.get("id", "d")); ly = py + 18
    while ly < py + ph - 14:  # the page's text as grey lines
        c.bar(px + 16, ly, pw * rnd.uniform(.35, .85) - 32, 5, FILL2); ly += 13 if rnd.random() > .15 else 22
    for i, r in enumerate(b.get("regions", [])):
        rx, ry, rw, rh = r["at"]; bx, by = px + pw * rx, py + ph * ry; bw, bh_ = pw * rw, ph * rh
        c.d.rounded_rectangle([bx, by, bx + bw, by + bh_], 3, outline=DARK, width=2, fill=(255, 255, 255, 140))
        lab = f"{i + 1} · {r['label']}"; f = BOLD(10); lw_ = c.tw(lab, f) + 12
        c.d.rounded_rectangle([bx, by - 18, bx + lw_, by - 2], 3, fill=DARK); c.text(bx + 6, by - 10, lab, f, PANEL, "lm")
def as_ratio(v, default=16 / 9):
    """A picture's width/height from a number (1.5) or an "a:b" / "a/b" string ("4:5", "16:9"); the default if unreadable."""
    if isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0: return float(v)
    if isinstance(v, str):
        m = re.match(r"^\s*(\d+(?:\.\d+)?)\s*(?:[:/x×]\s*(\d+(?:\.\d+)?))?\s*$", v)
        if m:
            a, b_ = float(m.group(1)), float(m.group(2) or 1)
            if a > 0 and b_ > 0: return a / b_
    return default
def b_media(c, x, y, w, h, b):
    """A grid of pictures (shots, posters, photos, products): each tile has its picture area, caption, meta and tags;
    `selected` thickens one; `ratio` is width/height of the picture."""
    c.box(x, y, w, h); t = title(c, x, y, b); items = b.get("items", []); n = b.get("cols", 3); ratio = as_ratio(b.get("ratio"))
    tw = (w - 32 - 12 * (n - 1)) / n; rows_ = max(1, (len(items) + n - 1) // n); extra = 22 + (18 if any(i.get("meta") for i in items) else 0) + (24 if any(i.get("tags") for i in items) else 0)
    ih = min(tw / ratio, (h - t - 10) / rows_ - extra - 14); th = ih + 22 + (18 if any(i.get("meta") for i in items) else 0) + (24 if any(i.get("tags") for i in items) else 0)
    for i, it in enumerate(items):
        tx, ty = x + 16 + (i % n) * (tw + 12), y + t + (i // n) * (th + 14)
        if ty + th > y + h - 6: break
        sel = it.get("selected"); c.box(tx, ty, tw, ih, FILL2, DARK if sel else None, 6, 3 if sel else 1)
        c.d.line([(tx + 8, ty + ih - 8), (tx + tw * .4, ty + ih * .45), (tx + tw * .6, ty + ih * .7), (tx + tw * .75, ty + ih * .5), (tx + tw - 8, ty + ih - 8)], fill=MUTED, width=2)
        c.d.ellipse([tx + tw * .72, ty + ih * .18, tx + tw * .72 + 14, ty + ih * .18 + 14], outline=MUTED, width=2)
        if it.get("badge"): c.pill(tx + 8, ty + 8, it["badge"], solid=bool(sel), f=REG(10))
        cy = ty + ih + 6; ttl = it.get("title", "")
        while c.tw(ttl, BOLD(12)) > tw and len(ttl) > 4: ttl = ttl[:-2].rstrip() + "…"
        c.text(tx, cy + 6, ttl, BOLD(12), INK, "lm"); cy += 18
        if it.get("meta"): c.text(tx, cy + 4, it["meta"], REG(10), MUTED, "lm"); cy += 18
        gx = tx
        for tg in it.get("tags", []): gx += c.pill(gx, cy, tg, f=REG(10)) + 4
def b_calendar(c, x, y, w, h, b):
    """Time across, things down: columns are days or weeks, each row a person, asset or item, bars span their time.
    A bar: {from, to, label, style: solid|outline|dashed}; `today` draws a line at a column."""
    c.box(x, y, w, h); t = title(c, x, y, b); cols = b.get("columns", []); lw_ = b.get("label_width", 170)
    gx, gw = x + 16 + lw_, w - 32 - lw_; cw = gw / max(1, len(cols)); hy = y + t
    td = b.get("today")
    for i, col in enumerate(cols):
        if td is not None and int(td) == i and float(td) == i: c.pill(gx + cw * i + 1, hy, f"{col} · Today", True, REG(10))  # the heading carries the marker
        else: c.text(gx + cw * i + 6, hy + 10, col, REG(11), DARK, "lm")
        c.d.line([(gx + cw * i, hy + 22), (gx + cw * i, y + h - 10)], fill=FILL)
    rows = b.get("rows", []); rh = min(44, (h - t - 34) / max(1, len(rows))); ry = hy + 26
    for r in rows:
        lx = x + 16
        if b.get("thumb"): pic(c, lx, ry + 4, rh - 8, rh - 8); lx += rh - 2
        lab = r["label"]
        while c.tw(lab, REG(12)) > gx - lx - 8 and len(lab) > 4: lab = lab[:-2].rstrip() + "…"
        c.text(lx, ry + rh / 2, lab, REG(12), INK, "lm"); c.d.line([(x + 16, ry + rh), (x + w - 16, ry + rh)], fill=FILL)
        for bar in r.get("bars", []):
            bx0, bx1 = gx + cw * bar["from"] + 3, gx + cw * bar["to"] - 3; st = bar.get("style", "solid")
            if st == "solid": c.d.rounded_rectangle([bx0, ry + 7, bx1, ry + rh - 7], 4, fill=FILL2, outline=DARK)
            elif st == "outline": c.d.rounded_rectangle([bx0, ry + 7, bx1, ry + rh - 7], 4, fill=PANEL, outline=DARK, width=2)
            else:
                for k in range(int(bx0), int(bx1), 10): c.d.line([(k, ry + 7), (min(k + 5, bx1), ry + 7)], fill=DARK); c.d.line([(k, ry + rh - 7), (min(k + 5, bx1), ry + rh - 7)], fill=DARK)
            if bar.get("label"):  # a label longer than its bar goes after the bar, clear of the today line
                f10 = REG(10); lw_txt = c.tw(bar["label"], f10)
                if lw_txt + 12 <= bx1 - bx0: c.text(bx0 + 6, ry + rh / 2, bar["label"], f10, INK, "lm")
                else:
                    lx = bx1 + 6
                    if td is not None and lx <= gx + cw * td + 2 <= lx + lw_txt: lx = gx + cw * td + 6
                    c.text(lx, ry + rh / 2, bar["label"], f10, INK, "lm")
        ry += rh
    if td is not None:
        tx = gx + cw * td; c.d.line([(tx, hy + 22), (tx, y + h - 10)], fill=DARK, width=2)
        if float(td) != int(td) or int(td) >= len(cols): c.pill(tx + 3, hy + 24, "Today", True, REG(9))  # between columns: below the headings
def b_tree(c, x, y, w, h, b):
    """A hierarchy (sites › areas › assets, folders, an org): indented rows with open/closed markers, meta and status."""
    c.box(x, y, w, h); iy = y + title(c, x, y, b)
    for nd in b.get("items", []):
        if iy + 30 > y + h - 6: break
        d = nd.get("depth", 0); nx = x + 16 + d * 20
        if d: c.d.line([(nx - 12, iy - 6), (nx - 12, iy + 12), (nx - 4, iy + 12)], fill=LINE)
        if nd.get("open") is not None:
            c.d.polygon([(nx, iy + 8), (nx + 8, iy + 8), (nx + 4, iy + 15)] if nd["open"] else [(nx + 1, iy + 6), (nx + 7, iy + 12), (nx + 1, iy + 18)], fill=DARK); nx += 14
        if nd.get("selected"): c.d.rounded_rectangle([x + 8, iy, x + w - 8, iy + 24], 4, fill=FILL)
        c.text(nx, iy + 12, nd["label"], BOLD(12) if nd.get("selected") else REG(12), INK, "lm")
        if nd.get("meta"): c.text(x + w - 16 - (c.tw(nd.get("status", ""), REG(10)) + 26 if nd.get("status") else 0), iy + 12, nd["meta"], REG(11), MUTED, "rm")
        if nd.get("status"): c.pill(x + w - 16 - c.tw(nd["status"], REG(10)) - 16, iy + 2, nd["status"], f=REG(10))
        iy += 28
def b_artefact(c, x, y, w, h, b):
    """v4.10 · the real thing its users know, drawn with its real text (SKILL.md rule 4). layout "product": a picture
    gallery on the left; title, price, bullets and description on the right. layout "page": a page of a document with
    a heading, paragraphs and line items. A `marks` entry {n, field, word, kind: ok|fail|limit} outlines that field
    (solid for fail, dashed for limit, underlined for ok) with its number."""
    c.box(x, y, w, h); t = title(c, x, y, b); lay = b.get("layout", "product"); marks = b.get("marks", [])
    def mark_for(field): return [m for m in marks if m.get("field") == field]
    def draw_mark(mx, my, mw, mh, ms):
        for m in ms:
            k = m.get("kind", "fail")
            if k == "fail": c.d.rectangle([mx - 4, my - 3, mx + mw + 4, my + mh + 3], outline=DARK, width=2)
            elif k == "limit":
                for z in range(int(mx), int(mx + mw), 8): c.d.line([(z, my + mh + 3), (min(z + 4, mx + mw), my + mh + 3)], fill=DARK)
            else: c.d.line([(mx, my + mh + 2), (mx + mw, my + mh + 2)], fill=DARK, width=2)
            c.d.ellipse([mx + mw + 6, my - 4, mx + mw + 22, my + 12], fill=DARK if k == "fail" else PANEL, outline=DARK)
            c.text(mx + mw + 14, my + 4, str(m.get("n", "")), BOLD(9), PANEL if k == "fail" else DARK, "mm")
    if lay == "product":
        gw = min(w * .38, 300); gx, gy = x + 16, y + t; n = b.get("gallery", 4); miss = b.get("missing", 0)
        main = gw - 52; slots = max(1, n + miss); ts = min(40, (main - 6 * (slots - 1)) / slots)  # every thumbnail fits beside the main picture
        pic(c, gx + 52, gy, main, main)
        for i in range(n): pic(c, gx, gy + i * (ts + 6), ts, ts)
        for i in range(miss):
            ty = gy + (n + i) * (ts + 6); c.box(gx, ty, ts, ts, PANEL, LINE, 4); c.text(gx + ts / 2, ty + ts / 2, "due", REG(9), MUTED, "mm")
        tx, tw_ = gx + gw + 16, w - gw - 48; iy = gy
        if b.get("store"): c.text(tx, iy, b["store"], REG(10), MUTED); iy += 18
        lines = wrap(c, b.get("title_text", ""), BOLD(15), tw_ - 30)[:3]; y0 = iy
        for ln in lines: c.text(tx, iy, ln, BOLD(15), INK); iy += 20
        draw_mark(tx, y0, min(tw_ - 30, max(c.tw(l, BOLD(15)) for l in lines) if lines else 10), iy - y0 - 4, mark_for("title"))
        if b.get("price"): iy += 4; c.text(tx, iy, b["price"], BOLD(16), INK); iy += 26
        if b.get("bullets"): c.text(tx, iy, b.get("bullets_head", "About this item"), BOLD(12), INK); iy += 20
        for k, bl in enumerate(b.get("bullets", [])):
            bl_lines = wrap(c, bl, REG(11), tw_ - 50)[:3]; y0 = iy
            c.text(tx, iy, "•", REG(11), INK)
            for ln in bl_lines: c.text(tx + 12, iy, ln, REG(11), DARK); iy += 15
            draw_mark(tx + 10, y0, min(tw_ - 50, max(c.tw(l, REG(11)) for l in bl_lines)), iy - y0 - 3, mark_for(f"bullet {k + 1}"))
            iy += 6
            if iy > y + h - 60: break
        if b.get("description") and iy < y + h - 50:
            c.text(tx, iy, "Product description", BOLD(12), INK); iy += 18; y0 = iy
            for ln in wrap(c, b["description"], REG(11), tw_ - 50)[:3]: c.text(tx, iy, ln, REG(11), DARK); iy += 15
            draw_mark(tx, y0, tw_ - 50, iy - y0 - 3, mark_for("description"))
        if b.get("foot") and iy < y + h - 24:
            for ln in wrap(c, b["foot"], MONO(10), tw_ - 20)[:2]: c.text(tx, iy + 8, ln, MONO(10), MUTED); iy += 14
    else:
        px, py, pw = x + 24, y + t, w - 48; c.box(px, py, pw, h - t - 16, PANEL, LINE, 2); iy = py + 16
        if b.get("heading"): c.text(px + 16, iy, b["heading"], BOLD(15), INK); iy += 26
        for k, para in enumerate(b.get("paragraphs", [])):
            y0 = iy
            for ln in wrap(c, para, REG(11), pw - 60)[:4]: c.text(px + 16, iy, ln, REG(11), DARK); iy += 15
            draw_mark(px + 14, y0, pw - 60, iy - y0 - 3, mark_for(f"paragraph {k + 1}")); iy += 8
        for k, row in enumerate(b.get("lines", [])):
            if iy > y + h - 40: break
            cw_ = (pw - 32) / max(1, len(row))
            for j, v in enumerate(row): c.text(px + 16 + j * cw_, iy, str(v), BOLD(11) if j == 0 else REG(11), INK)
            draw_mark(px + 14, iy - 2, pw - 40, 14, mark_for(f"line {k + 1}")); iy += 22
BLOCKS.update(document=b_document, media=b_media, calendar=b_calendar, tree=b_tree, artefact=b_artefact)
BLOCKS.update(stack=b_stack, next=b_next, steps=b_steps, chips=b_chips, options=b_options, compare=b_compare, board=b_board, graph=b_graph,
              chat=b_chat, decomp=b_decomp, work=b_work, facts=b_facts)
NO_TAG.update({"next", "steps", "chips", "stack"})
def flat(blocks):
    """Every block, with the ones inside a stack brought out (for the manifest and the checks)."""
    out = []
    for b in blocks: out += [b] + flat(b.get("blocks", [])) if b.get("type") == "stack" else [b]
    return out
PATTERNS = {"queue", "split", "focus", "decision", "board", "dashboard", "map", "feed", "guided"}

def shell_topbar(c, W, H, app, page):
    tb = page.get("topbar") or ({"tabs": app["nav"], "active": app["nav"].index(page["nav_active"]) if page.get("nav_active") in app["nav"] else 0} if page.get("layout") != "map" else {}); c.d.rectangle([0, 0, W, 72], fill=PANEL if page.get("layout") != "map" else None)
    c.box(20, 22, 116, 28, FILL2, None, 4); c.text(78, 36, app.get("logo", "LOGO"), BOLD(12), DARK, "mm")
    if tb.get("tabs"): b_segmented(c, W / 2 - 120 if page.get("layout") == "map" else 170, 18, 0, 36, {"items": tb["tabs"], "active": tb.get("active", 0)})
    rx = W - 64; c.d.ellipse([rx, 16, rx + 40, 56], fill=DARK); c.text(rx + 20, 36, "H", BOLD(14), PANEL, "mm"); rx -= 12
    for item in reversed(tb.get("right", [])):
        f = MONO(11) if item.isupper() else REG(13); w = c.tw(item, f) + (52 if not item.isupper() else 50); rx -= w
        c.box(rx, 18, w, 36, PANEL, LINE, 18)
        if item.isupper(): c.box(rx + 12, 28, 16, 16, FILL2, None, 3); c.text(rx + 34, 36, item, f, INK, "lm")
        else: c.text(rx + 16, 36, item, f, INK, "lm"); c.d.polygon([(rx + w - 22, 33), (rx + w - 14, 33), (rx + w - 18, 39)], fill=DARK)
        rx -= 10
    return 36, 72 + 8, W - 72, 72

# ---------- v4.9 · more navigation shells (SKILL.md rule 13): the spec chooses one per app or per persona ----------
def _topstrip(c, W, x, h, app):
    c.d.rectangle([x, 0, W, h], fill=PANEL); c.d.line([(x, h), (W, h)], fill=LINE)
    c.box(x + 24, (h - 32) // 2, 300, 32, BG, LINE, 6); c.text(x + 40, h // 2, app.get("search_label", "Search"), REG(12), MUTED, "lm")
    c.d.ellipse([W - 52, h // 2 - 16, W - 20, h // 2 + 16], fill=FILL2); c.d.ellipse([W - 96, h // 2 - 10, W - 76, h // 2 + 10], outline=MUTED, width=2)
def shell_icons(c, W, H, app, page):
    """A narrow icon rail (labels on hover), the most room for the work."""
    nw = 64; c.d.rectangle([0, 0, nw, H], fill=PANEL); c.d.line([(nw, 0), (nw, H)], fill=LINE); c.box(18, 14, 28, 28, FILL2, None, 6)
    for i, item in enumerate(app["nav"]):
        y = 76 + i * 52; act = item == page.get("nav_active")
        if act: c.d.rounded_rectangle([10, y - 6, nw - 10, y + 38], 8, fill=FILL)
        c.d.rounded_rectangle([22, y + 4, 42, y + 24], 5, fill=DARK if act else FILL2)
        c.text(nw / 2, y + 33, item[:9], REG(8), INK if act else MUTED, "mm")
    _topstrip(c, W, nw, 56, app); return nw + PAD, 56 + PAD, W - nw - 2 * PAD, 56
def shell_context(c, W, H, app, page):
    """An icon rail plus a context panel for the current area (saved views, groups, recent records)."""
    nw, pw = 64, 232; shell_icons(c, W, H, app, page)
    c.d.rectangle([nw + 1, 56, nw + pw, H], fill=BG); c.d.line([(nw + pw, 56), (nw + pw, H)], fill=LINE)
    c.text(nw + 20, 84, (page.get("nav_active") or "").upper(), MONO(10), DARK, "lm")
    for i, it in enumerate(page.get("context") or app.get("context", {}).get(page.get("nav_active"), [])):
        y = 104 + i * 34; act = i == 0
        if act: c.d.rounded_rectangle([nw + 10, y, nw + pw - 10, y + 28], 6, fill=FILL)
        s_ = it if isinstance(it, str) else f"{it[0]}"; c.text(nw + 22, y + 14, s_, BOLD(12) if act else REG(12), INK, "lm")
        if not isinstance(it, str) and len(it) > 1: c.text(nw + pw - 22, y + 14, str(it[1]), MONO(10), MUTED, "rm")
    return nw + pw + PAD, 56 + PAD, W - nw - pw - 2 * PAD, 56
def shell_band(c, W, H, app, page):
    """A dark band across the top holding the logo and the destinations; the active one underlined."""
    h = 64; c.d.rectangle([0, 0, W, h], fill=DARK); c.box(24, 18, 96, 28, MUTED, None, 4); c.text(72, 32, app.get("logo", "LOGO")[:10], BOLD(11), PANEL, "mm")
    c.text(132, 32, app.get("name", ""), REG(12), "#c9c9c4", "lm"); x = 132 + c.tw(app.get("name", ""), REG(12)) + 36
    for item in app["nav"]:
        act = item == page.get("nav_active"); f = BOLD(13) if act else REG(13); c.text(x, 32, item, f, PANEL, "lm")
        if act: c.d.rectangle([x, 50, x + c.tw(item, f), 53], fill=PANEL)
        x += c.tw(item, f) + 32
    c.box(W - 400, 16, 280, 32, "#5a5a56", None, 6); c.text(W - 386, 32, app.get("search_label", "Search"), REG(12), "#c9c9c4", "lm")
    c.d.ellipse([W - 52, 16, W - 20, 48], fill=FILL2); return PAD, h + PAD, W - 2 * PAD, h
def shell_command(c, W, H, app, page):
    """No rail: a slim bar with the destinations as text and a command field in the middle (type to go or ask)."""
    h = 56; c.d.rectangle([0, 0, W, h], fill=PANEL); c.d.line([(0, h), (W, h)], fill=LINE); c.box(20, 14, 28, 28, FILL2, None, 6)
    x = 64
    for item in app["nav"]:
        act = item == page.get("nav_active"); f = BOLD(12) if act else REG(12)
        if act: c.d.rounded_rectangle([x - 8, 14, x + c.tw(item, f) + 8, 42], 14, fill=FILL)
        c.text(x, 28, item, f, INK if act else DARK, "lm"); x += c.tw(item, f) + 24
    cx = max(x + 24, W / 2 - 200); c.box(cx, 10, 400, 36, BG, DARK, 8); c.text(cx + 16, 28, "Go to or ask…", REG(12), MUTED, "lm")
    c.box(cx + 400 - 58, 18, 50, 20, FILL, None, 4); c.text(cx + 400 - 32, 28, "Ctrl K", MONO(9), DARK, "mm")
    c.d.ellipse([W - 52, 12, W - 20, 44], fill=FILL2); return PAD, h + PAD, W - 2 * PAD, h
SHELLS = {"left": (None, 56), "topbar": (None, 80), "icons": (shell_icons, 56), "context": (shell_context, 56), "band": (shell_band, 64), "command": (shell_command, 56)}

# ---------- full-screen map pages: the map is the page, panels float over it ----------
def map_ground(c, x, y, w, h, seed):
    c.d.rectangle([x, y, x + w, y + h], fill="#e9e9e5"); rnd = random.Random(seed)
    for _ in range(9):  # coastline-ish land blobs and state lines, so it reads as a country map
        px, py = x + rnd.uniform(.1, .9) * w, y + rnd.uniform(.1, .9) * h
        c.d.line([(px, y + 80), (px + rnd.uniform(-90, 90), y + h - 40)], fill="#dcdcd6", width=2)
        c.d.line([(x + 40, py), (x + w - 40, py + rnd.uniform(-50, 50))], fill="#dcdcd6", width=2)
def ring(c, cx, cy, n, split, r=None):
    r = r or (16 + min(16, n ** .5 * 2.2)); box = [cx - r, cy - r, cx + r, cy + r]
    c.d.ellipse(box, fill=PANEL); a = -90; cols = [DARK, MUTED, "#bdbdb8", FILL2]
    tot = sum(split) or 1; split = [v / tot for v in split]
    for frac, col in zip(split, cols):
        if frac > 0: c.d.arc(box, a, a + 360 * frac, fill=col, width=5); a += 360 * frac
    c.text(cx, cy, str(n), BOLD(13), INK, "mm")
def site_dot(c, x, y, status, halo=True):
    if halo: c.d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=(140, 140, 135, 45))
    if status == 0: c.d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=DARK, outline=PANEL, width=2)
    elif status == 1: c.d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=PANEL, outline=DARK, width=3)
    else: c.d.ellipse([x - 6, y - 6, x + 6, y + 6], fill="#9c9c97", outline=PANEL, width=2)
def legend_mark(c, x, y, kind):
    if kind == "dot0": c.d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=DARK)
    elif kind == "dot1": c.d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=PANEL, outline=DARK, width=2)
    elif kind == "dot2": c.d.ellipse([x - 5, y - 5, x + 5, y + 5], fill="#9c9c97")
    elif kind == "dash":
        for k in range(3): c.d.line([(x - 9 + k * 7, y), (x - 5 + k * 7, y)], fill=DARK, width=2)
    elif kind == "ai": c.d.ellipse([x - 6, y - 6, x + 6, y + 6], outline=DARK, width=1); c.text(x, y, "≈", BOLD(9), DARK, "mm")
def draw_map(c, x, y, w, h, m, avoid_l, avoid_r):
    map_ground(c, x, y, w, h, m.get("id", "m")); rnd = random.Random(m.get("id", "m") + "p")
    lo, hi = x + avoid_l + 40, x + w - avoid_r - 60
    mode = m.get("mode", "dots")
    if mode == "rings":
        for n in m.get("counts", [2, 10, 2, 19, 4, 15, 61, 6, 41, 20, 3, 29, 9]):
            cx, cy = rnd.uniform(lo, hi), rnd.uniform(y + 130, y + h - 150)
            crit = rnd.uniform(.55, .95); watch = rnd.uniform(0, 1 - crit); ring(c, cx, cy, n, [crit, watch, 1 - crit - watch, 0])
    elif mode == "arcs":
        hubs = [(rnd.uniform(lo + 300, hi), rnd.uniform(y + 220, y + h - 200)) for _ in range(m.get("hubs", 5))]
        for _ in range(m.get("routes", 16)):
            sx, sy = x + avoid_l + rnd.uniform(-40, 160), rnd.uniform(y + 250, y + h * .62); tx, ty = rnd.choice(hubs)
            mx, my = (sx + tx) / 2, min(sy, ty) - rnd.uniform(40, 110)
            pts = [((1 - t) ** 2 * sx + 2 * (1 - t) * t * mx + t * t * tx, (1 - t) ** 2 * sy + 2 * (1 - t) * t * my + t * t * ty) for t in [i / 32 for i in range(33)]]
            for i in range(0, 32, 2): c.d.line([pts[i], pts[i + 1]], fill=DARK, width=2)
        for (hx, hy), n in zip(hubs, m.get("counts", [8, 2, 5, 5, 5])):
            s = rnd.uniform(.3, .7); ring(c, hx, hy, n, [s, 0, 0, 0] if False else [s, 0, 1 - s, 0])
    elif mode == "radius":
        cx, cy, r = x + w * .7, y + h * .5, h * .34
        c.d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=DARK, width=2, fill=(120, 120, 115, 18))
        c.pill(cx - 45, cy - r - 10, m.get("radius_label", "50 MI"))
        for _ in range(m.get("n", 26)):
            a, d = rnd.uniform(0, 6.28), r * rnd.uniform(.05, .95) ** .5
            site_dot(c, cx + d * __import__("math").cos(a), cy + d * __import__("math").sin(a), 0)
        site_dot(c, cx, cy, 0); c.d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], outline=DARK, width=3)
    else:
        for _ in range(m.get("n", 140)):
            st = 0 if rnd.random() < m.get("share0", .12) else (1 if rnd.random() < m.get("share1", .05) else 2)
            site_dot(c, rnd.uniform(lo - 200, hi + 60), rnd.uniform(y + 90, y + h - 90), st)
        for lab in m.get("labels", []):  # attention sites carry a label; healthy ones none
            lx, ly = rnd.uniform(lo, hi - 120), rnd.uniform(y + 140, y + h - 160); site_dot(c, lx, ly, 0)
            c.box(lx + 12, ly - 11, c.tw(lab, REG(10)) + 14, 22, PANEL, LINE, 4); c.text(lx + 19, ly, lab, REG(10), INK, "lm")
    if m.get("card"):  # the site card a click opens
        cd = m["card"]; cx, cy = min(x + w * .52, x + w - avoid_r - 290), y + h * .38; site_dot(c, cx, cy, 0)
        cw, ch = 250, 46 + 20 * len(cd["lines"]) + 16; bx, by = cx + 16, cy - 20
        c.box(bx, by, cw, ch, PANEL, DARK, 8, 2); c.text(bx + 14, by + 16, cd["title"], BOLD(13), INK, "lm")
        c.pill(bx + 14, by + 30, cd["status"], True)
        for i, l in enumerate(cd["lines"]): c.text(bx + 14, by + 66 + i * 20, l, REG(11), DARK, "lm")
    # legend pill, bottom centre
    items = m.get("legend", []); f = REG(12)
    lw = sum(c.tw(t, f) + 34 for _, t in items) + 16; lx, ly = x + avoid_l + max(0, (w - avoid_l - avoid_r - lw) / 2), y + h - 58
    c.box(lx, ly, lw, 36, PANEL, LINE, 18); px = lx + 18
    for kind, t in items: legend_mark(c, px, ly + 18, kind); c.text(px + 12, ly + 18, t, f, INK, "lm"); px += c.tw(t, f) + 34
    # zoom + fit, bottom right (left of an open right panel)
    zx = x + w - avoid_r - 66; zy = y + h - 210
    c.box(zx, zy, 42, 126, PANEL, LINE, 8)
    for i, s in enumerate(("+", "−", "⤢")): c.text(zx + 21, zy + 21 + i * 42, s if s != "⤢" else "↗", BOLD(16), DARK, "mm")
    c.text(x + w - 12, y + h - 8, "© OpenStreetMap contributors", REG(9), MUTED, "rb")
    c.tag(x, y, w - 90, h - 6, m)
def stack(c, x, y, w, blocks, gap=12):
    for b in blocks: b.setdefault("_w", w)
    outer = c.cur
    for b in blocks:
        h = b.get("h", 100)
        if outer: c.cur = (x, y, w, h, b.get("id") or b.get("component") or b["type"])
        BLOCKS[b["type"]](c, x, y, w, h, b); c.cur = outer
        if b["type"] not in NO_TAG: c.tag(x, y, w, h, b)
        y += h + b.get("gap", gap)
    return y
def render_map_page(app, page, out):
    W, H = page.get("width", 1280), page.get("height", 800); c = Canvas(W, H)
    left, right = page.get("left", {}), page.get("right")
    lw = left.get("width", 256) + 36 if left else 0; rw = right.get("width", 380) + 36 if right else 0
    draw_map(c, 0, 0, W, H, page["map"], lw, rw)
    x0, y0, cw, top = shell_topbar(c, W, H, app, page)
    if left:
        if left.get("card"):  # a solid panel (search form) rather than floating cards
            c.box(36, 88, left.get("width", 256), H - 120, PANEL, LINE, 10); stack(c, 56, 108, left.get("width", 256) - 40, left["blocks"], 14)
        else: stack(c, 36, 88, left.get("width", 256), left["blocks"])
    if right:
        rx = W - right.get("width", 380) - 24; c.box(rx, 88, right.get("width", 380), H - 112, PANEL, LINE, 12)
        c.d.ellipse([rx + 20, 108, rx + 36, 124], outline=DARK, width=2); c.text(rx + 46, 116, right["title"], BOLD(19), INK, "lm")
        c.d.ellipse([rx + right.get("width", 380) - 48, 100, rx + right.get("width", 380) - 16, 132], fill=FILL)
        c.d.line([(rx + right.get("width", 380) - 37, 111), (rx + right.get("width", 380) - 27, 121)], fill=DARK, width=2); c.d.line([(rx + right.get("width", 380) - 37, 121), (rx + right.get("width", 380) - 27, 111)], fill=DARK, width=2)
        stack(c, rx + 20, 148, right.get("width", 380) - 40, right["blocks"])
        c.tag(rx, 88, right.get("width", 380), H - 112, right)
    # copilot button, bottom right, above everything but overlays
    c.d.ellipse([W - 76, H - 76, W - 20, H - 20], fill=PANEL, outline=DARK, width=2); c.text(W - 48, H - 48, AGENT[0][:2].upper(), BOLD(13), INK, "mm")
    for o in page.get("overlays", []): OVERLAYS[o["type"]](c, W, H, 72, o)
    strip = 40; full = Image.new("RGB", (W, H + strip), "#ffffff"); full.paste(c.im, (0, strip))
    d = ImageDraw.Draw(full); d.text((14, 20), f"{page['id']} · {page['title']} · {page.get('persona', '')} · {W}px", font=MONO(12), fill=DARK, anchor="lm")
    full.save(os.path.join(out, "png", f"{page['id']}.png")); return full

# ---------- page ----------
def bh(b):
    if b.get("type") == "header" and not b.get("h"): return 36 + (22 if b.get("breadcrumb") else 0) + (22 if b.get("subtitle") else 0)
    return b.get("h") or (sum(k.get("h", 100) + k.get("gap", 12) for k in b.get("blocks", [])) - 12 if b.get("type") == "stack" else 120)
def row_height(row): return max(bh(b) for b in row)
def render_page(app, page, out):
    if page.get("layout") == "map": return render_map_page(app, page, out)
    W = page.get("width", 1280); phone = W < 600
    gap = 12 if phone else GAP
    rows = page["rows"]; body_h = sum(row_height(r) for r in rows) + gap * (len(rows) - 1)
    shell = page.get("shell") or app.get("shell") or "left"
    if shell not in SHELLS: shell = "left"
    topbar = shell == "topbar"
    H = SHELLS[shell][1] + (16 if phone else PAD) * 2 + body_h + (64 if phone else 0)
    fn = shell_phone if phone else shell_topbar if topbar else (SHELLS[shell][0] or shell_desktop)
    c = Canvas(W, H); x0, y0, cw, top = fn(c, W, H, app, page)
    if topbar: y0 += 12
    y = y0; col = (cw - gap * 11) / 12
    for row in rows:
        x = x0; rh = row_height(row)
        for b in row:
            span = b.get("span", 12); w = col * span + gap * (span - 1); h = b.get("h", rh) if b.get("type") != "stack" else rh
            b["_w"] = w; c.cur = (x, y, w, h, b.get("id") or b.get("component") or b["type"]); c.blocks[c.cur[4]] = (x, y, w, h, b["type"]); BLOCKS[b["type"]](c, x, y, w, h, b); c.cur = None; b.pop("_w", None)
            if b["type"] not in NO_TAG: c.tag(x, y, w, h, b)
            x += w + gap
        y += rh + gap
    RENDER_ISSUES.extend(c.sloppy(page["id"]))
    for o in page.get("overlays", []): OVERLAYS[o["type"]](c, W, H, top, o)
    # page label strip (outside the screen), so a reviewer always knows which page this is
    strip = 40; full = Image.new("RGB", (W, H + strip), "#ffffff"); full.paste(c.im, (0, strip))
    d = ImageDraw.Draw(full); d.text((14, 20), f"{page['id']} · {page['title']} · {page.get('persona', '')} · {W}px", font=MONO(12), fill=DARK, anchor="lm")
    full.save(os.path.join(out, "png", f"{page['id']}.png")); return full

def manifest(spec):
    comps = OrderedDict()
    parts = set()
    def add(b, page):
        if not b.get("component"):  # header, filters, tabs, labels, single controls: page parts, not components
            parts.add(b["type"]); return
        name = b["component"]
        e = comps.setdefault(name, {"component": name, "type": b["type"], "pages": [], "blocks": [], "variants": set(), "features": set(), "states": set()})
        if page["id"] not in e["pages"]: e["pages"].append(page["id"])
        if b.get("id"): e["blocks"].append(f"{page['id']}/{b['id']}")
        e["variants"].update(b.get("variants", []))
        if b.get("cmp"): e.setdefault("cmp", []); e["cmp"] += [b["cmp"]] if b["cmp"] not in e["cmp"] else []
        if b.get("note"): e.setdefault("notes", []); e["notes"] += [f"{page['id']}: {b['note']}"]
        for k in ("kind", "select", "bulk", "status_col", "cluster", "popup", "card"):
            if b.get(k): e["features"].add(f"kind:{b[k]}" if k == "kind" else k)
        if b["type"] == "map": e.setdefault("modes", []); e["modes"] += [b["mode"]] if b["mode"] not in e["modes"] else []
        e["states"].update(b.get("states", []))
        if b.get("hero"): e["hero"] = True
        if b.get("thumb") or b["type"] == "media" or b.get("media"):  # where the hero object's picture shows, and at what shape
            e["media"] = b.get("media") or {"ratio": b.get("ratio", "1:1" if b.get("thumb") else "16:9"), "where": "thumbnail" if b.get("thumb") else "grid"}
        if b.get("views"):
            e.setdefault("views", [])
            for v in b["views"]:
                nm = v["name"] if isinstance(v, dict) else v
                if nm not in [x["name"] if isinstance(x, dict) else x for x in e["views"]]: e["views"].append(v)
        for k in ("volume", "primary"):  # how many at once; the one main action
            if b.get(k): e[k] = b[k]
        for k in ("purpose", "shows", "does"):  # what it is for, the data it shows, the actions it drives: the design system designs from these
            v = b.get(k)
            if v and k == "purpose": e.setdefault("purpose", []); e["purpose"] += [v] if v not in e["purpose"] else []
            elif v: e.setdefault(k, []); e[k] += [s for s in v if s not in e[k]]
        if b["type"] == "map" and b.get("data"):
            e.setdefault("data_contract", {})[b.get("mode", "dots")] = b["data"]
        if b["type"] == "map" and b.get("behaviour"):
            e["behaviour"] = b["behaviour"]
    shells = set()
    for p in spec["pages"]:
        shells.add("phone" if p.get("width", 1280) < 600 else "desktop")
        for r in p.get("rows", []):
            for b in flat(r): add(b, p)
        if p.get("map"): add(p["map"], p)
        for b in p.get("left", {}).get("blocks", []): add(b, p)
        if p.get("right"): add(dict({k: v for k, v in p["right"].items() if k != "blocks"}, type=p["right"].get("type", "panel")), p)
        for b in (p.get("right") or {}).get("blocks", []): add(b, p)
        for o in p.get("overlays", []):
            add(dict({k: v for k, v in o.items() if k != "blocks"}), p)
            for b in flat(o.get("blocks", [])): add(b, p)
    out = {"app": spec["app"]["name"], "client": spec.get("client"), "use_case": spec.get("use_case"),
           "shells": sorted(shells), "pages": [{"id": p["id"], "title": p["title"], "persona": p.get("persona"),
           "width": p.get("width", 1280), "brd_ref": p.get("brd_ref"), "pattern": p.get("pattern"), "shape": p.get("shape"), "brief": p.get("brief")}
           for p in spec["pages"]], "signature": spec.get("signature"), "journey": spec.get("journey", []), "brd_overrides": spec.get("brd_overrides", []),
           "references": spec.get("references", []), "hero_object": spec.get("hero_object"),
           "shell": spec["app"].get("shell", "left"), "nav_options": spec.get("nav_options", []), "payoff_frame": spec.get("payoff_frame"),
           "alt_views": [{"frame": p["id"], "of": p["alt_view_of"], "view": p.get("view")} for p in spec["pages"] if p.get("alt_view_of")],
           "components": []}
    for e in comps.values():
        e["variants"] = sorted(e["variants"]); e["features"] = sorted(e["features"]); e["states"] = sorted(e["states"]); out["components"].append(e)
    out["page_parts"] = sorted(parts)
    return out

def is_legacy(spec):
    """A spec written before v4 (no `signature`): it renders as it always did, and the v4 checks it cannot meet are warnings."""
    return "signature" not in spec

def validate(spec):
    """Stop on spec errors before drawing anything, with one line per problem. A legacy spec (no `signature`) gets its
    missing v4 fields (brief, pattern, signature) as `warning:` lines instead, and renders as before."""
    errs, ids, warns = [], set(), []
    v4 = warns if is_legacy(spec) else errs
    if not spec.get("pages"): sys.exit("spec errors:\n  spec has no pages")
    for p in spec.get("pages", []):
        pid = p.get("id", "?")
        if pid in ids: errs.append(f"{pid}: duplicate page id")
        ids.add(pid)
        for k in ("id", "title", "persona"):
            if not p.get(k): errs.append(f"{pid}: page needs '{k}'")
        if not re.search(r"\d[a-z]$", pid):  # a page's first frame carries its brief; extra frames (PG-03b) inherit it
            br = p.get("brief") or {}
            miss = [k for k in ("job", "decision", "needs_you", "next") if not br.get(k)]
            if is_legacy(spec) and (miss or p.get("pattern") not in PATTERNS):  # one line per page: the spec predates briefs and patterns
                v4.append(f"{pid}: no " + " or ".join(x for x in (f"brief ({', '.join(miss)})" if miss else "", "pattern" if p.get("pattern") not in PATTERNS else "") if x) + " (SKILL.md rules 2-3; a spec from before v4)"); miss = []
            for k in miss: v4.append(f"{pid}: brief needs '{k}' (SKILL.md rule 2)")
            if p.get("pattern") not in PATTERNS and not is_legacy(spec): v4.append(f"{pid}: 'pattern' must be one of {', '.join(sorted(PATTERNS))} (references/patterns.md)")
        blocks = flat([b for r in p.get("rows", []) for b in r] + p.get("left", {}).get("blocks", []) + (p.get("right") or {}).get("blocks", [])
                      + [k for o in p.get("overlays", []) for k in o.get("blocks", [])])
        if p.get("layout") == "map":
            m = p.get("map") or {}
            if m.get("type") != "map": errs.append(f"{pid}: a map page needs a 'map' block with type 'map'")
            if m.get("mode") not in ("rings", "dots", "arcs", "radius"): errs.append(f"{pid}: map mode must be rings, dots, arcs or radius")
            if not m.get("data"): errs.append(f"{pid}: map block needs its data contract ('data')")
            if not m.get("legend"): errs.append(f"{pid}: map block needs a legend in this screen's own words")
        elif not p.get("rows"): errs.append(f"{pid}: page has no rows")
        for r in p.get("rows", []):
            if sum(b.get("span", 12) for b in r) > 12: errs.append(f"{pid}: a row spans more than 12 columns")
            if any(b.get("type") == "map" for b in r): errs.append(f"{pid}: a map is the page, never a block in a row: use \"layout\": \"map\" (references/map-component.md)")
        for o in p.get("overlays", []):
            if o.get("type") not in OVERLAYS: errs.append(f"{pid}: overlay type must be drawer or modal, not '{o.get('type')}'")
            if not o.get("component"): errs.append(f"{pid}: overlay {o.get('id', '')} needs a 'component' name")
        for b in blocks:
            t = b.get("type")
            if t not in BLOCKS: errs.append(f"{pid}: unknown block type '{t}'" + (" (drawer and modal go in 'overlays')" if t in OVERLAYS else ""))
            if t in BLOCKS and t not in NO_TAG and not b.get("component"):
                errs.append(f"{pid}: block '{t}' {b.get('id', '')} needs a 'component' name")
    for p in spec.get("pages", []):
        if p.get("shell") and p["shell"] not in SHELLS: errs.append(f"{p.get('id')}: shell must be one of {', '.join(SHELLS)}")
    if spec.get("app", {}).get("shell") and spec["app"]["shell"] not in SHELLS: errs.append(f"app.shell must be one of {', '.join(SHELLS)}")
    sig = spec.get("signature") or {}
    if is_legacy(spec): v4.append("spec: no 'signature' (a spec from before v4, rendered as before); name the app's signature when the spec is next reworked (SKILL.md rule 4)")
    else:
        for k in ("name", "frame", "why"):
            if not sig.get(k): errs.append(f"spec: 'signature' needs '{k}' (SKILL.md rule 4)")
    if sig.get("frame") and sig["frame"] not in ids: errs.append(f"spec: signature frame '{sig['frame']}' is not a page id")
    if errs: sys.exit("spec errors:\n  " + "\n  ".join(errs))
    for w_ in warns: print("warning:", w_)

BANNED = re.compile(r"\b(synthetic|dummy|simulate|simulated|simulation|lorem|placeholder|for the demo|demo data|demo persona|TBD|mock)\b", re.I)
# the journey and the briefs are written fresh (no BRD section names to quote), so the bare word counts there
BANNED_TEXT = re.compile(BANNED.pattern[:-3] + "|demo)\\b", re.I)
STYLING = re.compile(r"\b(hover|shadow|blur|blurred|gradient|glass|colou?r|font|radius|animation|animate)\b", re.I)
CODE = re.compile(r"^\s*[A-Z]{2,5}-\d{3,}\b")
MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
DATE = re.compile(r"\b(\d{1,2}) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\b", re.I)
KEYDATE = re.compile(r"\b(?:due|lock(?:s|ed)?|expires?(?: on)?|by|until|ends?)\s+(?:on\s+)?(\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*)", re.I)
AHEAD = re.compile(r"\bin (\d+) days?\b|\b(\d+) days? (?:from now|to go|left|to the lock|before)\b", re.I)
LATE = re.compile(r"\boverdue (?:by )?(\d+) days?\b|\b(\d+) days? (?:overdue|late)\b", re.I)
def _day(txt):
    import datetime
    m = DATE.search(txt); return datetime.date(2026, MONTHS[m.group(2)[:3].lower()], int(m.group(1)))
def implied_today(text):
    """The 'today' a piece of copy implies, from a date and a relative day count in the same item; None if it implies none."""
    import datetime
    keys = KEYDATE.findall(text); dates = DATE.findall(text)
    a, l = AHEAD.search(text), LATE.search(text)
    if a:
        anchor = keys[0] if len(keys) == 1 else (" ".join(dates[0]) if len(dates) == 1 else None)
        if anchor: return _day(anchor) - datetime.timedelta(days=int(a.group(1) or a.group(2)))
    if l:
        due = [k for k in re.findall(r"\bdue\s+(\d{1,2} \w+)", text, re.I) if DATE.search(k)]
        if len(due) == 1: return _day(due[0]) + datetime.timedelta(days=int(l.group(1) or l.group(2)))
    return None
def item_texts(o, path):
    """Each smallest dict's own strings joined, so a date and its day count are read together."""
    if isinstance(o, dict):
        own = [v for v in o.values() if isinstance(v, str)] + [x for v in o.values() if isinstance(v, list) for x in v if isinstance(x, str)]
        if own: yield path, " · ".join(own)
        for k, v in o.items():
            if isinstance(v, (dict, list)): yield from item_texts(v, path + [k])
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from item_texts(v, path + [str(i)])

def lint(spec):
    """The tells of a frame that transcribes instead of thinking (SKILL.md step 6, patterns.md part 6). Printed, not fatal: fix each one or
    say in the hand-over why it stays."""
    out = []
    # the v4 checks a legacy spec (no `signature`) cannot meet: house layout, signature, references, hero object, payoff,
    # navigation options, views. On a legacy spec they print as `warning:` lines; on a v4 spec they are `check:` lines.
    legacy = is_legacy(spec); g = [] if legacy else out
    def walk(o, path):
        if isinstance(o, dict):
            for k, v in o.items(): walk(v, path + [k])
        elif isinstance(o, list):
            for i, v in enumerate(o): walk(v, path + [str(i)])
        elif isinstance(o, str) and path and path[-1] not in ("id", "cmp", "component", "type", "brd_ref", "pattern", "persona"):
            if BANNED.search(o) and not any(w.lower() in o.lower() for w in spec.get("allow_words", [])): out.append(f"{'/'.join(path[:3])}: '{BANNED.search(o).group(0)}' on screen (no demo, synthetic or placeholder words)")
            if path[-1] in ("note",) and STYLING.search(o): out.append(f"{'/'.join(path[:3])}: styling in a note ('{STYLING.search(o).group(0)}'); looks are the design system's job, say what it must do")
            if path[-1] in ("title", "head") and CODE.match(o): out.append(f"{'/'.join(path[:3])}: '{o[:30]}' leads with an internal code; lead with the thing's name, the code goes after")
    for p in spec["pages"]:
        walk({k: v for k, v in p.items() if k != "brief"}, [p["id"]])
        for k, v in (p.get("brief") or {}).items():
            if isinstance(v, str) and BANNED_TEXT.search(v): out.append(f"{p['id']}/brief/{k}: '{BANNED_TEXT.search(v).group(0)}' in the brief; the build reads it (SKILL.md rule 5)")
        rows = p.get("rows", [])
        first = [b for r in rows[:3] for b in r if b["type"] not in ("header", "filters", "tabs", "label", "next", "steps", "chips")][:6]
        if first and len(first) >= 3 and all(b["type"] in ("kpi", "stat") or (b["type"] == "slot" and re.search(r"kpi|stat|tile|metric|number", b.get("component", ""), re.I)) for b in first[:3]):
            if p.get("pattern") != "dashboard": g.append(f"{p['id']}: opens with a row of number tiles on a '{p.get('pattern')}' page; lead with the work (patterns.md part 4 rule 1)")
        blocks = flat([b for r in rows for b in r] + p.get("left", {}).get("blocks", []) + (p.get("right") or {}).get("blocks", []))
        for b in blocks:
            if b["type"] == "slot" and b.get("hero"): out.append(f"{p['id']}/{b.get('id', '')}: the hero is a slot; draw the defining component with its real structure (rule 4)")
            if b["type"] == "slot" and len(b.get("note", "")) > 140: out.append(f"{p['id']}/{b.get('id', '')}: a slot note of {len(b['note'])} characters is content written as text; draw it or cut it to one line")
    # sameness: an app whose pages all open the same way has a house layout, not pages designed for their work
    base = [p for p in spec["pages"] if not re.search(r"\d[a-z]$", p["id"])]
    def opening(p):
        if p.get("layout") == "map": return ("map",)
        seq = [b["type"] for r in p.get("rows", []) for b in r if b["type"] not in ("header", "label", "text")]
        return tuple(seq[:3])
    if len(base) >= 3:
        from collections import Counter
        top, n = Counter(opening(p) for p in base).most_common(1)[0]
        if n >= 3 and n * 2 >= len(base): g.append(f"{n} of {len(base)} pages open the same way ({' → '.join(top)}); give each page the shape its work needs (patterns.md part 1)")
    frames = [p for p in spec["pages"] if p.get("layout") != "map"]
    if len(frames) >= 3:
        banners = [p["id"] for p in frames if any(b["type"] == "next" and b.get("kind") != "decision" for r in p.get("rows", []) for b in flat(r))]
        if len(banners) > 2 and len(banners) * 2 >= len(frames): g.append(f"a next-step banner on {len(banners)} of {len(frames)} frames ({', '.join(banners)}); carry the next step inside the page instead (patterns.md part 3)")
        chips = [p["id"] for p in frames if any(b["type"] == "chips" for r in p.get("rows", []) for b in flat(r))]
        if len(chips) > 2 and len(chips) * 2 >= len(frames): g.append(f"work-split chips on {len(chips)} of {len(frames)} frames; use them only where two or more groups really hold work (patterns.md part 3)")
        bars = [p["id"] for p in frames if any(b["type"] == "next" and b.get("kind") == "decision" for r in p.get("rows", []) for b in flat(r))]
        if len(bars) > 3 and len(bars) * 2 > len(frames): g.append(f"a decision bar on {len(bars)} of {len(frames)} frames ({', '.join(bars)}); keep it for pages that end in one choice, and let the hero carry the action elsewhere (patterns.md part 3)")
        steps = [p["id"] for p in frames if any(b["type"] == "steps" for r in p.get("rows", []) for b in flat(r))]
        if len(steps) > 3 and len(steps) * 2 > len(frames): g.append(f"a step indicator on {len(steps)} of {len(frames)} frames; use it only where the job has ordered steps (SKILL.md rule 3)")
    queues = [p for p in base if p.get("pattern") == "queue" and p.get("layout") != "map"]
    if len(queues) >= 2:
        from collections import Counter
        same = [o for o, n in Counter(opening(p) for p in queues).items() if n >= 2]
        if same: g.append(f"{len(queues)} queue pages and some open the same way ({' → '.join(same[0])}); give each queue a different shape (patterns.md part 1)")
    for i, j in enumerate(spec.get("journey", [])):
        t = j.get("step", "") if isinstance(j, dict) else str(j)
        if BANNED_TEXT.search(t): out.append(f"journey/{i + 1}: '{BANNED_TEXT.search(t).group(0)}' in the journey; the build reads it (SKILL.md rule 5)")
    # an extra frame copied from its page: a block keeps its id, its title changes, its rows do not
    byid = {p["id"]: p for p in spec["pages"]}
    def blockmap(p):
        bs = flat([b for r in p.get("rows", []) for b in r] + (p.get("left") or {}).get("blocks", []) + (p.get("right") or {}).get("blocks", []))
        return {b["id"]: b for b in bs if b.get("id")}
    for p in spec["pages"]:
        m = re.match(r"(.+?\d)[a-z]$", p["id"])
        if not m or m.group(1) not in byid: continue
        mine, theirs = blockmap(p), blockmap(byid[m.group(1)])
        for bid, b in mine.items():
            o = theirs.get(bid)
            meta = {"id", "title", "h", "hero", "states", "variants", "purpose", "shows", "does", "note", "component", "cmp", "type", "span", "gap"}
            content = (set(b) | set(o or {})) - meta
            if o and content and o.get("title") != b.get("title") and all(o.get(k) == b.get(k) for k in content):
                out.append(f"{p['id']}/{bid}: title changed from '{str(o.get('title'))[:40]}' but its rows did not; update what the change touches (SKILL.md rule 9)")
    sig = spec.get("signature") or {}
    sp = next((p for p in spec["pages"] if p["id"] == sig.get("frame")), None)
    home = spec["pages"][0] if spec.get("pages") else None
    if sp and home and home is not sp and home.get("layout") != "map":
        sig_blocks = flat([b for r in sp.get("rows", []) for b in r]) + ([sp["map"]] if sp.get("map") else [])
        sig_types = {b["type"] for b in sig_blocks if b.get("hero")} - {"table", "list", "card", "slot", "kpi", "stat", "form", "next", "work"}
        sig_comps = {b.get("component") for b in sig_blocks if b.get("hero")}
        hb = flat([b for r in home.get("rows", []) for b in r] + [k for o in home.get("overlays", []) for k in o.get("blocks", [])])
        if sig_types and not any(b["type"] in sig_types or b.get("component") in sig_comps for b in hb) and "signature" not in json.dumps(home.get("brief", {})).lower():
            g.append(f"{home['id']}: the home does not show the signature in any form; draw the home's items in its form or say why in the home's brief (patterns.md part 2)")
        # the signature as a side panel beside a list of the same work: the home every app ends up with
        SIGT = {"calendar", "document", "media", "graph", "tree", "board", "map", "compare", "decomp", "chat"}
        hs = [(k, b.get("span", 12)) for r in home.get("rows", []) for b in r for k in flat([b])]
        lead = next((k for k, _ in hs if k.get("hero")), None)
        side = [w for k, w in hs if k["type"] in SIGT and (k["type"] in sig_types or k.get("component") in sig_comps)]
        if lead is not None and lead["type"] in ("list", "work", "table") and side and max(side) <= 6:
            g.append(f"{home['id']}: the signature sits as a side panel ({max(side)} of 12 columns) beside a {lead['type']}; let it hold the home's items and keep a narrow rail for the rest (patterns.md part 2)")
    # a narrow side column: fine where the work needs it, a house layout when every home and most pages have one
    def side_col(p):
        for r in p.get("rows", []):
            sp_ = [b.get("span", 12) for b in r]
            if len(r) >= 2 and sum(sp_) == 12 and min(sp_[0], sp_[-1]) <= 4 and max(sp_) >= 8: return True
        return False
    if home and home.get("layout") != "map" and side_col(home) and not re.search(r"side column|rail", json.dumps(home.get("brief", {})), re.I):
        g.append(f"{home['id']}: the home has a narrow side column; put what it holds where the work needs it (below, folded, a tab, a drawer) or say in the home's brief why it sits beside (patterns.md part 2)")
    cols = [p["id"] for p in frames if side_col(p)] if len(frames) >= 3 else []
    if len(cols) > 3 and len(cols) * 2 > len(frames): g.append(f"a narrow side column on {len(cols)} of {len(frames)} frames ({', '.join(cols)}); give each page the shape its work needs (patterns.md part 1)")
    # research: the signature should be informed by how others do the same job (SKILL.md rule 11)
    refs = spec.get("references") or []
    if sig.get("name") and not any(r.get("take") for r in refs if isinstance(r, dict)):
        g.append("no reference recorded: research how others handle the signature (patterns.md part 7), or say in the hand-over why none was usable")
    for r in refs:
        if isinstance(r, dict) and r.get("take") and not (r.get("for") or r.get("source")):
            g.append(f"reference '{str(r)[:40]}' does not say which component it changed")
    if sp and sp.get("layout") != "map":
        allb = flat([b for r in sp.get("rows", []) for b in r] + (sp.get("left") or {}).get("blocks", []) + (sp.get("right") or {}).get("blocks", [])) + ([sp["map"]] if sp.get("map") else [])
        heroes = [b for b in allb if b.get("hero")]
        if not heroes or all(b["type"] in ("table", "list", "card", "slot", "kpi", "stat", "form", "next") for b in heroes):
            g.append(f"{sp['id']}: the signature '{sig.get('name', '')}' is drawn with generic blocks only; draw it as itself (SKILL.md rule 4)")
    # one today: every date and day count on a frame agrees with the day the frame is set on
    import datetime
    def as_day(v):
        try: return _day(v) if v and DATE.search(v) else None
        except Exception: return None
    byid2 = {p["id"]: p for p in spec["pages"]}
    seen = {}
    for p in spec["pages"]:
        par = byid2.get((re.match(r"(.+?\d)[a-z]$", p["id"]) or [None, None])[1]) if re.search(r"\d[a-z]$", p["id"]) else None
        set_day = as_day(p.get("today") or (par or {}).get("today") or spec.get("today"))
        for path, t in item_texts({k: v for k, v in p.items() if k not in ("brief", "today")}, [p["id"]]):
            d = implied_today(t)
            if not d: continue
            where = "/".join(path[:3])
            if set_day and d != set_day:
                out.append(f"{where}: '{t[:70]}' implies today is {d:%d %b}, the frame is set on {set_day:%d %b}; make the date or the day count agree")
            elif not set_day: seen.setdefault(d, []).append(where)
    if len(seen) > 1:
        out.append("dates disagree on what day it is (" + "; ".join(f"{d:%d %b}: {', '.join(w[:2])}" for d, w in sorted(seen.items())) + "); set `today` in the spec, and on any frame later in the story, and make every date agree")
    # counts: a tab or title that claims N above a hero showing more than N items
    for p in spec["pages"]:
        rows = p.get("rows", [])
        for i, r in enumerate(rows):
            for b in r:
                if b["type"] != "tabs" or b.get("active") is None: continue
                m = re.search(r"(\d+)\s*$", str((b.get("items") or [""])[b["active"]]) if b["active"] < len(b.get("items") or []) else "")
                nxt = next((k for rr in rows[i + 1:] for k in flat(rr) if k.get("items") or k.get("columns") and k.get("rows")), None)
                if m and nxt:
                    shown = len(nxt.get("items") or nxt.get("rows") or [])
                    if shown > int(m.group(1)): out.append(f"{p['id']}: the tab says {m.group(1)} but {nxt.get('id', nxt['type'])} below it shows {shown}; show only what the tab counts, or fix the count")
    # tables that carry the page must show their rows
    for p in spec["pages"]:
        for b in flat([b for r in p.get("rows", []) for b in r] + (p.get("left") or {}).get("blocks", []) + (p.get("right") or {}).get("blocks", [])):
            if b["type"] == "table" and b.get("hero") and not b.get("rows"):
                out.append(f"{p['id']}/{b.get('id', '')}: a hero table without `rows`; give it 4–8 real rows in the person's words (spec-format.md)")
    # the journey hands over between people where the people really meet
    titles = {p["title"].lower(): p for p in spec["pages"] if not re.search(r"\d[a-z]$", p["id"])}
    for p in spec["pages"]:
        arr = ((p.get("brief") or {}).get("arrives") or "").lower()
        for t, q in titles.items():
            if q is not p and t and t in arr and not re.search(r"message|email|notif|link|hand|sent|share|assign", arr) and q.get("persona") and p.get("persona") and q["persona"] != p["persona"]:
                out.append(f"{p['id']}: {p['persona']} arrives from '{q['title']}', which is {q['persona']}'s page; say how it reaches them (a message, a hand-off, a shared link) or start them from their own page (SKILL.md rule 7)")
    # v4.8 · the hero object: what the users care about most, and its picture where it has one (SKILL.md rule 4)
    ho = spec.get("hero_object") or {}
    if not ho.get("name"): g.append("spec: no `hero_object`; name the one thing these users care about most (scoping §21 'Hero object'), and whether it has a picture")
    def shows_picture(p):
        bs = flat([b for r in p.get("rows", []) for b in r] + (p.get("left") or {}).get("blocks", []) + (p.get("right") or {}).get("blocks", [])
                  + [k for o in p.get("overlays", []) for k in o.get("blocks", [])])
        return any(b["type"] in ("media", "document") or b.get("thumb") or b.get("media") for b in bs)
    if ho.get("picture"):
        if sp and not shows_picture(sp) and sp.get("layout") != "map": g.append(f"{sp['id']}: the hero object ({ho['name']}) has a picture but the signature shows none; put it on the signature's items (`thumb`) or draw them as `media`")
        if home and home is not sp and not shows_picture(home) and home.get("layout") != "map": g.append(f"{home['id']}: the home shows no picture of the {ho['name']}; people recognise it by eye, so show it where they meet it")
        lists = [p["id"] for p in base if p.get("layout") != "map" and not shows_picture(p)]
        if len(lists) * 2 > len(base): g.append(f"pictures of the {ho['name']} appear on only {len(base) - len(lists)} of {len(base)} pages ({', '.join(lists)} show none); show it wherever the person picks, checks or approves one")
    # v4.8 · the component brief the design system designs to (SKILL.md rule 4)
    briefed = {b.get("component") for p in spec["pages"] for b in flat([b for r in p.get("rows", []) for b in r]) if b.get("purpose")}
    for p in spec["pages"]:
        for b in flat([b for r in p.get("rows", []) for b in r] + (p.get("left") or {}).get("blocks", []) + (p.get("right") or {}).get("blocks", [])):
            if b.get("hero") and b.get("component") and b["component"] not in briefed:
                miss = [k for k in ("purpose", "shows", "does") if not b.get(k)]
                if miss: g.append(f"{p['id']}/{b.get('id', b['component'])}: hero component without {', '.join(miss)}; the design system designs from its brief")
    # v4.8 · UX rules that hold on any page (SKILL.md rule 12)
    for p in spec["pages"]:
        bs = flat([b for r in p.get("rows", []) for b in r] + (p.get("left") or {}).get("blocks", []) + (p.get("right") or {}).get("blocks", []))
        for b in bs:
            if b["type"] == "table" and len(b.get("columns", [])) > 7: out.append(f"{p['id']}/{b.get('id', '')}: {len(b['columns'])} columns; keep 7 or fewer in view and move the rest into the record or a detail row")
            vol = b.get("volume")
            n = int(re.search(r"\d+", str(vol)).group(0)) if vol and re.search(r"\d+", str(vol)) else 0
            if b["type"] in ("table", "list", "work", "media") and n > 20 and not b.get("bulk") and not b.get("select"):
                out.append(f"{p['id']}/{b.get('id', '')}: {n} items at once and no bulk action; let the person select several and act once")
        heads = [b for b in bs if b["type"] == "header"]
        prim = sum(1 for b in bs if b["type"] == "button" and b.get("primary", True)) + sum(1 for h_ in heads if h_.get("actions")) + sum(1 for b in bs if b["type"] == "next" and b.get("actions"))
        if prim > 1: out.append(f"{p['id']}: {prim} primary actions; keep one main action per page and make the rest secondary")
    IRREV = re.compile(r"\b(delete|remove|reject|submit|publish|send|lock|export|approve all|cancel order)\b", re.I)
    txt = json.dumps([p.get("rows", []) for p in spec["pages"]])
    if IRREV.search(txt) and not any(o.get("type") == "modal" for p in spec["pages"] for o in p.get("overlays", [])):
        out.append(f"an irreversible action ('{IRREV.search(txt).group(0)}') and no confirm frame; draw one modal for it (rule 9)")
    # v4.9 · navigation explored, not assumed (SKILL.md rule 13)
    nav = spec.get("nav_options") or []
    if len(nav) < 3 or sum(1 for n in nav if n.get("chosen")) != 1:
        g.append(f"`nav_options` has {len(nav)} options and {sum(1 for n in nav if n.get('chosen'))} chosen; draw three different navigation shells for the home and choose one with its reason (SKILL.md rule 13)")
    else:
        ch = next(n for n in nav if n.get("chosen"))
        if ch.get("shell") != spec["app"].get("shell", "left"): g.append(f"the chosen navigation is '{ch.get('shell')}' but app.shell is '{spec['app'].get('shell', 'left')}'")
        if len({n.get("shell") for n in nav}) < 3: g.append("the three navigation options use the same shell; make them really different")
    # v4.10 · navigation options from three different families (SKILL.md rule 13)
    FAM = {"left": "rail", "icons": "rail", "context": "rail", "topbar": "bar", "band": "bar", "command": "command"}
    if len(nav) >= 3 and len({FAM.get(n.get("shell"), "?") for n in nav}) < 3:
        g.append("the navigation options come from fewer than three families; draw one rail (left, icons or context), one bar (topbar or band) and the command bar")
    # v4.10 · the signature drawn as the real thing (SKILL.md rule 4)
    if sp and sp.get("layout") != "map":
        sbs = flat([b for r in sp.get("rows", []) for b in r] + [k for r in sp.get("rows", []) for b in r for k in b.get("blocks", [])])
        if any(b.get("hero") and b["type"] == "document" and not any(r_.get("text") for r_ in b.get("regions", [])) for b in sbs) and not any(b["type"] == "artefact" for b in sbs):
            g.append(f"{sp['id']}: the signature is grey lines in boxes; draw the real object with its real text as an `artefact` (rule 4)")
    # v4.10 · the payoff frame (SKILL.md rule 16)
    po = spec.get("payoff_frame")
    if not po: g.append("no `payoff_frame`: draw the moment the signature's decision resolves (the blocked thing cleared, the number moving) as its own frame (rule 16)")
    elif po not in {p["id"] for p in spec["pages"]}: g.append(f"payoff_frame '{po}' is not a page id")
    # v4.10 · states that tell the truth: a blocked action looks blocked
    BLOCKED = re.compile(r"\b(blocked|is blocked|stays? disabled|waiting for|until)\b", re.I)
    for p in spec["pages"]:
        for b in flat([b for r in p.get("rows", []) for b in r] + [k for r in p.get("rows", []) for b in r for k in b.get("blocks", [])]):
            if b["type"] in ("next", "button") and BLOCKED.search(" ".join(str(b.get(k, "")) for k in ("text", "sub", "note"))) and not b.get("disabled") and "approved" not in json.dumps(p.get("title", "")).lower():
                out.append(f"{p['id']}/{b.get('id', b['type'])}: the text says the action is blocked but the button is drawn live; set `disabled: true` (or draw the frame after it clears)")
    # v4.10 · filler that reads as generated (no AI slop)
    SLOP = re.compile(r"^(quick actions|recent activity|insights?|at a glance|welcome back.*|key metrics|overview|stats|highlights|dashboard)$", re.I)
    for p in spec["pages"]:
        for b in flat([b for r in p.get("rows", []) for b in r]):
            if SLOP.match(str(b.get("title", "")).strip()): out.append(f"{p['id']}/{b.get('id', b['type'])}: '{b['title']}' is a filler title; say what this block holds in the person's words")
    # v4.10 · every listed view can be drawn
    for p in base:
        for b in flat([b for r in p.get("rows", []) for b in r]):
            for v in b.get("views", []) or []:
                if isinstance(v, str) and v != b.get("view") and not any(q.get("alt_view_of") == p["id"] and q.get("view") == v for q in spec["pages"]):
                    out.append(f"{p['id']}/{b.get('id', '')}: view '{v}' is neither drawn as a frame nor given a kind; write it as {{\"name\": \"{v}\", \"kind\": \"board|table|wall|list\", \"group_by\": \"…\"}} so the renderer draws it")
    # v4.9 · more than one way to look at the hero data (SKILL.md rule 14)
    DATA = {"media", "table", "list", "work", "board", "calendar", "tree"}
    heroes = [b for p in base for b in flat([b for r in p.get("rows", []) for b in r]) if b.get("hero") and b["type"] in DATA]
    if heroes and not any(len(b.get("views") or []) >= 2 for b in heroes):
        g.append("no hero list, table, grid or board offers another view (`views`); give the main data sets 2 or 3 ways to look at them (SKILL.md rule 14)")
    if heroes and not any(p.get("alt_view_of") for p in spec["pages"]):
        g.append("no frame draws an alternative view (`alt_view_of`); draw at least one, e.g. the worklist as a board or a timeline (SKILL.md rule 14)")
    for w in out: print("check:", w)
    for w in (g if legacy else []): print("warning:", w)
    return out + (g if legacy else [])

def _records(b):
    """The items of a hero block as plain records, so the same items can be drawn in another view."""
    out = []
    for it in b.get("items", []) or []:
        if isinstance(it, str): out.append({"title": it, "meta": "", "status": ""}); continue
        tags = it.get("tags") or []
        out.append({"title": it.get("title") or it.get("label", ""), "meta": it.get("meta") or it.get("why", ""),
                    "status": it.get("status") or it.get("badge") or (tags[0] if tags else ""), "tags": tags})
    for r in b.get("rows", []) or []:
        if isinstance(r, list): out.append({"title": str(r[0]), "meta": " · ".join(str(v) for v in r[1:3]), "status": str(r[-1]) if len(r) > 1 else ""})
    for col in b.get("columns", []) if b.get("type") == "board" else []:
        for cd in col.get("cards", []): out.append({"title": cd.get("title", ""), "meta": cd.get("meta", ""), "status": col.get("title", "")})
    return out
def views_sheet(spec):
    """v4.10 · every listed view of every hero data set drawn from the same items (SKILL.md rule 14)."""
    tiles = []
    for p in spec["pages"]:
        for b in flat([b for r in p.get("rows", []) for b in r]):
            for v in b.get("views", []) or []:
                if not isinstance(v, dict) or v.get("name") == b.get("view"): continue
                recs = _records(b)
                if not recs: continue
                kind, key = v.get("kind", "table"), v.get("group_by", "status")
                c = Canvas(1180, 380); vb = {"title": f"{b.get('component')} · {v['name']}", "id": "view"}
                if kind == "board":
                    groups = OrderedDict()
                    for r in recs:
                        v_ = r.get(key) or ""
                        if isinstance(v_, list): v_ = v_[0] if v_ else ""
                        g = str(v_).split("·")[-1].strip() if key == "meta" else str(v_)
                        groups.setdefault(g or "Other", []).append(r)
                    cols = [{"title": g, "count": len(rs), "cards": [{"title": r["title"], "meta": r["meta"][:40]} for r in rs[:3]]} for g, rs in list(groups.items())[:5]]
                    c.text(16, 18, vb["title"], BOLD(13)); b_board(c, 16, 40, 1148, 324, {"columns": cols})
                elif kind in ("wall", "grid"):
                    b_media(c, 0, 0, 1180, 380, dict(vb, cols=6, ratio=1, items=[{"title": r["title"], "meta": r["meta"][:30], "tags": r.get("tags", [])[:2]} for r in recs[:6]]))
                elif kind == "list":
                    b_list(c, 0, 0, 1180, 380, dict(vb, thumb=b.get("thumb") or b["type"] == "media", items=[{"title": r["title"], "meta": r["meta"], "status": r["status"]} for r in recs[:5]]))
                else:
                    cols_ = v.get("columns") or ["Name", "Detail", "Status"]; nr = min(7, len(recs)); c = Canvas(1180, 44 + 32 + nr * 36 + 12)
                    b_table(c, 0, 0, 1179, 44 + 32 + nr * 36 + 11, dict(vb, columns=cols_, thumb=b.get("thumb") or b["type"] == "media", status_col=cols_[-1], rows=[[r["title"], r["meta"], r["status"]][:len(cols_)] for r in recs[:7]]))
                tiles.append((p["id"], v, c.im))
    if not tiles: return None
    sheet = Image.new("RGB", (1220, 60 + sum(im.height + 44 for _, _, im in tiles)), "#ffffff"); d = ImageDraw.Draw(sheet)
    d.text((20, 28), "Views · the same items, other ways to look at them", font=MONO(14), fill=DARK, anchor="lm"); y = 60
    for k, (pid, v, im) in enumerate(tiles):
        d.text((20, y + 14), f"{pid} · {v['name']} ({v.get('kind', 'table')}{', grouped by ' + v['group_by'] if v.get('group_by') else ''})", font=BOLD(13), fill=INK, anchor="lm"); sheet.paste(im, (20, y + 30)); y += im.height + 44
    return sheet

STOPW = set("the a an of and to in on with for as its their is are by at from one each every this that".split())
def _w(t): return {w for w in re.findall(r"[a-z]+", (t or "").lower()) if w not in STOPW and len(w) > 2}
def _same(a, b):
    wa, wb = _w(a), _w(b)
    return bool(wa and wb) and len(wa & wb) / min(len(wa), len(wb)) >= 0.6
def register_check(spec, path):
    """v4.10 · the signature and the home must not repeat an app already made (the design system's register)."""
    out = []
    try: reg = json.load(open(path))
    except Exception as e: return [f"register not read ({e}); pass the shared design-system register (~/.local/poc-studio/design-register.json) only when it exists"]
    me = (spec.get("client") or "").split()[:1]; sig = (spec.get("signature") or {}).get("name", "")
    home = next((p for p in spec["pages"] if not re.search(r"\d[a-z]$", p["id"])), {}); hs = f"{home.get('shape', '')}"
    for e in reg:
        own = (e.get("client") or "").split()[:1] == me
        if own and e.get("verdict") != "weak": continue
        if _same(sig, e.get("signature_form")): out.append(f"the signature repeats {e.get('client')} ({e.get('app')}): '{e.get('signature_form')}'; find this client's own object")
        if _same(hs, e.get("home_layout")): out.append(f"the home repeats {e.get('client')} ({e.get('app')}): '{e.get('home_layout')}'; give the home the shape this work needs")
    return out
def main(spec_path, out, register=None):
    spec = json.load(open(spec_path)); validate(spec); lint(spec)
    if register:
        for w_ in register_check(spec, register): print("check:", w_)
    os.makedirs(os.path.join(out, "png"), exist_ok=True)
    AGENT[0] = spec.get("app", {}).get("agent", "AI")
    imgs = [render_page(spec["app"], p, out) for p in spec["pages"]]
    for w_ in RENDER_ISSUES: print("check:", w_)
    vs = views_sheet(spec)
    if vs is not None: vs.save(os.path.join(out, "png", "VIEWS.png")); imgs.append(vs)
    nav = spec.get("nav_options") or []
    if nav and spec["pages"]:  # v4.9 · the navigation options drawn on the home, side by side, chosen one marked
        import copy, tempfile
        home = next((p for p in spec["pages"] if p.get("layout") != "map"), spec["pages"][0]); tiles = []
        with tempfile.TemporaryDirectory() as td:
            os.makedirs(os.path.join(td, "png"))
            for k, n in enumerate(nav[:4]):
                pg = copy.deepcopy(home); pg["id"] = f"NAV-{k + 1}"; pg["shell"] = n.get("shell", "left")
                im = render_page(spec["app"], pg, td); tiles.append((n, im.resize((640, int(640 * im.height / im.width)))))
        th = max(t.height for _, t in tiles); sheet = Image.new("RGB", (660 * len(tiles) + 20, th + 150), "#ffffff"); d = ImageDraw.Draw(sheet)
        d.text((20, 24), "Navigation options · " + home["id"] + " · " + home["title"], font=MONO(14), fill=DARK, anchor="lm")
        for k, (n, t) in enumerate(tiles):
            x = 20 + k * 660; sheet.paste(t, (x, 50))
            if n.get("chosen"): d.rectangle([x - 4, 46, x + 644, 54 + t.height], outline=DARK, width=4)
            d.text((x, th + 70), f"{k + 1} · {n.get('name', n.get('shell'))}" + ("  · CHOSEN" if n.get("chosen") else ""), font=BOLD(15), fill=INK, anchor="lm")
            for i, ln in enumerate(wrap(Canvas(10, 10), n.get("why", ""), REG(12), 630)[:4]): d.text((x, th + 94 + i * 17), ln, font=REG(12), fill=DARK, anchor="lm")
        sheet.save(os.path.join(out, "png", "NAV-options.png")); imgs.append(sheet)
    slug = spec.get("slug", "app")
    # PDF: one page per wireframe, each scaled onto A4 landscape-ish width
    pdf = [im.convert("RGB") for im in imgs]; pdf[0].save(os.path.join(out, f"{slug}-wireframes.pdf"), save_all=True, append_images=pdf[1:], resolution=110)
    json.dump(manifest(spec), open(os.path.join(out, "wireframe-manifest.json"), "w"), indent=2)
    print(f"{len(imgs)} pages → {out}/png, {slug}-wireframes.pdf, wireframe-manifest.json")

if __name__ == "__main__":
    a = sys.argv[1:]; reg = None
    if "--register" in a: i = a.index("--register"); reg = a[i + 1]; a = a[:i] + a[i + 2:]
    main(a[0], a[1], reg)
