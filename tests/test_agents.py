"""Tests for :mod:`agentstrike.agents`.

Covers:

* ``base.py``        — retry/backoff logic, event emission around ``_call_claude``.
* ``red_agent.py``   — produces a tool-call payload given a scenario brief.
* ``blue_agent.py``  — invokes the validation pipeline and constitutional
  checker before committing a response; refusals are emitted as structured
  events.
* ``judge_agent.py`` — returns a deterministic :class:`JudgeVerdict` for a
  fixed transcript when the model is mocked.
"""

from __future__ import annotations

import pytest


@pytest.mark.skip(reason="Red agent tests pending implementation.")
async def test_red_agent_produces_tool_call_for_scenario() -> None:
    """Red Agent must emit at least one allowed tool call."""


@pytest.mark.skip(reason="Blue agent tests pending implementation.")
async def test_blue_agent_refuses_when_validator_rejects() -> None:
    """Blue Agent must refuse and emit a structured rationale on rejection."""


@pytest.mark.skip(reason="Judge agent tests pending implementation.")
async def test_judge_agent_scores_within_range() -> None:
    """Judge verdict score must always lie in ``[0, 100]``."""
