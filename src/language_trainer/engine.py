"""Reusable learning engine for lessons, unlocking, schemas, and SRS."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING, Iterable

from .audio import AudioPlayer
from .cards import Card, load_cards

if TYPE_CHECKING:
	from .storage import Storage


@dataclass(slots=True)
class ReviewResult:
	"""Outcome of scheduling a reviewed card."""

	card: Card
	rating: int
	was_correct: bool
	repetition: int
	interval: int
	ef: float
	next_due: str
	last_reviewed: str


class Engine:
	"""Core teaching logic, independent from any UI."""

	def __init__(self, storage: Storage) -> None:
		self._storage = storage
		self._cards: dict[str, Card] = {card.id: card for card in load_cards()}
		self._audio = AudioPlayer(enabled=bool(self._storage.get_setting("audio_enabled", True)))

	def available_languages(self) -> list[str]:
		return sorted({card.language for card in self._cards.values()})

	def available_modes(self) -> list[str]:
		return [
			"study alphabet",
			"review alphabet",
			"study words",
			"review words",
			"study phrases",
			"review phrases",
			"translation quiz",
			"listening quiz",
			"stats",
			"settings",
		]

	def get_card(self, card_id: str) -> Card:
		return self._cards[card_id]

	def get_new_cards(self, language: str, card_type: str, limit: int | None = None) -> list[Card]:
		"""Return unlocked cards that have not yet been studied."""
		limit = limit or int(self._storage.get_setting("new_batch_size", 3))
		cards = [
			card for card in self._cards.values()
			if card.language == language
			and card.type == card_type
			and self._dependencies_mastered(card)
			and self._progress(card.id)["times_studied"] == 0
		]
		return cards[:limit]

	def get_due_cards(self, language: str, card_type: str | None = None, limit: int | None = None) -> list[Card]:
		"""Return due cards for review or mixed quiz modes."""
		limit = limit or int(self._storage.get_setting("review_batch_size", 10))
		today = self._storage.today()
		due_cards = []
		for card in self._cards.values():
			if card.language != language:
				continue
			if card_type is not None and card.type != card_type:
				continue
			if not self._dependencies_mastered(card):
				continue
			progress = self._progress(card.id)
			next_due = progress.get("next_due")
			if progress["times_studied"] <= 0:
				continue
			if next_due is None or next_due <= today.isoformat():
				due_cards.append(card)
		due_cards.sort(key=lambda item: (self._progress(item.id).get("next_due") or "", item.id))
		return due_cards[:limit]

	def describe_card(self, card: Card) -> dict[str, object]:
		"""Return a UI-friendly snapshot of card metadata and progress."""
		progress = self._progress(card.id)
		return {
			"id": card.id,
			"language": card.language,
			"type": card.type,
			"front": card.front,
			"answer": card.answer,
			"aliases": list(card.aliases),
			"hint": card.hint,
			"schema": card.schema,
			"dependencies": list(card.dependencies),
			"mastered": self.is_mastered(card.id),
			"progress": dict(progress),
		}

	def reveal_batch(self, cards: Iterable[Card]) -> list[dict[str, object]]:
		"""Return study material for a small batch of new items."""
		return [self.describe_card(card) for card in cards]

	def check_answer(self, card: Card, guess: str) -> bool:
		"""Return whether a typed learner response should count as correct."""
		return guess.strip().casefold() in card.accepted_answers

	def play_audio(self, card_id: str) -> bool:
		"""Ask the current audio backend to play a card's pronunciation."""
		return self._audio.play(card_id)

	def review_card(self, card: Card, rating: int, was_correct: bool) -> ReviewResult:
		"""Apply a simplified SM-2 update and persist it."""
		if rating < 1 or rating > 5:
			raise ValueError("Rating must be between 1 and 5.")

		progress = self._progress(card.id)
		today = self._storage.today()
		progress["times_studied"] += 1
		progress["last_reviewed"] = today.isoformat()
		progress.setdefault("history", []).append({
			"date": today.isoformat(),
			"rating": rating,
			"correct": was_correct,
		})

		ef = float(progress.get("ef", 2.5))
		repetition = int(progress.get("repetition", 0))
		interval = int(progress.get("interval", 0))

		if rating < 3:
			repetition = 0
			interval = 1 if rating == 2 else 0
			progress["lapses"] = int(progress.get("lapses", 0)) + 1
		else:
			repetition += 1
			if repetition == 1:
				interval = 1
			elif repetition == 2:
				interval = 3
			else:
				interval = max(1, round(interval * ef))

		ef = max(1.3, ef + (0.1 - (5 - rating) * (0.08 + (5 - rating) * 0.02)))
		next_due = today + timedelta(days=interval)

		progress["repetition"] = repetition
		progress["interval"] = interval
		progress["ef"] = round(ef, 2)
		progress["next_due"] = next_due.isoformat()

		return ReviewResult(
			card=card,
			rating=rating,
			was_correct=was_correct,
			repetition=repetition,
			interval=interval,
			ef=round(ef, 2),
			next_due=next_due.isoformat(),
			last_reviewed=today.isoformat(),
		)

	def is_mastered(self, card_id: str) -> bool:
		"""A card is mastered once its repetition meets the configured threshold."""
		threshold = int(self._storage.get_setting("mastery_repetition_threshold", 3))
		return int(self._progress(card_id).get("repetition", 0)) >= threshold

	def related_cards(self, card: Card) -> list[Card]:
		"""Return cards in the same conceptual schema family."""
		return [
			other for other in self._cards.values()
			if other.id != card.id and other.schema == card.schema and other.language == card.language
		]

	def language_stats(self, language: str) -> dict[str, object]:
		"""Aggregate stats for transparent learner feedback."""
		cards = [card for card in self._cards.values() if card.language == language]
		by_type: dict[str, dict[str, int]] = {}
		mastered = 0
		studied = 0
		for card in cards:
			progress = self._progress(card.id)
			card_bucket = by_type.setdefault(card.type, {"total": 0, "studied": 0, "mastered": 0, "available_new": 0, "due": 0})
			card_bucket["total"] += 1
			if self._dependencies_mastered(card):
				card_bucket["available_new"] += 1
			if progress["times_studied"] > 0:
				studied += 1
				card_bucket["studied"] += 1
			if self.is_mastered(card.id):
				mastered += 1
				card_bucket["mastered"] += 1
			if progress["times_studied"] > 0 and (progress.get("next_due") is None or progress["next_due"] <= self._storage.today().isoformat()):
				card_bucket["due"] += 1

		return {
			"language": language,
			"total_cards": len(cards),
			"studied_cards": studied,
			"mastered_cards": mastered,
			"by_type": by_type,
		}

	def _progress(self, card_id: str) -> dict[str, object]:
		return self._storage.get_card_progress(card_id)

	def _dependencies_mastered(self, card: Card) -> bool:
		if not card.dependencies:
			return True
		return all(self.is_mastered(dep_id) for dep_id in card.dependencies)
