"""Data-store tools for the mock MCP server.

Exposes a key/value store representing the application's database. Useful for
modelling secrets, user profiles and the like in red-team scenarios::

    data_store.read(key: str) -> str
    data_store.write(key: str, value: str) -> None
    data_store.list(prefix: str = "") -> list[str]

Writes go through the quorum check
(:mod:`agentstrike.infrastructure.quorum`) so that a jailbroken Blue Agent
cannot silently mutate state.
"""

from __future__ import annotations

from typing import Any


def register(server: Any, store: dict[str, str]) -> None:
    """Register the ``data_store.*`` tools with ``server``.

    Args:
        server: MCP server instance.
        store:  Initial key/value pairs (mutated in place by writes).
    """
    raise NotImplementedError


async def data_store_read(key: str, store: dict[str, str]) -> str:
    """Return the value stored under ``key``; raise :class:`KeyError` if absent."""
    raise NotImplementedError


async def data_store_write(
    key: str,
    value: str,
    store: dict[str, str],
    quorum_signatures: list[str],
) -> None:
    """Write ``value`` to ``key`` after the quorum check passes.

    Args:
        key:                 Target key.
        value:               New value.
        store:               Backing dict.
        quorum_signatures:   Signatures collected by Blue + Judge for this op.
    """
    raise NotImplementedError


async def data_store_list(prefix: str, store: dict[str, str]) -> list[str]:
    """Return every key in ``store`` that begins with ``prefix``."""
    raise NotImplementedError
