"""Generate audio pronunciation files for all cards in data/cards.json.

Uses gTTS (Google Text-to-Speech) to create one MP3 per card, saved in
the audio/ directory.  Filenames match the card ID so the AudioPlayer in
src/language_trainer/audio.py can find them automatically.

Usage
-----
    python3 tools/generate_audio_pack.py [--slow]

Options
-------
    --slow    Generate audio at reduced speed (useful for learning mode).
              Defaults to normal speed.

Requirements
------------
    pip install gTTS
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Resolve project root regardless of where the script is called from.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_CARDS_PATH = _PROJECT_ROOT / "data" / "cards.json"
_AUDIO_DIR = _PROJECT_ROOT / "audio"

# Map language names to BCP-47 codes recognised by gTTS.
_LANG_CODES: dict[str, str] = {
    "arabic": "ar",
    "korean": "ko",
    "english": "en",
    "french": "fr",
    "spanish": "es",
}


def main() -> None:
    """Generate MP3 files for every card in cards.json."""
    parser = argparse.ArgumentParser(
        description="Generate gTTS audio files for Language Trainer cards."
    )
    parser.add_argument(
        "--slow",
        action="store_true",
        default=False,
        help="Generate audio at reduced speed (default: normal speed).",
    )
    args = parser.parse_args()

    try:
        from gtts import gTTS  # noqa: PLC0415
    except ImportError:
        print("gTTS is not installed.  Run:  pip install gTTS")
        sys.exit(1)

    if not _CARDS_PATH.exists():
        print(f"Card file not found: {_CARDS_PATH}")
        sys.exit(1)

    _AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    with _CARDS_PATH.open(encoding="utf-8") as fh:
        cards = json.load(fh)

    generated = 0
    skipped = 0

    for card in cards:
        card_id = card["id"]
        language = card["language"]
        text = card["front"]

        lang_code = _LANG_CODES.get(language)
        if lang_code is None:
            print(f"  [SKIP] Unknown language '{language}' for card '{card_id}'")
            skipped += 1
            continue

        output_path = _AUDIO_DIR / f"{card_id}.mp3"
        if output_path.exists():
            print(f"  [SKIP] Already exists: {output_path.name}")
            skipped += 1
            continue

        try:
            tts = gTTS(text=text, lang=lang_code, slow=args.slow)
            tts.save(str(output_path))
            print(f"  [OK]   {output_path.name}")
            generated += 1
        except Exception as exc:  # noqa: BLE001
            print(f"  [ERR]  {card_id}: {exc}")

    print(f"\nDone — {generated} generated, {skipped} skipped.")


if __name__ == "__main__":
    main()
