"""
EN: Factory module for the NSGA-II optimizer exposed in the GUI registry.
"""

# ------------------------------------------------------------------------------------
# File: nsga2.py
# Contents: NSGA-II factory, parameter validation and GUI registry definition.
# What happens here: pop_size is validated and a configured pymoo NSGA2 instance is created.
# Role in the framework: adds NSGA-II as a selectable baseline algorithm for dissertation experiments.
# Author: mgr inż. Kristina Valevska
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict

from pymoo.algorithms.moo.nsga2 import NSGA2


def _parse_positive_int(value: Any, field_name: str) -> int:
    """
    EN:
    Convert a value to a positive integer and raise a validation error on failure.

    PL:
    Sprawdza, czy podana wartosc jest dodatnia liczba calkowita potrzebna do
    konfiguracji algorytmu.

    Args:
        value (Any): EN: Candidate value to parse.
                     PL: Wartosc wpisana lub przekazana do funkcji.
        field_name (str): EN: Human-readable field name used in error messages.
                          PL: Nazwa pola pokazywana w komunikacie bledu.

    Returns:
        int: EN: Parsed integer greater than or equal to 1.
             PL: Poprawna liczba calkowita co najmniej rowna 1.

    Raises:
        ValueError: EN: If the value cannot be converted or is below 1.
                    PL: Gdy wartosc nie jest liczba calkowita albo jest za mala.
    """
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if parsed < 1:
        raise ValueError(f"{field_name} must be >= 1, got {parsed}")
    return parsed


def make_nsga2(pop_size: int = 100) -> NSGA2:
    """
    EN:
    Create a configured pymoo `NSGA2` instance for the selected population size.

    PL:
    Tworzy algorytm NSGA-II z wybranym rozmiarem populacji, czyli liczba
    rozwiazan sprawdzanych w jednej generacji.

    Args:
        pop_size (int): EN: Number of individuals maintained by NSGA-II.
                        PL: Liczba rozwiazan przechowywanych w populacji.

    Returns:
        NSGA2: EN: Ready-to-run pymoo NSGA-II algorithm object.
               PL: Gotowy algorytm, ktory aplikacja moze uruchomic.

    Raises:
        ValueError: EN: If `pop_size` is not a positive integer.
                    PL: Gdy rozmiar populacji nie jest dodatnia liczba calkowita.
    """
    return NSGA2(pop_size=_parse_positive_int(pop_size, "pop_size"))


NSGA2_DEFINITION: Dict[str, Any] = {
    "label": "NSGA-II",
    "factory": make_nsga2,
    "form_note": "Formularz pokazuje tylko parametry przekazywane bezposrednio do factory algorytmu.",
}
