"""PDF report generator using :mod:`reportlab`.

A report is rendered from the JSONL event log produced by
:class:`agentstrike.events.log.EventLog`. The structure mirrors the dashboard:

1. **Cover page** — scenario title, session id, start / end timestamps,
   composite score.
2. **Summary metrics** — attack success rate, mean defence quality, validation
   stage failure breakdown.
3. **Per-round transcripts** — Red attack, Blue defence (with refusals
   highlighted), Judge verdict + rationale.
4. **Memory chain attestation** — recomputed SHA-256 chain root, vector clock
   summary, quorum signature audit.
5. **Appendix** — raw event log (compressed).
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentstrike.events.types import Event


class PDFReportGenerator:
    """Render a :mod:`reportlab` PDF from a list of :class:`Event` records."""

    def __init__(self, output_path: Path) -> None:
        """Create a generator writing to ``output_path``."""
        raise NotImplementedError

    def render(self, events: list["Event"]) -> Path:
        """Render the report and return the final ``Path``."""
        raise NotImplementedError

    def _render_cover(self, events: list["Event"]) -> None:
        """Draw the cover page (scenario, score, timestamps)."""
        raise NotImplementedError

    def _render_summary_metrics(self, events: list["Event"]) -> None:
        """Aggregate event statistics into the summary section."""
        raise NotImplementedError

    def _render_round_transcript(self, events: list["Event"], round_idx: int) -> None:
        """Render a single round's Red/Blue/Judge transcript."""
        raise NotImplementedError

    def _render_chain_attestation(self, events: list["Event"]) -> None:
        """Draw the memory store integrity attestation page."""
        raise NotImplementedError
