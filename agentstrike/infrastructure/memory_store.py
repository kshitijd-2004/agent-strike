"""Tamper-evident memory store.

Every committed turn is appended as a record of the form::

    {
        "index": int,
        "vector_clock": {agent_id: counter, ...},
        "payload": <opaque bytes / json>,
        "prev_hash": "<hex>",
        "this_hash": "<hex>",
        "quorum_signatures": ["<role:hmac>", ...]
    }

where ``this_hash = SHA256(prev_hash || canonical_payload || vector_clock)``.
A reader can re-walk the log and detect any tampering by recomputing the
chain.

Writes additionally require a quorum of HMAC signatures (see
:mod:`agentstrike.infrastructure.quorum`); the store rejects records whose
quorum cannot be verified.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class MemoryRecord:
    """One immutable, hash-chained record in the memory store.

    Attributes:
        index:             Monotonic position in the chain (0-indexed).
        vector_clock:      Snapshot of the causal clock at write time.
        payload:           Arbitrary JSON-serialisable data.
        prev_hash:         SHA-256 hex of the previous record (``"0" * 64``
            for the genesis record).
        this_hash:         SHA-256 hex of this record's canonical bytes.
        quorum_signatures: HMAC tags from the quorum members that approved
            the write.
    """

    index: int
    vector_clock: dict[str, int]
    payload: Any
    prev_hash: str
    this_hash: str
    quorum_signatures: list[str]


class MemoryStore:
    """Append-only, hash-chained, quorum-validated memory store."""

    def __init__(self, path: Path, quorum_size: int) -> None:
        """Open or create the on-disk log at ``path``.

        Args:
            path:        Directory the JSONL chain is written to.
            quorum_size: Minimum number of valid signatures per write.
        """
        raise NotImplementedError

    def append(
        self,
        payload: Any,
        vector_clock: dict[str, int],
        signatures: list[str],
    ) -> MemoryRecord:
        """Write a new record after verifying the quorum.

        Raises:
            ValueError: If fewer than ``quorum_size`` valid signatures present.
        """
        raise NotImplementedError

    def read(self, index: int) -> MemoryRecord:
        """Return the record at ``index``."""
        raise NotImplementedError

    def all(self) -> list[MemoryRecord]:
        """Return every record, in order."""
        raise NotImplementedError

    def verify_chain(self) -> bool:
        """Re-walk the chain and confirm no record has been tampered with."""
        raise NotImplementedError

    @staticmethod
    def _hash_record(
        prev_hash: str,
        payload: Any,
        vector_clock: dict[str, int],
    ) -> str:
        """Compute the SHA-256 hex hash for a record (canonical JSON form)."""
        raise NotImplementedError
