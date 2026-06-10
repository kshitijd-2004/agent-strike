"""Quorum-based memory write validation.

A *quorum* is a set of HMAC-SHA256 tags computed by independent signers
(typically Blue + Judge) over the same canonical payload. The
:class:`MemoryStore` admits a write only if at least ``quorum_size`` valid
signatures from distinct signers are presented.

This guards against a single compromised agent (notably a jailbroken Blue)
silently rewriting committed turns.
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass


@dataclass(frozen=True)
class QuorumSigner:
    """One member of the signing quorum.

    Attributes:
        signer_id: Stable identifier (e.g. ``"blue"`` or ``"judge"``).
        key:       HMAC key. Distinct per signer per session.
    """

    signer_id: str
    key: bytes


def sign(payload: bytes, signer: QuorumSigner) -> str:
    """Return ``"<signer_id>:<hex_hmac>"`` for ``payload``."""
    digest = hmac.new(signer.key, payload, hashlib.sha256).hexdigest()
    return f"{signer.signer_id}:{digest}"


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
        ``True`` iff at least ``quorum_size`` distinct, recognised signers each
        supplied a valid signature. Every candidate is checked so the negative
        path does not short-circuit on the first failure.
    """
    if quorum_size <= 0:
        return True

    roster = {s.signer_id: s for s in signers}
    valid_signers: set[str] = set()

    for entry in signatures:
        signer_id, _, claimed = entry.partition(":")
        signer = roster.get(signer_id)
        if signer is None or not claimed:
            continue
        expected = hmac.new(signer.key, payload, hashlib.sha256).hexdigest()
        if hmac.compare_digest(expected, claimed):
            valid_signers.add(signer_id)

    return len(valid_signers) >= quorum_size
