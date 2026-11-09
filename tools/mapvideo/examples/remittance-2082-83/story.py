import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
"""Example story: remittance FY 2082/83 (3-min map short, posted 2026-11-10). Copy this file for a new topic.
Run from a work folder containing narration.json and audio/ (made by tts_gemini.py + mix_audio.py).
Usage: python3 render3.py <scene> | --still <scene> <t> <out.png>
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw
import engine as R
from engine import (W, H, FPS, L, R as RX, F, T, tw, layer, put, panel, ease, eout, dev, Cam, camlerp,
                     draw_map, label, pin, arc, AMBER, COBALT, COBALT_L, WHITE, DARK, MUTED, FAINT, LOGO, fmt_np, background)

ROOT = os.getcwd()  # work folder: narration.json, audio/ (from mix_audio.py); scenes/ is written here
AUD = json.load(open(f"{ROOT}/audio/durations.json"))
NARR = json.load(open(f"{ROOT}/narration.json"))
ORDER = ["c01", "c02", "c03", "c04", "c05", "c06", "c07", "c08", "c09", "c10", "c11", "c12"]
STARTS = {}; _t = 0
for s in ORDER: STARTS[s] = _t; _t += AUD[s]["scene"]
TOTAL = _t
DRAFT = False
GREY = (112, 118, 134)
KTM = (85.32, 27.71)

def at(sc, phrase, key=None):
    """approx. seconds (scene time) when `phrase` is spoken"""
    k = key or sc; txt = NARR[k]; i = txt.find(phrase)
    if i < 0: raise KeyError(phrase)
    base = AUD[sc]["lead"] + (AUD["c04"]["offsets"][["c04a", "c04b", "c04c", "c04d", "c04e"].index(k)] if sc == "c04" else 0)
    dur = (R_dur(k) if sc == "c04" else AUD[sc]["audio"])
    return base + dur * i / len(txt)

_d = {}
def R_dur(k):
    if k not in _d:
        _d[k] = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{ROOT}/audio/{k}.wav"], capture_output=True, text=True).stdout)
    return _d[k]

# ---------------- shared chrome ----------------
def chrome(img, gt, chapter=None, headline=None, h_a=1.0, hl_col=WHITE):
    lay = layer(); d = ImageDraw.Draw(lay)
    # top scrim for legibility
    sc = np.zeros((H, W, 4), np.uint8); g = np.clip(1 - np.arange(H) / 620, 0, 1) ** 1.4
    sc[..., 3] = (g * 200)[:, None]; sc[..., :3] = (10, 12, 17)
    img.alpha_composite(Image.fromarray(sc))
    d.rounded_rectangle((L, 200, RX, 206), 3, fill=(255, 255, 255, 40))
    d.rounded_rectangle((L, 200, L + (RX - L) * min(1, gt / TOTAL), 206), 3, fill=AMBER)
    lay.alpha_composite(R.LOGO64, (L, 226))
    T(d, (L + 80, 228), "Ishaan Pranava", F("Bold", 34))
    T(d, (L + 80, 266), "बैंकिङ र फिनटेक नीति, प्रमाणसहित", F("Regular", 26), fill=MUTED)
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
    """news-style lower third: amber tag + fact + source line"""
    if a <= 0: return
    lay = layer(); d = ImageDraw.Draw(lay)
    ft = F("Bold", 34); fs = F("Regular", 26); tg = F("ExtraBold", 28)
    lines = fact.split("\n"); h = 44 * len(lines) + 72
    d.rounded_rectangle((L, y, RX, y + h), 18, fill=(14, 16, 22, 236))
    d.rounded_rectangle((L, y, L + 10, y + h), 5, fill=AMBER + (255,))
    w = tw(tag, tg) + 28
    d.rounded_rectangle((L + 28, y - 20, L + 28 + w, y + 20), 12, fill=AMBER + (255,)); T(d, (L + 42, y), tag, tg, fill=DARK, anchor="lm")
    yy = y + 32
    for ln in lines: T(d, (L + 32, yy), ln, ft); yy += 44
    T(d, (L + 32, yy + 4), "स्रोत: " + src, fs, fill=MUTED)
    put(img, lay, a, dy=(1 - eout(a)) * 20)

def bigstat(d, xy, s, size=96, col=AMBER, anchor="la"): T(d, xy, s, F("ExtraBold", size), fill=col, anchor=anchor, stroke=4)

def tri(d, x, y, up=True, s=26, col=AMBER):
    pts = [(x, y - s), (x - s, y + s * 0.6), (x + s, y + s * 0.6)] if up else [(x, y + s), (x - s, y - s * 0.6), (x + s, y - s * 0.6)]
    d.polygon(pts, fill=col + (255,))

def hbar(d, x, y, wmax, h, frac, col, label_l=None, val=None, valcol=None):
    d.rounded_rectangle((x, y, x + wmax, y + h), h // 2, fill=(255, 255, 255, 22))
    if frac > 0: d.rounded_rectangle((x, y, x + max(h, wmax * frac), y + h), h // 2, fill=col + (255,))

DESTS = {"ARE": (55.3, 25.2), "MYS": (101.7, 3.1), "QAT": (51.5, 25.3), "SAU": (46.7, 24.7), "KWT": (47.98, 29.37),
         "JPN": (139.7, 35.7), "KOR": (127.0, 37.5), "OMN": (58.4, 23.6), "BHR": (50.58, 26.2)}
GULF12 = ["SAU", "ARE", "QAT", "KWT", "BHR", "OMN", "IRQ", "YEM", "JOR", "LBN", "TUR", "ISR"]
CAM_NEP = (84.55, 28.5, 13.5, 760)
CAM_REG = (74.2, 15.0, 84, 720)
CAM_WIDE = (88.0, 20.0, 112, 820)

def frame(sc, t):
    A = AUD[sc]; gt = STARTS[sc] + t; ta = t - A["lead"]; TT = A["scene"]
    if sc == "c01":
        z = ease((t - (TT - 3.2)) / 2.8)
        cam = camlerp(CAM_WIDE, CAM_NEP, z)
        img = draw_map(cam, {"NPL": (COBALT, 0.92)}, glow="NPL")
        srcs = ["ARE", "MYS", "QAT", "SAU", "KWT", "JPN", "KOR", "OMN", "BHR"]
        for i, a3 in enumerate(srcs):
            st = 0.4 + i * 0.35
            if z < 0.6: arc(img, cam, DESTS[a3], KTM, eout((t - st) / 1.6), bend=0.18, width=4)
        for i, a3 in enumerate(srcs):
            if z < 0.6: pin(img, cam, *DESTS[a3], r=7, col=AMBER)
        pin(img, cam, *KTM, col=COBALT_L, r=11, pulse=(t % 1.4) / 1.4)
        label(img, cam, 84.0, 30.9 if z < 0.5 else 29.1, "नेपाल", 1, size=40 + 18 * z)
        p = eout((ta - 0.2) / 2.2)
        lay = layer(); d = ImageDraw.Draw(lay)
        T(d, (L, 1060), "हरेक दिन, औसतमा", F("Bold", 40), stroke=4)
        bigstat(d, (L, 1110), "रु. " + dev(f"{6.47 * p:.2f}") + " अर्ब", size=110)
        put(img, lay, ease(ta / 0.5))
        chrome(img, gt, "रेमिट्यान्स · आ.व. २०८२/८३", "विदेशबाट नेपाल\nपैसाको नदी", ease(t / 0.6), hl_col=AMBER)
        factstrip(img, "रु. २,३६३.१३ अर्ब ÷ ३६५ दिन ≈ रु. ६.४७ अर्ब/दिन", "नेपाल राष्ट्र बैंक, २०२६-०८-२६ (हिसाब: Ishaan Pranava)", ease((ta - 1.2) / 0.5))
        return img
    if sc == "c02":
        img = draw_map(Cam(*CAM_NEP), {"NPL": (COBALT, 0.92)}, dim=0.55, glow="NPL")
        t1 = at(sc, "श्रम स्वीकृति लिएर"); t2 = at(sc, "नेपाल भित्रिएको")
        cw = (RX - L - 24) // 2
        for i, (ts, ttl, big, up, frm, to, col) in enumerate([
                (t1, "श्रम स्वीकृति", "५.६%", False, "८,३९,२६६", "७,९२,१८७", WHITE),
                (t2, "रेमिट्यान्स", "३७.१%", True, "रु. १७.२३ खर्ब", "रु. २३.६३ खर्ब", AMBER)]):
            a = ease((t - ts) / 0.5)
            if a <= 0: continue
            lay = layer(); d = ImageDraw.Draw(lay); x0 = L + i * (cw + 24)
            panel(d, (x0, 620, x0 + cw, 1150), alpha=0.92)
            T(d, (x0 + 30, 650), ttl, F("Bold", 38))
            tri(d, x0 + 62, 770, up=up, s=30, col=col)
            bigstat(d, (x0 + 106, 712), ("+" if up else "−") + big, size=78, col=col)
            T(d, (x0 + 30, 860), "आ.व. २०८१/८२", F("Regular", 28), fill=MUTED)
            T(d, (x0 + 30, 896), frm, F("Bold", 40), fill=MUTED)
            T(d, (x0 + 30, 966), "आ.व. २०८२/८३", F("Regular", 28), fill=MUTED)
            T(d, (x0 + 30, 1002), to, F("ExtraBold", 46), fill=col)
            put(img, lay, a, dy=(1 - eout(a)) * 30)
        q = ease((t - at(sc, "कम मान्छे")) / 0.4)
        chrome(img, gt, "विरोधाभास", "कम मान्छे,\nधेरै पैसा", ease(t / 0.5) if q <= 0 else 1, hl_col=AMBER)
        factstrip(img, "श्रम स्वीकृति ५.६% घट्यो; रेमिट्यान्स ३७.१% बढ्यो", "नेपाल राष्ट्र बैंक (२०२६-०८-२६); वैदेशिक रोजगार विभाग", ease((t - t2 - 0.6) / 0.5))
        return img
    if sc == "c03":
        img = draw_map(Cam(*CAM_NEP), {"NPL": (COBALT, 0.92)}, dim=0.7)
        t1 = at(sc, "तेइस खर्ब"); t2 = at(sc, "संघीय बजेट")
        lay = layer(); d = ImageDraw.Draw(lay); panel(d, (L, 620, RX, 1180), alpha=0.92)
        put(img, lay, ease(t / 0.4))
        for i, (ts, nm, v, col) in enumerate([(t1, "रेमिट्यान्स आप्रवाह", 23.63, AMBER), (t2, "संघीय बजेट", 19.64, WHITE)]):
            p = eout((t - ts) / 1.0)
            if p <= 0: continue
            lay = layer(); d = ImageDraw.Draw(lay); y = 660 + i * 200
            T(d, (L + 36, y), nm, F("Bold", 38))
            hbar(d, L + 36, y + 60, RX - L - 72, 56, v / 25 * p, col)
            T(d, (L + 36, y + 128), "रु. " + dev(f"{v * p:.2f}") + " खर्ब", F("ExtraBold", 44), fill=col)
            put(img, lay, min(1, (t - ts) / 0.2))
        q = ease((t - t2 - 1.0) / 0.5)
        lay = layer(); d = ImageDraw.Draw(lay)
        T(d, (L + 36, 1080), "फरक: करिब रु. ३.९९ खर्ब", F("ExtraBold", 46), fill=AMBER)
        put(img, lay, q)
        chrome(img, gt, "आकार", "बजेटभन्दा\nठूलो रकम", ease(t / 0.5), hl_col=AMBER)
        factstrip(img, "रेमिट्यान्स रु. २३.६३ खर्ब; बजेट रु. १९.६४ खर्ब (आ.व. २०८२/८३)", "नेपाल राष्ट्र बैंक (२०२६-०८-२६); बजेट वक्तव्य २०८२/८३", ease((t - t2) / 0.5))
        return img
    if sc == "c04":
        D4 = [("ARE", "यूएई", (54.3, 24.0), 183580, (62, 40), "c04a", "संयुक्त"),
              ("MYS", "मलेसिया", (102.0, 4.3), 132646, (-60, 50), "c04b", "मलेसिया"),
              ("QAT", "कतार", (51.2, 25.4), 132051, (-4, -46), "c04c", "कतार"),
              ("SAU", "साउदी अरब", (44.2, 21.0), 124583, (0, 10), "c04d", "साउदी")]
        starts = [at(sc, ph, k) for *_, k, ph in D4]
        cam = camlerp(CAM_NEP, CAM_REG, t / 2.4)
        fills = {"NPL": (COBALT, 0.92)}
        for (a3, *_), s in zip(D4, starts): fills[a3] = (AMBER, 0.88 * ease((t - s) / 0.35))
        img = draw_map(cam, fills, glow="NPL")
        for (a3, *_), s in zip(D4, starts): arc(img, cam, KTM, DESTS[a3], eout((t - s + 0.25) / 0.9), bend=0.22 if a3 != "MYS" else 0.12)
        pin(img, cam, *KTM, col=COBALT_L, r=10)
        label(img, cam, 84.0, 31.4, "नेपाल", 1, size=38)
        for (a3, sh, lp, n, (dx, dy), *_), s in zip(D4, starts): label(img, cam, lp[0], lp[1], sh, ease((t - s) / 0.35), size=36, dx=dx, dy=dy)
        hdr = ease((t - starts[0]) / 0.4)
        lay = layer(); d = ImageDraw.Draw(lay); panel(d, (L, 1010, RX, 1360), alpha=0.92)
        T(d, (L + 36, 1030), "गन्तव्यअनुसार श्रम स्वीकृति · आ.व. २०८२/८३", F("Bold", 32), fill=MUTED)
        put(img, lay, hdr)
        for i, ((a3, sh, lp, n, *_), s) in enumerate(zip(D4, starts)):
            p = eout((t - s) / 0.7)
            if p <= 0: continue
            lay = layer(); d = ImageDraw.Draw(lay); y = 1082 + i * 66
            T(d, (L + 36, y), f"{dev(i + 1)}. {sh}", F("Bold", 36))
            hbar(d, L + 290, y + 12, RX - L - 290 - 200, 30, n / 183580 * p, AMBER)
            T(d, (RX - 36, y), fmt_np(int(n * p)), F("ExtraBold", 36), fill=AMBER, anchor="ra")
            put(img, lay, min(1, (t - s) / 0.25))
        te = at(sc, "यी चार", "c04e")
        q = ease((t - te) / 0.5)
        lay = layer(); d = ImageDraw.Draw(lay)
        d.rounded_rectangle((L, 1380, RX, 1470), 22, fill=AMBER + (255,))
        T(d, (L + 30, 1425), "४ देश = कुलको ७२.३%", F("ExtraBold", 46), fill=DARK, anchor="lm")
        T(d, (RX - 30, 1425), "५,७२,८६० / ७,९२,१८७", F("Bold", 30), fill=DARK, anchor="rm")
        put(img, lay, q, dy=(1 - eout(q)) * 20)
        chrome(img, gt, "नक्सा", "पैसाको बाटो", ease(t / 0.5))
        lay = layer(); d = ImageDraw.Draw(lay)
        T(d, (L, 1492), "स्रोत: वैदेशिक रोजगार विभाग, आ.व. २०८२/८३ (Republica, २०२६-०७-२०)", F("Regular", 26), fill=MUTED, stroke=3)
        put(img, lay, hdr)
        return img
    if sc == "c05":
        cam = Cam(*CAM_REG)
        fills = {"NPL": (COBALT, 0.92)}; [fills.__setitem__(x, (AMBER, 0.88)) for x in ["ARE", "MYS", "QAT", "SAU"]]
        img = draw_map(cam, fills, dim=0.62 * ease(t / 0.5))
        a = ease((t - 0.2) / 0.5)
        lay = layer(); d = ImageDraw.Draw(lay)
        panel(d, (L, 640, RX, 1220), outline=AMBER + (255,))
        cx = (L + RX) / 2
        d.ellipse((cx - 48, 680, cx + 48, 776), fill=AMBER + (255,)); T(d, (cx, 727), "!", F("ExtraBold", 68), fill=DARK, anchor="mm")
        T(d, (cx, 860), "कामदार जाने गन्तव्य", F("ExtraBold", 54), anchor="mm")
        for dy_ in (-10, 10): d.line([(cx - 64, 950 + dy_), (cx + 64, 950 + dy_)], fill=AMBER + (255,), width=7)
        d.line([(cx + 28, 914), (cx - 28, 986)], fill=AMBER + (255,), width=7)
        T(d, (cx, 1040), "रेमिट्यान्स आउने देश", F("ExtraBold", 54), fill=AMBER, anchor="mm")
        T(d, (cx, 1130), "यो तथ्याङ्कले देशगत रेमिट्यान्स देखाउँदैन", F("Regular", 32), fill=MUTED, anchor="mm")
        put(img, lay, a, dy=(1 - eout(a)) * 26)
        chrome(img, gt, "सावधानी", "स्पष्ट पारौँ", ease(t / 0.5))
        return img
    if sc == "c06":
        tp = at(sc, "फागुन सत्र"); tm = at(sc, "मलेसिया पहिलो"); tr = at(sc, "वैशाख सात")
        paused = ease((t - tp) / 0.6) * (1 - 0.65 * ease((t - tr) / 0.8))
        fills = {"NPL": (COBALT, 0.92)}
        for a3 in GULF12: fills[a3] = (GREY, 0.85 * paused) if t < tr else (AMBER, 0.55 * ease((t - tr) / 0.8))
        fills["MYS"] = (AMBER, 0.9 * ease((t - tm) / 0.4))
        cam = camlerp((72.0, 18.0, 100, 780), (71.0, 18.0, 96, 780), t / TT)
        img = draw_map(cam, fills, glow="NPL")
        if t > tm - 0.2: arc(img, cam, KTM, DESTS["MYS"], eout((t - tm + 0.2) / 0.9), bend=0.12)
        pin(img, cam, *KTM, col=COBALT_L, r=10)
        label(img, cam, 44.0, 26.5, "पश्चिम एसिया · १२ देश", ease((t - tp) / 0.4), size=34, dy=-6)
        label(img, cam, 44.0, 21.0, "नयाँ श्रम स्वीकृति रोक" if t < tr else "पुनः खुला", ease((t - tp) / 0.4), size=32, col=(255, 210, 160) if t < tr else AMBER)
        label(img, cam, 102.0, 4.3, "मलेसिया · पहिलो गन्तव्य", ease((t - tm) / 0.4), size=32, dx=-120, dy=54)
        # timeline
        lay = layer(); d = ImageDraw.Draw(lay); panel(d, (L, 1060, RX, 1300), alpha=0.94)
        x0, x1, y = L + 60, RX - 60, 1150
        d.line([(x0, y), (x1, y)], fill=(255, 255, 255, 60), width=6)
        pr = ease((t - tp) / 0.5) * (0.5 + 0.5 * ease((t - tr) / 0.8))
        d.line([(x0, y), (x0 + (x1 - x0) * pr, y)], fill=AMBER + (255,), width=6)
        for xx, on, top, bot in [(x0, t > tp, "फागुन १७, २०८२", "नयाँ स्वीकृति रोक"), (x1, t > tr, "वैशाख ७, २०८३", "पुनः खुला")]:
            d.ellipse((xx - 14, y - 14, xx + 14, y + 14), fill=(AMBER if on else GREY) + (255,), outline=WHITE, width=3)
            anc = "la" if xx == x0 else "ra"
            T(d, (xx - (0 if xx == x0 else 0), y - 66), top, F("Bold", 30), fill=WHITE, anchor=anc)
            T(d, (xx, y + 30), bot, F("Regular", 28), fill=MUTED, anchor=anc)
        T(d, ((x0 + x1) / 2, y + 74), "करिब ७ हप्ता", F("Bold", 28), fill=AMBER, anchor="mm")
        put(img, lay, ease((t - tp) / 0.5))
        chrome(img, gt, "मोड", "बीचमा अवरोध", ease(t / 0.5), hl_col=AMBER)
        factstrip(img, "फागुनमा सबैभन्दा धेरै: मलेसिया (१२,६०१ श्रम स्वीकृति)", "कान्तिपुर (२०२६-०४-२०); वैदेशिक रोजगार विभाग (हिमाल प्रेस)", ease((t - tm) / 0.5), y=1330)
        return img
    if sc == "c07":
        img = draw_map(Cam(*CAM_NEP), {"NPL": (COBALT, 0.92)}, dim=0.72)
        t1 = at(sc, "अमेरिकी डलरमा"); tv = at(sc, "मेरो दृष्टिकोणमा")
        lay = layer(); d = ImageDraw.Draw(lay); panel(d, (L, 620, RX, 1040), alpha=0.92)
        T(d, (L + 36, 645), "रेमिट्यान्स वृद्धि, आ.व. २०८२/८३", F("Bold", 34), fill=MUTED)
        put(img, lay, ease(t / 0.4))
        for i, (s, nm, v, col) in enumerate([(t1 + 0.6, "नेपाली रुपैयाँमा", 37.1, AMBER), (t1, "अमेरिकी डलरमा", 28.1, WHITE)]):
            p = eout((t - s) / 0.9)
            if p <= 0: continue
            lay = layer(); d = ImageDraw.Draw(lay); y = 705 + i * 150
            T(d, (L + 36, y), nm, F("Bold", 36))
            hbar(d, L + 36, y + 54, RX - L - 260, 54, v / 40 * p, col)
            T(d, (RX - 36, y + 81), dev(f"{v * p:.1f}") + "%", F("ExtraBold", 50), fill=col, anchor="rm")
            put(img, lay, min(1, (t - s) / 0.2))
        q = ease((t - t1 - 2.2) / 0.5)
        lay = layer(); d = ImageDraw.Draw(lay)
        T(d, (L + 36, 985), "≈ ९ प्रतिशत बिन्दु फरक: विनिमय दरको प्रभाव", F("Bold", 32), fill=AMBER, anchor="lm")
        put(img, lay, q)
        o = ease((t - tv) / 0.5)
        lay = layer(); d = ImageDraw.Draw(lay)
        d.rounded_rectangle((L, 1070, RX, 1290), 22, fill=(18, 20, 26, 240), outline=AMBER + (255,), width=3)
        T(d, (L + 30, 1092), "मेरो दृष्टिकोण", F("ExtraBold", 36), fill=AMBER)
        T(d, (L + 30, 1146), "अनौपचारिक माध्यमबाट बैंकिङ च्यानलतर्फको", F("Bold", 34))
        T(d, (L + 30, 1192), "सराइ पनि कारण हुन सक्छ", F("Bold", 34))
        T(d, (L + 30, 1240), "पुष्टि गर्न थप तथ्याङ्क चाहिन्छ", F("Regular", 28), fill=MUTED)
        put(img, lay, o, dy=(1 - eout(o)) * 20)
        chrome(img, gt, "विश्लेषण", "किन बढ्यो?", ease(t / 0.5))
        lay = layer(); d = ImageDraw.Draw(lay)
        T(d, (L, 1320), "स्रोत: नेपाल राष्ट्र बैंक, वार्षिक तथ्याङ्क (अनलाइनखबर, २०२६-०८-२६)", F("Regular", 26), fill=MUTED, stroke=3)
        put(img, lay, ease((t - t1) / 0.4))
        return img
    if sc == "c08":
        img = draw_map(Cam(*CAM_NEP), {"NPL": (COBALT, 0.92)}, dim=0.7)
        t1 = at(sc, "छब्बीस"); t2 = at(sc, "अठतीस")
        lay = layer(); d = ImageDraw.Draw(lay); panel(d, (L, 620, RX, 1240), alpha=0.92)
        T(d, (L + 36, 645), "कुल विदेशी विनिमय सञ्चिति", F("Bold", 34), fill=MUTED)
        put(img, lay, ease(t / 0.4))
        base_y, maxh = 1150, 380
        for i, (s, yr, v, col) in enumerate([(t1, "२०८२ असार", 26.77, GREY), (t2, "२०८३ असार", 38.97, AMBER)]):
            p = eout((t - s) / 1.0)
            if p <= 0: continue
            lay = layer(); d = ImageDraw.Draw(lay)
            cx = L + 200 + i * 400; h = maxh * v / 40 * p
            d.rounded_rectangle((cx - 90, base_y - h, cx + 90, base_y), 16, fill=col + (255,))
            T(d, (cx, base_y - h - 14), "रु. " + dev(f"{v * p:.2f}") + " खर्ब", F("ExtraBold", 40), fill=col if i else WHITE, anchor="mb")
            T(d, (cx, base_y + 16), yr, F("Bold", 32), anchor="ma")
            put(img, lay, min(1, (t - s) / 0.2))
        q = ease((t - t2 - 1.1) / 0.5)
        lay = layer(); d = ImageDraw.Draw(lay)
        d.rounded_rectangle((L + 36, 700, L + 250, 770), 35, fill=AMBER + (255,))
        T(d, (L + 143, 735), "+४५.६%", F("ExtraBold", 40), fill=DARK, anchor="mm")
        put(img, lay, q)
        chrome(img, gt, "प्रभाव", "सञ्चिति\nबलियो", ease(t / 0.5), hl_col=AMBER)
        factstrip(img, "असार मसान्त २०८३: रु. ३८.९७ खर्ब (अघिल्लो वर्ष रु. २६.७७ खर्ब)", "नेपाल राष्ट्र बैंक (अनलाइनखबर/कारोबार, २०२६-०८-२६)", ease((t - t2) / 0.5), y=1290)
        return img
    if sc == "c09":
        img = draw_map(Cam(*CAM_NEP), {"NPL": (COBALT, 0.92)}, dim=0.7)
        t1 = at(sc, "चार खर्ब"); t2 = at(sc, "वृद्धिदर")
        p = eout((t - t1) / 1.2)
        lay = layer(); d = ImageDraw.Draw(lay); panel(d, (L, 620, RX, 1250), alpha=0.92)
        T(d, (L + 36, 645), "आ.व. २०८३/८४ · पहिलो दुई महिना (साउन–भदौ)", F("Bold", 32), fill=MUTED)
        bigstat(d, (L + 36, 700), "रु. " + dev(f"{4.3636 * max(p, 0):.2f}") + " खर्ब", size=96)
        put(img, lay, ease(t / 0.4))
        lay = layer(); d = ImageDraw.Draw(lay)
        T(d, (L + 36, 870), "वार्षिक वृद्धिदर (सोही अवधि)", F("Bold", 34))
        for i, (yr, v, col) in enumerate([("गत वर्ष", 33.1, GREY), ("यस वर्ष", 23.9, AMBER)]):
            q = eout((t - t2 - i * 0.6) / 0.9); y = 940 + i * 130
            T(d, (L + 36, y), yr, F("Bold", 34))
            hbar(d, L + 200, y + 4, RX - L - 420, 46, v / 40 * max(q, 0), col)
            T(d, (RX - 36, y - 2), dev(f"{v * max(q, 0):.1f}") + "%", F("ExtraBold", 46), fill=col if i else WHITE, anchor="ra")
        put(img, lay, ease((t - t2) / 0.4))
        chrome(img, gt, "चालु वर्ष", "बढ्दै छ,\nतर सुस्त", ease(t / 0.5), hl_col=AMBER)
        factstrip(img, "दुई महिनामा रु. ४३६.३६ अर्ब, वृद्धि २३.९% (गत वर्ष ३३.१%)", "नेपाल राष्ट्र बैंक, २०२६-१०-१५", ease((t - t2) / 0.5), y=1290)
        return img
    if sc == "c10":
        img = draw_map(Cam(*CAM_NEP), {"NPL": (COBALT, 0.92)}, dim=0.6, glow="NPL")
        pts = [("पहिलो", "निक्षेप र तरलताको ठूलो आधार", "रेमिट्यान्स प्रवाह"),
               ("दोस्रो", "वृद्धिदर सुस्ताउँदा", "असर समयमै पढ्ने"),
               ("तेस्रो", "औपचारिक च्यानलका लागि", "छिटो सेवा + बलियो KYC")]
        for i, (ph, l1, l2) in enumerate(pts):
            s = at(sc, ph)
            a = ease((t - s) / 0.45)
            if a <= 0: continue
            lay = layer(); d = ImageDraw.Draw(lay); y = 640 + i * 230
            panel(d, (L, y, RX, y + 205), alpha=0.94)
            d.rounded_rectangle((L + 30, y + 40, L + 130, y + 140), 26, fill=AMBER + (255,))
            T(d, (L + 80, y + 90), dev(i + 1), F("ExtraBold", 64), fill=DARK, anchor="mm")
            T(d, (L + 160, y + 40), l1, F("ExtraBold", 42))
            T(d, (L + 160, y + 108), l2, F("Bold", 36), fill=AMBER)
            put(img, lay, a, dy=(1 - eout(a)) * 26)
        chrome(img, gt, "मेरो दृष्टिकोण", "बैंकरका लागि\nतीन कुरा", ease(t / 0.5), hl_col=AMBER)
        return img
    if sc == "c11":
        img = Image.new("RGBA", (W, H)); img.alpha_composite(background().convert("RGBA"))
        tq = at(sc, "यो दिगो"); tc = at(sc, "कमेन्टमा"); tf = at(sc, "फलो")
        lay = layer(); d = ImageDraw.Draw(lay)
        T(d, (W / 2, 560), "कम कामदार,", F("ExtraBold", 72), anchor="mm")
        T(d, (W / 2, 650), "धेरै रेमिट्यान्स", F("ExtraBold", 72), fill=AMBER, anchor="mm")
        put(img, lay, ease(t / 0.5))
        q = ease((t - tq) / 0.5)
        lay = layer(); d = ImageDraw.Draw(lay)
        d.rounded_rectangle((L, 760, RX, 920), 30, fill=AMBER + (255,))
        T(d, (W / 2 - 72, 840), "दिगो कि अस्थायी?", F("ExtraBold", 66), fill=DARK, anchor="mm")
        put(img, lay, q, dy=(1 - eout(q)) * 24)
        c = ease((t - tc) / 0.5)
        lay = layer(); d = ImageDraw.Draw(lay)
        T(d, (L, 980), "तपाईंको विश्लेषण कमेन्टमा लेख्नुहोस्", F("Bold", 40))
        put(img, lay, c)
        f = ease((t - tf + 0.6) / 0.5)
        lay = layer(); d = ImageDraw.Draw(lay)
        lay.alpha_composite(LOGO.resize((150, 150)), (L, 1080))
        T(d, (L + 180, 1096), "Ishaan Pranava", F("ExtraBold", 54))
        T(d, (L + 180, 1166), "तथ्यमा आधारित विश्लेषणका लागि फलो गर्नुहोस्", F("Regular", 32), fill=MUTED)
        put(img, lay, f, dy=(1 - eout(f)) * 20)
        chrome(img, gt)
        return img
    if sc == "c12":
        img = Image.new("RGBA", (W, H), (12, 14, 19, 255))
        d = ImageDraw.Draw(img)
        img.alpha_composite(LOGO.resize((120, 120)), (int(W / 2 - 60), 600))
        T(d, (W / 2, 800), "विचार व्यक्तिगत हुन्।", F("ExtraBold", 56), fill=AMBER, anchor="mm")
        T(d, (W / 2, 872), "सार्वजनिक जानकारीमा आधारित।", F("ExtraBold", 56), fill=AMBER, anchor="mm")
        T(d, (W / 2, 950), "Views are personal. Based on publicly available information.", F("Regular", 30), fill=MUTED, anchor="mm")
        T(d, (W / 2, 1000), "लगानी सल्लाह होइन · नक्सा: Natural Earth", F("Regular", 28), fill=FAINT, anchor="mm")
        if DRAFT: T(d, (W / 2, 330), "DRAFT · नक्सा जाँच बाँकी", F("Bold", 30), fill=(255, 120, 110), anchor="mm")
        return img
    raise ValueError(sc)

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
    else:
        for s in sys.argv[1:]: render_scene(s)
