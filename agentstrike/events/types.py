"""Typed event schemas.

Every event in AgentStrike is a Pydantic model that inherits from
:class:`Event`. The discriminator field is :attr:`Event.type` (an
:class:`EventType` enum) so the FastAPI / SSE layer can serialise and route
events generically.

The PT (Pydantic Tagged Union) discriminator pattern lets the dashboard
deserialise heterogeneous event lists with full type safety.
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class EventType(str, Enum):
    """Discriminator for the typed event union."""

    SIMULATION_STARTED = "simulation_started"
    SIMULATION_FINISHED = "simulation_finished"

    TURN_STARTED = "turn_started"
    TURN_ENDED = "turn_ended"

    LLM_CALL_STARTED = "llm_call_started"
    LLM_CALL_FINISHED = "llm_call_finished"

    TOOL_CALL_REQUESTED = "tool_call_requested"
    TOOL_CALL_EXECUTED = "tool_call_executed"

    VALIDATION_STAGE_PASSED = "validation_stage_passed"
    VALIDATION_STAGE_FAILED = "validation_stage_failed"

    CONSTITUTIONAL_CRITIQUE = "constitutional_critique"
    CONSTITUTIONAL_REVISION = "constitutional_revision"

    MEMORY_WRITE_COMMITTED = "memory_write_committed"
    MEMORY_WRITE_REJECTED = "memory_write_rejected"

    JUDGE_VERDICT = "judge_verdict"

    ERROR = "error"


class Event:
    """Base class for every typed event.

    Attributes (planned, all Pydantic fields):
        id:          ULID for the event (sortable, globally unique).
        type:        :class:`EventType` discriminator.
        session_id:  Owning simulation session id.
        round_idx:   Round number, or ``None`` for session-level events.
        turn_idx:    Turn number, or ``None`` for session-level events.
        agent_role:  ``"red" | "blue" | "judge"`` or ``None``.
        timestamp:   Unix epoch seconds (float).
        payload:     Event-specific data (subclasses narrow the type).
    """

    def __init__(self, **fields: Any) -> None:
        """Construct an event with the given fields. Real impl subclasses BaseModel."""
        raise NotImplementedError


class SignedMessage:
    """Envelope passed between agents through the orchestrator.

    Attributes (planned):
        sender:    Originating role.
        recipient: Target role.
        round_idx: Round of this message.
        turn_idx:  Turn within the round.
        body:      Serialised payload (text + tool calls + tool results).
        signature: Hex HMAC-SHA256 over canonical bytes (see
            :mod:`agentstrike.orchestrator.session`).
    """

    def __init__(self, **fields: Any) -> None:
        """Construct a signed message envelope."""
        raise NotImplementedError

    def canonical_bytes(self) -> bytes:
        """Return the bytes that should be signed / verified.

        Excludes the ``signature`` field and uses canonical JSON ordering so
        signing is deterministic.
        """
        raise NotImplementedError
