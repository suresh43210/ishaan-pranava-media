# explainer — "भित्र के हुन्छ?" series template

Step-by-step process explainers (vertical 1080×1920, 30 fps), inspired in rhythm (not copied) by tech explainer shorts: one example carried through every step, `// चरण ०N` labels, one idea per slide, a "भ्रम" myth slide, and a final pipeline diagram.

- `explainer.py` — scenes for episode 1 (QR भुक्तानी). Copy into a work folder and edit `frame()` per episode. Uses `tools/mapvideo/engine.py` for brand chrome and background.
- Voice: `tools/mapvideo/tts_gemini.py --style tools/mapvideo/style_explainer.txt` (curious teacher style), then `atempo=1.12` on raw clips, then `mix_audio.py`.
- Sync: `at(scene, phrase)` places a reveal at the moment the phrase is spoken (character-proportional).
- Fonts: Mukta (Devanagari) + JetBrains Mono (Latin labels only; never Devanagari in mono). JetBrains Mono is SIL OFL 1.1.
- Avoid glyphs Mukta lacks (→ ✓): write words or use DejaVu for ✓.
