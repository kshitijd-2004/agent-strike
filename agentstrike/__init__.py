"""AgentStrike — red team simulation platform for Claude-based AI agents.

The :mod:`agentstrike` package is organised into six layers that mirror the
architecture diagram in the project README:

1. :mod:`agentstrike.orchestrator` — session keys, turn sequencing, routing.
2. :mod:`agentstrike.agents`       — Red, Blue and Judge Claude agents.
3. :mod:`agentstrike.attack_defense` — scenarios, validation pipeline, CAI.
4. :mod:`agentstrike.infrastructure` — MCP mock tools, memory store, clocks.
5. :mod:`agentstrike.events`       — typed events, append-only log, SSE.
6. :mod:`agentstrike.api`,
   :mod:`agentstrike.cli`,
   :mod:`agentstrike.reporting`    — output adapters (HTTP / CLI / PDF).

Nothing is implemented in this scaffold; each module contains docstrings and
stub signatures intended as an implementation roadmap.
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
