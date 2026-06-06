"""Tests for :mod:`agentstrike.orchestrator`.

Covers:

* ``session.py`` — key generation, signing, constant-time verification, tamper
  detection (flipped bits, replayed signatures, wrong key).
* ``sequencer.py`` — turn ordering, ``max_rounds`` enforcement, idempotent
  ``reset``.
* ``router.py`` — verifies an end-to-end Red→Blue→Judge round with the
  ``mock_anthropic`` fixture and asserts that all expected events were
  emitted in order.
"""

from __future__ import annotations

import pytest


@pytest.mark.skip(reason="Orchestrator session key tests pending implementation.")
def test_session_key_signs_and_verifies() -> None:
    """``sign`` + ``verify`` round-trip should return ``True``."""


@pytest.mark.skip(reason="Sequencer tests pending implementation.")
def test_sequencer_yields_red_blue_judge_in_order() -> None:
    """The default sequencer must emit roles in the canonical cadence."""


@pytest.mark.skip(reason="Router integration tests pending implementation.")
async def test_router_runs_full_round() -> None:
    """End-to-end router run with mocked agents must finish cleanly."""
