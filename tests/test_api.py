"""Tests for :mod:`agentstrike.api`, :mod:`agentstrike.cli`, :mod:`agentstrike.reporting`.

Covers the output-layer adapters:

* FastAPI routes — exercised through ``httpx.AsyncClient`` against the app
  factory, with the orchestrator stubbed out.
* SSE endpoint   — verifies that frames are well-formed and that the
  ``Last-Event-ID`` resume mechanism works.
* Click CLI      — uses :class:`click.testing.CliRunner` to assert exit codes
  and stdout for ``list-scenarios``, ``run --report``, ``verify-chain``.
* PDF reporter   — renders a sample event log and asserts the resulting file
  is a non-empty, valid PDF (magic bytes ``%PDF-``).
"""

from __future__ import annotations

import pytest


@pytest.mark.skip(reason="API tests pending implementation.")
async def test_list_scenarios_endpoint_returns_bundled_scenarios() -> None:
    """``GET /api/scenarios`` must list every bundled scenario id."""


@pytest.mark.skip(reason="SSE tests pending implementation.")
async def test_sse_stream_replays_history_on_initial_connect() -> None:
    """The first SSE frame must be the earliest stored event."""


@pytest.mark.skip(reason="CLI tests pending implementation.")
def test_cli_list_scenarios_exits_zero() -> None:
    """``agentstrike list-scenarios`` must exit cleanly."""


@pytest.mark.skip(reason="PDF reporter tests pending implementation.")
def test_pdf_report_starts_with_magic_bytes() -> None:
    """Generated reports must begin with ``%PDF-``."""
