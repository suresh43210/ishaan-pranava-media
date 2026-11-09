#!/usr/bin/env python3
"""Nepali voiceover with the Gemini API (AI Studio key), one WAV per narration key.

Usage (from the work folder that holds narration.json):
    python3 tts_gemini.py --keyfile /path/to/gemini.env [--voice Charon] [--model gemini-3.1-flash-tts-preview] [keys...]

- The key is read from the file (line GEMINI_API_KEY=...) and never printed; it is masked in any error text.
- Output: raw/<key>.wav (24 kHz mono). Style prompt: style_news_anchor.txt next to this script.
"""
import argparse, base64, json, os, re, sys, time, urllib.error, urllib.request, wave

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--keyfile", required=True)
ap.add_argument("--voice", default="Charon")
ap.add_argument("--model", default="gemini-3.1-flash-tts-preview")
ap.add_argument("--narration", default="narration.json")
ap.add_argument("--style", default=os.path.join(HERE, "style_news_anchor.txt"))
ap.add_argument("keys", nargs="*")
a = ap.parse_args()

m = re.search(r'GEMINI_API_KEY\s*=\s*["\']?([^\s"\']+)', open(a.keyfile).read())
if not m: sys.exit("GEMINI_API_KEY line not found in keyfile")
KEY = m.group(1)
STYLE = open(a.style).read()
LINES = json.load(open(a.narration))
os.makedirs("raw", exist_ok=True)

def mask(s): return s.replace(KEY, "<key>")

def synth(k, text):
    body = {"contents": [{"parts": [{"text": STYLE + text}]}],
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
            print(f"ok {k} {len(pcm) / 48000:.2f}s", flush=True); return
        except urllib.error.HTTPError as e:
            print(f"ERR {k} HTTP {e.code} {mask(e.read().decode()[:300])}", flush=True)
            if e.code in (429, 500, 503): time.sleep(8 * (attempt + 1)); continue
            sys.exit(1)
    sys.exit(f"ERR {k}: retries exhausted")

for k in (a.keys or list(LINES)): synth(k, LINES[k])
