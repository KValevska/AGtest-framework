# Factory module for NSGA-III with reference-direction generation.

# ------------------------------------------------------------------------------------
# Module: nsga3.py
# Summary: NSGA-III factory, problem objective validation and reference-direction setup.
# Implementation: reference directions are generated from the selected problem and used to build pymoo NSGA3.
# Responsibility: provides a many-objective algorithm option for the dissertation GUI framework.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------

from __future__ import annotations

import math
from typing import Any, Dict

from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.util.ref_dirs import get_reference_directions


DEFAULT_NSGA3_POP_SIZE = 100
DEFAULT_NSGA3_N_PARTITIONS = 12


def _parse_positive_int(value: Any, field_name: str) -> int:
    # Parse a positive integer parameter used by the NSGA-III factory.
    # Args:
    # value (Any): Raw user or caller value.
    # field_name (str): Parameter name for validation messages.
    # Returns:
    # int: Parsed positive integer.
    # Raises:
    # ValueError: If parsing fails or the value is below 1.
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if parsed < 1:
        raise ValueError(f"{field_name} must be >= 1, got {parsed}")
    return parsed


def _problem_n_obj(problem: Any) -> int:
    # Validate the problem objective count required for reference directions.
    # Args:
    # problem (Any): Problem object exposing `n_obj`.
    # Returns:
    # int: Valid objective count.
    # Raises:
    try:
        n_obj = int(getattr(problem, "n_obj", None))
    except (TypeError, ValueError) as exc:
        raise ValueError("Selected problem does not expose a valid n_obj") from exc
    if n_obj < 2:
        raise ValueError(f"NSGA-III requires at least 2 objectives, got {n_obj}")
    return n_obj


def _ref_dir_count(n_obj: int, n_partitions: int) -> int:
    # Return the number of Das-Dennis reference directions for a given setup.
    return math.comb(int(n_partitions) + int(n_obj) - 1, int(n_obj) - 1)


def make_nsga3(
    problem: Any,
    pop_size: int = DEFAULT_NSGA3_POP_SIZE,
    n_partitions: int = DEFAULT_NSGA3_N_PARTITIONS,
) -> NSGA3:
    # Build a pymoo `NSGA3` instance using Das-Dennis reference directions.
    # Args:
    # problem (Any): Problem used to determine objective count.
    # pop_size (int): Population size for the optimizer.
    # n_partitions (int): Partition count for reference-direction generation.
    # Returns:
    # NSGA3: Configured pymoo NSGA-III algorithm.
    # Raises:
    # ValueError: If objective count, population size or partitions are invalid.
    n_obj = _problem_n_obj(problem)
    parsed_pop_size = _parse_positive_int(pop_size, "pop_size")
    parsed_n_partitions = _parse_positive_int(n_partitions, "n_partitions")
    ref_dir_count = _ref_dir_count(n_obj, parsed_n_partitions)
    if parsed_pop_size < ref_dir_count:
        raise ValueError(
            "NSGA-III requires pop_size >= number of reference directions; "
            f"got pop_size={parsed_pop_size}, ref_dirs={ref_dir_count} "
            f"for n_obj={n_obj} and n_partitions={parsed_n_partitions}."
        )
    ref_dirs = get_reference_directions(
        "das-dennis",
        n_obj,
        n_partitions=parsed_n_partitions,
    )
    return NSGA3(pop_size=parsed_pop_size, ref_dirs=ref_dirs)


NSGA3_DEFINITION: Dict[str, Any] = {
    "label": "NSGA-III",
    "factory": make_nsga3,
    "form_fields": {
        "pop_size": {
            "default": DEFAULT_NSGA3_POP_SIZE,
            "kind": "int",
            "minimum": 1,
            "tooltip": "Population size.",
        },
        "n_partitions": {
            "default": DEFAULT_NSGA3_N_PARTITIONS,
            "kind": "int",
            "minimum": 1,
            "tooltip": "Number of partitions for ref_dirs. Keep this low enough that ref_dirs <= pop_size.",
        },
    },
    "form_note": (
        "NSGA-III generates reference directions from the number of objectives of the selected problem. "
        "The GUI default uses n_partitions=12 to keep the number of reference directions compatible with pop_size=100 "
        "for common 3-objective cases."
    ),
}
