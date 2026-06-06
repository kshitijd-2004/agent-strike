"""Red Agent — attacker, backed by ``claude-haiku-4-5``.

The Red Agent is given:

* A scenario brief from
  :class:`agentstrike.attack_defense.scenarios.registry.ScenarioRegistry`.
* The current transcript (turns committed to the memory store so far).
* The MCP tool catalogue (filesystem, mock API, mock data store).

It emits an attack message — typically a tool call sequence designed to make
the Blue Agent leak information, exceed authority, or otherwise violate its
policy.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agentstrike.agents.base import BaseAgent

if TYPE_CHECKING:
    from agentstrike.attack_defense.scenarios.registry import Scenario
    from agentstrike.events.log import EventLog
    from agentstrike.events.types import SignedMessage


class RedAgent(BaseAgent):
    """Generates adversarial inputs and tool calls."""

    role = "red"

    def __init__(
        self,
        scenario: "Scenario",
        event_log: "EventLog",
        model: str | None = None,
    ) -> None:
        """Initialise the Red Agent for a specific scenario.

        Args:
            scenario:  The attack scenario being run; informs the system
                prompt and the tool catalogue.
            event_log: Shared append-only event log.
            model:     Override the default ``claude-haiku-4-5`` model id.
        """
        raise NotImplementedError

    async def act(self, message: "SignedMessage") -> "SignedMessage":
        """Produce the next attack payload.

        Returns a signed response that the orchestrator will route to the Blue
        Agent. The payload may include tool calls; tool execution is the
        Blue Agent's responsibility, not Red's.
        """
        raise NotImplementedError
