"""
EN: Factory module for Platypus Eps-MOEA adapted to pymoo GUI problems.
"""

# ------------------------------------------------------------------------------------
# File: eps_moea.py
# Contents: Platypus epsilon-MOEA factory and GUI metadata.
# What happens here: pymoo problems are adapted and optimized by platypus.EpsMOEA.
# Role in the framework: adds an epsilon-dominance MOEA variant from Platypus.
# Author: mgr inz. Kristina Valevska
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
    """
    EN:
    Create a Platypus Eps-MOEA algorithm adapter for a pymoo problem.

    PL:
    Tworzy adapter, ktory pozwala uruchomic Eps-MOEA na problemie z pymoo.
    Epsilony okreslaja, jak dokladnie algorytm rozroznia podobne rozwiazania.

    Args:
        problem (Any): EN: pymoo problem to wrap for Platypus.
                       PL: Problem wybrany w aplikacji.
        population_size (int): EN: Number of candidate solutions maintained by Eps-MOEA.
                               PL: Liczba rozwiazan przechowywanych przez algorytm.
        epsilons (Any): EN: Scalar or per-objective epsilon values.
                        PL: Jedna wartosc epsilon albo lista wartosci dla kazdego celu.

    Returns:
        PlatypusAlgorithmAdapter: EN: GUI-compatible adapter around Platypus Eps-MOEA.
                                  PL: Adapter, dzieki ktoremu GUI moze uruchomic Eps-MOEA.

    Raises:
        ValueError: EN: If population size, objective count or epsilon values are invalid.
                    PL: Gdy rozmiar populacji, liczba celow albo epsilony sa niepoprawne.
        ImportError: EN: If `platypus-opt` is not installed.
                     PL: Gdy brakuje biblioteki Platypus.
    """
    n_obj = problem_n_obj(problem, "Eps-MOEA")
    parsed_population_size = parse_positive_int(population_size, "population_size")
    parsed_epsilons = parse_epsilons(epsilons, n_obj)

    def _factory(platypus_problem: Any) -> Any:
        """
        EN:
        Instantiate Platypus `EpsMOEA` for an already adapted Platypus problem.

        PL:
        Tworzy wlasciwy algorytm Platypus dla problemu przygotowanego przez adapter.
        """
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
