"""Scene illustrations for the dollar-payments story (2026-11-17). Copy and rewrite the ill_cNN functions for a new topic."""
import math, sys
sys.path.insert(0, "/home/claude/ishaan-pranava-media/tools/mapvideo")
from icons import *
from engine import F, T, AMBER, COBALT, COBALT_L, WHITE, DARK, MUTED

# ---------- scenes ----------
def ill_c01(img, sc, t, box, at):
    x0, y0, x1, y1 = box; cy = y0 + 250
    pop(img, lambda d: tag(d, box, "उदाहरण पात्र"), A(at, sc, t, None))
    def p1(d):
        person(d, 220, cy - 20, 120, shirt=(230, 120, 160)); laptop(d, 220, cy + 120, 120)
        cap(d, 220, cy + 160, "डिजाइनर, पोखरा", 30, WHITE)
    pop(img, p1, A(at, sc, t, None))
    def p2(d):
        globe(d, 780, cy - 10, 90); person(d, 780, cy - 175, 70, shirt=AMBER)
        cap(d, 780, cy + 100, "अमेरिकी ग्राहक", 30, WHITE)
    pop(img, p2, A(at, sc, t, "अमेरिकी ग्राहक"))
    q = ease((t - at(sc, "पेपलबाट पैसा पठाइदिन्छु")) / 0.8)
    if q > 0:
        pop(img, lambda d: (arrow(d, (680, cy - 10), (330, cy - 10), AMBER, 8, prog=q, dashed=True), pill(d, 505, cy - 70, "पेपल", WHITE, DARK, 34)), 1.0, 0)
    pop(img, lambda d: xm(d, 505, cy - 10, 34), A(at, sc, t, "मिल्दैन"))
    def p4(d):
        card(d, 505, cy + 110, 150, AMBER, "$", size=40); cap(d, 505, cy + 170, "सफ्टवेयर शुल्क", 28, AMBER)
    pop(img, p4, A(at, sc, t, "सफ्टवेयरको"))

def ill_c02(img, sc, t, box, at):
    x0, y0, x1, y1 = box; cy = y0 + 200
    pop(img, lambda d: (bank(d, 500, cy + 40, 120), cap(d, 500, cy + 110, "नेपाल", 32, WHITE)), A(at, sc, t, None))
    q = ease((t - at(sc, "डलरमा कमाउने")) / 0.7)
    if q > 0: pop(img, lambda d: (arrow(d, (110, cy - 10), (380, cy - 10), GREEN, 10, prog=q), cap(d, 230, cy + 40, "कमाइ भित्र्याउने", 30, GREEN)), 1.0, 0)
    q = ease((t - at(sc, "डलरमा तिर्ने")) / 0.7)
    if q > 0: pop(img, lambda d: (arrow(d, (620, cy - 10), (890, cy - 10), AMBER, 10, prog=q), cap(d, 770, cy + 40, "डलर तिर्ने", 30, AMBER)), 1.0, 0)
    pop(img, lambda d: T(d, (500, cy - 150), "?", F("ExtraBold", 90), fill=WHITE, anchor="mm"), A(at, sc, t, "कति खुला"))

def ill_c03(img, sc, t, box, at):
    x0, y0, x1, y1 = box; cy = y0 + 200
    pop(img, lambda d: (card(d, 270, cy, 300, AMBER, "$५००", size=58), cap(d, 270, cy + 115, "प्रतिव्यक्ति, प्रतिवर्ष", 30, WHITE)), A(at, sc, t, "पाँच सय डलरसम्म"))
    def p2(d):
        for i in range(12):
            x = 590 + (i % 4) * 70; y = cy - 110 + (i // 4) * 62
            d.rounded_rectangle((x, y, x + 56, y + 48), 8, fill=(255, 255, 255, 34))
        T(d, (730, cy + 95), "≈ $४२ / महिना", F("ExtraBold", 50), fill=AMBER, anchor="mm")
    pop(img, p2, A(at, sc, t, "बयालीस डलर"))

def ill_c05(img, sc, t, box, at):
    x0, y0, x1, y1 = box; cy = y0 + 230
    pop(img, lambda d: (pill(d, 230, y0 + 70, "पेपल", WHITE, DARK, 30), xm(d, 320, y0 + 70, 24)), A(at, sc, t, "पेपल अझै"))
    def p1(d):
        globe(d, 170, cy + 20, 70); card(d, 170, cy + 125, 120, COBALT_L, "$", WHITE, 30); cap(d, 170, cy + 175, "विदेशी ग्राहक", 28, WHITE)
    pop(img, p1, A(at, sc, t, "विदेशी ग्राहकले"))
    def p2(d):
        pill(d, 480, cy + 20, "भुक्तानी लिंक", AMBER, DARK, 32); cap(d, 480, cy + 70, "स्ट्राइप", 28, MUTED)
    pop(img, p2, A(at, sc, t, "भुक्तानी लिंक"))
    q = ease((t - at(sc, "कार्डबाट तिर्छन्")) / 0.8)
    if q > 0: pop(img, lambda d: (arrow(d, (250, cy + 20), (365, cy + 20), AMBER, 7, prog=min(1, q * 2)), arrow(d, (600, cy + 20), (700, cy + 20), AMBER, 7, prog=max(0, q * 2 - 1))), 1.0, 0)
    pop(img, lambda d: (phone(d, 800, cy + 40, 260, [("खल्ती", 30, WHITE), ("रु", 64, AMBER)]), cap(d, 800, cy + 180, "नेपाली रुपैयाँमा", 28, WHITE)), A(at, sc, t, "नेपाली रुपैयाँमा"))

def ill_c07(img, sc, t, box, at):
    x0, y0, x1, y1 = box; cy = y0 + 210
    names = ["डीआर कंगो", "मोनाको", "बुल्गेरिया", "आइभरी कोस्ट"]
    pop(img, lambda d: (d.rounded_rectangle((100, cy - 130, 900, cy + 130), 26, outline=GREY, width=4), cap(d, 500, cy - 180, "ग्रे लिस्ट (बढी निगरानी)", 32, MUTED)), A(at, sc, t, "ग्रे लिस्टमा"))
    q = ease((t - at(sc, "चार देशलाई")) / 1.0)
    def p(d):
        for i, n in enumerate(names):
            x = 180 + i * 150 + q * 0; y = cy - 40 - q * 0
            col = GREEN if q > 0.5 else GREY
            d.ellipse((x - 42, y - 42, x + 42, y + 42), fill=col)
            if q > 0.5: tk(d, x, y, 20, WHITE, 8)
            cap(d, x, y + 56, n, 24, WHITE)
        cap(d, 405, cy + 78, "सूचीबाट हटे", 28, GREEN)
    pop(img, p, ease((t - at(sc, "चार देशलाई")) / 0.4))
    def p2(d):
        d.ellipse((800 - 52, cy - 92, 800 + 52, cy + 12), fill=RED); T(d, (800, cy - 40), "नेपाल", F("ExtraBold", 26), fill=WHITE, anchor="mm")
        cap(d, 800, cy + 30, "अझै सूचीमा", 28, RED)
    pop(img, p2, A(at, sc, t, "नेपाल त्यसमा"))

def ill_c09(img, sc, t, box, at):
    x0, y0, x1, y1 = box; cy = y0 + 190
    pop(img, lambda d: (d.rounded_rectangle((110, cy - 110, 420, cy + 110), 26, fill=(80, 200, 140, 60)), tk(d, 265, cy - 30, 40), cap(d, 265, cy + 40, "घोषणा", 40, WHITE, "ExtraBold")), A(at, sc, t, None))
    q = ease((t - at(sc, "दूरी छ")) / 0.8)
    if q > 0: pop(img, lambda d: arrow(d, (440, cy), (440 + 120 * q, cy), GREY, 8, prog=1, dashed=True, head=False), 1.0, 0)
    pop(img, lambda d: (d.rounded_rectangle((580, cy - 110, 890, cy + 110), 26, fill=(255, 181, 71, 50)), T(d, (735, cy - 30), "?", F("ExtraBold", 96), fill=AMBER, anchor="mm"), cap(d, 735, cy + 40, "कार्यान्वयन", 40, WHITE, "ExtraBold")), A(at, sc, t, "दूरी छ", off=0.5))

def ill_c10(img, sc, t, box, at):
    x0, y0, x1, y1 = box; cy = y0 + 230
    pop(img, lambda d: (bank(d, 250, cy + 20, 150), cap(d, 250, cy + 100, "बैंक", 32, WHITE)), A(at, sc, t, None))
    def p(d):
        for i, (c, lbl) in enumerate([((230, 120, 160), "फ्रिल्यान्सर"), (AMBER, "आइटी निर्यातकर्ता")]):
            x = 600 + i * 210; person(d, x, cy - 20, 95, shirt=c); laptop(d, x, cy + 100, 70); cap(d, x, cy + 140, lbl, 26, WHITE)
    pop(img, p, A(at, sc, t, "फ्रिल्यान्सर"))
    q = ease((t - at(sc, "बजार पाउँछ")) / 0.7)
    if q > 0: pop(img, lambda d: arrow(d, (370, cy - 40), (500, cy - 40), GREEN, 9, prog=q), 1.0, 0)

ILL = {"c01": ill_c01, "c02": ill_c02, "c03": ill_c03, "c05": ill_c05, "c07": ill_c07, "c09": ill_c09, "c10": ill_c10}
