"""4:5 (1080x1350) branded cards. Usage: from cards import card; card(name, chip, title, body=, rows=[(label,sub,value,colour)], bars=[(label,value,shown)], big=, footer=, src=, page=, nep=True). Writes $CARDS_OUT/<name>.png (convert to JPG for TikTok)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "mapvideo"))
from PIL import Image, ImageDraw
from engine import F, COBALT, COBALT_L, AMBER, WHITE, MUTED, FAINT, OCEAN_T, OCEAN_B, LOGO, dev
import numpy as np
W, H = 1080, 1350
RED = (235, 90, 80); GREY = (112, 118, 134); DARK = (22, 24, 29)
OUT = os.environ.get("CARDS_OUT", "img"); os.makedirs(OUT, exist_ok=True)

def bg():
    y = np.linspace(0, 1, H)[:, None, None]
    g = (np.array(OCEAN_T) * (1 - y) + np.array(OCEAN_B) * y) * np.ones((1, W, 1))
    im = Image.fromarray(g.clip(0, 255).astype(np.uint8)).convert("RGB")
    d = ImageDraw.Draw(im, "RGBA")
    for x in range(0, W, 90): d.line([(x, 0), (x, H)], fill=(255, 255, 255, 8))
    for yy in range(0, H, 90): d.line([(0, yy), (W, yy)], fill=(255, 255, 255, 8))
    return im

def wrap(d, text, font, maxw):
    out = []
    for para in text.split("\n"):
        words, line = para.split(" "), ""
        for w in words:
            t = (line + " " + w).strip()
            if d.textlength(t, font=font) <= maxw: line = t
            else: out.append(line); line = w
        out.append(line)
    return out

def card(name, chip, title, body=None, big=None, bigcol=AMBER, src=None, page=None, footer=None, rows=None, bars=None, nep=False):
    im = bg(); d = ImageDraw.Draw(im, "RGBA"); L, R = 72, W - 72
    lg = LOGO.resize((60, 60)); im.paste(lg, (L, 64), lg)
    d.text((L + 76, 66), "Ishaan Pranava", font=F("Bold", 32), fill=WHITE)
    d.text((L + 76, 102), "बैंकिङ र फिनटेक नीति, प्रमाणसहित" if nep else "Banking & fintech policy, with evidence", font=F("Regular", 24), fill=MUTED)
    if page: d.text((R, 84), page, font=F("Bold", 26), fill=MUTED, anchor="ra")
    y = 190
    if chip:
        f = F("Bold", 28); w = d.textlength(chip, font=f) + 40
        d.rounded_rectangle((L, y, L + w, y + 48), 24, fill=AMBER); d.text((L + 20, y + 24), chip, font=f, fill=DARK, anchor="lm"); y += 76
    ft = F("ExtraBold", 64 if len(title) < 60 else 54)
    for ln in wrap(d, title, ft, R - L):
        d.text((L, y), ln, font=ft, fill=WHITE); y += int(ft.size * 1.28)
    y += 20
    if big:
        fb = F("ExtraBold", 132)
        d.text((L, y), big, font=fb, fill=bigcol); y += 175
    if rows:
        for lab, a, b, col in rows:
            d.rounded_rectangle((L, y, R, y + 118), 22, fill=(255, 255, 255, 14))
            d.text((L + 28, y + 18), lab, font=F("Bold", 34), fill=WHITE)
            d.text((L + 28, y + 66), a, font=F("Regular", 28), fill=MUTED)
            d.text((R - 28, y + 59), b, font=F("ExtraBold", 58), fill=col, anchor="rm")
            y += 136
    if bars:
        mx = max(v for _, v, _ in bars); fl = F("Bold", 26)
        for lab, v, lbl in bars:
            d.text((L, y + 6), lab, font=fl, fill=MUTED)
            x0 = L + 190; wmax = R - x0 - 150
            d.rounded_rectangle((x0, y + 8, x0 + max(18, wmax * v / mx), y + 40), 16, fill=AMBER if v == mx else COBALT_L)
            d.text((R, y + 24), lbl, font=F("ExtraBold", 30), fill=WHITE, anchor="rm"); y += 62
        y += 10
    if body:
        fbd = F("Regular", 44)
        for para in body.split("\n\n"):
            for ln in wrap(d, para, fbd, R - L):
                d.text((L, y), ln, font=fbd, fill=WHITE); y += 62
            y += 22
    if footer:
        d.rounded_rectangle((L, H - 300, R, H - 190), 22, fill=AMBER)
        d.text((W / 2, H - 245), footer, font=F("ExtraBold", 40), fill=DARK, anchor="mm")
    if src:
        fs = F("Regular", 24); yy = H - 150
        for ln in wrap(d, ("स्रोत: " if nep else "Source: ") + src, fs, R - L)[:3]:
            d.text((L, yy), ln, font=fs, fill=FAINT); yy += 32
    im.convert("RGB").save(f"{OUT}/{name}.png")

