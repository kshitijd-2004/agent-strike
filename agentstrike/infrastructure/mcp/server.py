"""Mock MCP server bootstrap.

Instantiates the standard :mod:`mcp` server, registers the three tool
modules, and exposes a single :func:`build_server` factory used both by the
test suite and the live runtime.

The server is deliberately *mock*: every tool resolves against an in-memory
sandbox seeded from the active scenario, never against the host system.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agentstrike.attack_defense.scenarios.registry import Scenario


def build_server(scenario: "Scenario") -> Any:
    """Build and return a configured MCP server instance.

    Args:
        scenario: Drives which tools are registered (Red's allowed tools) and
            seeds the sandbox state (e.g. the contents of the data store).

    Returns:
        A ready-to-serve MCP server. The exact runtime type depends on the
        version of the ``mcp`` package; consumers should treat it as opaque.
    """
    raise NotImplementedError


def list_registered_tools(server: Any) -> list[dict[str, Any]]:
    """Return the JSON tool definitions exposed by ``server``.

    Used by :class:`agentstrike.agents.red_agent.RedAgent` to populate the
    Anthropic ``tools=`` parameter for tool-use calls.
    """
    raise NotImplementedError
