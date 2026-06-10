"""Tamper-evident memory store.

Every committed turn is appended as a record of the form::

    {
        "index": int,
        "vector_clock": {agent_id: counter, ...},
        "payload": <json>,
        "prev_hash": "<hex>",
        "this_hash": "<hex>",
        "quorum_signatures": ["<signer_id>:<hmac>", ...]
    }

The chain hash is::

    this_hash = SHA256(serialize(entry) || prev_hash)

where ``serialize(entry)`` is the canonical JSON of the record's *content*
(index, vector clock, payload, quorum signatures) and ``prev_hash`` is the
``this_hash`` of the preceding record. The genesis link uses a per-session,
domain-separated constant ``H0`` so records from one session can never be
spliced into another's chain.

A reader can re-walk the log via :meth:`MemoryStore.verify` and detect any
tampering (mutated payload, reordered or swapped records, truncated tail,
forged hash) **without modifying the log**.

Writes additionally require a quorum of HMAC signatures (see
:mod:`agentstrike.infrastructure.quorum`); the store rejects records whose
quorum cannot be verified.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentstrike.infrastructure.quorum import QuorumSigner, verify_quorum


_DOMAIN = "agentstrike.memory_store.v1"
"""Domain-separation tag mixed into the genesis hash ``H0``."""


@dataclass(frozen=True)
class MemoryRecord:
    """One immutable, hash-chained record in the memory store.

    Attributes:
        index:             Monotonic position in the chain (0-indexed).
        vector_clock:      Snapshot of the causal clock at write time.
        payload:           Arbitrary JSON-serialisable data.
        prev_hash:         ``this_hash`` of the previous record, or ``H0`` for
            the genesis record.
        this_hash:         ``SHA256(serialize(entry) || prev_hash)`` hex.
        quorum_signatures: HMAC tags from the quorum members that approved
            the write.
    """

    index: int
    vector_clock: dict[str, int]
    payload: Any
    prev_hash: str
    this_hash: str
    quorum_signatures: list[str]

    def content_bytes(self) -> bytes:
        """Canonical ``serialize(entry)`` bytes — everything except the hashes.

        This is exactly what the chain hash and the quorum signatures cover.
        """
        return _serialize(
            index=self.index,
            vector_clock=self.vector_clock,
            payload=self.payload,
            quorum_signatures=self.quorum_signatures,
        )


@dataclass(frozen=True)
class BrokenLink:
    """A single integrity violation discovered by :meth:`MemoryStore.verify`.

    Attributes:
        index:    Position of the offending record.
        reason:   ``"bad_hash"`` (recomputed ``this_hash`` mismatch) or
            ``"broken_link"`` (``prev_hash`` does not match the predecessor) or
            ``"bad_index"`` (index is not contiguous).
        expected: The value the store computed / expected.
        actual:   The value stored on disk.
    """

    index: int
    reason: str
    expected: str
    actual: str


@dataclass(frozen=True)
class ChainVerification:
    """Result of a non-mutating chain walk.

    Attributes:
        ok:           ``True`` iff no broken links were found.
        length:       Number of records inspected.
        broken_links: Every violation found (empty when ``ok``).
    """

    ok: bool
    length: int
    broken_links: list[BrokenLink] = field(default_factory=list)


def _serialize(
    *,
    index: int,
    vector_clock: dict[str, int],
    payload: Any,
    quorum_signatures: list[str],
) -> bytes:
    """Canonical JSON serialisation of a record's full content.

    Covers the quorum signatures too, so the chain hash makes them
    tamper-evident. Keys are sorted and whitespace stripped so the digest is
    independent of dict insertion order.
    """
    content = {
        "index": index,
        "vector_clock": vector_clock,
        "payload": payload,
        "quorum_signatures": quorum_signatures,
    }
    return json.dumps(content, sort_keys=True, separators=(",", ":")).encode("utf-8")


def commit_bytes(index: int, vector_clock: dict[str, int], payload: Any) -> bytes:
    """Canonical bytes the quorum signs to approve a write.

    Excludes ``quorum_signatures`` (a signer cannot sign bytes containing its
    own signature) and ``prev_hash`` (signers attest to *content*, not chain
    position). This is what callers must HMAC-sign before :meth:`MemoryStore.append`.
    """
    content = {
        "index": index,
        "vector_clock": vector_clock,
        "payload": payload,
    }
    return json.dumps(content, sort_keys=True, separators=(",", ":")).encode("utf-8")


def genesis_hash(session_id: str) -> str:
    """Return the per-session, domain-separated genesis constant ``H0``."""
    seed = f"{_DOMAIN}:{session_id}".encode("utf-8")
    return hashlib.sha256(seed).hexdigest()


class MemoryStore:
    """Append-only, hash-chained, quorum-validated memory store."""

    def __init__(
        self,
        path: Path,
        quorum_size: int,
        session_id: str | None = None,
        signers: list[QuorumSigner] | None = None,
    ) -> None:
        """Open or create the on-disk log.

        Args:
            path:        Directory the JSONL chain is written to (the file is
                ``<session_id>.chain.jsonl`` within it). If ``path`` has a
                suffix it is treated as the file itself.
            quorum_size: Minimum number of valid signatures per write.
            session_id:  Session this chain belongs to. Determines ``H0``. When
                reopening an existing log the persisted value wins.
            signers:     Roster of legitimate quorum signers. Required for the
                quorum check at :meth:`append` time when ``quorum_size > 0``.
        """
        self.quorum_size = quorum_size
        self.signers = list(signers) if signers else []

        path = Path(path)
        if path.suffix:
            self._path = path
            self._path.parent.mkdir(parents=True, exist_ok=True)
        else:
            path.mkdir(parents=True, exist_ok=True)
            sid = session_id or uuid.uuid4().hex
            self._path = path / f"{sid}.chain.jsonl"

        persisted = self._read_header()
        if persisted is not None:
            self.session_id = persisted
        else:
            self.session_id = session_id or uuid.uuid4().hex
            self._write_header()

    @property
    def path(self) -> Path:
        """Filesystem path of the underlying chain file."""
        return self._path

    @property
    def genesis_hash(self) -> str:
        """The per-session genesis constant ``H0`` for this chain."""
        return genesis_hash(self.session_id)

    # ------------------------------------------------------------------ #
    # Writes                                                             #
    # ------------------------------------------------------------------ #

    def append(
        self,
        payload: Any,
        vector_clock: dict[str, int],
        signatures: list[str],
    ) -> MemoryRecord:
        """Write a new record after verifying the quorum.

        The record's content (``serialize(entry)``) is what the quorum signs
        and what the chain hash covers.

        Raises:
            ValueError: If the quorum cannot be satisfied.
        """
        records = self._load_records()
        index = len(records)
        prev_hash = records[-1].this_hash if records else self.genesis_hash

        if self.quorum_size > 0:
            approved = commit_bytes(index, vector_clock, payload)
            if not verify_quorum(approved, list(signatures), self.signers, self.quorum_size):
                raise ValueError(
                    f"Quorum not satisfied for record {index}: need "
                    f"{self.quorum_size} distinct valid signatures."
                )

        content = _serialize(
            index=index,
            vector_clock=vector_clock,
            payload=payload,
            quorum_signatures=list(signatures),
        )
        this_hash = self._chain_hash(content, prev_hash)
        record = MemoryRecord(
            index=index,
            vector_clock=dict(vector_clock),
            payload=payload,
            prev_hash=prev_hash,
            this_hash=this_hash,
            quorum_signatures=list(signatures),
        )
        self._write_record(record)
        return record

    # ------------------------------------------------------------------ #
    # Reads                                                              #
    # ------------------------------------------------------------------ #

    def read(self, index: int) -> MemoryRecord:
        """Return the record at ``index``."""
        records = self._load_records()
        return records[index]

    def all(self) -> list[MemoryRecord]:
        """Return every record, in order."""
        return self._load_records()

    def __len__(self) -> int:
        return len(self._load_records())

    # ------------------------------------------------------------------ #
    # Integrity                                                          #
    # ------------------------------------------------------------------ #

    def verify(self) -> ChainVerification:
        """Re-walk the chain and report every broken link, without mutating it.

        Checks, for each record:
            * ``index`` is contiguous (0, 1, 2, ...).
            * ``prev_hash`` equals the predecessor's ``this_hash`` (``H0`` for
              the genesis record).
            * ``this_hash`` equals ``SHA256(serialize(entry) || prev_hash)``.

        Returns:
            A :class:`ChainVerification` describing the outcome. The on-disk
            log is never modified.
        """
        records = self._load_records()
        broken: list[BrokenLink] = []
        expected_prev = self.genesis_hash

        for position, record in enumerate(records):
            if record.index != position:
                broken.append(
                    BrokenLink(
                        index=position,
                        reason="bad_index",
                        expected=str(position),
                        actual=str(record.index),
                    )
                )

            if record.prev_hash != expected_prev:
                broken.append(
                    BrokenLink(
                        index=position,
                        reason="broken_link",
                        expected=expected_prev,
                        actual=record.prev_hash,
                    )
                )

            recomputed = self._chain_hash(record.content_bytes(), record.prev_hash)
            if recomputed != record.this_hash:
                broken.append(
                    BrokenLink(
                        index=position,
                        reason="bad_hash",
                        expected=recomputed,
                        actual=record.this_hash,
                    )
                )

            # The next record must chain off the hash actually stored here, so
            # a single tampered record surfaces as one violation rather than
            # cascading down the rest of the chain.
            expected_prev = record.this_hash

        return ChainVerification(ok=not broken, length=len(records), broken_links=broken)

    def verify_chain(self) -> bool:
        """Boolean convenience wrapper around :meth:`verify`."""
        return self.verify().ok

    @staticmethod
    def _chain_hash(content: bytes, prev_hash: str) -> str:
        """Compute ``SHA256(serialize(entry) || prev_hash)`` as hex."""
        return hashlib.sha256(content + prev_hash.encode("utf-8")).hexdigest()

    @staticmethod
    def _hash_record(
        prev_hash: str,
        payload: Any,
        vector_clock: dict[str, int],
        index: int = 0,
        quorum_signatures: list[str] | None = None,
    ) -> str:
        """Compute the chain hash for a record's components.

        Retained for API compatibility with the original stub; delegates to
        :meth:`_chain_hash` after canonicalising the content.
        """
        content = _serialize(
            index=index,
            vector_clock=vector_clock,
            payload=payload,
            quorum_signatures=quorum_signatures or [],
        )
        return MemoryStore._chain_hash(content, prev_hash)

    # ------------------------------------------------------------------ #
    # Persistence helpers                                                #
    # ------------------------------------------------------------------ #

    def _read_header(self) -> str | None:
        """Return the persisted ``session_id`` from the header line, if any."""
        if not self._path.exists():
            return None
        with self._path.open("r", encoding="utf-8") as handle:
            first = handle.readline().strip()
        if not first:
            return None
        obj = json.loads(first)
        header = obj.get("_header")
        if header is None:
            return None
        return header.get("session_id")

    def _write_header(self) -> None:
        """Write the header line (session id + domain) as line 0 of the file."""
        header = {"_header": {"session_id": self.session_id, "domain": _DOMAIN}}
        with self._path.open("w", encoding="utf-8") as handle:
            handle.write(json.dumps(header, sort_keys=True, separators=(",", ":")) + "\n")

    def _write_record(self, record: MemoryRecord) -> None:
        """Append one record as a JSON line."""
        row = {
            "index": record.index,
            "vector_clock": record.vector_clock,
            "payload": record.payload,
            "prev_hash": record.prev_hash,
            "this_hash": record.this_hash,
            "quorum_signatures": record.quorum_signatures,
        }
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
            handle.flush()

    def _load_records(self) -> list[MemoryRecord]:
        """Load every record (skipping the header line) from disk."""
        records: list[MemoryRecord] = []
        if not self._path.exists():
            return records
        with self._path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                if "_header" in obj:
                    continue
                records.append(
                    MemoryRecord(
                        index=obj["index"],
                        vector_clock=obj["vector_clock"],
                        payload=obj["payload"],
                        prev_hash=obj["prev_hash"],
                        this_hash=obj["this_hash"],
                        quorum_signatures=obj["quorum_signatures"],
                    )
                )
        return records
