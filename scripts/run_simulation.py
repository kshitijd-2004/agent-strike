"""Convenience launcher for a one-off simulation run.

Equivalent to ``python -m agentstrike.cli.main run`` but spelled as a plain
script so it's easy to attach a debugger. Real arguments will be parsed by
the underlying Click command; this wrapper just constructs the context.

Usage::

    python scripts/run_simulation.py --scenario prompt_injection_basic --turns 5
"""

from __future__ import annotations


def main() -> None:
    """Wire stdlib ``argparse`` (or just delegate to the Click CLI) and run."""
    raise NotImplementedError


if __name__ == "__main__":
    main()
