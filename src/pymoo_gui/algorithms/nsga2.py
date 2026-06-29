# Factory module for the NSGA-II optimizer exposed in the GUI registry.

# ------------------------------------------------------------------------------------
# Module: nsga2.py
# Summary: NSGA-II factory, parameter validation and GUI registry definition.
# Implementation: pop_size is validated and a configured pymoo NSGA2 instance is created.
# Responsibility: adds NSGA-II as a selectable baseline algorithm for dissertation experiments.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict

from pymoo.algorithms.moo.nsga2 import NSGA2


def _parse_positive_int(value: Any, field_name: str) -> int:
    # Convert a value to a positive integer and raise a validation error on failure.
    # Args:
    # value (Any): Candidate value to parse.
    # field_name (str): Human-readable field name used in error messages.
    # Returns:
    # int: Parsed integer greater than or equal to 1.
    # Raises:
    # ValueError: If the value cannot be converted or is below 1.
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if parsed < 1:
        raise ValueError(f"{field_name} must be >= 1, got {parsed}")
    return parsed


def make_nsga2(pop_size: int = 100) -> NSGA2:
    # Create a configured pymoo `NSGA2` instance for the selected population size.
    # Args:
    # pop_size (int): Number of individuals maintained by NSGA-II.
    # Returns:
    # NSGA2: Ready-to-run pymoo NSGA-II algorithm object.
    # Raises:
    return NSGA2(pop_size=_parse_positive_int(pop_size, "pop_size"))


NSGA2_DEFINITION: Dict[str, Any] = {
    "label": "NSGA-II",
    "factory": make_nsga2,
    "form_note": "Formularz pokazuje tylko parametry przekazywane bezposrednio do factory algorytmu.",
}
NSGA2_DEFINITION["form_note"] = "The form shows only the parameters passed directly to the algorithm factory."
