"""Reusable flat-illustration icons for story videos (original drawings, PIL primitives only).
Import in a topic's illus.py:  from icons import *
Icons: person, laptop, globe, card, phone, bank, pill, arrow, xm (cross), tk (tick), cap (caption), tag; pop() fades a drawing in; A() = fade timing from a narration phrase.
Example scenes: examples/dollar-payments-2026-11/illus.py
"""
import math, sys
sys.path.insert(0, "/home/claude/ishaan-pranava-media/tools/mapvideo")
from PIL import ImageDraw
from engine import F, T, tw, layer, put, ease, eout, AMBER, COBALT, COBALT_L, WHITE, DARK, MUTED

RED = (235, 90, 80); GREEN = (80, 200, 140); GREY = (112, 118, 134); SKIN = (232, 190, 150)
INK = (30, 34, 44)

def pop(img, draw_fn, a, dy=16):
    """draw_fn(d) on a fresh layer, faded in with a"""
    if a <= 0: return
    lay = layer(); d = ImageDraw.Draw(lay); draw_fn(d); put(img, lay, a, dy=(1 - eout(a)) * dy)

def A(at, sc, t, phrase, dur=0.45, off=0.0):
    return ease((t - at(sc, phrase) - off) / dur) if phrase else ease((t - 0.3) / dur)

# ---------- icons ----------
def person(d, cx, cy, s, shirt=COBALT_L, hair=INK):
    d.pieslice((cx - .55 * s, cy - .05 * s, cx + .55 * s, cy + 1.0 * s), 180, 360, fill=shirt)
    d.rectangle((cx - .55 * s, cy + .45 * s, cx + .55 * s, cy + .55 * s), fill=shirt)
    d.ellipse((cx - .27 * s, cy - .62 * s, cx + .27 * s, cy - .08 * s), fill=SKIN)
    d.chord((cx - .29 * s, cy - .66 * s, cx + .29 * s, cy - .2 * s), 180, 360, fill=hair)

def laptop(d, cx, cy, s):
    w, h = 1.15 * s, .72 * s
    d.rounded_rectangle((cx - w / 2, cy - h, cx + w / 2, cy), 10, fill=(60, 66, 82), outline=MUTED, width=3)
    d.rounded_rectangle((cx - w / 2 + 12, cy - h + 12, cx + w / 2 - 12, cy - 12), 6, fill=(36, 48, 96))
    for i, c in enumerate([AMBER, COBALT_L, WHITE]):
        d.rounded_rectangle((cx - w / 2 + 30, cy - h + 30 + i * 22, cx - w / 2 + 30 + (w - 60) * (0.8 - i * .2), cy - h + 42 + i * 22), 5, fill=c)
    d.polygon([(cx - w / 2 - 26, cy + 22), (cx + w / 2 + 26, cy + 22), (cx + w / 2, cy), (cx - w / 2, cy)], fill=MUTED)

def globe(d, cx, cy, r):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=COBALT, outline=WHITE, width=4)
    d.ellipse((cx - r * .45, cy - r, cx + r * .45, cy + r), outline=(255, 255, 255, 150), width=3)
    d.line([(cx, cy - r), (cx, cy + r)], fill=(255, 255, 255, 150), width=3)
    for k in (-.5, 0, .5):
        hw = r * math.sqrt(1 - k * k); d.line([(cx - hw, cy + k * r), (cx + hw, cy + k * r)], fill=(255, 255, 255, 150), width=3)

def card(d, cx, cy, w, col=AMBER, text="$", tcol=DARK, size=None):
    h = w / 1.586
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), int(w * .07), fill=col)
    d.rectangle((cx - w / 2, cy - h / 2 + h * .18, cx + w / 2, cy - h / 2 + h * .32), fill=(0, 0, 0, 70))
    d.rounded_rectangle((cx - w / 2 + w * .09, cy - h * .02, cx - w / 2 + w * .26, cy + h * .2), 6, fill=(250, 220, 140))
    T(d, (cx + w / 2 - w * .08, cy + h / 2 - h * .1), text, F("ExtraBold", size or int(w * .2)), fill=tcol, anchor="rb")

def phone(d, cx, cy, h, lines=()):
    w = h * .52
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 26, fill=(50, 54, 66), outline=MUTED, width=3)
    d.rounded_rectangle((cx - w / 2 + 12, cy - h / 2 + 30, cx + w / 2 - 12, cy + h / 2 - 30), 12, fill=(90, 40, 140))
    y = cy - h / 2 + 60
    for txt, sz, c in lines:
        T(d, (cx, y), txt, F("ExtraBold", sz), fill=c, anchor="ma"); y += sz * 1.35

def bank(d, cx, cy, s, col=COBALT_L):
    d.polygon([(cx - .75 * s, cy - .45 * s), (cx + .75 * s, cy - .45 * s), (cx, cy - .95 * s)], fill=col)
    for i in range(4):
        x = cx - .55 * s + i * .366 * s
        d.rectangle((x - .08 * s, cy - .38 * s, x + .08 * s, cy + .3 * s), fill=WHITE)
    d.rectangle((cx - .8 * s, cy + .3 * s, cx + .8 * s, cy + .42 * s), fill=col)

def pill(d, cx, cy, text, col=WHITE, tcol=DARK, size=36):
    f = F("ExtraBold", size); w = tw(text, f) + 44
    d.rounded_rectangle((cx - w / 2, cy - size * .85, cx + w / 2, cy + size * .85), int(size * .85), fill=col)
    T(d, (cx, cy), text, f, fill=tcol, anchor="mm")
    return w

def arrow(d, p0, p1, col=AMBER, width=8, prog=1.0, dashed=False, head=True):
    x0, y0 = p0; x1, y1 = p1; x1 = x0 + (x1 - x0) * prog; y1 = y0 + (y1 - y0) * prog
    if dashed:
        n = int(math.hypot(x1 - x0, y1 - y0) / 22)
        for i in range(0, n, 2):
            a0, a1 = i / max(n, 1), min(1, (i + 1) / max(n, 1))
            d.line([(x0 + (x1 - x0) * a0, y0 + (y1 - y0) * a0), (x0 + (x1 - x0) * a1, y0 + (y1 - y0) * a1)], fill=col, width=width)
    else:
        d.line([(x0, y0), (x1, y1)], fill=col, width=width)
    if head and prog > 0.15:
        ang = math.atan2(y1 - y0, x1 - x0); s = width * 2.6
        d.polygon([(x1 + math.cos(ang) * s * .6, y1 + math.sin(ang) * s * .6),
                   (x1 + math.cos(ang + 2.5) * s, y1 + math.sin(ang + 2.5) * s),
                   (x1 + math.cos(ang - 2.5) * s, y1 + math.sin(ang - 2.5) * s)], fill=col)

def xm(d, x, y, s=30, col=RED, w=11):
    d.line([(x - s, y - s), (x + s, y + s)], fill=col, width=w); d.line([(x - s, y + s), (x + s, y - s)], fill=col, width=w)

def tk(d, x, y, s=30, col=GREEN, w=11):
    d.line([(x - s, y), (x - s * .3, y + s * .7), (x + s, y - s * .7)], fill=col, width=w, joint="curve")

def cap(d, x, y, s, size=30, col=MUTED, w="Bold"): T(d, (x, y), s, F(w, size), fill=col, anchor="ma")

def tag(d, box, s):
    x0, y0, x1, y1 = box; f = F("Bold", 24); w = tw(s, f) + 26
    d.rounded_rectangle((x0 + 18, y0 + 16, x0 + 18 + w, y0 + 52), 12, fill=(255, 255, 255, 30)); T(d, (x0 + 18 + w / 2, y0 + 34), s, f, fill=MUTED, anchor="mm")

