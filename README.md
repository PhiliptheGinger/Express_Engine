# Language Trainer

A PyDroid-friendly language learning app focused on **teaching progression**, not one-off translation. The project now centers on a reusable learning engine with dependency-based unlocking, conceptual schema tags, transparent spaced repetition, and a CLI that is ready to be replaced by a future Kivy UI.

## Learning model

The trainer is built around these ideas:

- **Alphabet first**: letters unlock before words.
- **Dependency-based progression**: words appear only after prerequisite letters are mastered, and phrases appear only after their prerequisite words are mastered.
- **Structured meaning**: cards carry conceptual schema tags such as `SCRIPT`, `LIFE`, `PATH`, `STUDY`, and `SUCCESS`.
- **Transparent SRS**: every rated review shows the next due date, interval, ease factor, and repetition count.
- **Reusable engine**: storage, audio, and learning logic are separated from the interface layer.

## Project structure

```text
Express_Engine/
├─ README.md
├─ pyproject.toml
├─ requirements.txt
├─ data/
│  ├─ cards.json
│  └─ sample_settings.json
├─ tools/
│  └─ generate_audio_pack.py
├─ src/
│  └─ language_trainer/
│     ├─ __init__.py
│     ├─ __main__.py
│     ├─ app.py
│     ├─ audio.py
│     ├─ cards.py
│     ├─ engine.py
│     ├─ storage.py
│     └─ ui/
│        └─ kivy_app.py
└─ docs/
   └─ roadmap.md
```

## Starter content

The seed deck includes:

- Arabic letters: alif, ba, ta, ha, ya, ra, qaf, mim, dal, seen
- Arabic words: life, path, study, success, water
- Arabic phrase: life path
- Korean letters: giyeok, nieun, rieul, ieung, a, i
- Korean words: life, path, study, success
- Korean phrase: life path

Each card includes metadata for:

- `id`
- `language`
- `type`
- `front`
- `answer`
- `aliases`
- `hint`
- `dependencies`
- `schema`
- `repetition`
- `interval`
- `ef`
- `next_due`
- `last_reviewed`
- `times_studied`

## Installation

```bash
pip install -r requirements.txt
```

## Running the CLI

From the repository root:

```bash
PYTHONPATH=src python -m language_trainer
```

The CLI supports:

1. Study alphabet lesson
2. Review alphabet
3. Study new words
4. Review words
5. Study new phrases
6. Review phrases
7. Translation quiz
8. Listening quiz
9. Stats
10. Settings

## Progress storage

Learner progress is stored in `language_trainer_progress.json` in the working directory. Settings defaults live in `data/sample_settings.json`, and runtime changes are stored in the progress file so the engine and future UI can share the same preferences.

## Audio generation

Use the helper script to generate missing MP3 files for Arabic and Korean:

```bash
python tools/generate_audio_pack.py
```

Add `--slow` for slower pronunciation.

Audio files are expected at paths like:

- `audio/arabic_letter_alif.mp3`
- `audio/arabic_word_hayat.mp3`
- `audio/korean_letter_giyeok.mp3`

Playback is abstracted behind `src/language_trainer/audio.py` so the learning engine does not depend on a specific backend.

## Kivy path

A minimal Kivy bridge exists in `src/language_trainer/ui/kivy_app.py`. The next UI step is to bind the existing engine to:

- language selection
- mode menu
- card screen
- reveal answer button
- rating buttons
- optional audio button

## Notes for PyDroid

- Terminal mode is the primary supported experience right now.
- Audio generation is supported separately from lesson flow.
- Audio playback is optional because device-level playback reliability varies.
- The engine is intentionally UI-agnostic so a touch-first Kivy front end can be added next.
