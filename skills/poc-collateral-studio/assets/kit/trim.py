#!/usr/bin/env python3
# kit/trim.py: cut the waiting out of the finished film. Run after kit/build.py.
# A "wait" is a stretch inside a scene where the screen does not change (a loading screen, a spinner frozen,
# an automation still running) AND no one is speaking. Each wait longer than MIN seconds is cut down to KEEP
# seconds on each side, so the film shows the click, a beat, then the result, and the voice-over carries on in
# sync (the cut stretch is silent, so no narration is lost). Opening/closing cards and act cards are never cut:
# only time inside a scene window from build/placed.json is eligible.
# Writes: out/<Slug>_Demo.mp4 (trimmed, replaces the original), build/Demo_untrimmed.mp4 (the original),
#         out/<Slug>_Demo.srt and build/placed.json shifted to the new times, build/trim.json (what was cut).
# usage: python3 kit/trim.py            MIN=1.5 KEEP=0.4 python3 kit/trim.py
import json, os, re, shutil, subprocess, sys

MIN = float(os.environ.get("MIN", "1.5"))    # shortest wait worth cutting (s)
KEEP = float(os.environ.get("KEEP", "0.4"))  # seconds of the wait kept on each side of the cut
brief = json.load(open("brief.json")); slug = brief["slug"]
film, srt = f"out/{slug}_Demo.mp4", f"out/{slug}_Demo.srt"
placed = json.load(open("build/placed.json")) if os.path.exists("build/placed.json") else {}

def run(*a):
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *a], capture_output=True, text=True).stderr

def spans(log, start_key, end_key, end_of_file):
    s = [float(x) for x in re.findall(rf"{start_key}: ?([0-9.]+)", log)]
    e = [float(x) for x in re.findall(rf"{end_key}: ?([0-9.]+)", log)]
    e += [end_of_file] * (len(s) - len(e))  # a stretch still open at the end of the file
    return list(zip(s, e))

dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", film],
                           capture_output=True, text=True).stdout.strip())
frozen = spans(run("-i", film, "-map", "0:v", "-vf", f"freezedetect=n=0.003:d={MIN}", "-f", "null", "-"),
               "lavfi.freezedetect.freeze_start", "lavfi.freezedetect.freeze_end", dur)
silent = spans(run("-i", film, "-map", "0:a", "-af", f"silencedetect=noise=-40dB:d={MIN}", "-f", "null", "-"),
               "silence_start", "silence_end", dur)
windows = [(v["start"], v["end"]) for v in placed.values()] or [(0.0, dur)]

def inter(a, b):
    out = []
    for s1, e1 in a:
        for s2, e2 in b:
            s, e = max(s1, s2), min(e1, e2)
            if e - s >= MIN: out.append((s, e))
    return out

waits = inter(inter(frozen, silent), windows)
cuts = sorted((s + KEEP, e - KEEP) for s, e in waits if e - s - 2 * KEEP > 0.2)
if not cuts:
    print("trim: no waits to cut"); json.dump({"cuts": []}, open("build/trim.json", "w")); sys.exit(0)

keep, t = [], 0.0
for s, e in cuts:
    if s > t: keep.append((t, s))
    t = max(t, e)
if t < dur: keep.append((t, dur))

def newt(x):  # map an old film time to the trimmed film
    removed = sum(min(e, x) - s for s, e in cuts if x > s)
    return round(max(0.0, x - removed), 3)

shutil.copy(film, "build/Demo_untrimmed.mp4")
parts, labels = [], []
for i, (s, e) in enumerate(keep):
    parts.append(f"[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS[v{i}];"
                 f"[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS[a{i}]")
    labels.append(f"[v{i}][a{i}]")
fc = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(keep)}:v=1:a=1[v][a]"
err = run("-y", "-i", "build/Demo_untrimmed.mp4", "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
          "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
          "-movflags", "+faststart", film)
if not os.path.exists(film) or os.path.getsize(film) == 0:
    shutil.copy("build/Demo_untrimmed.mp4", film); sys.exit("trim failed, original kept:\n" + err[-800:])

if os.path.exists(srt):  # shift the clean subtitles
    def fix(m):
        h, mi, s = m.group(1), m.group(2), m.group(3).replace(",", ".")
        x = newt(int(h) * 3600 + int(mi) * 60 + float(s)); hh, r = divmod(x, 3600); mm, ss = divmod(r, 60)
        return f"{int(hh):02}:{int(mm):02}:{ss:06.3f}".replace(".", ",")
    txt = open(srt).read()
    open(srt, "w").write(re.sub(r"(\d\d):(\d\d):(\d\d,\d\d\d)", fix, txt))
for v in placed.values():  # keep review.py's frame times right
    for k in ("start", "voice", "end"): v[k] = newt(v[k])
    v["cues"] = {k: newt(x) for k, x in v.get("cues", {}).items()}
if placed: json.dump(placed, open("build/placed.json", "w"), indent=2)
saved = round(sum(e - s for s, e in cuts), 2)
json.dump({"min": MIN, "keep": KEEP, "cuts": [{"from": round(s, 2), "to": round(e, 2)} for s, e in cuts],
           "seconds_removed": saved}, open("build/trim.json", "w"), indent=2)
print(f"trim: {len(cuts)} wait(s) cut, {saved} s removed; original kept at build/Demo_untrimmed.mp4")
