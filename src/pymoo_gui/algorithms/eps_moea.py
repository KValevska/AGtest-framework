# Factory module for Platypus Eps-MOEA adapted to pymoo GUI problems.

# ------------------------------------------------------------------------------------
# Module: eps_moea.py
# Summary: Platypus epsilon-MOEA factory and GUI metadata.
# Implementation: pymoo problems are adapted and optimized by platypus.EpsMOEA.
# Responsibility: adds an epsilon-dominance MOEA variant from Platypus.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict

from .platypus_common import (
    PlatypusAlgorithmAdapter,
    parse_epsilons,
    parse_positive_int,
    problem_n_obj,
)


def make_eps_moea(
    problem: Any,
    population_size: int = 100,
    epsilons: Any = 0.01,
) -> PlatypusAlgorithmAdapter:
    # Create a Platypus Eps-MOEA algorithm adapter for a pymoo problem.
    # Args:
    # problem (Any): pymoo problem to wrap for Platypus.
    # population_size (int): Number of candidate solutions maintained by Eps-MOEA.
    # epsilons (Any): Scalar or per-objective epsilon values.
    # Returns:
    # PlatypusAlgorithmAdapter: GUI-compatible adapter around Platypus Eps-MOEA.
    # Raises:
    # ValueError: If population size, objective count or epsilon values are invalid.
    # ImportError: If `platypus-opt` is not installed.
    n_obj = problem_n_obj(problem, "Eps-MOEA")
    parsed_population_size = parse_positive_int(population_size, "population_size")
    parsed_epsilons = parse_epsilons(epsilons, n_obj)

    def _factory(platypus_problem: Any) -> Any:
        # Instantiate Platypus `EpsMOEA` for an already adapted Platypus problem.
        from platypus import EpsMOEA

        return EpsMOEA(
            platypus_problem,
            epsilons=parsed_epsilons,
            population_size=parsed_population_size,
        )

    return PlatypusAlgorithmAdapter(problem, _factory)


EPS_MOEA_DEFINITION: Dict[str, Any] = {
    "label": "Eps-MOEA",
    "factory": make_eps_moea,
    "form_fields": {
        "population_size": {
            "default": 100,
            "kind": "int",
            "minimum": 1,
            "tooltip": "Rozmiar populacji przekazywany do EpsMOEA.",
        },
        "epsilons": {
            "default": 0.01,
            "kind": "any",
            "tooltip": "Epsilon dla kazdego celu: skalar albo lista, np. 0.01 albo [0.01, 0.01].",
        },
    },
    "form_note": "Eps-MOEA uzywa epsilon-dominance archive i dziala przez adapter problemu pymoo.",
}
EPS_MOEA_DEFINITION["form_fields"]["population_size"]["tooltip"] = "Population size passed to EpsMOEA."
EPS_MOEA_DEFINITION["form_fields"]["epsilons"]["tooltip"] = (
    "Epsilon for each objective: scalar or list, e.g. 0.01 or [0.01, 0.01]."
)
EPS_MOEA_DEFINITION["form_note"] = (
    "Eps-MOEA uses an epsilon-dominance archive and runs through the pymoo problem adapter."
)
