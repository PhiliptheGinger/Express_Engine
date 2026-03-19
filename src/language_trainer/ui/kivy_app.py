"""Minimal Kivy-ready UI shell that reuses the engine."""

from __future__ import annotations

from language_trainer.engine import Engine
from language_trainer.storage import Storage


class KivyTrainerAdapter:
	"""Thin adapter for a future touch UI.

	The actual Kivy widgets are intentionally deferred, but this adapter keeps the
	data access points explicit so a mobile screen flow can call the same engine
	used by the CLI.
	"""

	def __init__(self) -> None:
		self.storage = Storage()
		self.engine = Engine(self.storage)

	def summary(self) -> dict[str, object]:
		return {
			"languages": self.engine.available_languages(),
			"modes": self.engine.available_modes(),
		}



def launch() -> None:
	"""Entry point for a future Kivy UI."""
	try:
		import kivy  # noqa: F401
	except ImportError:
		print("Kivy is not installed. Install it with: pip install kivy")
		return

	adapter = KivyTrainerAdapter()
	print("Minimal Kivy bridge ready.")
	print("Available languages:", ", ".join(adapter.summary()["languages"]))
	print("Next step: bind these engine calls to a language screen, menu screen, and card screen.")


if __name__ == "__main__":
	launch()
