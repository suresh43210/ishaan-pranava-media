# mapvideo — Ishaan Pranava map-story video tools

Original code for Ishaan Pranava map explainer videos (vertical 1080×1920, 30 fps). Nothing here is copied from third-party video tools.

| File | Purpose |
| --- | --- |
| `engine.py` | Map drawing (Natural Earth borders, Nepal point-of-view), brand chrome, text, pins, arcs, cards |
| `examples/remittance-2082-83/story.py` | Full 3-minute story (12 scenes) — copy this for a new topic |
| `tts_gemini.py` | Nepali voiceover via Gemini API. With `tone.json` in the work folder each scene gets its own tone (documentary base `style_documentary.txt`); otherwise news-anchor style. Cut-off clips are retried automatically |
| `sound.py` | **Default since 2026-11-18.** Original procedural music (mood per scene), sound effects (hit on stressed words, danger warning, melody on positive moments, whoosh between scenes), ducking under the voice, −14 LUFS. No samples, no licences |
| `icons.py` | Flat-illustration icons (person, laptop, globe, card, phone, bank, arrows, tick/cross) for `"k": "ill"` panels |
| `examples/dollar-payments-2026-11/` | Full non-map story with illustrations, `tone.json`, `mood.json`, `sfx_events.json` — copy this for explainer topics |
| `mix_audio.py` | Trim speech, group sub-keys into scenes, `audio/durations.json`, `audio/voice.wav` (−14 LUFS), silent disclaimer scene |
| `assemble.sh` | Join scene files + voice into the final MP4 |
| `data/region.json` | Natural Earth 1:10m admin-0, Nepal POV (public domain); **NPL replaced with the official चुच्चे map** (incl. Kalapani, Lipulekh, Limpiyadhura) from the npm package nepali-geo-pro-max 1.0.0 (MIT); `ZZFILL` = borderless land filler |
| `data/nepal_provinces_chuche.geojson` | 7 provinces, same source — for province maps |
| `fonts/` | Mukta (SIL OFL 1.1) |

## Steps (work folder outside the repo)
1. Write `narration.json` — keys `c01`, `c02`, … (split a scene into `c04a`, `c04b`… to time map reveals).
2. Write `tone.json` (one tone per scene; preset names or a short sentence), `mood.json` (music mood per scene) and `sfx_events.json` (sound effects on exact narration words). Copy them from `examples/dollar-payments-2026-11/` and edit.
3. `python3 tools/mapvideo/tts_gemini.py --keyfile <ishaan-secrets>/gemini.env`
4. `python3 tools/mapvideo/mix_audio.py` — if the total is over 2:59, speed the raw clips (`ffmpeg -af atempo=1.1`, keep originals) and run it again
5. `python3 tools/mapvideo/sound.py` — must run after mix_audio.py and before assemble.sh (it writes the final `audio/voice.wav`)
6. Copy the example story script, edit scenes, check stills: `python3 story.py --still c04 16.5 s.png`
7. Render: `python3 story.py c01 c02 …` (split across 2 processes), then `bash tools/mapvideo/assemble.sh final.mp4`
8. Put the MP4 in `posts/<date>/`, push, and use the raw URL in Metricool.

## Sound rules (from Suresh's feedback, 2026-11-17)
- Music must be clearly audible on a phone speaker: ducked music about 16 LU under the voice (defaults `MUSIC_DB=-6`, `SFX_DB=-5`). Never bury it at −30 LU or lower.
- `hit` on every key number and stressed word; `danger` (low warning hit + two beeps) on risks, bans, failures; `soft_danger` for milder cautions; `melody` (bell motif) on hopeful or positive turns and the follow line.
- Mood per scene follows the story: story → question → facts → danger/tension → hope → view → cta.
- Tone changes stay moderate so the delivery stays credible.
- Claude cannot listen: check `audio/sfx_times.json` and loudness numbers, and give Suresh a table of where each sound lands.

## Layout rules
- Safe area for TikTok / Shorts / Reels: x 64–936, y 220–1560.
- Brand bar + progress at top; chapter chip + headline (≤2 lines, 70 px); visual; "तथ्य" strip with source and date on every slide that shows a figure.
- Colours: cobalt `#2340C9` subject, amber `#FFB547` story places and numbers, grey for paused/old values.
- Last scene: 1-second disclaimer card, no voice.

## Map notes
- Nepal outline follows the post-May-2020 official map (चुच्चे नक्सा). The package does not name its upstream source; spot-check against the Survey Department map before high-stakes use.
- Neighbours' faint borders are drawn under highlighted countries, so no foreign line crosses Nepal.
