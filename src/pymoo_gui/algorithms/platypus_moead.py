# Factory module for the Platypus implementation of MOEA/D.

# ------------------------------------------------------------------------------------
# Module: platypus_moead.py
# Summary: Platypus MOEA/D factory and GUI metadata.
# Implementation: pymoo problems are adapted and optimized by platypus.MOEAD.
# Responsibility: adds the Platypus implementation of MOEA/D for comparison.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict

from .platypus_common import (
    PlatypusAlgorithmAdapter,
    parse_positive_int,
    parse_probability,
    problem_n_obj,
)


def make_platypus_moead(
    problem: Any,
    population_size: int = 100,
    neighborhood_size: int = 10,
    delta: float = 0.8,
    eta: int = 1,
) -> PlatypusAlgorithmAdapter:
    # Create a GUI-compatible Platypus MOEA/D adapter.
    # Args:
    # problem (Any): pymoo problem wrapped for Platypus.
    # population_size (int): Platypus MOEA/D population size.
    # neighborhood_size (int): Number of neighboring subproblems.
    # delta (float): Probability of choosing neighborhood mating.
    # eta (int): Maximum number of subproblems updated by one offspring.
    # Returns:
    # PlatypusAlgorithmAdapter: Adapter exposing Platypus MOEA/D through the GUI interface.
    # Raises:
    # ValueError: If any numeric configuration is invalid.
    # ImportError: If `platypus-opt` cannot be imported.
    problem_n_obj(problem, "MOEA/D")
    parsed_population_size = parse_positive_int(population_size, "population_size")
    parsed_neighborhood_size = parse_positive_int(neighborhood_size, "neighborhood_size")
    parsed_delta = parse_probability(delta, "delta")
    parsed_eta = parse_positive_int(eta, "eta")

    def _factory(platypus_problem: Any) -> Any:
        # Instantiate Platypus `MOEAD` for the adapted problem.
        from platypus import MOEAD

        return MOEAD(
            platypus_problem,
            population_size=parsed_population_size,
            neighborhood_size=parsed_neighborhood_size,
            delta=parsed_delta,
            eta=parsed_eta,
        )

    return PlatypusAlgorithmAdapter(problem, _factory)


PLATYPUS_MOEAD_DEFINITION: Dict[str, Any] = {
    "label": "MOEA/D (epsilon family)",
    "factory": make_platypus_moead,
    "form_fields": {
        "population_size": {
            "default": 100,
            "kind": "int",
            "minimum": 1,
            "tooltip": "Liczba wag/populacji przekazywana do MOEA/D.",
        },
        "neighborhood_size": {
            "default": 10,
            "kind": "int",
            "minimum": 1,
            "tooltip": "Rozmiar sasiedztwa MOEA/D.",
        },
        "delta": {
            "default": 0.8,
            "kind": "float",
            "minimum": 0.0,
            "maximum": 1.0,
            "tooltip": "Prawdopodobienstwo wyboru sasiedztwa w MOEA/D.",
        },
        "eta": {
            "default": 1,
            "kind": "int",
            "minimum": 1,
            "tooltip": "Maksymalna liczba podproblemow aktualizowanych przez jedno potomstwo.",
        },
    },
    "form_note": "The library does not provide EpsMOEAD; this entry adds standard MOEA/D.",
}
PLATYPUS_MOEAD_DEFINITION["form_fields"]["population_size"]["tooltip"] = (
    "Number of weights/population members passed to MOEA/D."
)
PLATYPUS_MOEAD_DEFINITION["form_fields"]["neighborhood_size"]["tooltip"] = "MOEA/D neighborhood size."
PLATYPUS_MOEAD_DEFINITION["form_fields"]["delta"]["tooltip"] = (
    "Probability of selecting the neighborhood in MOEA/D."
)
PLATYPUS_MOEAD_DEFINITION["form_fields"]["eta"]["tooltip"] = (
    "Maximum number of subproblems updated by one offspring."
)
