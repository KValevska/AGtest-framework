"""
EN: Factory module for reference-point-guided R-NSGA-III.
"""

# ------------------------------------------------------------------------------------
# File: rnsga3.py
# Contents: R-NSGA-III factory, reference-point normalization and GUI form metadata.
# What happens here: reference points and algorithm parameters are validated before creating pymoo RNSGA3.
# Role in the framework: enables reference-point-guided optimization studies in the dissertation framework.
# Author: mgr inż. Kristina Valevska
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict

import numpy as np
from pymoo.algorithms.moo.rnsga3 import RNSGA3


DEFAULT_REF_POINTS = np.array([[0.3, 0.4], [0.8, 0.5]], dtype=float)


def _problem_n_obj(problem: Any) -> int:
    """
    EN:
    Read and validate the number of objectives for R-NSGA-III.

    PL:
    Sprawdza liczbe funkcji celu, bo punkty odniesienia musza miec tyle samo
    wymiarow co problem.

    Args:
        problem (Any): EN: Problem object exposing `n_obj`.
                       PL: Wybrany problem optymalizacyjny.

    Returns:
        int: EN: Valid objective count.
             PL: Poprawna liczba celow.

    Raises:
        ValueError: EN: If the objective count is invalid or below 2.
                    PL: Gdy liczba celow jest niepoprawna albo zbyt mala.
    """
    try:
        n_obj = int(getattr(problem, "n_obj", None))
    except (TypeError, ValueError) as exc:
        raise ValueError("Selected problem does not expose a valid n_obj") from exc
    if n_obj < 2:
        raise ValueError(f"R-NSGA-III requires at least 2 objectives, got {n_obj}")
    return n_obj


def _parse_positive_int(value: Any, field_name: str) -> int:
    """
    EN:
    Parse a positive integer option.

    PL:
    Sprawdza, czy ustawienie jest dodatnia liczba calkowita.

    Args:
        value (Any): EN: Raw value to convert.
                     PL: Wartosc do sprawdzenia.
        field_name (str): EN: Field name used in error messages.
                          PL: Nazwa pola pokazywana przy bledzie.

    Returns:
        int: EN: Parsed integer >= 1.
             PL: Liczba calkowita co najmniej rowna 1.

    Raises:
        ValueError: EN: If conversion fails or the value is below 1.
                    PL: Gdy wartosc jest niepoprawna.
    """
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if parsed < 1:
        raise ValueError(f"{field_name} must be >= 1, got {parsed}")
    return parsed


def _parse_non_negative_float(value: Any, field_name: str) -> float:
    """
    EN:
    Parse a floating-point parameter that may be zero but not negative.

    PL:
    Sprawdza parametr liczbowy, ktory moze byc zerem, ale nie moze byc ujemny.

    Args:
        value (Any): EN: Raw numeric value.
                     PL: Wartosc do odczytania jako liczba.
        field_name (str): EN: Field name for validation messages.
                          PL: Nazwa pola w komunikacie bledu.

    Returns:
        float: EN: Parsed non-negative value.
               PL: Poprawna liczba nieujemna.

    Raises:
        ValueError: EN: If conversion fails or the value is negative.
                    PL: Gdy wartosc nie jest liczba albo jest ujemna.
    """
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if parsed < 0.0:
        raise ValueError(f"{field_name} must be >= 0, got {parsed}")
    return parsed


def _normalize_ref_points(ref_points: Any, n_obj: int) -> np.ndarray:
    """
    EN:
    Convert reference points to a finite 2D array matching the objective count.

    PL:
    Zamienia punkty odniesienia na tabele liczb i sprawdza, czy pasuja do
    liczby funkcji celu.

    Args:
        ref_points (Any): EN: Single point or collection of reference points.
                          PL: Jeden punkt odniesienia albo lista takich punktow.
        n_obj (int): EN: Expected number of objective coordinates per point.
                     PL: Oczekiwana liczba wartosci w kazdym punkcie.

    Returns:
        np.ndarray: EN: Valid 2D array of reference points.
                    PL: Poprawna tabela punktow odniesienia.

    Raises:
        ValueError: EN: If shape, length or numeric content is invalid.
                    PL: Gdy punkty maja zly ksztalt, dlugosc albo nie sa liczbami.
    """
    try:
        points = np.asarray(ref_points, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid ref_points: {ref_points!r}") from exc
    if points.ndim == 1:
        points = points.reshape(1, -1)
    if points.ndim != 2:
        raise ValueError("ref_points must be a 2D array-like value")
    if points.shape[0] == 0:
        raise ValueError("ref_points cannot be empty")
    if points.shape[1] != n_obj:
        raise ValueError(f"ref_points dimension mismatch: expected {n_obj}, got {points.shape[1]}")
    if not np.isfinite(points).all():
        raise ValueError("ref_points must contain only finite values")
    return points


def make_rnsga3(
    problem: Any,
    ref_points: Any = None,
    pop_per_ref_point: int = 50,
    mu: float = 0.1,
) -> RNSGA3:
    """
    EN:
    Create a pymoo `RNSGA3` instance with validated reference points.

    PL:
    Tworzy algorytm R-NSGA-III z punktami odniesienia i parametrami podanymi w GUI.

    Args:
        problem (Any): EN: Problem used to determine objective count.
                       PL: Problem, dla ktorego uruchamiany jest algorytm.
        ref_points (Any): EN: Reference points guiding the search.
                          PL: Punkty pokazujace, w ktorym obszarze szukac rozwiazan.
        pop_per_ref_point (int): EN: Number of individuals assigned to each reference point.
                                 PL: Liczba rozwiazan przypadajaca na jeden punkt odniesienia.
        mu (float): EN: R-NSGA-III niching parameter.
                    PL: Parametr sterujacy sposobem preferowania punktow odniesienia.

    Returns:
        RNSGA3: EN: Configured pymoo R-NSGA-III algorithm.
                PL: Gotowy algorytm R-NSGA-III.

    Raises:
        ValueError: EN: If problem metadata, reference points or parameters are invalid.
                    PL: Gdy problem, punkty odniesienia albo parametry sa niepoprawne.
    """
    n_obj = _problem_n_obj(problem)
    points = DEFAULT_REF_POINTS if ref_points is None else ref_points
    return RNSGA3(
        ref_points=_normalize_ref_points(points, n_obj),
        pop_per_ref_point=_parse_positive_int(pop_per_ref_point, "pop_per_ref_point"),
        mu=_parse_non_negative_float(mu, "mu"),
    )


RNSGA3_DEFINITION: Dict[str, Any] = {
    "label": "R-NSGA-III",
    "factory": make_rnsga3,
    "form_fields": {
        "ref_points": {
            "default": DEFAULT_REF_POINTS.tolist(),
            "kind": "any",
            "tooltip": "Punkty odniesienia, np. [[0.3, 0.4], [0.8, 0.5]].",
        },
        "pop_per_ref_point": {
            "default": 50,
            "kind": "int",
            "minimum": 1,
            "tooltip": "Liczba osobnikow na punkt odniesienia.",
        },
        "mu": {"default": 0.1, "kind": "float", "minimum": 0.0, "tooltip": "Parametr mu."},
    },
    "form_note": "R-NSGA-III uzywa reference points zgodnych z liczba celow problemu.",
}
