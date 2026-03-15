# Language Trainer

A PyDroid-friendly language learning app focused on alphabet-first progression, spaced repetition, and audio-supported study for Arabic and Korean.

## Features

- Alphabet lessons
- Word lessons
- Phrase lessons
- Translation quiz
- Listening quiz
- Automatic pronunciation generation

## Current Status

- Working in PyDroid
- CLI-based
- Audio generation works
- Audio playback still being refined

## Project Structure

```
Express_Engine/
├─ README.md
├─ .gitignore
├─ requirements.txt
├─ pyproject.toml
├─ src/
│  └─ language_trainer/
│     ├─ __init__.py
│     ├─ app.py          # Main entry point
│     ├─ engine.py       # Learning logic & spaced repetition
│     ├─ cards.py        # Card definitions and loading
│     ├─ audio.py        # Audio playback & fallback
│     ├─ storage.py      # JSON progress & settings persistence
│     └─ ui/
│        └─ kivy_app.py  # Kivy UI (future)
├─ data/
│  ├─ cards.json         # Card data (Arabic, Korean, etc.)
│  └─ sample_settings.json
├─ tools/
│  └─ generate_audio_pack.py
├─ audio/                # Generated pronunciation MP3 files
└─ docs/
   └─ roadmap.md
```

## Setup

```bash
python3 -m pip install gTTS pygame
```

Or install from the requirements file:

```bash
pip install -r requirements.txt
```

## Run

```bash
python3 -m language_trainer
```

Or, from the project root:

```bash
python3 src/language_trainer/app.py
```

## Generate Audio

```bash
python3 tools/generate_audio_pack.py
```

This script reads `data/cards.json` and generates MP3 files in the `audio/` directory using gTTS.

## How Audio Works

Audio files are pre-generated with `generate_audio_pack.py` and stored in the `audio/` directory. During a lesson the app looks up the correct file by card ID and plays it with pygame. If a file is missing, the app falls back to a silent no-op so lessons can still run without audio.

## Roadmap

See [docs/roadmap.md](docs/roadmap.md) for planned improvements.
