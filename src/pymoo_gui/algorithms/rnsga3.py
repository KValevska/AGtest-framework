# Factory module for reference-point-guided R-NSGA-III.

# ------------------------------------------------------------------------------------
# Module: rnsga3.py
# Summary: R-NSGA-III factory, reference-point normalization and GUI form metadata.
# Implementation: reference points and algorithm parameters are validated before creating pymoo RNSGA3.
# Responsibility: enables reference-point-guided optimization studies in the dissertation framework.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict

import numpy as np
from pymoo.algorithms.moo.rnsga3 import RNSGA3


DEFAULT_REF_POINTS = np.array([[0.3, 0.4], [0.8, 0.5]], dtype=float)


def _problem_n_obj(problem: Any) -> int:
    # Read and validate the number of objectives for R-NSGA-III.
    # wymiarow co problem.
    # Args:
    # problem (Any): Problem object exposing `n_obj`.
    # Returns:
    # int: Valid objective count.
    # Raises:
    # ValueError: If the objective count is invalid or below 2.
    try:
        n_obj = int(getattr(problem, "n_obj", None))
    except (TypeError, ValueError) as exc:
        raise ValueError("Selected problem does not expose a valid n_obj") from exc
    if n_obj < 2:
        raise ValueError(f"R-NSGA-III requires at least 2 objectives, got {n_obj}")
    return n_obj


def _parse_positive_int(value: Any, field_name: str) -> int:
    # Args:
    # value (Any): Raw value to convert.
    # field_name (str): Field name used in error messages.
    # Returns:
    # int: Parsed integer >= 1.
    # Raises:
    # ValueError: If conversion fails or the value is below 1.
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if parsed < 1:
        raise ValueError(f"{field_name} must be >= 1, got {parsed}")
    return parsed


def _parse_non_negative_float(value: Any, field_name: str) -> float:
    # Parse a floating-point parameter that may be zero but not negative.
    # Args:
    # value (Any): Raw numeric value.
    # field_name (str): Field name for validation messages.
    # Returns:
    # float: Parsed non-negative value.
    # Raises:
    # ValueError: If conversion fails or the value is negative.
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if parsed < 0.0:
        raise ValueError(f"{field_name} must be >= 0, got {parsed}")
    return parsed


def _normalize_ref_points(ref_points: Any, n_obj: int) -> np.ndarray:
    # Convert reference points to a finite 2D array matching the objective count.
    # Args:
    # ref_points (Any): Single point or collection of reference points.
    # n_obj (int): Expected number of objective coordinates per point.
    # Returns:
    # np.ndarray: Valid 2D array of reference points.
    # Raises:
    # ValueError: If shape, length or numeric content is invalid.
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
    # Create a pymoo `RNSGA3` instance with validated reference points.
    # Args:
    # problem (Any): Problem used to determine objective count.
    # ref_points (Any): Reference points guiding the search.
    # pop_per_ref_point (int): Number of individuals assigned to each reference point.
    # mu (float): R-NSGA-III niching parameter.
    # Returns:
    # RNSGA3: Configured pymoo R-NSGA-III algorithm.
    # Raises:
    # ValueError: If problem metadata, reference points or parameters are invalid.
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
    "form_note": "R-NSGA-III uses reference points consistent with the number of objectives of the problem.",
}
RNSGA3_DEFINITION["form_fields"]["ref_points"]["tooltip"] = (
    "Reference points, e.g. [[0.3, 0.4], [0.8, 0.5]]."
)
RNSGA3_DEFINITION["form_fields"]["pop_per_ref_point"]["tooltip"] = "Number of individuals per reference point."
RNSGA3_DEFINITION["form_fields"]["mu"]["tooltip"] = "Mu parameter."
