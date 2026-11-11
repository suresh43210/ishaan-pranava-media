import sys, os
sys.path.insert(0, "/home/claude/ishaan-pranava-media/tools/mapvideo")
"""Story: cyber fraud in Nepal — how money disappears and the 1247 centre (75-90s short, 2026-11-11).
Usage (work folder): python3 story.py <scene...> | --still <scene> <t> <out.png>
"""
import json, math, subprocess
import numpy as np
from PIL import Image, ImageDraw
import engine as R
from engine import (W, H, FPS, L, R as RX, F, T, tw, layer, put, panel, ease, eout, dev, Cam, camlerp,
                     draw_map, label, pin, arc, AMBER, COBALT, COBALT_L, WHITE, DARK, MUTED, FAINT, LOGO, fmt_np, background)

ROOT = os.getcwd()
AUD = json.load(open(f"{ROOT}/audio/durations.json"))
NARR = json.load(open(f"{ROOT}/narration.json"))
ORDER = list(AUD.keys())
SPEC = json.load(open(f"{ROOT}/spec.json"))
STARTS = {}; _t = 0
for s in ORDER: STARTS[s] = _t; _t += AUD[s]["scene"]
TOTAL = _t
DRAFT = False
GREY = (112, 118, 134)
KTM = (85.32, 27.71); DEL = (77.21, 28.61)
C4K = ["c04a", "c04b", "c04c", "c04d"]

_d = {}
def R_dur(k):
    if k not in _d:
        _d[k] = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{ROOT}/audio/{k}.wav"], capture_output=True, text=True).stdout)
    return _d[k]

def at(sc, phrase, key=None):
    k = key or sc; txt = NARR[k]; i = txt.find(phrase)
    if i < 0: raise KeyError(phrase)
    base = AUD[sc]["lead"] + (AUD[sc]["offsets"][C4K.index(k)] if k != sc else 0)
    dur = R_dur(k) if k != sc else AUD[sc]["audio"]
    return base + dur * i / len(txt)

# ---------------- provinces ----------------
PG = json.load(open("/home/claude/ishaan-pranava-media/tools/mapvideo/data/nepal_provinces_chuche.geojson"))
PROV = {}
for f in PG["features"]:
    g = f["geometry"]; ps = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    PROV[f["properties"]["id"]] = [np.array(p[0]) for p in ps]
PNAME = {"P1": "कोशी", "P2": "मधेश", "P3": "बागमती", "P4": "गण्डकी", "P5": "लुम्बिनी", "P6": "कर्णाली", "P7": "सुदूरपश्चिम"}
PLBL = {"P1": (87.3, 27.25), "P2": (85.9, 26.85), "P3": (85.45, 27.8), "P4": (84.0, 28.4), "P5": (82.9, 28.0), "P6": (82.65, 29.35), "P7": (80.85, 29.0)}
PVAL = {"P1": 16, "P2": 26, "P3": 152, "P4": 56, "P5": 24, "P6": 5, "P7": 42}
PSH = {"P1": "५.०%", "P2": "८.१%", "P3": "४७.४%", "P4": "१७.४%", "P5": "७.५%", "P6": "१.६%", "P7": "१३.१%"}

def draw_prov(img, cam, alphas):
    """alphas: {pid: (rgb, alpha)}; white province borders on top"""
    SS = 2
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for pid, rings in PROV.items():
        col, a = alphas.get(pid, (COBALT, 0.0))
        for r in rings:
            pts = tuple(map(tuple, cam.xy(r, SS)))
            if a > 0: d.polygon(pts, fill=col + (int(255 * a),))
    for pid, rings in PROV.items():
        for r in rings:
            pts = tuple(map(tuple, cam.xy(r, SS)))
            d.line(pts + (pts[0],), fill=(255, 255, 255, 170), width=2 * SS, joint="curve")
    img.alpha_composite(lay.resize((W, H), Image.LANCZOS))

def mix(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

# ---------------- shared chrome ----------------
def chrome(img, gt, chapter=None, headline=None, h_a=1.0, hl_col=WHITE):
    lay = layer(); d = ImageDraw.Draw(lay)
    sc = np.zeros((H, W, 4), np.uint8); g = np.clip(1 - np.arange(H) / 620, 0, 1) ** 1.4
    sc[..., 3] = (g * 200)[:, None]; sc[..., :3] = (10, 12, 17)
    img.alpha_composite(Image.fromarray(sc))
    d.rounded_rectangle((L, 200, RX, 206), 3, fill=(255, 255, 255, 40))
    d.rounded_rectangle((L, 200, L + (RX - L) * min(1, gt / TOTAL), 206), 3, fill=AMBER)
    lay.alpha_composite(R.LOGO64, (L, 226))
    T(d, (L + 80, 228), "Ishaan Pranava", F("Bold", 34))
    T(d, (L + 80, 266), SPEC.get("_tag", "बैंकिङ र फिनटेक नीति, प्रमाणसहित"), F("Regular", 26), fill=MUTED)
    if DRAFT:
        f = F("Bold", 24); w = tw("DRAFT", f)
        d.rounded_rectangle((RX - w - 28, 236, RX, 276), 10, fill=(150, 40, 40, 235)); T(d, (RX - 14, 256), "DRAFT", f, anchor="rm")
    img.alpha_composite(lay)
    if chapter or headline:
        lay = layer(); d = ImageDraw.Draw(lay)
        if chapter:
            f = F("Bold", 28); w = tw(chapter, f)
            d.rounded_rectangle((L, 320, L + w + 36, 364), 22, fill=AMBER + (255,)); T(d, (L + 18, 342), chapter, f, fill=DARK, anchor="lm")
        if headline:
            y = 382
            for i, ln in enumerate(headline.split("\n")):
                T(d, (L, y), ln, F("ExtraBold", 70), fill=hl_col if i else WHITE, stroke=4); y += 84
        put(img, lay, h_a, dy=(1 - eout(h_a)) * 24)

def factstrip(img, fact, src, a=1.0, y=1300, tag="तथ्य"):
    if a <= 0: return
    lay = layer(); d = ImageDraw.Draw(lay)
    ft = F("Bold", 34); fs = F("Regular", 28); tg = F("ExtraBold", 28)
    lines = fact.split("\n"); srcl = src.split("\n"); h = 44 * len(lines) + 38 * len(srcl) + 40
    d.rounded_rectangle((L, y, RX, y + h), 18, fill=(14, 16, 22, 236))
    d.rounded_rectangle((L, y, L + 10, y + h), 5, fill=AMBER + (255,))
    w = tw(tag, tg) + 28
    d.rounded_rectangle((L + 28, y - 20, L + 28 + w, y + 20), 12, fill=AMBER + (255,)); T(d, (L + 42, y), tag, tg, fill=DARK, anchor="lm")
    yy = y + 32
    for ln in lines: T(d, (L + 32, yy), ln, ft); yy += 44
    for i, ln in enumerate(srcl): T(d, (L + 32, yy + 4), ("स्रोत: " if i == 0 else "") + ln, fs, fill=MUTED); yy += 38
    put(img, lay, a, dy=(1 - eout(a)) * 20)

def bigstat(d, xy, s, size=96, col=AMBER, anchor="la"): T(d, xy, s, F("ExtraBold", size), fill=col, anchor=anchor, stroke=4)

def hbar(d, x, y, wmax, h, frac, col):
    d.rounded_rectangle((x, y, x + wmax, y + h), h // 2, fill=(255, 255, 255, 22))
    if frac > 0: d.rounded_rectangle((x, y, x + max(h, wmax * frac), y + h), h // 2, fill=col + (255,))

def xmark(d, x, y, s=26, col=(235, 90, 80)):
    d.line([(x - s, y - s), (x + s, y + s)], fill=col + (255,), width=9); d.line([(x - s, y + s), (x + s, y - s)], fill=col + (255,), width=9)
def tick(d, x, y, s=26, col=AMBER):
    d.line([(x - s, y), (x - s * 0.3, y + s * 0.7), (x + s, y - s * 0.7)], fill=col + (255,), width=9, joint="curve")

def dashed_arc(img, cam, a, b, prog, col=GREY, bend=0.25, width=5):
    if prog <= 0: return
    (x0, y0), (x1, y1) = cam.pt(*a), cam.pt(*b)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2; L_ = math.hypot(x1 - x0, y1 - y0); cx, cy = mx, my - L_ * bend
    ts = np.linspace(0, prog, 90)
    px = (1 - ts) ** 2 * x0 + 2 * (1 - ts) * ts * cx + ts ** 2 * x1; py = (1 - ts) ** 2 * y0 + 2 * (1 - ts) * ts * cy + ts ** 2 * y1
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(0, 89, 6): d.line([(px[i], py[i]), (px[min(i + 3, 89)], py[min(i + 3, 89)])], fill=col + (255,), width=width)
    return px, py

CAM_NEP = (84.3, 28.3, 10.8, 860)
CAM_IN = (80.5, 25.0, 30, 860)
CAM_US = (-97.0, 39.0, 64, 860)


def tile(d, box, big, small, col=AMBER, sub=None):
    panel(d, box, alpha=0.95)
    x0, y0, x1, y1 = box
    T(d, (x0 + 26, y0 + 18), big, F("ExtraBold", 54), fill=col)
    T(d, (x0 + 26, y0 + 92), small, F("Bold", 30))
    if sub: T(d, (x0 + 26, y0 + 134), sub, F("Regular", 28), fill=MUTED)

def srcline(img, lines, a, y=1470):
    lay = layer(); d = ImageDraw.Draw(lay)
    for i, ln in enumerate(lines): T(d, (L, y + 38 * i), ln, F("Regular", 28), fill=MUTED, stroke=3)
    put(img, lay, a)


RED = (235, 90, 80)


RED = (235, 90, 80)
COL = {"amber": AMBER, "red": RED, "blue": COBALT_L, "white": WHITE, "grey": GREY}

def bg(dim=0.75):
    return draw_map(Cam(*CAM_NEP), {"NPL": (COBALT, 0.92)}, dim=dim)

def wrapt(text, font, maxw):
    out, line = [], ""
    for w in text.split(" "):
        t2 = (line + " " + w).strip()
        if tw(t2, font) <= maxw: line = t2
        else: out.append(line); line = w
    out.append(line); return out

def frame(sc, t):
    A = AUD[sc]; gt = STARTS[sc] + t; s = SPEC[sc]; lang = SPEC.get("_lang", "ne")
    if s.get("type") == "disclaimer":
        img = Image.new("RGBA", (W, H), (12, 14, 19, 255)); d = ImageDraw.Draw(img)
        img.alpha_composite(LOGO.resize((120, 120)), (int(W / 2 - 60), 600))
        if lang == "ne":
            T(d, (W / 2, 800), "विचार व्यक्तिगत हुन्।", F("ExtraBold", 56), fill=AMBER, anchor="mm")
            T(d, (W / 2, 872), "सार्वजनिक जानकारीमा आधारित।", F("ExtraBold", 56), fill=AMBER, anchor="mm")
            T(d, (W / 2, 950), "लगानी सल्लाह होइन · आवाज: एआई", F("Regular", 30), fill=MUTED, anchor="mm")
        else:
            T(d, (W / 2, 800), "Views are personal.", F("ExtraBold", 56), fill=AMBER, anchor="mm")
            T(d, (W / 2, 872), "Based on public information.", F("ExtraBold", 56), fill=AMBER, anchor="mm")
            T(d, (W / 2, 950), "Not financial advice · AI voice", F("Regular", 30), fill=MUTED, anchor="mm")
        return img
    if s.get("type") == "cta":
        img = Image.new("RGBA", (W, H)); img.alpha_composite(background().convert("RGBA"))
        lay = layer(); d = ImageDraw.Draw(lay); y = 470
        for ln, c in s["lines"]:
            T(d, (W / 2, y), ln, F("ExtraBold", 60), fill=COL[c], anchor="mm"); y += 84
        put(img, lay, ease(t / 0.5))
        if s.get("box"):
            ts = at(sc, s["box_at"]); q = ease((t - ts) / 0.4)
            lay = layer(); d = ImageDraw.Draw(lay)
            d.rounded_rectangle((L, y + 20, RX, y + 190), 30, fill=AMBER + (255,))
            T(d, (W / 2, y + 105), s["box"], F("ExtraBold", 92 if len(s["box"]) < 8 else 58), fill=DARK, anchor="mm")
            put(img, lay, q, dy=(1 - eout(q)) * 24)
        f = ease((t - at(sc, s["follow_at"]) + 0.5) / 0.4)
        lay = layer(); d = ImageDraw.Draw(lay)
        lay.alpha_composite(LOGO.resize((150, 150)), (L, 1080))
        T(d, (L + 180, 1096), "Ishaan Pranava", F("ExtraBold", 54))
        T(d, (L + 180, 1166), s.get("follow_line", "तथ्यमा आधारित विश्लेषणका लागि फलो गर्नुहोस्"), F("Regular", 32), fill=MUTED)
        put(img, lay, f, dy=(1 - eout(f)) * 20)
        chrome(img, gt)
        return img
    img = bg(0.72); y = 640
    for it in s["items"]:
        ts = at(sc, it["at"]) if it.get("at") else 0.3
        a = ease((t - ts) / 0.45); k = it["k"]; col = COL[it.get("c", "amber")]
        lay = layer(); d = ImageDraw.Draw(lay)
        if k == "big":
            h = 250 if it.get("sub") else 190
            panel(d, (L, y, RX, y + h), alpha=0.95)
            if it.get("label"): T(d, (L + 30, y + 18), it["label"], F("Bold", 32), fill=MUTED)
            bigstat(d, (L + 30, y + (60 if it.get("label") else 30)), it["text"], size=104, col=col)
            if it.get("sub"): T(d, (L + 30, y + 196), it["sub"], F("Bold", 32), fill=WHITE)
        elif k == "row":
            h = 120; panel(d, (L, y, RX, y + h), alpha=0.95)
            T(d, (L + 30, y + 22), it["label"], F("Bold", 36))
            if it.get("sub"): T(d, (L + 30, y + 72), it["sub"], F("Regular", 28), fill=MUTED)
            T(d, (RX - 30, y + h / 2), it["text"], F("ExtraBold", 60), fill=col, anchor="rm")
        elif k == "bullet":
            f = F("Bold", 38); lines = wrapt(it["text"], f, RX - L - 160); h = 56 * len(lines) + 56
            panel(d, (L, y, RX, y + h), alpha=0.95)
            d.rounded_rectangle((L + 26, y + 26, L + 104, y + 104), 22, fill=col + (255,))
            T(d, (L + 65, y + 65), it.get("n", ""), F("ExtraBold", 48), fill=DARK, anchor="mm")
            for i, ln in enumerate(lines): T(d, (L + 130, y + 26 + 56 * i), ln, f)
            h = max(h, 130)
        elif k == "note":
            f = F("ExtraBold", 36); lines = wrapt(it["text"], f, RX - L - 60); h = 54 * len(lines) + 40
            d.rounded_rectangle((L, y, RX, y + h), 20, fill=col + (255,))
            for i, ln in enumerate(lines): T(d, (L + 30, y + 20 + 54 * i), ln, f, fill=DARK if it.get("c", "amber") in ("amber", "white") else WHITE)
        if a > 0: put(img, lay, a, dy=(1 - eout(a)) * 18)
        y += h + 22
    chrome(img, gt, s["chip"], s["head"], ease(t / 0.5), hl_col=AMBER)
    if s.get("src"):
        f = F("Regular", 28); lines = wrapt(("स्रोत: " if lang == "ne" else "Source: ") + s["src"], f, RX - L)
        srcline(img, lines, ease(t / 0.6), y=min(max(y + 6, 1300), 1560 - 38 * len(lines)))
    return img


def render_scene(sc):
    n = int(round(AUD[sc]["scene"] * FPS)); out = f"{ROOT}/scenes/{sc}.mp4"; tmp = out[:-4] + ".tmp.mp4"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
    for i in range(n): p.stdin.write(frame(sc, i / FPS).convert("RGB").tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, out)
    else: raise SystemExit("ffmpeg failed")

if __name__ == "__main__":
    if sys.argv[1] == "--still": frame(sys.argv[2], float(sys.argv[3])).convert("RGB").save(sys.argv[4])
    elif sys.argv[1] == "--sheet":
        os.makedirs("stills", exist_ok=True); ims = []
        for sc in ORDER:
            t = AUD[sc]["scene"] - 0.5 if sc != "c12" else 0.5
            im = frame(sc, t).convert("RGB"); dd = ImageDraw.Draw(im); dd.rectangle((L, 220, RX, 1560), outline=(255, 0, 0), width=3)
            T(dd, (20, 20), sc, F("Bold", 60), fill=(255, 0, 0)); im.save(f"stills/{sc}.png"); ims.append(im.resize((360, 640)))
        sh = Image.new("RGB", (360 * 4, 640 * 2))
        for i, im in enumerate(ims): sh.paste(im, ((i % 4) * 360, (i // 4) * 640))
        sh.save("stills/sheet.png")
    else:
        for s in sys.argv[1:]: render_scene(s)
