"""Audio playback: locate files, play them, and fall back gracefully."""

from __future__ import annotations

from pathlib import Path

# Audio directory relative to the project root.
_AUDIO_DIR = Path(__file__).resolve().parents[2] / "audio"


def _audio_path(card_id: str) -> Path:
    """Return the expected MP3 path for a given card ID."""
    return _AUDIO_DIR / f"{card_id}.mp3"


class AudioPlayer:
    """Play audio files for cards using pygame (if available)."""

    def __init__(self) -> None:
        self._available = self._init_pygame()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def play(self, card_id: str) -> None:
        """Play the audio file associated with *card_id*.

        Falls back silently if pygame is unavailable or the file is missing.
        """
        if not self._available:
            return

        path = _audio_path(card_id)
        if not path.exists():
            return

        try:
            import pygame  # noqa: PLC0415

            pygame.mixer.music.load(str(path))
            pygame.mixer.music.play()
            # Block until playback finishes.
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
        except Exception:  # noqa: BLE001
            # Never let an audio error crash the lesson.
            pass

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _init_pygame() -> bool:
        """Attempt to initialise pygame mixer; return True on success."""
        try:
            import pygame  # noqa: PLC0415

            pygame.mixer.init()
            return True
        except Exception:  # noqa: BLE001
            return False
