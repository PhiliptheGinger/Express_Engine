"""Generate missing gTTS pronunciation files for the card deck."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_CARDS_PATH = _PROJECT_ROOT / "data" / "cards.json"
_AUDIO_DIR = _PROJECT_ROOT / "audio"
_LANG_CODES: dict[str, str] = {
	"arabic": "ar",
	"korean": "ko",
}



def main() -> None:
	"""Generate any missing card audio files into ./audio/."""
	parser = argparse.ArgumentParser(description="Generate missing gTTS audio files for Language Trainer cards.")
	parser.add_argument("--slow", action="store_true", help="Generate slower pronunciation audio.")
	args = parser.parse_args()

	try:
		from gtts import gTTS  # noqa: PLC0415
	except ImportError:
		print("gTTS is not installed. Run: pip install gTTS")
		sys.exit(1)

	if not _CARDS_PATH.exists():
		print(f"Card file not found: {_CARDS_PATH}")
		sys.exit(1)

	_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
	with _CARDS_PATH.open(encoding="utf-8") as handle:
		cards = json.load(handle)

	generated = 0
	skipped = 0
	for card in cards:
		card_id = card["id"]
		lang_code = _LANG_CODES.get(card["language"])
		if lang_code is None:
			print(f"[SKIP] Unsupported language for audio generation: {card_id}")
			skipped += 1
			continue

		output_path = _AUDIO_DIR / f"{card_id}.mp3"
		if output_path.exists():
			print(f"[SKIP] {output_path.name} already exists")
			skipped += 1
			continue

		try:
			gTTS(text=card["front"], lang=lang_code, slow=args.slow).save(str(output_path))
			print(f"[OK]   Generated {output_path.name}")
			generated += 1
		except Exception as exc:  # noqa: BLE001
			print(f"[ERR]  {card_id}: {exc}")

	print(f"Done. Generated={generated} Skipped={skipped}")


if __name__ == "__main__":
	main()
