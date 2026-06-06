"""Click entry point: ``agentstrike <command>``.

Commands:

* ``list-scenarios``    — print every registered scenario id and title.
* ``run``               — execute a simulation headlessly.
* ``replay``            — re-render an old event log into a PDF report.
* ``verify-chain``      — recompute the memory store hash chain and report
  any tampering.
"""

from __future__ import annotations

from typing import Any


def cli() -> Any:
    """Top-level Click group; populated by the ``@cli.command`` decorators below."""
    raise NotImplementedError


def list_scenarios() -> None:
    """``agentstrike list-scenarios`` — print available scenarios."""
    raise NotImplementedError


def run(
    scenario: str,
    turns: int,
    report: bool,
    output_dir: str | None,
) -> None:
    """``agentstrike run`` — execute a single simulation.

    Args:
        scenario:   Scenario id from the registry.
        turns:      Maximum number of full Red/Blue/Judge rounds.
        report:     If ``True``, render a PDF report after the run finishes.
        output_dir: Override the default output directory for logs + reports.
    """
    raise NotImplementedError


def replay(session_id: str) -> None:
    """``agentstrike replay`` — render a PDF report from a stored event log."""
    raise NotImplementedError


def verify_chain(session_id: str) -> None:
    """``agentstrike verify-chain`` — recompute the SHA-256 chain.

    Exits with status ``0`` if the chain is intact, ``1`` otherwise.
    """
    raise NotImplementedError
