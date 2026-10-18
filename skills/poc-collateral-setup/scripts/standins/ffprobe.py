#!/usr/bin/env python3
# ffprobe stand-in (poc-collateral): built on the imageio-ffmpeg binary. Answers what the collateral kit asks:
#   -show_entries format=duration -of csv=p=0 <file>        -> seconds
#   -show_entries stream=width,height -of csv=p=0 <file>    -> W,H
#   -show_entries format=duration -of default=nw=1:nk=1     -> seconds
import sys, re, subprocess, imageio_ffmpeg
args = sys.argv[1:]; f = args[-1]
ent = args[args.index("-show_entries") + 1] if "-show_entries" in args else "format=duration"
err = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-i", f], capture_output=True, text=True).stderr
if "stream=" in ent:
    m = re.search(r"Video:.*?(\d{2,5})x(\d{2,5})", err)
    if not m: sys.exit(1)
    print(f"{m[1]},{m[2]}")
else:
    m = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", err)
    if not m: sys.exit(1)
    print(int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]))
