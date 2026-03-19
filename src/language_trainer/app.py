"""Simple CLI for the modular language trainer engine."""

from __future__ import annotations

from .engine import Engine
from .storage import Storage

_MODE_SHORTCUTS = {
	"1": "study alphabet",
	"2": "review alphabet",
	"3": "study words",
	"4": "review words",
	"5": "study phrases",
	"6": "review phrases",
	"7": "translation quiz",
	"8": "listening quiz",
	"9": "stats",
	"10": "settings",
}

_TYPE_MAP = {
	"alphabet": "letter",
	"words": "word",
	"phrases": "phrase",
}


class TrainerCLI:
	"""Terminal interface layered on top of the reusable engine."""

	def __init__(self) -> None:
		self.storage = Storage()
		self.engine = Engine(self.storage)

	def run(self) -> None:
		"""Main CLI loop."""
		print("Language Trainer")
		print("Alphabet first. Words unlock after letter mastery. Phrases unlock after word mastery.")
		print("Type 'quit' at any prompt to exit.\n")

		while True:
			language = self._choose_language()
			if language is None:
				break

			while True:
				mode = self._choose_mode(language)
				if mode is None:
					self.storage.save()
					print("Progress saved.")
					return
				if mode == "back":
					break
				if mode == "settings":
					self._settings_menu()
				elif mode == "stats":
					self._show_stats(language)
				else:
					self._run_learning_mode(language, mode)
				self.storage.save()

		self.storage.save()
		print("Goodbye! Progress saved.")

	def _choose_language(self) -> str | None:
		languages = self.engine.available_languages()
		default = self.storage.get_setting("default_language", languages[0] if languages else "arabic")
		print("Available languages:", ", ".join(languages))
		response = input(f"Choose a language [{default}]: ").strip().lower()
		if response == "quit":
			return None
		if not response:
			response = str(default)
		if response not in languages:
			print(f"Unknown language '{response}'.\n")
			return self._choose_language()
		return response

	def _choose_mode(self, language: str) -> str | None:
		print(f"\nMode menu for {language}:")
		for shortcut, mode in _MODE_SHORTCUTS.items():
			print(f"  {shortcut}. {mode}")
		print("  b. back to language selection")
		response = input("Choose a mode: ").strip().lower()
		if response == "quit":
			return None
		if response == "b":
			return "back"
		return _MODE_SHORTCUTS.get(response, response)

	def _run_learning_mode(self, language: str, mode: str) -> None:
		if mode.startswith("study "):
			label = mode.replace("study ", "")
			card_type = _TYPE_MAP[label]
			cards = self.engine.get_new_cards(language, card_type)
			if not cards:
				print(f"No new {label} available yet. Master prerequisites or review due items first.")
				return
			self._study_batch(cards)
			self._quiz_cards(cards, prompt_style="front", play_audio=False)
			return

		if mode.startswith("review "):
			label = mode.replace("review ", "")
			card_type = _TYPE_MAP[label]
			cards = self.engine.get_due_cards(language, card_type)
			if not cards:
				print(f"No {label} due for review right now.")
				return
			self._quiz_cards(cards, prompt_style="front", play_audio=False)
			return

		if mode == "translation quiz":
			cards = self.engine.get_due_cards(language, None)
			if not cards:
				print("No due cards for translation quiz.")
				return
			self._quiz_cards(cards, prompt_style="front", play_audio=False)
			return

		if mode == "listening quiz":
			cards = self.engine.get_due_cards(language, None)
			if not cards:
				print("No due cards for listening quiz.")
				return
			self._quiz_cards(cards, prompt_style="listening", play_audio=True)
			return

		print(f"Unknown mode '{mode}'.")

	def _study_batch(self, cards: list) -> None:
		print("\nStudy the new items first:\n")
		for item in self.engine.reveal_batch(cards):
			print(f"[{item['type'].upper()}] {item['front']} -> {item['answer']}")
			if item["aliases"]:
				print("  aliases:", ", ".join(item["aliases"]))
			print(f"  hint: {item['hint']}")
			print(f"  schema: {item['schema']}")
			related = self.engine.related_cards(self.engine.get_card(item["id"]))
			if related:
				print("  related schema cards:", ", ".join(card.front for card in related[:3]))
			if self.storage.get_setting("auto_play_audio_in_study", False):
				self.engine.play_audio(item["id"])
			input("  Press Enter for the next card...")
			print()

	def _quiz_cards(self, cards: list, prompt_style: str, play_audio: bool) -> None:
		print()
		for card in cards:
			if play_audio:
				played = self.engine.play_audio(card.id)
				print(f"Audio: {'played' if played else 'unavailable'}")
				prompt = f"[{card.type.upper()}] Listen and answer in English ({card.hint}): "
			else:
				prompt = f"[{card.type.upper()}] {card.front} -> "

			guess = input(prompt).strip()
			if guess.lower() == "quit":
				print("Leaving lesson early.")
				return

			was_correct = self.engine.check_answer(card, guess)
			print(f"Answer: {card.answer}")
			if card.aliases:
				print("Accepted aliases:", ", ".join(card.aliases))
			print("Result:", "correct" if was_correct else "needs work")
			print(f"Hint: {card.hint}")
			print(f"Schema: {card.schema}")
			rating = self._ask_for_rating(was_correct)
			result = self.engine.review_card(card, rating, was_correct)
			print(
				f"Next review: {result.next_due} | interval: {result.interval} day(s) | "
				f"ease factor: {result.ef:.2f} | repetition: {result.repetition}\n"
			)

	def _ask_for_rating(self, was_correct: bool) -> int:
		default_rating = 4 if was_correct else 2
		print("Rate recall: 5=Easy, 4=Good, 3=Hard, 2=Again soon, 1=Forgot")
		while True:
			response = input(f"Rating [{default_rating}]: ").strip().lower()
			if response == "quit":
				return default_rating
			if not response:
				return default_rating
			if response in {"1", "2", "3", "4", "5"}:
				return int(response)
			print("Please enter a number from 1 to 5.")

	def _show_stats(self, language: str) -> None:
		stats = self.engine.language_stats(language)
		print(f"\nStats for {language}:")
		print(f"  total cards: {stats['total_cards']}")
		print(f"  studied cards: {stats['studied_cards']}")
		print(f"  mastered cards: {stats['mastered_cards']}")
		for card_type, values in stats["by_type"].items():
			print(
				f"  {card_type}: total={values['total']} studied={values['studied']} "
				f"mastered={values['mastered']} unlocked={values['available_new']} due={values['due']}"
			)
		print()

	def _settings_menu(self) -> None:
		print("\nSettings:")
		print(f"  1. default_language = {self.storage.get_setting('default_language', 'arabic')}")
		print(f"  2. new_batch_size = {self.storage.get_setting('new_batch_size', 3)}")
		print(f"  3. review_batch_size = {self.storage.get_setting('review_batch_size', 10)}")
		print(f"  4. mastery_repetition_threshold = {self.storage.get_setting('mastery_repetition_threshold', 3)}")
		print(f"  5. audio_enabled = {self.storage.get_setting('audio_enabled', True)}")
		print(f"  6. auto_play_audio_in_study = {self.storage.get_setting('auto_play_audio_in_study', False)}")
		print("Press Enter to keep the current value.\n")
		self._update_setting("default_language", cast=str)
		self._update_setting("new_batch_size", cast=int)
		self._update_setting("review_batch_size", cast=int)
		self._update_setting("mastery_repetition_threshold", cast=int)
		self._update_setting("audio_enabled", cast=self._to_bool)
		self._update_setting("auto_play_audio_in_study", cast=self._to_bool)
		print("Settings updated. Restart the app if you changed audio_enabled.\n")

	def _update_setting(self, key: str, cast) -> None:
		current = self.storage.get_setting(key)
		response = input(f"{key} [{current}]: ").strip()
		if not response:
			return
		self.storage.update_setting(key, cast(response))

	@staticmethod
	def _to_bool(value: str) -> bool:
		return value.strip().lower() in {"1", "true", "yes", "y", "on"}



def main() -> None:
	"""Run the CLI app."""
	TrainerCLI().run()


if __name__ == "__main__":
	main()
