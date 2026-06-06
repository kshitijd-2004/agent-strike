/**
 * AgentStrike top-level dashboard shell.
 *
 * Layout:
 *   ┌──────────────────────────────────────────────────────────┐
 *   │  Header  (run picker, scenario name, status badge)       │
 *   ├──────────────────────────────────┬───────────────────────┤
 *   │  BattleLog  (live transcript)    │  MetricsPanel         │
 *   │                                  │  (score, validation,  │
 *   │                                  │   chain attestation)  │
 *   ├──────────────────────────────────┴───────────────────────┤
 *   │  EventStream  (raw firehose, collapsible)                │
 *   └──────────────────────────────────────────────────────────┘
 *
 * State management is intentionally minimal: a single `useEventStream` hook
 * provides the live event list, and components derive their own views.
 */

export function App(): JSX.Element {
  // TODO: read selected session id (from URL or run picker), wire into the
  // useEventStream hook, then compose the three panels below.
  return <div>AgentStrike — dashboard not yet implemented.</div>;
}
