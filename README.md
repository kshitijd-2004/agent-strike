# AgentStrike

> **Red team simulation platform for Claude-based AI agent deployments.**

AgentStrike pits three Claude models against each other in a controlled,
event-driven arena to surface vulnerabilities in agentic deployments **before**
they reach production:

| Role        | Model                | Responsibility                           |
| ----------- | -------------------- | ---------------------------------------- |
| Red Agent   | `claude-haiku-4-5`   | Generates jailbreaks, tool-abuse attacks |
| Blue Agent  | `claude-opus-4-6`    | Defends + Constitutional AI self-check   |
| Judge Agent | `claude-sonnet-4-6`  | Scores each round                        |

Every turn flows through an **HMAC-signed orchestrator**, executes against a
**mock MCP tool environment**, and is recorded in a **tamper-evident, vector-
clock-ordered event log** that streams live to the React dashboard via SSE.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Output Layer                            │
│   FastAPI + SSE  •  React dashboard  •  CLI  •  PDF reports     │
├─────────────────────────────────────────────────────────────────┤
│                         Event Stream                            │
│   Typed events  •  Append-only log  •  SSE broadcast            │
├─────────────────────────────────────────────────────────────────┤
│                     Attack + Defense Layer                      │
│   YAML scenario registry  •  5-stage validation pipeline        │
│   Constitutional AI self-check (Blue)                           │
├─────────────────────────────────────────────────────────────────┤
│                          Three Agents                           │
│        Red (Haiku)  •  Blue (Opus)  •  Judge (Sonnet)           │
├─────────────────────────────────────────────────────────────────┤
│                         Orchestrator                            │
│   HMAC-SHA256 session keys  •  Turn sequencer  •  Router        │
├─────────────────────────────────────────────────────────────────┤
│                       Infrastructure                            │
│   MCP mock tools  •  SHA-256 chained memory store               │
│   Vector clocks  •  Quorum write validation                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Project layout

```
agent-strike/
├── README.md
├── requirements.txt
├── pyproject.toml
├── .env.example
├── .gitignore
│
├── agentstrike/                 # Python package
│   ├── config.py                # Settings (pydantic-settings)
│   │
│   ├── orchestrator/            # Layer 1
│   │   ├── session.py           # HMAC-SHA256 session keys
│   │   ├── sequencer.py         # Turn sequencing
│   │   └── router.py            # Signed message routing
│   │
│   ├── agents/                  # Layer 2
│   │   ├── base.py              # Shared Claude agent base
│   │   ├── red_agent.py
│   │   ├── blue_agent.py
│   │   └── judge_agent.py
│   │
│   ├── attack_defense/          # Layer 3
│   │   ├── scenarios/
│   │   │   ├── registry.py      # YAML-backed scenario registry
│   │   │   └── library.yaml     # Built-in attack scenarios
│   │   ├── validation_pipeline.py  # 5-stage tool call validator
│   │   └── constitutional.py    # Blue Agent CAI self-check
│   │
│   ├── infrastructure/          # Layer 4
│   │   ├── mcp/
│   │   │   ├── server.py        # MCP server bootstrap
│   │   │   ├── file_tools.py
│   │   │   ├── api_tools.py
│   │   │   └── data_store_tools.py
│   │   ├── memory_store.py      # SHA-256 chained tamper-evident log
│   │   ├── vector_clock.py      # Causal ordering
│   │   └── quorum.py            # Quorum-based write validation
│   │
│   ├── events/                  # Layer 5
│   │   ├── types.py             # Typed event schemas
│   │   ├── log.py               # Append-only event log
│   │   └── broadcast.py         # SSE broadcaster
│   │
│   ├── api/                     # Layer 6 (HTTP)
│   │   ├── server.py            # FastAPI app factory
│   │   ├── routes.py            # REST endpoints
│   │   └── sse.py               # SSE endpoint
│   │
│   ├── cli/                     # Layer 6 (CLI)
│   │   └── main.py              # Click entry point
│   │
│   └── reporting/               # Layer 6 (offline output)
│       └── pdf_generator.py     # ReportLab PDF builder
│
├── tests/                       # pytest suite (mirrors package layout)
│
├── frontend/                    # React + Vite dashboard
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   └── src/
│
└── scripts/
    └── run_simulation.py        # Convenience launcher
```

---

## Setup

### 1. Backend

```bash
python -m venv .venv
source .venv/bin/activate          # PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env               # then edit ANTHROPIC_API_KEY
```

### 2. Frontend

```bash
cd frontend
npm install
```

### 3. Running

```bash
# API server (FastAPI + SSE)
uvicorn agentstrike.api.server:app --reload

# Dashboard (separate terminal)
cd frontend && npm run dev

# Headless CLI run
agentstrike run --scenario prompt_injection_basic --turns 10
```

### 4. Tests

```bash
pytest
pytest --cov=agentstrike
```

---

## What to implement next

The repository is **scaffolded only** — every module contains a docstring and
empty stubs. Recommended order of implementation:

1. **`agentstrike/config.py`** — finish the `Settings` model so every other
   module can pull from it.
2. **`agentstrike/events/types.py`** — define the typed event schema first; the
   whole platform is event-driven, so this unblocks every other layer.
3. **`agentstrike/events/log.py`** — append-only writer. Trivial dependency for
   Orchestrator + Infrastructure.
4. **`agentstrike/infrastructure/memory_store.py`** + **`vector_clock.py`** +
   **`quorum.py`** — these are pure data structures and easy to unit-test.
5. **`agentstrike/orchestrator/session.py`** — HMAC signing/verification. Pair
   with `router.py` and `sequencer.py`.
6. **`agentstrike/agents/base.py`** then the three concrete agents. Mock the
   Anthropic client first so you can drive end-to-end tests without burning
   API credits.
7. **`agentstrike/attack_defense/`** — scenario registry → validation pipeline
   → constitutional self-check.
8. **`agentstrike/infrastructure/mcp/`** — wire the mock tools last; they are
   exercised through the agents.
9. **`agentstrike/api/`** + **`agentstrike/events/broadcast.py`** — expose the
   running simulation over SSE.
10. **`agentstrike/cli/main.py`** + **`agentstrike/reporting/pdf_generator.py`**
    — headless runner and post-mortem PDF.
11. **`frontend/`** — connect the dashboard to `/events/stream`.

Run `pytest` after each layer; the tests folder is pre-populated with empty
suites mirroring the package layout so you have an obvious place to add
coverage as you go.
