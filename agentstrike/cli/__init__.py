"""Click-based CLI (Layer 6 — output adapter).

Headless runner for AgentStrike, used in CI and for offline batch evaluation.
The entry point is registered as the ``agentstrike`` console script via
``pyproject.toml``::

    agentstrike --help
    agentstrike list-scenarios
    agentstrike run --scenario prompt_injection_basic --turns 10 --report
"""
