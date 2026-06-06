/**
 * BattleLog — live Red/Blue/Judge transcript.
 *
 * Consumes typed events emitted by useEventStream and renders one card per
 * turn with role-coloured backgrounds (red / blue / amber). Refusals,
 * validation failures and Judge verdicts get inline badges.
 */

interface BattleLogProps {
  // TODO: type this with the shared Event union once the Pydantic schema is
  //       ported to TypeScript (see hooks/useEventStream.ts).
  events: unknown[];
}

export function BattleLog(_props: BattleLogProps): JSX.Element {
  // TODO: group events by (round_idx, turn_idx) and render per-turn cards.
  return <section aria-label="Battle log">Battle log placeholder</section>;
}
