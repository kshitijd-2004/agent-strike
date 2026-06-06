"""HTTP API (Layer 6 — output adapter).

FastAPI app exposing:

* REST endpoints for starting / inspecting simulation runs
  (:mod:`agentstrike.api.routes`).
* SSE endpoint streaming the live event log
  (:mod:`agentstrike.api.sse`).

Construct the ASGI app via :func:`agentstrike.api.server.create_app`.
"""
