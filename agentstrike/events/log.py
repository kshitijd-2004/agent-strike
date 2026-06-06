"""Append-only event log.

Events are written as JSON Lines under
``Settings.event_log_dir / <session_id>.jsonl``. The log is the single source
of truth for replay, PDF report generation and the SSE broadcaster.

Concurrency model:
    * One :class:`EventLog` per simulation session.
    * All writes go through an ``asyncio.Lock`` so events from the
      Red/Blue/Judge tasks interleave atomically.
    * Subscribers (the SSE broadcaster) read from an in-memory queue rather
      than re-tailing the file.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, AsyncIterator

if TYPE_CHECKING:
    from agentstrike.events.types import Event


class EventLog:
    """Append-only, fan-out-friendly event log."""

    def __init__(self, session_id: str, base_dir: Path) -> None:
        """Open / create the log file for ``session_id``.

        Args:
            session_id: Owning simulation session id.
            base_dir:   Root directory for ``<session_id>.jsonl``.
        """
        raise NotImplementedError

    async def append(self, event: "Event") -> None:
        """Persist ``event`` to disk and notify every live subscriber."""
        raise NotImplementedError

    async def subscribe(self) -> AsyncIterator["Event"]:
        """Yield future events as they are appended.

        The iterator never replays past events; for that, call
        :meth:`replay` first.
        """
        raise NotImplementedError

    def replay(self) -> list["Event"]:
        """Return every event currently on disk, in order.

        Used by the dashboard on initial connect and by the PDF reporter.
        """
        raise NotImplementedError

    async def close(self) -> None:
        """Flush and close the underlying file handle."""
        raise NotImplementedError
