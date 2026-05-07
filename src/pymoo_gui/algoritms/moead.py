"""
EN: Factory module for pymoo MOEA/D with GUI-oriented parameter validation.
"""

# ------------------------------------------------------------------------------------
# File: moead.py
# Contents: MOEA/D factory, parameter validators and reference-direction generation.
# What happens here: objective count, neighborhood settings and mating probability are validated for pymoo MOEAD.
# Role in the framework: contributes a decomposition-based optimizer to the dissertation experiment framework.
# Author: mgr inż. Kristina Valevska
# ------------------------------------------------------------------------------------

from __future__ import annotations
from typing import Any, Dict

from pymoo.algorithms.moo.moead import MOEAD
from pymoo.util.ref_dirs import get_reference_directions


def _parse_positive_int(value: Any, field_name: str) -> int:
    """
    EN:
    Parse a required positive integer option.

    PL:
    Odczytuje dodatnia liczbe calkowita z ustawienia podanego w formularzu.

    Args:
        value (Any): EN: Raw value supplied by the GUI or caller.
                     PL: Wartosc wpisana przez uzytkownika lub przekazana w kodzie.
        field_name (str): EN: Field name included in validation messages.
                          PL: Nazwa pola uzywana w komunikacie bledu.

    Returns:
        int: EN: Parsed integer greater than or equal to 1.
             PL: Poprawna liczba calkowita co najmniej rowna 1.

    Raises:
        ValueError: EN: If conversion fails or the number is below 1.
                    PL: Gdy wartosc nie jest poprawna liczba dodatnia.
    """
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if parsed < 1:
        raise ValueError(f"{field_name} must be >= 1, got {parsed}")
    return parsed


def _parse_probability(value: Any, field_name: str) -> float:
    """
    EN:
    Parse a probability value constrained to the inclusive interval [0, 1].

    PL:
    Sprawdza, czy wartosc jest prawdopodobienstwem od 0 do 1.

    Args:
        value (Any): EN: Raw probability value.
                     PL: Podana wartosc prawdopodobienstwa.
        field_name (str): EN: Field name used in validation messages.
                          PL: Nazwa pola pokazywana przy bledzie.

    Returns:
        float: EN: Valid probability.
               PL: Poprawna wartosc z zakresu od 0 do 1.

    Raises:
        ValueError: EN: If conversion fails or the value is outside [0, 1].
                    PL: Gdy wartosc nie jest liczba albo wychodzi poza zakres.
    """
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if not 0.0 <= parsed <= 1.0:
        raise ValueError(f"{field_name} must be in [0, 1], got {parsed}")
    return parsed


def _problem_n_obj(problem: Any) -> int:
    """
    EN:
    Read and validate the number of objectives required by MOEA/D reference directions.

    PL:
    Sprawdza, ile funkcji celu ma wybrany problem, bo MOEA/D potrzebuje tej
    informacji do przygotowania kierunkow odniesienia.

    Args:
        problem (Any): EN: pymoo-like problem exposing `n_obj`.
                       PL: Wybrany problem optymalizacyjny.

    Returns:
        int: EN: Objective count greater than or equal to 2.
             PL: Liczba funkcji celu, co najmniej 2.

    Raises:
        ValueError: EN: If `n_obj` is missing, invalid or below 2.
                    PL: Gdy problem nie podaje poprawnej liczby celow.
    """
    try:
        n_obj = int(getattr(problem, "n_obj", None))
    except (TypeError, ValueError) as exc:
        raise ValueError("Selected problem does not expose a valid n_obj") from exc
    if n_obj < 2:
        raise ValueError(f"MOEAD requires at least 2 objectives, got {n_obj}")
    return n_obj


def make_moead(
    problem: Any,
    n_partitions: int = 12,
    n_neighbors: int = 15,
    prob_neighbor_mating: float = 0.7,
) -> MOEAD:
    """
    EN:
    Create a pymoo `MOEAD` instance with generated reference directions.

    PL:
    Tworzy algorytm MOEA/D i automatycznie przygotowuje kierunki odniesienia
    dopasowane do liczby funkcji celu.

    Args:
        problem (Any): EN: Problem used to determine objective dimensionality.
                       PL: Problem, z ktorego pobierana jest liczba celow.
        n_partitions (int): EN: Number of partitions for uniform reference directions.
                            PL: Liczba podzialow uzywana przy tworzeniu kierunkow.
        n_neighbors (int): EN: Neighborhood size used by MOEA/D.
                           PL: Liczba sasiadow branych pod uwage przez algorytm.
        prob_neighbor_mating (float): EN: Probability of mating within the neighborhood.
                                      PL: Szansa wyboru rodzicow z sasiedztwa.

    Returns:
        MOEAD: EN: Configured pymoo MOEA/D algorithm.
               PL: Gotowy algorytm MOEA/D do uruchomienia.

    Raises:
        ValueError: EN: If objective count or user parameters are invalid.
                    PL: Gdy liczba celow albo ustawienia algorytmu sa niepoprawne.
    """
    n_obj = _problem_n_obj(problem)
    ref_dirs = get_reference_directions(
        "uniform",
        n_obj,
        n_partitions=_parse_positive_int(n_partitions, "n_partitions"),
    )
    return MOEAD(
        ref_dirs=ref_dirs,
        n_neighbors=_parse_positive_int(n_neighbors, "n_neighbors"),
        prob_neighbor_mating=_parse_probability(prob_neighbor_mating, "prob_neighbor_mating"),
    )


MOEAD_DEFINITION: Dict[str, Any] = {
    "label": "MOEAD",
    "factory": make_moead,
    "form_fields": {
        "n_partitions": {
            "default": 12,
            "kind": "int",
            "minimum": 1,
            "tooltip": "Liczba partycji do generowania uniform ref_dirs.",
        },
        "n_neighbors": {
            "default": 15,
            "kind": "int",
            "minimum": 1,
            "tooltip": "Liczba sąsiadów używana przez MOEAD.",
        },
        "prob_neighbor_mating": {
            "default": 0.7,
            "kind": "float",
            "minimum": 0.0,
            "maximum": 1.0,
            "tooltip": "Prawdopodobieństwo krzyżowania w sąsiedztwie.",
        },
    },
    "form_note": "MOEAD generuje uniform reference directions z liczby celów wybranego problemu.",
}
