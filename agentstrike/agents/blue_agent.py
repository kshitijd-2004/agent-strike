"""Blue Agent — defender, backed by ``claude-opus-4-6``.

The Blue Agent represents the **system under test**. For every incoming Red
attack it must:

1. Run the candidate response through the
   :mod:`agentstrike.attack_defense.validation_pipeline` (5-stage tool-call
   validator).
2. Apply the Constitutional AI self-check from
   :mod:`agentstrike.attack_defense.constitutional`.
3. Either execute the validated tool calls (against the MCP mock environment)
   or refuse with a structured rationale.

Refusals and successful tool executions both emit events that the Judge will
score.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agentstrike.agents.base import BaseAgent

if TYPE_CHECKING:
    from agentstrike.attack_defense.constitutional import ConstitutionalChecker
    from agentstrike.attack_defense.validation_pipeline import ValidationPipeline
    from agentstrike.events.log import EventLog
    from agentstrike.events.types import SignedMessage


class BlueAgent(BaseAgent):
    """Defender that validates every tool call before executing it."""

    role = "blue"

    def __init__(
        self,
        validator: "ValidationPipeline",
        constitution: "ConstitutionalChecker",
        event_log: "EventLog",
        model: str | None = None,
    ) -> None:
        """Wire the Blue Agent up with its defensive collaborators.

        Args:
            validator:    Five-stage tool-call validator.
            constitution: Constitutional AI self-critique helper.
            event_log:    Shared append-only event log.
            model:        Override the default ``claude-opus-4-6`` model id.
        """
        raise NotImplementedError

    async def act(self, message: "SignedMessage") -> "SignedMessage":
        """Defend against the incoming Red attack and produce a response.

        Steps:
            1. Generate a candidate completion via the Anthropic SDK.
            2. Validate any tool calls via :attr:`validator`.
            3. Self-critique with :attr:`constitution`. If the critique flags
               a violation, regenerate up to ``N`` times before refusing.
            4. Execute approved tool calls and embed results in the response.
        """
        raise NotImplementedError
