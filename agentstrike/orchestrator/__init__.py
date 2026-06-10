"""Orchestrator layer (Layer 1).

Glues the three Claude agents together inside a single simulation:

* :mod:`agentstrike.orchestrator.session`   — HMAC-SHA256 session keys.
* :mod:`agentstrike.orchestrator.sequencer` — Deterministic turn sequencing.
* :mod:`agentstrike.orchestrator.router`    — Verifies signatures and routes
  each :class:`agentstrike.events.types.SignedMessage` to the next agent.

The orchestrator is the only component that holds the session secret; agents
and tools see only signed envelopes.
"""

from agentstrike.orchestrator.router import AgentProtocol, MemoryProtocol, Router
from agentstrike.orchestrator.sequencer import Role, TurnSequencer
from agentstrike.orchestrator.session import (
    SessionKey,
    SignatureError,
    new_session_key,
    sign,
    verify,
)

__all__ = [
    "AgentProtocol",
    "MemoryProtocol",
    "Role",
    "Router",
    "SessionKey",
    "SignatureError",
    "TurnSequencer",
    "new_session_key",
    "sign",
    "verify",
]
