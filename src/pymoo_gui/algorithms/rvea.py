# Factory module for RVEA with GUI-specific termination handling.

# ------------------------------------------------------------------------------------
# Module: rvea.py
# Summary: RVEA factory, problem objective validation and reference-direction setup.
# Implementation: reference directions are generated from the selected problem and used to build pymoo RVEA.
# Responsibility: provides a reference-vector-guided algorithm option for the dissertation GUI framework.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict, Optional

from pymoo.core.termination import NoTermination
from pymoo.algorithms.moo.rvea import RVEA
from pymoo.optimize import minimize as _pymoo_minimize
from pymoo.termination.max_gen import MaximumGenerationTermination
from pymoo.util.ref_dirs import get_reference_directions

RVEA_RAN_VIRTUAL_N_GEN = 100


class _RveaRanTermination(MaximumGenerationTermination):
    # Termination shim that keeps RVEA compatible with the GUI's unbounded RAN mode.

    def _update(self, algorithm: Any) -> float:
        # Report no progress toward maximum-generation termination.
        # Args:
        # algorithm (Any): Running pymoo algorithm instance.
        # Returns:
        # float: Always `0.0` to prevent automatic termination.
        # RVEA requires MaximumGenerationTermination for n_max_gen, but GUI RAN
        # mode must keep running until the worker callback raises cancellation.
        return 0.0


def _parse_positive_int(value: Any, field_name: str) -> int:
    # Parse a positive integer configuration value.
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if parsed < 1:
        raise ValueError(f"{field_name} must be >= 1, got {parsed}")
    return parsed


def _parse_positive_float(value: Any, field_name: str) -> float:
    # Parse a floating-point configuration value that must be greater than zero.
    # Raises:
    # ValueError: If the value cannot be parsed or is not positive.
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if parsed <= 0.0:
        raise ValueError(f"{field_name} must be > 0, got {parsed}")
    return parsed


def _parse_optional_positive_int(value: Any, field_name: str) -> Optional[int]:
    # Parse an optional positive integer, preserving `None` for pymoo defaults.
    if value is None:
        return None
    return _parse_positive_int(value, field_name)


def _problem_n_obj(problem: Any) -> int:
    # Validate objective dimensionality required to generate RVEA reference vectors.
    # Raises:
    # ValueError: If the problem has no valid objective count.
    try:
        n_obj = int(getattr(problem, "n_obj", None))
    except (TypeError, ValueError) as exc:
        raise ValueError("Selected problem does not expose a valid n_obj") from exc
    if n_obj < 2:
        raise ValueError(f"RVEA requires at least 2 objectives, got {n_obj}")
    return n_obj


def _is_no_termination(termination: Any) -> bool:
    # Detect pymoo `NoTermination` objects across compatible API versions.
    return isinstance(termination, NoTermination) or termination.__class__.__name__ == "NoTermination"


def _rvea_gui_termination(termination: Any) -> Any:
    # Replace unbounded GUI termination with the RVEA-compatible shim when needed.
    if _is_no_termination(termination):
        return _RveaRanTermination(n_max_gen=RVEA_RAN_VIRTUAL_N_GEN)
    return termination


def make_rvea(
    problem: Any,
    pop_size: Optional[int] = 100,
    n_partitions: int = 99,
    alpha: float = 2.0,
    adapt_freq: float = 0.1,
) -> RVEA:
    # Create an RVEA algorithm and attach a GUI-aware `gui_minimize` runner.
    # Args:
    # problem (Any): Problem used to infer objective count.
    # pop_size (Optional[int]): Population size or `None` for pymoo default behavior.
    # n_partitions (int): Partition count for reference directions.
    # alpha (float): APD penalty parameter.
    # adapt_freq (float): Reference-vector adaptation frequency.
    # Returns:
    # RVEA: Configured RVEA instance with GUI minimize support.
    # Raises:
    # ValueError: If problem metadata or numeric parameters are invalid.
    n_obj = _problem_n_obj(problem)
    ref_dirs = get_reference_directions(
        "das-dennis",
        n_obj,
        n_partitions=_parse_positive_int(n_partitions, "n_partitions"),
    )
    algorithm = RVEA(
        ref_dirs=ref_dirs,
        pop_size=_parse_optional_positive_int(pop_size, "pop_size"),
        alpha=_parse_positive_float(alpha, "alpha"),
        adapt_freq=_parse_positive_float(adapt_freq, "adapt_freq"),
    )

    def gui_minimize(*, problem: Any, termination: Any, **kwargs: Any) -> Any:
        # Run pymoo minimize with termination adapted for RVEA's internal requirements.
        return _pymoo_minimize(problem, algorithm, _rvea_gui_termination(termination), **kwargs)

    algorithm.gui_minimize = gui_minimize
    return algorithm


RVEA_DEFINITION: Dict[str, Any] = {
    "label": "RVEA",
    "factory": make_rvea,
    "form_fields": {
        "pop_size": {
            "default": 100,
            "kind": "int",
            "minimum": 1,
            "tooltip": "Rozmiar populacji.",
        },
        "n_partitions": {
            "default": 99,
            "kind": "int",
            "minimum": 1,
            "tooltip": "Liczba partycji dla ref_dirs.",
        },
        "alpha": {
            "default": 2.0,
            "kind": "float",
            "minimum": 0.0000000001,
            "tooltip": "Parametr alpha dla kary APD.",
        },
        "adapt_freq": {
            "default": 0.1,
            "kind": "float",
            "minimum": 0.0000000001,
            "tooltip": "Czestotliwosc adaptacji reference vectors wzgledem liczby generacji.",
        },
    },
    "form_note": "RVEA generates reference directions from the number of objectives of the selected problem.",
}
RVEA_DEFINITION["form_fields"]["pop_size"]["tooltip"] = "Population size."
RVEA_DEFINITION["form_fields"]["n_partitions"]["tooltip"] = "Number of partitions for ref_dirs."
RVEA_DEFINITION["form_fields"]["alpha"]["tooltip"] = "Alpha parameter for the APD penalty."
RVEA_DEFINITION["form_fields"]["adapt_freq"]["tooltip"] = (
    "Adaptation frequency of reference vectors relative to the number of generations."
)
