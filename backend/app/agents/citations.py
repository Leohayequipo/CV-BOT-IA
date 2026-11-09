"""Turn the model's [source-id] markers into numbered citations, keeping only real sources.

The model cites by id because the profile sits in a prompt that never changes between requests
(so it stays cached) and can't carry per-answer numbers. Here each id becomes [1], [2]... in
order of appearance, and its `citation` event goes out just before the first marker that uses it
(docs/API.md). A marker whose id wasn't offered to the model is dropped: a citation the
assistant invented never reaches the visitor.
"""

import re
from collections.abc import Mapping

from app.agents.sources import Source
from app.schemas.chat import CitationEvent, TokenEvent

# Looks like a source id; anything else in brackets is ordinary text
_SOURCE_ID = re.compile(r"[a-z0-9][a-z0-9:#_-]*")
# A bracket that isn't closed within this many characters wasn't a marker
_MAX_MARKER = 80


class CitationStream:
    def __init__(self, sources: Mapping[str, Source]) -> None:
        self._sources = sources
        self._numbers: dict[str, int] = {}
        self._pending = ""  # an unclosed "[" and what follows it

    @property
    def cited(self) -> list[Source]:
        return [self._sources[source_id] for source_id in self._numbers]

    def feed(self, text: str) -> list[TokenEvent | CitationEvent]:
        data, self._pending = self._pending + text, ""
        events: list[TokenEvent | CitationEvent] = []
        position = 0
        while True:
            start = data.find("[", position)
            if start == -1:
                _append_text(events, data[position:])
                return events
            _append_text(events, data[position:start])
            end = data.find("]", start)
            if end == -1:
                rest = data[start:]
                if len(rest) > _MAX_MARKER or "\n" in rest:
                    _append_text(events, rest)
                else:
                    self._pending = rest  # the rest of the marker may come in the next piece
                return events
            self._marker(events, data[start + 1 : end], data[start : end + 1])
            position = end + 1

    def flush(self) -> list[TokenEvent | CitationEvent]:
        """The text held back waiting for a "]" that never came."""
        events: list[TokenEvent | CitationEvent] = []
        _append_text(events, self._pending)
        self._pending = ""
        return events

    def _marker(self, events: list[TokenEvent | CitationEvent], inner: str, original: str) -> None:
        if not _SOURCE_ID.fullmatch(inner):
            _append_text(events, original)
        elif inner in self._sources:
            if inner not in self._numbers:
                self._numbers[inner] = len(self._numbers) + 1
                source = self._sources[inner]
                events.append(
                    CitationEvent(
                        id=self._numbers[inner],
                        label=source.label,
                        source=source.source,
                        section=source.section,
                    )
                )
            _append_text(events, f"[{self._numbers[inner]}]")
        # else: an id nobody offered, so there's nothing to cite and nothing to show


def _append_text(events: list[TokenEvent | CitationEvent], text: str) -> None:
    if text:
        events.append(TokenEvent(text=text))
