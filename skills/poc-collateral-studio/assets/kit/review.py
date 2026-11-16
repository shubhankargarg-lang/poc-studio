# kit/review.py: the review pass for version N. Pulls a frame at every scene's middle and at every cue,
# makes a contact sheet, runs the automatic checks (timing, loading screens, kit/check.py consistency gate),
# and writes review/v<N>/report.md with the coverage matrix for you to complete by LOOKING at every frame.
# usage: python3 kit/review.py 1
import json, os, sys, subprocess, re
from PIL import Image, ImageDraw, ImageFont

n = sys.argv[1]; d = f"review/v{n}"; os.makedirs(f"{d}/frames", exist_ok=True)
brief = json.load(open("brief.json")); story = json.load(open("story.json")); cov = json.load(open("coverage.json"))
placed = json.load(open("build/placed.json")); narr = json.load(open("build/narration.json"))
film = f"out/{brief['slug']}_Demo.mp4"
def grab(t, out):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", film, "-frames:v", "1", "-q:v", "3", out], check=True)

frames = []
for act in story["acts"]:
    for sc in act["scenes"]:
        p = placed.get(sc["id"])
        if not p: frames.append((sc["id"], "NOT RECORDED", None)); continue
        marks = [((p["start"] + p["end"]) / 2, "middle", "mid")] + [(t + 0.9, f'cue "{k}"', re.sub(r'[^a-z0-9]+', '_', k.lower())[:30])
                 for k, t in p["cues"].items()] + [(p["end"] - 0.3, "end", "end")]
        for t, what, tag in sorted(marks):  # in film order
            f = f"{d}/frames/{sc['id']}_{t:07.2f}_{tag}.jpg"; grab(t, f); frames.append((sc["id"], what, f))

# contact sheet, 4 across
shots = [x for x in frames if x[2]]; cols, tw, th = 4, 480, 270
sheet = Image.new("RGB", (cols * tw, ((len(shots) + cols - 1) // cols) * (th + 28)), "#F7F3ED"); dr = ImageDraw.Draw(sheet)
for i, (sid, what, f) in enumerate(shots):
    x, y = (i % cols) * tw, (i // cols) * (th + 28)
    sheet.paste(Image.open(f).resize((tw - 8, th - 8)), (x + 4, y + 4)); dr.text((x + 8, y + th), f"{sid} · {what}", fill="#0F2805")
sheet.save(f"{d}/contact_sheet.jpg", quality=85)

# automatic checks
issues = []
logs = "".join(open(f"build/{x}.log").read() for x in ("record", "build") if os.path.exists(f"build/{x}.log"))
for l in logs.splitlines():
    m = re.match(r"LATE CUE .* by ([\d.]+) s", l)
    if m and float(m.group(1)) >= 1.2: issues.append("MUST FIX (the glow lands after the words): " + l)
    elif re.match(r"(OVERRUN|FAIL|SLOW)", l): issues.append("MUST FIX: " + l)
    elif re.match(r"(LATE CUE|GOTO|WARN)", l): issues.append(l)
chk = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "check.py")], capture_output=True, text=True)
issues.append(("MUST FIX: " if chk.returncode else "") + "consistency gate: " + chk.stdout.strip() + " (details in review/check.md)")
if os.path.exists("review/check.md"): import shutil; shutil.copy("review/check.md", f"{d}/check.md")
if os.path.exists("build/build.log") and "zoompan" in open("build/build.log").read(): issues.append("zoompan found in the ffmpeg graph: forbidden")
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", film], capture_output=True, text=True).stdout)
spoken = sum(narr[s["id"]]["dur"] for a in story["acts"] for s in a["scenes"] if s["id"] in narr)
cards = story.get("opening", {}).get("seconds", 4) + story.get("closing", {}).get("seconds", 5) + sum(a.get("card_seconds", 3) for a in story["acts"])
silence = dur - spoken - cards
if silence > 0.15 * spoken: issues.append(f"{silence:.0f} s of silence on app footage (>{0.15*spoken:.0f} s): tighten actions or pads")

scene_of = {s["id"]: s for a in story["acts"] for s in a["scenes"]}
with open(f"{d}/report.md", "w") as r:
    r.write(f"# Review v{n}: {brief['customer']} · {brief['poc']}\n\nFilm {dur/60:.1f} min · narration {spoken/60:.1f} min · persona {brief['persona']} · voice {brief['voice']}\n\n")
    r.write("## Coverage (fill Status after looking at each frame: shown / missing / wrong screen / unclear)\n\n")
    r.write("| Feature | Screen | Scenes | Frames | Video | Walkthrough | Deck | Swimlane |\n|---|---|---|---|---|---|---|---|\n")
    for c in cov:
        sc = [s for s, v in scene_of.items() if c["id"] in v.get("covers", [])]
        fr = ", ".join(os.path.basename(f) for s in sc for (sid, _, f) in frames if sid == s and f)
        r.write(f"| {c['id']} {c['feature']} | {c['screen']} | {', '.join(sc) or '**none**'} | {fr} | ? | ? | ? | ? |\n")
    r.write("\n## Automatic findings\n\n" + ("\n".join(f"- {i}" for i in issues) or "- none") + "\n")
    r.write("\n## Visual findings (navigation that teleports, dead air, wrong highlight, cut-off line, font fallback)\n\n- \n")
print(f"{d}/report.md, {len(shots)} frames, contact sheet {d}/contact_sheet.jpg, {len(issues)} automatic finding(s)")
