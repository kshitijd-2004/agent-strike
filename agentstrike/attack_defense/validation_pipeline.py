"""Five-stage tool-call validation pipeline.

Every tool call the Blue Agent intends to execute is funnelled through this
pipeline. A call is admitted only if **all five** stages pass. The stages are
independent and can be unit-tested in isolation:

1. **Schema**     — tool name + arguments match the MCP tool definition.
2. **Authority**  — the current scenario's guardrails permit this tool/args.
3. **Resource**   — quotas (rate limit, byte budget, recursion depth) honoured.
4. **Causality**  — vector-clock check: no out-of-order or missing prerequisites.
5. **Quorum**     — write-class operations carry a quorum signature
   (see :mod:`agentstrike.infrastructure.quorum`).

Each stage emits a ``VALIDATION_STAGE_*`` event so failures are observable in
the dashboard.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agentstrike.attack_defense.scenarios.registry import Scenario
    from agentstrike.events.log import EventLog


class ValidationStage(str, Enum):
    """Identifiers for the five pipeline stages."""

    SCHEMA = "schema"
    AUTHORITY = "authority"
    RESOURCE = "resource"
    CAUSALITY = "causality"
    QUORUM = "quorum"


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of running a single tool call through the pipeline.

    Attributes:
        approved: ``True`` iff every stage passed.
        failed_stage: The first stage to reject, or ``None`` on approval.
        reason: Human-readable explanation surfaced in events / reports.
    """

    approved: bool
    failed_stage: ValidationStage | None
    reason: str


class ValidationPipeline:
    """Run the five-stage validator against a candidate tool call."""

    def __init__(self, scenario: "Scenario", event_log: "EventLog") -> None:
        """Bind the pipeline to a specific scenario.

        Args:
            scenario:  Drives the *Authority* stage's allow-list.
            event_log: Where stage-level events are emitted.
        """
        raise NotImplementedError

    async def validate(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        context: dict[str, Any],
    ) -> ValidationResult:
        """Run every stage in order, short-circuiting on the first failure."""
        raise NotImplementedError

    async def _stage_schema(self, tool_name: str, arguments: dict[str, Any]) -> None:
        """Verify the tool exists and its arguments match the JSON schema."""
        raise NotImplementedError

    async def _stage_authority(self, tool_name: str, arguments: dict[str, Any]) -> None:
        """Verify the active scenario permits this tool + argument pattern."""
        raise NotImplementedError

    async def _stage_resource(self, tool_name: str, arguments: dict[str, Any]) -> None:
        """Verify rate limits / size budgets are not exceeded."""
        raise NotImplementedError

    async def _stage_causality(self, context: dict[str, Any]) -> None:
        """Verify vector-clock invariants for ordering and prerequisites."""
        raise NotImplementedError

    async def _stage_quorum(self, tool_name: str, context: dict[str, Any]) -> None:
        """Verify a quorum signature exists for write-class operations."""
        raise NotImplementedError
