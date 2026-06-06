"""HMAC-SHA256 session key management.

Every simulation run is bound to a freshly generated 256-bit session key.
Messages exchanged between the orchestrator and agents are signed with this
key so that the router can detect tampering, replay or out-of-band injection.

Threat model:
    * An attacker with read access to the event log must not be able to forge
      messages that the router will accept.
    * The Red Agent's tool calls cannot be smuggled directly to the Blue Agent
      without passing through the orchestrator (which re-signs them).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SessionKey:
    """A 256-bit symmetric key bound to a single simulation session.

    Attributes:
        session_id: UUIDv4 identifying this simulation run.
        key_bytes:  32 raw bytes of CSPRNG output. Never logged or persisted.
        created_at: Unix timestamp (seconds) when the key was minted.
    """

    session_id: str
    key_bytes: bytes
    created_at: float


def new_session_key(secret: str | None = None) -> SessionKey:
    """Mint a fresh :class:`SessionKey`.

    Args:
        secret: Optional master secret to mix into the derived key (HKDF). When
            ``None``, a pure CSPRNG key is generated.

    Returns:
        A new :class:`SessionKey` with a unique ``session_id``.
    """
    raise NotImplementedError


def sign(payload: bytes, key: SessionKey) -> str:
    """Compute the hex-encoded HMAC-SHA256 of ``payload`` under ``key``.

    Args:
        payload: Canonical bytes to authenticate (typically a JSON dump of a
            :class:`agentstrike.events.types.SignedMessage` minus its
            ``signature`` field).
        key: The session key.

    Returns:
        Lowercase hex digest, 64 characters.
    """
    raise NotImplementedError


def verify(payload: bytes, signature: str, key: SessionKey) -> bool:
    """Constant-time verification of a signature.

    Args:
        payload:   Canonical message bytes.
        signature: Hex digest claimed by the sender.
        key:       Expected session key.

    Returns:
        ``True`` iff ``signature`` matches; never raises.
    """
    raise NotImplementedError
