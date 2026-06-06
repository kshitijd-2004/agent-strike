"""Event stream layer (Layer 5).

Modules:

* :mod:`agentstrike.events.types`     — typed Pydantic event schemas plus the
  :class:`SignedMessage` envelope.
* :mod:`agentstrike.events.log`       — append-only on-disk event log.
* :mod:`agentstrike.events.broadcast` — fan-out to SSE subscribers.

All inter-layer communication in AgentStrike is funnelled through these
modules, which makes the platform fully observable and replayable.
"""
