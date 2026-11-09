#!/usr/bin/env python3
"""Trim each raw/<key>.wav, group sub-keys into scenes, build audio/durations.json and audio/voice.wav.

Usage (work folder): python3 mix_audio.py [--disclaimer 1.0]
- Keys like c04a, c04b ... are joined into one scene "c04"; audio/durations.json gets c04.offsets (start of each part).
- Each scene = lead + speech + 0.6 s tail. A silent disclaimer scene (default 1.0 s) is appended as the last scene.
- voice.wav is loudness-normalised to -14 LUFS (social-video level).
"""
import argparse, json, re, subprocess
from collections import OrderedDict

ap = argparse.ArgumentParser(); ap.add_argument("--disclaimer", type=float, default=1.0); ap.add_argument("--narration", default="narration.json")
a = ap.parse_args()
def run(*c): subprocess.run(c, check=True)
def dur(f): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)

keys = list(json.load(open(a.narration)))
import os; os.makedirs("audio", exist_ok=True)
for k in keys:
    run("ffmpeg", "-y", "-loglevel", "error", "-i", f"raw/{k}.wav", "-af",
        "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,"
        "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.1,areverse,aresample=48000", f"audio/{k}.wav")

groups = OrderedDict()
for k in keys:
    g = re.sub(r"[a-z]$", "", k) if re.search(r"\d[a-z]$", k) else k
    groups.setdefault(g, []).append(k)

D = OrderedDict()
for g, parts in groups.items():
    if len(parts) > 1:
        offs, t = [], 0.0
        for i, p in enumerate(parts):
            offs.append(round(t, 3)); t += dur(f"audio/{p}.wav") + (0.3 if i == 0 else 0.2)
        ins, fl = [], []
        for i, p in enumerate(parts):
            ins += ["-i", f"audio/{p}.wav"]; fl.append(f"[{i}:a]adelay={int(offs[i] * 1000)}|{int(offs[i] * 1000)}[a{i}]")
        run("ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex",
            ";".join(fl) + ";" + "".join(f"[a{i}]" for i in range(len(parts))) + f"amix=inputs={len(parts)}:normalize=0[o]", "-map", "[o]", f"audio/{g}.wav")
    lead = 0.35 if not D else 0.15
    au = dur(f"audio/{g}.wav")
    D[g] = {"audio": au, "lead": lead, "scene": round(lead + au + 0.6, 2)}
    if len(parts) > 1: D[g]["offsets"] = offs
last = f"c{len(D) + 1:02d}"
D[last] = {"audio": 0, "lead": 0, "scene": a.disclaimer}
json.dump(D, open("audio/durations.json", "w"), indent=1)

ins, fl, t = [], [], 0.0
spoken = [g for g in D if D[g]["audio"] > 0]
for i, g in enumerate(spoken):
    st = t + D[g]["lead"]; ins += ["-i", f"audio/{g}.wav"]
    fl.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,adelay={int(st * 1000)}|{int(st * 1000)}[a{i}]"); t += D[g]["scene"]
t += a.disclaimer
run("ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex",
    ";".join(fl) + ";" + "".join(f"[a{i}]" for i in range(len(spoken))) + f"amix=inputs={len(spoken)}:normalize=0,apad,atrim=0:{t},loudnorm=I=-14:TP=-1.5:LRA=11[o]",
    "-map", "[o]", "-ar", "48000", "audio/voice.wav")
print(json.dumps({g: v["scene"] for g, v in D.items()}), "total", round(t, 2))
