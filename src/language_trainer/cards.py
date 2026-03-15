"""Card definitions and JSON card-loading logic."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

# Default location of the card data file, relative to the project root.
_DEFAULT_CARDS_PATH = Path(__file__).resolve().parents[2] / "data" / "cards.json"


@dataclass
class Card:
    """A single flashcard."""

    id: str
    language: str
    type: str          # 'letter', 'word', 'phrase'
    front: str         # The character / word / phrase shown to the learner
    answer: str        # Canonical correct answer
    aliases: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    hint: str = ""

    @property
    def accepted_answers(self) -> list[str]:
        """Return all answers that should be marked correct (lowercase)."""
        return [self.answer.lower()] + [a.lower() for a in self.aliases]


def load_cards(path: Path | None = None) -> list[Card]:
    """Load cards from a JSON file.

    Parameters
    ----------
    path:
        Path to the JSON card file.  Defaults to ``data/cards.json`` in the
        project root.

    Returns
    -------
    list[Card]
        The parsed card objects.
    """
    cards_path = path or _DEFAULT_CARDS_PATH
    if not cards_path.exists():
        return []

    with cards_path.open(encoding="utf-8") as fh:
        raw = json.load(fh)

    return [
        Card(
            id=entry["id"],
            language=entry["language"],
            type=entry["type"],
            front=entry["front"],
            answer=entry["answer"],
            aliases=entry.get("aliases", []),
            dependencies=entry.get("dependencies", []),
            hint=entry.get("hint", ""),
        )
        for entry in raw
    ]
