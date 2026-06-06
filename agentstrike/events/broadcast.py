"""SSE fan-out for the event log.

Bridges :class:`agentstrike.events.log.EventLog` to many concurrent HTTP
clients. Each connected dashboard receives an independent async iterator that
yields events as JSON-encoded SSE frames.

The broadcaster is process-local; horizontal scaling would require a Redis
pub/sub or similar shared bus, which is intentionally out of scope.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, AsyncIterator

if TYPE_CHECKING:
    from agentstrike.events.log import EventLog
    from agentstrike.events.types import Event


class EventBroadcaster:
    """Multi-subscriber wrapper around an :class:`EventLog`."""

    def __init__(self, event_log: "EventLog") -> None:
        """Wrap ``event_log`` and spawn the fan-out task on first subscribe."""
        raise NotImplementedError

    async def stream(self, replay_history: bool = True) -> AsyncIterator[bytes]:
        """Yield SSE frames (``data: ...\\n\\n``) for every event.

        Args:
            replay_history: If ``True``, send every existing event before
                streaming live updates. The dashboard uses ``True`` on its
                initial connect and ``False`` for reconnects.
        """
        raise NotImplementedError

    @staticmethod
    def _format_sse_frame(event: "Event") -> bytes:
        """Serialise an :class:`Event` to an ``id: ...\\ndata: ...\\n\\n`` frame."""
        raise NotImplementedError

    async def close(self) -> None:
        """Tear down every active subscriber and free resources."""
        raise NotImplementedError
