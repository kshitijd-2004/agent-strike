"""Append-only event log.

Events are written as JSON Lines under ``base_dir / <session_id>.jsonl`` and
also fanned out to in-memory subscribers (used by the SSE broadcaster).

This module is the single source of truth for replay, PDF report generation
and the live dashboard.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import AsyncIterator

from agentstrike.events.types import Event


class EventLog:
    """Append-only, fan-out-friendly event log."""

    def __init__(self, session_id: str, base_dir: Path) -> None:
        """Open / create the log file for ``session_id`` under ``base_dir``."""
        self.session_id = session_id
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._path = self.base_dir / f"{session_id}.jsonl"
        self._path.touch(exist_ok=True)
        self._lock = asyncio.Lock()
        self._subscribers: list[asyncio.Queue[Event]] = []

    @property
    def path(self) -> Path:
        """Filesystem path of the underlying JSONL log."""
        return self._path

    async def append(self, event: Event) -> None:
        """Persist ``event`` to disk and notify every live subscriber."""
        async with self._lock:
            line = event.model_dump_json() + "\n"
            with self._path.open("a", encoding="utf-8") as handle:
                handle.write(line)
                handle.flush()
            for queue in list(self._subscribers):
                await queue.put(event)

    async def subscribe(self) -> AsyncIterator[Event]:
        """Yield future events as they are appended (no historical replay)."""
        queue: asyncio.Queue[Event] = asyncio.Queue()
        self._subscribers.append(queue)
        try:
            while True:
                yield await queue.get()
        finally:
            self._subscribers.remove(queue)

    def replay(self) -> list[Event]:
        """Return every event currently on disk, in order."""
        events: list[Event] = []
        if not self._path.exists():
            return events
        with self._path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                events.append(Event.model_validate(json.loads(line)))
        return events

    async def close(self) -> None:
        """Drain subscribers; the file handle is opened per-write so nothing else to close."""
        async with self._lock:
            self._subscribers.clear()
