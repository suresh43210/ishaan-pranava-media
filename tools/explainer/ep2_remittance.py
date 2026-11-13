"""'भित्र के हुन्छ?' भाग २ — रेमिट्यान्स घरसम्म कसरी आउँछ (Ishaan Pranava, 2026-11-14).
Reuses helpers from the QR explainer template. Usage: python3 remit.py <scene...> | --still sc t out.png | --sheet
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import explainer as X
from explainer import *  # noqa: helpers, colours, AUD/NARR of the current folder
from PIL import ImageDraw, ImageFont

DJ = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)

def frame(sc, t):
    img = base(sc, t)
    if sc == "c01":
        label(img, "भित्र के हुन्छ? · भाग २", rv(t, 0.1), col=AMBER)
        head(img, "रमेश कतारबाट पठाउँछन्।", "आमाको मोबाइलमा पैसा।", rv(t, 0.2))
        a = rv(t, 0.6); lay = layer(); d = ImageDraw.Draw(lay)
        tag(d, (L, 610), "उदाहरण")
        box(d, (L, 650, 640, 750), "कतार · रमेश · १,००० रियाल", AMBER, F("Bold", 34), align="lm")
        put(img, lay, a, dy=(1 - eout(a)) * 20)
        a = rv(t, at(sc, "र केही बेरमै")); lay = layer(); d = ImageDraw.Draw(lay)
        box(d, (360, 1040, RX, 1140), "गाउँ · आमा · पैसा आयो", GREEN, F("Bold", 34), tcol=GREEN, align="lm")
        put(img, lay, a, dy=(1 - eout(a)) * 20)
        a = rv(t, at(sc, "तर हजारौँ")); lay = layer(); d = ImageDraw.Draw(lay)
        dashed_rect(d, (L, 790, RX, 1000), (100, 130, 220, 255))
        T(d, (W / 2, 870), "?    ?    ?", M(700, 90), fill=CYAN, anchor="mm")
        T(d, (W / 2, 955), "हजारौँ किलोमिटरबीच के हुन्छ", F("Regular", 32), fill=MUTED, anchor="mm")
        put(img, lay, a)
        a = rv(t, at(sc, "त्यो पैसा कसरी")); lay = layer(); d = ImageDraw.Draw(lay)
        T(d, (L, 1230), "तर पैसा", F("ExtraBold", 54)); x = L + tw("तर पैसा", F("ExtraBold", 54)) + 18
        T(d, (x, 1230), "कसरी आयो?", F("ExtraBold", 54), fill=CYAN)
        d.rectangle((x, 1312, x + tw("कसरी आयो?", F("ExtraBold", 54)) * min(1, max(0, (t - at(sc, "त्यो पैसा कसरी") - 0.3) / 0.5)), 1318), fill=CYAN)
        put(img, lay, a, dy=(1 - eout(a)) * 16)

    elif sc == "c02":
        label(img, "चरण ०१ · पठाउने", rv(t, 0.1))
        head(img, "विदेशमा तिर्छन्,", "नम्बर पाउँछन्।", rv(t, 0.2))
        a = rv(t, at(sc, "रमेश विदेशको")); lay = layer(); d = ImageDraw.Draw(lay)
        panel(d, (L, 650, RX, 1200), r=26, outline=AMBER)
        T(d, (L + 36, 690), "रेमिट्यान्स कम्पनी · विदेश", F("Bold", 34), fill=AMBER)
        tag(d, (RX - 130, 690), "उदाहरण")
        d.line((L + 36, 760, RX - 36, 760), fill=LINE, width=2)
        put(img, lay, a)
        rows = [("रियाल", "रकम", "१,००० रियाल", WHITE), ("पाउनेको नाम", "पाउने", "आमा · नेपाल", WHITE), ("कारोबार नम्बर", "कारोबार नम्बर", None, AMBER)]
        for i, (ph, k, v, c) in enumerate(rows):
            a = rv(t, at(sc, ph)); lay = layer(); d = ImageDraw.Draw(lay); y = 800 + i * 120
            T(d, (L + 36, y + 30), k, F("Regular", 34), fill=MUTED, anchor="lm")
            if v: T(d, (RX - 36, y + 30), v, F("Bold", 40), fill=c, anchor="rm")
            else: T(d, (RX - 36, y + 30), "#### ####", M(700, 44), fill=c, anchor="rm")
            put(img, lay, a, dy=(1 - eout(a)) * 14)
        bottom(img, [("एप वा काउन्टर,", WHITE), ("दुवै बाटो", CYAN)], rv(t, at(sc, "वा एपमा")), y=1270)

    elif sc == "c03":
        label(img, "चरण ०२ · इजाजत", rv(t, 0.1))
        head(img, "बीचमा राष्ट्र बैंकको", "इजाजत र स्वीकृति।", rv(t, 0.2))
        a = rv(t, at(sc, "त्यो विदेशी")); lay = layer(); d = ImageDraw.Draw(lay)
        box(d, (L, 680, 440, 800), "विदेशी कम्पनी", AMBER, F("Bold", 36))
        put(img, lay, a)
        a = rv(t, at(sc, "उसले नेपाल")); lay = layer(); d = ImageDraw.Draw(lay)
        box(d, (560, 660, RX, 820), "", CYAN)
        T(d, (748, 712), "नेपालको इजाजतप्राप्त", F("Bold", 32), anchor="mm"); T(d, (748, 766), "कम्पनी वा बैंक", F("Bold", 32), anchor="mm")
        arrow(d, (445, 740), (553, 740), CYAN, ease((t - at(sc, "सम्झौता")) / 0.5), w=5)
        T(d, (500, 860), "सम्झौता", F("Bold", 30), fill=CYAN, anchor="mm")
        put(img, lay, a)
        b = rv(t, at(sc, "स्वीकृत"), 0.35)
        if b > 0:
            lay = layer(); d = ImageDraw.Draw(lay)
            d.rounded_rectangle((300, 920, 780, 1020), 50, outline=GREEN + (255,), width=4, fill=(20, 52, 38, 230))
            T(d, (520, 970), "राष्ट्र बैंक स्वीकृत", F("ExtraBold", 40), fill=GREEN, anchor="mm"); T(d, (720, 972), "✓", DJ, fill=GREEN, anchor="mm")
            put(img, lay, b, dy=(1 - eout(b)) * 20)
        a = rv(t, at(sc, "इजाजत पाएको") + 0.8); lay = layer(); d = ImageDraw.Draw(lay)
        panel(d, (L, 1080, RX, 1250), r=20, outline=LINE)
        T(d, (L + 30, 1100), "इजाजतप्राप्त: ४८", F("ExtraBold", 46), fill=AMBER)
        T(d, (L + 30, 1170), "१९ वाणिज्य बैंक · ६ विकास बैंक · २३ कम्पनी", F("Regular", 32), fill=WHITE)
        put(img, lay, a, dy=(1 - eout(a)) * 14)
        src(img, "राष्ट्र बैंक, रेमिट्यान्स विनियमावली २०७९ (दफा १२); FXMD सूची, असार मसान्त २०८३", rv(t, 1.0))

    elif sc == "c04":
        label(img, "चरण ०३ · प्रि-फन्डिङ", rv(t, 0.1), col=AMBER)
        a = rv(t, 0.3); lay = layer(); d = ImageDraw.Draw(lay)
        T(d, (L, 380), "प्रि-फन्डिङ।", F("ExtraBold", 120), fill=CYAN)
        d.rectangle((L, 540, L + tw("प्रि-फन्डिङ।", F("ExtraBold", 120)) * a, 548), fill=CYAN)
        T(d, (L, 572), "पैसा पहिले नै आइसकेको हुन्छ।", F("Regular", 38), fill=MUTED)
        put(img, lay, a)
        steps = [("पठाउनुअघि", "पहिले", "विदेशी मुद्रा नेपाल भित्रियो", "बैंकिङ प्रणालीबाट", AMBER),
                 ("रमेशले पठाउनु", "अनि", "रमेशले पैसा पठाए", "विदेशमा", WHITE),
                 ("त्यही अग्रिम", "त्यसपछि", "त्यही रकमबाट भुक्तानी", "नेपालको कम्पनीबाट", GREEN)]
        x0 = L + 30
        for i, (ph, when, s, sub, c) in enumerate(steps):
            a = rv(t, at(sc, ph) if i != 1 else at(sc, ph) + 0.4); lay = layer(); d = ImageDraw.Draw(lay); y = 690 + i * 190
            d.ellipse((x0 - 16, y + 34, x0 + 16, y + 66), fill=c + (255,))
            if i < 2: d.line((x0, y + 70, x0, y + 210), fill=LINE, width=4)
            T(d, (x0 + 50, y + 4), when, F("Bold", 28), fill=c)
            T(d, (x0 + 50, y + 42), s, F("Bold", 42))
            T(d, (x0 + 50, y + 100), sub, F("Regular", 30), fill=MUTED)
            put(img, lay, a, dy=(1 - eout(a)) * 14)
        a = rv(t, at(sc, "त्यही अग्रिम") + 1.0); lay = layer(); d = ImageDraw.Draw(lay)
        T(d, (L, 1290), "अग्रिम नआए: विदेशी बैंकको जमानत वा नगद धरौटी चाहिन्छ", F("Regular", 30), fill=MUTED)
        put(img, lay, a)
        src(img, "राष्ट्र बैंक, रेमिट्यान्स विनियमावली २०७९, दफा ९ (क)(ख)", rv(t, 1.0))

    elif sc == "c05":
        label(img, "चरण ०४ · सटही र भुक्तानी", rv(t, 0.1))
        head(img, "रियालबाट रुपैयाँ,", "अनि तीन बाटा।", rv(t, 0.2))
        a = rv(t, at(sc, "रियाललाई")); lay = layer(); d = ImageDraw.Draw(lay)
        box(d, (L, 680, 420, 790), "१,००० रियाल", AMBER, F("ExtraBold", 40))
        arrow(d, (430, 735), (540, 735), WHITE, ease((t - at(sc, "सटही")) / 0.5), w=5)
        box(d, (550, 680, RX, 790), "रुपैयाँ", GREEN, F("ExtraBold", 40), tcol=GREEN)
        T(d, (W / 2, 830), "त्यस दिनको सटही दरमा", F("Regular", 30), fill=MUTED, anchor="mm")
        put(img, lay, a)
        ways = [("बैंक खातामा", "बैंक खाता"), ("वालेटमा", "वालेट"), ("एजेन्टबाट", "एजेन्टबाट नगद")]
        for i, (ph, s) in enumerate(ways):
            a = rv(t, at(sc, ph)); lay = layer(); d = ImageDraw.Draw(lay); x = L + i * 300
            box(d, (x, 920, x + 272, 1070), s, CYAN, F("Bold", 34))
            T(d, (x + 136, 1110), f"बाटो {dev(i + 1)}", F("Regular", 28), fill=FAINT, anchor="mm")
            put(img, lay, a, dy=(1 - eout(a)) * 18)
        a = rv(t, at(sc, "एजेन्टबाट") + 0.8); lay = layer(); d = ImageDraw.Draw(lay)
        T(d, (L, 1200), "वालेट/भुक्तानी सेवामार्फत दिँदा नगदमा दिन मिल्दैन", F("Regular", 30), fill=MUTED)
        put(img, lay, a)
        src(img, "राष्ट्र बैंक, रेमिट्यान्स विनियमावली २०७९, दफा ९ (प), ३५", rv(t, 1.0))

    elif sc == "c06":
        label(img, "भ्रम", rv(t, 0.1), col=RED)
        head(img, "हुन्डी त सस्तो", "र छिटो छ नि?", rv(t, 0.2), c2=WHITE)
        a = rv(t, at(sc, "हुन्डीमा पैसा")); lay = layer(); d = ImageDraw.Draw(lay)
        panel(d, (L, 680, RX, 800), r=18, outline=GREEN)
        T(d, (L + 30, 740), "औपचारिक बाटो", F("Bold", 38), anchor="lm"); T(d, (RX - 30, 740), "बैंकिङ प्रणाली भएर", F("Bold", 34), fill=GREEN, anchor="rm")
        dashed_rect(d, (L, 830, RX, 950), (190, 80, 80, 255))
        T(d, (L + 30, 890), "हुन्डी", F("Bold", 38), anchor="lm"); T(d, (RX - 30, 890), "बैंकिङ प्रणालीबाहिर", F("Bold", 34), fill=RED, anchor="rm")
        put(img, lay, a)
        b = rv(t, at(sc, "दूतावास")); lay = layer(); d = ImageDraw.Draw(lay)
        d.rounded_rectangle((L, 1010, RX, 1180), 22, fill=(70, 26, 30, 240), outline=RED + (255,), width=3)
        T(d, (L + 30, 1035), "नेपाली दूतावासहरूको आग्रह", F("Regular", 30), fill=MUTED)
        T(d, (L + 30, 1085), "हुन्डीबाट पैसा नपठाउनुहोस्", F("ExtraBold", 48))
        put(img, lay, b, dy=(1 - eout(b)) * 18)
        src(img, "अनलाइनखबर, पुस १, २०८२ (दक्षिण कोरिया र यूएईस्थित दूतावास)", rv(t, at(sc, "दूतावास")))

    elif sc == "c07":
        label(img, "कति ठूलो?", rv(t, 0.1), col=AMBER)
        head(img, "एक वर्षमा,", "२३ खर्बभन्दा बढी।", rv(t, 0.2))
        E.stat_card(img, 680, "रु. २३.६३ खर्ब", "रेमिट्यान्स आप्रवाह", "आर्थिक वर्ष २०८२/८३", (t - at(sc, "तेइस खर्ब")) / 0.6, delta="+३७.१%")
        E.stat_card(img, 960, "$ १६.१९ अर्ब", "अमेरिकी डलरमा", "आर्थिक वर्ष २०८२/८३", (t - at(sc, "सैँतीस")) / 0.6, delta="+२८.१%")
        src(img, "नेपाल राष्ट्र बैंक, चालु आर्थिक तथा वित्तीय स्थिति (२०८२/८३ वार्षिक)", rv(t, 1.0))

    elif sc == "c08":
        label(img, "पूरा बाटो", rv(t, 0.1))
        head(img, "कतारबाट तिर्नुहोस्।", "गाउँमा पाउनुहोस्।", rv(t, 0.2))
        steps = [("रमेश: विदेशमा तिर्छन्", AMBER, "रमेशले विदेशमा"), ("विदेशी साझेदार: जानकारी दिन्छ", CYAN, "विदेशी साझेदारले"),
                 ("नेपालको इजाजतप्राप्त कम्पनी/बैंक", CYAN, "इजाजतप्राप्त कम्पनीलाई"), ("अग्रिम विदेशी मुद्रा: रुपैयाँमा", CYAN, "अग्रिम आएको"),
                 ("आमा: खाता · वालेट · नगद", GREEN, "आमाको खाता")]
        y0, hgt, gap = 640, 96, 34
        for i, (s, c, ph) in enumerate(steps):
            ts = at(sc, ph); a = rv(t, 0.4 + i * 0.15, 0.3)
            lay = layer(); d = ImageDraw.Draw(lay); y = y0 + i * (hgt + gap); on = t >= ts
            box(d, (L, y, 760, y + hgt), s, c if on else LINE, F("Bold", 32), tcol=WHITE if on else FAINT, align="lm")
            if i < len(steps) - 1: arrow(d, (L + 120, y + hgt + 2), (L + 120, y + hgt + gap - 2), (c if on else LINE), 1.0, w=4, head_=12)
            put(img, lay, a)
        ts = at(sc, "अग्रिम आएको"); p = ease((t - ts) / 0.8)
        if p > 0:
            lay = layer(); d = ImageDraw.Draw(lay); ya = y0 + hgt / 2; yb = y0 + 3 * (hgt + gap) + hgt / 2
            arrow(d, (760, ya), (850, ya), AMBER, min(1, p * 3), w=4, head_=1, dashed=True)
            if p > 0.33: arrow(d, (850, ya), (850, yb), AMBER, min(1, (p - 0.33) * 3), w=4, head_=1, dashed=True)
            if p > 0.66: arrow(d, (850, yb), (766, yb), AMBER, (p - 0.66) * 3, w=4, head_=14, dashed=True)
            T(d, (866, (ya + yb) / 2 - 30), "पहिले", F("Bold", 28), fill=AMBER); T(d, (866, (ya + yb) / 2 + 8), "नै", F("Bold", 28), fill=AMBER)
            img.alpha_composite(lay)
        src(img, "राष्ट्र बैंक, रेमिट्यान्स विनियमावली २०७९", rv(t, 1.0))

    elif sc == "c09":
        a = rv(t, 0.2); lay = layer(); d = ImageDraw.Draw(lay)
        T(d, (W / 2, 520), "पैसा पठाउँदा", F("ExtraBold", 72), anchor="mm")
        T(d, (W / 2, 620), "इजाजत पाएको बाटो।", F("ExtraBold", 72), fill=AMBER, anchor="mm")
        put(img, lay, a)
        a = rv(t, at(sc, "अर्को भागमा")); lay = layer(); d = ImageDraw.Draw(lay)
        panel(d, (L, 760, RX, 1010), r=24, outline=CYAN)
        T(d, (L + 36, 800), "//", M(700, 28), fill=CYAN); T(d, (L + 80, 798), "अर्को भाग", F("Bold", 30), fill=CYAN)
        T(d, (L + 36, 855), "राष्ट्र बैंकको ब्याजदर", F("ExtraBold", 50))
        T(d, (L + 36, 915), "तपाईंको किस्तासम्म कसरी?", F("ExtraBold", 50), fill=AMBER)
        put(img, lay, a, dy=(1 - eout(a)) * 18)
        f = rv(t, at(sc, "अर्को भागमा") + 1.4); lay = layer(); d = ImageDraw.Draw(lay)
        lay.alpha_composite(LOGO.resize((120, 120)), (L, 1090))
        T(d, (L + 150, 1100), "Ishaan Pranava", F("ExtraBold", 48))
        T(d, (L + 150, 1160), "विदेशमा रहेका आफन्तलाई सेयर गर्नुहोस्", F("Regular", 32), fill=MUTED)
        put(img, lay, f)
    else:  # disclaimer card
        lay = layer(); d = ImageDraw.Draw(lay)
        panel(d, (L, 760, RX, 1160), r=30, outline=LINE)
        for i, s in enumerate(("विचार व्यक्तिगत", "सार्वजनिक जानकारीमा आधारित", "लगानी सल्लाह होइन", "आवाज: एआई")):
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
        sh = Image.new("RGB", (360 * 5, 640 * 2))
        for i, im in enumerate(ims): sh.paste(im, ((i % 5) * 360, (i // 5) * 640))
        sh.save("stills/sheet.png")
    else:
        for s in sys.argv[1:]: X.render_scene(s)
