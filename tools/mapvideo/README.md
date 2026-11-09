# mapvideo — Ishaan Pranava map-story video tools

Original code for Ishaan Pranava map explainer videos (vertical 1080×1920, 30 fps). Nothing here is copied from third-party video tools.

| File | Purpose |
| --- | --- |
| `engine.py` | Map drawing (Natural Earth borders, Nepal point-of-view), brand chrome, text, pins, arcs, cards |
| `examples/remittance-2082-83/story.py` | Full 3-minute story (12 scenes) — copy this for a new topic |
| `tts_gemini.py` | Nepali voiceover via Gemini API, news-anchor style (`style_news_anchor.txt`) |
| `mix_audio.py` | Trim speech, group sub-keys into scenes, `audio/durations.json`, `audio/voice.wav` (−14 LUFS), silent disclaimer scene |
| `assemble.sh` | Join scene files + voice into the final MP4 |
| `data/region.json` | Natural Earth 1:10m admin-0, Nepal POV, simplified (public domain) |
| `fonts/` | Mukta (SIL OFL 1.1) |

## Steps (work folder outside the repo)
1. Write `narration.json` — keys `c01`, `c02`, … (split a scene into `c04a`, `c04b`… to time map reveals).
2. `python3 tools/mapvideo/tts_gemini.py --keyfile <ishaan-secrets>/gemini.env`
3. `python3 tools/mapvideo/mix_audio.py`
4. Copy the example story script, edit scenes, check stills: `python3 story.py --still c04 16.5 s.png`
5. Render: `python3 story.py c01 c02 …` (split across 2 processes), then `bash tools/mapvideo/assemble.sh final.mp4`
6. Put the MP4 in `posts/<date>/`, push, and use the raw URL in Metricool.

## Layout rules
- Safe area for TikTok / Shorts / Reels: x 64–936, y 220–1560.
- Brand bar + progress at top; chapter chip + headline (≤2 lines, 70 px); visual; "तथ्य" strip with source and date on every slide that shows a figure.
- Colours: cobalt `#2340C9` subject, amber `#FFB547` story places and numbers, grey for paused/old values.
- Last scene: 1-second disclaimer card, no voice.

## Known limits
- `data/region.json` does **not** match Nepal's official 2020 map (Lipulekh, Kalapani, Limpiyadhura). Replace the NPL geometry with the Survey Department boundary when available.
