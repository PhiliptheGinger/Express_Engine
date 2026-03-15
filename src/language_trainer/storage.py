"""Persistence layer: read/write JSON progress, settings, and save state."""

from __future__ import annotations

import json
from pathlib import Path

_DEFAULT_SAVE_PATH = Path("language_trainer_v2_data.json")
_DEFAULT_SETTINGS_PATH = Path(__file__).resolve().parents[2] / "data" / "sample_settings.json"


class Storage:
    """Load and persist learner progress and app settings."""

    def __init__(
        self,
        save_path: Path | None = None,
        settings_path: Path | None = None,
    ) -> None:
        self._save_path = save_path or _DEFAULT_SAVE_PATH
        self._settings = self._load_settings(settings_path or _DEFAULT_SETTINGS_PATH)
        self._data = self._load()

    # ------------------------------------------------------------------
    # Card-level recording
    # ------------------------------------------------------------------

    def record_correct(self, card_id: str) -> None:
        """Increment the correct-answer counter for *card_id*."""
        entry = self._entry(card_id)
        entry["correct"] = entry.get("correct", 0) + 1
        entry["attempts"] = entry.get("attempts", 0) + 1

    def record_incorrect(self, card_id: str) -> None:
        """Increment the attempt counter (without correct) for *card_id*."""
        entry = self._entry(card_id)
        entry["attempts"] = entry.get("attempts", 0) + 1

    def correct_count(self, card_id: str) -> int:
        """Return the number of correct answers for *card_id*."""
        return self._entry(card_id).get("correct", 0)

    def score(self, card_id: str) -> float:
        """Return the ratio of correct answers to total attempts (0–1)."""
        entry = self._entry(card_id)
        attempts = entry.get("attempts", 0)
        if attempts == 0:
            return 0.0
        return entry.get("correct", 0) / attempts

    # ------------------------------------------------------------------
    # Unlocking
    # ------------------------------------------------------------------

    def unlock(self, card_id: str) -> None:
        """Mark *card_id* as unlocked."""
        self._data.setdefault("unlocked", [])
        if card_id not in self._data["unlocked"]:
            self._data["unlocked"].append(card_id)

    def unlocked_cards(self) -> set[str]:
        """Return the set of currently unlocked card IDs."""
        return set(self._data.get("unlocked", []))

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------

    def get_setting(self, key: str, default: object = None) -> object:
        """Return a setting value by *key*."""
        return self._settings.get(key, default)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self) -> None:
        """Write progress to disk."""
        with self._save_path.open("w", encoding="utf-8") as fh:
            json.dump(self._data, fh, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self) -> dict:
        if self._save_path.exists():
            with self._save_path.open(encoding="utf-8") as fh:
                return json.load(fh)
        return {}

    def _entry(self, card_id: str) -> dict:
        self._data.setdefault("cards", {})
        self._data["cards"].setdefault(card_id, {})
        return self._data["cards"][card_id]

    @staticmethod
    def _load_settings(path: Path) -> dict:
        if path.exists():
            with path.open(encoding="utf-8") as fh:
                return json.load(fh)
        return {}
