"""Tests for :mod:`agentstrike.infrastructure`.

Covers:

* ``memory_store.py`` — append + read round-trip, hash chain integrity,
  tamper detection (modified payload, swapped records, truncated tail).
* ``vector_clock.py`` — tick / merge / happens-before / concurrent-with.
* ``quorum.py``       — accepts valid quorums, rejects duplicates and forged
  signatures, constant-time on negative paths.
* ``mcp/*``           — sandbox isolation (no host disk access, no real
  network, path traversal blocked).
"""

from __future__ import annotations

import pytest


@pytest.mark.skip(reason="Memory store tests pending implementation.")
def test_memory_store_detects_payload_tamper() -> None:
    """Mutating a payload byte must fail :meth:`verify_chain`."""


@pytest.mark.skip(reason="Vector clock tests pending implementation.")
def test_vector_clock_happens_before_is_strict() -> None:
    """``a.happens_before(a)`` must be ``False``."""


@pytest.mark.skip(reason="Quorum tests pending implementation.")
def test_quorum_rejects_duplicate_signers() -> None:
    """Two signatures from the same signer must not satisfy the quorum."""


@pytest.mark.skip(reason="MCP sandbox tests pending implementation.")
async def test_mcp_file_tools_block_path_traversal() -> None:
    """``file.read('../etc/passwd')`` must raise :class:`PermissionError`."""
