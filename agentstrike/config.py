"""Global configuration for AgentStrike.

All runtime configuration is loaded once from environment variables (or a local
``.env`` file via :mod:`python-dotenv`) and exposed as a singleton
:class:`Settings` instance. Other modules should import :func:`get_settings`
rather than reading ``os.environ`` directly so that tests can override values
cleanly.

The settings cover:

* Anthropic API credentials and per-role model overrides.
* HMAC session secret used by :mod:`agentstrike.orchestrator.session`.
* Filesystem locations for the memory store, event log and PDF reports.
* HTTP server bind address.
* Quorum size for :mod:`agentstrike.infrastructure.quorum`.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any


class Settings:
    """Typed runtime settings for AgentStrike.

    The real implementation will subclass ``pydantic_settings.BaseSettings`` so
    fields can be populated from environment variables prefixed with
    ``AGENTSTRIKE_`` (plus ``ANTHROPIC_API_KEY`` for SDK compatibility).

    Attributes (planned):
        anthropic_api_key: Bearer token for the Anthropic SDK.
        red_model:    Model id for the Red Agent (default ``claude-haiku-4-5``).
        blue_model:   Model id for the Blue Agent (default ``claude-opus-4-6``).
        judge_model:  Model id for the Judge Agent (default ``claude-sonnet-4-6``).
        session_secret: Secret used for HMAC-SHA256 message signing.
        max_turns:    Hard cap on turns per simulation.
        host / port:  FastAPI bind address.
        memory_dir:   Where the tamper-evident memory store writes files.
        event_log_dir: Where the append-only event log writes files.
        report_dir:   Where generated PDF reports are placed.
        quorum_size:  Minimum signatures required for a memory write.
        log_level:    Standard logging level name.
    """

    def __init__(self, **overrides: Any) -> None:
        """Build a :class:`Settings` instance, optionally overriding fields.

        Args:
            **overrides: Field-name / value pairs that win over both defaults
                and environment-variable values. Used by tests.
        """
        raise NotImplementedError


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide :class:`Settings` singleton.

    Cached so repeated imports are cheap. Tests should call
    ``get_settings.cache_clear()`` between cases that mutate the environment.
    """
    raise NotImplementedError


def project_root() -> Path:
    """Return the absolute path of the AgentStrike project root.

    Useful for resolving bundled assets like the YAML scenario library.
    """
    raise NotImplementedError
