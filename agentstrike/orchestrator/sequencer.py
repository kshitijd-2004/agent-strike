"""Deterministic turn sequencing for AgentStrike simulations.

The default cadence per round is::

    Red  → Blue → Judge

The :class:`TurnSequencer` is a pure state machine: it does not call any
agent, it only declares whose turn it is. The
:mod:`agentstrike.orchestrator.router` is responsible for actually invoking
the chosen agent.
"""

from __future__ import annotations

from enum import Enum
from typing import Iterator


class Role(str, Enum):
    """The three roles in a simulation."""

    RED = "red"
    BLUE = "blue"
    JUDGE = "judge"


_ROUND_ORDER: tuple[Role, ...] = (Role.RED, Role.BLUE, Role.JUDGE)
"""Canonical per-round role order. Length 3 → one round = three turns."""


class TurnSequencer:
    """State machine that yields the next :class:`Role` to act.

    A ``round`` is a full Red→Blue→Judge cycle. The sequencer enforces
    ``max_rounds`` and tracks a monotonically increasing turn index used for
    vector-clock initialisation.
    """

    def __init__(self, max_rounds: int) -> None:
        if max_rounds < 0:
            raise ValueError("max_rounds must be non-negative")
        self._max_rounds = max_rounds
        self._round_idx = 0
        self._slot = 0
        self._turn_idx = 0

    def __iter__(self) -> Iterator[tuple[int, int, Role]]:
        """Yield ``(round_idx, turn_idx, role)`` triples until exhausted."""
        while self._round_idx < self._max_rounds:
            role = _ROUND_ORDER[self._slot]
            triple = (self._round_idx, self._turn_idx, role)
            self._advance()
            yield triple

    def _advance(self) -> None:
        """Move one slot forward, wrapping to the next round if needed."""
        self._turn_idx += 1
        self._slot += 1
        if self._slot >= len(_ROUND_ORDER):
            self._slot = 0
            self._round_idx += 1

    @property
    def current_round(self) -> int:
        """The 0-indexed round currently being executed (or ``max_rounds`` once done)."""
        return self._round_idx

    @property
    def current_turn(self) -> int:
        """Number of turns yielded so far (0 before the first call)."""
        return self._turn_idx

    @property
    def max_rounds(self) -> int:
        """Total number of rounds this sequencer is configured for."""
        return self._max_rounds

    @property
    def is_finished(self) -> bool:
        """True once every scheduled turn has been yielded."""
        return self._round_idx >= self._max_rounds

    def reset(self) -> None:
        """Rewind back to round 0, turn 0. Useful for replay tooling."""
        self._round_idx = 0
        self._slot = 0
        self._turn_idx = 0
