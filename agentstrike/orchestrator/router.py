"""Signed message router — the heart of the orchestrator.

For each turn:

1. The :class:`Router` asks the :class:`agentstrike.orchestrator.sequencer.TurnSequencer`
   whose turn it is.
2. It builds a :class:`agentstrike.events.types.SignedMessage` containing the
   transcript and any tool results, signs it with the session key, and hands
   it to the appropriate agent.
3. The agent's reply is verified, validated through the
   :mod:`agentstrike.attack_defense.validation_pipeline`, then committed to
   the :class:`agentstrike.infrastructure.memory_store.MemoryStore`.
4. Events are emitted at every step.

The router never executes agent logic itself; it composes the other building
blocks.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentstrike.agents.base import BaseAgent
    from agentstrike.events.log import EventLog
    from agentstrike.events.types import SignedMessage
    from agentstrike.infrastructure.memory_store import MemoryStore
    from agentstrike.orchestrator.sequencer import Role, TurnSequencer
    from agentstrike.orchestrator.session import SessionKey


class Router:
    """Coordinates one full simulation run."""

    def __init__(
        self,
        sequencer: "TurnSequencer",
        agents: dict["Role", "BaseAgent"],
        session_key: "SessionKey",
        memory: "MemoryStore",
        event_log: "EventLog",
    ) -> None:
        """Wire the router up with all the collaborators it needs.

        Args:
            sequencer:   Turn schedule.
            agents:      Mapping of role → concrete agent instance.
            session_key: HMAC key for message signing/verification.
            memory:      Tamper-evident memory store for committed turns.
            event_log:   Append-only log used for SSE broadcast + reports.
        """
        raise NotImplementedError

    async def run(self) -> None:
        """Drive the simulation until the sequencer is exhausted.

        Emits ``SIMULATION_STARTED`` / ``SIMULATION_FINISHED`` events at the
        boundaries and ``TURN_*`` events for each step.
        """
        raise NotImplementedError

    async def _dispatch(self, role: "Role", message: "SignedMessage") -> "SignedMessage":
        """Verify, deliver to the agent, then re-sign the response.

        Internal helper. Raises if signature verification fails.
        """
        raise NotImplementedError
