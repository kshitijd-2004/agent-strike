"""Typed event schemas.

Every event in AgentStrike is a Pydantic model that inherits from
:class:`Event`. The discriminator field is :attr:`Event.type` (an
:class:`EventType` enum) so the FastAPI / SSE layer can serialise and route
events generically.
"""

from __future__ import annotations

import json
import time
import uuid
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


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


class Event(BaseModel):
    """A single observable event in a simulation run.

    Carries the discriminator :attr:`type`, optional positional metadata
    (``round_idx`` / ``turn_idx`` / ``agent_role``) and a free-form
    :attr:`payload`. The dashboard, PDF reporter and SSE broadcaster all
    consume this shape.
    """

    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    type: EventType
    session_id: str
    round_idx: int | None = None
    turn_idx: int | None = None
    agent_role: str | None = None
    timestamp: float = Field(default_factory=time.time)
    payload: dict[str, Any] = Field(default_factory=dict)


class SignedMessage(BaseModel):
    """Envelope passed between agents through the orchestrator.

    The :attr:`signature` is an HMAC-SHA256 hex digest over
    :meth:`canonical_bytes` (the message minus the signature). An empty
    string is reserved for unsigned messages, which the router refuses to
    accept on the inbound path.
    """

    model_config = ConfigDict(extra="forbid")

    sender: str
    recipient: str
    round_idx: int
    turn_idx: int
    body: dict[str, Any] = Field(default_factory=dict)
    signature: str = ""

    def canonical_bytes(self) -> bytes:
        """Return the canonical JSON bytes that should be signed/verified.

        ``signature`` is excluded; keys are sorted and whitespace is stripped
        so the digest is independent of insertion order.
        """
        data = self.model_dump(exclude={"signature"}, mode="json")
        return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
