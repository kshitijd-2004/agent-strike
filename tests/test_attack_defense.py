"""Tests for :mod:`agentstrike.attack_defense`.

Covers:

* ``scenarios/registry.py``    — YAML loading, id collision policy,
  ``reload`` semantics.
* ``validation_pipeline.py``   — every stage individually plus end-to-end
  short-circuit on the first failure.
* ``constitutional.py``        — critique / revise loop converges within
  ``N`` iterations; revisions never reintroduce a previously-flagged
  violation.
"""

from __future__ import annotations

import pytest


@pytest.mark.skip(reason="Scenario registry tests pending implementation.")
def test_registry_loads_bundled_library() -> None:
    """The bundled ``library.yaml`` must parse cleanly."""


@pytest.mark.skip(reason="Validation pipeline tests pending implementation.")
async def test_validation_pipeline_short_circuits_on_first_failure() -> None:
    """Once a stage fails, later stages must not run."""


@pytest.mark.skip(reason="Constitutional checker tests pending implementation.")
async def test_constitutional_revise_removes_flagged_violation() -> None:
    """Revising a flagged response must remove the named violation."""
