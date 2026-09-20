"""Persistent output locations for source and standalone application runs."""

from pathlib import Path
import sys


def results_root() -> Path:
    """Keep standalone results beside the EXE, outside its temporary bundle."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]
