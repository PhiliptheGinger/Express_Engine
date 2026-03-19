"""Card models and card-deck loading helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_DEFAULT_CARDS_PATH = Path(__file__).resolve().parents[2] / "data" / "cards.json"
_VALID_TYPES = {"letter", "word", "phrase"}


@dataclass(slots=True)
class Card:
	"""A single learning card.

	The data model intentionally carries both current SRS fields and future-facing
	concept metadata so the engine can stay reusable across CLI and later UIs.
	"""

	id: str
	language: str
	type: str
	front: str
	answer: str
	aliases: list[str] = field(default_factory=list)
	hint: str = ""
	dependencies: list[str] = field(default_factory=list)
	schema: str = "GENERAL"
	repetition: int = 0
	interval: int = 0
	ef: float = 2.5
	next_due: str | None = None
	last_reviewed: str | None = None
	times_studied: int = 0

	@property
	def accepted_answers(self) -> set[str]:
		"""Return the accepted answers for typed checks."""
		answers = {self.answer.casefold()}
		answers.update(alias.casefold() for alias in self.aliases)
		return answers

	@property
	def is_new(self) -> bool:
		"""Return whether the card has never been reviewed."""
		return self.repetition <= 0 and self.times_studied <= 0



def load_cards(path: Path | None = None) -> list[Card]:
	"""Load and validate cards from disk."""
	cards_path = path or _DEFAULT_CARDS_PATH
	if not cards_path.exists():
		return []

	with cards_path.open(encoding="utf-8") as handle:
		raw_cards = json.load(handle)

	cards: list[Card] = []
	for raw in raw_cards:
		_validate_raw_card(raw)
		cards.append(
			Card(
				id=raw["id"],
				language=raw["language"],
				type=raw["type"],
				front=raw["front"],
				answer=raw["answer"],
				aliases=list(raw.get("aliases", [])),
				hint=raw.get("hint", ""),
				dependencies=list(raw.get("dependencies", [])),
				schema=raw.get("schema", "GENERAL"),
				repetition=int(raw.get("repetition", 0)),
				interval=int(raw.get("interval", 0)),
				ef=float(raw.get("ef", 2.5)),
				next_due=raw.get("next_due"),
				last_reviewed=raw.get("last_reviewed"),
				times_studied=int(raw.get("times_studied", 0)),
			)
		)
	return cards



def _validate_raw_card(raw: dict[str, Any]) -> None:
	"""Validate the minimum required card fields."""
	required_fields = {
		"id",
		"language",
		"type",
		"front",
		"answer",
		"aliases",
		"hint",
		"dependencies",
		"schema",
	}
	missing = sorted(required_fields.difference(raw))
	if missing:
		raise ValueError(f"Card '{raw.get('id', '<unknown>')}' is missing fields: {', '.join(missing)}")

	card_type = raw["type"]
	if card_type not in _VALID_TYPES:
		raise ValueError(f"Card '{raw['id']}' has unsupported type '{card_type}'.")
