#!/usr/bin/env python3
"""Turn the rendered TikTok slides into a narrated 9:16 video.

Usage:
    python3 tools/make_video.py posts/2026-11-07/slides.json [--voice ne-NP-SagarNeural]

Needs: tt-XX.jpg already rendered by tools/render.py, and a "say" field (Nepali
narration, 1-3 short sentences) on every slide in the "tt" list of slides.json.
Writes posts/<date>/tt-video.mp4 (1080x1920, H.264 + AAC).

Narration uses Microsoft's Nepali neural voices through the `edge-tts` package
(pip install edge-tts). The host speech.platform.bing.com must be reachable.
Exit codes: 0 ok, 3 text-to-speech unavailable (post the photo carousel instead),
1 other error.
"""
import argparse, asyncio, json, pathlib, subprocess, sys, tempfile

LEAD_IN = 0.3   # seconds of silence before the first line
GAP = 0.6       # seconds each slide stays on screen after its narration ends


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


async def synth(text, voice, rate, path):
    import os, ssl
    import edge_tts, edge_tts.communicate as comm
    # Inside a proxied sandbox: trust its CA bundle and route through the proxy.
    ca = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
    if ca and os.path.exists(ca):
        comm._SSL_CTX = ssl.create_default_context(cafile=ca)
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    await edge_tts.Communicate(text, voice, rate=rate, proxy=proxy).save(str(path))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--voice", default="ne-NP-SagarNeural", help="or ne-NP-HemkalaNeural")
    ap.add_argument("--rate", default="+0%")
    a = ap.parse_args()

    spec_path = pathlib.Path(a.spec).resolve()
    folder = spec_path.parent
    slides = json.loads(spec_path.read_text(encoding="utf-8")).get("tt") or []
    if not slides:
        print("no tt slides in spec"); return 1
    missing = [i for i, s in enumerate(slides, 1) if not (s.get("say") or "").strip()]
    if missing:
        print(f"slides without 'say' narration: {missing}"); return 1

    try:
        import edge_tts  # noqa: F401
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", "edge-tts"], check=False)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        parts = []
        for i, s in enumerate(slides, 1):
            img = folder / f"tt-{i:02d}.jpg"
            if not img.exists():
                print(f"missing {img.name}; run tools/render.py first"); return 1
            mp3 = tmp / f"n{i:02d}.mp3"
            try:
                asyncio.run(synth(s["say"], a.voice, a.rate, mp3))
                if mp3.stat().st_size == 0:
                    raise RuntimeError("empty audio")
            except Exception as e:
                print(f"TTS_UNAVAILABLE: {e}"); return 3
            lead = LEAD_IN if i == 1 else 0.0
            dur = lead + duration(mp3) + GAP
            seg = tmp / f"s{i:02d}.mp4"
            run(["ffmpeg", "-y", "-loop", "1", "-framerate", "30", "-i", str(img), "-i", str(mp3),
                 "-filter_complex", f"[1:a]adelay={int(lead*1000)}|{int(lead*1000)},apad[a]",
                 "-map", "0:v", "-map", "[a]", "-t", f"{dur:.2f}",
                 "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage", "-pix_fmt", "yuv420p",
                 "-vf", "scale=1080:1920", "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2", str(seg)])
            parts.append(seg)
        lst = tmp / "list.txt"
        lst.write_text("".join(f"file '{p}'\n" for p in parts))
        out = folder / "tt-video.mp4"
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", "-movflags", "+faststart", str(out)])
    print(f"video: {out} ({duration(out):.1f}s, {out.stat().st_size/1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
