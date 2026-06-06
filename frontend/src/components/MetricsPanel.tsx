/**
 * MetricsPanel — running score + validation pipeline breakdown.
 *
 * Aggregates events client-side rather than calling a separate metrics
 * endpoint, so the panel updates on every SSE frame.
 *
 * Sections:
 *   1. Composite score (Judge verdicts, mean of last N rounds).
 *   2. Validation pipeline breakdown — per-stage pass/fail counts.
 *   3. Memory store attestation — chain-root hash, quorum coverage.
 */

interface MetricsPanelProps {
  events: unknown[];
}

export function MetricsPanel(_props: MetricsPanelProps): JSX.Element {
  // TODO: compute aggregates with useMemo and render <ScoreGauge />,
  //       <ValidationBreakdown />, <ChainAttestation /> children.
  return <aside aria-label="Metrics">Metrics placeholder</aside>;
}
