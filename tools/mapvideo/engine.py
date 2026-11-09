"""Ishaan Pranava map-video engine: map drawing, chrome, text helpers (original code for this project).
Imported by story scripts (see examples/). Run a story script, not this file.
Safe area for TikTok / YouTube Shorts / Facebook Reels: x 64-936, y 220-1560.
Usage: python3 render2.py <scene> | --still <scene> <t> <out.png>
"""
import json, math, subprocess, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SS = 1080, 1920, 30, 2
ROOT = os.path.dirname(os.path.abspath(__file__))
COBALT = (35, 64, 201); COBALT_L = (88, 116, 245); AMBER = (255, 181, 71); DARK = (22, 24, 29); WHITE = (255, 255, 255)
MUTED = (178, 186, 202); FAINT = (120, 128, 146)
OCEAN_T, OCEAN_B = (13, 16, 23), (19, 24, 34); LAND = (45, 50, 62)
L, R, TOP, BOT = 64, 936, 220, 1560
DRAFT = True

_fc = {}
def F(w, s):
    k = (w, s)
    if k not in _fc: _fc[k] = ImageFont.truetype(f"{ROOT}/fonts/Mukta-{w}.ttf", s, layout_engine=ImageFont.Layout.RAQM)
    return _fc[k]
_lp = f"{ROOT}/assets/logo.png"
if not os.path.exists(_lp):
    import cairosvg; cairosvg.svg2png(url=f"{ROOT}/assets/logo.svg", write_to=_lp, output_width=440)
LOGO = Image.open(_lp).convert("RGBA")
LOGO64 = LOGO.resize((64, 64), Image.LANCZOS)
DEV = str.maketrans("0123456789", "०१२३४५६७८९")
def dev(s): return str(s).translate(DEV)
def ease(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def eout(t): t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3

# ---------------- geography ----------------
REG = json.load(open(f"{ROOT}/data/region.json"))
def rings(g):
    polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    return [[np.array(r) for r in p] for p in polys]
SHAPES = {c["a3"]: rings(c["geom"]) for c in REG}
BBOX = {a: (lambda p: (p[:, 0].min(), p[:, 1].min(), p[:, 0].max(), p[:, 1].max()))(np.concatenate([r for pp in ps for r in pp])) for a, ps in SHAPES.items()}
COSF = math.cos(math.radians(22))

class Cam:
    def __init__(self, lon, lat, span, cy):
        self.lon, self.lat, self.span, self.cy = lon, lat, span, cy
        self.s = W / (span * COSF)
    def xy(self, p, ss=1):
        return np.stack([(W / 2 + (p[:, 0] - self.lon) * COSF * self.s) * ss, (self.cy - (p[:, 1] - self.lat) * self.s) * ss], 1)
    def pt(self, lon, lat):
        q = self.xy(np.array([[lon, lat]]))[0]; return float(q[0]), float(q[1])
    def vis(self, bb):
        x0, y0 = self.pt(bb[0], bb[3]); x1, y1 = self.pt(bb[2], bb[1])
        return not (x1 < -60 or x0 > W + 60 or y1 < -60 or y0 > H + 60)

def camlerp(a, b, t):
    t = ease(t)
    return Cam(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, math.exp(math.log(a[2]) + (math.log(b[2]) - math.log(a[2])) * t), a[3] + (b[3] - a[3]) * t)

_bg = None
def background():
    global _bg
    if _bg is None:
        y = np.linspace(0, 1, H)[:, None, None]
        g = (np.array(OCEAN_T) * (1 - y) + np.array(OCEAN_B) * y) * np.ones((1, W, 1))
        xx, yy = np.meshgrid(np.linspace(-1, 1, W), np.linspace(-1, 1, H))
        v = 1 - 0.35 * np.clip((xx ** 2 * 0.8 + (yy * 0.9) ** 2), 0, 1)
        _bg = Image.fromarray((g * v[..., None]).clip(0, 255).astype(np.uint8))
    return _bg

def draw_map(cam, fills, dim=0.0, glow=None):
    """fills: {a3: (rgb, alpha)}; glow: a3 of country to glow"""
    base = background().resize((W * SS, H * SS), Image.BILINEAR)
    d = ImageDraw.Draw(base, "RGBA")
    # graticule
    for lon in range(0, 181, 10):
        x = cam.pt(lon, 0)[0] * SS
        if -10 < x < W * SS + 10: d.line([(x, 0), (x, H * SS)], fill=(255, 255, 255, 10), width=SS)
    for lat in range(-40, 81, 10):
        y = cam.pt(0, lat)[1] * SS
        if -10 < y < H * SS + 10: d.line([(0, y), (W * SS, y)], fill=(255, 255, 255, 10), width=SS)
    vis = [a for a in SHAPES if cam.vis(BBOX[a])]
    for a in vis:
        for p in SHAPES[a]:
            d.polygon([tuple(map(tuple, cam.xy(r, SS))) for r in p][0], fill=LAND)
            for h in p[1:]: d.polygon(tuple(map(tuple, cam.xy(h, SS))), fill=OCEAN_B)
    img = base.resize((W, H), Image.LANCZOS).convert("RGBA")
    if glow and glow in SHAPES:
        m = Image.new("L", (W, H), 0); md = ImageDraw.Draw(m)
        for p in SHAPES[glow]: md.polygon(tuple(map(tuple, cam.xy(p[0]))), fill=255)
        gl = Image.new("RGBA", (W, H), COBALT_L + (0,)); gl.putalpha(m.filter(ImageFilter.GaussianBlur(26)).point(lambda v: int(v * 0.85)))
        img.alpha_composite(gl)
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for a, (col, al) in fills.items():
        if al <= 0 or a not in SHAPES: continue
        for p in SHAPES[a]:
            d.polygon(tuple(map(tuple, cam.xy(p[0], SS))), fill=col + (int(255 * al),))
    for a in vis:
        hl = a in fills and fills[a][1] > 0.05
        for p in SHAPES[a]:
            pts = tuple(map(tuple, cam.xy(p[0], SS)))
            d.line(pts + (pts[0],), fill=(255, 255, 255, 240 if hl else 46), width=(3 * SS if hl else SS), joint="curve")
    img.alpha_composite(lay.resize((W, H), Image.LANCZOS))
    if dim > 0:
        img = Image.blend(img, Image.new("RGBA", (W, H), OCEAN_T + (255,)), dim)
    return img

# ---------------- drawing helpers ----------------
def T(d, xy, s, f, fill=WHITE, anchor="la", stroke=0):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(10, 12, 16))
def tw(s, f): b = f.getbbox(s); return b[2] - b[0]

def layer(): return Image.new("RGBA", (W, H), (0, 0, 0, 0))
def put(img, lay, a=1.0, dy=0):
    if a <= 0: return
    if dy: l2 = layer(); l2.paste(lay, (0, int(dy))); lay = l2
    if a < 1:
        arr = np.array(lay); arr[..., 3] = (arr[..., 3].astype(np.float32) * a).astype(np.uint8); lay = Image.fromarray(arr)
    img.alpha_composite(lay)

def panel(d, box, r=30, alpha=0.9, outline=None):
    d.rounded_rectangle(box, r, fill=(18, 20, 26, int(255 * alpha)), outline=outline, width=3 if outline else 0)

def chrome(img, scene_t, total_t, chapter=None):
    lay = layer(); d = ImageDraw.Draw(lay)
    # progress
    d.rounded_rectangle((L, 200, R, 206), 3, fill=(255, 255, 255, 40))
    d.rounded_rectangle((L, 200, L + (R - L) * min(1, scene_t / total_t), 206), 3, fill=AMBER)
    lay.alpha_composite(LOGO64, (L, 226))
    T(d, (L + 80, 228), "Ishaan Pranava", F("Bold", 34))
    T(d, (L + 80, 266), "बैंकिङ र फिनटेक नीति, प्रमाणसहित", F("Regular", 26), fill=MUTED)
    if DRAFT:
        f = F("Bold", 24); s = "DRAFT"; w = tw(s, f)
        d.rounded_rectangle((R - w - 28, 236, R, 276), 10, fill=(150, 40, 40, 235))
        T(d, (R - 14, 256), s, f, anchor="rm")
    if chapter:
        f = F("Bold", 30); w = tw(chapter, f)
        d.rounded_rectangle((L, 322, L + w + 40, 370), 24, fill=AMBER + (255,))
        T(d, (L + 20, 345), chapter, f, fill=DARK, anchor="lm")
    img.alpha_composite(lay)

def source(img, s, a=1.0):
    lay = layer(); d = ImageDraw.Draw(lay)
    T(d, (L, 1478), "स्रोत: " + s, F("Regular", 28), fill=MUTED, stroke=3)
    put(img, lay, a)

def label(img, cam, lon, lat, s, a=1.0, size=40, dx=0, dy=0, col=WHITE, w="Bold"):
    if a <= 0: return
    lay = layer(); d = ImageDraw.Draw(lay); x, y = cam.pt(lon, lat)
    T(d, (x + dx, y + dy), s, F(w, size), fill=col, anchor="mm", stroke=6)
    put(img, lay, a)

def pin(img, cam, lon, lat, col=AMBER, r=11, pulse=None):
    d = ImageDraw.Draw(img, "RGBA"); x, y = cam.pt(lon, lat)
    if pulse is not None:
        R_ = r + 34 * pulse; d.ellipse((x - R_, y - R_, x + R_, y + R_), outline=col + (int(220 * (1 - pulse)),), width=4)
    d.ellipse((x - r, y - r, x + r, y + r), fill=col, outline=WHITE, width=3)

def arc(img, cam, a, b, prog, col=AMBER, width=5, bend=0.25):
    if prog <= 0: return
    (x0, y0), (x1, y1) = cam.pt(*a), cam.pt(*b)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2; L_ = math.hypot(x1 - x0, y1 - y0)
    cx, cy = mx, my - L_ * bend
    n = 90; ts = np.linspace(0, prog, n)
    px = (1 - ts) ** 2 * x0 + 2 * (1 - ts) * ts * cx + ts ** 2 * x1
    py = (1 - ts) ** 2 * y0 + 2 * (1 - ts) * ts * cy + ts ** 2 * y1
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    pts = list(zip(px * SS, py * SS))
    d.line(pts, fill=col + (70,), width=width * SS * 3, joint="curve")
    d.line(pts, fill=col + (255,), width=width * SS, joint="curve")
    x, y = pts[-1]; r = 9 * SS
    d.ellipse((x - r, y - r, x + r, y + r), fill=WHITE + (255,))
    img.alpha_composite(lay.resize((W, H), Image.LANCZOS))

def fmt_np(n):  # Indian grouping, Devanagari
    s = str(n); head, tail = s[:-3], s[-3:]
    parts = []
    while len(head) > 2: parts.insert(0, head[-2:]); head = head[:-2]
    if head: parts.insert(0, head)
    return dev(",".join(parts + [tail]))

def stat_card(img, y, big, line1, line2, a, big_col=AMBER, delta=None, delta_up=True):
    if a <= 0: return
    lay = layer(); d = ImageDraw.Draw(lay)
    panel(d, (L, y, R, y + 250))
    T(d, (L + 40, y + 28), big, F("ExtraBold", 80), fill=big_col)
    if delta:
        f = F("ExtraBold", 40); w = tw(delta, f) + 36
        x = L + 40 + tw(big, F("ExtraBold", 80)) + 22
        if x + w > R - 30: x = R - 30 - w
        d.rounded_rectangle((x, y + 52, x + w, y + 106), 27, fill=(AMBER if delta_up else (70, 76, 92)) + (255,))
        T(d, (x + w / 2, y + 79), delta, f, fill=DARK if delta_up else WHITE, anchor="mm")
    T(d, (L + 40, y + 142), line1, F("Bold", 38))
    T(d, (L + 40, y + 192), line2, F("Regular", 32), fill=MUTED)
    put(img, lay, ease(a), dy=(1 - eout(a)) * 36)
