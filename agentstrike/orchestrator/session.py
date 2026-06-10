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

import hashlib
import hmac
import secrets
import time
import uuid
from dataclasses import dataclass


_KEY_BYTES = 32
"""Length of a session key in bytes (256 bits — matches HMAC-SHA256 block)."""


class SignatureError(Exception):
    """Raised when a signature is missing, malformed, or fails verification."""


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

    def __post_init__(self) -> None:
        if len(self.key_bytes) != _KEY_BYTES:
            raise ValueError(
                f"SessionKey.key_bytes must be {_KEY_BYTES} bytes, got {len(self.key_bytes)}"
            )


def new_session_key(secret: str | None = None) -> SessionKey:
    """Mint a fresh :class:`SessionKey`.

    Args:
        secret: Optional master secret. When provided, the session key is
            derived as ``HMAC-SHA256(secret, random_salt)`` so the operator
            can audit-trail per-deployment entropy. When ``None``, a pure
            CSPRNG key is generated.

    Returns:
        A new :class:`SessionKey` with a unique ``session_id``.
    """
    if secret is None:
        key_bytes = secrets.token_bytes(_KEY_BYTES)
    else:
        salt = secrets.token_bytes(16)
        key_bytes = hmac.new(secret.encode("utf-8"), salt, hashlib.sha256).digest()

    return SessionKey(
        session_id=str(uuid.uuid4()),
        key_bytes=key_bytes,
        created_at=time.time(),
    )


def sign(payload: bytes, key: SessionKey) -> str:
    """Compute the hex-encoded HMAC-SHA256 of ``payload`` under ``key``.

    Args:
        payload: Canonical bytes to authenticate (typically the output of
            :meth:`agentstrike.events.types.SignedMessage.canonical_bytes`).
        key:     Active session key.

    Returns:
        Lowercase hex digest, 64 characters.
    """
    return hmac.new(key.key_bytes, payload, hashlib.sha256).hexdigest()


def verify(payload: bytes, signature: str, key: SessionKey) -> bool:
    """Constant-time verification of a signature.

    Returns ``False`` on any mismatch — including an empty / malformed
    ``signature`` — and never raises.
    """
    if not signature:
        return False
    expected = sign(payload, key)
    try:
        return hmac.compare_digest(expected, signature)
    except (TypeError, ValueError):
        return False
