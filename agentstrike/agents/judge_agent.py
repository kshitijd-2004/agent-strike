"""Judge Agent — scorer, backed by ``claude-sonnet-4-6``.

The Judge sees the full Red attack and Blue defence for the round and emits a
structured ``JudgeVerdict`` covering:

* ``attack_success``      — did Red achieve the scenario objective?
* ``defense_quality``     — was Blue's refusal/execution well-justified?
* ``policy_violations``   — list of named policies the Blue Agent violated.
* ``score``               — composite integer 0–100.
* ``rationale``           — plain-text explanation surfaced in the dashboard.

Scoring is deterministic given the same model + transcript by setting
temperature to 0 and seeding via the session id.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from agentstrike.agents.base import BaseAgent

if TYPE_CHECKING:
    from agentstrike.events.log import EventLog
    from agentstrike.events.types import SignedMessage


@dataclass(frozen=True)
class JudgeVerdict:
    """Structured output of :meth:`JudgeAgent.act`.

    Attributes:
        round_idx:         Which round was judged.
        attack_success:    Did the Red attack succeed?
        defense_quality:   Qualitative grade for Blue's defence.
        policy_violations: Named policies broken by Blue, if any.
        score:             Composite integer in ``[0, 100]``.
        rationale:         Human-readable justification.
    """

    round_idx: int
    attack_success: bool
    defense_quality: str
    policy_violations: list[str]
    score: int
    rationale: str


class JudgeAgent(BaseAgent):
    """Independent scorer for each round."""

    role = "judge"

    def __init__(self, event_log: "EventLog", model: str | None = None) -> None:
        """Initialise the Judge Agent.

        Args:
            event_log: Shared append-only event log.
            model:     Override the default ``claude-sonnet-4-6`` model id.
        """
        raise NotImplementedError

    async def act(self, message: "SignedMessage") -> "SignedMessage":
        """Return a signed message wrapping a :class:`JudgeVerdict` payload."""
        raise NotImplementedError
