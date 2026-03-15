"""Learning engine: spaced repetition, lesson progression, dependency unlocking."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from .cards import Card, load_cards
from .audio import AudioPlayer

if TYPE_CHECKING:
    from .storage import Storage

# Minimum correct answers before a card is considered mastered.
MASTERY_THRESHOLD = 5

# Minimum score (0-1) to unlock dependent cards.
UNLOCK_SCORE = 0.8


class Engine:
    """Core learning engine."""

    def __init__(self, storage: Storage) -> None:
        self._storage = storage
        self._cards: dict[str, Card] = {c.id: c for c in load_cards()}
        self._audio = AudioPlayer()

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def available_languages(self) -> list[str]:
        """Return the unique language names present in the card deck."""
        return sorted({c.language for c in self._cards.values()})

    # ------------------------------------------------------------------
    # Lesson runners
    # ------------------------------------------------------------------

    def run_lesson(self, language: str, lesson_type: str) -> None:
        """Run a single lesson session."""
        candidates = self._get_candidates(language, lesson_type)
        if not candidates:
            print(f"No cards available for {language} / {lesson_type}.")
            return

        deck = self._build_deck(candidates)
        correct = 0
        total = len(deck)

        for card in deck:
            self._audio.play(card.id)
            prompt = f"[{card.type.upper()}] {card.front}  →  "
            answer = input(prompt).strip().lower()

            if answer == "quit":
                break

            if answer in card.accepted_answers:
                print("  ✓ Correct!")
                correct += 1
                self._storage.record_correct(card.id)
            else:
                print(f"  ✗  Answer: {card.answer}")
                self._storage.record_incorrect(card.id)

            self._maybe_unlock(card)

        print(f"\nLesson complete — {correct}/{total} correct.\n")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_candidates(self, language: str, lesson_type: str) -> list[Card]:
        """Return unlocked cards matching language and lesson type."""
        type_map = {
            "alphabet": "letter",
            "words": "word",
            "phrases": "phrase",
            "translate": None,  # all types
            "listen": None,
        }
        card_type = type_map.get(lesson_type)
        unlocked = self._storage.unlocked_cards()

        return [
            c for c in self._cards.values()
            if c.language == language
            and (card_type is None or c.type == card_type)
            and (not c.dependencies or all(d in unlocked for d in c.dependencies))
        ]

    def _build_deck(self, candidates: list[Card], size: int = 10) -> list[Card]:
        """Build a practice deck, weighting weak cards more heavily."""
        weak = [c for c in candidates if self._storage.correct_count(c.id) < MASTERY_THRESHOLD]
        pool = weak if weak else candidates
        return random.sample(pool, k=min(size, len(pool)))

    def _maybe_unlock(self, card: Card) -> None:
        """Unlock cards whose dependencies are now met."""
        score = self._storage.score(card.id)
        if score >= UNLOCK_SCORE:
            self._storage.unlock(card.id)
