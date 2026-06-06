"""Agent layer (Layer 2).

Three Anthropic-backed agents are arranged in an adversarial triangle:

* :mod:`agentstrike.agents.red_agent`   — ``claude-haiku-4-5``, attacker.
* :mod:`agentstrike.agents.blue_agent`  — ``claude-opus-4-6``, defender +
  Constitutional AI self-check.
* :mod:`agentstrike.agents.judge_agent` — ``claude-sonnet-4-6``, scorer.

All three share :class:`agentstrike.agents.base.BaseAgent`, which encapsulates
the Anthropic SDK call, retry policy and event emission.
"""
