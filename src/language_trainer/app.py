"""Main entry point for Language Trainer."""

from __future__ import annotations

import sys

from .engine import Engine
from .storage import Storage


def main() -> None:
    """Launch the Language Trainer CLI."""
    storage = Storage()
    engine = Engine(storage)

    print("Welcome to Language Trainer!")
    print("Available languages:", ", ".join(engine.available_languages()))
    print("Type 'quit' at any prompt to exit.\n")

    while True:
        language = input("Choose a language (arabic/korean): ").strip().lower()
        if language == "quit":
            break
        if language not in engine.available_languages():
            print(f"Unknown language '{language}'. Please try again.")
            continue

        lesson_type = input("Choose lesson type (alphabet/words/phrases/translate/listen): ").strip().lower()
        if lesson_type == "quit":
            break

        engine.run_lesson(language, lesson_type)

    print("Goodbye! Progress saved.")
    storage.save()


if __name__ == "__main__":
    main()
