"""'भित्र के हुन्छ? विशेष' — राज्य कसरी चल्छ, कानुन कसरी बन्छ (Ishaan Pranava, 2026-11-14).
Usage: python3 state.py <scene...> | --sheet
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import explainer as X
from explainer import *  # noqa
from PIL import ImageDraw, ImageFont

DJ = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 38)
SRC = "नेपालको संविधान"

def card_col(d, x, y, w, h, title, sub, col):
    d.rounded_rectangle((x, y, x + w, y + h), 20, fill=(18, 21, 30, 245), outline=col + (255,), width=3)
    T(d, (x + w / 2, y + h * 0.38), title, F("ExtraBold", 36), fill=WHITE, anchor="mm")
    T(d, (x + w / 2, y + h * 0.70), sub, F("Regular", 30), fill=col, anchor="mm")

def frame(sc, t):
    img = base(sc, t)
    if sc == "c01":
        label(img, "भित्र के हुन्छ? · विशेष", rv(t, 0.1), col=AMBER)
        head(img, "नियम हरेक ठाउँमा।", "तर बनाउने को?", rv(t, 0.2))
        for i, (ph, s) in enumerate((("ट्राफिक", "ट्राफिक नियम"), ("कर", "कर"), ("बैंकमा", "बैंकिङ नियम"))):
            a = rv(t, at(sc, ph)); lay = layer(); d = ImageDraw.Draw(lay); x = L + i * 300
            box(d, (x, 660, x + 272, 760), s, LINE, F("Bold", 34))
            put(img, lay, a, dy=(1 - eout(a)) * 16)
        for i, (ph, s) in enumerate((("कसले बनायो", "कसले बनाउँछ?"), ("कसले लागू", "कसले लागू गर्छ?"), ("विवाद भए", "विवाद भए, कसले छिन्छ?"))):
            a = rv(t, at(sc, ph)); lay = layer(); d = ImageDraw.Draw(lay); y = 840 + i * 120
            T(d, (L, y), "?", M(700, 54), fill=AMBER)
            T(d, (L + 60, y), s, F("ExtraBold", 52), fill=CYAN if i == 2 else WHITE)
            put(img, lay, a, dy=(1 - eout(a)) * 14)

    elif sc == "c02":
        label(img, "राज्यका अंग", rv(t, 0.1))
        head(img, "तीन अंग,", "एउटा संविधान।", rv(t, 0.2))
        cols = [("व्यवस्थापिका", "कानुन बनाउँछ", AMBER, "व्यवस्थापिकाले"), ("कार्यपालिका", "लागू गर्छ", CYAN, "कार्यपालिकाले"), ("न्यायपालिका", "न्याय दिन्छ", GREEN, "न्यायपालिकाले")]
        b = rv(t, at(sc, "संविधान"))
        if b > 0:
            lay = layer(); d = ImageDraw.Draw(lay)
            d.rounded_rectangle((L, 660, RX, 760), 22, fill=AMBER + (255,))
            T(d, (W / 2, 710), "संविधान · सबैभन्दा माथि", F("ExtraBold", 44), fill=DARK, anchor="mm")
            for i in range(3): d.line((L + 136 + i * 300, 760, L + 136 + i * 300, 830), fill=AMBER + (255,), width=4)
            put(img, lay, b, dy=(1 - eout(b)) * 16)
        for i, (n, s, c, ph) in enumerate(cols):
            a = rv(t, at(sc, ph)); lay = layer(); d = ImageDraw.Draw(lay)
            card_col(d, L + i * 300, 830, 272, 220, n, s, c)
            put(img, lay, a, dy=(1 - eout(a)) * 18)

    elif sc == "c03":
        label(img, "अंग ०१ · व्यवस्थापिका", rv(t, 0.1), col=AMBER)
        head(img, "संघीय संसद:", "दुई सदन।", rv(t, 0.2))
        for i, (ph, big, n, sub) in enumerate((("दुई सय", "२७५", "प्रतिनिधि सभा", "१६५ प्रत्यक्ष · ११० समानुपातिक"), ("उनान्साठी", "५९", "राष्ट्रिय सभा", "५६ निर्वाचित · ३ मनोनीत"))):
            a = rv(t, at(sc, ph)); lay = layer(); d = ImageDraw.Draw(lay); y = 660 + i * 200
            panel(d, (L, y, RX, y + 176), r=22, outline=AMBER if i == 0 else CYAN)
            T(d, (L + 36, y + 88), big, F("ExtraBold", 96), fill=AMBER if i == 0 else CYAN, anchor="lm")
            T(d, (L + 270, y + 62), n, F("ExtraBold", 44), anchor="lm")
            T(d, (L + 270, y + 120), sub, F("Regular", 30), fill=MUTED, anchor="lm")
            put(img, lay, a, dy=(1 - eout(a)) * 16)
        a = rv(t, at(sc, "प्रदेशमा")); lay = layer(); d = ImageDraw.Draw(lay)
        box(d, (L, 1080, 492, 1170), "प्रदेश सभा", LINE, F("Bold", 34)); box(d, (520, 1080, RX, 1170), "गाउँ/नगर सभा", LINE, F("Bold", 34))
        put(img, lay, a)
        src(img, SRC + ", धारा ८४, ८६", rv(t, 1.0))

    elif sc == "c04":
        label(img, "अंग ०२ · कार्यपालिका", rv(t, 0.1), col=CYAN)
        head(img, "मन्त्रिपरिषद्,", "प्रधानमन्त्रीको नेतृत्वमा।", rv(t, 0.2))
        a = rv(t, at(sc, "मन्त्रिपरिषद्")); lay = layer(); d = ImageDraw.Draw(lay)
        panel(d, (L, 700, RX, 1080), r=26, outline=CYAN)
        T(d, (W / 2, 750), "मन्त्रिपरिषद्", F("ExtraBold", 44), fill=CYAN, anchor="mm")
        d.rounded_rectangle((330, 800, 750, 890), 45, fill=CYAN + (255,))
        T(d, (540, 845), "प्रधानमन्त्री", F("ExtraBold", 40), fill=DARK, anchor="mm")
        for i in range(7):
            cx = 200 + i * 113; d.ellipse((cx - 30, 940, cx + 30, 1000), outline=CYAN + (200,), width=3)
        T(d, (W / 2, 1040), "मन्त्रीहरू", F("Regular", 30), fill=MUTED, anchor="mm")
        put(img, lay, a)
        a = rv(t, at(sc, "राष्ट्रपति")); lay = layer(); d = ImageDraw.Draw(lay)
        box(d, (L, 1120, RX, 1220), "राष्ट्रपति · राष्ट्राध्यक्ष", AMBER, F("Bold", 38))
        put(img, lay, a, dy=(1 - eout(a)) * 16)
        src(img, SRC + ", धारा ७५", rv(t, 1.0))

    elif sc == "c05":
        label(img, "अंग ०३ · न्यायपालिका", rv(t, 0.1), col=GREEN)
        head(img, "तीन तह,", "संविधानको रक्षा।", rv(t, 0.2))
        tiers = [("सर्वोच्च अदालत", 320), ("उच्च अदालत", 540), ("जिल्ला अदालत", 760)]
        for i, (s, w) in enumerate(tiers):
            a = rv(t, at(sc, "तीन तह") + i * 0.25); lay = layer(); d = ImageDraw.Draw(lay); y = 680 + i * 110
            x0 = (W - w) / 2
            box(d, (x0, y, x0 + w, y + 92), s, GREEN if i == 0 else LINE, F("Bold", 36), tcol=GREEN if i == 0 else WHITE)
            put(img, lay, a, dy=(1 - eout(a)) * 14)
        a = rv(t, at(sc, "बाझिए")); lay = layer(); d = ImageDraw.Draw(lay)
        d.rounded_rectangle((L, 1040, RX, 1200), 22, fill=(70, 26, 30, 240), outline=RED + (255,), width=3)
        T(d, (L + 30, 1065), "संविधानसँग बाझिएको कानुन", F("Regular", 32), fill=MUTED)
        T(d, (L + 30, 1110), "अमान्य घोषणा हुन सक्छ", F("ExtraBold", 50))
        put(img, lay, a, dy=(1 - eout(a)) * 16)
        src(img, SRC + ", धारा १२८, १३३, १३९, १४८", rv(t, 1.0))

    elif sc == "c06":
        label(img, "मुख्य कुरा", rv(t, 0.1), col=AMBER)
        a = rv(t, 0.3); lay = layer(); d = ImageDraw.Draw(lay)
        T(d, (L, 380), "शक्ति सन्तुलन।", F("ExtraBold", 110), fill=CYAN)
        d.rectangle((L, 532, L + tw("शक्ति सन्तुलन।", F("ExtraBold", 110)) * a, 540), fill=CYAN)
        T(d, (L, 566), "सबै शक्ति एउटै ठाउँमा होइन।", F("Regular", 38), fill=MUTED)
        put(img, lay, a)
        P = {"v": (540, 720), "k": (250, 1130), "n": (830, 1130)}
        a = rv(t, at(sc, "छुट्याइन्छ")); lay = layer(); d = ImageDraw.Draw(lay)
        for key, s, c in (("v", "व्यवस्थापिका", AMBER), ("k", "कार्यपालिका", CYAN), ("n", "न्यायपालिका", GREEN)):
            x, y = P[key]; d.rounded_rectangle((x - 150, y - 50, x + 150, y + 50), 24, fill=(18, 21, 30, 250), outline=c + (255,), width=3)
            T(d, (x, y), s, F("ExtraBold", 36), fill=c, anchor="mm")
        T(d, (540, 1000), "संविधान", F("Bold", 34), fill=FAINT, anchor="mm")
        put(img, lay, a)
        p = ease((t - at(sc, "एउटाले")) / 1.0)
        if p > 0:
            lay = layer(); d = ImageDraw.Draw(lay)
            for (u, v_) in (("v", "k"), ("k", "n"), ("n", "v")):
                (x0, y0), (x1, y1) = P[u], P[v_]
                ox, oy = (x1 - x0) * 0.32, (y1 - y0) * 0.32
                arrow(d, (x0 + ox, y0 + oy), (x1 - ox, y1 - oy), WHITE, p, w=4, head_=16)
                arrow(d, (x1 - ox, y1 - oy), (x0 + ox, y0 + oy), FAINT, p, w=2, head_=12)
            img.alpha_composite(lay)
        bottom(img, [("एउटाले अर्कोलाई", WHITE), ("नियन्त्रण र सन्तुलन", AMBER)], rv(t, at(sc, "एउटाले") + 0.6), y=1260)

    elif sc == "c07":
        label(img, "कानुन ०१ · विधेयक", rv(t, 0.1), col=AMBER)
        head(img, "कानुनको मस्यौदा", "= विधेयक।", rv(t, 0.2))
        a = rv(t, at(sc, "कुनै पनि सदनमा")); lay = layer(); d = ImageDraw.Draw(lay)
        T(d, (L, 640), "दर्ता: कुनै पनि सदनमा", F("Bold", 34), fill=MUTED)
        box(d, (L, 700, 492, 810), "प्रतिनिधि सभा", AMBER, F("Bold", 36)); box(d, (520, 700, RX, 810), "राष्ट्रिय सभा", CYAN, F("Bold", 36))
        put(img, lay, a)
        b = rv(t, at(sc, "अर्थ विधेयक")); lay = layer(); d = ImageDraw.Draw(lay)
        tag(d, (L, 828), "अर्थ विधेयक: यहाँ मात्र", AMBER)
        put(img, lay, b, dy=(1 - eout(b)) * 10)
        stages = [("सामान्य छलफल", "सामान्य छलफल"), ("संशोधन", "संशोधन"), ("समितिमा", "समितिमा दफावार छलफल")]
        for i, (ph, s) in enumerate(stages):
            a = rv(t, at(sc, ph)); lay = layer(); d = ImageDraw.Draw(lay); y = 920 + i * 112
            T(d, (L + 6, y + 44), dev(i + 1), F("ExtraBold", 44), fill=AMBER, anchor="lm")
            box(d, (L + 60, y, RX, y + 88), s, LINE if i < 2 else CYAN, F("Bold", 34), align="lm")
            put(img, lay, a, dy=(1 - eout(a)) * 14)
        src(img, SRC + ", धारा ११०; प्रतिनिधि सभा प्रक्रिया (Farsight Nepal, २०२३)", rv(t, 1.0))

    elif sc == "c08":
        label(img, "कानुन ०२ · दोस्रो सदन", rv(t, 0.1), col=AMBER)
        head(img, "एउटा सदनबाट", "अर्को सदनमा।", rv(t, 0.2))
        a = rv(t, at(sc, "एउटा सदनले")); lay = layer(); d = ImageDraw.Draw(lay)
        box(d, (L, 680, 420, 790), "पहिलो सदन: पारित", GREEN, F("Bold", 32), tcol=GREEN)
        arrow(d, (430, 735), (548, 735), WHITE, ease((t - at(sc, "अर्को सदनमा")) / 0.5), w=5)
        box(d, (560, 680, RX, 790), "दोस्रो सदन", CYAN, F("Bold", 36))
        put(img, lay, a)
        for i, (ph, k, v) in enumerate((("साधारण विधेयक", "साधारण विधेयक", "२ महिनाभित्र"), ("अर्थ विधेयक पन्ध्र", "अर्थ विधेयक", "१५ दिनभित्र"))):
            a = rv(t, at(sc, ph)); lay = layer(); d = ImageDraw.Draw(lay); y = 860 + i * 140
            panel(d, (L, y, RX, y + 116), r=18, outline=LINE)
            T(d, (L + 32, y + 58), k, F("Bold", 40), anchor="lm")
            T(d, (RX - 32, y + 58), v, F("ExtraBold", 48), fill=AMBER, anchor="rm")
            put(img, lay, a, dy=(1 - eout(a)) * 14)
        a = rv(t, at(sc, "फिर्ता पठाउनुपर्छ") + 0.4); lay = layer(); d = ImageDraw.Draw(lay)
        T(d, (L, 1170), "मत नमिले: सुरु भएको सदनमा फिर्ता, वा संयुक्त बैठक", F("Regular", 30), fill=MUTED)
        put(img, lay, a)
        src(img, SRC + ", धारा १११", rv(t, 1.0))

    elif sc == "c09":
        label(img, "कानुन ०३ · प्रमाणीकरण", rv(t, 0.1), col=AMBER)
        head(img, "राष्ट्रपति,", "१५ दिनभित्र।", rv(t, 0.2))
        ts = at(sc, "पन्ध्र दिन"); a = rv(t, ts); lay = layer(); d = ImageDraw.Draw(lay)
        cx, cy, r = 300, 870, 150
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=LINE + (255,), width=16)
        p = min(1, max(0, (t - ts) / 2.0))
        d.arc((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * p, fill=AMBER + (255,), width=16)
        T(d, (cx, cy - 10), "१५", F("ExtraBold", 96), fill=WHITE, anchor="mm"); T(d, (cx, cy + 62), "दिन", F("Bold", 34), fill=MUTED, anchor="mm")
        put(img, lay, a)
        a = rv(t, at(sc, "पुनर्विचार")); lay = layer(); d = ImageDraw.Draw(lay)
        panel(d, (500, 730, RX, 1010), r=20, outline=LINE)
        T(d, (530, 760), "एक पटक", F("Bold", 34), fill=CYAN)
        T(d, (530, 815), "पुनर्विचारका लागि", F("Bold", 34)); T(d, (530, 865), "फिर्ता पठाउन सकिन्छ", F("Bold", 34))
        T(d, (530, 935), "अर्थ विधेयकबाहेक", F("Regular", 28), fill=MUTED)
        put(img, lay, a, dy=(1 - eout(a)) * 14)
        a = rv(t, at(sc, "ऐन बन्छ"), 0.35); lay = layer(); d = ImageDraw.Draw(lay)
        d.rounded_rectangle((L, 1090, RX, 1220), 26, fill=(20, 52, 38, 250), outline=GREEN + (255,), width=4)
        T(d, (W / 2, 1155), "विधेयक अब ऐन बन्यो", F("ExtraBold", 54), fill=GREEN, anchor="mm")
        put(img, lay, a, dy=(1 - eout(a)) * 24)
        src(img, SRC + ", धारा ११३", rv(t, 1.0))

    elif sc == "c10":
        label(img, "भ्रम", rv(t, 0.1), col=RED)
        head(img, "सरकारले आफैं", "कानुन बनाउँछ?", rv(t, 0.2), c2=WHITE)
        a = rv(t, at(sc, "अध्यादेश")); lay = layer(); d = ImageDraw.Draw(lay)
        tag(d, (L, 640), "अध्यादेश", AMBER)
        put(img, lay, a)
        rows = [("अधिवेशन", "कहिले", "दुवै सदनको अधिवेशन एकैसाथ नचलेको बेला", WHITE),
                ("राष्ट्रपतिले", "कसले", "मन्त्रिपरिषद्को सिफारिसमा राष्ट्रपतिले", WHITE),
                ("पारित नगरे", "कहिलेसम्म", "दुवै सदनले पारित नगरे, वा बैठक बसेको\n६० दिनपछि निष्क्रिय", AMBER)]
        for i, (ph, k, v, c) in enumerate(rows):
            a = rv(t, at(sc, ph) if i != 1 else at(sc, ph) - 0.3); lay = layer(); d = ImageDraw.Draw(lay); y = 700 + i * 190
            panel(d, (L, y, RX, y + 168), r=18, outline=LINE if i < 2 else AMBER)
            T(d, (L + 30, y + 22), k, F("Bold", 30), fill=CYAN)
            lines = v.split("\n")
            for j, ln in enumerate(lines[:2]): T(d, (L + 30, y + 68 + j * 46), ln, F("Bold", 36), fill=c)
            put(img, lay, a, dy=(1 - eout(a)) * 14)
        src(img, SRC + ", धारा ११४", rv(t, 1.0))

    elif sc == "c11":
        label(img, "पूरा बाटो", rv(t, 0.1))
        head(img, "विधेयकदेखि", "ऐनसम्म।", rv(t, 0.2))
        steps = [("विधेयक दर्ता", AMBER, "विधेयक दर्ता"), ("छलफल र संशोधन", CYAN, "छलफल र"), ("पहिलो सदनबाट पारित", CYAN, "पहिलो सदनबाट"),
                 ("दोस्रो सदन", CYAN, "दोस्रो सदन"), ("राष्ट्रपतिको प्रमाणीकरण", CYAN, "राष्ट्रपतिको"), ("ऐन", GREEN, "बन्छ, ऐन")]
        y0, hgt, gap = 630, 82, 30
        for i, (s, c, ph) in enumerate(steps):
            ts = at(sc, ph); a = rv(t, 0.4 + i * 0.12, 0.3)
            lay = layer(); d = ImageDraw.Draw(lay); y = y0 + i * (hgt + gap); on = t >= ts
            box(d, (L, y, 760, y + hgt), s, c if on else LINE, F("Bold", 34), tcol=WHITE if on else FAINT, align="lm")
            if i < len(steps) - 1: arrow(d, (L + 120, y + hgt + 2), (L + 120, y + hgt + gap - 2), (c if on else LINE), 1.0, w=4, head_=12)
            put(img, lay, a)
        src(img, SRC + ", धारा ११०–११३", rv(t, 1.0))

    elif sc == "c12":
        a = rv(t, 0.2); lay = layer(); d = ImageDraw.Draw(lay)
        T(d, (W / 2, 560), "तपाईंलाई कुन कानुन", F("ExtraBold", 66), anchor="mm")
        T(d, (W / 2, 650), "बुझ्न मन छ?", F("ExtraBold", 66), fill=AMBER, anchor="mm")
        d.rounded_rectangle((200, 740, 880, 860), 30, outline=CYAN + (255,), width=3)
        T(d, (540, 800), "कमेन्टमा लेख्नुहोस्", F("Bold", 44), fill=CYAN, anchor="mm")
        put(img, lay, a)
        f = rv(t, 1.2); lay = layer(); d = ImageDraw.Draw(lay)
        lay.alpha_composite(LOGO.resize((120, 120)), (L, 980))
        T(d, (L + 150, 990), "Ishaan Pranava", F("ExtraBold", 48))
        T(d, (L + 150, 1050), "बुझौँ, तथ्य र स्रोतसहित", F("Regular", 32), fill=MUTED)
        put(img, lay, f)

    else:
        lay = layer(); d = ImageDraw.Draw(lay)
        panel(d, (L, 760, RX, 1160), r=30, outline=LINE)
        for i, s in enumerate(("जानकारीमूलक सामग्री", "कानुनी सल्लाह होइन", "संविधानको सार्वजनिक पाठमा आधारित", "आवाज: एआई")):
            T(d, (W / 2, 830 + i * 82), s, F("Bold", 40), fill=WHITE if i == 0 else MUTED, anchor="mm")
        img.alpha_composite(lay)
    return img

X.frame = frame
if __name__ == "__main__":
    if sys.argv[1] == "--still": frame(sys.argv[2], float(sys.argv[3])).convert("RGB").save(sys.argv[4])
    elif sys.argv[1] == "--sheet":
        os.makedirs("stills", exist_ok=True); ims = []
        for sc in ORDER:
            im = frame(sc, AUD[sc]["scene"] - 0.4).convert("RGB"); dd = ImageDraw.Draw(im); dd.rectangle((L, 220, RX, 1560), outline=(255, 0, 0), width=3)
            T(dd, (20, 20), sc, F("Bold", 60), fill=(255, 0, 0)); ims.append(im.resize((360, 640)))
        sh = Image.new("RGB", (360 * 7, 640 * 2))
        for i, im in enumerate(ims): sh.paste(im, ((i % 7) * 360, (i // 7) * 640))
        sh.save("stills/sheet.png")
    else:
        for s in sys.argv[1:]: X.render_scene(s)
