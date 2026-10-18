"""agent-business-os backbone: deterministic (T0) tools for the ledger, handoffs and status board.

Standard library only, so nothing has to be installed and there is no third-party
supply-chain risk in the code that guards project state.
"""

from pathlib import Path

__version__ = "0.1.0"

# Repo root = two levels above this file (tools/abos/__init__.py).
REPO_ROOT = Path(__file__).resolve().parents[2]
