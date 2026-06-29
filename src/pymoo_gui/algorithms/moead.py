# Factory module for pymoo MOEA/D with GUI-oriented parameter validation.

# ------------------------------------------------------------------------------------
# Module: moead.py
# Summary: MOEA/D factory, parameter validators and reference-direction generation.
# Implementation: objective count, neighborhood settings and mating probability are validated for pymoo MOEAD.
# Responsibility: contributes a decomposition-based optimizer to the dissertation experiment framework.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------

from __future__ import annotations
from typing import Any, Dict

from pymoo.algorithms.moo.moead import MOEAD
from pymoo.util.ref_dirs import get_reference_directions


def _parse_positive_int(value: Any, field_name: str) -> int:
    # Args:
    # value (Any): Raw value supplied by the GUI or caller.
    # field_name (str): Field name included in validation messages.
    # Returns:
    # int: Parsed integer greater than or equal to 1.
    # Raises:
    # ValueError: If conversion fails or the number is below 1.
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if parsed < 1:
        raise ValueError(f"{field_name} must be >= 1, got {parsed}")
    return parsed


def _parse_probability(value: Any, field_name: str) -> float:
    # Parse a probability value constrained to the inclusive interval [0, 1].
    # Args:
    # value (Any): Raw probability value.
    # field_name (str): Field name used in validation messages.
    # Returns:
    # float: Valid probability.
    # Raises:
    # ValueError: If conversion fails or the value is outside [0, 1].
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if not 0.0 <= parsed <= 1.0:
        raise ValueError(f"{field_name} must be in [0, 1], got {parsed}")
    return parsed


def _problem_n_obj(problem: Any) -> int:
    # Read and validate the number of objectives required by MOEA/D reference directions.
    # Args:
    # problem (Any): pymoo-like problem exposing `n_obj`.
    # Returns:
    # int: Objective count greater than or equal to 2.
    # Raises:
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
    # Create a pymoo `MOEAD` instance with generated reference directions.
    # Args:
    # problem (Any): Problem used to determine objective dimensionality.
    # n_partitions (int): Number of partitions for uniform reference directions.
    # n_neighbors (int): Neighborhood size used by MOEA/D.
    # prob_neighbor_mating (float): Probability of mating within the neighborhood.
    # Returns:
    # MOEAD: Configured pymoo MOEA/D algorithm.
    # Raises:
    # ValueError: If objective count or user parameters are invalid.
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
    "form_note": "MOEAD generates uniform reference directions from the number of objectives of the selected problem.",
}
MOEAD_DEFINITION["form_fields"]["n_partitions"]["tooltip"] = (
    "Number of partitions used to generate uniform ref_dirs."
)
MOEAD_DEFINITION["form_fields"]["n_neighbors"]["tooltip"] = "Number of neighbors used by MOEAD."
MOEAD_DEFINITION["form_fields"]["prob_neighbor_mating"]["tooltip"] = "Probability of neighborhood mating."
