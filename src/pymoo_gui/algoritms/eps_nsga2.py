"""
EN: Factory module for Platypus Eps-NSGA-II adapted to pymoo GUI problems.
"""

# ------------------------------------------------------------------------------------
# File: eps_nsga2.py
# Contents: Platypus epsilon-NSGA-II factory and GUI metadata.
# What happens here: pymoo problems are adapted and optimized by platypus.EpsNSGAII.
# Role in the framework: adds an epsilon-dominance NSGA-II variant from Platypus.
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


def make_eps_nsga2(
    problem: Any,
    population_size: int = 100,
    epsilons: Any = 0.01,
) -> PlatypusAlgorithmAdapter:
    """
    EN:
    Create a GUI-compatible adapter for Platypus `EpsNSGAII`.

    PL:
    Tworzy adapter dla Eps-NSGA-II, aby algorytm mogl pracowac na problemach
    z pymoo i raportowac wyniki do aplikacji.

    Args:
        problem (Any): EN: pymoo problem to optimize.
                       PL: Problem wybrany w aplikacji.
        population_size (int): EN: Number of solutions in the algorithm population.
                               PL: Liczba rozwiazan w populacji.
        epsilons (Any): EN: Scalar or per-objective epsilon configuration.
                        PL: Jedna wartosc epsilon albo osobne wartosci dla celow.

    Returns:
        PlatypusAlgorithmAdapter: EN: Adapter exposing pymoo-like runtime fields.
                                  PL: Adapter zgodny z reszta aplikacji.

    Raises:
        ValueError: EN: If provided settings cannot be validated.
                    PL: Gdy ustawienia sa niepoprawne.
        ImportError: EN: If the Platypus package is unavailable.
                     PL: Gdy biblioteka Platypus nie jest zainstalowana.
    """
    n_obj = problem_n_obj(problem, "Eps-NSGA-II")
    parsed_population_size = parse_positive_int(population_size, "population_size")
    parsed_epsilons = parse_epsilons(epsilons, n_obj)

    def _factory(platypus_problem: Any) -> Any:
        """
        EN:
        Instantiate Platypus `EpsNSGAII` for the adapted problem.

        PL:
        Tworzy obiekt algorytmu Eps-NSGA-II po stronie biblioteki Platypus.
        """
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
