#!/usr/bin/env python3
"""Render Ishaan Pranava carousel slides from a slides.json file.

Usage:
    python3 tools/render.py posts/2026-11-07/slides.json

Writes JPEGs next to the JSON:
    ig-01.jpg ... (Instagram, 1080x1350, 4:5)
    tt-01.jpg ... (TikTok, 1080x1920, 9:16, TikTok safe zones respected)

Exits with status 2 and prints OVERFLOW lines if any slide's text does not fit;
shorten that slide's text and render again.

slides.json shape:
{
  "series": {"ig": "NRB Act Amendment · 2083", "tt": "राष्ट्र बैंक ऐन संशोधन"},
  "ig": [ <slide>, ... ],      # English, 6-8 slides
  "tt": [ <slide>, ... ]       # Nepali, 6-8 slides
}
Slide types (text in [[double brackets]] is shown in amber):
  {"type":"cover",     "title":"...", "sub":"..."}
  {"type":"bullets",   "kicker":"...", "title":"...", "items":[{"t":"...","d":"..."}]}      # 2-4 items
  {"type":"timeline",  "kicker":"...", "title":"...", "steps":[{"date":"...","text":"...","done":true}]}  # 2-4 steps
  {"type":"compare",   "kicker":"...", "title":"...", "cards":[{"label":"...","head":"...","body":"..."}, {...}]}  # exactly 2
  {"type":"stat",      "kicker":"...", "value":"NPR 1.2", "accent":"trillion+", "body":"...", "source":"..."}
  {"type":"questions", "kicker":"...", "title":"...", "items":["...","..."], "note":"..."}  # 2-3 items
  {"type":"view",      "label":"My view", "title":"...", "body":"..."}
  {"type":"sources",   "kicker":"...", "title":"...", "items":[{"name":"...","date":"..."}], "note":"..."}
"""
import asyncio, html, json, pathlib, re, sys

from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent
FONTS = ROOT / "fonts"

COBALT, COBALT_DK, AMBER = "#1B3FA6", "#132E7A", "#F2A93B"
INK, PAPER, MUTED, LINE = "#14203D", "#F6F4EF", "#5B6680", "#DCD8CE"
DARK_TYPES = {"cover", "stat", "view"}
NE_DIGITS = str.maketrans("0123456789", "०१२३४५६७८९")


def font_css():
    out = []
    for w in (400, 600, 700, 800):
        out.append(f"@font-face{{font-family:'Inter';font-weight:{w};src:url('file://{FONTS}/inter-latin-{w}-normal.woff2') format('woff2');}}")
        out.append(f"@font-face{{font-family:'Mukta';font-weight:{w};src:url('file://{FONTS}/mukta-devanagari-{w}-normal.woff2') format('woff2');unicode-range:U+0900-097F,U+1CD0-1CF9,U+200C-200D,U+20A8,U+20B9,U+25CC,U+A830-A839,U+A8E0-A8FF;}}")
        out.append(f"@font-face{{font-family:'Mukta';font-weight:{w};src:url('file://{FONTS}/mukta-latin-{w}-normal.woff2') format('woff2');}}")
    return "".join(out)


def t(s):
    """Escape text and turn [[x]] into amber highlight."""
    s = html.escape(str(s or ""))
    return re.sub(r"\[\[(.+?)\]\]", lambda m: f'<span style="color:{AMBER}">{m.group(1)}</span>', s)


LOGO = """<svg width="{s}" height="{s}" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<circle cx="50" cy="50" r="50" fill="{fill}"/>
<rect x="30" y="40" width="9" height="30" rx="2" fill="#fff"/><circle cx="34.5" cy="29" r="5.5" fill="#F2A93B"/>
<rect x="45" y="40" width="9" height="40" rx="2" fill="#fff"/>
<circle cx="60" cy="54" r="10.5" fill="none" stroke="#fff" stroke-width="8.5"/>
<circle cx="79" cy="72" r="4.5" fill="#F2A93B"/></svg>"""

# Format profiles. k scales type sizes; pad is (top, right, bottom, left).
FORMATS = {
    "ig": dict(w=1080, h=1350, pad=(96, 92, 96, 92), k=1.0, font="'Inter','Mukta',sans-serif", logo=64, nums=False),
    "tt": dict(w=1080, h=1920, pad=(170, 160, 430, 90), k=1.32, font="'Mukta','Inter',sans-serif", logo=72, nums=True),
}


def css(f):
    k = f["k"]; p = f["pad"]
    px = lambda v: f"{round(v * k)}px"
    return font_css() + f"""
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{f['w']}px;height:{f['h']}px}}
body{{font-family:{f['font']};-webkit-font-smoothing:antialiased}}
.slide{{width:{f['w']}px;height:{f['h']}px;overflow:hidden;padding:{p[0]}px {p[1]}px {p[2]}px {p[3]}px;display:flex;flex-direction:column}}
.light{{background:{PAPER};color:{INK}}} .dark{{background:{COBALT};color:#fff}}
.top{{display:flex;justify-content:space-between;font-size:{px(25)};font-weight:600;letter-spacing:.04em}}
.light .top{{color:{MUTED}}} .dark .top{{color:rgba(255,255,255,.75)}}
.body{{flex:1;min-height:0;display:flex;flex-direction:column;justify-content:center;overflow:hidden}}
.kicker{{font-size:{px(29)};font-weight:700;letter-spacing:.06em;color:{AMBER};margin-bottom:{px(22)}}}
h1{{font-weight:800;font-size:{px(86)};line-height:1.1;letter-spacing:-.015em}}
h2{{font-weight:800;font-size:{px(62)};line-height:1.15;letter-spacing:-.01em;margin-bottom:{px(48)}}}
.lead{{font-size:{px(38)};line-height:1.4;margin-top:{px(32)}}}
.dark .lead{{color:rgba(255,255,255,.88)}}
.muted{{color:{MUTED}}} .dark .muted{{color:rgba(255,255,255,.65)}}
.foot{{display:flex;justify-content:space-between;align-items:center;font-size:{px(23)};margin-top:{px(28)}}}
.brand{{display:flex;align-items:center;gap:18px;font-weight:700;font-size:{px(27)}}}
.rule{{width:120px;height:8px;background:{AMBER};border-radius:4px;margin-bottom:{px(40)}}}
.row{{display:flex;gap:{px(30)};padding:{px(30)} 0;border-top:2px solid {LINE}}}
.dot{{flex:none;width:{px(22)};height:{px(22)};border-radius:50%;background:{AMBER};margin-top:{px(16)}}}
.it{{font-size:{px(44)};font-weight:700;line-height:1.2}} .id{{font-size:{px(31)};margin-top:6px}}
.step{{position:relative;display:flex;gap:{px(40)};padding-bottom:{px(56)}}}
.sdot{{flex:none;width:{px(48)};height:{px(48)};border-radius:50%;border:{px(6)} solid {COBALT};position:relative;z-index:1}}
.sline{{position:absolute;left:{px(22)};top:{px(48)};bottom:0;width:{px(4)}}}
.sd{{font-size:{px(32)};font-weight:700}} .st{{font-size:{px(44)};font-weight:700;line-height:1.2;margin-top:4px}}
.card{{border-radius:28px;padding:{px(44)} {px(44)};margin-bottom:{px(28)}}}
.cl{{font-size:{px(27)};font-weight:700;letter-spacing:.06em;opacity:.75}}
.ch{{font-size:{px(52)};font-weight:800;line-height:1.12;margin-top:8px}} .cb{{font-size:{px(33)};line-height:1.38;margin-top:12px;opacity:.92}}
.big{{font-weight:800;font-size:{px(170)};line-height:1;letter-spacing:-.03em}}
.q{{display:flex;gap:{px(32)};align-items:flex-start;margin-bottom:{px(48)}}}
.qm{{flex:none;width:{px(84)};height:{px(84)};border-radius:50%;background:{AMBER};color:{INK};font-size:{px(52)};font-weight:800;display:flex;align-items:center;justify-content:center}}
.qt{{font-size:{px(44)};font-weight:700;line-height:1.24;padding-top:4px}}
.badge{{align-self:flex-start;background:{AMBER};color:{INK};font-size:{px(29)};font-weight:800;letter-spacing:.05em;padding:12px 24px;border-radius:12px;margin-bottom:{px(48)}}}
.src{{display:flex;justify-content:space-between;gap:20px;font-size:{px(36)};padding:{px(24)} 0;border-top:2px solid {LINE}}}
"""


def slide_html(s, fmt):
    ty = s["type"]
    if ty == "cover":
        return f'<div class="rule"></div><h1>{t(s["title"])}</h1>' + (f'<p class="lead">{t(s.get("sub"))}</p>' if s.get("sub") else "")
    if ty == "bullets":
        rows = "".join(f'<div class="row"><div class="dot"></div><div><div class="it">{t(i["t"])}</div>'
                       + (f'<div class="id muted">{t(i.get("d"))}</div>' if i.get("d") else "") + "</div></div>" for i in s["items"])
        return f'<div class="kicker">{t(s.get("kicker"))}</div><h2>{t(s["title"])}</h2>{rows}<div style="border-top:2px solid {LINE}"></div>'
    if ty == "timeline":
        steps = s["steps"]; out = ""
        for i, st in enumerate(steps):
            nxt = steps[i + 1] if i + 1 < len(steps) else None
            line = f'<div class="sline" style="background:{COBALT if nxt and nxt.get("done") else "#C9C4B8"}"></div>' if nxt else ""
            done = st.get("done")
            out += (f'<div class="step">{line}<div class="sdot" style="background:{COBALT if done else PAPER}"></div><div>'
                    f'<div class="sd" style="color:{COBALT if done else AMBER}">{t(st["date"])}</div><div class="st">{t(st["text"])}</div></div></div>')
        return f'<div class="kicker">{t(s.get("kicker"))}</div><h2>{t(s["title"])}</h2>{out}'
    if ty == "compare":
        styles = [(COBALT, "#fff"), ("#E7E3D9", INK)]
        cards = "".join(f'<div class="card" style="background:{bg};color:{fg}"><div class="cl">{t(c.get("label"))}</div>'
                        f'<div class="ch">{t(c["head"])}</div><div class="cb">{t(c.get("body"))}</div></div>'
                        for c, (bg, fg) in zip(s["cards"], styles))
        return f'<div class="kicker">{t(s.get("kicker"))}</div><h2>{t(s["title"])}</h2>{cards}'
    if ty == "stat":
        return (f'<div class="kicker">{t(s.get("kicker"))}</div><div class="big">{t(s["value"])}<br>'
                f'<span style="color:{AMBER}">{t(s.get("accent"))}</span></div><p class="lead">{t(s.get("body"))}</p>'
                + (f'<div class="muted" style="font-size:{round(25*FORMATS[fmt]["k"])}px;margin-top:32px">{t(s["source"])}</div>' if s.get("source") else ""))
    if ty == "questions":
        qs = "".join(f'<div class="q"><div class="qm">?</div><div class="qt">{t(q)}</div></div>' for q in s["items"])
        note = f'<div class="muted" style="font-size:{round(25*FORMATS[fmt]["k"])}px">{t(s["note"])}</div>' if s.get("note") else ""
        return f'<div class="kicker">{t(s.get("kicker"))}</div><h2>{t(s["title"])}</h2>{qs}{note}'
    if ty == "view":
        return (f'<div class="badge">{t(s.get("label", "My view"))}</div><h2 style="margin-bottom:0">{t(s["title"])}</h2>'
                f'<p class="lead">{t(s.get("body"))}</p>')
    if ty == "sources":
        rows = "".join(f'<div class="src"><span style="font-weight:700">{t(i["name"])}</span><span class="muted">{t(i.get("date"))}</span></div>' for i in s["items"])
        note = f'<p class="muted" style="font-size:{round(30*FORMATS[fmt]["k"])}px;line-height:1.4;margin-top:40px">{t(s["note"])}</p>' if s.get("note") else ""
        return f'<div class="kicker">{t(s.get("kicker"))}</div><h2>{t(s["title"])}</h2>{rows}<div style="border-top:2px solid {LINE}"></div>{note}'
    raise ValueError(f"unknown slide type: {ty}")


def page(s, idx, total, fmt, series):
    f = FORMATS[fmt]
    cls = "dark" if s["type"] in DARK_TYPES else "light"
    counter = f"{idx:02d} / {total:02d}" if not f["nums"] else f"{idx} / {total}".translate(NE_DIGITS)
    swipe = "" if fmt == "tt" else ("Follow for more" if idx == total else "Swipe →")
    logo = LOGO.replace("{s}", str(f["logo"])).replace("{fill}", COBALT_DK if cls == "dark" else COBALT)
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{css(f)}</style></head><body>'
            f'<div class="slide {cls}"><div class="top"><span>{t(series)}</span><span>{counter}</span></div>'
            f'<div class="body">{slide_html(s, fmt)}</div>'
            f'<div class="foot"><div class="brand">{logo}<span>Ishaan Pranava</span></div><span style="font-weight:600">{swipe}</span></div>'
            f'</div></body></html>')


async def main(spec_path):
    spec_path = pathlib.Path(spec_path).resolve()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    out_dir = spec_path.parent
    overflow = []
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(args=["--allow-file-access-from-files"])
        except Exception:
            browser = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--allow-file-access-from-files"])
        for fmt in ("ig", "tt"):
            slides = spec.get(fmt) or []
            if not slides:
                continue
            f = FORMATS[fmt]
            pg = await browser.new_page(viewport={"width": f["w"], "height": f["h"]})
            for i, s in enumerate(slides, 1):
                tmp = out_dir / f".{fmt}-{i:02d}.html"
                tmp.write_text(page(s, i, len(slides), fmt, spec.get("series", {}).get(fmt, "")), encoding="utf-8")
                await pg.goto(f"file://{tmp}")
                await pg.evaluate("document.fonts.ready")
                await pg.wait_for_timeout(150)
                over = await pg.evaluate("(() => {const b=document.querySelector('.body'); return b.scrollHeight - b.clientHeight;})()")
                if over > 2:
                    overflow.append(f"OVERFLOW {fmt}-{i:02d}: text is {over}px too tall; shorten it")
                await pg.screenshot(path=str(out_dir / f"{fmt}-{i:02d}.jpg"), type="jpeg", quality=90)
                tmp.unlink()
            await pg.close()
        await browser.close()
    for line in overflow:
        print(line)
    print(f"rendered into {out_dir}")
    return 2 if overflow else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__); sys.exit(1)
    sys.exit(asyncio.run(main(sys.argv[1])))
