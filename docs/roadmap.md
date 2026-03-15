# Roadmap

This file tracks planned improvements for Language Trainer.

## Near-term

- [ ] **Better Android audio playback** — investigate alternatives to pygame that work reliably in PyDroid (e.g. `android.media.MediaPlayer` via Pyjnius, or pre-bundled `playsound`).
- [ ] **More vocabulary** — expand `data/cards.json` with common Arabic and Korean words and phrases.
- [ ] **Settings UI** — let the user toggle audio, change lesson size, and reset progress from within the app.

## Medium-term

- [ ] **Kivy UI** — implement `src/language_trainer/ui/kivy_app.py` so the app has a touch-friendly interface suitable for mobile devices.
- [ ] **More languages** — add French and Spanish card sets as proofs-of-concept for the multi-language architecture.
- [ ] **Smarter spaced repetition** — integrate a proper SM-2 / FSRS algorithm instead of the simple mastery-threshold approach.

## Long-term

- [ ] **Sync / cloud save** — allow progress to be backed up and restored across devices.
- [ ] **Audio recording** — let learners record their own pronunciation and compare it against the reference audio.
- [ ] **Community card packs** — support importing third-party `cards.json` files.
