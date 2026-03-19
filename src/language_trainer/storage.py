"""Persistence helpers for learner progress and settings."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import date
from pathlib import Path
from typing import Any

_DEFAULT_SAVE_PATH = Path("language_trainer_progress.json")
_DEFAULT_SETTINGS_PATH = Path(__file__).resolve().parents[2] / "data" / "sample_settings.json"

_DEFAULT_PROGRESS: dict[str, Any] = {
	"cards": {},
	"settings": {},
}


class Storage:
	"""Load and save learner data independently from the UI."""

	def __init__(
		self,
		save_path: Path | None = None,
		settings_path: Path | None = None,
	) -> None:
		self._save_path = save_path or _DEFAULT_SAVE_PATH
		self._settings = self._load_json(settings_path or _DEFAULT_SETTINGS_PATH, default={})
		self._data = self._load_json(self._save_path, default=deepcopy(_DEFAULT_PROGRESS))
		self._data.setdefault("cards", {})
		self._data.setdefault("settings", {})

	def get_card_progress(self, card_id: str) -> dict[str, Any]:
		"""Return mutable progress for a single card."""
		cards = self._data.setdefault("cards", {})
		cards.setdefault(
			card_id,
			{
				"repetition": 0,
				"interval": 0,
				"ef": 2.5,
				"next_due": None,
				"last_reviewed": None,
				"times_studied": 0,
				"lapses": 0,
				"history": [],
			},
		)
		return cards[card_id]

	def get_setting(self, key: str, default: Any = None) -> Any:
		"""Return a setting with progress overrides applied on top of defaults."""
		if key in self._data.get("settings", {}):
			return self._data["settings"][key]
		return self._settings.get(key, default)

	def update_setting(self, key: str, value: Any) -> None:
		"""Persist a runtime setting override."""
		self._data.setdefault("settings", {})[key] = value

	def card_items(self) -> list[tuple[str, dict[str, Any]]]:
		"""Return all persisted card progress entries."""
		return list(self._data.get("cards", {}).items())

	def save(self) -> None:
		"""Write progress to disk as UTF-8 JSON."""
		with self._save_path.open("w", encoding="utf-8") as handle:
			json.dump(self._data, handle, ensure_ascii=False, indent=2)

	@staticmethod
	def today() -> date:
		"""Expose the scheduler date source for easy future substitution."""
		return date.today()

	@staticmethod
	def _load_json(path: Path, default: Any) -> Any:
		if path.exists():
			with path.open(encoding="utf-8") as handle:
				return json.load(handle)
		return default
