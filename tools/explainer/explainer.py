"""'भित्र के हुन्छ?' explainer — भाग १: QR भुक्तानी (Ishaan Pranava, original code, 2026-11-14).
Usage (work folder): python3 explainer.py <scene...> | --still <scene> <t> <out.png> | --sheet
"""
import sys, os, json, math, random, subprocess
sys.path.insert(0, "/home/claude/ishaan-pranava-media/tools/mapvideo")
from PIL import Image, ImageDraw, ImageFont
import engine as E
from engine import W, H, FPS, L, R as RX, F, T, tw, layer, put, panel, ease, eout, dev, AMBER, COBALT, COBALT_L, WHITE, DARK, MUTED, FAINT, LOGO, background

E.DRAFT = False
ROOT = os.getcwd()
AUD = json.load(open(f"{ROOT}/audio/durations.json"))
NARR = json.load(open(f"{ROOT}/narration.json"))
ORDER = list(AUD.keys())
STARTS, _t = {}, 0.0
for s in ORDER: STARTS[s] = _t; _t += AUD[s]["scene"]
TOTAL = _t
GREEN = (88, 196, 132); RED = (232, 92, 92); LINE = (60, 68, 88); CYAN = (130, 160, 255)
_mf = {}
def M(w, s):
    if (w, s) not in _mf: _mf[(w, s)] = ImageFont.truetype(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"JBMono-{w}.ttf"), s)
    return _mf[(w, s)]

def at(sc, phrase):
    txt = NARR[sc]; i = txt.find(phrase)
    if i < 0: raise KeyError(f"{sc}: {phrase}")
    return AUD[sc]["lead"] + AUD[sc]["audio"] * i / len(txt)

def rv(t, ts, d=0.45): return ease((t - ts) / d)

# ---------- drawing helpers ----------
def label(img, s, a, col=CYAN):
    lay = layer(); d = ImageDraw.Draw(lay)
    T(d, (L, 352), "//", M(700, 30), fill=col, anchor="lm")
    T(d, (L + 50, 350), s, F("Bold", 32), fill=col, anchor="lm")
    put(img, lay, a)

def head(img, l1, l2, a, c2=AMBER, size=76, y=392):
    lay = layer(); d = ImageDraw.Draw(lay)
    T(d, (L, y), l1, F("ExtraBold", size))
    if l2: T(d, (L, y + int(size * 1.22)), l2, F("ExtraBold", size), fill=c2)
    put(img, lay, a, dy=(1 - eout(a)) * 24)

def box(d, xy, text, col, f=None, fill_a=0.95, tcol=WHITE, r=18, w=3, align="mm"):
    x0, y0, x1, y1 = xy
    d.rounded_rectangle(xy, r, fill=(18, 21, 30, int(255 * fill_a)), outline=col + (255,), width=w)
    f = f or F("Bold", 38)
    if align == "mm": T(d, ((x0 + x1) / 2, (y0 + y1) / 2), text, f, fill=tcol, anchor="mm")
    else: T(d, (x0 + 28, (y0 + y1) / 2), text, f, fill=tcol, anchor="lm")

def dashed_rect(d, xy, col, dash=14, gap=10, w=3, r=0):
    x0, y0, x1, y1 = xy
    for (a, b, c, e) in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)):
        L_ = math.hypot(c - a, e - b); n = int(L_ // (dash + gap)) + 1
        for i in range(n):
            s0 = i * (dash + gap) / L_; s1 = min(1, (i * (dash + gap) + dash) / L_)
            d.line((a + (c - a) * s0, b + (e - b) * s0, a + (c - a) * s1, b + (e - b) * s1), fill=col, width=w)

def arrow(d, p0, p1, col, prog=1.0, w=5, head_=18, dashed=False):
    if prog <= 0: return
    x0, y0 = p0; x1, y1 = p1
    xe, ye = x0 + (x1 - x0) * prog, y0 + (y1 - y0) * prog
    if dashed:
        L_ = math.hypot(xe - x0, ye - y0); n = int(L_ // 22) + 1
        for i in range(n):
            s0 = i * 22 / max(L_, 1); s1 = min(1, (i * 22 + 12) / max(L_, 1))
            d.line((x0 + (xe - x0) * s0, y0 + (ye - y0) * s0, x0 + (xe - x0) * s1, y0 + (ye - y0) * s1), fill=col, width=w)
    else:
        d.line((x0, y0, xe, ye), fill=col, width=w)
    ang = math.atan2(ye - y0, xe - x0)
    pts = [(xe, ye), (xe - head_ * math.cos(ang - 0.45), ye - head_ * math.sin(ang - 0.45)),
           (xe - head_ * math.cos(ang + 0.45), ye - head_ * math.sin(ang + 0.45))]
    d.polygon(pts, fill=col)

def bottom(img, parts, a, y=1372, size=40):
    """parts: [(text, colour)] drawn on one line"""
    lay = layer(); d = ImageDraw.Draw(lay); x = L
    for s, c in parts:
        T(d, (x, y), s, F("Bold", size), fill=c); x += tw(s, F("Bold", size)) + 12
    put(img, lay, a, dy=(1 - eout(a)) * 16)

def src(img, s, a):
    lay = layer(); d = ImageDraw.Draw(lay)
    T(d, (L, 1486), "स्रोत: " + s, F("Regular", 27), fill=FAINT)
    put(img, lay, a)

def tag(d, xy, s, col=MUTED):
    f = F("Bold", 24); x, y = xy; w = tw(s, f) + 24
    d.rounded_rectangle((x, y, x + w, y + 38), 19, outline=col, width=2)
    T(d, (x + w / 2, y + 19), s, f, fill=col, anchor="mm")

def base(sc, t):
    img = background().copy().convert("RGBA")
    E.chrome(img, STARTS[sc] + t, TOTAL)
    return img

random.seed(7)
QR = [[random.random() < 0.47 for _ in range(25)] for _ in range(25)]
def draw_qr(d, x0, y0, size, a=1.0, scan=None):
    c = size / 25; col = (235, 238, 245, int(255 * a))
    d.rounded_rectangle((x0 - 18, y0 - 18, x0 + size + 18, y0 + size + 18), 18, fill=(245, 246, 250, int(255 * a)))
    for i in range(25):
        for j in range(25):
            fin = any(i0 <= i < i0 + 7 and j0 <= j < j0 + 7 for i0, j0 in ((0, 0), (0, 18), (18, 0)))
            if fin:
                ii, jj = i % 18 if i >= 18 else i, j % 18 if j >= 18 else j
                on = (ii in (0, 6) or jj in (0, 6) or (2 <= ii <= 4 and 2 <= jj <= 4))
            else: on = QR[i][j]
            if on: d.rectangle((x0 + j * c, y0 + i * c, x0 + (j + 1) * c - 1, y0 + (i + 1) * c - 1), fill=(16, 18, 26, int(255 * a)))
    if scan is not None and 0 < scan < 1:
        yy = y0 + size * scan
        d.rectangle((x0 - 18, yy - 3, x0 + size + 18, yy + 3), fill=AMBER + (int(230 * a),))

# ---------- scenes ----------
def frame(sc, t):
    img = base(sc, t)
    if sc == "c01":
        label(img, "भित्र के हुन्छ? · भाग १", rv(t, 0.1), col=AMBER)
        head(img, "तपाईं स्क्यान गर्नुहुन्छ।", "पसलेको 'टिङ' बज्छ।", rv(t, 0.2))
        a1 = rv(t, 0.6); lay = layer(); d = ImageDraw.Draw(lay)
        box(d, (360, 650, RX, 750), "रु. ५०० · राम चिया पसल", AMBER, F("Bold", 36)); tag(d, (360, 610), "उदाहरण")
        put(img, lay, a1, dy=(1 - eout(a1)) * 20)
        a2 = rv(t, at(sc, "अनि")); lay = layer(); d = ImageDraw.Draw(lay)
        dashed_rect(d, (L, 800, RX, 1060), (100, 130, 220, 255))
        T(d, (W / 2, 900), "?    ?    ?", M(700, 96), fill=CYAN, anchor="mm")
        T(d, (W / 2, 1000), "बीचमा के-के हुन्छ", F("Regular", 32), fill=MUTED, anchor="mm")
        put(img, lay, a2)
        a3 = rv(t, at(sc, "टिङ")); lay = layer(); d = ImageDraw.Draw(lay)
        box(d, (L, 1110, 700, 1210), "भुक्तानी प्राप्त: रु. ५००", GREEN, F("Bold", 36), tcol=GREEN)
        put(img, lay, a3, dy=(1 - eout(a3)) * 20)
        a4 = rv(t, at(sc, "तर ती")); lay = layer(); d = ImageDraw.Draw(lay)
        T(d, (L, 1300), "तर बीचमा", F("ExtraBold", 54)); x = L + tw("तर बीचमा", F("ExtraBold", 54)) + 18
        T(d, (x, 1300), "के हुन्छ?", F("ExtraBold", 54), fill=CYAN)
        d.rectangle((x, 1382, x + tw("के हुन्छ?", F("ExtraBold", 54)) * min(1, max(0, (t - at(sc, "तर ती") - 0.3) / 0.5)), 1388), fill=CYAN)
        put(img, lay, a4, dy=(1 - eout(a4)) * 16)

    elif sc == "c02":
        label(img, "चरण ०१ · स्क्यान", rv(t, 0.1))
        head(img, "QR एउटा चित्र होइन,", "सूचनाको लहर हो।", rv(t, 0.2))
        a = rv(t, 0.5); lay = layer(); d = ImageDraw.Draw(lay)
        draw_qr(d, L + 18, 650, 330, 1.0, scan=((t - 0.8) % 2.2) / 1.6 if t < at(sc, "तपाईंको एपले") else None)
        put(img, lay, a)
        a = rv(t, at(sc, "अक्षर र अंक")); lay = layer(); d = ImageDraw.Draw(lay)
        s1 = "000201 010211 26..XXXX"; s2 = "5913RAM CHIYA PASAL"; s3 = "6009KATHMANDU 5403500"
        for i, s in enumerate((s1, s2, s3)): T(d, (L, 1050 + 46 * i), s, M(500, 34), fill=CYAN)
        tag(d, (L, 1196), "उदाहरण · EMVCo ढाँचा")
        put(img, lay, a)
        fields = [("पसलेको पहिचान", "पसलेको पहिचान", AMBER), ("नाम", "नाम: राम चिया पसल", WHITE), ("सहर", "सहर: काठमाडौं", WHITE), ("रकम", "रकम (कहिलेकाहीँ)", WHITE)]
        y = 650
        for ph, s, c in fields:
            a = rv(t, at(sc, ph)); lay = layer(); d = ImageDraw.Draw(lay)
            box(d, (440, y, RX, y + 84), s, COBALT_L, F("Bold", 32), tcol=c, align="lm")
            put(img, lay, a, dy=(1 - eout(a)) * 14); y += 100
        bottom(img, [("तपाईंको", WHITE), ("एपले", CYAN), ("पढेर छुट्याउँछ।", WHITE)], rv(t, at(sc, "तपाईंको एपले")), y=1290)
        src(img, "नेपाल राष्ट्र बैंक, NepalQR Framework (फेब्रुअरी २०२१)", rv(t, 1.0))

    elif sc == "c03":
        label(img, "चरण ०२ · अनुमति", rv(t, 0.1))
        head(img, "तपाईंको बैंकले", "रकम काट्छ।", rv(t, 0.2))
        a = rv(t, at(sc, "रकम हाल्नु")); lay = layer(); d = ImageDraw.Draw(lay)
        panel(d, (L, 650, RX, 900), r=24, outline=AMBER)
        T(d, (L + 36, 690), "रकम", F("Regular", 30), fill=MUTED); T(d, (L + 36, 730), "रु. ५००", F("ExtraBold", 64))
        n = int(max(0, min(4, (t - at(sc, "पिन")) / 0.25)))
        for i in range(4):
            cx = 620 + i * 70; cy = 775
            d.ellipse((cx - 18, cy - 18, cx + 18, cy + 18), fill=(AMBER if i < n else (60, 66, 84)))
        T(d, (620 - 18, 830), "PIN / OTP", M(500, 28), fill=MUTED)
        put(img, lay, a, dy=(1 - eout(a)) * 18)
        a = rv(t, at(sc, "तपाईंको बैंक")); lay = layer(); d = ImageDraw.Draw(lay)
        panel(d, (L, 950, RX, 1220), r=24, outline=COBALT_L)
        T(d, (L + 36, 985), "तपाईंको खाता", F("Bold", 36))
        tag(d, (RX - 230, 985), "ISSUER · इस्युअर", CYAN)
        b = rv(t, at(sc, "छ कि छैन"))
        if b > 0: T(d, (L + 36, 1060), "मौज्दात जाँच", F("Regular", 34), fill=MUTED); T(d, (L + 270, 1062), "✓", ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40), fill=GREEN)
        c = rv(t, at(sc, "रकम काट्छ"))
        if c > 0: T(d, (L + 36, 1120), "− रु. ५००", F("ExtraBold", 66), fill=AMBER)
        put(img, lay, a, dy=(1 - eout(a)) * 18)
        bottom(img, [("इस्युअर", CYAN), ("= तपाईंको बैंक वा वालेट", WHITE)], rv(t, at(sc, "इस्युअर")), y=1290)

    elif sc == "c04":
        label(img, "चरण ०३ · नेटवर्क", rv(t, 0.1), col=AMBER)
        a = rv(t, 0.3); lay = layer(); d = ImageDraw.Draw(lay)
        T(d, (L, 380), "नेटवर्क।", F("ExtraBold", 130), fill=CYAN)
        d.rectangle((L, 548, L + tw("नेटवर्क।", F("ExtraBold", 130)) * a, 556), fill=CYAN)
        T(d, (L, 580), "फरक बैंक, एउटै QR।", F("Regular", 38), fill=MUTED)
        put(img, lay, a)
        top = [("अर्को बैंक", False), ("तपाईंको बैंक", True), ("वालेट", False)]
        bot = [("बैंक", False), ("पसलेको बैंक", True), ("वालेट", False)]
        xs = [L, 360, 656]; bw = 280
        hub = (300, 930, 780, 1060)
        a_top = rv(t, at(sc, "तपाईंको बैंक एउटा")); a_bot = rv(t, at(sc, "पसलेको बैंक अर्को")); a_hub = rv(t, at(sc, "बीचमा"))
        lay = layer(); d = ImageDraw.Draw(lay)
        for i, (s, hl) in enumerate(top):
            if a_hub > 0: d.line((xs[i] + bw / 2, 790, (hub[0] + hub[2]) / 2, hub[1]), fill=(LINE if not hl else LINE) + (int(255 * a_hub),), width=3)
        for i, (s, hl) in enumerate(bot):
            if a_hub > 0: d.line(((hub[0] + hub[2]) / 2, hub[3], xs[i] + bw / 2, 1200), fill=LINE + (int(255 * a_hub),), width=3)
        img.alpha_composite(lay)
        lay = layer(); d = ImageDraw.Draw(lay)
        for i, (s, hl) in enumerate(top):
            box(d, (xs[i], 690, xs[i] + bw, 790), s, AMBER if hl else LINE, F("Bold", 32), tcol=WHITE if hl else FAINT)
        put(img, lay, a_top)
        lay = layer(); d = ImageDraw.Draw(lay)
        for i, (s, hl) in enumerate(bot):
            box(d, (xs[i], 1200, xs[i] + bw, 1300), s, GREEN if hl else LINE, F("Bold", 32), tcol=WHITE if hl else FAINT)
        put(img, lay, a_bot)
        lay = layer(); d = ImageDraw.Draw(lay)
        d.rounded_rectangle(hub, 22, fill=(24, 34, 74, 245), outline=CYAN + (255,), width=4)
        T(d, ((hub[0] + hub[2]) / 2, 975), "QR नेटवर्क", F("ExtraBold", 44), fill=WHITE, anchor="mm")
        T(d, ((hub[0] + hub[2]) / 2, 1030), "Fonepay · NEPALPAY QR", M(500, 24), fill=CYAN, anchor="mm")
        put(img, lay, a_hub)
        p = ease((t - at(sc, "सन्देशलाई")) / 1.2)
        if p > 0:
            lay = layer(); d = ImageDraw.Draw(lay); cx = (hub[0] + hub[2]) / 2
            arrow(d, (500, 790), (cx, hub[1]), AMBER, min(1, p * 2), w=6)
            if p > 0.5: arrow(d, (cx, hub[3]), (500, 1200), AMBER, (p - 0.5) * 2, w=6)
            img.alpha_composite(lay)
        bottom(img, [("NEPALPAY QR मा मात्र:", MUTED), ("५६", AMBER), ("एप/संस्था ·", MUTED), ("५२", AMBER), ("acquirer", MUTED)], rv(t, at(sc, "जसले")), y=1350, size=32)
        src(img, "NCHL, NEPALPAY QR पृष्ठ (२०२६-११-१४ मा हेरिएको)", rv(t, at(sc, "जसले")))

    elif sc == "c05":
        label(img, "चरण ०४ · सूचना", rv(t, 0.1))
        head(img, "पसलेको बैंकले", "सूचना पठाउँछ।", rv(t, 0.2))
        a = rv(t, at(sc, "पसलेको बैंक")); lay = layer(); d = ImageDraw.Draw(lay)
        panel(d, (230, 680, 850, 1220), r=46, outline=LINE)
        d.rounded_rectangle((470, 700, 610, 716), 8, fill=LINE)
        T(d, (540, 780), "राम चिया पसल", F("Bold", 38), anchor="mm")
        T(d, (540, 830), "पसलेको मोबाइल", F("Regular", 28), fill=FAINT, anchor="mm")
        tag(d, (L, 620), "ACQUIRER · एक्वायरर = पसलेको बैंक", CYAN)
        put(img, lay, a)
        ts = at(sc, "टिङ"); b = rv(t, ts, 0.3)
        if b > 0:
            lay = layer(); d = ImageDraw.Draw(lay)
            for k in range(2):
                q = ((t - ts) * 0.9 + k * 0.5) % 1.0
                rr = 60 + 160 * q
                d.ellipse((540 - rr, 1010 - rr, 540 + rr, 1010 + rr), outline=GREEN + (int(160 * (1 - q)),), width=4)
            d.rounded_rectangle((260, 930, 820, 1090), 26, fill=(20, 52, 38, 250), outline=GREEN + (255,), width=3)
            T(d, (540, 980), "भुक्तानी प्राप्त", F("Bold", 38), fill=GREEN, anchor="mm")
            T(d, (540, 1040), "रु. ५००", F("ExtraBold", 50), anchor="mm")
            put(img, lay, b, dy=(1 - eout(b)) * 30)
        bottom(img, [("हरेक कारोबारको", WHITE), ("सूचना/SMS", GREEN), ("पसलेलाई", WHITE)], rv(t, ts + 0.6), y=1290)
        src(img, "नेपाल राष्ट्र बैंक, NepalQR Framework, खण्ड ४.५ (२०२१)", rv(t, ts + 0.6))

    elif sc == "c06":
        label(img, "भ्रम", rv(t, 0.1), col=RED)
        head(img, "पैसा तुरुन्तै", "बैंकबाट बैंकमा?", rv(t, 0.2), c2=WHITE)
        a = rv(t, 0.5); lay = layer(); d = ImageDraw.Draw(lay)
        dashed_rect(d, (L + 60, 680, RX - 60, 800), (170, 80, 80, 255))
        T(d, (W / 2, 740), "तपाईंको बैंकबाट पसलेको बैंकमा", F("Bold", 38), fill=(200, 200, 210), anchor="mm")
        s = ease((t - at(sc, "सरिसकेको")) / 0.5)
        if s > 0: d.line((L + 80, 790, L + 80 + (RX - L - 160) * s, 690), fill=RED + (255,), width=6)
        put(img, lay, a)
        b = rv(t, at(sc, "सरिसकेको") + 0.4); lay = layer(); d = ImageDraw.Draw(lay)
        T(d, (W / 2, 880), "होइन।", F("ExtraBold", 80), fill=RED, anchor="mm")
        put(img, lay, b)
        for i, (ph, k, v, c) in enumerate((("सूचना तुरुन्तै", "सूचना", "तुरुन्तै", GREEN), ("पछि मिलाइन्छ", "बैंकबीचको हिसाब", "पछि", AMBER))):
            a = rv(t, at(sc, ph) - (0.2 if i else 0)); lay = layer(); d = ImageDraw.Draw(lay); y = 1000 + i * 140
            panel(d, (L, y, RX, y + 116), r=18, outline=LINE)
            T(d, (L + 32, y + 58), k, F("Bold", 40), anchor="lm")
            T(d, (RX - 32, y + 58), v, F("ExtraBold", 50), fill=c, anchor="rm")
            put(img, lay, a, dy=(1 - eout(a)) * 16)

    elif sc == "c07":
        label(img, "चरण ०५ · सेटलमेन्ट", rv(t, 0.1))
        head(img, "सबै कारोबार जोडेर,", "खुद हिसाब।", rv(t, 0.2))
        rows = [("बैंक A ले बैंक B लाई", "रु. १,०००"), ("बैंक B ले बैंक A लाई", "रु. ७००")]
        lay = layer(); d = ImageDraw.Draw(lay); tag(d, (L, 640), "उदाहरण"); put(img, lay, rv(t, 0.4))
        for i, (k, v) in enumerate(rows):
            a = rv(t, 0.6 + i * 0.5); lay = layer(); d = ImageDraw.Draw(lay); y = 700 + i * 110
            panel(d, (L, y, RX, y + 92), r=16, outline=LINE)
            T(d, (L + 30, y + 46), k, F("Bold", 36), fill=WHITE, anchor="lm")
            T(d, (RX - 30, y + 46), v, F("Bold", 38), fill=MUTED, anchor="rm")
            put(img, lay, a)
        a = rv(t, at(sc, "खुद हिसाब")); lay = layer(); d = ImageDraw.Draw(lay)
        d.rounded_rectangle((L, 940, RX, 1060), 20, fill=AMBER + (255,))
        T(d, (W / 2, 1000), "खुद: बैंक A ले बैंक B लाई रु. ३००", F("ExtraBold", 42), fill=DARK, anchor="mm")
        put(img, lay, a, dy=(1 - eout(a)) * 18)
        a = rv(t, at(sc, "सेटलमेन्ट")); lay = layer(); d = ImageDraw.Draw(lay)
        T(d, (L, 1100), "नेटवर्क:", F("Bold", 36), fill=CYAN)
        T(d, (L + 160, 1100), "तिर्नेबाट काट्छ, पाउनेलाई दिन्छ", F("Regular", 36))
        put(img, lay, a)
        a = rv(t, at(sc, "अनि पसलेको")); lay = layer(); d = ImageDraw.Draw(lay)
        T(d, (L, 1170), "पसलेको बैंक:", F("Bold", 36), fill=GREEN)
        T(d, (L + 230, 1170), "हिसाब मिलान", F("Regular", 36))
        put(img, lay, a)
        bottom(img, [("यसलाई भनिन्छ", WHITE), ("सेटलमेन्ट।", AMBER)], rv(t, at(sc, "सेटलमेन्ट")), y=1300)
        src(img, "नेपाल राष्ट्र बैंक, NepalQR Framework, खण्ड ४.८ (२०२१)", rv(t, 1.0))

    elif sc == "c08":
        label(img, "कति ठूलो?", rv(t, 0.1), col=AMBER)
        head(img, "सानो प्रक्रिया,", "ठूलो संख्या।", rv(t, 0.2))
        E.stat_card(img, 680, "७.५६ करोड", "QR भुक्तानी (संख्या)", "भदौ २०८३ · एक वर्षअघि ४.११ करोड", (t - at(sc, "सात करोड")) / 0.6, delta="+८४%")
        E.stat_card(img, 960, "रु. १.६८ खर्ब", "QR भुक्तानी (रकम)", "भदौ २०८३ · एक वर्षअघि रु. १.०१ खर्ब", (t - at(sc, "एक खर्ब")) / 0.6, delta="+६६%")
        src(img, "नेपाल राष्ट्र बैंक, Payment Systems Indicators, भदौ २०८३", rv(t, 1.0))

    elif sc == "c09":
        label(img, "पूरा बाटो", rv(t, 0.1))
        head(img, "स्क्यान गर्नुहोस्।", "टिङ सुन्नुहोस्।", rv(t, 0.2))
        steps = [("एपले QR पढ्छ", AMBER, "एपले"), ("तपाईंको बैंकले रकम काट्छ", CYAN, "तपाईंको बैंकले"), ("नेटवर्कले सन्देश पुर्‍याउँछ", CYAN, "नेटवर्कले"),
                 ("पसलेको बैंकले सूचना दिन्छ", CYAN, "पसलेको बैंकले"), ("पसले: टिङ", GREEN, "सूचना दिन्छ")]
        y0, hgt, gap = 640, 96, 34
        for i, (s, c, ph) in enumerate(steps):
            ts = at(sc, ph) if ph != "सूचना दिन्छ" else at(sc, ph) + 0.6
            a = rv(t, 0.4 + i * 0.15, 0.3)
            lay = layer(); d = ImageDraw.Draw(lay); y = y0 + i * (hgt + gap)
            on = t >= ts
            box(d, (L, y, 720, y + hgt), s, c if on else LINE, F("Bold", 34), tcol=WHITE if on else FAINT, align="lm")
            if i < len(steps) - 1: arrow(d, (L + 120, y + hgt + 2), (L + 120, y + hgt + gap - 2), (c if on else LINE), 1.0, w=4, head_=12)
            put(img, lay, a)
        ls = at(sc, "र पछि"); a = rv(t, ls); lay = layer(); d = ImageDraw.Draw(lay)
        ya = y0 + 1 * (hgt + gap) + hgt / 2; yb = y0 + 3 * (hgt + gap) + hgt / 2
        p = ease((t - ls) / 0.9)
        for (x0_, y0_, x1_, y1_) in ((720, ya, 820, ya), (820, ya, 820, yb), (820, yb, 720, yb)):
            pass
        if p > 0:
            arrow(d, (720, ya), (830, ya), AMBER, min(1, p * 3), w=4, head_=1, dashed=True)
            if p > 0.33: arrow(d, (830, ya), (830, yb), AMBER, min(1, (p - 0.33) * 3), w=4, head_=1, dashed=True)
            if p > 0.66: arrow(d, (830, yb), (725, yb), AMBER, (p - 0.66) * 3, w=4, head_=14, dashed=True)
            T(d, (850, (ya + yb) / 2 - 30), "पछि:", F("Bold", 30), fill=AMBER)
            T(d, (850, (ya + yb) / 2 + 10), "हिसाब", F("Bold", 30), fill=AMBER)
        put(img, lay, a)
        src(img, "नेपाल राष्ट्र बैंक, NepalQR Framework (२०२१); NCHL", rv(t, 1.0))

    elif sc == "c10":
        a = rv(t, 0.2); lay = layer(); d = ImageDraw.Draw(lay)
        T(d, (W / 2, 520), "QR स्क्यान गर्दा", F("ExtraBold", 72), anchor="mm")
        T(d, (W / 2, 620), "तपाईं तिर्नुहुन्छ।", F("ExtraBold", 72), fill=AMBER, anchor="mm")
        put(img, lay, a)
        a = rv(t, at(sc, "पाउनुहुन्न")); lay = layer(); d = ImageDraw.Draw(lay)
        d.rounded_rectangle((L, 700, RX, 820), 24, fill=(70, 26, 30, 240), outline=RED + (255,), width=3)
        T(d, (W / 2, 760), "पैसा पाउन QR स्क्यान गर्नुपर्दैन", F("Bold", 40), fill=WHITE, anchor="mm")
        put(img, lay, a, dy=(1 - eout(a)) * 18)
        a = rv(t, at(sc, "अर्को भागमा")); lay = layer(); d = ImageDraw.Draw(lay)
        panel(d, (L, 880, RX, 1100), r=24, outline=CYAN)
        T(d, (L + 36, 920), "//", M(700, 28), fill=CYAN); T(d, (L + 80, 918), "अर्को भाग", F("Bold", 30), fill=CYAN)
        T(d, (L + 36, 975), "विदेशबाट पठाएको पैसा", F("ExtraBold", 50))
        T(d, (L + 36, 1035), "घरसम्म कसरी आउँछ?", F("ExtraBold", 50), fill=AMBER)
        put(img, lay, a, dy=(1 - eout(a)) * 18)
        f = rv(t, at(sc, "अर्को भागमा") + 1.6); lay = layer(); d = ImageDraw.Draw(lay)
        lay.alpha_composite(LOGO.resize((120, 120)), (L, 1170))
        T(d, (L + 150, 1180), "Ishaan Pranava", F("ExtraBold", 48))
        T(d, (L + 150, 1240), "परिवारलाई सेयर गर्नुहोस् · फलो गर्नुहोस्", F("Regular", 32), fill=MUTED)
        put(img, lay, f)

    else:  # disclaimer
        lay = layer(); d = ImageDraw.Draw(lay)
        panel(d, (L, 760, RX, 1160), r=30, outline=LINE)
        for i, s in enumerate(("विचार व्यक्तिगत", "सार्वजनिक जानकारीमा आधारित", "लगानी सल्लाह होइन", "आवाज: एआई")):
            T(d, (W / 2, 830 + i * 82), s, F("Bold", 40), fill=WHITE if i == 0 else MUTED, anchor="mm")
        img.alpha_composite(lay)
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
            tt = AUD[sc]["scene"] - 0.4
            im = frame(sc, tt).convert("RGB"); dd = ImageDraw.Draw(im); dd.rectangle((L, 220, RX, 1560), outline=(255, 0, 0), width=3)
            T(dd, (20, 20), sc, F("Bold", 60), fill=(255, 0, 0)); im.save(f"stills/{sc}.png"); ims.append(im.resize((360, 640)))
        sh = Image.new("RGB", (360 * 6, 640 * 2))
        for i, im in enumerate(ims): sh.paste(im, ((i % 6) * 360, (i // 6) * 640))
        sh.save("stills/sheet.png")
    else:
        for s in sys.argv[1:]: render_scene(s)
