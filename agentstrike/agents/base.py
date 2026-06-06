"""Common base class for Red, Blue and Judge agents.

:class:`BaseAgent` owns:

* The Anthropic SDK client (configured via :func:`agentstrike.config.get_settings`).
* The model id and system prompt for the role.
* Tool registration (when the role uses MCP tools — only Red, in practice).
* A small retry / backoff layer.
* Event emission helpers so subclasses don't need to know about the event log.

Subclasses implement :meth:`act`, which receives the orchestrator's signed
input and returns a signed output payload.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agentstrike.events.log import EventLog
    from agentstrike.events.types import SignedMessage


class BaseAgent(ABC):
    """Abstract Claude-backed agent.

    Attributes:
        role:          One of ``"red" | "blue" | "judge"``.
        model:         Anthropic model id used for completions.
        system_prompt: Role-specific system prompt.
    """

    role: str
    model: str
    system_prompt: str

    def __init__(
        self,
        model: str,
        system_prompt: str,
        event_log: "EventLog",
        tools: list[dict[str, Any]] | None = None,
    ) -> None:
        """Construct an agent.

        Args:
            model:         Anthropic model identifier.
            system_prompt: Role-specific system prompt.
            event_log:     Where to emit per-call events.
            tools:         Optional list of Anthropic tool definitions exposed
                to the model. Only the Red Agent uses tools by default.
        """
        raise NotImplementedError

    @abstractmethod
    async def act(self, message: "SignedMessage") -> "SignedMessage":
        """Process an incoming signed message and return a signed response.

        Subclasses must implement role-specific behaviour. The base class is
        responsible for transport (Anthropic call) and event emission only.
        """
        raise NotImplementedError

    async def _call_claude(
        self,
        messages: list[dict[str, Any]],
        max_tokens: int = 1024,
    ) -> str:
        """Issue a chat completion request and return the assistant text.

        Internal helper used by :meth:`act`. Handles retries on transient
        errors and emits ``LLM_CALL_*`` events around the request.
        """
        raise NotImplementedError
