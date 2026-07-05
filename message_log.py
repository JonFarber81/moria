"""In-game message log.

Holds the running list of things that have happened (combat, death, later
pickups) so they can be drawn in the UI panel instead of printed to stdout.
This module is pure state — how the log *looks* lives in render.py, keeping
presentation in one place.
"""
from __future__ import annotations

import config


class Message:
    """A single log line and the color to draw it in."""

    def __init__(self, text: str, fg: tuple[int, int, int]) -> None:
        self.text = text
        self.fg = fg


class MessageLog:
    """An append-only list of messages. Rendering shows the most recent tail,
    so the log can grow unbounded without affecting what's on screen."""

    def __init__(self) -> None:
        self.messages: list[Message] = []

    def add(self, text: str, fg: tuple[int, int, int] = config.COLOR_TEXT) -> None:
        self.messages.append(Message(text, fg))

    def add_all(self, texts: list[str], fg: tuple[int, int, int] = config.COLOR_TEXT) -> None:
        """Convenience for the list[str] that combat resolution returns."""
        for text in texts:
            self.add(text, fg)
