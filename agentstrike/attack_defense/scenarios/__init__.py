"""Attack scenario registry.

A *scenario* is a declarative YAML record describing:

* The attacker objective (e.g. exfiltrate ``/etc/passwd``).
* Which MCP tools are exposed to Red.
* Hard guardrails that Blue must enforce (the Judge's success criteria).
* Optional seed prompts.

Built-in scenarios live in :file:`library.yaml`; users can register additional
scenarios at runtime.
"""
