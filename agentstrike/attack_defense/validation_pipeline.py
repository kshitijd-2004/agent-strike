"""Five-stage tool-call validation pipeline.

Every tool call the Blue Agent intends to execute is funnelled through this
pipeline. A call is admitted only if **all five** stages pass, in order:

1. **Schema**          — tool name + arguments match the tool definition.
2. **Intent**          — does this call match the agent's stated goal?
3. **Privilege**       — is this tool permitted for the current task?
4. **Sanitization**    — strip instruction-like patterns from return values.
5. **Audit**           — record an audit-log entry for the admitted call.

Each stage returns a pass/fail verdict plus a human-readable reason. The first
stage to fail short-circuits the pipeline and emits a
``VALIDATION_STAGE_FAILED`` (blocked) event; passing stages emit
``VALIDATION_STAGE_PASSED``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from agentstrike.events.types import Event, EventType

if TYPE_CHECKING:
    from agentstrike.attack_defense.scenarios.registry import Scenario
    from agentstrike.events.log import EventLog


class ValidationStage(str, Enum):
    """Identifiers for the five pipeline stages, in execution order."""

    SCHEMA = "schema"
    INTENT = "intent"
    PRIVILEGE = "privilege"
    SANITIZATION = "sanitization"
    AUDIT = "audit"


#: Execution order of the stages.
STAGE_ORDER: tuple[ValidationStage, ...] = (
    ValidationStage.SCHEMA,
    ValidationStage.INTENT,
    ValidationStage.PRIVILEGE,
    ValidationStage.SANITIZATION,
    ValidationStage.AUDIT,
)


# Argument schema for the built-in mock MCP tools: tool name -> required args.
DEFAULT_TOOL_SCHEMAS: dict[str, dict[str, type]] = {
    "file.read": {"path": str},
    "file.write": {"path": str, "contents": str},
    "file.list": {"path": str},
    "api.fetch": {"url": str},
    "data_store.read": {"key": str},
    "data_store.write": {"key": str, "value": str},
    "data_store.list": {},
}


# Patterns that look like injected instructions inside tool return values.
_INSTRUCTION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?i)ignore\s+(?:all\s+|any\s+)?(?:previous|prior|above)\s+(?:instructions?|prompts?)"),
    re.compile(r"(?i)disregard\s+(?:the\s+)?(?:previous|prior|above|system)"),
    re.compile(r"(?i)\byou are now\b"),
    re.compile(r"(?i)\bsystem\s*(?:prompt|message)\s*:"),
    re.compile(r"(?i)<\s*/?\s*system\s*>"),
    re.compile(r"(?i)\[\s*system\s*\]"),
    re.compile(r"(?i)\bnew\s+instructions?\b\s*:?"),
    re.compile(r"(?i)reveal\s+(?:your\s+|the\s+)?(?:system\s+)?(?:prompt|instructions?)"),
)

_REDACTION = "[REDACTED-INSTRUCTION]"


@dataclass(frozen=True)
class StageOutcome:
    """Result of a single stage.

    Attributes:
        passed: Whether the stage admitted the call.
        reason: Human-readable explanation (used for both pass and fail).
        data:   Optional stage output (e.g. sanitized value, audit entry).
    """

    passed: bool
    reason: str
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of running a single tool call through the pipeline.

    Attributes:
        approved:         ``True`` iff every stage passed.
        failed_stage:     The first stage to reject, or ``None`` on approval.
        reason:           Human-readable explanation surfaced in events/reports.
        sanitized_output: The tool return value after sanitization (``None`` if
            the pipeline stopped before the sanitization stage or no output was
            supplied).
        audit_entry:      The audit-log record produced on approval, else ``None``.
    """

    approved: bool
    failed_stage: ValidationStage | None
    reason: str
    sanitized_output: Any | None = None
    audit_entry: dict[str, Any] | None = None


class ValidationPipeline:
    """Run the five-stage validator against a candidate tool call."""

    def __init__(
        self,
        scenario: "Scenario",
        event_log: "EventLog",
        tool_schemas: dict[str, dict[str, type]] | None = None,
    ) -> None:
        """Bind the pipeline to a specific scenario.

        Args:
            scenario:     Drives the *Privilege* allow-list and the *Intent*
                goal when the context does not override it.
            event_log:    Where stage-level events are emitted.
            tool_schemas: Tool-name → required-argument-type map. Defaults to
                the built-in mock MCP tool set.
        """
        self.scenario = scenario
        self.event_log = event_log
        self.tool_schemas = tool_schemas if tool_schemas is not None else dict(DEFAULT_TOOL_SCHEMAS)

    async def validate(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """Run every stage in order, short-circuiting on the first failure.

        Args:
            tool_name: The tool the agent wants to call.
            arguments: The call arguments.
            context:   Per-call context. Recognised keys:
                * ``stated_goal``  (str)  — the agent's declared objective.
                * ``planned_calls`` (list[str]) — tools the agent said it would
                  use this turn; an unplanned call fails *Intent*.
                * ``tool_output`` (Any)  — the value to sanitize.
                * ``session_id`` / ``round_idx`` / ``turn_idx`` — event metadata.

        Returns:
            A :class:`ValidationResult`. On failure, ``failed_stage`` names the
            blocking stage and a blocked event has been emitted.
        """
        context = context or {}
        sanitized_output: Any | None = None
        audit_entry: dict[str, Any] | None = None

        for stage in STAGE_ORDER:
            outcome = await self._run_stage(stage, tool_name, arguments, context)

            if not outcome.passed:
                await self._emit_stage(stage, tool_name, context, passed=False, reason=outcome.reason)
                return ValidationResult(
                    approved=False,
                    failed_stage=stage,
                    reason=outcome.reason,
                    sanitized_output=sanitized_output,
                    audit_entry=audit_entry,
                )

            if stage is ValidationStage.SANITIZATION:
                sanitized_output = outcome.data.get("sanitized_output")
            elif stage is ValidationStage.AUDIT:
                audit_entry = outcome.data.get("audit_entry")

            await self._emit_stage(stage, tool_name, context, passed=True, reason=outcome.reason)

        return ValidationResult(
            approved=True,
            failed_stage=None,
            reason="All validation stages passed.",
            sanitized_output=sanitized_output,
            audit_entry=audit_entry,
        )

    async def _run_stage(
        self,
        stage: ValidationStage,
        tool_name: str,
        arguments: dict[str, Any],
        context: dict[str, Any],
    ) -> StageOutcome:
        """Dispatch to the handler for ``stage``."""
        if stage is ValidationStage.SCHEMA:
            return self._stage_schema(tool_name, arguments)
        if stage is ValidationStage.INTENT:
            return self._stage_intent(tool_name, arguments, context)
        if stage is ValidationStage.PRIVILEGE:
            return self._stage_privilege(tool_name, arguments)
        if stage is ValidationStage.SANITIZATION:
            return self._stage_sanitization(context)
        return self._stage_audit(tool_name, arguments, context)

    # ------------------------------------------------------------------ #
    # Stage 1 — Schema                                                   #
    # ------------------------------------------------------------------ #

    def _stage_schema(self, tool_name: str, arguments: dict[str, Any]) -> StageOutcome:
        """Verify the tool exists and its arguments match the declared schema."""
        schema = self.tool_schemas.get(tool_name)
        if schema is None:
            return StageOutcome(False, f"Unknown tool {tool_name!r}.")

        missing = [name for name in schema if name not in arguments]
        if missing:
            return StageOutcome(False, f"Missing required argument(s): {', '.join(sorted(missing))}.")

        unexpected = [name for name in arguments if name not in schema]
        if unexpected:
            return StageOutcome(False, f"Unexpected argument(s): {', '.join(sorted(unexpected))}.")

        for name, expected_type in schema.items():
            if not isinstance(arguments[name], expected_type):
                return StageOutcome(
                    False,
                    f"Argument {name!r} must be {expected_type.__name__}, "
                    f"got {type(arguments[name]).__name__}.",
                )

        return StageOutcome(True, "Arguments conform to the tool schema.")

    # ------------------------------------------------------------------ #
    # Stage 2 — Intent classification                                    #
    # ------------------------------------------------------------------ #

    def _stage_intent(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        context: dict[str, Any],
    ) -> StageOutcome:
        """Check the call is consistent with the agent's stated goal.

        Heuristic, deterministic classification:
            * If the agent declared ``planned_calls``, the tool must be among
              them — an off-plan call signals goal drift / hijack.
            * A write/network-class tool fails when the stated goal is
              explicitly read-only.
        """
        planned = context.get("planned_calls")
        if planned is not None and tool_name not in planned:
            return StageOutcome(
                False,
                f"Call {tool_name!r} is not part of the agent's stated plan {sorted(planned)}.",
            )

        goal = (context.get("stated_goal") or self.scenario.objective or "").lower()
        if goal and self._is_mutating(tool_name) and ("read-only" in goal or "read only" in goal):
            return StageOutcome(
                False,
                f"Mutating call {tool_name!r} contradicts the read-only stated goal.",
            )

        return StageOutcome(True, "Call is consistent with the stated goal.")

    # ------------------------------------------------------------------ #
    # Stage 3 — Privilege scope                                          #
    # ------------------------------------------------------------------ #

    def _stage_privilege(self, tool_name: str, arguments: dict[str, Any]) -> StageOutcome:
        """Verify the active scenario permits this tool for the current task."""
        permitted = set(self.scenario.red_tools)
        if tool_name not in permitted:
            return StageOutcome(
                False,
                f"Tool {tool_name!r} is not permitted for task {self.scenario.id!r}.",
            )
        return StageOutcome(True, f"Tool {tool_name!r} is within the task's privilege scope.")

    # ------------------------------------------------------------------ #
    # Stage 4 — Output sanitization                                      #
    # ------------------------------------------------------------------ #

    def _stage_sanitization(self, context: dict[str, Any]) -> StageOutcome:
        """Strip instruction-like patterns from the tool's return value."""
        if "tool_output" not in context:
            return StageOutcome(True, "No tool output to sanitize.", {"sanitized_output": None})

        sanitized, redactions = self._sanitize(context["tool_output"])
        reason = (
            "Output sanitized: no instruction-like patterns found."
            if redactions == 0
            else f"Output sanitized: redacted {redactions} instruction-like pattern(s)."
        )
        return StageOutcome(True, reason, {"sanitized_output": sanitized, "redactions": redactions})

    @staticmethod
    def _sanitize(value: Any) -> tuple[Any, int]:
        """Recursively redact instruction-like patterns; return (clean, count)."""
        if isinstance(value, str):
            count = 0
            cleaned = value
            for pattern in _INSTRUCTION_PATTERNS:
                cleaned, n = pattern.subn(_REDACTION, cleaned)
                count += n
            return cleaned, count
        if isinstance(value, list):
            total = 0
            out_list = []
            for item in value:
                clean_item, n = ValidationPipeline._sanitize(item)
                out_list.append(clean_item)
                total += n
            return out_list, total
        if isinstance(value, dict):
            total = 0
            out_dict = {}
            for key, item in value.items():
                clean_item, n = ValidationPipeline._sanitize(item)
                out_dict[key] = clean_item
                total += n
            return out_dict, total
        return value, 0

    # ------------------------------------------------------------------ #
    # Stage 5 — Audit log entry                                          #
    # ------------------------------------------------------------------ #

    def _stage_audit(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        context: dict[str, Any],
    ) -> StageOutcome:
        """Produce an audit-log entry for the admitted call."""
        entry = {
            "tool_name": tool_name,
            "arguments": arguments,
            "scenario_id": self.scenario.id,
            "session_id": context.get("session_id"),
            "round_idx": context.get("round_idx"),
            "turn_idx": context.get("turn_idx"),
        }
        return StageOutcome(True, "Audit entry recorded.", {"audit_entry": entry})

    # ------------------------------------------------------------------ #
    # Helpers                                                            #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _is_mutating(tool_name: str) -> bool:
        """Heuristic: does the tool mutate state or reach the network?"""
        return any(token in tool_name for token in (".write", "api.", ".delete", ".put", ".post"))

    async def _emit_stage(
        self,
        stage: ValidationStage,
        tool_name: str,
        context: dict[str, Any],
        *,
        passed: bool,
        reason: str,
    ) -> None:
        """Emit a ``VALIDATION_STAGE_PASSED`` / ``..._FAILED`` (blocked) event."""
        event_type = EventType.VALIDATION_STAGE_PASSED if passed else EventType.VALIDATION_STAGE_FAILED
        await self.event_log.append(
            Event(
                type=event_type,
                session_id=context.get("session_id", "unknown"),
                round_idx=context.get("round_idx"),
                turn_idx=context.get("turn_idx"),
                agent_role="blue",
                payload={
                    "stage": stage.value,
                    "tool_name": tool_name,
                    "passed": passed,
                    "blocked": not passed,
                    "reason": reason,
                },
            )
        )
