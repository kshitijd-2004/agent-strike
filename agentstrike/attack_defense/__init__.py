"""Attack + Defense layer (Layer 3).

Components:

* :mod:`agentstrike.attack_defense.scenarios` — YAML-backed registry of attack
  scenarios that drive the Red Agent.
* :mod:`agentstrike.attack_defense.validation_pipeline` — five-stage
  tool-call validator used by the Blue Agent.
* :mod:`agentstrike.attack_defense.constitutional` — Constitutional AI
  self-critique used by the Blue Agent before committing a response.
"""
