"""REST endpoints for the AgentStrike control plane.

All routes live under the ``/api`` prefix. Endpoints:

* ``GET    /api/scenarios``                — list registered scenarios.
* ``POST   /api/runs``                     — start a new simulation run.
* ``GET    /api/runs``                     — list every run (live + finished).
* ``GET    /api/runs/{session_id}``        — fetch metadata for one run.
* ``GET    /api/runs/{session_id}/events`` — replay the JSONL event log.
* ``GET    /api/runs/{session_id}/report`` — download the generated PDF.

The router is wired into the FastAPI app by
:func:`agentstrike.api.server.create_app`.
"""

from __future__ import annotations

from typing import Any


def build_router() -> Any:
    """Build and return the ``APIRouter`` for the AgentStrike control plane."""
    raise NotImplementedError


async def list_scenarios() -> list[dict[str, Any]]:
    """``GET /api/scenarios`` — return the registered scenarios."""
    raise NotImplementedError


async def start_run(scenario_id: str, max_rounds: int) -> dict[str, Any]:
    """``POST /api/runs`` — kick off a new simulation in the background."""
    raise NotImplementedError


async def list_runs() -> list[dict[str, Any]]:
    """``GET /api/runs`` — every run currently known to the process."""
    raise NotImplementedError


async def get_run(session_id: str) -> dict[str, Any]:
    """``GET /api/runs/{session_id}`` — metadata + summary metrics."""
    raise NotImplementedError


async def get_run_events(session_id: str) -> list[dict[str, Any]]:
    """``GET /api/runs/{session_id}/events`` — full event log replay (JSON)."""
    raise NotImplementedError


async def get_run_report(session_id: str) -> Any:
    """``GET /api/runs/{session_id}/report`` — stream the generated PDF.

    Returns a FastAPI ``FileResponse`` (or 404 if the report has not been
    rendered yet).
    """
    raise NotImplementedError
