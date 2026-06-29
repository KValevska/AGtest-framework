# Factory module for Platypus Eps-NSGA-II adapted to pymoo GUI problems.

# ------------------------------------------------------------------------------------
# Module: eps_nsga2.py
# Summary: Platypus epsilon-NSGA-II factory and GUI metadata.
# Implementation: pymoo problems are adapted and optimized by platypus.EpsNSGAII.
# Responsibility: adds an epsilon-dominance NSGA-II variant from Platypus.
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


def make_eps_nsga2(
    problem: Any,
    population_size: int = 100,
    epsilons: Any = 0.01,
) -> PlatypusAlgorithmAdapter:
    # Create a GUI-compatible adapter for Platypus `EpsNSGAII`.
    # z pymoo i raportowac wyniki do aplikacji.
    # Args:
    # problem (Any): pymoo problem to optimize.
    # population_size (int): Number of solutions in the algorithm population.
    # epsilons (Any): Scalar or per-objective epsilon configuration.
    # Returns:
    # PlatypusAlgorithmAdapter: Adapter exposing pymoo-like runtime fields.
    # Raises:
    # ImportError: If the Platypus package is unavailable.
    n_obj = problem_n_obj(problem, "Eps-NSGA-II")
    parsed_population_size = parse_positive_int(population_size, "population_size")
    parsed_epsilons = parse_epsilons(epsilons, n_obj)

    def _factory(platypus_problem: Any) -> Any:
        # Instantiate Platypus `EpsNSGAII` for the adapted problem.
        from platypus import EpsNSGAII

        return EpsNSGAII(
            platypus_problem,
            epsilons=parsed_epsilons,
            population_size=parsed_population_size,
        )

    return PlatypusAlgorithmAdapter(problem, _factory)


EPS_NSGA2_DEFINITION: Dict[str, Any] = {
    "label": "Eps-NSGA-II",
    "factory": make_eps_nsga2,
    "form_fields": {
        "population_size": {
            "default": 100,
            "kind": "int",
            "minimum": 1,
            "tooltip": "Rozmiar populacji przekazywany do EpsNSGAII.",
        },
        "epsilons": {
            "default": 0.01,
            "kind": "any",
            "tooltip": "Epsilon dla kazdego celu: skalar albo lista, np. 0.01 albo [0.01, 0.01].",
        },
    },
    "form_note": "Eps-NSGA-II uzywa epsilon-dominance archive i dziala przez adapter problemu pymoo.",
}
EPS_NSGA2_DEFINITION["form_fields"]["population_size"]["tooltip"] = "Population size passed to EpsNSGAII."
EPS_NSGA2_DEFINITION["form_fields"]["epsilons"]["tooltip"] = (
    "Epsilon for each objective: scalar or list, e.g. 0.01 or [0.01, 0.01]."
)
EPS_NSGA2_DEFINITION["form_note"] = (
    "Eps-NSGA-II uses an epsilon-dominance archive and runs through the pymoo problem adapter."
)
