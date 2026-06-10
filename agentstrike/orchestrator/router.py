"""Signed message router — the heart of the orchestrator.

For each turn:

1. The :class:`Router` asks the
   :class:`agentstrike.orchestrator.sequencer.TurnSequencer` whose turn it is.
2. It builds a :class:`agentstrike.events.types.SignedMessage` containing the
   transcript so far, signs it with the session key, and hands it to the
   appropriate agent.
3. The agent's reply is verified — **unsigned or tampered messages are
   rejected** — then appended to the transcript and (optionally) committed
   to the memory store.
4. Events are emitted at every step.

The router never executes agent logic itself; it composes the other building
blocks.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Protocol, runtime_checkable

from agentstrike.events.log import EventLog
from agentstrike.events.types import Event, EventType, SignedMessage
from agentstrike.orchestrator.sequencer import Role, TurnSequencer
from agentstrike.orchestrator.session import (
    SessionKey,
    SignatureError,
    new_session_key,
    sign,
    verify,
)


_ORCHESTRATOR_SENDER = "orchestrator"


@runtime_checkable
class AgentProtocol(Protocol):
    """Minimal duck-typed agent interface the router relies on.

    Concrete agents (:class:`agentstrike.agents.base.BaseAgent`) implement
    this naturally; tests can pass any object exposing ``role`` + ``act``.
    """

    role: str

    async def act(self, message: SignedMessage) -> SignedMessage:
        """Process an incoming signed message and return a signed response."""
        ...


class MemoryProtocol(Protocol):
    """Optional memory store interface (Layer 4).

    The router only requires an ``append``-style hook so it can be unit-
    tested without the real :class:`MemoryStore`.
    """

    def append(self, payload: Any, vector_clock: dict[str, int], signatures: list[str]) -> Any:
        ...


class Router:
    """Coordinates one full simulation run."""

    def __init__(
        self,
        sequencer: TurnSequencer,
        agents: dict[Role, AgentProtocol],
        session_key: SessionKey,
        event_log: EventLog,
        memory: MemoryProtocol | None = None,
    ) -> None:
        """Wire the router up with all the collaborators it needs.

        Args:
            sequencer:   Turn schedule.
            agents:      Mapping of role → concrete agent instance.
            session_key: HMAC key for message signing/verification.
            event_log:   Append-only log used for SSE broadcast + reports.
            memory:      Optional tamper-evident store for committed turns.
        """
        missing = {Role.RED, Role.BLUE, Role.JUDGE} - set(agents)
        if missing:
            raise ValueError(f"Router missing agents for roles: {sorted(r.value for r in missing)}")

        self.sequencer = sequencer
        self.agents = agents
        self.session_key = session_key
        self.event_log = event_log
        self.memory = memory

        self._transcript: list[SignedMessage] = []
        self._finished = False

    # ------------------------------------------------------------------ #
    # Public API                                                         #
    # ------------------------------------------------------------------ #

    @classmethod
    def with_new_session(
        cls,
        sequencer: TurnSequencer,
        agents: dict[Role, AgentProtocol],
        event_log: EventLog,
        secret: str | None = None,
        memory: MemoryProtocol | None = None,
    ) -> "Router":
        """Convenience constructor that mints a fresh :class:`SessionKey`."""
        return cls(
            sequencer=sequencer,
            agents=agents,
            session_key=new_session_key(secret),
            event_log=event_log,
            memory=memory,
        )

    @property
    def session_id(self) -> str:
        """UUID of the active simulation session."""
        return self.session_key.session_id

    @property
    def transcript(self) -> list[SignedMessage]:
        """Defensive copy of the verified transcript."""
        return list(self._transcript)

    @property
    def is_finished(self) -> bool:
        """True once :meth:`run` has emitted ``SIMULATION_FINISHED``."""
        return self._finished

    def sign_message(
        self,
        sender: str,
        recipient: str,
        round_idx: int,
        turn_idx: int,
        body: dict[str, Any] | None = None,
    ) -> SignedMessage:
        """Build a :class:`SignedMessage` and sign it with the session key.

        Use this from tests or from agent implementations that need to emit
        a properly-signed reply.
        """
        message = SignedMessage(
            sender=sender,
            recipient=recipient,
            round_idx=round_idx,
            turn_idx=turn_idx,
            body=body or {},
        )
        signature = sign(message.canonical_bytes(), self.session_key)
        return message.model_copy(update={"signature": signature})

    def verify_message(self, message: SignedMessage) -> bool:
        """Return ``True`` iff ``message`` carries a valid signature.

        Empty / missing signatures always return ``False``.
        """
        if not message.signature:
            return False
        return verify(message.canonical_bytes(), message.signature, self.session_key)

    async def run(self) -> None:
        """Drive the simulation until the sequencer is exhausted."""
        await self._emit(EventType.SIMULATION_STARTED, payload={"max_rounds": self.sequencer.max_rounds})

        try:
            for round_idx, turn_idx, role in self.sequencer:
                await self._run_turn(round_idx, turn_idx, role)
        except SignatureError as exc:
            await self._emit(
                EventType.ERROR,
                payload={"error": "signature_error", "detail": str(exc)},
            )
            raise
        finally:
            self._finished = True
            await self._emit(EventType.SIMULATION_FINISHED, payload={"turns": len(self._transcript)})

    # ------------------------------------------------------------------ #
    # Internal helpers                                                   #
    # ------------------------------------------------------------------ #

    async def _run_turn(self, round_idx: int, turn_idx: int, role: Role) -> None:
        """Build the outgoing envelope, dispatch, and commit the response."""
        await self._emit(
            EventType.TURN_STARTED,
            round_idx=round_idx,
            turn_idx=turn_idx,
            agent_role=role.value,
        )

        outgoing = self.sign_message(
            sender=_ORCHESTRATOR_SENDER,
            recipient=role.value,
            round_idx=round_idx,
            turn_idx=turn_idx,
            body={"transcript": [m.model_dump(mode="json") for m in self._transcript]},
        )
        response = await self._dispatch(role, outgoing)
        self._transcript.append(response)

        await self._emit(
            EventType.TURN_ENDED,
            round_idx=round_idx,
            turn_idx=turn_idx,
            agent_role=role.value,
            payload={"response_signature": response.signature[:16] + "..."},
        )

    async def _dispatch(self, role: Role, message: SignedMessage) -> SignedMessage:
        """Verify the outgoing envelope, deliver, and verify the response.

        Raises :class:`SignatureError` if either side fails verification —
        which is how the orchestrator rejects unsigned or tampered traffic.
        """
        if not self.verify_message(message):
            raise SignatureError(
                f"Outgoing envelope to {role.value} failed self-verification "
                "(this indicates a coding bug, not an attack)."
            )

        agent = self.agents[role]
        response = await agent.act(message)

        if not isinstance(response, SignedMessage):
            raise SignatureError(
                f"Agent {role.value!r} returned {type(response).__name__}, "
                "expected SignedMessage."
            )
        if not response.signature:
            raise SignatureError(
                f"Agent {role.value!r} returned an unsigned message; rejecting."
            )
        if not self.verify_message(response):
            raise SignatureError(
                f"Agent {role.value!r} returned a message with an invalid signature; rejecting."
            )
        if response.sender != role.value:
            raise SignatureError(
                f"Agent {role.value!r} claimed sender={response.sender!r}; rejecting."
            )

        return response

    async def _emit(
        self,
        event_type: EventType,
        *,
        round_idx: int | None = None,
        turn_idx: int | None = None,
        agent_role: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> None:
        """Append a typed :class:`Event` to the event log."""
        await self.event_log.append(
            Event(
                type=event_type,
                session_id=self.session_id,
                round_idx=round_idx,
                turn_idx=turn_idx,
                agent_role=agent_role,
                payload=payload or {},
            )
        )


# Re-exported for callers that just need the helper signature shape.
SignerCallable = Callable[[bytes], Awaitable[str]]
