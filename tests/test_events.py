"""Tests for :mod:`agentstrike.events`.

Covers:

* ``types.py``     — every :class:`EventType` round-trips through Pydantic
  serialisation; :meth:`SignedMessage.canonical_bytes` is stable across
  Python invocations (deterministic JSON ordering).
* ``log.py``       — concurrent appends preserve order; ``replay`` returns
  exactly what was written; ``subscribe`` only sees future events.
* ``broadcast.py`` — multiple subscribers each receive every frame; closing
  the broadcaster cleans up subscriber tasks.
"""

from __future__ import annotations

import pytest


@pytest.mark.skip(reason="Event type tests pending implementation.")
def test_signed_message_canonical_bytes_is_stable() -> None:
    """Two equal :class:`SignedMessage` instances must serialise identically."""


@pytest.mark.skip(reason="Event log tests pending implementation.")
async def test_event_log_replay_matches_written_events() -> None:
    """:meth:`replay` must return exactly the events that were appended."""


@pytest.mark.skip(reason="Broadcast tests pending implementation.")
async def test_broadcaster_fans_out_to_multiple_subscribers() -> None:
    """Every subscriber receives every event after they connect."""
