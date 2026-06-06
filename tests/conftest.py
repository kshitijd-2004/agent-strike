"""Shared pytest fixtures for AgentStrike.

Planned fixtures:

* ``settings``           — :class:`agentstrike.config.Settings` populated with
  test-safe values (mock API key, ephemeral tmp directories).
* ``mock_anthropic``     — monkey-patched Anthropic client returning canned
  completions, so tests run offline.
* ``deterministic_csprng`` — seeds :mod:`secrets` and :mod:`os.urandom` for
  reproducible session keys.
* ``in_memory_event_log`` — :class:`agentstrike.events.log.EventLog` writing
  to ``tmp_path``.
* ``scenario`` (param)   — yields each built-in :class:`Scenario` for
  parameterised end-to-end tests.
"""

from __future__ import annotations

import pytest


@pytest.fixture
def settings() -> None:
    """Return a :class:`Settings` populated with test-safe values."""
    raise NotImplementedError


@pytest.fixture
def mock_anthropic() -> None:
    """Patch the Anthropic SDK client so no real API calls happen."""
    raise NotImplementedError


@pytest.fixture
def deterministic_csprng() -> None:
    """Seed CSPRNG sources for reproducible session keys / signatures."""
    raise NotImplementedError


@pytest.fixture
def in_memory_event_log() -> None:
    """Yield an :class:`EventLog` rooted at ``tmp_path``."""
    raise NotImplementedError
