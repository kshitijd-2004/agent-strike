# AgentStrike Dashboard

Vite + React + TypeScript front-end for the AgentStrike red-team platform.

## Development

```bash
npm install
npm run dev          # http://localhost:5173 (proxies /api to :8000)
```

The Python backend must be running on `http://127.0.0.1:8000`:

```bash
uvicorn agentstrike.api.server:app --reload
```

## Layout

```
src/
├── main.tsx              # React bootstrap
├── App.tsx               # Top-level dashboard shell
├── components/
│   ├── BattleLog.tsx     # Streaming Red/Blue/Judge transcript
│   ├── MetricsPanel.tsx  # Score + validation breakdown
│   └── EventStream.tsx   # Raw event firehose (debug)
└── hooks/
    └── useEventStream.ts # EventSource wrapper for /api/runs/{id}/stream
```

Every file in this scaffold contains TODO comments marking what to implement.
