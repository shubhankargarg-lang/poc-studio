# kit/narrate.py: US-English narration, offline (Kokoro). One WAV per scene, split into beats at each
# action's `at` phrase so every cue time is exact. Writes build/audio/<scene>.wav + build/narration.json.
# usage: python3 kit/narrate.py            python3 kit/narrate.py a3 b1   (re-voice only those scenes)
import json, os, sys, re
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

brief = json.load(open("brief.json")); story = json.load(open("story.json"))
v = brief.get("voice", {}); voice = v.get("id") or "af_heart"  # always US English, female (alternates: af_bella, af_nicole)
speed = v.get("speed") or (0.95 if brief.get("persona") == "technical" else 1.0)
MODEL = os.environ.get("KOKORO_DIR", "models")
k = Kokoro(f"{MODEL}/kokoro-v1.0.onnx", f"{MODEL}/voices-v1.0.bin")
os.makedirs("build/audio", exist_ok=True)
out = json.load(open("build/narration.json")) if os.path.exists("build/narration.json") else {}
only = set(sys.argv[1:])
GAP = 0.08  # seconds of silence between beats

def say(text):
    # Spell things the way they should sound; keep the written script clean.
    for a, b in brief.get("pronounce", {}).items(): text = re.sub(rf"\b{re.escape(a)}\b", b, text)
    s, sr = k.create(text, voice=voice, speed=speed, lang="en-us")
    nz = np.where(np.abs(s) > 0.01)[0]                        # trim the model's leading/trailing silence
    if len(nz): s = s[max(0, nz[0] - int(.03 * sr)): nz[-1] + int(.06 * sr)]
    return s, sr

for act in story["acts"]:
    for sc in act["scenes"]:
        if only and sc["id"] not in only: continue
        text = sc["narration"].strip()
        cuts = sorted({text.index(a["at"]) for a in sc.get("actions", []) if a.get("at")} - {0})
        bounds = [0] + cuts + [len(text)]
        pieces, cues, t, sr = [], {}, 0.0, 24000
        for i in range(len(bounds) - 1):
            beat = text[bounds[i]:bounds[i + 1]].strip()
            if not beat: continue
            for a in sc.get("actions", []):
                if a.get("at") and bounds[i] <= text.index(a["at"]) < bounds[i + 1]: cues[a["at"]] = round(t, 3)
            s, sr = say(beat); pieces += [s, np.zeros(int(GAP * sr), dtype=s.dtype)]; t += len(s) / sr + GAP
        audio = np.concatenate(pieces)
        sf.write(f"build/audio/{sc['id']}.wav", audio, sr)
        out[sc["id"]] = {"dur": round(len(audio) / sr, 3), "cues": cues, "voice": voice}
        print(f"{sc['id']}: {out[sc['id']]['dur']:.1f}s  cues={cues}")
json.dump(out, open("build/narration.json", "w"), indent=2)
total = sum(v["dur"] for v in out.values()); print(f"total narration {total/60:.1f} min, voice {voice}")
