import sys, os
sys.path.insert(0, "/home/claude/ishaan-pranava-media/tools/mapvideo")
from PIL import Image, ImageDraw
from engine import F, COBALT, COBALT_L, AMBER, WHITE, MUTED, FAINT, OCEAN_T, OCEAN_B, LOGO, dev
import numpy as np
W, H = 1080, 1350
RED = (235, 90, 80); GREY = (112, 118, 134); DARK = (22, 24, 29)
OUT = "/home/claude/work/w1/img"; os.makedirs(OUT, exist_ok=True)

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

# ---------- IG carousel 1 (EN) — 12 Nov ----------
S1 = "Nepal Police Cyber Bureau via eAarthik (1 Nov 2026), Banking Samachar, Annapurna Post; Kantipur (6 Nov 2026)"
card("ig1_1", "CYBER FRAUD · NEPAL", "Lose Rs 10 to online fraud in Nepal, get back about Rs 1", big="10–12%", body="is roughly how much stolen money police say is recovered. Why so little? Swipe.", src="Nepal Police Cyber Bureau spokesperson, quoted by eAarthik (1 Nov 2026)", page="1/6")
card("ig1_2", "MINUTES, NOT DAYS", "The money moves before you notice", big="5–10 min", body="Stolen funds are split across 4–5 accounts at different banks within 5 to 10 minutes.\n\nMost of it is then withdrawn as cash from ATMs in border areas.", src="Nepal Police Cyber Bureau spokesperson, quoted by eAarthik (1 Nov 2026)", page="2/6")
card("ig1_3", "THE SCALE", "Cyber-crime complaints, FY 2025/26", big="20,526", body="More than 7,000 of them involved financial fraud. Facebook/Messenger (7,123) and TikTok (6,776) led the list.", src="Nepal Police Cyber Bureau data via Banking Samachar and Annapurna Post (Sept 2026)", page="3/6")
card("ig1_4", "COMMON TRICKS", "Three patterns behind most cases", body="1. A call ‘from your bank or wallet’ asking for your OTP.\n\n2. A prize, gift or lottery that needs a fee first.\n\n3. A fake job abroad or a paid ‘online task’.", src="Nepal Police Cyber Bureau via Banking Samachar, Annapurna Post", page="4/6")
card("ig1_5", "NEW SINCE 6 NOV 2026", "Hotline 1247: one roof, one hour", big="1247", body="Police, Nepal Rastra Bank, banks, wallets and telecoms now sit together 24/7. Target: freeze the money within 10–60 minutes.", src="Kantipur (6 Nov 2026); Onlinekhabar (9 Nov 2026)", page="5/6")
card("ig1_6", "IF IT HAPPENS TO YOU", "Call 1247 at once. Never share your OTP.", body="Speed is everything: the first hour decides whether money can be frozen.\n\nSave this post and share it with your family.", footer="Follow @ishaan.pranava", src="Views personal; based on public information. Not legal advice.", page="6/6")

# ---------- IG carousel 2 (EN) — 16 Nov ----------
S2 = "Nepal Rastra Bank, Current Macroeconomic and Financial Situation (two months of FY 2026/27), Oct 2026"
card("ig2_1", "NEPAL · SAVINGS", "Your deposit earns 3.11%. Prices rise 6.34%.", big="−3.2 pts", bigcol=RED, body="That is the gap between the average deposit rate and inflation, mid-September 2026.", src=S2 + "; gap = simple calculation", page="1/5")
card("ig2_2", "ONE YEAR APART", "The picture flipped", rows=[("Deposit rate", "a year ago: 3.96%", "3.11%", COBALT_L), ("Inflation", "a year ago: 1.87%", "6.34%", RED)], src=S2 + " (commercial banks, weighted average)", page="2/5")
card("ig2_3", "BORROWERS GAIN", "Loans got cheaper", rows=[("Average lending rate", "a year ago: 7.66%", "6.38%", AMBER), ("Average base rate", "a year ago: 5.72%", "4.70%", AMBER)], src=S2, page="3/5")
card("ig2_4", "WHY RATES FELL", "Too much money, too little borrowing", rows=[("Deposits, y/y", "mid-Sept 2026", "+14.4%", COBALT_L), ("Private credit, y/y", "mid-Sept 2026", "+7.3%", AMBER)], body="NRB was holding about Rs 1.37 trillion of absorbed liquidity in mid-September.", src=S2, page="4/5")
card("ig2_5", "FOR Rs 100,000 SAVED", "About Rs 3,200 of buying power lost in a year", body="Simple calculation: 3.11% interest minus 6.34% inflation. Actual results vary by bank, tax and product.\n\nThis is not investment advice.", footer="Follow @ishaan.pranava", src=S2 + "; calculation by Ishaan Pranava", page="5/5")

# ---------- LinkedIn chart (EN) — 13 Nov ----------
card("li_chart", "NEPAL · CYBER CRIME", "Cyber-crime complaints to Nepal Police, by fiscal year", bars=[("2018/19", 357, "357"), ("2019/20", 2301, "2,301"), ("2020/21", 3906, "3,906"), ("2021/22", 4686, "4,686"), ("2022/23", 9013, "9,013"), ("2023/24", 19730, "19,730"), ("2024/25", 18926, "18,926"), ("2025/26", 20526, "20,526")], body="About two-thirds of 2025/26 complaints came from people aged 18–35.", src="Nepal Police Cyber Bureau data via Annapurna Post (Sept 2026). Nepali FY 2075/76–2082/83 shown in AD terms.")

# ---------- FB fact card (NP) — 15 Nov ----------
SN = "नेपाल राष्ट्र बैंक, चालु आर्थिक तथा वित्तीय स्थिति (२०८३/८४ का दुई महिना), वाणिज्य बैंकको भारित औसत"
card("fb_card1", "भदौ मसान्त २०८३", "निक्षेपको ब्याजदर ३.११%, महँगी ६.३४%", rows=[("निक्षेपको औसत ब्याजदर", "एक वर्षअघि: ३.९६%", "३.११%", COBALT_L), ("महँगी (मुद्रास्फीति)", "एक वर्षअघि: १.८७%", "६.३४%", RED), ("कर्जाको औसत ब्याजदर", "एक वर्षअघि: ७.६६%", "६.३८%", AMBER), ("औसत आधार दर", "एक वर्षअघि: ५.७२%", "४.७०%", AMBER)], src=SN, nep=True, footer="बचतकर्ताको वास्तविक प्रतिफल ऋणात्मक")

# ---------- FB photo carousel (NP) — 18 Nov ----------
SC = "नेपाल प्रहरी साइबर ब्युरोको तथ्याङ्क — अन्नपूर्ण पोस्ट (असोज २०८३), बैंकिङ समाचार"
card("fb_cyb_1", "साइबर अपराध", "साइबर अपराधका उजुरी: ३५७ बाट २०,५२६", bars=[("२०७५/७६", 357, "३५७"), ("२०७६/७७", 2301, "२,३०१"), ("२०७७/७८", 3906, "३,९०६"), ("२०७८/७९", 4686, "४,६८६"), ("२०७९/८०", 9013, "९,०१३"), ("२०८०/८१", 19730, "१९,७३०"), ("२०८१/८२", 18926, "१८,९२६"), ("२०८२/८३", 20526, "२०,५२६")], src=SC, nep=True, page="१/३")
card("fb_cyb_2", "आ.व. २०८२/८३", "उजुरी कहाँबाट आए?", bars=[("फेसबुक", 7123, "७,१२३"), ("टिकटक", 6776, "६,७७६"), ("ह्वाट्सएप", 3105, "३,१०५"), ("टेलिग्राम", 1031, "१,०३१"), ("बैंक/एसएमएस", 744, "७४४")], body="उजुरी गर्नेमध्ये झन्डै दुई तिहाइ १८ देखि ३५ वर्ष उमेरका छन्।", src=SC, nep=True, page="२/३")
card("fb_cyb_3", "ठगीमा पर्नुभयो?", "तुरुन्तै हटलाइन १२४७ मा फोन गर्नुहोस्", big="१२४७", body="प्रहरी, राष्ट्र बैंक, बैंक, वालेट र टेलिकम एउटै केन्द्रमा चौबीसै घण्टा। लक्ष्य: १० देखि ६० मिनेटभित्र रकम रोक्का।\n\nओटीपी कसैलाई नदिनुहोस्।", src="कान्तिपुर (कात्तिक २०, २०८३); अनलाइनखबर (कात्तिक २३, २०८३)", nep=True, page="३/३")

# ---------- LinkedIn PDF (EN) — 18 Nov ----------
SM = "eAarthik (1 Nov 2026) quoting Nepal Police Cyber Bureau and NRB spokespersons; Kantipur (6 Nov 2026)"
card("li_pdf_1", "FOR BANKERS", "Mule accounts: what Nepali banks must tighten", body="How scam money moves through Nepal's banking system, and where it can be stopped.", page="1/7", src="Views personal; based on public information.")
card("li_pdf_2", "THE ROUTE", "Minutes from victim to cash", body="Within 5–10 minutes, stolen funds are split across 4–5 accounts at different banks.\n\nMost are withdrawn as cash at ATMs in border areas. Some may move via hundi or crypto (police suspicion).", src=SM, page="2/7")
card("li_pdf_3", "THE MULES", "Who holds the receiving accounts?", body="NRB's spokesperson: dormant accounts and accounts with outdated KYC are commonly used.\n\nPolice report people lending their citizenship documents to open many accounts for a fee.", src=SM, page="3/7")
card("li_pdf_4", "THE COST", "Recovery stays low", big="10–12%", body="Share of online-fraud money police say is recovered. FY 2025/26: 20,526 cyber-crime complaints; 7,000+ involved financial fraud.", src="eAarthik (1 Nov 2026); Banking Samachar; Annapurna Post", page="4/7")
card("li_pdf_5", "THE NEW TOOL", "Hotline 1247 since 6 Nov 2026", body="Police, NRB, banks, payment providers, telecoms and ISPs under one roof, 24/7.\n\nTarget: register a complaint in 10 minutes; freeze accounts, wallets and SIMs in 10–60 minutes.", src="Kantipur (6 Nov 2026); Onlinekhabar (9 Nov 2026)", page="5/7")
card("li_pdf_6", "MY VIEW", "Four controls worth tightening", body="1. Extra checks when a dormant account is reactivated.\n\n2. Prioritised KYC refresh for long-inactive customers.\n\n3. Velocity alerts on rapid inbound-then-outbound transfers.\n\n4. A tested freeze drill with the 1247 centre.", src="Opinion of the author; not the policy of any institution.", page="6/7")
card("li_pdf_7", "THE TAKEAWAY", "The first hour decides recovery", body="Faster freezes need clean accounts upstream. KYC hygiene is now a fraud-prevention tool, not just compliance.", footer="Follow Ishaan Pranava", src="Views personal; based on public information.", page="7/7")
print("ok")
