"""Kivy-based graphical UI for Language Trainer.

This module is a placeholder for future Kivy UI development.
The learning engine (engine.py) is intentionally kept separate so it
remains fully reusable from both the CLI app (app.py) and this UI.

To run the Kivy app (once implemented):
    python3 -m language_trainer.ui.kivy_app
"""

from __future__ import annotations


def launch() -> None:
    """Launch the Kivy UI.

    Replace this stub with a real ``kivy.app.App`` subclass when you are
    ready to move away from the CLI.
    """
    try:
        import kivy  # noqa: F401
    except ImportError:
        print(
            "Kivy is not installed.  Install it with:\n"
            "    pip install kivy\n"
            "and then run this module again."
        )
        return

    print("Kivy UI is not yet implemented.  Coming soon!")


if __name__ == "__main__":
    launch()
