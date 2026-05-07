"""
EN: Factory module for NSGA-III with reference-direction generation.
"""

# ------------------------------------------------------------------------------------
# File: nsga3.py
# Contents: NSGA-III factory, problem objective validation and reference-direction setup.
# What happens here: reference directions are generated from the selected problem and used to build pymoo NSGA3.
# Role in the framework: provides a many-objective algorithm option for the dissertation GUI framework.
# Author: mgr inż. Kristina Valevska
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict

from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.util.ref_dirs import get_reference_directions


def _parse_positive_int(value: Any, field_name: str) -> int:
    """
    EN:
    Parse a positive integer parameter used by the NSGA-III factory.

    PL:
    Sprawdza, czy ustawienie algorytmu jest dodatnia liczba calkowita.

    Args:
        value (Any): EN: Raw user or caller value.
                     PL: Wartosc wpisana w formularzu albo przekazana w kodzie.
        field_name (str): EN: Parameter name for validation messages.
                          PL: Nazwa parametru do komunikatu bledu.

    Returns:
        int: EN: Parsed positive integer.
             PL: Poprawna dodatnia liczba calkowita.

    Raises:
        ValueError: EN: If parsing fails or the value is below 1.
                    PL: Gdy wartosc jest niepoprawna albo mniejsza od 1.
    """
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if parsed < 1:
        raise ValueError(f"{field_name} must be >= 1, got {parsed}")
    return parsed


def _problem_n_obj(problem: Any) -> int:
    """
    EN:
    Validate the problem objective count required for reference directions.

    PL:
    Sprawdza liczbe celow problemu, bo NSGA-III musi wiedziec, w ilu wymiarach
    szuka rozwiazan.

    Args:
        problem (Any): EN: Problem object exposing `n_obj`.
                       PL: Wybrany problem optymalizacyjny.

    Returns:
        int: EN: Valid objective count.
             PL: Poprawna liczba funkcji celu.

    Raises:
        ValueError: EN: If `n_obj` is invalid or smaller than 2.
                    PL: Gdy problem nie ma poprawnej liczby celow.
    """
    try:
        n_obj = int(getattr(problem, "n_obj", None))
    except (TypeError, ValueError) as exc:
        raise ValueError("Selected problem does not expose a valid n_obj") from exc
    if n_obj < 2:
        raise ValueError(f"NSGA-III requires at least 2 objectives, got {n_obj}")
    return n_obj


def make_nsga3(problem: Any, pop_size: int = 100, n_partitions: int = 99) -> NSGA3:
    """
    EN:
    Build a pymoo `NSGA3` instance using Das-Dennis reference directions.

    PL:
    Tworzy NSGA-III z kierunkami odniesienia, ktore pomagaja rownomiernie
    rozkladac rozwiazania na froncie Pareto.

    Args:
        problem (Any): EN: Problem used to determine objective count.
                       PL: Problem, z ktorego pobierana jest liczba celow.
        pop_size (int): EN: Population size for the optimizer.
                        PL: Liczba rozwiazan w populacji.
        n_partitions (int): EN: Partition count for reference-direction generation.
                            PL: Liczba podzialow przy tworzeniu kierunkow.

    Returns:
        NSGA3: EN: Configured pymoo NSGA-III algorithm.
               PL: Gotowy algorytm NSGA-III.

    Raises:
        ValueError: EN: If objective count, population size or partitions are invalid.
                    PL: Gdy ktorys parametr jest niepoprawny.
    """
    n_obj = _problem_n_obj(problem)
    ref_dirs = get_reference_directions(
        "das-dennis",
        n_obj,
        n_partitions=_parse_positive_int(n_partitions, "n_partitions"),
    )
    return NSGA3(pop_size=_parse_positive_int(pop_size, "pop_size"), ref_dirs=ref_dirs)


NSGA3_DEFINITION: Dict[str, Any] = {
    "label": "NSGA-III",
    "factory": make_nsga3,
    "form_fields": {
        "pop_size": {"default": 100, "kind": "int", "minimum": 1, "tooltip": "Rozmiar populacji."},
        "n_partitions": {"default": 99, "kind": "int", "minimum": 1, "tooltip": "Liczba partycji dla ref_dirs."},
    },
    "form_note": "NSGA-III generuje reference directions z liczby celow wybranego problemu.",
}
