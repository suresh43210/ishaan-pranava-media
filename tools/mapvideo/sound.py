#!/usr/bin/env python3
"""Sound design for Ishaan Pranava story videos: original procedural music + sound effects + ducking (no samples, no licences needed).

Run in the work folder AFTER mix_audio.py and BEFORE assemble.sh:
    python3 /home/claude/ishaan-pranava-media/tools/mapvideo/sound.py
Optional inputs in the work folder (auto defaults are used when missing):
  mood.json        per-scene music: {"c01": {"mood": "story"}, "c06": {"mood": "danger"}, ...} or full chord settings
  sfx_events.json  [[scene, phrase, kind], ...] kind = hit | danger | soft_danger | melody
                   default: hit on every spec item with "at"; danger on red items; melody on the CTA follow line
Levels (env): MUSIC_DB (default -6), SFX_DB (default -5). Ducked music sits about 16 LU under the voice.
Writes audio/music.wav, audio/sfx.wav, audio/sfx_times.json; voice-only track kept as audio/voice_only.wav; final mix -> audio/voice.wav (-14 LUFS).
Re-running is safe: it always mixes from audio/voice_only.wav.
"""
import json, os, subprocess, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
ROOT = os.getcwd()
AUD = json.load(open("audio/durations.json"))
ORDER = list(AUD)
STARTS, t = {}, 0.0
for s in ORDER: STARTS[s] = t; t += AUD[s]["scene"]
PRESETS = {
 "story":   {"chords": ["Am", "F", "C", "G"], "bpm": 78, "arp": 0.8, "steps": 4, "pattern": [0, 2, 1, 2], "bright": 0.35, "bass": 0.6},
 "question": {"chords": ["Fsus2", "Gsus4"], "bpm": 78, "bright": 0.3, "arp": 0.5, "steps": 2, "pattern": [2, 1]},
 "facts":   {"chords": ["C", "G", "Am", "F"], "bpm": 90, "arp": 1.0, "bright": 0.6, "bass": 0.9, "kick": 0.7},
 "danger":  {"chords": ["Dm", "Bb", "Gm", "A"], "bpm": 74, "bright": 0.22, "drone": 1.0, "arp": 0.35, "steps": 2, "pattern": [0, 2], "gain": 0.9},
 "hope":    {"chords": ["F", "G", "C", "Am"], "bpm": 92, "arp": 1.1, "bright": 0.7, "bass": 0.9, "kick": 0.7},
 "tension": {"chords": ["Am", "Esus4"], "bpm": 76, "bright": 0.3, "arp": 0.5, "steps": 4, "pattern": [0, 2, 1, 2], "drone": 0.5},
 "view":    {"chords": ["C", "Am", "F", "G"], "bpm": 84, "arp": 0.9, "bright": 0.55, "bass": 0.8, "kick": 0.4},
 "cta":     {"chords": ["F", "G", "Cadd9", "Cadd9"], "bpm": 96, "arp": 1.1, "bright": 0.75, "bass": 1.0, "kick": 0.8},
}
_raw = json.load(open("mood.json")) if os.path.exists("mood.json") else {}
_spec = json.load(open("spec.json")) if os.path.exists("spec.json") else {}
MOOD = {}
_spoken = [s for s in ORDER if AUD[s]["audio"] > 0]
for i, s in enumerate(_spoken):
    v = _raw.get(s)
    if isinstance(v, dict) and "chords" in v: MOOD[s] = v
    else:
        m = (v or {}).get("mood") if isinstance(v, dict) else v
        if not m:  # default arc: story -> question -> facts ... -> view -> cta
            typ = _spec.get(s, {}).get("type")
            m = "cta" if typ == "cta" else "story" if i == 0 else "question" if i == 1 else "facts"
        MOOD[s] = dict(PRESETS[m])
TOTAL = t
N = int(TOTAL * SR) + SR
rng = np.random.default_rng(7)

def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def lp(x, fc, order=2): return sosfilt(butter(order, fc, "low", fs=SR, output="sos"), x)
def hp(x, fc, order=2): return sosfilt(butter(order, fc, "high", fs=SR, output="sos"), x)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x)

CH = {  # chord tones (MIDI)
 "Am": [57, 60, 64], "F": [53, 57, 60], "C": [48, 55, 60, 64], "G": [55, 59, 62], "Dm": [50, 53, 57],
 "Bb": [46, 53, 58, 62], "Gm": [55, 58, 62], "A": [57, 61, 64], "Fsus2": [53, 55, 60], "Gsus4": [55, 60, 62],
 "Esus4": [52, 57, 59], "Em": [52, 55, 59], "Fmaj7": [53, 57, 60, 64], "Cadd9": [48, 55, 62, 64],
}

def pad(notes, dur, bright=0.5):
    n = int(dur * SR); tt = np.arange(n) / SR; out = np.zeros(n)
    for m in notes:
        f = mtof(m)
        for det in (-0.12, 0.0, 0.11):
            ff = f * 2 ** (det / 12)
            ph = rng.uniform(0, 2 * np.pi)
            out += np.sin(2 * np.pi * ff * tt + ph) * 0.5 + np.sin(4 * np.pi * ff * tt + ph) * 0.18 * bright + np.sin(6 * np.pi * ff * tt + ph) * 0.07 * bright
    env = np.minimum(1, tt / 0.9) * np.minimum(1, (dur - tt) / 0.9).clip(0)
    out = lp(out, 900 + 1400 * bright)
    return out * env / (len(notes) * 3)

def pluck(m, dur=1.4, vel=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR; f = mtof(m)
    x = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(4 * np.pi * f * tt) * np.exp(-tt * 6) + 0.12 * np.sin(6 * np.pi * f * tt) * np.exp(-tt * 9))
    return x * np.exp(-tt * 3.2) * np.minimum(1, tt / 0.004) * vel

def bass(m, dur):
    n = int(dur * SR); tt = np.arange(n) / SR; f = mtof(m - 12)
    return np.sin(2 * np.pi * f * tt) * np.minimum(1, tt / 0.05) * np.minimum(1, (dur - tt) / 0.3).clip(0)

def kick():
    n = int(0.35 * SR); tt = np.arange(n) / SR
    f = 50 + 70 * np.exp(-tt * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)

def hat():
    n = int(0.06 * SR); tt = np.arange(n) / SR
    return hp(rng.standard_normal(n), 7000) * np.exp(-tt * 70)

def add(buf, x, at):
    i = int(at * SR); j = min(len(buf), i + len(x))
    if j > i: buf[i:j] += x[: j - i]

def scene_music(sc, dur):
    cfg = MOOD[sc]; bpm = cfg.get("bpm", 84); beat = 60 / bpm; bar = beat * 4
    seg = np.zeros(int((dur + 2.5) * SR))
    prog = cfg["chords"]; i = 0; t0 = 0.0
    while t0 < dur + 0.5:
        ch = CH[prog[i % len(prog)]]
        add(seg, pad([m + 12 for m in ch], bar + 1.0, cfg.get("bright", 0.5) + 0.25) * cfg.get("pad", 1.0), t0)
        if cfg.get("bass", 0): add(seg, bass(ch[0], bar) * 0.22 * cfg["bass"], t0)
        if cfg.get("arp", 0):
            pat = cfg.get("pattern", [0, 1, 2, 1])
            steps = cfg.get("steps", 8)
            for k in range(steps):
                note = ch[pat[k % len(pat)] % len(ch)] + 24
                add(seg, pluck(note, vel=0.9 if k % 4 == 0 else 0.6) * 0.22 * cfg["arp"], t0 + k * bar / steps)
        if cfg.get("kick", 0):
            for k in range(4):
                if k in (0, 2): add(seg, kick() * 0.25 * cfg["kick"], t0 + k * beat)
                add(seg, hat() * 0.10 * cfg["kick"], t0 + k * beat + beat / 2)
        if cfg.get("drone", 0):
            add(seg, lp(pad([ch[0] - 12], bar + 1.0, 0.1), 220) * 1.8 * cfg["drone"], t0)
        t0 += bar; i += 1
    return seg

music = np.zeros(N)
for sc in ORDER:
    if sc not in MOOD: continue
    d = AUD[sc]["scene"]; seg = scene_music(sc, d)
    # fade in 0.6 s, fade out over the 1.2 s that overlaps the next scene
    n_in = int(0.6 * SR); seg[:n_in] *= np.linspace(0, 1, n_in)
    end = int((d + 1.2) * SR); seg[end:] = 0
    fo = int(1.2 * SR); s0 = end - fo; seg[s0:end] *= np.linspace(1, 0, fo)
    add(music, seg * MOOD[sc].get("gain", 1.0), max(0, STARTS[sc] - 0.3))
music = np.stack([music, music], 1)
# gentle stereo width: delay right channel slightly
music[:, 1] = np.roll(music[:, 1], int(0.012 * SR))
music = music / (np.abs(music).max() + 1e-9) * 0.5

# ---------------- sound effects ----------------
def whoosh(d=0.55):
    n = int(d * SR); tt = np.arange(n) / SR
    x = rng.standard_normal(n); env = np.sin(np.pi * tt / d) ** 2
    lo = bp(x, 300, 2500) * env; hi = bp(x, 1500, 6000) * env * np.linspace(0, 1, n)
    return (lo * 0.6 + hi * 0.4) * 0.5

def verb(x, d=0.09, fb=0.45, n=5):
    out = np.concatenate([x, np.zeros(int(d * n * SR))]); y = out.copy()
    for k in range(1, n): y[int(d * k * SR):] += out[: len(out) - int(d * k * SR)] * fb ** k
    return y

def hit():  # accent on stressed words: thump + bright snap + short tail
    n = int(0.45 * SR); tt = np.arange(n) / SR
    thump = np.sin(2 * np.pi * np.cumsum(70 + 120 * np.exp(-tt * 40)) / SR) * np.exp(-tt * 12)
    snap = hp(rng.standard_normal(n), 2500) * np.exp(-tt * 60) * 0.7
    tone = (np.sin(2 * np.pi * 1320 * tt) + 0.5 * np.sin(2 * np.pi * 1980 * tt)) * np.exp(-tt * 14) * 0.35
    return verb(thump * 0.9 + snap + tone) * 0.55

def danger():  # warning: low brass-like hit + two alarm beeps
    n = int(1.1 * SR); tt = np.arange(n) / SR
    saw = sum(np.sin(2 * np.pi * 73.4 * k * tt) / k for k in range(1, 14)) + sum(np.sin(2 * np.pi * 77.8 * k * tt) / k for k in range(1, 14)) * 0.7
    braam = lp(np.tanh(saw * 1.6), 1600) * np.exp(-tt * 2.6) * np.minimum(1, tt / 0.01)
    out = braam * 0.55
    for k, f in enumerate([988, 932]):
        b = int(0.16 * SR); tb = np.arange(b) / SR
        sq = np.sign(np.sin(2 * np.pi * f * tb)) * np.minimum(1, tb / 0.005) * np.minimum(1, (0.16 - tb) / 0.02)
        add(out, lp(sq, 4000) * 0.22, 0.05 + k * 0.2)
    return out

def melody():  # short bell motif for hopeful / positive moments
    out = np.zeros(int(2.0 * SR))
    for k, m in enumerate([76, 79, 83, 88]):
        nn = int(1.4 * SR); tt = np.arange(nn) / SR; f = mtof(m)
        bell = (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt * 6) + 0.25 * np.sin(2 * np.pi * f * 5.4 * tt) * np.exp(-tt * 10)) * np.exp(-tt * 2.8)
        add(out, bell * 0.3, k * 0.13)
    return verb(out, 0.12, 0.35, 4)

def soft_danger():
    return danger() * 0.6

import importlib.util
sys.path.insert(0, ROOT)
spec_ = importlib.util.spec_from_file_location("story", f"{ROOT}/story.py"); S = importlib.util.module_from_spec(spec_); spec_.loader.exec_module(S)
sfx = np.zeros(N)
for i, sc in enumerate(ORDER):
    if i > 0: add(sfx, whoosh(), STARTS[sc] - 0.25)
EV = []
def default_events():
    ev = []
    for sc in ORDER:
        s = _spec.get(sc, {})
        for it in s.get("items", []):
            if it.get("at"): ev.append([sc, it["at"], "danger" if it.get("c") == "red" else "hit"])
        if s.get("type") == "cta":
            if s.get("box_at"): ev.append([sc, s["box_at"], "hit"])
            if s.get("follow_at"): ev.append([sc, s["follow_at"], "melody"])
    return ev
EVENTS = json.load(open("sfx_events.json")) if os.path.exists("sfx_events.json") else default_events()
for sc, phrase, kind in EVENTS:
    t_ = STARTS[sc] + S.at(sc, phrase) - 0.03
    add(sfx, {"hit": hit, "danger": danger, "soft_danger": soft_danger, "melody": melody}[kind](), t_)
    EV.append((round(t_, 1), kind, phrase))
json.dump(EV, open("audio/sfx_times.json", "w"), ensure_ascii=False, indent=0)
sfx = sfx / (np.abs(sfx).max() + 1e-9) * 0.9
sfx = np.stack([sfx, sfx], 1)

wavfile.write("audio/music.wav", SR, (music * 32767).astype(np.int16))
wavfile.write("audio/sfx.wav", SR, (np.clip(sfx, -1, 1) * 32767).astype(np.int16))
if not os.path.exists("audio/voice_only.wav"): os.replace("audio/voice.wav", "audio/voice_only.wav")
MV = float(os.environ.get("MUSIC_DB", "-6")); FX = float(os.environ.get("SFX_DB", "-5"))
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "audio/voice_only.wav", "-i", "audio/music.wav", "-i", "audio/sfx.wav", "-filter_complex",
    f"[0:a]asplit=2[v][sc];[1:a]volume={MV}dB[m];[m][sc]sidechaincompress=threshold=0.05:ratio=3:attack=40:release=450:makeup=1[md];"
    f"[2:a]volume={FX}dB[fx];[v][md][fx]amix=inputs=3:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[o]",
    "-map", "[o]", "-ar", "48000", "audio/voice.wav"], check=True)
print("music+sfx mixed", round(TOTAL, 2))
