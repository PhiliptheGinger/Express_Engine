"""Audio backends kept separate from the learning engine."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Protocol

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

_AUDIO_DIR = Path(__file__).resolve().parents[2] / "audio"


class AudioBackend(Protocol):
	"""Protocol for pluggable audio playback backends."""

	def play_file(self, path: Path) -> bool:
		"""Play a file and return whether playback was attempted successfully."""


class NullAudioBackend:
	"""Fallback backend used on environments where playback is unreliable."""

	def play_file(self, path: Path) -> bool:
		return False


class PygameAudioBackend:
	"""Optional pygame backend for environments where it works."""

	def __init__(self) -> None:
		import pygame  # noqa: PLC0415

		pygame.mixer.init()
		self._pygame = pygame

	def play_file(self, path: Path) -> bool:
		self._pygame.mixer.music.load(str(path))
		self._pygame.mixer.music.play()
		while self._pygame.mixer.music.get_busy():
			self._pygame.time.wait(100)
		return True


class AudioPlayer:
	"""Facade around card-based audio lookup and backend management."""

	def __init__(self, enabled: bool = True) -> None:
		self._enabled = enabled
		self._backend: AudioBackend = self._build_backend() if enabled else NullAudioBackend()

	def play(self, card_id: str) -> bool:
		"""Attempt to play the audio file matching *card_id*."""
		if not self._enabled:
			return False
		path = _AUDIO_DIR / f"{card_id}.mp3"
		if not path.exists():
			return False
		try:
			return self._backend.play_file(path)
		except Exception:  # noqa: BLE001
			return False

	@staticmethod
	def _build_backend() -> AudioBackend:
		try:
			return PygameAudioBackend()
		except Exception:  # noqa: BLE001
			return NullAudioBackend()
