/**
 * EventStream — raw firehose of typed events.
 *
 * A debug/inspection panel rendered as a collapsible footer. Lets reviewers
 * page through the underlying events that drive BattleLog and MetricsPanel.
 */

interface EventStreamProps {
  events: unknown[];
}

export function EventStream(_props: EventStreamProps): JSX.Element {
  // TODO: virtualised list (react-window) once event volume justifies it.
  return <details><summary>Raw events</summary>{/* TODO */}</details>;
}
