"""Backward-compatible alias for the historical `algoritms` package name."""

from __future__ import annotations

import sys
from importlib import import_module

from ..algorithms import ALGORITHMS, GenerationPayload, known_pareto_front, make_generation_callback, minimize

__all__ = [
    "ALGORITHMS",
    "GenerationPayload",
    "known_pareto_front",
    "make_generation_callback",
    "minimize",
]

_SUBMODULES = (
    "age",
    "common",
    "empty_algorithm_template",
    "eps_moea",
    "eps_nsga2",
    "gde3",
    "hype",
    "ibea",
    "learning_edmo",
    "lmoea_ds",
    "moead",
    "nsga2",
    "nsga3",
    "platypus_common",
    "platypus_moead",
    "research_common",
    "rnn_guided_dmo",
    "rnsga3",
    "rvea",
    "spea2",
    "ts_nsga",
)

for _name in _SUBMODULES:
    sys.modules[f"{__name__}.{_name}"] = import_module(f"pymoo_gui.algorithms.{_name}")
