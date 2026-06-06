"""Quorum-based memory write validation.

A *quorum* is a set of HMAC-SHA256 tags computed by independent signers
(typically Blue + Judge) over the same canonical payload. The
:class:`MemoryStore` admits a write only if at least ``quorum_size`` valid
signatures from distinct signers are presented.

This guards against a single compromised agent (notably a jailbroken Blue)
silently rewriting committed turns.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QuorumSigner:
    """One member of the signing quorum.

    Attributes:
        signer_id: Stable identifier (e.g. ``"blue"`` or ``"judge"``).
        key:       32-byte HMAC key. Distinct per signer per session.
    """

    signer_id: str
    key: bytes


def sign(payload: bytes, signer: QuorumSigner) -> str:
    """Return ``"<signer_id>:<hex_hmac>"`` for ``payload``."""
    raise NotImplementedError


def verify_quorum(
    payload: bytes,
    signatures: list[str],
    signers: list[QuorumSigner],
    quorum_size: int,
) -> bool:
    """Verify that at least ``quorum_size`` signatures are valid + distinct.

    Args:
        payload:     Canonical bytes that were signed.
        signatures:  ``"<signer_id>:<hex_hmac>"`` strings to verify.
        signers:     The roster of legitimate signers.
        quorum_size: Minimum number of valid distinct signatures required.

    Returns:
        ``True`` iff the quorum is satisfied. Constant-time per signature.
    """
    raise NotImplementedError
