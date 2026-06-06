"""Deterministic turn sequencing for AgentStrike simulations.

The default cadence per round is::

    Red  → Blue → Judge

The :class:`TurnSequencer` is a pure state machine: it does not call any
agent, it only declares whose turn it is and emits ``TURN_STARTED`` /
``TURN_ENDED`` events into the log. The :mod:`agentstrike.orchestrator.router`
is responsible for actually invoking the chosen agent.
"""

from __future__ import annotations

from enum import Enum
from typing import Iterator


class Role(str, Enum):
    """The three roles in a simulation."""

    RED = "red"
    BLUE = "blue"
    JUDGE = "judge"


class TurnSequencer:
    """State machine that yields the next :class:`Role` to act.

    A ``round`` is a full Red→Blue→Judge cycle. The sequencer enforces
    ``max_rounds`` and tracks a monotonically increasing turn index used for
    vector-clock initialisation.
    """

    def __init__(self, max_rounds: int) -> None:
        """Initialise the sequencer.

        Args:
            max_rounds: Total number of full Red/Blue/Judge cycles to run.
        """
        raise NotImplementedError

    def __iter__(self) -> Iterator[tuple[int, int, Role]]:
        """Yield ``(round_idx, turn_idx, role)`` triples until exhausted."""
        raise NotImplementedError

    @property
    def current_round(self) -> int:
        """The 0-indexed round currently being executed."""
        raise NotImplementedError

    @property
    def is_finished(self) -> bool:
        """True once every scheduled turn has been yielded."""
        raise NotImplementedError

    def reset(self) -> None:
        """Rewind back to round 0, turn 0. Useful for replay tooling."""
        raise NotImplementedError
