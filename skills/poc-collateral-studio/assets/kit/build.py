# kit/build.py: acts + narration + cards + subtitles + badge -> out/<Slug>_Demo.mp4 and .srt
# Cuts and cross-dissolves only (no dip to black). No zoompan, no animated scale/crop: app footage is shown
# exactly as recorded. Subtitles move to the top of the frame whenever the thing being clicked or highlighted
# sits in the lower part of the screen, so a caption never covers what the voice is talking about.
# usage: python3 kit/build.py
import json, os, re, subprocess
import numpy as np

FPS, AR = 30, 48000
XF = 0.5             # cross-dissolve between segments (seconds)
LEAD = XF + 0.15     # still frames held before each act so the dissolve never eats footage or a word
LOW = 0.70           # a click/highlight below 70% of the frame height sends the caption to the top
brief = json.load(open("brief.json")); story = json.load(open("story.json"))
tl = json.load(open("build/timeline.json")); narr = json.load(open("build/narration.json"))
slug = brief["slug"]; os.makedirs("build/seg", exist_ok=True); os.makedirs("out", exist_ok=True)
log = open("build/build.log", "w")
def sh(*a):
    log.write(" ".join(map(str, a)) + "\n"); subprocess.run(["ffmpeg", "-y", "-v", "error", *map(str, a)], check=True)
def dur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                capture_output=True, text=True).stdout)
ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", FPS,
       "-c:a", "aac", "-b:a", "192k", "-ar", AR, "-ac", 2]

def find_flash(video, est):
    """Return the time of the first frame after the magenta sync flash, or None."""
    start = max(0.0, est - 3)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-i", video, "-t", "6", "-vf", f"fps={FPS},scale=32:18",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 18, 32, 3).astype(int)
    hit = [(np.abs(f[..., 0] - 255) + f[..., 1] + np.abs(f[..., 2] - 255)).mean() < 60 for f in fr]
    return start + (max(i for i, h in enumerate(hit) if h) + 1) / FPS if any(hit) else None

def card(png, seconds, out):
    sh("-loop", 1, "-t", seconds, "-i", png, "-f", "lavfi", "-t", seconds, "-i", f"anullsrc=r={AR}:cl=stereo",
       "-vf", f"fps={FPS},format=yuv420p", *ENC, "-shortest", out)

def captions(text, d, start):
    """Split a scene's line into caption chunks (sentence, then clause if long), timed by length."""
    parts = []
    for s in [x for x in re.split(r"(?<=[.!?])\s+", text.strip()) if x]:
        if len(s) <= 84: parts.append(s); continue
        chunk = ""
        for c in re.split(r"(?<=[,;:])\s+", s):
            if chunk and len(chunk) + len(c) > 84: parts.append(chunk); chunk = c
            else: chunk = f"{chunk} {c}".strip()
        if chunk: parts.append(chunk)
    total, pos, out = sum(len(x) for x in parts), 0, []
    for x in parts:
        a = start + d * pos / total; pos += len(x); out.append((a, start + d * pos / total, x))
    return out

segments, subs, placed, lows = [], [], {}, []
t = 0.0  # where the next segment starts in the final film (segments overlap by XF)
def add(f):
    global t
    start = t; segments.append((f, dur(f))); t = start + segments[-1][1] - XF; return start

card("build/cards/opening.png", story.get("opening", {}).get("seconds", 4), "build/seg/00_opening.mp4"); add("build/seg/00_opening.mp4")
for act in story["acts"]:
    a = tl[act["id"]]
    card(f"build/cards/act_{act['id']}.png", act.get("card_seconds", 3), f"build/seg/{act['id']}_0card.mp4")
    add(f"build/seg/{act['id']}_0card.mp4")
    flash = find_flash(a["video"], a["clock"])
    if flash is None: print(f"WARN act {act['id']}: no sync flash found; using recorded clock (audio may drift by ~0.2 s)")
    else: print(f"act {act['id']}: synced on the flash ({flash - a['clock']:+.2f} s)")
    v0 = flash if flash is not None else a["clock"]; length = a["end"] - a["clock"]
    act_start = t  # film time of this act segment's first frame
    inputs, chains = ["-ss", v0, "-t", length, "-i", a["video"]], []
    for i, s in enumerate(a["scenes"], start=1):
        voice = s.get("voice", s["start"])
        ms = int((max(0, voice - a["clock"]) + LEAD) * 1000)
        inputs += ["-i", f"build/audio/{s['id']}.wav"]
        chains.append(f"[{i}:a]aresample={AR},aformat=channel_layouts=stereo,adelay={ms}:all=1[a{i}]")
        sc = next(x for x in act["scenes"] if x["id"] == s["id"])
        f0 = act_start + ms / 1000; film = lambda x: act_start + LEAD + (x - a["clock"])
        placed[s["id"]] = {"act": act["id"], "start": round(film(s["start"]), 2), "voice": round(f0, 2),
                           "end": round(film(s["end"]), 2),
                           "cues": {k: round(f0 + v, 2) for k, v in narr[s["id"]]["cues"].items()}}
        lows += [(film(m["t"]), film(m["t"]) + 3.0) for m in s.get("marks", []) if m["y1"] > LOW * 1080]
        subs += captions(sc["narration"], narr[s["id"]]["dur"], f0)
    n = len(a["scenes"])
    mix = "".join(f"[a{i}]" for i in range(1, n + 1)) + f"amix=inputs={n}:normalize=0:dropout_transition=0,apad[aout]"
    out = f"build/seg/{act['id']}_1act.mp4"
    sh(*inputs, "-filter_complex", ";".join(chains + [mix]), "-map", "0:v", "-map", "[aout]",
       "-vf", f"fps={FPS},scale=1920:1080,format=yuv420p,tpad=start_duration={LEAD}:start_mode=clone",
       *ENC, "-t", length + LEAD, out)
    add(out)
card("build/cards/closing.png", story.get("closing", {}).get("seconds", 5), "build/seg/99_closing.mp4"); add("build/seg/99_closing.mp4")

json.dump(placed, open("build/placed.json", "w"), indent=2)  # where each scene sits in the final film (for review)
def ts(x): h, r = divmod(x, 3600); m, s = divmod(r, 60); return f"{int(h):02}:{int(m):02}:{s:06.3f}".replace(".", ",")
srt = f"out/{slug}_Demo.srt"
with open(srt, "w") as f:  # clean SRT for upload / players
    for i, (a, b, x) in enumerate(subs, 1): f.write(f"{i}\n{ts(a)} --> {ts(b - 0.05)}\n{x}\n\n")
burn = "build/burn.srt"; up = 0; AN8 = "{\\an8}"  # libass: anchor top-centre
with open(burn, "w") as f:  # the burned-in copy: top-anchored where the action is low on screen
    for i, (a, b, x) in enumerate(subs, 1):
        top = any(lo < b and hi > a for lo, hi in lows); up += top
        f.write(f"{i}\n{ts(a)} --> {ts(b - 0.05)}\n{AN8 if top else ''}{x}\n\n")
print(f"captions: {len(subs)}, {up} moved to the top to keep the action visible")

T = json.load(open("brand/tokens.json"))
def ass(hexc, alpha="00"): h = hexc.lstrip("#"); return f"&H{alpha}{h[4:6]}{h[2:4]}{h[0:2]}"
style = (f"FontName=Spectral,FontSize=12,PrimaryColour={ass(T['ink'])},OutlineColour={ass(T['card'], '18')},"
         f"BackColour={ass(T['card'], '18')},BorderStyle=3,Outline=6,Shadow=0,MarginV=26,MarginL=40,MarginR=40")
ins, vch, ach = [], [], []
for k, (f, d) in enumerate(segments): ins += ["-i", f]
off, prev_v, prev_a = 0.0, "[0:v]", "[0:a]"
for k in range(1, len(segments)):
    off += segments[k - 1][1] - XF
    vch.append(f"{prev_v}[{k}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[v{k}]"); prev_v = f"[v{k}]"
    ach.append(f"{prev_a}[{k}:a]acrossfade=d={XF}[a{k}]"); prev_a = f"[a{k}]"
nb = len(segments)
sub = f"{prev_v}subtitles={burn}:fontsdir=fonts:force_style='{style}'[s]" if brief.get("subtitles", True) else f"{prev_v}null[s]"
final = f"out/{slug}_Demo.mp4"
sh(*ins, "-i", "build/cards/badge.png", "-filter_complex", ";".join(vch + ach + [sub, f"[s][{nb}:v]overlay=W-w-28:H-h-22[v]"]),
   "-map", "[v]", "-map", prev_a, *ENC, "-movflags", "+faststart", final)
spoken = sum(narr[s["id"]]["dur"] for a in story["acts"] for s in a["scenes"] if s["id"] in narr); film_len = dur(final)
print(f"{final}: {film_len/60:.1f} min film, {spoken/60:.1f} min narration ({film_len-spoken:.0f} s of cards + silence)")
