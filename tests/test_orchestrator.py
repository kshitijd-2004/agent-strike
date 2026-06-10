"""Tests for :mod:`agentstrike.orchestrator`.

Covers the five contractual requirements of the orchestrator:

1. HMAC-SHA256 session keys are generated at startup.
2. Every outgoing inter-agent message is signed.
3. Incoming messages are verified; unsigned ones are rejected.
4. Agent turn sequencing follows Red → Blue → Judge for ``max_rounds``.
5. Session state (transcript, finished flag, session id) is maintained.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentstrike.events.log import EventLog
from agentstrike.events.types import EventType, SignedMessage
from agentstrike.orchestrator import (
    Role,
    Router,
    SessionKey,
    SignatureError,
    TurnSequencer,
    new_session_key,
    sign,
    verify,
)


# --------------------------------------------------------------------------- #
# Helpers / fixtures                                                          #
# --------------------------------------------------------------------------- #


class StubAgent:
    """Minimal agent that signs its replies with a supplied session key."""

    def __init__(self, role: Role, session_key: SessionKey) -> None:
        self.role = role.value
        self._key = session_key
        self.calls = 0

    async def act(self, message: SignedMessage) -> SignedMessage:
        self.calls += 1
        reply = SignedMessage(
            sender=self.role,
            recipient=message.sender,
            round_idx=message.round_idx,
            turn_idx=message.turn_idx,
            body={"echo": True, "incoming_sig_len": len(message.signature)},
        )
        return reply.model_copy(update={"signature": sign(reply.canonical_bytes(), self._key)})


class UnsignedAgent:
    """Agent that returns a SignedMessage with an empty signature."""

    role = Role.RED.value

    async def act(self, message: SignedMessage) -> SignedMessage:
        return SignedMessage(
            sender=self.role,
            recipient=message.sender,
            round_idx=message.round_idx,
            turn_idx=message.turn_idx,
            body={"sneaky": "no signature"},
        )


class TamperingAgent:
    """Agent that signs correctly, then mutates the body after signing."""

    def __init__(self, role: Role, session_key: SessionKey) -> None:
        self.role = role.value
        self._key = session_key

    async def act(self, message: SignedMessage) -> SignedMessage:
        reply = SignedMessage(
            sender=self.role,
            recipient=message.sender,
            round_idx=message.round_idx,
            turn_idx=message.turn_idx,
            body={"original": True},
        )
        signed = reply.model_copy(update={"signature": sign(reply.canonical_bytes(), self._key)})
        return signed.model_copy(update={"body": {"original": False, "tampered": True}})


def _build_router(tmp_path: Path, max_rounds: int = 2) -> tuple[Router, EventLog, dict[Role, StubAgent]]:
    key = new_session_key()
    log = EventLog(session_id=key.session_id, base_dir=tmp_path)
    agents: dict[Role, StubAgent] = {role: StubAgent(role, key) for role in Role}
    router = Router(
        sequencer=TurnSequencer(max_rounds=max_rounds),
        agents=agents,  # type: ignore[arg-type]
        session_key=key,
        event_log=log,
    )
    return router, log, agents


# --------------------------------------------------------------------------- #
# 1. HMAC-SHA256 session keys are generated at startup                        #
# --------------------------------------------------------------------------- #


def test_new_session_key_is_unique_and_correctly_sized() -> None:
    a = new_session_key()
    b = new_session_key()
    assert isinstance(a, SessionKey)
    assert len(a.key_bytes) == 32
    assert a.session_id != b.session_id
    assert a.key_bytes != b.key_bytes


def test_new_session_key_with_secret_is_deterministic_in_size() -> None:
    key = new_session_key(secret="hunter2")
    assert len(key.key_bytes) == 32


def test_session_key_rejects_wrong_size() -> None:
    with pytest.raises(ValueError):
        SessionKey(session_id="x", key_bytes=b"too short", created_at=0.0)


# --------------------------------------------------------------------------- #
# 2. Outgoing messages are signed; signatures verify                          #
# --------------------------------------------------------------------------- #


def test_sign_and_verify_round_trip() -> None:
    key = new_session_key()
    payload = b"hello world"
    sig = sign(payload, key)
    assert len(sig) == 64
    assert verify(payload, sig, key) is True


def test_verify_rejects_wrong_key() -> None:
    payload = b"hello"
    sig = sign(payload, new_session_key())
    assert verify(payload, sig, new_session_key()) is False


def test_verify_rejects_empty_signature_without_raising() -> None:
    assert verify(b"x", "", new_session_key()) is False


def test_router_sign_message_produces_verifiable_envelope(tmp_path: Path) -> None:
    router, _, _ = _build_router(tmp_path)
    msg = router.sign_message(
        sender="orchestrator",
        recipient=Role.RED.value,
        round_idx=0,
        turn_idx=0,
        body={"hello": "red"},
    )
    assert msg.signature
    assert router.verify_message(msg) is True


# --------------------------------------------------------------------------- #
# 3. Incoming messages are verified; unsigned ones are rejected               #
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_router_rejects_unsigned_agent_response(tmp_path: Path) -> None:
    key = new_session_key()
    log = EventLog(session_id=key.session_id, base_dir=tmp_path)
    agents: dict[Role, object] = {
        Role.RED: UnsignedAgent(),
        Role.BLUE: StubAgent(Role.BLUE, key),
        Role.JUDGE: StubAgent(Role.JUDGE, key),
    }
    router = Router(
        sequencer=TurnSequencer(max_rounds=1),
        agents=agents,  # type: ignore[arg-type]
        session_key=key,
        event_log=log,
    )

    with pytest.raises(SignatureError, match="unsigned"):
        await router.run()


@pytest.mark.asyncio
async def test_router_rejects_tampered_agent_response(tmp_path: Path) -> None:
    key = new_session_key()
    log = EventLog(session_id=key.session_id, base_dir=tmp_path)
    agents: dict[Role, object] = {
        Role.RED: TamperingAgent(Role.RED, key),
        Role.BLUE: StubAgent(Role.BLUE, key),
        Role.JUDGE: StubAgent(Role.JUDGE, key),
    }
    router = Router(
        sequencer=TurnSequencer(max_rounds=1),
        agents=agents,  # type: ignore[arg-type]
        session_key=key,
        event_log=log,
    )

    with pytest.raises(SignatureError, match="invalid signature"):
        await router.run()


def test_router_verify_message_rejects_signature_for_wrong_session(tmp_path: Path) -> None:
    router, _, _ = _build_router(tmp_path)
    other_key = new_session_key()
    forged = SignedMessage(sender="x", recipient="y", round_idx=0, turn_idx=0)
    forged = forged.model_copy(
        update={"signature": sign(forged.canonical_bytes(), other_key)}
    )
    assert router.verify_message(forged) is False


# --------------------------------------------------------------------------- #
# 4. Turn sequencing                                                          #
# --------------------------------------------------------------------------- #


def test_sequencer_yields_red_blue_judge_in_order() -> None:
    seq = TurnSequencer(max_rounds=2)
    triples = list(seq)
    assert [role for _, _, role in triples] == [
        Role.RED, Role.BLUE, Role.JUDGE,
        Role.RED, Role.BLUE, Role.JUDGE,
    ]
    assert [t for _, t, _ in triples] == [0, 1, 2, 3, 4, 5]
    assert [r for r, _, _ in triples] == [0, 0, 0, 1, 1, 1]
    assert seq.is_finished is True


def test_sequencer_reset_replays_from_start() -> None:
    seq = TurnSequencer(max_rounds=1)
    list(seq)
    assert seq.is_finished
    seq.reset()
    assert not seq.is_finished
    assert len(list(seq)) == 3


def test_sequencer_zero_rounds_is_empty() -> None:
    assert list(TurnSequencer(max_rounds=0)) == []


# --------------------------------------------------------------------------- #
# 5. Session state                                                            #
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_router_run_drives_full_simulation(tmp_path: Path) -> None:
    router, log, agents = _build_router(tmp_path, max_rounds=2)

    assert router.is_finished is False
    assert router.transcript == []

    await router.run()

    assert router.is_finished is True
    assert len(router.transcript) == 6
    assert all(router.verify_message(m) for m in router.transcript)
    assert all(agent.calls == 2 for agent in agents.values())

    events = log.replay()
    types = [e.type for e in events]
    assert types[0] == EventType.SIMULATION_STARTED
    assert types[-1] == EventType.SIMULATION_FINISHED
    assert types.count(EventType.TURN_STARTED) == 6
    assert types.count(EventType.TURN_ENDED) == 6


def test_router_session_id_matches_session_key(tmp_path: Path) -> None:
    router, _, _ = _build_router(tmp_path)
    assert router.session_id == router.session_key.session_id


def test_router_requires_all_three_roles(tmp_path: Path) -> None:
    key = new_session_key()
    log = EventLog(session_id=key.session_id, base_dir=tmp_path)
    with pytest.raises(ValueError, match="missing agents"):
        Router(
            sequencer=TurnSequencer(max_rounds=1),
            agents={Role.RED: StubAgent(Role.RED, key)},  # type: ignore[arg-type]
            session_key=key,
            event_log=log,
        )
