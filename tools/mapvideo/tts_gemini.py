#!/usr/bin/env python3
"""Nepali voiceover with the Gemini API (AI Studio key), one WAV per narration key.

Usage (from the work folder that holds narration.json):
    python3 tts_gemini.py --keyfile /path/to/gemini.env [--voice Charon] [--model gemini-3.1-flash-tts-preview] [keys...]

- The key is read from the file (line GEMINI_API_KEY=...) and never printed; it is masked in any error text.
- Output: raw/<key>.wav (24 kHz mono). Style prompt: style_news_anchor.txt next to this script.
- Per-scene tone (default when tone.json exists in the work folder): style_documentary.txt + the scene's tone line,
  e.g. {"c01": "storytelling and empathetic, a little slower", "c06": "serious and cautionary"}.
  Presets you can name instead of a sentence: story, question, facts, policy, positive, caution, grave, hope, sceptic, view, cta.
- A clip that is far too short for its text (cut-off generation) is retried automatically.
"""
import argparse, base64, json, os, re, sys, time, urllib.error, urllib.request, wave

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--keyfile", required=True)
ap.add_argument("--voice", default="Charon")
ap.add_argument("--model", default="gemini-3.1-flash-tts-preview")
ap.add_argument("--narration", default="narration.json")
ap.add_argument("--style", default=os.path.join(HERE, "style_news_anchor.txt"))
ap.add_argument("--tones", default="tone.json")
ap.add_argument("keys", nargs="*")
a = ap.parse_args()

m = re.search(r'GEMINI_API_KEY\s*=\s*["\']?([^\s"\']+)', open(a.keyfile).read())
if not m: sys.exit("GEMINI_API_KEY line not found in keyfile")
KEY = m.group(1)
STYLE = open(a.style).read()
PRESET = {
 "story": "storytelling and empathetic, a little slower and softer, as if describing a real person's struggle",
 "question": "curious and inviting; rising intonation on the question; a short pause before the last sentence",
 "facts": "clear, factual and authoritative; steady newsroom pace; firm emphasis on the numbers",
 "policy": "crisp and brisk, like announcing a policy change; give each number its own weight",
 "positive": "practical and positive, explaining a new solution step by step",
 "caution": "serious and cautionary, slightly lower pitch and slower pace; measured, not alarmist",
 "grave": "grave and analytical; calm, thoughtful delivery",
 "hope": "hopeful and slightly upbeat, a sense of doors starting to open; still professional",
 "sceptic": "restrained and matter-of-fact with mild scepticism",
 "view": "thoughtful, confident and advisory, speaking peer-to-peer to bankers",
 "cta": "warm and direct, speaking straight to the viewer; friendly invitation, energetic but not shouting",
}
TONES = json.load(open(a.tones)) if os.path.exists(a.tones) else {}
DOC = open(os.path.join(HERE, "style_documentary.txt")).read()
def style_for(k):
    if k not in TONES: return STYLE
    t = PRESET.get(TONES[k], TONES[k])
    return DOC + "Tone for this part: " + t + ". Read exactly this text, nothing else:"
LINES = json.load(open(a.narration))
os.makedirs("raw", exist_ok=True)

def mask(s): return s.replace(KEY, "<key>")

def synth(k, text, tries=0):
    body = {"contents": [{"parts": [{"text": style_for(k) + text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": a.voice}}}}}
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{a.model}:generateContent",
                                 data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": KEY})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=180) as r: data = json.load(r)
            pcm = base64.b64decode(data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
            with wave.open(f"raw/{k}.wav", "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
            secs = len(pcm) / 48000
            if secs < 0.22 * len(text.split()) and tries < 3:  # cut-off generation
                print(f"short {k} {secs:.2f}s, retrying", flush=True); return synth(k, text, tries + 1)
            print(f"ok {k} {secs:.2f}s", flush=True); return
        except urllib.error.HTTPError as e:
            print(f"ERR {k} HTTP {e.code} {mask(e.read().decode()[:300])}", flush=True)
            if e.code in (429, 500, 503): time.sleep(8 * (attempt + 1)); continue
            sys.exit(1)
    sys.exit(f"ERR {k}: retries exhausted")

for k in (a.keys or list(LINES)): synth(k, LINES[k])
