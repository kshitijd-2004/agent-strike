"""Infrastructure layer (Layer 4).

Pure-Python primitives used by the upper layers:

* :mod:`agentstrike.infrastructure.mcp`         — mock MCP tool server.
* :mod:`agentstrike.infrastructure.memory_store` — tamper-evident, SHA-256
  chained, append-only memory store.
* :mod:`agentstrike.infrastructure.vector_clock` — causal ordering primitive.
* :mod:`agentstrike.infrastructure.quorum`       — quorum-based write
  validation used by the memory store and the validator's quorum stage.
"""
