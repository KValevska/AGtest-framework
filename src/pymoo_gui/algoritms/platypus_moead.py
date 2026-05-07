"""
EN: Factory module for the Platypus implementation of MOEA/D.
"""

# ------------------------------------------------------------------------------------
# File: platypus_moead.py
# Contents: Platypus MOEA/D factory and GUI metadata.
# What happens here: pymoo problems are adapted and optimized by platypus.MOEAD.
# Role in the framework: adds the Platypus implementation of MOEA/D for comparison.
# Author: mgr inz. Kristina Valevska
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
    """
    EN:
    Create a GUI-compatible Platypus MOEA/D adapter.

    PL:
    Tworzy adapter dla MOEA/D z biblioteki Platypus, aby algorytm mogl zostac
    uruchomiony w tym samym oknie co pozostale metody.

    Args:
        problem (Any): EN: pymoo problem wrapped for Platypus.
                       PL: Problem wybrany w aplikacji.
        population_size (int): EN: Platypus MOEA/D population size.
                               PL: Liczba rozwiazan w populacji algorytmu.
        neighborhood_size (int): EN: Number of neighboring subproblems.
                                 PL: Rozmiar sasiedztwa uzywany przez MOEA/D.
        delta (float): EN: Probability of choosing neighborhood mating.
                       PL: Prawdopodobienstwo wyboru sasiedztwa.
        eta (int): EN: Maximum number of subproblems updated by one offspring.
                   PL: Maksymalna liczba podproblemow aktualizowanych przez jedno nowe rozwiazanie.

    Returns:
        PlatypusAlgorithmAdapter: EN: Adapter exposing Platypus MOEA/D through the GUI interface.
                                  PL: Adapter pozwalajacy GUI sterowac algorytmem.

    Raises:
        ValueError: EN: If any numeric configuration is invalid.
                    PL: Gdy ktorys parametr liczbowy jest niepoprawny.
        ImportError: EN: If `platypus-opt` cannot be imported.
                     PL: Gdy brakuje biblioteki Platypus.
    """
    problem_n_obj(problem, "MOEA/D")
    parsed_population_size = parse_positive_int(population_size, "population_size")
    parsed_neighborhood_size = parse_positive_int(neighborhood_size, "neighborhood_size")
    parsed_delta = parse_probability(delta, "delta")
    parsed_eta = parse_positive_int(eta, "eta")

    def _factory(platypus_problem: Any) -> Any:
        """
        EN:
        Instantiate Platypus `MOEAD` for the adapted problem.

        PL:
        Tworzy wlasciwy obiekt MOEA/D po stronie biblioteki Platypus.
        """
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
    "form_note": "Biblioteka nie dostarcza EpsMOEAD; ten wpis dodaje zwykly MOEA/D.",
}
