#!/usr/bin/env python3
"""Turn the rendered TikTok slides into a narrated 9:16 video.

Usage:
    python3 tools/make_video.py posts/2026-11-07/slides.json [--engine gemini|edge] [--voice NAME]

Needs: tt-XX.jpg already rendered by tools/render.py, and a "say" field (Nepali
narration, 1-3 short sentences) on every slide in the "tt" list of slides.json.
Writes posts/<date>/tt-video.mp4 (1080x1920, H.264 + AAC).

Engines:
  gemini (default) - Google Gemini TTS, Nepali newsreader style. Needs env GEMINI_API_KEY
                     and network access to generativelanguage.googleapis.com.
                     Default voice "Charon" (male), model gemini-3.8-flash-tts.
  edge             - Microsoft neural voice via edge-tts (ne-NP-SagarNeural). Fallback.
If the gemini engine fails, the script falls back to edge automatically.

Exit codes: 0 ok, 3 no voice service reachable (post the photo carousel instead), 1 other error.
"""
import argparse, asyncio, base64, difflib, json, os, pathlib, ssl, subprocess, sys, tempfile, time, urllib.request, urllib.error

LEAD_IN = 0.3   # seconds of silence before the first line
GAP = 0.6       # seconds each slide stays on screen after its narration ends

GEMINI_MODEL = "gemini-3.8-flash-tts"
GEMINI_STYLE = ("# AUDIO PROFILE: Senior Nepali TV news anchor\n"
                "## THE SCENE: A Kathmandu television studio, evening news bulletin.\n"
                "### DIRECTOR'S NOTES\nStyle: calm, formal, authoritative. Native Nepali (Kathmandu) pronunciation. "
                "Natural pauses at commas. Steady pace.\n"
                "#### TRANSCRIPT\n")


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def _ssl_ctx():
    ca = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
    return ssl.create_default_context(cafile=ca) if ca and os.path.exists(ca) else ssl.create_default_context()


def _opener():
    handlers = [urllib.request.HTTPSHandler(context=_ssl_ctx())]
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if proxy:
        handlers.append(urllib.request.ProxyHandler({"https": proxy}))
    return urllib.request.build_opener(*handlers)


def _letters(s):
    """Devanagari/Latin letters only, for comparing spoken vs written text."""
    return "".join(ch for ch in s
                   if (ch.isalpha() or "ऀ" <= ch <= "ॿ") and not ch.isdigit() and ch not in "।॥")


def transcribe(wav):
    """Transcribe a narration clip with Gemini so we can catch repeated or skipped lines."""
    key = os.environ["GEMINI_API_KEY"]
    mp3 = pathlib.Path(str(wav) + ".check.mp3")
    run(["ffmpeg", "-y", "-i", str(wav), "-ac", "1", "-ar", "16000", "-b:a", "48k", str(mp3)])
    body = {"contents": [{"parts": [
        {"text": "Transcribe this audio exactly as spoken. Write Nepali in Devanagari and any English words in Latin script. Write numbers as spoken words. Output only the transcript."},
        {"inlineData": {"mimeType": "audio/mp3", "data": base64.b64encode(mp3.read_bytes()).decode()}}]}]}
    req = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
                                 data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "x-goog-api-key": key})
    d = json.load(_opener().open(req, timeout=120))
    mp3.unlink()
    return d["candidates"][0]["content"]["parts"][0]["text"]


def narration_ok(wav, text):
    """True if the spoken audio matches the script closely (no repeats, nothing skipped)."""
    try:
        heard = transcribe(wav)
    except Exception as e:
        print(f"  (could not verify narration: {e!r:.120})")
        return True
    want, got = _letters(text), _letters(heard)
    ratio = len(got) / max(len(want), 1)
    sim = difflib.SequenceMatcher(None, want, got).ratio()
    latin_extra = sum(c.isascii() and c.isalpha() for c in heard) - sum(c.isascii() and c.isalpha() for c in text)
    leaked = latin_extra > 8 or any(w in heard.lower() for w in ("anchor", "pronunciation", "authoritative", "news-anchor", "voice with"))
    leaked = leaked or any(w in heard.lower() for w in ("profile", "scene", "director", "transcript", "style"))
    leaked = leaked or any(w in heard for w in ("एन्कर", "प्रोफाइल", "डाइरेक्टर", "ट्रान्सक्रिप्ट", "प्रोनन्सिएसन", "अथोरिटेटिभ", "रीड द"))
    ok = 0.8 <= ratio <= 1.2 and sim >= 0.7 and not leaked
    if not ok:
        why = "instructions read aloud" if leaked else f"length x{ratio:.2f}, similarity {sim:.2f}"
        print(f"  narration mismatch ({why}); regenerating")
    return ok


def synth_gemini(text, voice, out_path, model=GEMINI_MODEL, verify=True):
    for attempt in range(3):
        _synth_gemini_once(text, voice, out_path, model)
        if not verify or narration_ok(out_path, text):
            return
    print("  narration still differs after 3 tries; keeping the last take — listen before publishing")


def _synth_gemini_once(text, voice, out_path, model=GEMINI_MODEL):
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY not set")
    opener = _opener()
    body = {"contents": [{"parts": [{"text": GEMINI_STYLE + text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                                 data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "x-goog-api-key": key})
    last = None
    for attempt in range(3):
        try:
            d = json.load(opener.open(req, timeout=180))
            part = d["candidates"][0]["content"]["parts"][0]["inlineData"]
            raw = base64.b64decode(part["data"])
            mt = part.get("mimeType", "")
            tmp = pathlib.Path(str(out_path) + ".src")
            tmp.write_bytes(raw)
            if raw[:4] == b"RIFF":
                run(["ffmpeg", "-y", "-i", str(tmp), "-ar", "44100", "-ac", "1", str(out_path)])
            else:
                rate = int(mt.split("rate=")[1].split(";")[0]) if "rate=" in mt else 24000
                run(["ffmpeg", "-y", "-f", "s16le", "-ar", str(rate), "-ac", "1", "-i", str(tmp), "-ar", "44100", str(out_path)])
            tmp.unlink()
            return
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read()[:200]!r}"
            if e.code in (400, 401, 402, 403, 404):
                break
        except Exception as e:  # network hiccup or odd response
            last = repr(e)[:200]
        time.sleep(4 * (attempt + 1))
    raise RuntimeError(f"gemini TTS failed: {last}")


async def _edge(text, voice, rate, pitch, path):
    import edge_tts, edge_tts.communicate as comm
    comm._SSL_CTX = _ssl_ctx()
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, proxy=proxy).save(str(path))


def synth_edge(text, voice, out_path, rate="-8%", pitch="-4Hz"):
    try:
        import edge_tts  # noqa: F401
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", "edge-tts"], check=False)
    asyncio.run(_edge(text, voice, rate, pitch, out_path))
    if not pathlib.Path(out_path).exists() or pathlib.Path(out_path).stat().st_size == 0:
        raise RuntimeError("edge TTS produced empty audio")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--engine", default="gemini", choices=["gemini", "edge"])
    ap.add_argument("--voice", default=None, help="gemini: Charon (default), Kore, Orus ... / edge: ne-NP-SagarNeural, ne-NP-HemkalaNeural")
    a = ap.parse_args()

    spec_path = pathlib.Path(a.spec).resolve()
    folder = spec_path.parent
    slides = json.loads(spec_path.read_text(encoding="utf-8")).get("tt") or []
    if not slides:
        print("no tt slides in spec"); return 1
    missing = [i for i, s in enumerate(slides, 1) if not (s.get("say") or "").strip()]
    if missing:
        print(f"slides without 'say' narration: {missing}"); return 1

    def synth_all(engine, tmp):
        wavs = []
        for i, s in enumerate(slides, 1):
            wav = tmp / f"{engine}-{i:02d}.wav"
            if engine == "gemini":
                synth_gemini(s["say"], a.voice or "Charon", wav)
            else:
                mp3 = tmp / f"{engine}-{i:02d}.mp3"
                synth_edge(s["say"], a.voice if (a.engine == "edge" and a.voice) else "ne-NP-SagarNeural", mp3)
                run(["ffmpeg", "-y", "-i", str(mp3), "-ar", "44100", "-ac", "1", str(wav)])
            wavs.append(wav)
        return wavs

    for i in range(1, len(slides) + 1):
        if not (folder / f"tt-{i:02d}.jpg").exists():
            print(f"missing tt-{i:02d}.jpg; run tools/render.py first"); return 1

    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        engine = a.engine
        try:
            wavs = synth_all(engine, tmp)
        except Exception as e:
            if engine != "gemini":
                print(f"TTS_UNAVAILABLE: {e}"); return 3
            print(f"GEMINI_FAILED ({e}); falling back to the Microsoft voice")
            engine = "edge"
            try:
                wavs = synth_all(engine, tmp)
            except Exception as e2:
                print(f"TTS_UNAVAILABLE: {e2}"); return 3
        parts = [segment(tmp, folder, i, w) for i, w in enumerate(wavs, 1)]
        lst = tmp / "list.txt"
        lst.write_text("".join(f"file '{p}'\n" for p in parts))
        out = folder / "tt-video.mp4"
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", "-movflags", "+faststart", str(out)])
    print(f"video: {out} ({duration(out):.1f}s, {out.stat().st_size/1e6:.1f} MB, voice engine: {engine})")
    return 0


def segment(tmp, folder, i, wav):
    img = folder / f"tt-{i:02d}.jpg"
    lead = LEAD_IN if i == 1 else 0.0
    dur = lead + duration(wav) + GAP
    seg = tmp / f"s{i:02d}.mp4"
    run(["ffmpeg", "-y", "-loop", "1", "-framerate", "30", "-i", str(img), "-i", str(wav),
         "-filter_complex", f"[1:a]loudnorm=I=-16:TP=-1.5,adelay={int(lead*1000)}|{int(lead*1000)},apad[a]",
         "-map", "0:v", "-map", "[a]", "-t", f"{dur:.2f}",
         "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage", "-pix_fmt", "yuv420p",
         "-vf", "scale=1080:1920", "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2", str(seg)])
    return seg


if __name__ == "__main__":
    sys.exit(main())
