"""Vector-clock primitive for causal ordering.

A :class:`VectorClock` is a mapping ``agent_id -> counter`` whose semantics
are the standard Lamport / Mattern vector-clock rules:

* :meth:`tick` — increment the local agent's counter (called when the agent
  emits an event).
* :meth:`merge` — element-wise max with an incoming clock, used when receiving
  a message.
* :meth:`happens_before` — partial ordering predicate.

The orchestrator stamps every memory store record with a snapshot of the
clock so that the validator's *Causality* stage can reject out-of-order tool
calls.
"""

from __future__ import annotations

from typing import Iterable


class VectorClock:
    """Mutable vector clock keyed by agent id."""

    def __init__(self, agents: Iterable[str]) -> None:
        """Initialise with a fixed roster of agent ids, all set to zero."""
        raise NotImplementedError

    def tick(self, agent_id: str) -> None:
        """Increment ``agent_id``'s component by one."""
        raise NotImplementedError

    def merge(self, other: "VectorClock") -> None:
        """In-place element-wise max with ``other``."""
        raise NotImplementedError

    def snapshot(self) -> dict[str, int]:
        """Return an immutable dict snapshot for embedding in a record."""
        raise NotImplementedError

    def happens_before(self, other: "VectorClock") -> bool:
        """``True`` iff ``self`` causally precedes ``other``."""
        raise NotImplementedError

    def concurrent_with(self, other: "VectorClock") -> bool:
        """``True`` iff neither clock causally precedes the other."""
        raise NotImplementedError
