"""SSE endpoint that streams the live event log.

Single endpoint:

    ``GET /api/runs/{session_id}/stream``

Implemented with :mod:`sse_starlette` so backpressure and disconnect handling
are correct out of the box. Initial connect replays the full history; on
reconnect the dashboard sends ``Last-Event-ID`` and we resume from there.
"""

from __future__ import annotations

from typing import Any


def build_router() -> Any:
    """Return the ``APIRouter`` exposing the SSE endpoint."""
    raise NotImplementedError


async def stream_events(session_id: str, last_event_id: str | None) -> Any:
    """Yield ``EventSourceResponse`` frames for ``session_id``.

    Args:
        session_id:    Simulation run to subscribe to.
        last_event_id: Optional resume token sent by the browser; events with
            ids ``<= last_event_id`` are skipped.

    Returns:
        A ``sse_starlette.EventSourceResponse`` instance.
    """
    raise NotImplementedError
