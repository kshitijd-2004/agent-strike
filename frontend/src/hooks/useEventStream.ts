/**
 * useEventStream — React hook wrapping the SSE endpoint.
 *
 * Connects to ``/api/runs/{sessionId}/stream``, reconnects on failure with
 * an exponentially backed-off delay, and uses the SSE ``Last-Event-ID``
 * mechanism to resume without dropping events.
 *
 * Returns the running event list plus a connection-status enum that the
 * dashboard surfaces in the header.
 */

import { useEffect, useState } from 'react';

export type ConnectionStatus = 'idle' | 'connecting' | 'open' | 'reconnecting' | 'closed';

export interface UseEventStreamResult {
  events: unknown[];
  status: ConnectionStatus;
}

export function useEventStream(_sessionId: string | null): UseEventStreamResult {
  const [events] = useState<unknown[]>([]);
  const [status] = useState<ConnectionStatus>('idle');

  useEffect(() => {
    // TODO:
    //   1. Open EventSource pointed at /api/runs/{sessionId}/stream.
    //   2. Push parsed events into state via a reducer / functional setState.
    //   3. On error, transition status -> 'reconnecting' and retry with
    //      exponential backoff up to a cap.
    //   4. Tear down the EventSource in the cleanup function.
  }, []);

  return { events, status };
}
